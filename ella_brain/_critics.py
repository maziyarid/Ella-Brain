"""Two independent critique models.

A write happens only when both return allow. Disagreement does not write.
Neither model receives a mutate handle or a filesystem path.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from ella_brain._io import canonical
from ella_brain.errors import MutationRejected, Verdict
from ella_brain.models import Agent, AgentType, EntityKind, Status, Task, TaskType


class SchemaCritic:
    """Structural model. Re-reads the closed schema from the canonical document."""

    name = "schema-critic"

    def critique(self, before: Any, proposed: Any, view: Any) -> Verdict:
        del view
        reasons: list[str] = []
        if not isinstance(proposed, (Task, Agent)):
            return Verdict(self.name, False, "proposed is not a closed schema")
        try:
            again = type(proposed).model_validate(canonical(proposed))
        except Exception as exc:
            reasons.append(f"schema round-trip failed: {exc}")
        else:
            if canonical(again) != canonical(proposed):
                reasons.append("schema round-trip mismatch")
        reasons.extend(_closed_value_reasons(proposed))
        if before is None:
            if proposed.version != 1:
                reasons.append("create must be version 1")
        else:
            if not isinstance(before, type(proposed)):
                reasons.append("kind changed")
            if proposed.id != before.id:
                reasons.append("id is immutable")
            if proposed.created != before.created:
                reasons.append("created is immutable")
            if proposed.version != before.version + 1:
                reasons.append("version must increment by exactly 1")
        if proposed.updated < proposed.created:
            reasons.append("updated is earlier than created")
        if reasons:
            return Verdict(self.name, False, "; ".join(reasons))
        return Verdict(self.name, True, "schema ok")


class GraphCritic:
    """Dependency and owner model. Separate code from the pre-validate graph check."""

    name = "graph-critic"

    def critique(self, before: Any, proposed: Any, view: Any) -> Verdict:
        del before
        if not isinstance(proposed, (Task, Agent)):
            return Verdict(self.name, False, "proposed is not a closed schema")
        reasons: list[str] = []
        kind = EntityKind.task if isinstance(proposed, Task) else EntityKind.agent
        if proposed.id in proposed.deps:
            reasons.append("deps cannot include self")
        if len(proposed.deps) != len(set(proposed.deps)):
            reasons.append("deps must be unique")
        missing = False
        for dep_id in proposed.deps:
            try:
                dep = view.current(kind, dep_id)
            except Exception as exc:
                reasons.append(f"dep {dep_id} unreadable: {exc}")
                missing = True
                continue
            if dep is None:
                reasons.append(f"missing dep {dep_id}")
                missing = True
        if not missing:
            cycle = _cycle_reason(kind, proposed, view)
            if cycle:
                reasons.append(cycle)
        reasons.extend(_owner_reasons(proposed, view))
        if proposed.status in (Status.active, Status.done) and not missing:
            for dep_id in proposed.deps:
                dep = view.current(kind, dep_id)
                if dep is not None and dep.status is not Status.done:
                    reasons.append(
                        f"{proposed.status.value} requires dep {dep_id} "
                        f"to be done (is {dep.status.value})"
                    )
        if reasons:
            return Verdict(self.name, False, "; ".join(reasons))
        return Verdict(self.name, True, "graph ok")


def _closed_value_reasons(model: Any) -> list[str]:
    data = canonical(model)
    reasons: list[str] = []
    allowed_type = {member.value for member in (TaskType if isinstance(model, Task) else AgentType)}
    if data["status"] not in {member.value for member in Status}:
        reasons.append("status is not a closed value")
    if data["type"] not in allowed_type:
        reasons.append("type is not a closed value")
    if "unknown" in {str(data["status"]).lower(), str(data["type"]).lower()}:
        reasons.append("UNKNOWN is banned")
    return reasons


def _owner_reasons(proposed: Any, view: Any) -> list[str]:
    if isinstance(proposed, Agent) and proposed.owner == proposed.id:
        return []
    try:
        owner = view.current(EntityKind.agent, proposed.owner)
    except Exception as exc:
        return [f"owner unreadable: {exc}"]
    if owner is None:
        return [f"missing owner {proposed.owner}"]
    return []


def _cycle_reason(kind: EntityKind, proposed: Any, view: Any) -> str | None:
    visiting: set[UUID] = set()

    def deps_of(entity_id: UUID) -> list[UUID]:
        if entity_id == proposed.id:
            return list(proposed.deps)
        other = view.current(kind, entity_id)
        if other is None:
            raise MutationRejected(f"missing dep {entity_id}")
        return list(other.deps)

    def walk(entity_id: UUID) -> str | None:
        if entity_id in visiting:
            return f"dependency cycle at {entity_id}"
        visiting.add(entity_id)
        for dep_id in deps_of(entity_id):
            found = walk(dep_id)
            if found:
                return found
        visiting.remove(entity_id)
        return None

    try:
        return walk(proposed.id)
    except MutationRejected as exc:
        return str(exc)


def default_critics() -> tuple[SchemaCritic, GraphCritic]:
    return (SchemaCritic(), GraphCritic())
