"""Synthetic Task and Agent writes. Not conversational memory."""

from __future__ import annotations

from uuid import UUID, uuid5

from ella_brain import Ella, EntityKind, MutationRejected, NotFound

NS = UUID("6f0c1a2e-0000-4000-8000-000000000001")


def _id(request_id: str, role: str) -> UUID:
    return uuid5(NS, f"{request_id}:{role}")


def _exists(ella: Ella, kind: EntityKind, entity_id: UUID) -> bool:
    try:
        ella.get(kind, entity_id)
    except NotFound:
        return False
    return True


def _ensure_agent(ella: Ella, agent_id: UUID) -> None:
    if _exists(ella, EntityKind.agent, agent_id):
        return
    ella.mutate(
        EntityKind.agent,
        agent_id,
        {
            "type": "companion",
            "status": "active",
            "owner": str(agent_id),
            "deps": [],
        },
    )


def roundtrip(ella: Ella, request_id: str) -> dict[str, object]:
    agent_id = _id(request_id, "agent")
    task_id = _id(request_id, "task")
    _ensure_agent(ella, agent_id)
    if not _exists(ella, EntityKind.task, task_id):
        ella.mutate(
            EntityKind.task,
            task_id,
            {
                "type": "perceive",
                "status": "pending",
                "owner": str(agent_id),
                "deps": [],
            },
        )
    doc = ella.get(EntityKind.task, task_id)
    return {
        "ok": True,
        "op": "roundtrip",
        "kind": "task",
        "id": str(doc.id),
        "type": doc.type.value,
        "status": doc.status.value,
        "version": doc.version,
        "read_back": (
            f"خوانده شد: {doc.type.value} وضعیت {doc.status.value} نسخه {doc.version}. "
            "این حافظهٔ گفتگو نیست."
        ),
    }


def invalid_dependency(ella: Ella, request_id: str) -> dict[str, object]:
    agent_id = _id(request_id, "agent")
    dep_id = _id(request_id, "dep")
    task_id = _id(request_id, "bad")
    _ensure_agent(ella, agent_id)
    if not _exists(ella, EntityKind.task, dep_id):
        ella.mutate(
            EntityKind.task,
            dep_id,
            {
                "type": "perceive",
                "status": "pending",
                "owner": str(agent_id),
                "deps": [],
            },
        )
    before = ella.get(EntityKind.task, dep_id).version
    try:
        ella.mutate(
            EntityKind.task,
            task_id,
            {
                "type": "interpret",
                "status": "active",
                "owner": str(agent_id),
                "deps": [str(dep_id)],
            },
        )
    except MutationRejected as exc:
        after = ella.get(EntityKind.task, dep_id).version
        created = _exists(ella, EntityKind.task, task_id)
        if after != before or created:
            raise RuntimeError("rejected dependency mutate changed the store") from exc
        return {
            "ok": False,
            "op": "invalid_dependency",
            "kind": "task",
            "id": str(task_id),
            "version": None,
            "dep_version": after,
            "read_back": "رد شد: وابستگی تمام نشده است. نسخهٔ تازه‌ای نوشته نشد.",
            "reason": str(exc),
        }
    raise RuntimeError("invalid dependency mutate was accepted")
