# Ella voice preview

Local browser prototype for a Persian conversation slice. It is not Ella-Brain, not authentication, and not a telephone.

## Run

```bash
cd apps/ella-voice-preview
npm ci
npm test
npm run typecheck
npm run build
npm run dev
```

Open the dev server and type Persian. Device speech is optional. If the microphone is denied, the text box still sends a final utterance.

The reviewer control is a demonstration flag. It does not identify anyone. Do not type private information. Accepted memories are written only to `localStorage` key `ella-channel-preview-v0` in this browser.

## What is real

- The session reducer in `src/lib/ella/machine.ts`.
- Fixture replies and the mocked public-context receipt in `src/lib/ella/fixtures.ts`.
- Preview memory cards. Accepting one does not call Ella-Brain.
- The two gate sentences, which call `get` and `mutate` on a disposable synthetic store when the local server is running.

## What is not real

- No provider session, no uploaded audio, no evaluated voice.
- No conversational memory in the task store.
- No call, no purchased number, no webhook.

See `docs/voice/` and `evals/persian/fa-IR-conversational-baseline-v0/`.
## Local gate

The two Persian gate sentences in `ella_channel/phrases.json` call a localhost adapter. Preview memory (`یادت باشد`) stays mocked.

Run the server from a checkout of this branch. It uses this tree's hardened `ella_brain` and checks both `_io.py` and `_stages.py`. No second checkout.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python -m ella_channel.server --store /tmp/ella-synthetic-store --port 8765
```

Start that server before `npm run dev`. Choose backend access, then Start. Operator is not the reviewer flag. The two sentences are `کار مصنوعی را ثبت کن` and `وابستگی نامعتبر را امتحان کن`.


