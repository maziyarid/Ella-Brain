"""Versioned JSON. Not part of Ella's API.

Layout: {root}/{tasks|agents}/{uuid}/v{n}.json
Current = max n. Versions are immutable. Writes are atomic.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from datetime import timezone
from pathlib import Path
from typing import Any
from uuid import UUID

from ella_brain.errors import VerificationError
from ella_brain.models import MODELS, EntityKind

_VERSION_RE = re.compile(r"^v([1-9][0-9]*)\.json$")


def entity_dir(root: Path, kind: EntityKind, entity_id: UUID) -> Path:
    return root / kind.dirname / str(entity_id)


def version_path(root: Path, kind: EntityKind, entity_id: UUID, version: int) -> Path:
    if version < 1:
        raise VerificationError(f"illegal version {version}")
    return entity_dir(root, kind, entity_id) / f"v{version}.json"


def list_versions(directory: Path) -> list[int]:
    if not directory.is_dir():
        return []
    found: list[int] = []
    for entry in directory.iterdir():
        match = _VERSION_RE.match(entry.name)
        if match and entry.is_file():
            found.append(int(match.group(1)))
    return sorted(found)


def max_version(directory: Path) -> int | None:
    versions = list_versions(directory)
    if not versions:
        return None
    return versions[-1]


def canonical(model: Any) -> dict[str, Any]:
    """Stable document. Key order does not matter; dump sorts keys."""

    created = model.created.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    updated = model.updated.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return {
        "created": created,
        "deps": [str(dep) for dep in model.deps],
        "id": str(model.id),
        "owner": str(model.owner),
        "status": model.status.value,
        "type": model.type.value,
        "updated": updated,
        "version": model.version,
    }


def dump_bytes(model: Any) -> bytes:
    text = json.dumps(canonical(model), sort_keys=True, separators=(",", ":"))
    return (text + "\n").encode("utf-8")


def parse_document(payload: bytes, kind: EntityKind, entity_id: UUID, version: int) -> Any:
    try:
        data = json.loads(payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"version file is not JSON: {exc}") from exc
    try:
        model = MODELS[kind].model_validate(data)
    except Exception as exc:
        raise VerificationError(f"version file failed schema: {exc}") from exc
    if model.id != entity_id or model.version != version:
        raise VerificationError(
            f"v{version}.json for {entity_id} does not match its path "
            f"(id={model.id}, version={model.version})"
        )
    return model


def load_version(root: Path, kind: EntityKind, entity_id: UUID, version: int) -> Any:
    path = version_path(root, kind, entity_id, version)
    if not path.is_file():
        raise VerificationError(f"missing {path.name}")
    return parse_document(path.read_bytes(), kind, entity_id, version)


def load_current(root: Path, kind: EntityKind, entity_id: UUID) -> Any | None:
    """Read max n from disk. No cache. Corrupt max version fails closed."""

    directory = entity_dir(root, kind, entity_id)
    current = max_version(directory)
    if current is None:
        return None
    return load_version(root, kind, entity_id, current)


def _fsync_dir(directory: Path) -> None:
    fd = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_write(path: Path, payload: bytes) -> None:
    """Create path exactly once via same-directory hard link. Does not overwrite."""

    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise VerificationError(f"refusing to overwrite {path.name}")
    fd, tmp_name = tempfile.mkstemp(
        dir=path.parent, prefix=".tmp-", suffix=".json"
    )
    tmp_path = Path(tmp_name)
    published = False
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(tmp_path, path)
        except (FileExistsError, IsADirectoryError) as exc:
            raise VerificationError(f"refusing to overwrite {path.name}") from exc
        published = True
        _fsync_dir(path.parent)
    finally:
        # The destination name, once linked, is independent of the
        # temporary name, so removing the temporary name never
        # removes the destination.
        if tmp_path.exists():
            tmp_path.unlink()
    if published:
        _fsync_dir(path.parent)


def fingerprint(root: Path) -> tuple[tuple[str, str], ...]:
    """Hash of every store file except the lock. Critique must not change this."""

    if not root.exists():
        return ()
    items: list[tuple[str, str]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file():
            continue
        if path.name == ".lock" or path.name.startswith(".tmp-"):
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        items.append((path.relative_to(root).as_posix(), digest))
    return tuple(items)
