# Verification

Fresh checks against this branch's source. Earlier App Builder screenshots were taken in a different shell and are not evidence for this tree.

Runtime, recorded after `npm ci` in `apps/ella-voice-preview`:

| Tool | Version |
|---|---|
| Node.js | v22.23.3 |
| npm | 10.9.9 |
| react | 19.3.1 |
| vite | 8.3.5 |
| typescript | 5.9.3 |

Ella-Brain pytest was not run. `_io.py`, `_stages.py`, and `tests/test_lock_timeout.py` were not modified. `tests/test_atomic_write.py` was not added.

Lint is not configured in this package. No eslint result is claimed.

## Commands

Working directory: `apps/ella-voice-preview`.

```bash
npm ci --ignore-scripts
npm test
npm run typecheck
npm run build
```

`npm ci --ignore-scripts` exit 0. `added 87 packages`.

`npm test` exit 0. `node --experimental-strip-types --test tests/*.test.ts`. 11 tests, 11 pass, 0 fail. Duration about 213 ms. The tests cover guest denial, proposal-until-accept, exact proposal id, exact `بله`, expanded `بله، و به علی هم زنگ بزن`, reject and cancel, read-back, resume, duplicate mock tool plus reconnect, microphone-denial note, speech-failure return to listening, and stop / interrupt / end / kill.

`npm run typecheck` (`tsc --noEmit`) exit 0.

`npm run build` (`tsc --noEmit && vite build`) exit 0. Production client build:

```text
dist/index.html                   0.42 kB │ gzip:  0.28 kB
dist/assets/index-BzidWerq.css   12.01 kB │ gzip:  3.41 kB
dist/assets/index-E3T9PrnC.js   249.84 kB │ gzip: 78.63 kB
✓ built in 706ms
```

`dist/` is not committed.

## Browser

Command: headless Playwright Chromium (Chrome for Testing 156.0.8078.4) against `vite preview` at `http://127.0.0.1:4173/`, permissions empty.

| Viewport | Horizontal overflow | Banner | Microphone note | Typed `سلام` in transcript | Console errors |
|---|---|---|---|---|---|
| 1280×800 | scrollWidth 1280 = clientWidth | Demonstration only… reviewer switch is not authentication | Microphone permission denied. Type the utterance. No audio was stored. | yes | none |
| 390×844 | scrollWidth 390 = clientWidth | same | same | yes | none |

The Speaking label was not still visible 300 ms after send. Headless speech synthesis does not hold the speaking phase, which matches the reducer returning to listening when audio cannot be played. This is not a Persian speech-quality check. A granted physical microphone was not tested.

## No-overwrite, read only

`ella_brain/_io.py` at `cea47fabecd1eb3ac4d5c2427afa2d09e2f98868` (`atomic_write`):

1. `path.parent.mkdir(parents=True, exist_ok=True)`
2. If `path.exists()`, raise `VerificationError` and return.
3. `tempfile.mkstemp` in the same directory.
4. Write, flush, and `os.fsync` the temp file.
5. `os.replace(tmp_path, path)`.
6. `os.fsync` the directory.

The existence check refuses a destination that is already there. `os.replace` will replace a destination created after that check and before the replace. This is not an atomic no-overwrite publication. This branch does not change that function.

## Not tested

- Ella-Brain pytest and any lock-timeout behavior.
- A granted microphone, a real `fa-IR` voice, recognition accuracy, or naturalness.
- Provider sessions, telephony, webhooks, or a production deploy.
- Account-specific Twilio eligibility.
