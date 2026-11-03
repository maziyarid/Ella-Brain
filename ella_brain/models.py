"""External schemas only.

Closed enums and UUIDs. No free strings. UNKNOWN is not a value.
Extra fields are rejected.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_BANNED = frozenset({"unknown"})


class Status(str, Enum):
    pending = "pending"
    active = "active"
    blocked = "blocked"
    done = "done"


class TaskType(str, Enum):
    """Five base pipeline stages, then domain types. Adding a member is a schema change.

    The first five are the stages open_pipeline builds (pipeline.BASE_STAGES).
    Domain members are created by the helpers in ella_brain.domains.
    """

    perceive = "perceive"
    interpret = "interpret"
    plan = "plan"
    act = "act"
    review = "review"
    content_factory = "content_factory"
    medical_crm = "medical_crm"


class AgentType(str, Enum):
    companion = "companion"
    critic = "critic"
    worker = "worker"
    orchestrator = "orchestrator"


class EntityKind(str, Enum):
    task = "task"
    agent = "agent"

    @property
    def dirname(self) -> str:
        if self is EntityKind.task:
            return "tasks"
        return "agents"


def _reject_unknown(value: Any, loc: str) -> None:
    if isinstance(value, str) and value.strip().lower() in _BANNED:
        raise ValueError(f"{loc}: UNKNOWN is banned")
    if isinstance(value, dict):
        for key, item in value.items():
            _reject_unknown(str(key), f"{loc}.{key}")
            _reject_unknown(item, f"{loc}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_unknown(item, f"{loc}[{index}]")


def _as_closed_str(value: Any, allowed: set[str], field_name: str) -> Any:
    if isinstance(value, str):
        if value.strip().lower() in _BANNED:
            raise ValueError(f"{field_name}: UNKNOWN is banned")
        if value not in allowed:
            choices = ", ".join(sorted(allowed))
            raise ValueError(
                f"free strings are banned; {field_name} must be one of: {choices}"
            )
    return value


def _as_uuid(value: Any, field_name: str) -> Any:
    if isinstance(value, str):
        if value.strip().lower() in _BANNED:
            raise ValueError(f"{field_name}: UNKNOWN is banned")
        try:
            UUID(value)
        except ValueError as exc:
            raise ValueError(
                f"free strings are banned; {field_name} must be a UUID"
            ) from exc
    elif isinstance(value, UUID):
        return value
    elif value is not None and not isinstance(value, UUID):
        # ints, bools, dicts: not UUIDs. Let a clear error fire for strings only;
        # other wrong types still fail in the field type.
        if not isinstance(value, (str, UUID)):
            raise ValueError(f"free strings are banned; {field_name} must be a UUID")
    return value


class _Document(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: UUID
    status: Status
    owner: UUID
    deps: list[UUID]
    version: int = Field(ge=1)
    created: datetime
    updated: datetime

    @model_validator(mode="before")
    @classmethod
    def ban_unknown_and_extra(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            raise ValueError("document must be an object")
        extra = set(data) - set(cls.model_fields)
        if extra:
            names = ", ".join(sorted(str(name) for name in extra))
            raise ValueError(f"extra fields banned: {names}")
        _reject_unknown(data, cls.__name__)
        return data

    @field_validator("status", mode="before")
    @classmethod
    def status_closed(cls, value: Any) -> Any:
        return _as_closed_str(value, {member.value for member in Status}, "status")

    @field_validator("id", "owner", mode="before")
    @classmethod
    def ids_are_uuids(cls, value: Any, info: Any) -> Any:
        return _as_uuid(value, info.field_name)

    @field_validator("deps", mode="before")
    @classmethod
    def deps_are_uuids(cls, value: Any) -> Any:
        if isinstance(value, str):
            raise ValueError("free strings are banned; deps must be a list of UUIDs")
        if isinstance(value, (list, tuple)):
            return [_as_uuid(item, "deps") for item in value]
        return value

    @field_validator("deps")
    @classmethod
    def deps_unique(cls, value: list[UUID]) -> list[UUID]:
        if len(value) != len(set(value)):
            raise ValueError("deps must be unique")
        return list(value)

    @field_validator("created", "updated")
    @classmethod
    def timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            raise ValueError("datetime must be timezone-aware")
        return value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def time_order_and_self_dep(self) -> "_Document":
        if self.updated < self.created:
            raise ValueError("updated must be >= created")
        if self.id in self.deps:
            raise ValueError("deps cannot include self")
        return self


class Task(_Document):
    type: TaskType

    @field_validator("type", mode="before")
    @classmethod
    def type_closed(cls, value: Any) -> Any:
        return _as_closed_str(value, {member.value for member in TaskType}, "type")


class Agent(_Document):
    type: AgentType

    @field_validator("type", mode="before")
    @classmethod
    def type_closed(cls, value: Any) -> Any:
        return _as_closed_str(value, {member.value for member in AgentType}, "type")


MUTABLE_FIELDS = frozenset({"type", "status", "owner", "deps"})
SYSTEM_FIELDS = frozenset({"id", "version", "created", "updated"})

MODELS: dict[EntityKind, type[Task] | type[Agent]] = {
    EntityKind.task: Task,
    EntityKind.agent: Agent,
}
