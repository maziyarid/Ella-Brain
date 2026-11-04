# Local gate demonstration

A typed Persian sentence can cross the browser session, a localhost adapter, and `Ella.get` / `Ella.mutate`. The store is a disposable directory of synthetic tasks. This is not conversational memory, not a voice model, and not telephony.

## Hardened gate in this repository

The adapter imports this checkout's `ella_brain`. It refuses to start unless both files match main `9132753e4be980c75269be6de2658134e4960208`:

| File | Requirement | sha256 |
|---|---|---|
| `ella_brain/_io.py` | no-overwrite publication (`os.link`, existing destination refused) | `9787d2223cf4a69a9c7664eff3240d170e2b8992e33efc87b276d3216807c874` |
| `ella_brain/_stages.py` | bounded lock acquisition (5s non-blocking loop, no mutation on timeout) | `afc5ca45a8ee15d7b6aef7a19e2131800a910572ead847d6622ef069abb4133e` |

Those bytes are the same as reviewed commit `d01d1f15f0048d3a5874b59fb6c0759e508c6539`. The merge commit is not that SHA. Do not check out a second tree and do not set `PYTHONPATH` to one.

From a fresh clone of this branch:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python -m ella_channel.server --store /tmp/ella-synthetic-store --port 8765
```

The store directory is created empty. It is not a production root.

## Phrases

| Typed text | Effect |
|---|---|
| `کار مصنوعی را ثبت کن` | Create a synthetic pending `perceive` task owned by a synthetic agent, then read it back. |
| `وابستگی نامعتبر را امتحان کن` | Reject an `active` task whose dependency is still `pending`. That task gets no version file. |
| `یادت باشد …` | Still a mocked preview-memory proposal. It does not call the gate. |

Backend access is `guest` or `operator` on `POST /v1/sessions`. The reviewer dropdown is not sent as authority. A guest token is rejected even if the page claims to be a reviewer. Tokens live in the server process. Restarting the server keeps the version files and invalidates every token.

An operator session is granted only to a loopback client whose request carries no forwarding header (`X-Forwarded-For`, `X-Forwarded-Host`, `X-Real-IP`, `Forwarded`) and whose `Host` and any `Origin` name `127.0.0.1`, `localhost`, or `::1` (`is_local_request` in `ella_channel/server.py`). Other requests get 403 `operator_not_local`; guest sessions are unaffected. The Vite dev and preview servers bind to `127.0.0.1` by default. Residual limit: this is not authentication. Any process or browser page served from this machine's loopback can still obtain an operator session.

Each call carries `session_id` and `request_id`. Cancel before the mutate writes nothing. The same request id returns the first receipt and does not add a version.

If `/v1/ops` gets no usable reply (network error, proxy error, or a non-JSON body), the page says the outcome is unknown and asks you to check before retrying (`OUTCOME_UNKNOWN_READ_BACK` in `apps/ella-voice-preview/src/lib/ella/gate-client.ts`). "Nothing written" is shown only when the adapter itself replied with a rejection, or when no gate session exists so no request was sent.
