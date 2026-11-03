"""Domain task types and the content_factory helper. The graph rules still hold."""

import inspect
from pathlib import Path
from uuid import uuid4

import pytest

from ella_brain import (
    BASE_STAGES,
    AgentType,
    Ella,
    EntityKind,
    MutationRejected,
    Status,
    TaskType,
    act,
    content_factory,
    interpret,
    open_content_factory,
    open_pipeline,
    perceive,
    plan,
    review,
)
from ella_brain import domains as domains_module


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


def _base(ella: Ella, agent_id: object) -> dict:
    ids = {stage: uuid4() for stage in BASE_STAGES}
    open_pipeline(ella, owner=agent_id, ids=ids)
    return ids


def _finish_base(ella: Ella, agent_id: object, ids: dict) -> None:
    for fn, stage in (
        (perceive, TaskType.perceive),
        (interpret, TaskType.interpret),
        (plan, TaskType.plan),
        (act, TaskType.act),
        (review, TaskType.review),
    ):
        fn(ella, ids[stage], owner=agent_id, status=Status.done)


def test_domains_source_has_no_filesystem():
    source = inspect.getsource(domains_module)
    assert "_io" not in source
    assert "open(" not in source
    assert "write_text" not in source
    assert "mkdir" not in source


def test_closed_enum_accepts_domain_types_and_rejects_free_strings(tmp_path: Path):
    ella, agent_id = _root_agent(tmp_path)
    for member in (TaskType.content_factory, TaskType.medical_crm):
        task_id = uuid4()
        created = ella.mutate(
            EntityKind.task,
            task_id,
            {"type": member, "status": Status.pending, "owner": agent_id, "deps": []},
        )
        assert created.type is member
        assert created.version == 1
    with pytest.raises(MutationRejected, match="free strings"):
        ella.mutate(
            EntityKind.task,
            uuid4(),
            {"type": "content_factory2", "status": "pending", "owner": agent_id, "deps": []},
        )


def test_open_pipeline_stays_on_the_original_five(tmp_path: Path):
    ella, agent_id = _root_agent(tmp_path)
    assert list(BASE_STAGES) == list(TaskType)[:5]
    with pytest.raises(MutationRejected, match="exactly the five"):
        open_pipeline(ella, owner=agent_id, ids={stage: uuid4() for stage in TaskType})
    created = open_pipeline(ella, owner=agent_id, ids={s: uuid4() for s in BASE_STAGES})
    assert set(created) == set(BASE_STAGES)


def test_open_content_factory_hangs_off_the_completion_node(tmp_path: Path):
    ella, agent_id = _root_agent(tmp_path)
    ids = _base(ella, agent_id)
    cf_id = uuid4()
    made = open_content_factory(ella, owner=agent_id, task_id=cf_id, after=ids[TaskType.review])
    assert made.type is TaskType.content_factory
    assert made.status is Status.pending
    assert made.deps == [ids[TaskType.review]]
    assert made.version == 1
    again = open_content_factory(ella, owner=agent_id, task_id=cf_id, after=ids[TaskType.review])
    assert again.version == 1


def test_content_factory_cannot_run_before_the_base_pipeline_is_done(tmp_path: Path):
    ella, agent_id = _root_agent(tmp_path)
    ids = _base(ella, agent_id)
    cf_id = uuid4()
    open_content_factory(ella, owner=agent_id, task_id=cf_id, after=ids[TaskType.review])
    with pytest.raises(MutationRejected, match="done"):
        content_factory(ella, cf_id, owner=agent_id, status=Status.active)
    assert ella.get(EntityKind.task, cf_id).version == 1

    _finish_base(ella, agent_id, ids)
    active = content_factory(ella, cf_id, owner=agent_id, status=Status.active)
    assert active.status is Status.active
    finished = content_factory(ella, cf_id, owner=agent_id, status=Status.done)
    assert finished.status is Status.done


def test_open_content_factory_requires_a_real_review_node(tmp_path: Path):
    ella, agent_id = _root_agent(tmp_path)
    ids = _base(ella, agent_id)
    cf_id = uuid4()
    with pytest.raises(MutationRejected, match="not review"):
        open_content_factory(ella, owner=agent_id, task_id=cf_id, after=ids[TaskType.act])
    with pytest.raises(MutationRejected, match="not found"):
        open_content_factory(ella, owner=agent_id, task_id=cf_id, after=uuid4())
    assert not (tmp_path / "tasks" / str(cf_id)).exists()


def test_graph_critic_still_blocks_cycles_for_domain_tasks(tmp_path: Path):
    ella, agent_id = _root_agent(tmp_path)
    ids = _base(ella, agent_id)
    cf_id = uuid4()
    open_content_factory(ella, owner=agent_id, task_id=cf_id, after=ids[TaskType.review])

    review_id = ids[TaskType.review]
    with pytest.raises(MutationRejected, match="cycle"):
        ella.mutate(EntityKind.task, review_id, {"deps": [ids[TaskType.act], cf_id]})
    assert ella.get(EntityKind.task, review_id).deps == [ids[TaskType.act]]

    with pytest.raises(MutationRejected, match="self"):
        content_factory(ella, cf_id, owner=agent_id, deps=[cf_id])
    with pytest.raises(MutationRejected, match="missing dep"):
        content_factory(ella, cf_id, owner=agent_id, deps=[uuid4()])
    assert ella.get(EntityKind.task, cf_id).version == 1
