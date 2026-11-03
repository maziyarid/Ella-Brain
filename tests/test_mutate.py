"""Gate behavior: versioned files, consensus, no cache, no partial writes."""

import json
from pathlib import Path
from uuid import uuid4

import pytest

from ella_brain import (
    AgentType,
    ConsensusRejected,
    Ella,
    EllaError,
    EntityKind,
    MutationRejected,
    NotFound,
    Status,
    TaskType,
    VerificationError,
    Verdict,
)
from ella_brain._io import atomic_write, dump_bytes


def _agent_patch(agent_id, **overrides):
    body = {
        "type": AgentType.companion,
        "status": Status.active,
        "owner": agent_id,
        "deps": [],
    }
    body.update(overrides)
    return body


def _task_patch(owner, **overrides):
    body = {
        "type": TaskType.perceive,
        "status": Status.pending,
        "owner": owner,
        "deps": [],
    }
    body.update(overrides)
    return body


def test_create_get_and_version_files(tmp_path: Path):
    ella = Ella(tmp_path)
    agent_id = uuid4()
    created = ella.mutate(EntityKind.agent, agent_id, _agent_patch(agent_id))
    assert created.version == 1
    assert ella.get(EntityKind.agent, agent_id) == created

    task_id = uuid4()
    task = ella.mutate(EntityKind.task, task_id, _task_patch(agent_id))
    path = tmp_path / "tasks" / str(task_id) / "v1.json"
    assert path.is_file()
    original = path.read_bytes()
    stored = json.loads(original)
    assert set(stored) == {
        "id",
        "type",
        "status",
        "owner",
        "deps",
        "version",
        "created",
        "updated",
    }
    assert stored["version"] == 1
    assert task.status is Status.pending

    updated = ella.mutate(
        EntityKind.task,
        task_id,
        {"status": Status.done},
    )
    assert updated.version == 2
    assert updated.created == task.created
    assert path.read_bytes() == original
    v1 = json.loads((tmp_path / "tasks" / str(task_id) / "v1.json").read_text())
    assert v1["status"] == "pending"
    assert ella.get("task", str(task_id)).version == 2


def test_current_is_max_version_even_with_a_gap(tmp_path: Path):
    ella = Ella(tmp_path)
    agent_id = uuid4()
    ella.mutate(EntityKind.agent, agent_id, _agent_patch(agent_id))
    task_id = uuid4()
    first = ella.mutate(EntityKind.task, task_id, _task_patch(agent_id))
    skipped = first.model_copy(update={"version": 3, "status": Status.blocked})
    atomic_write(
        tmp_path / "tasks" / str(task_id) / "v3.json",
        dump_bytes(skipped),
    )
    (tmp_path / "tasks" / str(task_id) / "notes.txt").write_text("ignore me")
    assert ella.get(EntityKind.task, task_id).version == 3
    nxt = ella.mutate(EntityKind.task, task_id, {"status": Status.pending})
    assert nxt.version == 4
    assert (tmp_path / "tasks" / str(task_id) / "v4.json").is_file()
    assert not (tmp_path / "tasks" / str(task_id) / "v2.json").exists()


def test_rejected_patch_writes_nothing(tmp_path: Path):
    ella = Ella(tmp_path)
    task_id = uuid4()
    with pytest.raises(MutationRejected, match="missing owner"):
        ella.mutate(EntityKind.task, task_id, _task_patch(uuid4()))
    assert not (tmp_path / "tasks" / str(task_id)).exists()

    agent_id = uuid4()
    ella.mutate(EntityKind.agent, agent_id, _agent_patch(agent_id))
    ella.mutate(EntityKind.task, task_id, _task_patch(agent_id))
    before = (tmp_path / "tasks" / str(task_id) / "v1.json").read_bytes()
    with pytest.raises(MutationRejected, match="extra fields"):
        ella.mutate(EntityKind.task, task_id, {"note": "nope"})
    with pytest.raises(MutationRejected, match="UNKNOWN"):
        ella.mutate(EntityKind.task, task_id, {"status": "UNKNOWN"})
    with pytest.raises(MutationRejected, match="free strings"):
        ella.mutate(EntityKind.task, task_id, {"type": "free prose"})
    with pytest.raises(MutationRejected, match="gate-owned"):
        ella.mutate(EntityKind.task, task_id, {"version": 9})
    with pytest.raises(MutationRejected, match="does not change"):
        ella.mutate(EntityKind.task, task_id, {"status": Status.pending})
    assert list((tmp_path / "tasks" / str(task_id)).glob("v*.json")) == [
        tmp_path / "tasks" / str(task_id) / "v1.json"
    ]
    assert (tmp_path / "tasks" / str(task_id) / "v1.json").read_bytes() == before


def test_dependency_rules(tmp_path: Path):
    ella = Ella(tmp_path)
    agent_id = uuid4()
    ella.mutate(EntityKind.agent, agent_id, _agent_patch(agent_id))
    first = uuid4()
    second = uuid4()
    ella.mutate(EntityKind.task, first, _task_patch(agent_id, type=TaskType.perceive))
    ella.mutate(
        EntityKind.task,
        second,
        _task_patch(agent_id, type=TaskType.interpret, deps=[first]),
    )
    with pytest.raises(MutationRejected, match="done"):
        ella.mutate(EntityKind.task, second, {"status": Status.active})
    assert ella.get(EntityKind.task, second).version == 1

    ella.mutate(EntityKind.task, second, {"status": Status.blocked})
    ella.mutate(EntityKind.task, first, {"status": Status.done})
    active = ella.mutate(EntityKind.task, second, {"status": Status.active})
    assert active.status is Status.active

    with pytest.raises(MutationRejected, match="cycle"):
        ella.mutate(EntityKind.task, first, {"deps": [second]})
    assert ella.get(EntityKind.task, first).deps == []

    with pytest.raises(MutationRejected, match="self"):
        ella.mutate(EntityKind.task, first, {"deps": [first]})
    with pytest.raises(MutationRejected, match="missing dep"):
        ella.mutate(EntityKind.task, first, {"deps": [uuid4()]})


def test_consensus_split_does_not_write(tmp_path: Path):
    class Allow:
        name = "allow-model"

        def critique(self, before, proposed, view):
            return Verdict(self.name, True, "ok")

    class Deny:
        name = "deny-model"

        def critique(self, before, proposed, view):
            return Verdict(self.name, False, "no")

    ella = Ella(tmp_path, critics=(Allow(), Deny()))
    agent_id = uuid4()
    with pytest.raises(ConsensusRejected) as caught:
        ella.mutate(EntityKind.agent, agent_id, _agent_patch(agent_id))
    assert caught.value.verdicts[0].allow is True
    assert caught.value.verdicts[1].allow is False
    assert not (tmp_path / "agents" / str(agent_id) / "v1.json").exists()


def test_reentrant_mutate_and_store_tamper_do_not_commit(tmp_path: Path):
    class Reenter:
        name = "reenter"

        def critique(self, before, proposed, view):
            Ella(tmp_path).mutate(
                EntityKind.agent,
                uuid4(),
                _agent_patch(uuid4()),
            )
            return Verdict(self.name, True, "should not get here")

    class Tamper:
        name = "tamper"

        def critique(self, before, proposed, view):
            target = view._root / "tamper.txt"
            target.write_text("nope")
            return Verdict(self.name, True, "touched disk")

    class Allow:
        name = "allow-model"

        def critique(self, before, proposed, view):
            return Verdict(self.name, True, "ok")

    agent_id = uuid4()
    with pytest.raises(MutationRejected, match="re-entrant"):
        Ella(tmp_path, critics=(Allow(), Reenter())).mutate(
            EntityKind.agent, agent_id, _agent_patch(agent_id)
        )
    assert not (tmp_path / "agents" / str(agent_id) / "v1.json").exists()

    other = uuid4()
    with pytest.raises(MutationRejected, match="changed the store"):
        Ella(tmp_path, critics=(Allow(), Tamper())).mutate(
            EntityKind.agent, other, _agent_patch(other)
        )
    assert not (tmp_path / "agents" / str(other) / "v1.json").exists()


def test_corrupt_max_version_fails_closed(tmp_path: Path):
    ella = Ella(tmp_path)
    agent_id = uuid4()
    ella.mutate(EntityKind.agent, agent_id, _agent_patch(agent_id))
    task_id = uuid4()
    ella.mutate(EntityKind.task, task_id, _task_patch(agent_id))
    (tmp_path / "tasks" / str(task_id) / "v2.json").write_text('{"version": 2}\n')
    with pytest.raises(VerificationError):
        ella.get(EntityKind.task, task_id)


def test_no_entity_memory(tmp_path: Path):
    ella = Ella(tmp_path)
    agent_id = uuid4()
    first = ella.mutate(EntityKind.agent, agent_id, _agent_patch(agent_id))
    edited = first.model_copy(update={"version": 2, "status": Status.blocked})
    atomic_write(tmp_path / "agents" / str(agent_id) / "v2.json", dump_bytes(edited))
    assert ella.get(EntityKind.agent, agent_id).version == 2
    assert ella.get(EntityKind.agent, agent_id).status is Status.blocked
    with pytest.raises(AttributeError):
        ella.memory = {}  # type: ignore[attr-defined]
    assert Ella.__slots__ == ("root", "_critics")


def test_get_missing_and_banned_kind(tmp_path: Path):
    ella = Ella(tmp_path)
    with pytest.raises(NotFound):
        ella.get(EntityKind.task, uuid4())
    with pytest.raises(EllaError, match="UNKNOWN"):
        ella.get("UNKNOWN", uuid4())
    with pytest.raises(EllaError, match="free strings"):
        ella.get("brain", uuid4())


def test_both_default_critics_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    from ella_brain._critics import GraphCritic, SchemaCritic

    calls: list[str] = []
    schema = SchemaCritic.critique
    graph = GraphCritic.critique

    def schema_spy(self, before, proposed, view):
        calls.append(self.name)
        return schema(self, before, proposed, view)

    def graph_spy(self, before, proposed, view):
        calls.append(self.name)
        return graph(self, before, proposed, view)

    monkeypatch.setattr(SchemaCritic, "critique", schema_spy)
    monkeypatch.setattr(GraphCritic, "critique", graph_spy)
    ella = Ella(tmp_path)
    agent_id = uuid4()
    ella.mutate(EntityKind.agent, agent_id, _agent_patch(agent_id))
    assert calls == ["schema-critic", "graph-critic"]


def test_same_critic_twice_rejected(tmp_path: Path):
    class Allow:
        name = "same"

        def critique(self, before, proposed, view):
            return Verdict(self.name, True, "ok")

    with pytest.raises(ValueError, match="independent"):
        Ella(tmp_path, critics=(Allow(), Allow()))

