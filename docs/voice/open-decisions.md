# Open decisions

None of these are resolved by the prototype. Snippets and conflicting prices are not accepted facts. No provider is selected.

## Approved Qalam source

Unresolved. No approved profile path or version was found in Ella-Brain at `cea47fabecd1eb3ac4d5c2427afa2d09e2f98868`. This branch does not invent one and does not apply Qalam to the pack or the UI copy.

## Speech provider and Persian quality

Unresolved. No realtime session was opened. Persian recognition, pronunciation, and naturalness are unscored. Device Web Speech and `speechSynthesis` are a local fallback only.

Public xAI voice pages have been reported, in earlier notes, to disagree on speech-to-speech price. Those figures are not re-certified here and are not a recommendation.

## Pricing and retention

Unresolved. No account was priced, and no retention term was accepted. Audio in this prototype is not uploaded.

## Browser identity and authentication

Unresolved. The reviewer control is a local flag. Production needs a separate decision for who the principal is, how they authenticate, and which actions that authentication allows. Those are three different decisions.

## Durable memory ownership

Unresolved. Preview records live in `localStorage` under `ella-channel-preview-v0` until deleted. They are not Task documents and not the four-component memory system. A durable store needs an explicit owner and must not widen the closed Task schema.

## Telephone destination coverage

No route is implemented. Nothing was dialed, and no Ella account was queried.

Read on 2026-11-03:

| Source | Product | What it actually says | What it does not say |
|---|---|---|---|
| [Twilio error 21408](https://www.twilio.com/docs/api/errors/21408) | Messaging error page | "Twilio stopped delivering voice, messaging, and email traffic to recipients in Iran on March 15, 2025, and to recipients in Syria and Cuba on September 15, 2025." Geo permissions do not restore that traffic. WhatsApp/RCS numbers beginning with `+98` are included in the blocked examples. | It is not a Programmable Voice geo-permissions page, and it is not an account-specific eligibility result. |
| [Twilio error 32203](https://www.twilio.com/docs/api/errors/32203) | Elastic SIP Trunking / Voice | A general pre-destination block: fraud risk, regulatory restriction, or a missing Primary Customer Profile for `+1`. Page content observed with a 2026-06-08 publication marker in search metadata. | The page does not name Iran. |
| Help Center article `55718438161947` | Programmable Voice, as described by a search snippet | A search result quoted a Help Center article saying outbound calls to `+98` fail with 32203 and cannot be overridden. | A direct fetch of that article on 2026-11-03 did not return the body. The snippet is a lead, not the source of record. |
| [Voice dialing permissions](https://www.twilio.com/docs/voice/api/dialing-permissions-resources) | Programmable Voice API | Account geo permissions exist and distinguish low-risk and high-risk prefixes. | No Iran row was retrieved, and no Ella account permissions were read. |

Do not treat "Iran calling is unsupported" as an account decision. The verified service document is the 21408 statement above. Inbound coverage, other carriers, and consent to place any call remain open.

## Consent, recording, cost, and outbound-call policy

Unresolved. Recording in this prototype is off. There is no consent copy, no spend limit, and no outbound policy, because there is no call.
