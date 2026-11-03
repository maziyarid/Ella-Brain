"""Five stage functions around mutate.

perceive -> interpret -> plan -> act -> review.

They call Ella.get and Ella.mutate only. They do not read or write files,
and they do not remember tasks between calls.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any
from uuid import UUID

from ella_brain.errors import MutationRejected, NotFound
from ella_brain.gate import Ella
from ella_brain.models import EntityKind, Status, Task, TaskType

_ORDER = (
    TaskType.perceive,
    TaskType.interpret,
    TaskType.plan,
    TaskType.act,
    TaskType.review,
)

# The five stages open_pipeline builds. TaskType also holds domain members, so
# callers that mean "the base chain" use this, not TaskType.
BASE_STAGES = _ORDER


def _uuid(value: Any, field_name: str) -> UUID:
    try:
        return value if isinstance(value, UUID) else UUID(str(value))
    except (TypeError, ValueError, AttributeError) as exc:
        raise MutationRejected(f"free strings are banned; {field_name} must be a UUID") from exc


def _stage(
    ella: Ella,
    stage: TaskType,
    task_id: UUID | str,
    *,
    owner: UUID | str,
    deps: Sequence[UUID | str] | None,
    status: Status | None,
) -> Task:
    task_uuid = _uuid(task_id, "id")
    owner_uuid = _uuid(owner, "owner")
    try:
        current = ella.get(EntityKind.task, task_uuid)
    except NotFound:
        current = None
    if current is None:
        chosen = status if status is not None else Status.pending
        body = {
            "type": stage.value,
            "status": chosen.value,
            "owner": str(owner_uuid),
            "deps": [str(_uuid(dep, "deps")) for dep in (deps or ())],
        }
        return ella.mutate(EntityKind.task, task_uuid, body)
    if current.type is not stage:
        raise MutationRejected(
            f"task {task_uuid} is type {current.type.value}, not {stage.value}"
        )
    patch: dict[str, Any] = {}
    if status is not None and status is not current.status:
        patch["status"] = status.value
    if deps is not None:
        next_deps = [_uuid(dep, "deps") for dep in deps]
        if next_deps != list(current.deps):
            patch["deps"] = [str(dep) for dep in next_deps]
    if owner_uuid != current.owner:
        patch["owner"] = str(owner_uuid)
    if not patch:
        return current
    return ella.mutate(EntityKind.task, task_uuid, patch)


def perceive(
    ella: Ella,
    task_id: UUID | str,
    *,
    owner: UUID | str,
    deps: Sequence[UUID | str] | None = None,
    status: Status | None = None,
) -> Task:
    return _stage(ella, TaskType.perceive, task_id, owner=owner, deps=deps, status=status)


def interpret(
    ella: Ella,
    task_id: UUID | str,
    *,
    owner: UUID | str,
    deps: Sequence[UUID | str] | None = None,
    status: Status | None = None,
) -> Task:
    return _stage(ella, TaskType.interpret, task_id, owner=owner, deps=deps, status=status)


def plan(
    ella: Ella,
    task_id: UUID | str,
    *,
    owner: UUID | str,
    deps: Sequence[UUID | str] | None = None,
    status: Status | None = None,
) -> Task:
    return _stage(ella, TaskType.plan, task_id, owner=owner, deps=deps, status=status)


def act(
    ella: Ella,
    task_id: UUID | str,
    *,
    owner: UUID | str,
    deps: Sequence[UUID | str] | None = None,
    status: Status | None = None,
) -> Task:
    return _stage(ella, TaskType.act, task_id, owner=owner, deps=deps, status=status)


def review(
    ella: Ella,
    task_id: UUID | str,
    *,
    owner: UUID | str,
    deps: Sequence[UUID | str] | None = None,
    status: Status | None = None,
) -> Task:
    return _stage(ella, TaskType.review, task_id, owner=owner, deps=deps, status=status)


_FUNCS = {
    TaskType.perceive: perceive,
    TaskType.interpret: interpret,
    TaskType.plan: plan,
    TaskType.act: act,
    TaskType.review: review,
}


def open_pipeline(
    ella: Ella,
    *,
    owner: UUID | str,
    ids: Mapping[TaskType, UUID | str],
) -> dict[TaskType, Task]:
    """Create the five tasks, each depending on the previous stage. Via mutate only."""

    if set(ids) != set(_ORDER):
        raise MutationRejected("open_pipeline requires exactly the five stage ids")
    owner_uuid = _uuid(owner, "owner")
    created: dict[TaskType, Task] = {}
    previous: UUID | None = None
    for stage in _ORDER:
        deps: tuple[UUID, ...] = () if previous is None else (previous,)
        created[stage] = _FUNCS[stage](
            ella,
            _uuid(ids[stage], "id"),
            owner=owner_uuid,
            deps=deps,
        )
        previous = created[stage].id
    return created
