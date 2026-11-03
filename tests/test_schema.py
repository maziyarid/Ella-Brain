"""Closed schemas: no UNKNOWN, no extra fields, no free strings."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from ella_brain import Agent, AgentType, Status, Task, TaskType


def _doc(**overrides):
    now = datetime.now(timezone.utc)
    base = {
        "id": uuid4(),
        "type": TaskType.perceive,
        "status": Status.pending,
        "owner": uuid4(),
        "deps": [],
        "version": 1,
        "created": now,
        "updated": now,
    }
    base.update(overrides)
    return base


def test_task_round_trip():
    task = Task.model_validate(_doc())
    assert task.status is Status.pending
    assert task.version == 1


@pytest.mark.parametrize("status", ["UNKNOWN", "unknown", "Unknown"])
def test_status_unknown_is_banned(status):
    with pytest.raises(ValidationError, match="UNKNOWN"):
        Task.model_validate(_doc(status=status))


def test_status_free_string_is_banned():
    with pytest.raises(ValidationError, match="free strings"):
        Task.model_validate(_doc(status="in progress"))


def test_type_free_string_is_banned():
    with pytest.raises(ValidationError, match="free strings"):
        Task.model_validate(_doc(type="write a poem"))


def test_owner_free_string_is_banned():
    with pytest.raises(ValidationError, match="free strings"):
        Task.model_validate(_doc(owner="Ella"))


def test_extra_field_is_banned():
    with pytest.raises(ValidationError, match="extra fields"):
        Task.model_validate(_doc(note="remember this"))


def test_deps_must_be_uuids():
    with pytest.raises(ValidationError, match="free strings"):
        Task.model_validate(_doc(deps=["the other one"]))


def test_duplicate_and_self_deps():
    dep = uuid4()
    with pytest.raises(ValidationError, match="unique"):
        Task.model_validate(_doc(deps=[dep, dep]))
    own = uuid4()
    with pytest.raises(ValidationError, match="self"):
        Task.model_validate(_doc(id=own, deps=[own]))


def test_naive_datetime_rejected():
    with pytest.raises(ValidationError, match="timezone-aware"):
        Task.model_validate(_doc(created=datetime.now()))


def test_agent_enum_closed():
    now = datetime.now(timezone.utc)
    agent = Agent.model_validate(
        {
            "id": uuid4(),
            "type": AgentType.companion,
            "status": "pending",
            "owner": uuid4(),
            "deps": [],
            "version": 1,
            "created": now,
            "updated": now,
        }
    )
    assert agent.type is AgentType.companion
    with pytest.raises(ValidationError):
        Agent.model_validate(
            {
                "id": uuid4(),
                "type": "friend",
                "status": "pending",
                "owner": uuid4(),
                "deps": [],
                "version": 1,
                "created": now,
                "updated": now,
            }
        )
