"""The five stage functions may only use get and mutate."""

import inspect
from pathlib import Path
from uuid import uuid4

import pytest

from ella_brain import (
    AgentType,
    BASE_STAGES,
    Ella,
    EntityKind,
    MutationRejected,
    Status,
    TaskType,
    act,
    interpret,
    open_pipeline,
    perceive,
    plan,
    review,
)
from ella_brain import pipeline as pipeline_module


def _root_agent(tmp_path: Path) -> tuple[Ella, object]:
    ella = Ella(tmp_path)
    agent_id = uuid4()
    ella.mutate(
        EntityKind.agent,
        agent_id,
        {
            "type": AgentType.worker,
            "status": Status.active,
            "owner": agent_id,
            "deps": [],
        },
    )
    return ella, agent_id


def test_pipeline_source_has_no_filesystem():
    source = inspect.getsource(pipeline_module)
    assert "_io" not in source
    assert "open(" not in source
    assert "write_text" not in source
    assert "mkdir" not in source


def test_open_pipeline_and_stage_advance(tmp_path: Path):
    ella, agent_id = _root_agent(tmp_path)
    ids = {stage: uuid4() for stage in BASE_STAGES}
    created = open_pipeline(ella, owner=agent_id, ids=ids)
    assert [created[stage].type for stage in BASE_STAGES] == list(BASE_STAGES)
    assert created[TaskType.perceive].deps == []
    assert created[TaskType.interpret].deps == [ids[TaskType.perceive]]
    assert created[TaskType.review].deps == [ids[TaskType.act]]
    for stage, task_id in ids.items():
        path = tmp_path / "tasks" / str(task_id) / "v1.json"
        assert path.is_file()
        assert created[stage].version == 1

    done = perceive(ella, ids[TaskType.perceive], owner=agent_id, status=Status.done)
    assert done.version == 2
    assert done.status is Status.done

    active = interpret(
        ella,
        ids[TaskType.interpret],
        owner=agent_id,
        deps=[ids[TaskType.perceive]],
        status=Status.active,
    )
    assert active.status is Status.active

    with pytest.raises(MutationRejected, match="done"):
        plan(
            ella,
            ids[TaskType.plan],
            owner=agent_id,
            deps=[ids[TaskType.interpret]],
            status=Status.active,
        )
    assert ella.get(EntityKind.task, ids[TaskType.plan]).version == 1

    again = perceive(ella, ids[TaskType.perceive], owner=agent_id, status=Status.done)
    assert again.version == 2

    with pytest.raises(MutationRejected, match="not perceive"):
        perceive(ella, ids[TaskType.interpret], owner=agent_id, status=Status.done)


def test_later_stages_are_real_functions(tmp_path: Path):
    ella, agent_id = _root_agent(tmp_path)
    ids = {stage: uuid4() for stage in BASE_STAGES}
    open_pipeline(ella, owner=agent_id, ids=ids)
    perceive(ella, ids[TaskType.perceive], owner=agent_id, status=Status.done)
    interpret(
        ella,
        ids[TaskType.interpret],
        owner=agent_id,
        deps=[ids[TaskType.perceive]],
        status=Status.done,
    )
    plan(
        ella,
        ids[TaskType.plan],
        owner=agent_id,
        deps=[ids[TaskType.interpret]],
        status=Status.done,
    )
    act(
        ella,
        ids[TaskType.act],
        owner=agent_id,
        deps=[ids[TaskType.plan]],
        status=Status.done,
    )
    reviewed = review(
        ella,
        ids[TaskType.review],
        owner=agent_id,
        deps=[ids[TaskType.act]],
        status=Status.active,
    )
    assert reviewed.type is TaskType.review
    assert reviewed.status is Status.active
    assert reviewed.version == 2
