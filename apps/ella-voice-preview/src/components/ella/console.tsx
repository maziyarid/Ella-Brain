import { useEffect, useRef, useState } from "react";
import {
  Ear,
  Mic,
  MicOff,
  PhoneOff,
  RotateCcw,
  Shield,
  Square,
  Volume2,
  VolumeX,
} from "lucide-react";
import { EVAL_PACK } from "../../lib/ella/pack";
import { planTurn } from "../../lib/ella/fixtures";
import {
  emptyChannel,
  reduce,
  type ChannelState,
  type MemoryRecord,
  type Phase,
} from "../../lib/ella/machine";
import { afterSpokenAudioFailure, noteAfterMicrophone } from "../../lib/ella/speech-boundary";
import {
  cancelGateOp,
  gatePhrase,
  openGateSession,
  outcomeUnknown,
  postGateOp,
  type BackendAccess,
  type GateSession,
} from "../../lib/ella/gate-client";

const MEMORY_KEY = "ella-channel-preview-v0";

const PHASE_LABEL: Record<Phase, string> = {
  idle: "Idle",
  listening: "Listening",
  thinking: "Thinking",
  speaking: "Speaking",
  reconnecting: "Reconnecting",
  unavailable: "Unavailable",
  ended: "Ended",
};

function loadMemories(): MemoryRecord[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(MEMORY_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as { memories?: MemoryRecord[] };
    return Array.isArray(parsed.memories) ? parsed.memories : [];
  } catch {
    return [];
  }
}

function saveMemories(memories: MemoryRecord[]) {
  window.localStorage.setItem(MEMORY_KEY, JSON.stringify({ memories }));
}

interface SpeechRec {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  onresult: ((event: {
    resultIndex: number;
    results: ArrayLike<{ isFinal: boolean; 0: { transcript: string } }>;
  }) => void) | null;
  onerror: (() => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
  abort: () => void;
}

function getRecognition(): SpeechRec | null {
  const w = window as Window & {
    SpeechRecognition?: new () => SpeechRec;
    webkitSpeechRecognition?: new () => SpeechRec;
  };
  const Ctor = w.SpeechRecognition ?? w.webkitSpeechRecognition;
  if (!Ctor) return null;
  const rec = new Ctor();
  rec.lang = "fa-IR";
  rec.interimResults = true;
  rec.continuous = false;
  return rec;
}

export function EllaConsole() {
  const [state, setState] = useState<ChannelState>(() => emptyChannel());
  const [draft, setDraft] = useState("");
  const [speechNote, setSpeechNote] = useState("Device speech is optional. Typed Persian is the reliable path.");
  const [showPack, setShowPack] = useState(false);
  const [backendAccess, setBackendAccess] = useState<BackendAccess>("guest");
  const [gateNote, setGateNote] = useState("Backend access is separate from the reviewer flag. Start a session after choosing it.");
  const stateRef = useRef(state);
  const recRef = useRef<SpeechRec | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const gateRef = useRef<GateSession | null>(null);
  const inflightRef = useRef<{ session: GateSession; requestId: string } | null>(null);
  stateRef.current = state;

  useEffect(() => {
    setState(emptyChannel(loadMemories()));
  }, []);

  useEffect(() => {
    saveMemories(state.memories);
  }, [state.memories]);

  function apply(next: ChannelState) {
    stateRef.current = next;
    setState(next);
    return next;
  }

  function releaseMic() {
    recRef.current?.abort();
    recRef.current = null;
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
  }

  function speak(text: string, epoch: number, sessionId: string) {
    if (typeof window === "undefined" || !window.speechSynthesis) {
      apply(reduce(stateRef.current, { type: "speak_done", epoch, sessionId }));
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "fa-IR";
    const voice = window.speechSynthesis
      .getVoices()
      .find((item) => item.lang.toLowerCase().startsWith("fa"));
    if (voice) utterance.voice = voice;
    utterance.onend = () => {
      if (stateRef.current.epoch !== epoch || stateRef.current.sessionId !== sessionId) return;
      apply(reduce(stateRef.current, { type: "speak_done", epoch, sessionId }));
    };
    utterance.onerror = () => {
      if (stateRef.current.epoch !== epoch || stateRef.current.sessionId !== sessionId) return;
      apply(afterSpokenAudioFailure(stateRef.current, epoch));
    };
    window.speechSynthesis.speak(utterance);
  }

  function cancelInflight() {
    const flight = inflightRef.current;
    inflightRef.current = null;
    if (flight) void cancelGateOp(flight.session, flight.requestId);
  }

  function commitText(text: string) {
    const current = stateRef.current;
    const id = `u-${current.epoch + 1}-${Date.now()}`;
    const now = new Date().toISOString();
    const next = reduce(current, { type: "final_utterance", id, text, now });
    if (next.phase !== "thinking") {
      apply(next);
      return;
    }
    const phrase = gatePhrase(text);
    if (!phrase) {
      const plan = planTurn(next, id, text.trim());
      const spoken = reduce(next, {
        type: "reply_ready",
        epoch: next.epoch,
        sessionId: next.sessionId ?? "",
        utteranceId: id,
        reply: plan.reply,
        proposal: plan.proposal,
        tool: plan.tool,
      });
      apply(spoken);
      speak(plan.reply, spoken.epoch, spoken.sessionId ?? "");
      return;
    }
    const epoch = next.epoch;
    const sessionId = next.sessionId ?? "";
    apply(next);
    void finishGate(text, id, epoch, sessionId);
  }

  async function finishGate(text: string, requestId: string, epoch: number, sessionId: string) {
    const session = gateRef.current;
    const stale = () => stateRef.current.sessionId !== sessionId || stateRef.current.epoch !== epoch;
    if (!session) {
      if (stale()) return;
      const spoken = reduce(stateRef.current, {
        type: "reply_ready",
        epoch,
        sessionId,
        utteranceId: requestId,
        reply: "درگاه محلی باز نیست. چیزی نوشته نشد.",
        proposal: null,
        tool: null,
      });
      apply(spoken);
      speak(spoken.transcript.at(-1)?.text ?? "", spoken.epoch, sessionId);
      return;
    }
    inflightRef.current = { session, requestId };
    let result: { read_back: string };
    try {
      result = await postGateOp(session, requestId, text);
    } catch {
      result = outcomeUnknown();
    }
    if (inflightRef.current?.requestId === requestId) inflightRef.current = null;
    if (stale()) {
      void cancelGateOp(session, requestId);
      return;
    }
    const spoken = reduce(stateRef.current, {
      type: "reply_ready",
      epoch,
      sessionId,
      utteranceId: requestId,
      reply: result.read_back,
      proposal: null,
      tool: null,
    });
    apply(spoken);
    speak(result.read_back, spoken.epoch, sessionId);
  }

  async function begin() {
    releaseMic();
    cancelInflight();
    window.speechSynthesis?.cancel();
    const now = new Date().toISOString();
    const sessionId = crypto.randomUUID();
    apply(reduce(stateRef.current, { type: "start", now, sessionId }));
    try {
      gateRef.current = await openGateSession(backendAccess);
      setGateNote(
        backendAccess === "operator"
          ? "Operator grant is held by the local server for this browser session only. It is not the reviewer flag."
          : "Guest grant. The server will reject the synthetic gate even if the reviewer flag is on.",
      );
    } catch {
      gateRef.current = null;
      setGateNote("Local gate is not running. Typed fixture replies still work. Nothing was written.");
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      setSpeechNote(noteAfterMicrophone(true));
    } catch {
      setSpeechNote(noteAfterMicrophone(false));
    }
    const rec = getRecognition();
    if (!rec) {
      setSpeechNote((prev) => `${prev} This browser has no fa-IR speech recognizer.`);
      return;
    }
    recRef.current = rec;
    rec.onresult = (event) => {
      let interim = "";
      let finalText = "";
      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const piece = event.results[i][0].transcript;
        if (event.results[i].isFinal) finalText += piece;
        else interim += piece;
      }
      if (interim) apply(reduce(stateRef.current, { type: "partial", text: interim }));
      if (finalText) commitText(finalText);
    };
    rec.onerror = () => {
      setSpeechNote("Recognizer failed. Typed text still works. Nothing was sent to a provider.");
    };
    rec.onend = () => {
      if (stateRef.current.partial) {
        apply(
          reduce(stateRef.current, {
            type: "cancel_utterance",
            id: `c-${Date.now()}`,
            text: stateRef.current.partial,
          }),
        );
      }
    };
    try {
      rec.start();
    } catch {
      setSpeechNote("Could not start device recognition. Type instead.");
    }
  }

  function interrupt() {
    window.speechSynthesis?.cancel();
    recRef.current?.abort();
    cancelInflight();
    apply(reduce(stateRef.current, { type: "interrupt" }));
  }

  function stopAll() {
    window.speechSynthesis?.cancel();
    releaseMic();
    cancelInflight();
    apply(reduce(stateRef.current, { type: "stop" }));
  }

  function endSession() {
    window.speechSynthesis?.cancel();
    releaseMic();
    cancelInflight();
    apply(reduce(stateRef.current, { type: "end" }));
  }

  function resume() {
    releaseMic();
    const now = new Date().toISOString();
    apply(reduce(stateRef.current, { type: "resume", now, sessionId: crypto.randomUUID() }));
    void begin();
  }

  const phase = state.phase;

  return (
    <main className="mx-auto min-h-screen max-w-6xl px-4 py-6 text-ink md:px-8 md:py-10">
      <p className="mb-4 rounded-card border border-line bg-surface px-4 py-3 text-sm leading-relaxed">
        Demonstration only. The reviewer switch is not authentication and is not production authorization.
        Do not enter private information. Accepted preview memories stay in this browser only.
      </p>
      <header className="mb-6 flex flex-col gap-4 border-b border-line pb-6 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-medium text-muted">Ella · browser slice · not a telephone call</p>
          <h1 className="mt-1 text-3xl font-semibold tracking-tight md:text-4xl">Persian conversation, local only</h1>
          <p className="mt-2 max-w-2xl text-base leading-relaxed text-muted">
            Fixture replies, not a scored voice. Main is the hardened baseline. Qalam is unresolved, so nothing here is product copy.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="rounded-full bg-accent px-4 py-2 text-sm font-semibold text-accent-fg">{PHASE_LABEL[phase]}</span>
          <Ear className="text-accent" aria-hidden="true" />
        </div>
      </header>

      <section className="mb-6 grid gap-3 rounded-card border border-line bg-surface p-4 md:grid-cols-2">
        <label className="flex flex-col gap-2 text-sm">
          <span className="font-medium">Principal</span>
          <select
            className="min-h-11 rounded-xl border border-line bg-bg px-3 text-ink"
            value={state.principal}
            onChange={(event) =>
              apply(
                reduce(state, {
                  type: "set_principal",
                  principal: event.target.value === "local_reviewer" ? "local_reviewer" : "guest",
                }),
              )
            }
          >
            <option value="guest">Guest — no context, no memory</option>
            <option value="local_reviewer">Local reviewer flag — not Maziyar auth</option>
          </select>
        </label>
        <label className="flex flex-col gap-2 text-sm">
          <span className="font-medium">Backend access</span>
          <select
            id="backend-access"
            className="min-h-11 rounded-xl border border-line bg-bg px-3 text-ink"
            value={backendAccess}
            onChange={(event) => setBackendAccess(event.target.value === "operator" ? "operator" : "guest")}
          >
            <option value="guest">Guest — server rejects the gate</option>
            <option value="operator">Operator grant — not the reviewer flag</option>
          </select>
        </label>
        <p className="text-sm leading-relaxed text-muted md:col-span-2">{gateNote}</p>
      </section>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.4fr)_minmax(18rem,0.8fr)]">
        <section className="flex flex-col gap-4">
          <div className="flex flex-wrap gap-2">
            <button type="button" className="inline-flex min-h-11 items-center gap-2 rounded-full bg-accent px-4 text-sm font-semibold text-accent-fg" onClick={() => void begin()}>
              <Mic size={18} aria-hidden="true" /> Start
            </button>
            <button type="button" className="inline-flex min-h-11 items-center gap-2 rounded-full border border-line bg-surface px-4 text-sm font-medium" onClick={interrupt}>
              <Square size={18} aria-hidden="true" /> Interrupt
            </button>
            <button type="button" className="inline-flex min-h-11 items-center gap-2 rounded-full border border-line bg-surface px-4 text-sm font-medium" onClick={stopAll}>
              <MicOff size={18} aria-hidden="true" /> Stop
            </button>
            <button
              type="button"
              className="inline-flex min-h-11 items-center gap-2 rounded-full border border-line bg-surface px-4 text-sm font-medium"
              onClick={() => apply(reduce(state, { type: "mute", muted: !state.muted }))}
            >
              {state.muted ? <VolumeX size={18} aria-hidden="true" /> : <Volume2 size={18} aria-hidden="true" />}
              {state.muted ? "Unmute" : "Mute"}
            </button>
            <button type="button" className="inline-flex min-h-11 items-center gap-2 rounded-full border border-line bg-surface px-4 text-sm font-medium" onClick={endSession}>
              End
            </button>
            <button type="button" className="inline-flex min-h-11 items-center gap-2 rounded-full border border-line bg-surface px-4 text-sm font-medium" onClick={resume}>
              <RotateCcw size={18} aria-hidden="true" /> Resume
            </button>
            <button
              type="button"
              className="inline-flex min-h-11 items-center gap-2 rounded-full border border-line bg-surface px-4 text-sm font-medium"
              onClick={() => {
                window.speechSynthesis?.cancel();
                releaseMic();
                cancelInflight();
                apply(reduce(stateRef.current, { type: "kill" }));
              }}
            >
              <Shield size={18} aria-hidden="true" /> Kill switch
            </button>
          </div>

          <form
            className="flex flex-col gap-3 rounded-card border border-line bg-surface p-4"
            onSubmit={(event) => {
              event.preventDefault();
              const text = draft;
              setDraft("");
              if (stateRef.current.phase === "speaking") interrupt();
              commitText(text);
            }}
          >
            <label className="text-sm font-medium" htmlFor="utterance">
              Utterance
            </label>
            <textarea
              id="utterance"
              dir="auto"
              lang="fa"
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="مثلاً: یادت باشد که جواب کوتاه می‌خواهم"
              className="min-h-24 w-full resize-y rounded-xl border border-line bg-bg px-3 py-3 text-base leading-relaxed text-ink"
            />
            <div className="flex flex-wrap gap-2">
              <button type="submit" className="min-h-11 rounded-full bg-ink px-4 text-sm font-semibold text-bg">
                Send final utterance
              </button>
              <button
                type="button"
                className="min-h-11 rounded-full border border-line px-4 text-sm"
                onClick={() => {
                  apply(
                    reduce(stateRef.current, {
                      type: "cancel_utterance",
                      id: `c-${Date.now()}`,
                      text: draft,
                    }),
                  );
                  setDraft("");
                }}
              >
                Cancel draft
              </button>
              <button
                type="button"
                className="min-h-11 rounded-full border border-line px-4 text-sm"
                onClick={() => {
                  apply(reduce(stateRef.current, { type: "reconnect" }));
                  window.setTimeout(() => {
                    apply(reduce(stateRef.current, { type: "reconnect_settled" }));
                  }, 400);
                }}
              >
                Simulate reconnect
              </button>
            </div>
            <p className="text-sm text-muted">{speechNote}</p>
            {state.partial ? (
              <p className="text-sm text-muted" dir="auto">
                Partial, not actionable: {state.partial}
              </p>
            ) : null}
          </form>

          <ol className="flex flex-col gap-3">
            {state.transcript.length === 0 ? (
              <li className="rounded-card border border-dashed border-line bg-surface px-4 py-6 text-sm text-muted">
                No transcript yet. A transcript is not memory.
              </li>
            ) : (
              state.transcript.map((turn) => (
                <li key={turn.id} className="rounded-card border border-line bg-surface px-4 py-3" dir="auto">
                  <p className="text-xs font-medium uppercase tracking-wide text-muted">
                    {turn.role} · {turn.disposition}
                  </p>
                  <p className="mt-1 text-base leading-relaxed">{turn.text}</p>
                </li>
              ))
            )}
          </ol>
        </section>

        <aside className="flex flex-col gap-4">
          <section className="rounded-card border border-line bg-surface p-4">
            <h2 className="text-lg font-semibold">Pending proposal</h2>
            {state.proposal ? (
              <div className="mt-3 flex flex-col gap-3">
                <p className="text-sm text-muted">
                  {state.proposal.memoryClass} · {state.proposal.action} · {state.proposal.resource}
                </p>
                <p dir="auto" className="text-base leading-relaxed">
                  {state.proposal.text}
                </p>
                <div className="flex gap-2">
                  <button
                    type="button"
                    className="min-h-11 flex-1 rounded-full bg-accent text-sm font-semibold text-accent-fg"
                    onClick={() =>
                      apply(
                        reduce(state, {
                          type: "accept_proposal",
                          proposalId: state.proposal!.id,
                          now: new Date().toISOString(),
                        }),
                      )
                    }
                  >
                    Accept this card
                  </button>
                  <button
                    type="button"
                    className="min-h-11 flex-1 rounded-full border border-line text-sm"
                    onClick={() => apply(reduce(state, { type: "reject_proposal", proposalId: state.proposal!.id }))}
                  >
                    Reject
                  </button>
                </div>
              </div>
            ) : (
              <p className="mt-3 text-sm leading-relaxed text-muted">None. Say «یادت باشد» as the local reviewer to create one.</p>
            )}
          </section>

          <section className="rounded-card border border-line bg-surface p-4">
            <h2 className="text-lg font-semibold">Accepted read-back</h2>
            <ul className="mt-3 flex flex-col gap-3">
              {state.memories.length === 0 ? (
                <li className="text-sm text-muted">No accepted preview memory.</li>
              ) : (
                state.memories.map((memory) => (
                  <li key={memory.id} className="border-t border-line pt-3 text-sm leading-relaxed" dir="auto">
                    <span className="font-medium">{memory.memoryClass}</span> · {memory.readBack}
                  </li>
                ))
              )}
            </ul>
            <button
              type="button"
              className="mt-4 min-h-11 rounded-full border border-line px-4 text-sm"
              onClick={() => {
                saveMemories([]);
                apply({ ...stateRef.current, memories: [], note: "Preview memories deleted from this browser." });
              }}
            >
              Delete preview memories
            </button>
          </section>

          <section className="rounded-card border border-line bg-surface p-4">
            <h2 className="text-lg font-semibold">Tools this session</h2>
            <ul className="mt-3 flex flex-col gap-2 text-sm text-muted">
              {state.tools.length === 0 ? <li>None.</li> : null}
              {state.tools.map((tool, index) => (
                <li key={`${tool.key}-${index}`}>
                  {tool.name}: {tool.duplicate ? "duplicate suppressed" : "ran once"}
                </li>
              ))}
            </ul>
            <p className="mt-3 text-xs leading-relaxed text-muted">Session {state.sessionId ?? "none"}</p>
          </section>

          <section className="rounded-card border border-line bg-surface p-4">
            <h2 className="flex items-center gap-2 text-lg font-semibold">
              <PhoneOff size={18} aria-hidden="true" /> Telephony
            </h2>
            <p className="mt-2 text-sm leading-relaxed text-muted">
              Inbound and outbound calls are not implemented and none were placed. Twilio error 21408
              documentation, read on 2026-11-03, says Twilio stopped delivering voice, messaging, and email
              to Iran on 15 March 2025 and that geo permissions do not restore that traffic. That page is a
              messaging error document, not an Ella account check. No number is purchased here.
            </p>
          </section>
        </aside>
      </div>

      <section className="mt-8 rounded-card border border-line bg-surface p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-lg font-semibold">Persian baseline {EVAL_PACK.id}</h2>
          <button type="button" className="min-h-11 rounded-full border border-line px-4 text-sm" onClick={() => setShowPack((value) => !value)}>
            {showPack ? "Hide pack" : "Show pack"}
          </button>
        </div>
        <p className="mt-2 text-sm leading-relaxed text-muted">
          {EVAL_PACK.status}. Pass scores: none. {EVAL_PACK.evaluationNote} {EVAL_PACK.qalamResolution}
        </p>
        {showPack ? (
          <ul className="mt-4 flex flex-col gap-3">
            {EVAL_PACK.items.map((item) => (
              <li key={item.id} className="border-t border-line pt-3">
                <p className="text-xs font-medium text-muted">
                  {item.id} · {item.category} · audio {item.audio}
                </p>
                <p dir="rtl" lang="fa" className="mt-1 text-base leading-relaxed">
                  {item.stimulus}
                </p>
                <p className="text-sm text-muted">{item.meaningToPreserve}</p>
              </li>
            ))}
          </ul>
        ) : null}
      </section>
    </main>
  );
}
