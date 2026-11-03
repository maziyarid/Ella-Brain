"""Domain helpers on top of the base pipeline.

Same rules as pipeline.py: they call Ella.get and Ella.mutate only, through the
shared stage writer. They do not read or write files and keep no state. The gate
and both critics still decide every write, so cycles, missing deps, and an
active or done task with unfinished deps are rejected exactly as for the five
base stages.
"""

from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from ella_brain.errors import MutationRejected, NotFound
from ella_brain.gate import Ella
from ella_brain.models import EntityKind, Status, Task, TaskType
from ella_brain.pipeline import _stage, _uuid


def content_factory(
    ella: Ella,
    task_id: UUID | str,
    *,
    owner: UUID | str,
    deps: Sequence[UUID | str] | None = None,
    status: Status | None = None,
) -> Task:
    """Create or advance one content_factory task. Same shape as the five stage functions."""

    return _stage(
        ella, TaskType.content_factory, task_id, owner=owner, deps=deps, status=status
    )


def open_content_factory(
    ella: Ella,
    *,
    owner: UUID | str,
    task_id: UUID | str,
    after: UUID | str,
) -> Task:
    """Open a content_factory task behind a base pipeline.

    `after` is the pipeline's completion node, its review task. The new task
    starts pending and depends on that node alone, so it cannot become active
    or done until the review is done. Calling again with the same ids changes
    nothing.
    """

    after_uuid = _uuid(after, "after")
    try:
        node = ella.get(EntityKind.task, after_uuid)
    except NotFound as exc:
        raise MutationRejected(f"completion node {after_uuid} not found") from exc
    if node.type is not TaskType.review:
        raise MutationRejected(
            f"completion node {after_uuid} is type {node.type.value}, not review"
        )
    return content_factory(ella, task_id, owner=owner, deps=(after_uuid,))
