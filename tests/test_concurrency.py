"""Concurrent writers.

The root lock serializes writers: a blocking flock across processes, a
non-blocking lock inside one process. The version gate (apply_stage) rejects a
write whose predecessor is no longer the max version on disk.

Processes stand in for separate writers. Barriers force every writer to start
from the same snapshot.
"""

import json
import multiprocessing
import os
import threading
from pathlib import Path
from uuid import uuid4

import pytest

from ella_brain import (
    AgentType,
    Ella,
    EntityKind,
    MutationRejected,
    Status,
    TaskType,
    Verdict,
    perceive,
)
from ella_brain._stages import _root_lock, apply_stage, load_stage, prevalidate_stage

pytestmark = pytest.mark.skipif(not hasattr(os, "fork"), reason="needs fork")

CTX = multiprocessing.get_context("fork") if hasattr(os, "fork") else None


def _setup(root: Path) -> tuple[Ella, object]:
    ella = Ella(root)
    agent_id = uuid4()
    ella.mutate(
        EntityKind.agent,
        agent_id,
        {"type": AgentType.worker, "status": Status.active, "owner": agent_id, "deps": []},
    )
    return ella, agent_id


def _task_body(agent_id: object) -> dict:
    return {
        "type": TaskType.perceive,
        "status": Status.pending,
        "owner": agent_id,
        "deps": [],
    }


def _new_task(ella: Ella, agent_id: object):
    task_id = uuid4()
    ella.mutate(EntityKind.task, task_id, _task_body(agent_id))
    return task_id


def _version_files(root: Path, task_id: object) -> list[str]:
    return sorted(path.name for path in (root / "tasks" / str(task_id)).iterdir())


def _stored_status(root: Path, task_id: object, version: int) -> str:
    path = root / "tasks" / str(task_id) / f"v{version}.json"
    return json.loads(path.read_text())["status"]


def _run(target, arg_sets: list[tuple]) -> list[tuple]:
    results = CTX.Queue()
    barrier = CTX.Barrier(len(arg_sets))
    procs = [CTX.Process(target=target, args=(*args, barrier, results)) for args in arg_sets]
    for proc in procs:
        proc.start()
    collected = [results.get(timeout=30) for _ in procs]
    for proc in procs:
        proc.join(timeout=30)
    assert [proc.exitcode for proc in procs] == [0] * len(procs)
    return collected


def _stale_apply(root, task_id, status, barrier, results):
    """Snapshot v1 and build a v2 proposal, wait for everyone, then apply."""

    try:
        stale = prevalidate_stage(
            root,
            EntityKind.task,
            task_id,
            load_stage(root, EntityKind.task, task_id),
            {"status": status},
        )
        barrier.wait(timeout=20)
        with _root_lock(root):
            apply_stage(root, EntityKind.task, stale)
        results.put((status.value, "ok"))
    except MutationRejected as exc:
        results.put((status.value, str(exc)))
    except Exception as exc:
        results.put((status.value, f"error: {exc!r}"))


def _advance(root, task_id, owner, barrier, results):
    try:
        barrier.wait(timeout=20)
        task = perceive(Ella(root), task_id, owner=owner, status=Status.done)
        results.put(("returned", task.version))
    except MutationRejected as exc:
        results.put(("rejected", str(exc)))
    except Exception as exc:
        results.put(("error", repr(exc)))


def _set_status(root, task_id, status, barrier, results):
    try:
        barrier.wait(timeout=20)
        task = Ella(root).mutate(EntityKind.task, task_id, {"status": status})
        results.put((status.value, task.version))
    except Exception as exc:
        results.put((status.value, f"error: {exc!r}"))


def test_stale_writers_are_rejected_by_the_version_gate(tmp_path: Path):
    ella, agent_id = _setup(tmp_path)
    task_id = _new_task(ella, agent_id)
    statuses = [Status.blocked, Status.active, Status.done]

    results = _run(_stale_apply, [(tmp_path, task_id, status) for status in statuses])

    winners = [label for label, outcome in results if outcome == "ok"]
    losers = [outcome for _, outcome in results if outcome != "ok"]
    assert len(winners) == 1, results
    assert len(losers) == 2 and all("version conflict" in text for text in losers), results
    assert _version_files(tmp_path, task_id) == ["v1.json", "v2.json"]
    assert _stored_status(tmp_path, task_id, 2) == winners[0]
    assert ella.get(EntityKind.task, task_id).version == 2


def test_stale_write_cannot_overwrite_an_existing_version(tmp_path: Path):
    ella, agent_id = _setup(tmp_path)
    task_id = _new_task(ella, agent_id)
    stale = prevalidate_stage(
        tmp_path,
        EntityKind.task,
        task_id,
        load_stage(tmp_path, EntityKind.task, task_id),
        {"status": Status.blocked},
    )
    ella.mutate(EntityKind.task, task_id, {"status": Status.done})
    kept = (tmp_path / "tasks" / str(task_id) / "v2.json").read_bytes()

    with _root_lock(tmp_path):
        with pytest.raises(MutationRejected, match="version conflict"):
            apply_stage(tmp_path, EntityKind.task, stale)

    assert (tmp_path / "tasks" / str(task_id) / "v2.json").read_bytes() == kept
    assert _version_files(tmp_path, task_id) == ["v1.json", "v2.json"]


def test_racing_advances_on_one_node_write_exactly_once(tmp_path: Path):
    ella, agent_id = _setup(tmp_path)
    node = _new_task(ella, agent_id)

    results = _run(_advance, [(tmp_path, node, agent_id)] * 5)

    kinds = [kind for kind, _ in results]
    assert "error" not in kinds, results
    assert "returned" in kinds
    assert all(value == 2 for kind, value in results if kind == "returned"), results
    assert all("does not change" in value for kind, value in results if kind == "rejected")
    assert _version_files(tmp_path, node) == ["v1.json", "v2.json"]
    assert ella.get(EntityKind.task, node).status is Status.done


def test_racing_writers_with_different_patches_lose_no_update(tmp_path: Path):
    ella, agent_id = _setup(tmp_path)
    node = _new_task(ella, agent_id)
    statuses = [Status.blocked, Status.active, Status.done]

    results = _run(_set_status, [(tmp_path, node, status) for status in statuses])

    assert all(isinstance(version, int) for _, version in results), results
    assert sorted(version for _, version in results) == [2, 3, 4]
    assert _version_files(tmp_path, node) == ["v1.json", "v2.json", "v3.json", "v4.json"]
    history = [_stored_status(tmp_path, node, number) for number in (2, 3, 4)]
    assert sorted(history) == sorted(status.value for status in statuses)
    for label, version in results:
        assert _stored_status(tmp_path, node, version) == label


def test_a_second_thread_is_rejected_while_a_mutate_is_in_flight(tmp_path: Path):
    ella, agent_id = _setup(tmp_path)
    entered = threading.Event()
    release = threading.Event()

    class Hold:
        name = "hold-critic"

        def critique(self, before, proposed, view):
            entered.set()
            assert release.wait(10)
            return Verdict(self.name, True, "ok")

    class Allow:
        name = "allow-critic"

        def critique(self, before, proposed, view):
            return Verdict(self.name, True, "ok")

    first, second = uuid4(), uuid4()
    outcome: dict = {}

    def slow_writer() -> None:
        try:
            held = Ella(tmp_path, critics=(Hold(), Allow()))
            outcome["first"] = held.mutate(EntityKind.task, first, _task_body(agent_id))
        except Exception as exc:
            outcome["first"] = exc

    thread = threading.Thread(target=slow_writer)
    thread.start()
    try:
        assert entered.wait(10)
        with pytest.raises(MutationRejected):
            ella.mutate(EntityKind.task, second, _task_body(agent_id))
        assert not (tmp_path / "tasks" / str(second)).exists()
    finally:
        release.set()
        thread.join(10)

    assert not isinstance(outcome["first"], Exception), outcome
    assert outcome["first"].version == 1
    assert _version_files(tmp_path, first) == ["v1.json"]
