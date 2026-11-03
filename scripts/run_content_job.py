#!/usr/bin/env python3
"""Run one content_factory job behind the shared base pipeline.

Each distinct content request is an independent job: its own content_factory
task that depends only on the shared base review node.

Steps, all through Ella.get and Ella.mutate (the critics enforce readiness):
  1. Walk the base chain back from the review node.
  2. Advance perceive -> interpret -> plan -> act -> review to done, in order.
  3. open_content_factory(after=review), then active, then done.

Safe to re-run. A step already in its target state changes nothing.

    python scripts/run_content_job.py --root /var/lib/ella-brain \
        --review-id <uuid> [--job-id <uuid>]

Without --job-id a new job (new task id) is created.
"""

from __future__ import annotations

import argparse
from uuid import UUID, uuid4

from ella_brain import (
    BASE_STAGES,
    Ella,
    EntityKind,
    Status,
    TaskType,
    act,
    content_factory,
    interpret,
    open_content_factory,
    perceive,
    plan,
    review,
)

_STAGE_FUNCS = {
    TaskType.perceive: perceive,
    TaskType.interpret: interpret,
    TaskType.plan: plan,
    TaskType.act: act,
    TaskType.review: review,
}


def base_chain(ella: Ella, review_id: UUID) -> list:
    """The five base tasks in order, found by following deps back from review."""

    chain = []
    node = ella.get(EntityKind.task, review_id)
    while True:
        chain.append(node)
        if len(node.deps) > 1:
            raise SystemExit(f"{node.id} has several deps; not a base pipeline chain")
        if not node.deps:
            break
        node = ella.get(EntityKind.task, node.deps[0])
    chain.reverse()
    if [task.type for task in chain] != list(BASE_STAGES):
        found = [task.type.value for task in chain]
        raise SystemExit(f"{review_id} is not the review node of a base pipeline: {found}")
    return chain


def _show(label: str, task) -> None:
    print(f"{label:<16} {task.id}  {task.status.value:<8} v{task.version}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", required=True)
    parser.add_argument("--review-id", required=True)
    parser.add_argument("--job-id")
    args = parser.parse_args()

    ella = Ella(args.root)
    chain = base_chain(ella, UUID(args.review_id))
    owner = chain[-1].owner

    for node in chain:
        _show(node.type.value, _STAGE_FUNCS[node.type](ella, node.id, owner=owner, status=Status.done))

    job_id = UUID(args.job_id) if args.job_id else uuid4()
    job = open_content_factory(ella, owner=owner, task_id=job_id, after=chain[-1].id)
    _show("content_factory", job)
    job = content_factory(ella, job.id, owner=owner, status=Status.active)
    _show("  -> active", job)
    job = content_factory(ella, job.id, owner=owner, status=Status.done)
    _show("  -> done", job)


if __name__ == "__main__":
    main()
