"""The only operations Ella gets: get and mutate.

No cached entities. Every call reads the version files.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any
from uuid import UUID

from ella_brain._critics import default_critics
from ella_brain._stages import load_stage, run_mutate
from ella_brain.errors import EllaError, NotFound
from ella_brain.models import EntityKind


def _kind(value: Any) -> EntityKind:
    if isinstance(value, str) and value.strip().lower() == "unknown":
        raise EllaError("kind: UNKNOWN is banned")
    try:
        return value if isinstance(value, EntityKind) else EntityKind(value)
    except ValueError as exc:
        raise EllaError("free strings are banned; kind must be task or agent") from exc


def _uuid(value: Any) -> UUID:
    if isinstance(value, UUID):
        return value
    if isinstance(value, str) and value.strip().lower() == "unknown":
        raise EllaError("id: UNKNOWN is banned")
    try:
        return UUID(str(value))
    except (TypeError, ValueError, AttributeError) as exc:
        raise EllaError("free strings are banned; id must be a UUID") from exc


def get(kind: EntityKind | str, entity_id: UUID | str, *, root: Path) -> Any:
    """Return the current document (max version). Always from disk."""

    resolved_kind = _kind(kind)
    resolved_id = _uuid(entity_id)
    found = load_stage(Path(root), resolved_kind, resolved_id)
    if found is None:
        raise NotFound(f"{resolved_kind.value} {resolved_id} not found")
    return found


def mutate(
    kind: EntityKind | str,
    entity_id: UUID | str,
    patch: Mapping[str, Any],
    *,
    root: Path,
    critics: tuple[Any, Any] | None = None,
) -> Any:
    """load -> prevalidate -> two-model consensus -> version++ atomic write -> reload."""

    return run_mutate(Path(root), _kind(kind), _uuid(entity_id), patch, critics)


class Ella:
    """Handle for one store directory.

    Holds the directory and the two critique models. Holds no tasks, agents,
    or version cache. Filesystem access stays inside get and mutate.
    """

    __slots__ = ("root", "_critics")

    def __init__(self, root: Path | str, critics: tuple[Any, Any] | None = None) -> None:
        pair = default_critics() if critics is None else critics
        if len(pair) != 2 or getattr(pair[0], "name", None) == getattr(pair[1], "name", None):
            raise ValueError("exactly two independent critique models are required")
        object.__setattr__(self, "root", Path(root))
        object.__setattr__(self, "_critics", pair)

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("Ella stores no entity state")

    def get(self, kind: EntityKind | str, entity_id: UUID | str) -> Any:
        return get(kind, entity_id, root=self.root)

    def mutate(
        self,
        kind: EntityKind | str,
        entity_id: UUID | str,
        patch: Mapping[str, Any],
    ) -> Any:
        return mutate(kind, entity_id, patch, root=self.root, critics=self._critics)
