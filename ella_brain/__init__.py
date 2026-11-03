"""Ella's external state.

Public operations are get and mutate, plus the five stage functions and the
domain helpers (ella_brain.domains) that call only those two. There is no
in-memory copy of the graph.
"""

from ella_brain.errors import (
    ConsensusRejected,
    EllaError,
    MutationRejected,
    NotFound,
    VerificationError,
    Verdict,
)
from ella_brain.domains import content_factory, open_content_factory
from ella_brain.gate import Ella, get, mutate
from ella_brain.models import Agent, AgentType, EntityKind, Status, Task, TaskType
from ella_brain.pipeline import (
    BASE_STAGES,
    act,
    interpret,
    open_pipeline,
    perceive,
    plan,
    review,
)

__all__ = [
    "Agent",
    "AgentType",
    "BASE_STAGES",
    "ConsensusRejected",
    "Ella",
    "EllaError",
    "EntityKind",
    "MutationRejected",
    "NotFound",
    "Status",
    "Task",
    "TaskType",
    "Verdict",
    "VerificationError",
    "act",
    "content_factory",
    "get",
    "interpret",
    "mutate",
    "open_content_factory",
    "open_pipeline",
    "perceive",
    "plan",
    "review",
]
