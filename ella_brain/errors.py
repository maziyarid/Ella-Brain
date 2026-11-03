"""Failures of the gate. A rejected mutate leaves the store unchanged."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Verdict:
    """One critique model's decision. Consensus needs both models."""

    model_name: str
    allow: bool
    reason: str


class EllaError(Exception):
    """Base error. Callers can catch this or a specific subclass."""


class NotFound(EllaError):
    """No version file exists for this id."""


class MutationRejected(EllaError):
    """The patch was refused before any version file was written."""


class ConsensusRejected(MutationRejected):
    """The two critique models did not both allow the write."""

    def __init__(self, verdicts: tuple[Verdict, Verdict]) -> None:
        self.verdicts = verdicts
        detail = "; ".join(
            f"{v.model_name}: {'allow' if v.allow else 'deny'} ({v.reason})"
            for v in verdicts
        )
        super().__init__(f"critique consensus failed: {detail}")


class VerificationError(EllaError):
    """A version file exists but does not match the schema or its path."""
