"""Combined hardening: publication collision through the full gate.

Why this test exists, and why the two slice files do not cover it:

- tests/test_atomic_write.py drives ella_brain._io.atomic_write
  directly. It bypasses _root_lock, prevalidation, the two-critic
  stage, apply_stage and reload_verify, so it cannot prove the gate
  releases the process-local lock after a publication refusal, nor
  that the gate's error path behaves with the new publish code.
- tests/test_lock_timeout.py never triggers a publication
  collision: its contender path times out before any entity
  publication, and its success paths publish to empty destinations.

This test drives the complete public Ella.mutate() path (lock
acquire, prevalidation, critique, apply, hard-link publication)
with a destination planted at the shared fsync point, then proves
the store stays usable: no leaked process-local lock, and a
follow-up mutation in the same process publishes cleanly.
"""

import os
from pathlib import Path
from uuid import uuid4

import pytest

from ella_brain import AgentType, Ella, EntityKind, Status, TaskType
from ella_brain import _stages as stages
from ella_brain.errors import VerificationError


def test_public_mutate_collision_refuses_overwrite_and_releases_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Collision inside a real gate mutation: planted bytes survive,
    the refusal propagates, no temp file leaks, the process-local
    lock is free, and a follow-up mutation publishes cleanly."""
    agent_id = uuid4()
    Ella(tmp_path).mutate(
        EntityKind.agent,
        agent_id,
        {
            "type": AgentType.companion,
            "status": Status.active,
            "owner": agent_id,
            "deps": [],
        },
    )

    task_id = uuid4()
    dest = tmp_path / "tasks" / str(task_id) / "v1.json"
    real_fsync = os.fsync
    state = {"planted": False}

    def planting_fsync(fd, *args, **kwargs):
        result = real_fsync(fd, *args, **kwargs)
        if not state["planted"]:
            state["planted"] = True
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(b"PLANTED")
        return result

    monkeypatch.setattr("ella_brain._io.os.fsync", planting_fsync)
    raised = None
    try:
        Ella(tmp_path).mutate(
            EntityKind.task,
            task_id,
            {
                "type": TaskType.perceive,
                "status": Status.pending,
                "owner": agent_id,
                "deps": [],
            },
        )
    except VerificationError as exc:
        raised = exc
    # Bytes first: on old publish code this is the assertion that
    # fails, proving the overwrite rather than only a missing
    # exception.
    assert state["planted"]
    assert dest.read_bytes() == b"PLANTED", "planted destination was overwritten"
    assert raised is not None
    assert "refusing to overwrite" in str(raised)
    assert sorted(tmp_path.rglob(".tmp-*")) == []
    assert not stages._THREAD_LOCK.locked()

    # Same process, same store, clean destination: proves the failed
    # mutation left no leaked lock and the gate is still healthy.
    follow_id = uuid4()
    created = Ella(tmp_path).mutate(
        EntityKind.task,
        follow_id,
        {
            "type": TaskType.perceive,
            "status": Status.pending,
            "owner": agent_id,
            "deps": [],
        },
    )
    assert created.version == 1
    read_back = Ella(tmp_path).get(EntityKind.task, follow_id)
    assert read_back.version == 1
    assert read_back.owner == agent_id
    assert read_back.status == Status.pending
    assert set(tmp_path.rglob("v*.json")) == {
        tmp_path / "agents" / str(agent_id) / "v1.json",
        dest,
        tmp_path / "tasks" / str(follow_id) / "v1.json",
    }
