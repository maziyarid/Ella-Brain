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
- The browser console in `src/components/ella/console.tsx`.

## What is not real

- No Ella-Brain `get` or `mutate`.
- No provider session, no uploaded audio, no evaluated voice.
- No call, no purchased number, no webhook.

See `docs/voice/` and `evals/persian/fa-IR-conversational-baseline-v0/`.
