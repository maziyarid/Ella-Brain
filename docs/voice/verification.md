# Verification

Three passes. They are not the same run. Pass A and Pass B are not evidence for this head.

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

This pass is not evidence for later commits.

## Pass C — in-tree hardened gate

Baseline is main `9132753e4be980c75269be6de2658134e4960208`. `PYTHONPATH` and `ELLA_BRAIN_PIN_ROOT` were unset. No second checkout.

A clean directory of this branch, new virtualenv:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python -m pytest -q
```

Exit 0. 61 passed in 4.01s. Zero failures, zero skipped.

| File | Passed |
|---|---|
| `tests/test_schema.py` | 12 |
| `tests/test_mutate.py` | 11 |
| `tests/test_domains.py` | 7 |
| `tests/test_pipeline.py` | 3 |
| `tests/test_concurrency.py` | 5 |
| `tests/test_atomic_write.py` | 7 |
| `tests/test_lock_timeout.py` | 9 |
| `tests/test_combined_hardening.py` | 1 |
| `tests/test_channel_backend.py` | 6 |

The 7 atomic-write tests and the combined test exercise no-overwrite publication in `_io.py`. The 9 lock tests exercise bounded acquisition in `_stages.py`. Imported paths were `ella_brain/_io.py` sha256 `9787d2223cf4a69a9c7664eff3240d170e2b8992e33efc87b276d3216807c874` and `ella_brain/_stages.py` sha256 `afc5ca45a8ee15d7b6aef7a19e2131800a910572ead847d6622ef069abb4133e`, both inside that directory.

Channel results in that suite:

- Guest with `principal: local_reviewer` is rejected and writes no task file.
- Operator roundtrip reads back version 1. The same request id does not add a version.
- Invalid dependency returns no version for the rejected task. The pending dependency stays at version 1.
- Cancel while the handler is held writes nothing.
- Restart keeps version 1 and rejects the old token.
- Tampering either `_io.py` or `_stages.py` on the import path exits with `pin mismatch`.

Documented server, empty store `/tmp/ella-synthetic-store`, port 8765:

```text
listening 127.0.0.1:8765 baseline 9132753e4be980c75269be6de2658134e4960208
```

Guest op: 403 `guest_denied`. Operator create: version 1, `pending`, read-back `خوانده شد`. Duplicate request: `duplicate: true`, still one `v1.json`. Invalid dependency: `version` null, read-back `نسخهٔ تازه‌ای نوشته نشد`, no version file. After process restart the old token is 401 and a new token still reads version 1.

Frontend, in `apps/ella-voice-preview`, Node v22.23.3:

```bash
npm test
npm run typecheck
npm run build
```

`npm test` exit 0, 16 passed. `npm run typecheck` exit 0. `npm run build` exit 0 (`dist/assets/index-CmdLtXPk.js`, 253.62 kB). `dist/` is not committed. Frontend source did not change in this pass.

Browser pass C used the dev server at `http://127.0.0.1:5173/`. Headless Chromium 156.0.8078.4. The reducer was imported in the page from `/src/lib/ella/machine.ts`. Microphone was not granted. No page errors.

| Check | Result |
|---|---|
| Other-session reply, same epoch | phase stayed `thinking`, session `sess-2`, tools 0, proposal null, memories 0, dropped turn |
| Reviewer to guest while pending | phase `listening`, proposal null, tools 0, memories 0, note "Principal changed" |
| Stop, then late accept and `بله` | phase `idle`, memories 0, notes "No write" and "Delayed utterance ignored" |
| Audio unavailable, then typed `سلام` | phase `thinking`; note "Typed input still works" |
| UI: Start, mic denied, Stop, send `بله` | denial note visible, phase Idle, typed `بله` not in the transcript, no horizontal overflow at 1280×800 or 390×844 |

The reducer note is not painted as its own DOM line. The UI check is the phase and the transcript, not a second copy of that sentence.

