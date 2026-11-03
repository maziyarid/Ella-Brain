# Verification

Two browser passes. They are not the same run.

## Pass A — head `ac7b9b2` only

Dev server `http://127.0.0.1:5173/` from that commit, before the gate adapter. Headless Chromium 156.0.8078.4, viewport 1280×800. The reducer was imported in the page from `/src/lib/ella/machine.ts`.

| Check | Result |
|---|---|
| Other-session reply, same epoch | phase stayed `thinking`, tools 0, proposal null, dropped turn |
| Reviewer to guest while pending | phase `listening`, proposal null, memories 0 |
| Stop, then late accept and `بله` | phase `idle`, memories 0, notes "No write" and "Delayed utterance ignored" |
| Audio unavailable, then typed `سلام` | phase returned to `thinking`; speech-failure note kept the text path |
| UI: Start with mic denied, Stop, send `بله` | denial note visible, delayed-utterance note visible, no horizontal overflow |

This pass is not evidence for later commits.

## Pass B — gate adapter

`ELLA_BRAIN_PIN_ROOT=/tmp/ella-brain-pin` is checkout `d01d1f15f0048d3a5874b59fb6c0759e508c6539`.

```bash
ELLA_BRAIN_PIN_ROOT=/tmp/ella-brain-pin python3 -m pytest tests/test_channel_backend.py -q
```

Exit 0. 5 passed in 1.62s.

- Guest with `principal: local_reviewer` is rejected and writes no task file.
- Operator roundtrip reads back version 1. The same request id does not add a version.
- Invalid dependency returns no version for the rejected task. The pending dependency stays at version 1.
- Cancel while the handler is held writes nothing.
- A second process on the same directory rejects the old token and still reads version 1.
- Starting the server on this branch's own `ella_brain` (not the pin) exits with `pin mismatch`.

Frontend, in `apps/ella-voice-preview`, Node v22.23.3:

```bash
npm test
npm run typecheck
npm run build
```

`npm test` exit 0, 16 passed. `npm run typecheck` exit 0. `npm run build` exit 0 (`dist/assets/index-CmdLtXPk.js`, 253.62 kB). `dist/` is not committed.

Browser pass B used that build via `vite preview` at `http://127.0.0.1:4173/` with the adapter on `127.0.0.1:8765` and store `/tmp/ella-demo-store`. Headless Chromium, microphone denied. No page errors.

| Run | Viewport | Access | Typed | Seen |
|---|---|---|---|---|
| operator | 1280×800 | operator | `کار مصنوعی را ثبت کن` | `خوانده شد` |
| invalid | 1280×800 | operator | `وابستگی نامعتبر را امتحان کن` | `نسخهٔ تازه‌ای نوشته نشد` |
| guest | 1280×800 | guest | `کار مصنوعی را ثبت کن` | `مهمان اجازه` |
| mobile | 390×844 | operator | `کار مصنوعی را ثبت کن` | `خوانده شد`, no horizontal overflow |

Ella-Brain's existing suite was not re-run. `_io.py` and `_stages.py` in this branch are untouched.
