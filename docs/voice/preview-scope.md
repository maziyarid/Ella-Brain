# Preview scope

This page is a local browser demonstration.

- The local reviewer flag is not authentication. It does not identify Maziyar or anyone else.
- Guest and reviewer UI behavior is not production authorization.
- Mocked tools are not a live Ella-Brain integration. Nothing calls `get` or `mutate`.
- The public repository sentence in the fixture is not private memory.
- Accepted preview memories are not the four-component memory system. They are JSON in this browser.
- A device `fa-IR` voice, if the browser has one, is not an evaluated Ella voice.
- No telephone capability is implemented or verified. The page does not buy a number, open a provider session, or place a call.
- No Persian speech-recognition, pronunciation, or naturalness score has been established.
- Qalam has not been applied. No approved profile was resolved.

The demonstration banner says not to enter private information. The reviewer switch is visible as a flag, not a login.

Persian is the primary product language. The fixture replies are fixed Persian strings plus the user's own accepted text. They are not evidence that a model is generally competent or generally incompetent at Persian. The interface has not been reviewed by a Persian editor, and device recognition quality is unknown.

## Where state lives

| Data | Where | Survives reload |
|---|---|---|
| Accepted preview memories | `localStorage` key `ella-channel-preview-v0` | yes, until Delete |
| Session id, transcript, proposal, tool ledger | page memory only | no |
| Reviewer flag | page memory only | no; reload returns to guest |

- **Start** opens a new session id, clears the transcript, proposal, and tool ledger, and keeps accepted memories.
- **Resume** keeps accepted memories, opens a new session, and does not promote the old transcript.
- **Reload** drops the session and restores only accepted memories. The flag returns to guest.
- **Stop** goes idle, drops the pending card without writing, and ignores a delayed utterance or card acceptance until Start.
- **Audio unavailable** stays on the typed path. It does not freeze the page. The kill switch is the hard stop.
- A reply is bound to the session id and the epoch. A reply from an older session cannot land on a newer turn, even if the epoch number matches.
- Switching from reviewer to guest while a reply is pending drops that reply. It does not write memory and does not run the mock tool.

Exact `بله` is a prototype rule for the card on screen. It is not the production design for Persian approval.
