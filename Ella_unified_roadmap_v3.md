# Ella Unified Roadmap v3

Version: 3.0 — consolidated main roadmap, not a separate addendum.
Snapshot: 4 November 2026, 20:07 Asia/Tehran (UTC+03:30).
Prepared by Perplexity | roadmap, evidence and acceptance coordination.

## 1. Purpose, scope and governing priority

Ella must retain and advance the owner's portfolio through interruptions, unavailable workers, rate limits and fresh sessions, without requiring the owner to repeatedly reconstruct context or supervise every action. The system should reduce executive workload and produce useful reviewed deliverables, not reporting loops.

Primary sequence:

1. Reconcile and harden the existing deployed core and external state foundation.
2. Prove durable portfolio continuity, bounded delegation and safe recurring operations.
3. Develop the medical CRM transactional integration on that foundation.
4. Develop the Content Factory, SEO, bilingual publishing and Qalam workflow.
5. Expand to other projects using the same tested contracts.

A bounded real-project delivery pilot begins as soon as the minimum continuity slice works. Do not postpone all useful work until every infrastructure feature is perfected. Voice/UI work is preserved in a parallel lane, not a prerequisite for text-first project management.

This document consolidates the previous roadmap, the reliability plan, the retrieved X-discussion requirements and subsequent implementation handoffs. It supersedes their planning priorities while preserving evidence and historical revisions. It is a planning artifact, not proof that the new runtime is implemented or deployed.

## 2. Status and evidence rules

- [x] The named activity is complete at the evidence level stated.
- [ ] Pending, proposed, deferred, unverified or requiring a decision.
- Historical owner report, implementer report, independent reported execution and direct source inspection are distinct evidence categories.
- Perplexity has not personally executed the candidate suites or inspected the live VPS.
- Local implementation is not publication, integration, merge, deployment or unattended operation.
- Matching reconstructed trees does not establish original commit-object identity.
- A posted assignment is not acknowledgement or proof of execution.
- No numerical completion percentage, release ETA, zero-drift guarantee or once-and-for-all reliability guarantee is asserted.
- Proposed ownership in this document is not a new external dispatch.

### Completeness limitation

The original X post and accessible replies were followed through the domain-task extension discussion. Every branch/later reply was not established as retrieved. This roadmap covers identified requirements, not a certified complete archive of the entire conversation. Missing history becomes a source-recovery task; never invent it or require the owner to repeat everything from memory.

## 3. Owner needs and portfolio

The owner reports memory, focus and ADHD-related difficulties and needs continuity, prioritization and low-friction oversight. Do not infer incapacity, diagnosis details or decision-making ability from this report.

Known portfolio/context to recover and verify:

- Project management and agent orchestration.
- Content editing, Qalam and Content Factory/SEO operations.
- Medical CRM and asynchronous MySQL/SQL Server integration.
- Roya, named in the X discussion as an execution objective; current status to recover.
- Ella/OpenCode, MCP endpoints and reported 15+ execution nodes; present inventory and capabilities unverified.
- Xmemo/Engram; actual configuration, data and integration unverified.
- Finance, coding, simulation, research, design and self-growth as additional named areas, not invented active tasks.

Recurring commitments to recover: daily journaling, reflective dreaming, social posts, habits, morning/evening loops and urgent milestones. Cadences, destinations, permissions and current activation are not assumed.

User-facing contract:

- One inbox; new topics do not silently replace execution priorities.
- Short view: Done / Next / Blocked / Need you.
- At most one consolidated decision request at a time by default.
- Preserve interrupted work and the next recoverable action.
- Never claim remembered without persistence and retrieval evidence.
- Never claim unattended monitoring from a chat-only session.
- Do not expose raw diagnostics as the default owner update.

## 4. Corrected deployment baseline: preserve before changing

### Historical core deployment

- [x] Owner publicly reported deploying and seeding Ella-Brain on a VPS, with 26 tests passing and perceive/interpret/plan/act/review nodes under /var/lib/ella-brain.
- [x] Owner later referred to source under /srv/ella-brain.
- [ ] Independently establish the present revision, process/service, store, permissions and health.
- [ ] Determine whether actual Ella sessions consult this engine or whether it only contains demonstration nodes.
- [ ] Determine which project workflows and workers actually use its gated interfaces.
- [ ] Preserve data and configurations before migration; do not reinstall/reseed blindly.

Correction to earlier broad wording: an original core deployment was owner-reported. The newer voice/UI upgrade is not confirmed deployed, and current operation of the older core is not independently verified.

### Existing core contract described in the discussion

Task and Agent records have closed schemas and versioned JSON files. Required fields include id, type, status, owner, deps, version, created and updated. Reported task statuses are pending/active/blocked/done. The supported access path is get/mutate, not arbitrary agent filesystem writes.

The reported mutation sequence is load -> prevalidate -> critique -> versioned atomic write -> reload/verify -> return. Default schema-critic and graph-critic are separate deterministic checks, not proof of two independent network reasoning models.

Important qualifications:

- A typed store does not establish that every session retrieves relevant state.
- Single-record atomic writes are not automatically request-wide transactions across several mutations.
- Post-write reload verification does not mean no write ever preceded an exception.
- Version history is not a proven tamper-proof audit merely because older files are retained.
- Actual atomicity, crash recovery and permissions must be measured in the deployed configuration.

## 5. Preserved implementation and verification ledger

### 5.1 Voice/error-handling work

- [x] Published boundary branch through a5c936df reported present.
- [x] Voice locally implemented 09069fb2: JSON/error classification and presence-based proxy-header checks.
- [x] Voice locally implemented 3a6c32a1: accurate Persian unknown-outcome text and assertion.
- [x] Ella and Claude independently reconstructed expected source trees and reported 67 backend / 24 frontend passes for the pre-correction candidate.
- [x] Claude reproduced post-write ValueError misclassification by injection, not a known natural production trigger.
- [x] Claude naturally observed setup agent/dependency writes before target rejection; Ella independently corroborated.
- [x] Voice locally implemented 8fe272b1: generic 400 bad_request becomes unknown outcome; dependency read-back scoped to rejected target, with setup-write disclosure.
- [x] Regression tests and documentation delivered.
- [x] Ella independently reconstructed tree 1500683c and reported 69 backend / 25 frontend passes, typecheck/build success, at 17:05.

No natural post-write ValueError trigger was found in the bounded investigation; this is not proof of absence. The backend may still return 400 after injected persistence; the frontend correction treats that response conservatively.

### 5.2 UI readiness

- [x] Prior local UI commit 7621b0e reported: visible notes/status, failure alerts, language/direction handling, proposal focus, pack expanded semantics and focus styling.
- [x] Grok Build reported reproducing lost uncertainty after a fresh Start and an invisible focused-status ring.
- [x] Grok reported fixes in 378cabe9 and 491e20b8: page-load uncertainty log, late-unknown handling and removal of outline suppression.
- [x] Grok reported 32 frontend tests, successful typecheck/build and bounded headless built-preview checks at final source.
- [x] Runnable browser-check subset reported added; it does not cover all keyboard/viewports.
- [ ] Obtain transferable full and incremental patches and browser script.
- [ ] Independently reproduce final tree and inspect uncertainty-log lifecycle, late-response isolation and focus behavior.
- [ ] Confirm outcomes are associated with correct requests/sessions and cannot trigger stale speech/tools.
- [ ] Decide whether page-load-only uncertainty persistence is adequate for this preview; it is not durable task memory and reload loses it.
- [ ] Review speech-failure phrase 'Nothing extra was stored' beside uncertain gate outcomes; proposed alternative: 'Spoken audio failed. The text reply remains available.'
- [ ] Decide bounded Mute label clarification; existing behavior affects incoming audio, not outgoing TTS.
- [ ] Record real screen-reader, microphone, Resume and repeated-alert announcement gaps honestly.

### 5.3 Continuity

- [x] Branch fast-forward b67bc80 -> d02f459 reported executed and independently rechecked.
- [x] Signed-register verifier, adapter trust constraints and inventory improvements reported implemented at d02f459.
- [x] Non-root independent rerun reported 143 passed, zero skipped, 119 subtests inside the 143 collected methods; 16 checker fixtures passed.
- [x] Ella relayed proposed PR #1 body; Continuity completed factual review.
- [ ] Correct body to lead with non-root result; two permission-test skips are root-specific.
- [ ] Apply corrected body through appropriate authorization; no application confirmed.
- [ ] Keep 6573f985 -> f2d133d separate documentation chain excluded unless explicitly selected for publication.

### 5.4 Revision identities

| Object | Identity | Evidence/status |
|---|---|---|
| Ella-Brain main | 9132753e4be980c75269be6de2658134e4960208 | Latest earlier report; refresh before writes |
| PR #2 head | c37cd07e9945d5fd6051fc31f2b50bcfa5bebce4 | Latest reported draft/unmerged |
| Published boundary branch | a5c936df8b908b0001527384d45c9b9a0a44f88b | Latest reported held |
| First local correction | 09069fb28ecc1a62a90ebc01e18d54d924a9dc4c | Source independently reconstructed |
| Wording follow-up | 3a6c32a10afa3baff4376f959153e443c6f30b2d | Source independently reconstructed |
| Voice corrective head | 8fe272b12f3f17a33d9c88533bff7a77a34329be | Original object not independently verified |
| Verified pre-UI tree | 1500683c8dbfc87db9fb3f68e7135f6520af5f5c | Independent reconstruction report |
| Local reconstructed pre-UI commit | 63893fa0cb7052d3a2761976f89ed0692650809d | NOT Voice's original commit |
| Prior local UI commit | 7621b0ed2fa0008072990a252378758bb66ae711 | Prior-session handoff, author label Claude |
| Prior UI tree | 1368c8606eeb5a193c977d16b7bc73663efce090 | Reported |
| Grok follow-up | 378cabe980f94f6058f2ca6ab7cd409909256560 | Reported |
| Latest UI local head | 491e20b844dc1a15c578c388539d96d163c37d59 | Grok report, not published |
| Latest UI tree | b2faf69b796c5366815c4f09110cf7a69f95a851 | Independent review pending |
| Ella continuity main | 8269aa19844c03e38848222acfd58154896e6498 | Latest reported unchanged |
| Continuity PR #1 head | d02f4591a213fc0ec7e5b332528f0e7277a3cd3d | Latest reported draft/unmerged |

Preserve authorship attribution from existing objects; explain inherited/reconstructed work instead of rewriting history to claim it as another agent's work.

### 5.5 Artifact checksums

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| 09069fb boundary patch | 14630 | 93adc60f822900649cd013b860783a900ed795ae2a71df9faf6d0126a510d633 |
| Original two-commit bundle | 6987 | 770b5b1eb4a0f677debeb1d0d408a59df6cb443345c98f5795e55ede7b0461be |
| 8fe272b corrective diff | 13007 | e197b61cfde7d1c07b3e2a70ab466ce46de6682a62b378c58baa31bc88eb1407 |
| Prior UI patch | 23610 | 5c1d34dd983ccdd2feb3fc2c5e446ae3bab304a9475446886a2505cdd3ee1386 |
| Grok incremental UI patch | 22396 | d794b0e70c24dc785c78764515db3f726292b09c7f06eca86185ee753c665d90 |
| Full UI patch from reconstructed pre-UI | 38521 | 13b758aab2de61e10b6623562660e68e0eb5f382e67a2f80676a224485aaebdb |

Original bundle only contains 09069fb/3a6c32a above a5c936df, not later corrections/UI. Reviewers reported binary-retrieval limitations; do not generalize that every connector lacks a file reader. Bundle bytes and original objects remain unverified; source reconstruction remains valid content evidence.

## 6. Requirements traceability: all 17 identified failure patterns

These originate in the owner's retrieved post; they are requirements/failure reports, not a claim of independent diagnosis.

| ID | Failure pattern | Required control | Acceptance evidence |
|---|---|---|---|
| R01 | Context/state degradation | External canonical state, startup retrieval, supersession | Fresh-session recovery test |
| R02 | Asynchronous agent stalling | Leases/heartbeats, bounded failover, outcome reconciliation | Worker failure/reassignment test |
| R03 | Fatigued-state approval concern | Owner-configured decision-safety mode | Policy-specific high-impact approval test |
| R04 | Telemetry pollution | Short owner view; separate redacted traces | Useful update without raw log flood |
| R05 | Focus fragmentation | Inbox vs execution priority; checkpoint/resume | New-topic interruption test |
| R06 | Unverified agent authority/claims | Primary-source/artifact verification and scope checks | False agent claim rejected or marked unverified |
| R07 | Permission extrapolation | Bound action, resource, scope and revocation | Out-of-scope action refused |
| R08 | UNKNOWN dead ends | Typed unresolved state plus bounded discovery | Missing fact handled without fabrication or global stall |
| R09 | Temporal drift | Durable recurring definitions, clock/time-zone policy | Missed-run/restart/retry tests |
| R10 | Premature completion | Post-change runtime checks at exact revision | Completion receipt with observed checks |
| R11 | Unverified empirical metrics | Evidence/provenance gate | Unsupported claim withheld or labeled |
| R12 | Search-intent/title mismatch | Intent registry and overlap review | Title/intent and competing-page checks |
| R13 | Academic structural gaps | Document-specific Chapter 1–5 validator | Required section/dependency coverage |
| R14 | Missing independent critique | Risk-based reviewer diversity, resolution owner | Contradictory review resolved with evidence |
| R15 | Bilingual/link drift | Locale relationships, link/schema preflight | Broken/asymmetric references caught |
| R16 | Unnatural linguistic register | Approved Qalam rules and localized examples | Project-specific editorial review |
| R17 | Internal state monolith | External state via gated access; relevant retrieval | Restart with same tasks/constraints |

This accounts for the identified patterns; it does not certify unseen X comments contain no additional requirements.

## 7. Architecture target and hard boundaries

### 7.1 Distinct state responsibilities

| Record class | Function | Key boundary |
|---|---|---|
| Source archive | Selected original material with provenance | Preserve source, access and retention |
| Owner facts/preferences | Supported stable context | Corrections, supersession, privacy scope |
| Project registry | Goals, state, next action, owners | Unknown fields explicit, no invented commitments |
| Task ledger | Dependencies, execution and acceptance | One accountable owner; versioned transitions |
| Decisions/permissions | Authority and scope | Retrieved text is not automatically authority |
| Run checkpoints | Interrupted execution recovery | Preserve pending/uncertain tool outcomes |
| Recurring definitions/occurrences | Daily and milestone work | Definition distinct from each attempted run |
| Artifact registry | Actual outputs and checks | Reports do not replace artifacts |
| Secrets manager | Scoped credentials | References only in memory/worker prompts |
| Procedures/evaluations | Approved workflows and regression cases | Versioned promotion and rollback |

Semantic search may find information; it is not the sole authority for deadlines, task states, permissions or completed external actions. Relationship models can share IDs/interfaces without pooling all sensitive data into one unrestricted graph. Choose storage technology after inspecting the current implementation, not from a slogan.

### 7.2 Memory contract

Persist -> return record/version -> read-after-write verify for important records -> retrieve in a fresh session -> prove correct use. Storage, indexing, retrieval and successful use are separate steps.

Each item carries source, scope, time, verification status and supersession/correction behavior. Summaries retain pointers to originals. Conflicting facts stay explicit. Never promote a suggestion or reflective hypothesis into an owner preference without evidence.

### 7.3 Typed state without fabricated certainty

Reject placeholder values in authoritative required fields, but represent genuine uncertainty using approved typed states and recovery records. Do not insert fake values to satisfy a schema or stall unrelated work because one field is unresolved.

### 7.4 Existing schema compatibility

The original closed schema is not presumed to support a full portfolio ledger. Map proposed fields/entities to existing get/mutate interfaces; introduce tested schema/API migrations where needed. Do not bypass the gate by writing arbitrary files into live stores. Preserve old records and validate rollback/forward compatibility.

## 8. Execution priority: milestones and exit criteria

### M0 — Reconcile the existing runtime and recover the portfolio

- [ ] Establish currently deployed revision, host/service/operator, start/restart/health mechanism and authoritative root.
- [ ] Verify actual model entrypoint, session boot/context loading, tool execution, scheduler and storage.
- [ ] Check Ella session -> get/mutate -> persisted record -> next-session retrieval path.
- [ ] Inventory accessible MCP/OpenCode workers and Xmemo/Engram integration; distinguish configured, reachable and operational.
- [ ] Search authorized sources for projects, decisions, obligations and artifacts; list gaps and unavailable sources.
- [ ] Deduplicate and preserve provenance/conflicts; owner reviews only material ambiguities.
- [ ] Inventory credential references/provider/scope without collecting raw key values.
- [ ] Capture non-destructive backup/restore plan before migration.

Exit: source-backed capability map and recovered portfolio; one real session reads existing persisted state. Historical paths/deployment are verified or clearly marked stale/unavailable. No reinstall/reseed assumption.

### M1 — Durable portfolio continuation vertical slice

- [ ] Implement compatible project/task records and read/write receipts.
- [ ] Load owner constraints, open commitments, active project state and interrupted runs at startup.
- [ ] Retrieve relevant details rather than flooding context with full archives.
- [ ] Preserve task next step and artifact references across restart.
- [ ] Detect conflicting updates rather than silently overwrite.
- [ ] Separate project/client scopes.
- [ ] Keep uncertain external actions in needs_reconciliation, not safe-to-retry.

Exit: fresh process/session resumes a prior task from external state without owner restatement; one useful reviewed artifact is produced. Start a bounded delivery pilot here rather than wait for every later feature.

### M2 — Product management, interruption and delegation

- [ ] Separate conversational question answering from reprioritization.
- [ ] Default new topics to inbox capture; replace active priority only on explicit instruction or pre-agreed urgent-work policy.
- [ ] Use validated task lifecycle states such as inbox/triaged/ready/assigned/running/blocked/awaiting_review/needs_reconciliation/done/cancelled/superseded; map to existing schema through approved changes.
- [ ] Distinguish dispatch, acknowledgement and actual execution.
- [ ] Record worker tools, project scope, availability, rate limits, capability verification and cost envelope.
- [ ] Assign bounded input, deliverable, acceptance criteria, time/tool budget and checkpoint/stop rule.
- [ ] Use leases/heartbeats or equivalent real liveness mechanism.
- [ ] On worker failure, reconcile in-flight side effects before reassignment; preserve task ID/artifacts.
- [ ] Keep one accountable writer for coupled edits; parallelize genuinely independent work.
- [ ] Before owner escalation, perform bounded source lookup, alternative method or specialist check within permission.
- [ ] Block only the dependent task; continue independent authorized work.

Starting WIP policy to test: one substantial task per worker and one integrating change per shared code area. Tune from measured capacity, not assumed universal limits.

Exit: urgent request arrives, normal task checkpoints, independent work delegates, a worker rate-limits, replacement resumes, original task continues, no duplicate external action occurs.

### M3 — Recurring operations and temporal integrity

- [ ] Recover precise cadence/destination/time zone/policy for morning/evening loops, journaling, habits, social drafts/posts and milestones.
- [ ] Separate recurrence definition from each occurrence with stable occurrence IDs.
- [ ] Track next due, last attempt, last success, failure and missed-run states.
- [ ] Deploy a real scheduler only after target/scope approval; assign health/restart owner.
- [ ] Configure skip/coalesce/catch-up behavior; prevent floods after downtime.
- [ ] Reconcile publication outcomes before retries.
- [ ] Default social work to drafts absent verified publication authority.
- [ ] Journal observed/supplied events, never invented completion.
- [ ] Label dreaming as reflective hypotheses; do not silently change facts, priorities, habits or policies.

Exit: clock/restart/missed-trigger simulation plus deployed health evidence when activated; duplicate publication prevented in supported retry cases. Chat promises do not satisfy this milestone.

### M4 — Medical CRM transactional integration

- [ ] Recover actual data owners, workflow boundaries, MySQL/SQL Server mappings and synchronization direction.
- [ ] Define authoritative record/field source and permitted schema changes.
- [ ] Validate required fields and pre/post conditions using synthetic patients.
- [ ] Test duplicate events, out-of-order delivery, partial failure and reconciliation.
- [ ] Define transaction boundaries, audit evidence and compensating actions; do not claim distributed atomicity without implementation evidence.
- [ ] Keep unknown outcomes explicit; no silent fallback to plausible values.
- [ ] Separate patient access, secrets and retention from general agent memory.
- [ ] Require scoped privacy/security approval before live patient integration; no compliance certification implied here.

Exit: synthetic end-to-end ledger demonstration with restart/replay/reconciliation evidence and accountable operational owner. Live enablement is a separate gate.

### M5 — Content Factory, SEO and Qalam

- [ ] Recover approved Qalam rule set, localized examples and project-specific acceptance criteria.
- [ ] Model content identity, target query, intent silo, locale, canonical and translated counterparts.
- [ ] Check title/intent alignment and competing pages before publication.
- [ ] Validate links, reference existence, bilingual symmetry and relevant structured-data relationships.
- [ ] Apply Chapter 1–5 structures to required academic document types, not every artifact.
- [ ] Require sources for material facts, citations and empirical/competitor metrics.
- [ ] Use independent editorial critique for substantial/high-risk outputs with a named resolution owner.
- [ ] Treat multi-model agreement as evidence, not truth; deterministic checks and primary sources remain necessary.
- [ ] Maintain draft/review/publish separation and scoped authorization.

Exit: one real reviewed draft/artifact with passing relevant structural/link/intent checks; later publication uses exact approved content and scope.

### M6 — Controlled growth and non-regression

- [ ] Convert demonstrated failures into versioned tests with held-out scenarios.
- [ ] Track retrieval correctness, continuity, missed obligations, duplicate actions, review failures, cost and owner interventions.
- [ ] Compare candidate models/prompts/procedures against the same baseline.
- [ ] Require critical safety/authority/continuity tests before promotion.
- [ ] Shadow consequential changes and retain rollbackable configurations/migrations.
- [ ] Prevent self-reflection from rewriting owner facts, permissions or test expectations.
- [ ] Validate backup restoration in isolation.

Exit: provider/model change or new skill preserves critical behavior; failed experiments stay quarantined. Growth means measured capability, not automatic self-modification.

## 9. Approval safety and authority governance

- [ ] Recover the owner's desired policy for low-alert/fatigued periods.
- [ ] Offer explicit user-set defer-consequential-decisions mode, quiet hours or fresh confirmations for selected high-impact operations.
- [ ] Keep low-risk already-authorized work moving.
- [ ] Never infer incapacity from ADHD, time of day or writing style.
- [ ] Bind approvals to actor, action, target, content/scope and revocation/expiry where applicable.
- [ ] Preserve separate gates for deployment, merge, spending, live data and outward publication.
- [ ] Do not treat worker signatures/shared-account names as owner approval by themselves.
- [ ] Verify consequential external claims against primary artifacts/revisions; label unverifiable claims.

Standing owner preferences do not bypass tool-specific confirmation gates. This document itself authorizes no external write, scheduling activation or live-data access.

## 10. Anti-loop operations and communication

Proposed pilot policy:

- Every work cycle ends in an artifact, validated state change or concrete blocker.
- Two consecutive cycles without one trigger reassessment, not another summary task.
- Same blocked condition is deduplicated unless evidence/deadline changes.
- No agents whose only output is summaries of other summaries.
- Enforce tool/time/cost budgets in the runtime where possible.
- External UNKNOWN results trigger bounded discovery/reconciliation, not fabricated completion.
- Logs/traces are redacted and separate from owner-facing status.
- Do not expose private chain-of-thought; record decisions, inputs, outputs and tool evidence.

Default owner update:

Done: actual artifact and short result.
Next: highest priority and accountable owner.
Blocked: reason and recovery action.
Need you: one concrete decision, only when required.

## 11. Acceptance and regression suite

| Scenario | Observable requirement |
|---|---|
| Session restart | Retrieve actual saved constraints/projects/next action with source IDs |
| Decision correction | New verified version supersedes old while retaining provenance |
| Missing information | Targeted bounded lookup, explicit unresolved state, no invention |
| Topic change | Current execution remains checkpointed and prioritized correctly |
| Urgent client task | Safe preemption/delegation; original work resumes |
| Worker rate limit | Same task/artifacts recovered; no duplicate action |
| No worker available | Honest queue/block state, not fictional running status |
| Crash after external write | Outcome reconciliation before retry |
| Concurrent update | Version conflict detected |
| Missed scheduled run | Correct skip/coalesce/catch-up behavior |
| Publication retry | Stable occurrence/idempotency handling; no blind replay |
| Privacy boundary | Unrelated client/patient records unavailable to workers |
| Secret handling | No raw keys in prompts/fixtures/reports/exports |
| Approval scope | Specific grant not generalized to new resources/actions |
| Decision-safety mode | User-defined high-impact defer/confirmation policy respected |
| False third-party claim | Primary evidence sought, unsupported completion withheld |
| Runtime validation | Done status linked to post-edit checks at actual revision |
| Content intent/link tests | Overlap, broken references and bilingual mismatch detected |
| Academic/Qalam tests | Required structure and approved register checked |
| Model change | Critical baseline passes before promotion |
| Backup restore | Commitments and pending runs recover in isolation |
| Real delivery | Reviewed usable artifact, not only a plan or test count |

Do not invent benchmark percentages or exactly-once guarantees for arbitrary third-party services. Establish quantitative targets from pilot baselines. Safety/authority/duplicate-action failures block relevant live write enablement.

## 12. Known preview limits and unfinished parallel work

- [ ] Request timeout absent; abort never implies rollback.
- [ ] Local operator boundary is not authentication; local processes omitting headers can pass.
- [ ] Forged exact known-rejection pairs remain a trust limit.
- [ ] Cancel state lost after restart; duplicate flag differs after restart.
- [ ] Two adapter processes sharing a store remain untested.
- [ ] Actual dev loopback runtime binding and CLI override behavior need scoped acceptance.
- [ ] Real screen reader, microphone privacy/network behavior and full supported-browser coverage incomplete.
- [ ] fa-007 synthetic flag coverage and other Persian copy findings remain open.
- [ ] Preview memory stays mocked; page-load uncertainty log is not conversational or business memory.
- [ ] Preserve immediate Kill/Stop; deletion confirmation/undo is separate UX scope.
- [ ] Review UI residuals without allowing cosmetic polish to block core continuity work.

Embodiment-shadow design remains undeployed/unproven in this record and is deferred behind portfolio continuity. Any later design must define interfaces, non-goals, permissions and acceptance tests.

## 13. Trust and live-memory prerequisites

- [ ] CONT-D6 signing key and fingerprint pin location.
- [ ] Owner-protected anchor storage/advancement, not rolled back with the same backup.
- [ ] Freeze/freshness protection.
- [ ] Per-family live-format descriptions and compatibility.
- [ ] CONT-D7 scoped owner-approved inventory of actual live layout.
- [ ] Resolve unsigned manifest owner-approval claims.
- [ ] Separate authorization/validation for /home/ella adapter use, currently refused in prior reports.
- [ ] Exercise GnuPG-unavailable behavior instead of reporting inspection as execution.
- [ ] Decide repository privacy restoration after temporary public work period.

New project-memory components must not bypass these restrictions by being renamed. Keep synthetic development distinct from trusted live authority.

## 14. Proposed ownership and first implementation brief

| Lane | Proposed responsibility | Deliverable |
|---|---|---|
| Grok Build | Existing core/runtime audit and minimum continuity slice | File-referenced capability map, runnable local proof, patch/tests |
| Ella | Independent continuity/delegation acceptance and UI review | Reproduction evidence, defects and explicit acceptance scope |
| Perplexity | Requirements recovery, priorities, evidence reconciliation | This unified roadmap and bounded briefs |
| Continuity successor | Storage/trust compatibility review | Material constraints, no parallel redesign |
| Voice/UI | Preserve work and answer targeted review findings | Transferable patch and checksums |
| Specialists | Bounded project-specific delivery | Reviewed code/content/research artifacts |

These are proposed allocations, not proof of dispatch or availability. User-session success in Grok Build does not establish an unattended API integration.

First brief:

1. Inspect the existing runtime and historical VPS deployment without destructive changes.
2. Map actual session/state/tool/scheduler paths with file references.
3. Prove a fresh session reads one existing project/task through supported interfaces.
4. In an isolated synthetic environment, persist multiple project commitments, delegate a bounded subtask and save output references.
5. Restart, inject urgent work and a worker limit, resume the old task without duplicate actions.
6. Produce one reviewed artifact and a short owner update.
7. Return exact source identity, commands, tests, gaps and migration needs.

No broad framework migration, new live schedules, external posts, real patient access or deployment as part of the initial proof. Reuse what works; implement only demonstrated missing paths.

## 15. Publication, deployment and rollout

- [ ] Refresh actual remote heads and PR state before any write.
- [ ] Resolve exact destination branch/PR update workflow; do not confuse separate boundary branch with PR head.
- [ ] Verify accepted commit/tree/ancestry; original and reconstructed commits differ.
- [ ] Obtain action-specific confirmation where required.
- [ ] Publish accepted revision only, then independently reread remote state.
- [ ] Make explicit draft/merge/deployment decisions; review acceptance is not deployment authorization.
- [ ] Select target host/service/scheduler operator and health/restart owner.
- [ ] Begin read-only/draft operation before consequential live writes.
- [ ] Run recovery/security/regression checks in target environment.
- [ ] Define health checks, stop/cleanup, rollback and data-compatibility procedures.
- [ ] Roll out scoped project capabilities incrementally after relevant trust/privacy gates.

Application rollback does not undo persisted business actions. Failover must reconcile side effects, not assume task-state rollback reverses reality.

## 16. Evidence sources and retrieval limitations

### Coordination record

https://ella-7tc1505.slack.com/archives/C0CC6MD4HNJ/p1793782513862549

Key timestamps:
- Original Voice bundle: 1793792006.344369.
- Continuity body review: 1793792549.067369.
- Ella initial reconstruction: 1793796374.883349.
- Claude findings: 1793796979.792889 and 1793796991.491819.
- Ella corrected recommendation: 1793797371.141109.
- Corrective assignment: 1793797444.501659.
- Voice correction: 1793797637.026259.
- Corrective text attachment: 1793797674.787099; file F0CEN0LBGTD.
- Ella independent corrective review: 1793799301.265269 (17:05).

Latest 20:07 refresh returned no newer messages. Later UI evidence is supplied by the owner in this conversation, not a retrieved Slack handoff.

### Owner/Grok X discussion

Original: https://x.com/Maziyar_ID/status/2117516898699030646
Workload explanation: https://x.com/Maziyar_ID/status/2117523474436514195
Priority order: https://x.com/Maziyar_ID/status/2117525516404060550
Interruption/memory requirements: https://x.com/Maziyar_ID/status/2117528248368181511
Core contract/progress: https://x.com/Maziyar_ID/status/2117537935591440422
Historical VPS deployment report: https://x.com/Maziyar_ID/status/2117543825568633289
Domain extension discussion exposed further replies; not all branches/later comments established retrieved.

Treat 'zero session drift', 'only stable base' and 'total structural integrity' in conversation as claims, not verified guarantees. A graph database is not mandated by those assertions. Preserve logical relationships and integrity requirements while choosing technology from existing-runtime evidence.

### Engineering pattern research

https://www.anthropic.com/research/effective-harnesses-for-long-running-agents
Long-horizon coding examples support progress artifacts, incremental tasks and tests; not a guarantee of personal-assistant reliability.

https://www.anthropic.com/research/multi-agent-research-system
Supports explicit delegation and orchestration with cost/coordination trade-offs; research-system results do not predict Ella performance.

https://www.langchain.com/blog/runtime-behind-production-deep-agents
Vendor runtime description distinguishes durable execution, memory, scheduling and observability; not independent evidence that migration to its stack is needed.

Perplexity also inspected baseline server.py, synthetic.py, gate.py and _stages.py via GitHub earlier in this conversation. This was source inspection, not current VPS verification or final candidate execution.

## 17. Immediate next actions and definition of initial success

1. [ ] Transfer final UI artifacts and preserve their identities; leave them in a bounded review lane.
2. [ ] Perform M0 existing-core audit and source-backed portfolio recovery.
3. [ ] Implement/test only the missing M1/M2 continuity path.
4. [ ] Demonstrate a real reviewed deliverable and fresh-session resume.
5. [ ] Activate recovered recurring commitments only with explicit schedules, scope and operational ownership.
6. [ ] Advance medical CRM then Content Factory domain integrity using the same proven contracts.
7. [ ] Keep controlled non-regression evaluation active throughout.

Initial success is not 'every project complete'. It is Ella demonstrably retaining the portfolio, handling interruptions, distributing bounded work and producing useful outputs without repeatedly offloading reconstruction to the owner.

This document preserves current progress and merges identified missing requirements into the main plan. It does not claim unseen discussion coverage, runtime deployment, new agent dispatch, scheduler activation or live-data authorization.
