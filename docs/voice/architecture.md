# Voice preview architecture

Integration baseline: `9132753e4be980c75269be6de2658134e4960208` (`main` after the hardening merge). This branch adds a browser prototype and a localhost adapter beside the hardened gate. It does not change `_io.py`, `_stages.py`, the Task/Agent schema, or the hardening tests. Those files are the merged gate, checked by hash at adapter startup.

## Boundary

`apps/ella-voice-preview` is a Vite + React app. The original console ran inside a Grok App Builder shell (TanStack Start, auth scaffold, PWA injector). Those platform files are not part of Ella-Brain and are not in this branch. The editable behavior is the console, the reducer, the fixture planner, and the Persian pack.

`ella_channel` is a local adapter. It calls `Ella.get` and `Ella.mutate` for two synthetic sentences. It does not import the private write path to publish its own files. Preview memory stays in the browser.


## Session

`reduce` in `src/lib/ella/machine.ts` is the only state transition. Phases are `idle`, `listening`, `thinking`, `speaking`, `reconnecting`, `unavailable`, and `ended`.

Preview state has two homes:

| Data | Where | Lifetime |
|---|---|---|
| Phase, transcript, proposal, tool receipts, principal flag | React state, in memory | Lost on reload. Cleared on start (new transcript) and resume (new session id, transcript and tools dropped). |
| Accepted memory records | `localStorage` key `ella-channel-preview-v0` | Survives reload and resume until "Delete preview memories". Not sent anywhere. |

`SESSION_TTL_MS` is 30 minutes from `startedAt`. An event that carries `now` after that ends the session and drops the pending proposal. It does not delete accepted memories.

| Action | Effect |
|---|---|
| Start | New session id, listening, transcript and tool receipts cleared. Accepted memories kept. Microphone is requested; denial only changes the on-screen note. |
| Resume | New session id, listening, transcript and tools cleared, accepted memories kept, then the same microphone request as start. |
| Reload | In-memory session is gone. Accepted memories are read back from `localStorage` into an idle channel. |
| Reset / delete | The delete control writes an empty memory list to `localStorage`. It is not a brain mutation. |

## Rules that are implemented

- Guest never receives the public-context tool or a memory proposal. `بله` does not write.
- A proposal is not memory. Accept requires the exact proposal id and the local reviewer flag.
- The exact tokens `بله`, `آره`, and `yes` accept the visible card. `بله، و به علی هم زنگ بزن` is an ambiguous approval: the card stays, nothing is written, and there is no dial action in the model.
- Cancel and reject do not write.
- Accept appends a read-back turn whose text is the accepted string.
- Resume reloads only accepted preview records.
- A second `retrieve_public_context` for the same session key is stored as `duplicate: true` with the first summary. Reconnect does not add a receipt.
- Speech-synthesis failure calls `speak_done` and leaves the channel listening.
- Stop, interrupt, end, and kill bump the epoch or end the phase so a stale reply cannot commit. Kill moves to `unavailable` and clears the proposal.

Exact-string acceptance is a prototype rule. It is not the production Persian approval design.

## Mocked tool

`planTurn` may return `retrieve_public_context`. The summary is a frozen, SHA-free sentence (`PUBLIC_CONTEXT` in `apps/ella-voice-preview/src/lib/ella/fixtures.ts`): "Public GitHub main of maziyarid/Ella-Brain is the hardened baseline. Writes go through get and mutate only. This browser does not read people files or private memory." The browser does not call GitHub and does not read private memory.
