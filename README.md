# Ella-Brain

External state for Ella. She does not remember the graph, and she does not touch the files. She calls `get` and `mutate`.

This repository starts with Python and versioned JSON, not a graph database. A graph database can replace the store later. It cannot replace the gate.

## Contract

- Schemas are closed. `status` is `pending | active | blocked | done`. `type` is an enum. `id`, `owner`, and `deps` are UUIDs. There is no `UNKNOWN` and no extra field.
- Files are `tasks/{id}/v{n}.json` and `agents/{id}/v{n}.json`. Current means max `n`. Old versions stay.
- `mutate` is the only write. Order is fixed: load, pre-validate schema and deps, two-model critique consensus, version++, atomic write, reload-verify.
- A write lands only when both critique models allow it. A split decision does not write. A deny does not write.
- `get` and `mutate` read from disk every time. `Ella` keeps the directory path and the two models. It does not keep tasks.

## Layout

```text
ella_brain/
  models.py      external Task and Agent schemas
  gate.py        get, mutate, Ella
  pipeline.py    perceive, interpret, plan, act, review
  domains.py     domain helpers (content_factory) on top of the base pipeline
  _stages.py     the five functions inside mutate
  _critics.py    schema critic and graph critic
  _io.py         version files (not her API)
```

## mutate

```text
load -> pre-validate schema/deps -> 2-model consensus -> version++ and atomic write -> reload-verify -> return
```

Create requires `type`, `status`, `owner`, `deps`. The gate sets `id`, `version`, `created`, and `updated`. Those four are rejected if a patch contains them.

`active` and `done` require every dependency to already be `done`. `pending` and `blocked` may cite unfinished work. Dependencies must exist, must be unique, and must not cycle. A task owner must be an existing agent. An agent may be owned by itself (the root) or by an existing agent.

The default critics are two separate checks, not two network models:

| Model | What it re-checks |
|---|---|
| `schema-critic` | Closed schema, version step, frozen `id` and `created` |
| `graph-critic` | Dependencies, cycles, owner, `active`/`done` rule |

Pass your own pair to `Ella(root, critics=(model_a, model_b))`. Each needs a distinct `.name` and `.critique(before, proposed, view) -> Verdict`. `view.current(kind, id)` is read-only. If a critic changes any file, `mutate` aborts its write.

## Five stages around mutate

`perceive`, `interpret`, `plan`, `act`, and `review` are the only workflow helpers. They take an `Ella` and call `get` / `mutate`. They do not import the file store.

`open_pipeline` creates that chain, each stage depending on the previous one. Calling it again aligns dependencies and does not rewind status.

```python
from uuid import uuid4
from ella_brain import AgentType, BASE_STAGES, Ella, EntityKind, Status, TaskType, open_pipeline

root = "/var/lib/ella-brain"  # on the VPS, any durable directory
ella = Ella(root)

agent_id = uuid4()
ella.mutate(EntityKind.agent, agent_id, {
    "type": AgentType.companion,
    "status": Status.active,
    "owner": agent_id,
    "deps": [],
})

ids = {stage: uuid4() for stage in BASE_STAGES}
tasks = open_pipeline(ella, owner=agent_id, ids=ids)
```

## Domain task types

`TaskType` holds the five base stages plus domain members: `content_factory` and `medical_crm`. The schema critic accepts them because the enum is closed. `open_pipeline` still builds only the five base stages (`BASE_STAGES`), so use `BASE_STAGES`, not `TaskType`, when you mean the base chain.

Domain helpers live in `ella_brain/domains.py`. They call `get` / `mutate` only, so the graph critic applies unchanged: no cycles, no missing deps, and no `active` or `done` while a dep is unfinished.

`open_content_factory` creates one `content_factory` task that depends on the base pipeline's completion node (its `review` task). It starts `pending` and cannot become `active` until that review is `done`.

```python
from ella_brain import content_factory, open_content_factory

job = open_content_factory(ella, owner=agent_id, task_id=uuid4(), after=ids[TaskType.review])
content_factory(ella, job.id, owner=agent_id, status=Status.active)  # rejected until review is done
```

`medical_crm` has no helper yet.

## Tests

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python -m pytest
```

Requires Python 3.10+.

## Sharing

Issues and pull requests are for schema changes and critique policies. Do not add a cache, a free-string field, or a second write path.

## Voice preview

`apps/ella-voice-preview` is a local browser prototype. Ordinary replies and preview memory stay mocked. Two typed Persian sentences call `get` and `mutate` on a disposable synthetic store through `ella_channel`, and only when that local server is running. Setup is in `docs/voice/gate-demo.md`.

