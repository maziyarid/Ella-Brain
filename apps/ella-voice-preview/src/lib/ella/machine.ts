/** Browser-channel session. Not Ella-Brain task state. No provider calls. */

export const SESSION_TTL_MS = 30 * 60 * 1000;

export type Phase =
  | "idle"
  | "listening"
  | "thinking"
  | "speaking"
  | "reconnecting"
  | "unavailable"
  | "ended";

export type Principal = "guest" | "local_reviewer";

export type MemoryClass =
  | "fact"
  | "preference"
  | "decision"
  | "hypothesis"
  | "unresolved";

export interface TranscriptTurn {
  id: string;
  role: "user" | "ella" | "system";
  text: string;
  disposition: "final" | "cancelled" | "dropped" | "readback";
}

export interface Proposal {
  id: string;
  memoryClass: MemoryClass;
  text: string;
  utteranceId: string;
  action: "memory.write";
  resource: "preview_browser_memory";
}

export interface MemoryRecord {
  id: string;
  memoryClass: MemoryClass;
  text: string;
  sessionId: string;
  utteranceId: string;
  acceptedAt: string;
  scope: "preview_browser";
  confidence: "user_confirmed";
  readBack: string;
}

export interface ToolReceipt {
  key: string;
  name: "retrieve_public_context";
  duplicate: boolean;
  summary: string;
}

export interface ChannelState {
  phase: Phase;
  phaseBeforeReconnect: Phase | null;
  principal: Principal;
  sessionId: string | null;
  startedAt: string | null;
  epoch: number;
  muted: boolean;
  partial: string;
  transcript: TranscriptTurn[];
  proposal: Proposal | null;
  memories: MemoryRecord[];
  tools: ToolReceipt[];
  note: string | null;
}

export const emptyChannel = (memories: MemoryRecord[] = []): ChannelState => ({
  phase: "idle",
  phaseBeforeReconnect: null,
  principal: "guest",
  sessionId: null,
  startedAt: null,
  epoch: 0,
  muted: false,
  partial: "",
  transcript: [],
  proposal: null,
  memories,
  tools: [],
  note: null,
});

export type ChannelEvent =
  | { type: "set_principal"; principal: Principal }
  | { type: "start"; now: string; sessionId: string }
  | { type: "stop" }
  | { type: "mute"; muted: boolean }
  | { type: "partial"; text: string }
  | { type: "final_utterance"; id: string; text: string; now: string }
  | { type: "cancel_utterance"; id: string; text: string }
  | { type: "interrupt" }
  | {
      type: "reply_ready";
      epoch: number;
      utteranceId: string;
      reply: string;
      proposal: Proposal | null;
      tool: Omit<ToolReceipt, "duplicate"> | null;
    }
  | { type: "speak_done"; epoch: number }
  | { type: "provider_unavailable" }
  | { type: "reconnect" }
  | { type: "reconnect_settled" }
  | { type: "kill" }
  | { type: "end" }
  | { type: "resume"; now: string; sessionId: string }
  | { type: "accept_proposal"; proposalId: string; now: string }
  | { type: "reject_proposal"; proposalId: string }
  | { type: "expire"; now: string };

const APPROVAL = new Set(["بله", "آره", "yes"]);
const STOP = new Set(["بس", "stop", "cancel", "قطع"]);

export function normalizeUtterance(text: string): string {
  return text.replace(/\s+/g, " ").trim();
}

function expired(state: ChannelState, now: string): boolean {
  if (!state.startedAt || !state.sessionId) return false;
  return Date.parse(now) - Date.parse(state.startedAt) > SESSION_TTL_MS;
}

function withExpiry(state: ChannelState, now: string | undefined): ChannelState {
  if (!now || !expired(state, now)) return state;
  return {
    ...state,
    phase: "ended",
    partial: "",
    proposal: null,
    note: "Session expired. Accepted memories stay. Nothing new was written.",
  };
}

function push(
  state: ChannelState,
  turn: TranscriptTurn,
): ChannelState {
  return { ...state, transcript: [...state.transcript, turn] };
}

export function reduce(state: ChannelState, event: ChannelEvent): ChannelState {
  const now = "now" in event ? event.now : undefined;
  const base = event.type === "expire" ? state : withExpiry(state, now);
  if (
    base.phase === "ended" &&
    event.type !== "resume" &&
    event.type !== "start" &&
    event.type !== "set_principal"
  ) {
    return base;
  }
  if (
    base.phase === "unavailable" &&
    event.type !== "resume" &&
    event.type !== "start" &&
    event.type !== "end" &&
    event.type !== "set_principal"
  ) {
    return { ...base, note: "Unavailable. No tool ran." };
  }

  switch (event.type) {
    case "set_principal":
      return {
        ...base,
        principal: event.principal,
        note:
          event.principal === "local_reviewer"
            ? "Local reviewer flag only. This is not authentication of Maziyar."
            : "Guest. No project context and no memory writes.",
      };
    case "kill":
      return {
        ...base,
        phase: "unavailable",
        partial: "",
        proposal: null,
        epoch: base.epoch + 1,
        note: "Kill switch. Speech and tools are stopped.",
      };
    case "provider_unavailable":
      return {
        ...base,
        phase: "unavailable",
        partial: "",
        epoch: base.epoch + 1,
        note: "Audio path unavailable. Type instead, or end the session. No call was placed.",
      };
    case "expire":
      return withExpiry(base, event.now);
    case "end":
      return {
        ...base,
        phase: "ended",
        partial: "",
        proposal: null,
        epoch: base.epoch + 1,
        note: "Session ended. Accepted preview memories remain until you delete them.",
      };
    case "start":
      return {
        ...base,
        phase: "listening",
        principal: base.principal,
        sessionId: event.sessionId,
        startedAt: event.now,
        epoch: base.epoch + 1,
        partial: "",
        transcript: [],
        proposal: null,
        tools: [],
        note: "Listening. Cancelled or partial speech will not run a tool.",
      };
    case "resume":
      return {
        ...emptyChannel(base.memories),
        principal: base.principal,
        phase: "listening",
        sessionId: event.sessionId,
        startedAt: event.now,
        note: `Resumed with ${base.memories.length} accepted preview memory record(s). Prior transcripts were not promoted.`,
      };
    case "stop":
      return { ...base, phase: base.sessionId ? "idle" : "idle", partial: "", epoch: base.epoch + 1, note: "Stopped listening." };
    case "mute":
      return {
        ...base,
        muted: event.muted,
        partial: event.muted ? "" : base.partial,
        note: event.muted ? "Muted. Incoming audio will not be acted on." : "Unmuted.",
      };
    case "partial":
      if (base.muted || base.phase === "ended" || base.phase === "unavailable") return base;
      return { ...base, partial: event.text, phase: base.phase === "speaking" ? "speaking" : "listening" };
    case "interrupt":
      return {
        ...base,
        phase: "listening",
        epoch: base.epoch + 1,
        partial: "",
        note: "Interrupted. The in-flight reply will be dropped and will not run a tool.",
      };
    case "cancel_utterance":
      return push(
        {
          ...base,
          phase: base.sessionId ? "listening" : "idle",
          partial: "",
          epoch: base.epoch + 1,
          note: "Cancelled utterance. No tool. No memory proposal.",
        },
        { id: event.id, role: "user", text: event.text || "(cancelled)", disposition: "cancelled" },
      );
    case "final_utterance": {
      if (!base.sessionId || base.muted) {
        return { ...base, note: base.muted ? "Muted. Utterance ignored." : "Start a session first." };
      }
      const text = normalizeUtterance(event.text);
      if (!text) {
        return { ...base, partial: "", note: "Empty utterance ignored." };
      }
      const userTurn: TranscriptTurn = {
        id: event.id,
        role: "user",
        text,
        disposition: "final",
      };
      const token = text.toLowerCase();
      if (STOP.has(token) || text === "قطع کن") {
        return push(
          {
            ...base,
            phase: "idle",
            partial: "",
            proposal: null,
            epoch: base.epoch + 1,
            note: "Stop honored. No write.",
          },
          userTurn,
        );
      }
      if (APPROVAL.has(token)) {
        if (!base.proposal) {
          return push(
            { ...base, phase: "listening", partial: "", note: "No proposal is waiting. Yes did nothing." },
            userTurn,
          );
        }
        if (base.principal !== "local_reviewer") {
          return push(
            {
              ...base,
              phase: "listening",
              partial: "",
              note: "Guest cannot accept memory. The proposal is unchanged.",
            },
            userTurn,
          );
        }
        return reduce(push({ ...base, partial: "" }, userTurn), {
          type: "accept_proposal",
          proposalId: base.proposal.id,
          now: event.now,
        });
      }
      if (/^(بله|آره|yes)([\s،,.!؟?;:]|$)/i.test(text) && !APPROVAL.has(token)) {
        return push(
          {
            ...base,
            phase: "listening",
            partial: "",
            epoch: base.epoch + 1,
            note: "Ambiguous approval. The extra words were not authorized. Confirm the card or restate one action.",
          },
          userTurn,
        );
      }
      return push(
        {
          ...base,
          phase: "thinking",
          partial: "",
          epoch: base.epoch + 1,
          note: "Thinking. A stale reply from an older turn cannot commit.",
        },
        userTurn,
      );
    }
    case "reply_ready": {
      if (event.epoch !== base.epoch || base.phase !== "thinking") {
        return push(
          { ...base, note: "Stale reply dropped. No tool. No proposal." },
          {
            id: `drop-${event.utteranceId}`,
            role: "system",
            text: "Dropped stale reply.",
            disposition: "dropped",
          },
        );
      }
      let tools = base.tools;
      if (event.tool) {
        const seen = base.tools.some((item) => item.key === event.tool!.key);
        if (base.principal !== "local_reviewer") {
          tools = base.tools;
        } else {
          tools = [
            ...base.tools,
            {
              key: event.tool.key,
              name: event.tool.name,
              summary: seen ? base.tools.find((item) => item.key === event.tool!.key)!.summary : event.tool.summary,
              duplicate: seen,
            },
          ];
        }
      }
      const proposal = base.principal === "local_reviewer" ? event.proposal : null;
      return push(
        {
          ...base,
          phase: "speaking",
          tools,
          proposal: proposal ?? base.proposal,
          note: proposal ? "Proposal only. Nothing is stored until you accept this exact card." : "Speaking fixture text. Not a language score.",
        },
        { id: `ella-${event.utteranceId}`, role: "ella", text: event.reply, disposition: "final" },
      );
    }
    case "speak_done":
      if (event.epoch !== base.epoch || base.phase !== "speaking") return base;
      return { ...base, phase: "listening", note: "Listening." };
    case "reconnect":
      return {
        ...base,
        phaseBeforeReconnect: base.phase === "reconnecting" ? base.phaseBeforeReconnect : base.phase,
        phase: "reconnecting",
        note: "Reconnecting. Committed tools will not run again.",
      };
    case "reconnect_settled":
      return {
        ...base,
        phase: base.phaseBeforeReconnect === "thinking" || base.phaseBeforeReconnect === "speaking"
          ? "listening"
          : base.phaseBeforeReconnect ?? "listening",
        phaseBeforeReconnect: null,
        note: "Reconnected. No duplicate tool execution.",
      };
    case "accept_proposal": {
      if (!base.proposal || base.proposal.id !== event.proposalId) {
        return { ...base, note: "That proposal is not the one on screen. No write." };
      }
      if (base.principal !== "local_reviewer" || !base.sessionId) {
        return { ...base, note: "Memory write refused for this principal." };
      }
      const record: MemoryRecord = {
        id: base.proposal.id,
        memoryClass: base.proposal.memoryClass,
        text: base.proposal.text,
        sessionId: base.sessionId,
        utteranceId: base.proposal.utteranceId,
        acceptedAt: event.now,
        scope: "preview_browser",
        confidence: "user_confirmed",
        readBack: base.proposal.text,
      };
      return push(
        {
          ...base,
          proposal: null,
          memories: [...base.memories, record],
          phase: base.phase === "ended" ? "ended" : "listening",
          note: "Read-back matches the accepted text. Preview store only.",
        },
        {
          id: `rb-${record.id}`,
          role: "system",
          text: `Read-back (${record.memoryClass}): ${record.readBack}`,
          disposition: "readback",
        },
      );
    }
    case "reject_proposal":
      if (!base.proposal || base.proposal.id !== event.proposalId) {
        return { ...base, note: "Nothing rejected. The card did not match." };
      }
      return {
        ...base,
        proposal: null,
        note: "Proposal rejected. No memory write.",
      };
    default:
      return base;
  }
}
