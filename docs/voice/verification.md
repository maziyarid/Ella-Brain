# Verification

Two checks are recorded. They are not the same tree.

## This commit

Fresh check after the race-case fix. Parent of the branch before this commit was `dc5a4f9ed00bd46b1c5682aec1a9c85da6847cf0`. Main was still `cea47fabecd1eb3ac4d5c2427afa2d09e2f98868`.

| Tool | Version |
|---|---|
| Node.js | v22.23.3 |
| npm | 10.9.9 |

Working directory: `apps/ella-voice-preview`. Dependencies were already installed with `npm ci --ignore-scripts` (exit 0, `added 87 packages`).

```bash
npm test
npm run typecheck
npm run build
```

`npm test` exit 0. `node --experimental-strip-types --test tests/*.test.ts`. 15 tests, 15 pass, 0 fail. Duration about 219 ms. The four new cases are:

1. An old-session reply, including one with the same epoch and the other session id, does not commit during the new turn.
2. Switching reviewer to guest while a reply is pending drops that reply, proposal, and tool.
3. Stop drops the card. A delayed accept does not write. A delayed utterance stays idle.
4. `provider_unavailable` leaves the phase listening, and a later typed utterance can think and reply.

`npm run typecheck` (`tsc --noEmit`) exit 0.

`npm run build` (`tsc --noEmit && vite build`) exit 0:

```text
dist/index.html                   0.42 kB │ gzip:  0.28 kB
dist/assets/index-BajrcjqZ.css    9.34 kB │ gzip:  2.88 kB
dist/assets/index-BtY7hNgg.js   250.80 kB │ gzip: 78.87 kB
✓ built in 619ms
```

`dist/` is not committed. Lint is not configured. Ella-Brain pytest was not run. `_io.py`, `_stages.py`, and `tests/test_lock_timeout.py` were not modified. `tests/test_atomic_write.py` was not added.

Browser checks were not repeated for this commit. Do not treat the earlier headless pass as evidence for this SHA.

## Earlier commit dc5a4f9

Historical only. `npm test` then reported 11 pass. `tsc --noEmit` exit 0. `vite build` produced `index-BzidWerq.css` and `index-E3T9PrnC.js`. A headless Chromium pass at 1280×800 and 390×844 saw the demonstration banner, microphone denial, typed `سلام`, and no console errors. That was not a Persian speech-quality check.

## No-overwrite, read only

`ella_brain/_io.py` at main `cea47fabecd1eb3ac4d5c2427afa2d09e2f98868` (`atomic_write`):

1. `path.parent.mkdir(parents=True, exist_ok=True)`
2. If `path.exists()`, raise `VerificationError` and return.
3. `tempfile.mkstemp` in the same directory.
4. Write, flush, and `os.fsync` the temp file.
5. `os.replace(tmp_path, path)`.
6. `os.fsync` the directory.

The existence check refuses a destination that is already there. `os.replace` will replace a destination created after that check and before the replace. This is not an atomic no-overwrite publication. This branch does not change that function. The separate hardening branch is `hardening/combined-no-overwrite-lock-timeout` and is not included here.

## Not tested

- Ella-Brain pytest and any lock-timeout behavior.
- A granted microphone, a real `fa-IR` voice, recognition accuracy, or naturalness.
- Provider sessions, telephony, webhooks, or a production deploy.
- Account-specific Twilio eligibility.
- A browser pass of this commit.
