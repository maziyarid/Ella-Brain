# Local gate demonstration

A typed Persian sentence can cross the browser session, a localhost adapter, and `Ella.get` / `Ella.mutate`. The store is a disposable directory of synthetic tasks. This is not conversational memory, not a voice model, and not telephony.

## Pin

The adapter checks that the imported `ella_brain/_io.py` is the hardening commit `d01d1f15f0048d3a5874b59fb6c0759e508c6539` (sha256 `9787d2223cf4a69a9c7664eff3240d170e2b8992e33efc87b276d3216807c874`). Point `PYTHONPATH` at a checkout of that commit. This branch does not contain those `_io.py` or `_stages.py` edits.

## Phrases

| Typed text | Effect |
|---|---|
| `کار مصنوعی را ثبت کن` | Create a synthetic pending `perceive` task owned by a synthetic agent, then read it back. |
| `وابستگی نامعتبر را امتحان کن` | Reject an `active` task whose dependency is still `pending`. That task gets no version file. |
| `یادت باشد …` | Still a mocked preview-memory proposal. It does not call the gate. |

Backend access is `guest` or `operator` on `POST /v1/sessions`. The reviewer dropdown is not sent as authority. A guest token is rejected even if the page claims to be a reviewer. Tokens live in the server process. Restarting the server keeps the version files and invalidates every token.

Each call carries `session_id` and `request_id`. Cancel before the mutate writes nothing. The same request id returns the first receipt and does not add a version.
