# Ella Unified Roadmap v5 — Practical Continuity First

Version: 5.0. Revised: 2026-11-04, 20:43 Asia/Tehran (UTC+03:30).
Prepared by Perplexity at Maziyar's request.

## 1. Status and relationship to previous roadmaps

Owner direction in this conversation accepts the practical audit-and-harness sequence and requests publication of this revision. Publication of this document is documentation only: it does not authorize live-data access, deployment, scheduling, external effects, spending, merges or unrelated repository changes.

This is the latest execution-priority revision. The complete portfolio requirements, historical implementation ledger and parallel workstreams in [v3](Ella_unified_roadmap_v3.md) remain incorporated by reference. Where execution sequence or acceptance language conflicts, this v5 takes precedence. It does not discard v3's scope or claim to reproduce every section inline.

[v4](Ella_unified_roadmap_v4_unapproved.md) remains an unapproved design proposal. Its new planes, record kinds, research grades and atomicity claims are not accepted wholesale. Existing documents remain unchanged.

No live VPS audit or practical continuity harness has been independently demonstrated by this revision. A roadmap is not runtime evidence.

## 2. Governing objective

Ella must recover relevant project state, preserve interrupted work, delegate within verified capacity, produce a useful artifact, verify it and leave a resumable handoff without the owner reconstructing context.

Main order: existing core audit -> smallest practical continuity proof -> bounded real-project delivery -> medical CRM integrity -> Content Factory, SEO and Qalam -> broader portfolio expansion. Recurring obligations, permissions, privacy and non-regression controls remain required. Voice/UI work stays preserved in parallel and does not block text-first continuity.

Do not promise zero drift, total integrity, exactly-once effects across arbitrary services or a permanent cure. Judge observable behavior.

## 3. Current-code constraints: do not substitute labels for capabilities

Source inspection before this revision found:

- Task/Agent are closed schemas; task status is pending/active/blocked/done.
- Mutable fields are type/status/owner/deps; prose, priority, deadlines and artifact references are not current Task fields.
- The default schema and graph critics establish structural validity, not execution of business acceptance tests.
- active and done require dependencies to be done. An active checkpoint directly depending on pending children conflicts with that rule.
- get requires a known kind and ID. The inspected perceive helper does not discover all tasks by owner/status.
- Version history records stored changes, not briefs or evidence never represented in the store.

Refresh source identity during the audit. These findings are source inspection, not a live VPS test.

Consequently, neither a Task called evidence nor a done status proves that an actual artifact passed its test. Reload verification proves a persistence/read-back property, not correctness of project work. Highest priority and current step require explicit recoverable semantics, not improvisation from a fresh chat.

## 4. M0 — Read-only audit of the existing VPS installation

Historical owner reports describe source under /srv/ella-brain and seeded state under /var/lib/ella-brain. Those may be different legitimate roles, not evidence of a wrong-root defect. Verify rather than reinstall.

- [ ] Resolve authorized host, operator and narrowly scoped read-only access. No credential values in reports.
- [ ] Record actual source revision, dirty state, dependency/runtime versions and service entrypoint.
- [ ] Identify source directory, authoritative store root, existing data ownership and permissions.
- [ ] Establish service/scheduler status and whether actual Ella sessions call this store.
- [ ] Trace bootstrap discovery: how a new session obtains record IDs and reads current versions.
- [ ] Recover available test, cron, webhook and soak-test evidence without promoting historical claims to independent results.
- [ ] Identify existing backups and a non-destructive isolated test route. Do not seed, migrate or run mutation tests against the live root.

Exit artifact: concise capability map, exact inspected revision/root identities, file references, observed versus reported findings and concrete access gaps. Minimize personal data in collected evidence.

A blocked host audit must be reported precisely. Local experiments may continue against inspected source but cannot be labeled VPS verification.

## 5. Harness A — Establish the current engine's actual capability

Use an isolated disposable store and pinned source revision.

- [ ] Create a valid agent and small task dependency chain via supported interfaces.
- [ ] Exercise permitted transitions and reject an active task with unfinished dependencies.
- [ ] Restart the process, re-get known IDs and compare versions.
- [ ] Record how IDs were discovered: supplied known IDs are not autonomous bootstrap discovery.
- [ ] Execute one bounded mutate and independently re-read its result.
- [ ] Distinguish validation rejection from an uncertain post-write outcome.

Exit: commands, environment, test source, entity/version receipts and explicit limitations. Do not invent fields or overload dependencies to manufacture a passing result.

## 6. Harness B — Fresh-session project continuation

Use synthetic but realistic project material. No patient records, secrets, outward posts or live effects.

Required information: project identity, task brief, acceptance criterion, artifact reference/location, next unfinished step and one unresolved condition.

- [ ] Establish a documented bootstrap entry point, not hidden conversational memory.
- [ ] Persist the relevant information through supported interfaces. If impossible, record the exact representational gap instead of inventing a workaround.
- [ ] Session 1 reads current state, records baseline versions and performs one bounded step.
- [ ] Save actual output, check result and recoverable next action.
- [ ] End the process/session. Session 2 receives no earlier conversational history, only the documented bootstrap.
- [ ] Discover the task, re-get current versions, detect relevant changes and recover brief/constraints/next action.
- [ ] Continue to a useful artifact and verify against the acceptance criterion.
- [ ] Produce a short owner update: Done / Next / Blocked / Need you.

A negative result is useful evidence. Do not claim successful continuity because manually supplied prompts reconstructed what the store lacked.

## 7. Harness C — Interruption, worker limit and side-effect recovery

Build on the smallest successful continuation slice.

- [ ] Register a second commitment and introduce an urgent request under an explicit priority policy.
- [ ] Preserve the interrupted task's next action and resumption cue before switching.
- [ ] Inject worker unavailability/rate limit; checkpoint and reassign the same task with its artifacts.
- [ ] Verify that an obsolete worker cannot apply an outdated completion if concurrent execution is supported.
- [ ] Use a controlled side-effect stub with stable operation IDs; simulate a lost receipt and reconcile before retry.
- [ ] Demonstrate no duplicate effect in the tested cases; do not generalize to unsupported external services.
- [ ] Resume original work without dropped obligations or stale replies.

Record injected versus natural failures separately. Heartbeat expiry never proves an external action did not happen. Task rollback does not reverse reality.

## 8. Only then approve the smallest missing mechanism

If existing schemas cannot represent continuation information, propose a narrow schema/API change with:

1. The exact failed test and missing information.
2. Where artifact bytes live and how records reference/hash them.
3. How a fresh session discovers references.
4. Who can read/write them and how the gate enforces scope.
5. How actual test evidence binds to acceptance.
6. Migration/old-reader compatibility, crash behavior and restore plan.
7. Independent regression tests.

Do not introduce a second authoritative task database, hidden side files or an unrestricted prose escape. Markdown can be a generated readable view; no file format is inherently a memory architecture. Do not prohibit necessary task content merely to preserve an insufficient schema.

Do not assume record/blob atomicity from separate atomic file writes. Test or explicitly constrain it. New kinds, effect outboxes, leases/fencing, lifecycle states and root pins remain candidate mechanisms until justified and approved; not a mandatory all-at-once rewrite.

## 9. Retained portfolio and safety requirements

The detailed v3 requirements remain in scope:

- Source-backed recovery of projects, commitments, decisions and approved Qalam rules.
- Journaling, habits, social work, reflections and morning/evening/milestone obligations with explicit cadence, occurrence IDs and missed-run policy. No claim of scheduling without an operating service.
- Run checkpoints distinct from knowledge memory. Corrections, supersession, archive, expiration and deletion are separate operations. Expiration is not proof of erasure.
- Shared reusable context defaults to approved specs/procedures/tool contracts; task-specific facts follow project access. No patient data, journals or raw credentials in general shared context.
- Consequential permissions remain action/resource scoped. Owner-configured decision-safety policies do not authorize inferring incapacity.
- Runtime-enforced cost/step/retry limits, dead-end recovery and non-flooding owner updates.
- Medical CRM synthetic transaction/replay/reconciliation tests before live integration; no compliance claim.
- Content intent/title alignment, bilingual link/schema integrity, academic structures, factual-source checks and risk-based independent editorial review.
- Regression tests for restart, interruption, poisoning/scope violations, duplicate actions, correction and model/provider changes.
- Retention/deletion behavior must cover applicable indexes/derived records and documented backup handling. Do not delete authoritative unresolved commitments simply for age.

## 10. Preserve current progress and keep release claims narrow

- [x] Independent report for corrective pre-UI tree 1500683c8dbfc87db9fb3f68e7135f6520af5f5c: 69 backend / 25 frontend passes, typecheck/build successful. This is prior independent reported execution, not execution in this revision.
- [x] Owner supplied Grok Build UI handoff: local head 491e20b844dc1a15c578c388539d96d163c37d59, tree b2faf69b796c5366815c4f09110cf7a69f95a851, 32 frontend tests and bounded browser checks reported.
- [ ] Transfer full UI patch and independently review late-unknown handling, persistent page-load warning, focus and remaining wording.
- [ ] Original bundle/commit identity limitations remain explicit; reconstructed content equality is not original commit identity.
- [ ] Preserve continuity work at d02f459 and separate documentation publication decisions.
- [ ] Refresh remote branches/PRs before publication. No voice/UI deployment or current VPS upgrade is asserted.

Full historical details and checksums remain in v3 and the owner-supplied handoffs. Missing Claude report sections do not block tests whose inputs/evidence already exist.

## 11. Ownership and reporting

Proposed implementer: existing capable local build worker, after access/capability resolution. Independent reviewer: separate reviewer/session with reproducible artifacts. Perplexity retains evidence/priorities coordination. These roles are not claims of agent dispatch.

Every cycle must yield an artifact, verified state change or concrete blocker. Repeated reporting without progress triggers reassessment, not more summarization agents. Never claim work running without execution evidence.

## 12. Immediate execution order and stopping rule

1. M0 read-only audit.
2. Harness A for the existing engine.
3. Harness B for meaningful fresh-session continuation.
4. Approve only the missing mechanism demonstrated by B, if required.
5. Harness C for interruption/limit recovery and controlled effects.
6. One reviewed real-project deliverable, then incremental expansion.

Do not keep enlarging the roadmap before this proof. Stop and report the precise gap if bootstrap, representation or acceptance cannot be demonstrated honestly.

Success means observed recovery and useful work, not a valid graph alone.
