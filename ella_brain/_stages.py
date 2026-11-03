"""The five functions `mutate` wires together.

load -> prevalidate -> critique consensus -> apply (version++, atomic write)
-> reload-verify.

Not Ella's API.
"""

from __future__ import annotations

import threading
from collections.abc import Mapping
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator
from uuid import UUID

import fcntl
from pydantic import ValidationError

from ella_brain._critics import default_critics
from ella_brain._io import (
    atomic_write,
    canonical,
    dump_bytes,
    entity_dir,
    fingerprint,
    load_current,
    load_version,
    max_version,
    version_path,
)
from ella_brain.errors import ConsensusRejected, MutationRejected, VerificationError, Verdict
from ella_brain.models import MODELS, MUTABLE_FIELDS, SYSTEM_FIELDS, Agent, EntityKind, Status

_THREAD_LOCK = threading.Lock()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid(value: Any, field_name: str) -> UUID:
    if isinstance(value, UUID):
        return value
    try:
        return UUID(str(value))
    except (TypeError, ValueError, AttributeError) as exc:
        raise MutationRejected(f"free strings are banned; {field_name} must be a UUID") from exc


@contextmanager
def _root_lock(root: Path) -> Iterator[None]:
    """One mutate at a time in this process, and across processes via flock.

    A critic that calls mutate fails fast instead of deadlocking.
    """

    if not _THREAD_LOCK.acquire(blocking=False):
        raise MutationRejected("re-entrant mutate is banned")
    handle = None
    try:
        root.mkdir(parents=True, exist_ok=True)
        handle = open(root / ".lock", "a+", encoding="utf-8")
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        if handle is not None:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            handle.close()
        _THREAD_LOCK.release()


class _ReadView:
    """Disk reads only. No write method and no mutate."""

    __slots__ = ("_root",)

    def __init__(self, root: Path) -> None:
        self._root = root

    def current(self, kind: EntityKind, entity_id: UUID) -> Any | None:
        resolved = EntityKind(kind)
        return load_current(self._root, resolved, _uuid(entity_id, "id"))


def load_stage(root: Path, kind: EntityKind, entity_id: UUID) -> Any | None:
    return load_current(root, kind, entity_id)


def _check_patch_shape(patch: Mapping[str, Any] | Any) -> dict[str, Any]:
    if not isinstance(patch, Mapping) or isinstance(patch, (str, bytes)):
        raise MutationRejected("patch must be an object")
    if any(not isinstance(key, str) for key in patch):
        raise MutationRejected("patch keys must be strings")
    data = dict(patch)
    extra = set(data) - MUTABLE_FIELDS - SYSTEM_FIELDS
    if extra:
        raise MutationRejected(
            "extra fields banned: " + ", ".join(sorted(str(name) for name in extra))
        )
    system = set(data) & SYSTEM_FIELDS
    if system:
        raise MutationRejected(
            "system fields are gate-owned: " + ", ".join(sorted(system))
        )
    for key, value in data.items():
        if isinstance(value, str) and value.strip().lower() == "unknown":
            raise MutationRejected(f"{key}: UNKNOWN is banned")
        if isinstance(value, (list, tuple)):
            for item in value:
                if isinstance(item, str) and item.strip().lower() == "unknown":
                    raise MutationRejected(f"{key}: UNKNOWN is banned")
    return data


def _build(kind: EntityKind, entity_id: UUID, current: Any, patch: dict[str, Any]) -> Any:
    model_cls = MODELS[kind]
    if current is None:
        missing = sorted(MUTABLE_FIELDS - set(patch))
        if missing:
            raise MutationRejected("create requires fields: " + ", ".join(missing))
        stamp = _now()
        raw: dict[str, Any] = {
            "id": entity_id,
            "version": 1,
            "created": stamp,
            "updated": stamp,
            "type": patch["type"],
            "status": patch["status"],
            "owner": patch["owner"],
            "deps": patch["deps"],
        }
    else:
        if not patch:
            raise MutationRejected("empty patch")
        raw = {
            "id": current.id,
            "version": current.version + 1,
            "created": current.created,
            "updated": _now(),
            "type": patch.get("type", current.type),
            "status": patch.get("status", current.status),
            "owner": patch.get("owner", current.owner),
            "deps": patch.get("deps", list(current.deps)),
        }
    try:
        proposed = model_cls.model_validate(raw)
    except (ValidationError, ValueError) as exc:
        raise MutationRejected(str(exc)) from exc
    if current is not None:
        previous = canonical(current)
        nxt = canonical(proposed)
        if all(nxt[key] == previous[key] for key in nxt if key not in {"version", "updated"}):
            raise MutationRejected("patch does not change the document")
    return proposed


def _graph_ok(root: Path, kind: EntityKind, proposed: Any) -> None:
    """Deps, cycles, owner, and active/done pre-check. Not the graph critic."""

    view = _ReadView(root)
    if proposed.id in proposed.deps:
        raise MutationRejected("deps cannot include self")
    for dep_id in proposed.deps:
        if view.current(kind, dep_id) is None:
            raise MutationRejected(f"missing dep {dep_id}")
    visiting: set[UUID] = set()

    def deps_of(entity_id: UUID) -> list[UUID]:
        if entity_id == proposed.id:
            return list(proposed.deps)
        other = view.current(kind, entity_id)
        if other is None:
            raise MutationRejected(f"missing dep {entity_id}")
        return list(other.deps)

    def walk(entity_id: UUID) -> None:
        if entity_id in visiting:
            raise MutationRejected(f"dependency cycle at {entity_id}")
        visiting.add(entity_id)
        for dep_id in deps_of(entity_id):
            walk(dep_id)
        visiting.remove(entity_id)

    walk(proposed.id)
    if not (isinstance(proposed, Agent) and proposed.owner == proposed.id):
        if view.current(EntityKind.agent, proposed.owner) is None:
            raise MutationRejected(f"missing owner {proposed.owner}")
    if proposed.status in (Status.active, Status.done):
        for dep_id in proposed.deps:
            dep = view.current(kind, dep_id)
            if dep is None or dep.status is not Status.done:
                actual = "missing" if dep is None else dep.status.value
                raise MutationRejected(
                    f"{proposed.status.value} requires dep {dep_id} to be done (is {actual})"
                )


def prevalidate_stage(
    root: Path,
    kind: EntityKind,
    entity_id: UUID,
    current: Any,
    patch: Mapping[str, Any],
) -> Any:
    proposed = _build(kind, entity_id, current, _check_patch_shape(patch))
    _graph_ok(root, kind, proposed)
    return proposed


def critique_stage(
    root: Path,
    before: Any,
    proposed: Any,
    critics: tuple[Any, Any],
) -> tuple[Verdict, Verdict]:
    if len(critics) != 2:
        raise MutationRejected("exactly two critique models are required")
    left, right = critics
    if getattr(left, "name", None) in (None, "") or left.name == right.name:
        raise MutationRejected("the two critique models must be independent")
    view = _ReadView(root)
    seen = fingerprint(root)

    def _one(critic: Any) -> Verdict:
        before_copy = before.model_copy(deep=True) if before is not None else None
        proposed_copy = proposed.model_copy(deep=True)
        verdict = critic.critique(before_copy, proposed_copy, view)
        if not isinstance(verdict, Verdict):
            raise MutationRejected(f"{critic.name} did not return a Verdict")
        return verdict

    verdicts = (_one(left), _one(right))
    if fingerprint(root) != seen:
        raise MutationRejected("a critique model changed the store; write aborted")
    if not (verdicts[0].allow and verdicts[1].allow):
        raise ConsensusRejected(verdicts)
    return verdicts


def apply_stage(root: Path, kind: EntityKind, proposed: Any) -> Path:
    """`proposed.version` is already the next n. Write that file once."""

    directory = entity_dir(root, kind, proposed.id)
    current = max_version(directory)
    expected_prev = None if proposed.version == 1 else proposed.version - 1
    if current != expected_prev:
        raise MutationRejected(
            f"version conflict: disk max is {current}, write wanted predecessor {expected_prev}"
        )
    path = version_path(root, kind, proposed.id, proposed.version)
    atomic_write(path, dump_bytes(proposed))
    return path


def reload_verify_stage(root: Path, kind: EntityKind, proposed: Any) -> Any:
    path = version_path(root, kind, proposed.id, proposed.version)
    try:
        loaded = load_version(root, kind, proposed.id, proposed.version)
        if canonical(loaded) != canonical(proposed):
            raise VerificationError("reload did not match the proposed document")
        if max_version(entity_dir(root, kind, proposed.id)) != proposed.version:
            raise VerificationError("reloaded version is not the current max")
        again = load_current(root, kind, proposed.id)
        if again is None or canonical(again) != canonical(proposed):
            raise VerificationError("second read did not match")
    except VerificationError:
        if path.exists():
            path.unlink()
        raise
    return again


def run_mutate(
    root: Path,
    kind: EntityKind,
    entity_id: UUID,
    patch: Mapping[str, Any],
    critics: tuple[Any, Any] | None,
) -> Any:
    pair = critics if critics is not None else default_critics()
    with _root_lock(root):
        current = load_stage(root, kind, entity_id)
        proposed = prevalidate_stage(root, kind, entity_id, current, patch)
        critique_stage(root, current, proposed, pair)
        apply_stage(root, kind, proposed)
        return reload_verify_stage(root, kind, proposed)
