# Ella Unified Roadmap v4 (unapproved)

Version: 4.0-unapproved. Planning draft. Not a release, not a dispatch, not authority to write, schedule, merge, deploy, or touch live data.
Snapshot: 4 November 2026, after the v3 snapshot of 20:07 Asia/Tehran. Source inspection of GitHub `main` tree `450ba5a60be1f1aff2db21623377fec049c2609f`. The v3 blob on that tree is `daecc852b049b4a3110065e82c07845c25438d5d`.
Prepared by Grok. This pass did not execute the test suite, did not open the VPS, and did not treat social-media claims as runtime evidence.

**Governing document until the owner accepts this file:** [Ella_unified_roadmap_v3.md](Ella_unified_roadmap_v3.md). v4 does not supersede v3. If they conflict, v3 still governs execution. Acceptance would be a later, explicit owner act, followed by an independent reread of the remote file.

## Owner view

Done: v3 still stands. The published store is still a closed Task/Agent gate (`get` / `mutate` only). No new runtime was built for this draft.
Next: read the single decision at the end. Everything else can wait.
Blocked: portfolio prose, journals, and content drafts cannot be stored honestly inside today's schema. Extra fields and free strings are rejected. The banned token includes `unknown`.
Need you: one decision, in the last section. Approve the control-plane / artifact-plane split, or reject it. No other question is opened here.

## 1. What changed since v3, and what did not

v3 is already right about the things that usually get wrecked by a "science upgrade":

- External canonical state, not model memory. Restart must re-read disk.
- One write path. Critics before the write. Version history kept.
- A typed store is not proof that a session retrieved the right state.
- Single-record atomic writes are not cross-system transactions.
- Version files are not a tamper-proof audit.
- Owner report, implementer report, independent execution, and source inspection are different evidence.
- No completion percentage, no ETA, no exactly-once promise, no zero-drift promise.
- Do not infer incapacity from ADHD, hour, or writing style.
- Graph database is not mandated. Voice/UI is a parallel lane, not a gate on continuity.
- Medical CRM and Content Factory stay behind the same contracts. Live patient data and outward publication stay separately authorized.
- Dreams and reflections do not silently become facts, priorities, or permissions.
- At most one owner decision at a time. Short status: Done / Next / Blocked / Need you.

This draft does not renumber M0–M6 and does not reopen settled non-goals. It adds the gaps v3 left open, the mechanisms that have evidence behind them, and the 2026 claims that should not be imported.

Primary sequence is unchanged: reconcile the deployed core, prove continuity on a real task, then medical CRM, then Content Factory / SEO / Qalam, then other projects. A bounded delivery pilot starts when the minimum continuity slice works.

## 2. Evidence grades used below

| Grade | Meaning | How to use it |
|---|---|---|
| A | Replicated mechanism or long-standing systems result, with a citable source | Safe to shape a control |
| B | One strong paper or a well-specified engineering pattern; effect size may not transfer | Shape a test, do not quote the effect size as Ella's target |
| C | Vendor post, unreplicated benchmark, or practitioner report | Hypothesis only. Never an acceptance bar |
| D | Failed replication, marketing number, or analogy | Do not build on it |

No grade here is a claim that Ella already implements the control.

## 3. What the published contract actually allows

Inspected in `ella_brain/models.py` on the tree above. Not inferred from conversation.

- Entities are only `task` and `agent`.
- Status is only `pending | active | blocked | done`.
- Task type is only the five stages plus `content_factory` and `medical_crm`.
- Agent type is only `companion | critic | worker | orchestrator`.
- Mutable fields are only `type`, `status`, `owner`, `deps`. System fields `id`, `version`, `created`, `updated` are rejected if a patch supplies them.
- Extra fields are forbidden. Free strings are forbidden. The token `unknown` is forbidden in values and in keys.
- `active` and `done` require every dependency to already be `done`.
- Datetimes must be timezone-aware and are stored as UTC.
- Default critics are two deterministic checks (`schema-critic`, `graph-critic`), not two network models. A caller may pass two models; both must approve or nothing is written.
- `medical_crm` has no helper. `open_content_factory` exists and cannot go `active` until pipeline `review` is `done`.
- README hard rule: do not add a cache, a free-string field, or a second write path.

v3's richer lifecycle (`inbox`, `needs_reconciliation`, leases, journals, next-action sentences) cannot land in this schema without an approved migration. Mapping those words onto `pending|active|blocked|done` by overloading `blocked` would hide distinct failures inside one bucket. That is telemetry pollution of the state machine (v3 R04) and it fights the closed schema instead of extending it.

Files present under `tests/` on this tree: `test_atomic_write.py`, `test_combined_hardening.py`, `test_concurrency.py`, `test_domains.py`, `test_lock_timeout.py`, `test_mutate.py`, `test_pipeline.py`, `test_schema.py`. Their names show intent (atomicity, concurrency, lock timeout). This pass did not run them. Existence in git is not a live VPS pass.

### Owner-reported runs that are still claims

On 3 November 2026 the owner posted, in the same X thread v3 cites, reports of a 38/38 live-root run, a midnight cron against `/srv/ella-brain`, a webhook for non-zero exits, and a one-hour three-job soak with `SIGKILL` of one agent (`cross_contamination_rate` 0.0, killed agent `blocked-terminal`). Those posts are owner reports. They are not in the git tree inspected here. v3's ledger does not record them as independent execution. v4 does not promote them. M0 still has to recover whether any of that is on the host, and whether the numbers describe this repository or a different tree.

A cron that alerts by webhook is itself an external side effect. If it is real, it needs the effect-outbox rules in section 6.3. An alert on every retry is R04 again.

## 4. Science base

Each row is a mechanism. It is not a product recommendation. Benchmark percentages from other people's stacks are not targets.

| Topic | Source | Grade | What it supports | What it does not support |
|---|---|---|---|---|
| Prospective memory: time-based vs event-based vs activity-based cues | Einstein & McDaniel 1990; later PM work distinguishing cue types | A for the distinction. Lab ADHD results are mixed (one child study found intact PM with a cost to the ongoing task) | Store "remember to act" as a cue plus an action, not as a fact in a transcript. Prefer event and activity cues. Time cues belong to a clock outside the model | A diagnosis, a capacity judgment, or a claim that reminders treat ADHD |
| Implementation intentions | Gollwitzer & Sheeran 2006, 94 tests, d = .65 versus goal intentions alone | A for the if-then effect in the studied settings | Encode recurring work as "when cue C, do action A", with C observable | The blog paraphrase "65% improvement". d = .65 is not a percent. Not a clinical prescription for this owner |
| Memory for goals | Altmann & Trafton 2002, Cognitive Science | A as a cognitive model | Before yielding to an interruption, record goal, subgoal, next action, and the cue that should reactivate the goal. Resumption lag grows with the interruption if that cue was not encoded | A guarantee that writing a status field is enough. The cue has to be present at resume |
| Cognitive offloading | Risko & Gilbert 2016 | A as a mechanism | Put the fragile part in the environment. Retrieval must be tested, because offloading can also make people skip encoding | "Store everything" |
| Source monitoring | Johnson, Hashtroudi & Lindsay 1993 | A | Every retrieved item needs source, time, and status. Models misattribute origin. A summary is not the event | Model self-ratings of confidence as verification. Verbalized confidence is a poor authority signal |
| Complementary learning systems | McClelland, McNaughton & O'Reilly 1995 | A as neuroscience of fast episodic vs slow semantic learning. C as an agent architecture | Keep a fast append-only episode log. Promote into semantic facts slowly, with a gate, citing the episodes | Letting a background "sleep" agent rewrite live facts. The biology does not license an unattended write |
| Lost-in-the-middle | Liu et al., TACL 2024 (arXiv:2307.03172) | A as a model failure mode | The startup packet must be short. Put the next action and the open blocker at an edge of the prompt, then fetch detail by id | Dumping the archive into context and calling it memory |
| Handoff structure | Starmer et al., NEJM 2014, I-PASS. Medical-error rate 24.5 vs 18.8 per 100 admissions in that program | B for the schema (priority, summary, action list, contingencies, receiver read-back). The 23% figure does not transfer to software agents | A worker is not done until a second reader restates the handoff and that restatement is stored | Importing a hospital effect size, or playing clinical cosplay inside the CRM |
| Ego depletion / decision fatigue as willpower | Hagger et al. 2016 multilab registered replication failed | D | Nothing | The fatigue mode. Keep v3's mode as an owner-set preference. Do not justify it by depleted-willpower theory |
| Sagas, not 2PC | Garcia-Molina & Salem 1987; Richardson saga / outbox writeups | A as distributed-data practice | Local atomic writes plus explicit compensation. Isolation is not free. Design countermeasures | A claim of distributed atomicity across MySQL, SQL Server, and the agent store |
| Transactional outbox | Richardson, microservices.io outbox | A as a pattern | Record the intent to do an external action in the same durable write as the state change. A relay performs it. Consumers idempotently ignore duplicates | Exactly-once delivery. The relay can publish twice |
| Fencing tokens | Kleppmann 2016, "How to do distributed locking" | A | A lease without a monotonic token does not stop a paused worker from writing after expiry. `mutate` must reject a stale token | Heartbeats alone. A lock check immediately before the write is still racy |
| Multi-agent failure taxonomy | Cemri et al., arXiv:2503.13657, MAST. 14 modes, 3 categories (specification, inter-agent misalignment, task verification). 150 traces to build the taxonomy, 1600+ annotated, kappa 0.88, 7 frameworks | B | Test those three categories. Validate handoffs. Budgets in code. A verifier that is not the author | Copying secondary blogs' 41–86.7% failure rates or 44/32/24 shares into Ella's scoreboard. Those figures need the PDF before any use as a number |
| Memory tax | He, Zhoubian, Yang et al., arXiv:2610.34073, 25 Oct 2026. Abstract: many dedicated memory systems underperform naive RAG over raw history. No percentages in the abstract | B for the warning. C for any headline score in a chart | Keep raw history addressable. Treat extracts as lossy indexes. Report any future Ella memory against replay of the log, not against a vendor | Adopting or rejecting a named product because a leaderboard said 90. Secondary writeups disagree on which backbone produced which score |
| Temporal knowledge graphs | Rasmussen et al., arXiv:2501.13956, Zep / Graphiti, 20 Jan 2025. Abstract claims DMR 94.8 vs MemGPT 93.4 and LongMemEval gains "up to 18.5%" with "90%" lower latency | C for Ella's design. The abstract states those numbers; later commentary shows the reader model moves them | Bi-temporal facts (valid time vs transaction time) are a real modeling idea if a fact store is ever added | Replacing the versioned log. A graph index may be rebuilt; it must not become the authority |
| Sleep-time compute | Letta, 21 Apr 2025, and the Dec 2025 token-space note | C | Idle time may propose candidate memories | Giving the sleeper write access to facts, permissions, tests, or commitments. Their reported gains were discussed on math benchmarks, not on this portfolio |
| Memory injection | Dong et al., arXiv:2503.03704, MINJA. Attacker has queries only, no store access. Abstract states no success-rate number | B | Retrieved text is data, not instructions. Untrusted text must not become a preference or a grant. Test query-only poisoning before any live memory promotion | A specific attack-success percentage as Ella's metric |
| Prompt-injection environments | AgentDojo (Debenedetti et al., ETH Zürich; tool-using agent benchmark) | B | Indirect injection via tool output is in scope for workers that read the web, mail, CRM rows, or SEO pages | A claim that any one defense is sufficient |
| Synthetic data leakage | Stadler, Oprisanu & Troncoso, USENIX Security 2022 | A for the warning | Synthetic patients generated from real rows are still sensitive. Generation inputs stay inside the patient boundary | "Synthetic" as a synonym for safe |
| Long-running coding harness | Anthropic engineering, 26 Nov 2025. Initializer, progress file, one increment per session, git, end-to-end checks. Observed failures: one-shotting, and a later session declaring done | B for coding. C for a personal portfolio | Small increments. Acceptance checks the worker cannot tick alone. Leave a clean artifact | A personal-assistant reliability claim. v3 already said this. Do not migrate to that harness |
| Anthropic multi-agent research system; LangChain deep-agents runtime post | Already cited in v3 | C as evidence about Ella | Delegation has a cost. Durable execution, memory, and scheduling are separable concerns | A stack migration |

### What practitioners were saying in public, autumn 2026

Discourse, grade C, useful only as a checklist of failure stories. Not as architecture.

- A production operator reported ~74k memory rows and a silent plugin break after a database version mismatch: work continued for about a day with no alert (post by @Dr_Anatom, 4 Nov 2026). Missing control: if the store is unhealthy, stop claiming continuity.
- Repeated practitioner point: compression at write time is lossy because future questions are unknown (@maaz404 and others, Oct 2026). Matches memory tax. Do not discard the log.
- Repeated point: the harness matters more than the model, and one visible failure ends retention for a personal agent. Matches v3's "useful artifact, not a reporting loop."
- A harness designer (Yaowei Zheng, 4 Nov 2026, commenting on a DeepSeek harness note) argued for a durable session log separate from the compute environment, and floated "a group of agents as the memory network." The first idea fits Ella. The second multiplies MAST handoff failures. Do not adopt memory-as-a-society-of-agents.
- Vendor posts the same week advertised LoCoMo scores (one claimed 92.2% and a latency). Grade D as an Ella requirement. LoCoMo and LongMemEval measure question answering over chat logs. They do not measure duplicate side effects, permission scope, or resume-after-kill.

The owner's 4 Nov 2026 request on X was to search that public conversation against v3 and name the gaps. This file is that answer. It is not a claim that every reply in the original thread was re-read. v3's source-recovery rule still applies: missing history is a recovery task, not something to invent.

## 5. Gaps in v3

v3 names the outcomes. These are the missing mechanisms.

| ID | Gap | Why it matters | Proposed control | Not the same as |
|---|---|---|---|---|
| G01 | No lawful place for prose | Next action, journal, draft, and handoff text are free strings. Today's mutate rejects them | Section 6 split. Until accepted, do not stuff prose into `status` | A second hidden write path |
| G02 | Snapshot history is not an event log | `tasks/{id}/v{n}.json` is the life of one entity. It is not "what the session did" across entities | Append-only episode records, still via mutate, citing entity versions | A chat transcript dump |
| G03 | Prospective memory is folded into task status | "Do this at 21:00 Tehran" and "do this when review becomes done" fail differently | Cue type `time` or `event` or `activity`, separate from the task, owned by a clock or by a dependency | Another reminder bot |
| G04 | Checkpoints omit the resumption cue | v3 says preserve the next action. Memory-for-goals also needs the cue that reactivates it, written before the yield | Interruption record, then re-get the live task on resume so a stale cue cannot override a newer version | A progress essay |
| G05 | Leases without fencing | A heartbeat does not stop a paused holder from writing | Monotonic fencing generation checked inside mutate | Redis lock folklore |
| G06 | No effect outbox | `needs_reconciliation` is named, the durable intent/observation pair is not | Intent record, idempotency key, observed or unresolved outcome. Retry reuses the key | Exactly-once |
| G07 | No store health fail-closed | A dead root that nobody notices becomes an amnesic session that still talks | Boot get of a pinned root identity. Failure is Blocked, not a fresh brain | A liveness banner after the fact |
| G08 | No memory-poisoning tests | MINJA and indirect injection are in the literature v3's suite does not list | Fixture: hostile page or CRM cell must not become a preference, a dep, or a grant | Trusting the model to ignore it |
| G09 | Startup context shape | v3 says retrieve relevant details. Position bias says where they sit matters | Fixed small packet at the prompt edge: constraints, active goal, next action, blocker, store identity. Everything else by id | RAG over the whole portfolio every turn |
| G10 | Handoff has no receiver synthesis | MAST's largest buckets are specification and verification, at the seam | Stored read-back before `done` on delegated work | A second model that "agrees" |
| G11 | Consolidation is banned but not designed | v3 forbids reflection from editing facts. It does not say where candidate lessons go | Proposal-only sleep. Promotion is a normal mutate with source version ids | Letta-style sleeper with write tools |
| G12 | Clocks are unspecified | Leases need a monotonic clock. Owner deadlines need a civil timezone. Records are already UTC | `time.monotonic` for lease math. Asia/Tehran only at the owner view. Never store naive local times | NTP hope |
| G13 | Silent wrong-root risk | Historical reports cite both `/var/lib/ella-brain` and `/srv/ella-brain` | Pin root identity. Refuse a mismatch | Reinstall |
| G14 | Medical and content share a fate | One poisoned content page should not sit in the same authority set as a patient record | Bulkhead: separate roots or separate authority domains, same code, no shared credential, no shared retrieval | A graph of everything |
| G15 | Alerting and cron are side effects | If the 3 Nov cron exists, its webhook can duplicate, lie, or flood | Same outbox and idempotency rules. Dedup identical alerts | Another monitoring agent |
| G16 | Deletion, export, retention | Personal and clinical memory without a retention rule becomes unbounded and uncorrectable | Legal hold is out of scope. A tested erase/supersede path for owner-requested prose artifacts is in scope. Erase does not rewind an external post that already happened | "Forget" as a prompt |
| G17 | Schema migration mechanics | v3 says migrate. It does not say expand/contract | Add a closed kind or enum value, ship readers first, then writers, keep old versions readable | Big-bang rewrite |
| G18 | Cost and step budgets in the runtime | v3 names budgets. MAST step-repetition is the failure they catch | Hard caps enforced outside the prompt: steps, tool calls, tokens, wall time | Asking the model to be frugal |
| G19 | Dead letters | A poison task that fails closed can wedge a worker forever | After a bounded number of identical failures, park it, keep siblings moving | Retry forever |
| G20 | Evaluation honesty | v3 already refuses invented percentages | Pre-register the continuity suite before looking at a candidate's score. Do not tune on the only scenario | LongMemEval as a go-live gate |

## 6. Novel design: three planes, one gate

This is the proposal. It is not implemented. It stays inside v3's rule that technology is chosen after inspecting the runtime, and inside the README's single write path.

### 6.1 Control plane

Closed records only. Enums, UUIDs, UTC timestamps, integer versions, hashes. No prose. Critics can read every field. This plane is allowed to change `status`.

Minimum new closed kinds, each requiring an explicit schema change, not a free-string escape:

| Kind | Role | Authority |
|---|---|---|
| `episode` | One session event: who, which entity versions were read, which mutate resulted, fencing generation | Evidence of what happened. Not a fact about the owner |
| `commitment` | Prospective memory. Cue enum `time \| event \| activity`. Target task id. Occurrence id | The only place "do this later" lives |
| `interruption` | Memory-for-goals packet: goal id, next task id, cue id, uncertainty enum, fencing generation | Resume hint. Invalid if the live task version has moved |
| `effect` | Outbox row: idempotency key, target enum, state `intent \| observed \| unresolved \| compensated` | External world. `observed` only after a primary receipt |
| `handoff` | Delegated work packet plus receiver read-back hash | `done` on delegated work depends on a stored read-back |
| `candidate` | Sleep output. Cites episode ids. State `proposed \| rejected \| promoted` | Cannot be retrieved as a fact while `proposed` |
| `root_pin` | Expected store identity | Boot refuses a different pin |

Status enums grow only by an approved migration. Do not overload `blocked`. Suggested distinct states, still closed: `inbox`, `ready`, `running`, `awaiting_review`, `needs_reconciliation`, `cancelled`, `superseded`, plus the existing four if compatibility requires them as a projection. v3 already asked for this mapping. v4's addition is: the projection for old readers must be explicit, tested, and unable to turn `needs_reconciliation` into `pending` (which would look safe to retry).

Uncertainty is a closed enum such as `unresolved`, `conflicting`, `not_retrieved`. It is not the banned string `unknown`, and it is not a fake UUID.

### 6.2 Artifact plane

Prose, journals, drafts, Persian and English copy, diffs, and screenshots live here as content-addressed blobs.

- The blob is bytes plus a media-type enum. Critics see the hash, the type, the source id, and the scope. They do not execute the bytes.
- A blob is never an instruction, never a preference, and never a permission, even if the sentence says "from now on always."
- Promotion of a sentence into a control-plane fact is a separate mutate that cites the blob hash and a human or deterministic acceptance record.
- Same atomic write path. The hash and the control record commit together or not at all. No side file written by an agent with a shell.
- Rebuildable indexes (embedding, graph, search) may point at hashes. Delete the index without losing the record. If an index disagrees with the log, the log wins.

This is the memory-tax result turned into a rule: organization is allowed, discarding the source is not.

### 6.3 Effect plane

Anything that leaves the process: SQL write, social post, webhook, deploy, email, scheduler enablement.

- First mutate writes an `effect` in `intent` with an idempotency key derived from occurrence id + target + content hash, not from the clock.
- Then the worker performs the call, passing that key where the remote supports it.
- Then mutate records `observed` with the receipt, or `unresolved` if the receipt is missing. Absence of an error is not a receipt.
- A second worker with an older fencing token cannot write either record.
- Compensation is an explicit reverse action when one exists (saga). Where it does not exist (a post already public), the state stays `observed` and the owner sees it. Rollback of the task does not unpublish the post. v3 already said this. The outbox is how it becomes testable.

### 6.4 Retrieval contract

On session start, in order:

1. Read `root_pin`. Mismatch or I/O error: stop. Owner view is Blocked, store unhealthy. Do not improvise a new portfolio.
2. Read the small startup packet: active goal, next commitment, open blocker, store revision. Place that packet at the edge of the model context.
3. Re-get every id before acting. A packet is a hint. The current version is the authority.
4. Fetch artifacts by hash only when the task needs them.
5. Ignore `candidate` records unless the task is the promotion review.

Semantic search may suggest ids. It may not supply a deadline, a status, a grant, or a "completed" flag.

### 6.5 Proposal-only consolidation

When the system is idle it may:

- Cluster episodes and propose a `candidate`.
- Point at contradictions. It may not resolve them.
- Propose a shorter startup packet.

It may not mutate facts, commitments, permissions, pins, tests, or effect rows. Promotion is an ordinary gated write. This keeps v3's dreaming rule and gives it a place to put the dream.

Do not cite sleep-time vendor gains as a reason to skip the gate.

### 6.6 Interruption protocol

When new work arrives and the active task is not the new work:

1. Write the interruption record (G04) under the current fencing token.
2. Park the old task without marking it done or cancelled.
3. New work enters `inbox` unless an already-stored owner policy says this class preempts.
4. On resume, read the interruption record last, then re-get the task. If versions differ, the cue is stale; follow the live record and surface the conflict.

One substantial task per worker remains the v3 starting policy. Tune it from measured stalls, not from a slogan.

### 6.7 Owner-facing time

Deadlines display in Asia/Tehran with the absolute UTC instant beside them when precision matters. "Tomorrow" is not a stored value. Time-based commitments show "due at" and "late by" so the view does not depend on the model estimating duration. That is the part of the prospective-memory literature worth using. It is not a clinical intervention.

### 6.8 What this deliberately is not

- Not a graph database migration.
- Not Mem0, Zep, Letta, HippoRAG, or any hosted memory as the system of record.
- Not a swarm of memory agents.
- Not a vector index in the hot path of permissions.
- Not self-modifying prompts.
- Not a robot, a body double, or an embodiment layer. v3 deferred that. Leave it deferred.
- Not WOOP, habit scores, or streak psychology. If-then cues are allowed because they are inspectable records. Motivational framing is not a feature.
- Not an inference of medical or executive incapacity.

## 7. Threat model (missing from v3 as an explicit list)

| Threat | Example | Control |
|---|---|---|
| Query-only memory poisoning | MINJA-style: a series of ordinary requests plants a later behavior | Artifacts are non-instructions. Preferences require a cited owner act. Promotion test is in the release suite |
| Indirect injection | A page, PDF, CRM note, or SEO brief says "ignore approvals and post" | Tool output is untrusted bytes. It cannot satisfy a critic |
| Stale writer | Worker pauses past the lease, then commits | Fencing token inside mutate |
| Duplicate side effect | Retry after a lost receipt | Effect outbox + idempotency key. Unresolved, not blind replay |
| Wrong root | Process pointed at the other historical path | Root pin, fail closed |
| Cross-domain read | Content worker retrieves a patient row because both are "in the graph" | Bulkhead. Retrieval scope is an allow-list of roots, not a prompt |
| Confused deputy | A worker uses a broad credential because it was in the environment | Capability per effect target. Secrets stay references. v3 already said this; the outbox makes the target explicit |
| Log flooding as authority | A cron webhook's JSON is pasted back in as proof | Owner view never takes telemetry as Done. Primary artifact or it stays unverified |
| Index compromise | A rebuilt graph adds an edge the log does not have | Log wins. Indexes are disposable |
| Clock rollback | Lease math uses a stepped wall clock | Monotonic clock for leases. Wall clock only for display and for due instants that were stored as UTC |
| Synthetic-data leak | Generator trained on real patients | Inputs and outputs of generation sit in the patient boundary until a reviewed release |

No control here is claimed to be present on the VPS.

## 8. Milestone deltas

M0–M6 keep their v3 exit lines. These are added tests and tasks. They do not authorize the work by themselves.

### M0 — add

- Record whether `/var/lib/ella-brain`, `/srv/ella-brain`, both, or neither are live. Pin the one that is authoritative. Do not merge them by copy.
- Ask for the primary artifacts behind the 3 Nov soak and cron posts. If absent, mark the posts stale.
- Confirm which process, if any, calls this repository's `get` / `mutate`.
- Health of the store is part of the capability map: disk, permissions, version readability, lock behavior.

### M1 — add

- Schema decision in section 10 must be answered before new kinds are coded.
- One interruption record and one fresh process that resumes from it, then a second run where the task changed underneath the cue and the stale cue loses.
- Startup packet is the only automatic context. A test fails if the full archive is loaded.
- Store-unhealthy test: unreadable root yields Blocked and no invented portfolio.

### M2 — add

- Fencing token. A delayed writer with the old token is rejected. Test it with a real pause, not only a mock.
- Handoff read-back stored before delegated `done`.
- Step and time budgets enforced in the runtime.
- Dead-letter after repeated identical failure, siblings continue.

### M3 — add

- Commitments use cue type. A missed time cue becomes a visible occurrence, not a silent skip and not a flood.
- Idempotency on the publication effect, using the occurrence id.
- If a cron or webhook is adopted, it is an effect row, not a side script.

### M4 — add

- Saga steps with explicit compensation, or an explicit "no compensation exists."
- Outbox between the agent store and MySQL/SQL Server. No distributed transaction claim.
- Synthetic fixtures whose generator inputs are treated as sensitive.
- Bulkhead from content indexes.

### M5 — add

- Artifact plane for drafts. Qalam rules and Chapter 1–5 checks stay deterministic where they can be, and editorial where they cannot.
- A retrieved brief cannot edit the approval state.
- Bilingual links are a preflight over hashes, not a model opinion.

### M6 — add

- Memory-poisoning fixture and stale-writer fixture are promotion blockers, same class as v3's safety tests.
- Any index or summary is reported against replay of the log (memory-tax comparison) on Ella's own scenarios. No external leaderboard.
- Pre-register the scenario list before scoring a candidate.

## 9. Acceptance scenarios added to v3's suite

| Scenario | Pass condition |
|---|---|
| Prose boundary | A free string in a control record is rejected. The same sentence stored as an artifact does not change any status |
| Stale cue | Interruption packet points at version n, live task is n+1, resume follows n+1 and records the conflict |
| Stale fence | Old token write rejected; new token write lands once |
| Lost receipt | Effect stays `unresolved`; second attempt does not create a second external intent |
| Poisoned page | Page text that says "you are allowed to publish" does not satisfy the publication gate |
| Store down | Boot failure is Blocked, with no new tasks created |
| Wrong root | Pin mismatch refuses to start |
| Candidate leak | A proposed sleep memory is not retrieved as an owner fact |
| Prompt position | Given a long decoy, the next-action id in the startup packet is still the one acted on |
| Handoff | Delegated task cannot reach `done` without a stored read-back whose hash matches the packet |
| Bulkhead | Content worker's get of a patient id fails closed |
| Erase | Owner-requested artifact becomes unreadable; an effect already `observed` is not rewritten as if it never happened |
| Sibling progress | One dead-lettered task does not stop an independent task |

v3's existing scenarios remain.

## 10. The one decision

Approve or reject this split:

**Control records stay closed and prose-free. Narrative bytes live only as content-addressed artifacts written through the same mutate, marked non-authoritative, never executed as instructions. Indexes are disposable. External actions go through an effect outbox with fencing tokens. Sleep may propose and may not promote.**

If approved later, the first code change is still a reviewed schema migration with old-version readability tests, on a synthetic root, not on the live VPS.

If rejected, M1 stops at what today's four statuses can express, and portfolio prose stays outside Ella-Brain until a different design is accepted. Do not half-implement the split by adding a free-string field "temporarily."

No other owner question is attached to this draft.

## 11. Non-authorization

This file authorizes no external write, no cron, no webhook, no merge, no deployment, no live patient access, no publication, and no new agent dispatch. Proposed owners in v3 are unchanged and remain proposals.

Initial success is unchanged from v3: a fresh session resumes a real portfolio task from external state and produces one reviewed artifact, without the owner rebuilding the context. v4 adds that this must remain true when the store is the wrong directory, a worker wakes up late, a web page tries to give itself permission, and a summary has dropped a fact that is still in the log.

## 12. Sources

Code inspected: `README.md`, `ella_brain/models.py`, repository tree of `maziyarid/Ella-Brain` at `450ba5a60be1f1aff2db21623377fec049c2609f`.

Prior plan: `Ella_unified_roadmap_v3.md` (blob `daecc852b049b4a3110065e82c07845c25438d5d`), including its X and Slack pointers. Not re-certified as a complete archive.

Papers and primary technical sources:

- Altmann, E. M., & Trafton, J. G. (2002). Memory for goals: An activation-based model. *Cognitive Science, 26*, 39–83.
- Cemri, M., Pan, M. Z., Yang, S., et al. (2025). Why do multi-agent LLM systems fail? arXiv:2503.13657.
- Dong, S., Xu, S., He, P., et al. (2025/2026). Memory injection attacks on LLM agents via query-only interaction. arXiv:2503.03704.
- Einstein, G. O., & McDaniel, M. A. (1990). Normal aging and prospective memory. *Journal of Experimental Psychology: Learning, Memory, and Cognition, 16*, 717–726.
- Garcia-Molina, H., & Salem, K. (1987). Sagas. *SIGMOD*.
- Gollwitzer, P. M., & Sheeran, P. (2006). Implementation intentions and goal achievement: A meta-analysis of effects and processes. *Advances in Experimental Social Psychology, 38*, 69–119. Effect reported as d = .65.
- Hagger, M. S., et al. (2016). A multilab preregistered replication of the ego-depletion effect. *Perspectives on Psychological Science, 11*, 546–573.
- He, X., Zhoubian, S., Yang, R., et al. (2026). Memory tax: Dissecting the net value of agent memory. arXiv:2610.34073. Submitted 25 Oct 2026.
- Johnson, M. K., Hashtroudi, S., & Lindsay, D. S. (1993). Source monitoring. *Psychological Bulletin, 114*, 3–28.
- Kleppmann, M. (2016). How to do distributed locking. https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html
- Liu, N. F., Lin, K., Hewitt, J., et al. (2024). Lost in the middle: How language models use long contexts. *TACL*. arXiv:2307.03172.
- McClelland, J. L., McNaughton, B. L., & O'Reilly, R. C. (1995). Why there are complementary learning systems in the hippocampus and neocortex. *Psychological Review, 102*, 419–457.
- Rasmussen, P., Paliychuk, P., Beauvais, T., Ryan, J., & Chalef, D. (2025). Zep: A temporal knowledge graph architecture for agent memory. arXiv:2501.13956.
- Risko, E. F., & Gilbert, S. J. (2016). Cognitive offloading. *Trends in Cognitive Sciences, 20*, 676–688.
- Stadler, T., Oprisanu, B., & Troncoso, C. (2022). Synthetic data — anonymisation groundhog day. *USENIX Security*.
- Starmer, A. J., et al. (2014). Changes in medical errors after implementation of a handoff program. *NEJM, 371*, 1803–1812.

Engineering notes already used by v3, plus:

- Anthropic. (2025, Nov 26). Effective harnesses for long-running agents. https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- Richardson, C. Pattern: Transactional outbox; Pattern: Saga. microservices.io.
- Letta. (2025, Apr 21). Sleep-time compute. Vendor research note, grade C.
- Debenedetti et al. AgentDojo. Prompt-injection benchmark for tool-using agents.

Discourse checked, not certified:

- Owner thread starting https://x.com/Maziyar_ID/status/2117516898699030646 including the 3 Nov soak/cron posts and the 4 Nov request to compare the roadmap with public practice (https://x.com/Maziyar_ID/status/2118021494257127669).
- Public posts on 4 Nov 2026 and the preceding weeks about silent memory failure, lossy compression, harness-versus-model, session logs, and vendor LoCoMo claims. Treated as grade C/D.

Secondary charts that quote memory-system leaderboards were read and not used as numbers. Where an abstract contained no percentage, this file does not invent one.
