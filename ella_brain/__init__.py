"""Ella's external state.

Public operations are get and mutate, plus the five stage functions that call
only those two. There is no in-memory copy of the graph.
"""

from ella_brain.errors import (
    ConsensusRejected,
    EllaError,
    MutationRejected,
    NotFound,
    VerificationError,
    Verdict,
)
from ella_brain.gate import Ella, get, mutate
from ella_brain.models import Agent, AgentType, EntityKind, Status, Task, TaskType
from ella_brain.pipeline import act, interpret, open_pipeline, perceive, plan, review

__all__ = [
    "Agent",
    "AgentType",
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
    "get",
    "interpret",
    "mutate",
    "open_pipeline",
    "perceive",
    "plan",
    "review",
]
