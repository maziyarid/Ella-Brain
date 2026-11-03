import assert from "node:assert/strict";
import test from "node:test";
import { planTurn } from "../src/lib/ella/fixtures.ts";
import {
  emptyChannel,
  reduce,
  type ChannelState,
  type Proposal,
} from "../src/lib/ella/machine.ts";
import { afterSpokenAudioFailure, noteAfterMicrophone } from "../src/lib/ella/speech-boundary.ts";

const NOW = "2026-11-03T15:00:00.000Z";
const LATER = "2026-11-03T15:01:00.000Z";

function start(principal: "guest" | "local_reviewer", memories: ChannelState["memories"] = []): ChannelState {
  return reduce(
    { ...emptyChannel(memories), principal },
    { type: "start", now: NOW, sessionId: "sess-1" },
  );
}

function reply(state: ChannelState, text: string, id: string) {
  const next = reduce(state, { type: "final_utterance", id, text, now: LATER });
  assert.equal(next.phase, "thinking");
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
  return { plan, spoken };
}

function listen(state: ChannelState): ChannelState {
  return reduce(state, { type: "speak_done", epoch: state.epoch, sessionId: state.sessionId ?? "" });
}

test("guest receives no reviewer context and no memory-write capability", () => {
  const context = reply(start("guest"), "وضعیت مخزن Ella-Brain چیست؟", "g-ctx");
  assert.equal(context.plan.tool, null);
  assert.equal(context.plan.proposal, null);
  assert.equal(context.spoken.tools.length, 0);
  assert.match(context.plan.reply, /مهمان|بسته/);

  const memory = reply(start("guest"), "یادت باشد که جواب کوتاه می‌خواهم", "g-mem");
  assert.equal(memory.plan.proposal, null);
  assert.equal(memory.spoken.proposal, null);
  assert.equal(memory.spoken.memories.length, 0);

  const reviewerCard = reply(start("local_reviewer"), "یادت باشد که جواب کوتاه می‌خواهم", "r-mem");
  const asGuest = reduce(listen(reviewerCard.spoken), { type: "set_principal", principal: "guest" });
  const yes = reduce(asGuest, { type: "final_utterance", id: "g-yes", text: "بله", now: LATER });
  assert.equal(yes.memories.length, 0);
  assert.equal(yes.proposal?.id, reviewerCard.spoken.proposal?.id);
  assert.match(yes.note ?? "", /Guest cannot accept/);
});

test("a memory card stays a proposal until that exact card is accepted", () => {
  const proposed = reply(start("local_reviewer"), "یادت باشد که جواب کوتاه می‌خواهم", "u1");
  const card = proposed.spoken.proposal;
  assert.ok(card);
  assert.equal(proposed.spoken.memories.length, 0);
  assert.match(proposed.plan.reply, /پیشنهاد/);

  const wrong = reduce(proposed.spoken, {
    type: "accept_proposal",
    proposalId: "not-this-card",
    now: LATER,
  });
  assert.equal(wrong.memories.length, 0);
  assert.equal(wrong.proposal?.id, card?.id);
  assert.match(wrong.note ?? "", /not the one on screen/);
});

test("exact بله accepts only the pending card and read-back matches it", () => {
  const proposed = reply(start("local_reviewer"), "یادت باشد که جواب کوتاه می‌خواهم", "u1");
  const card = proposed.spoken.proposal as Proposal;
  const accepted = reduce(listen(proposed.spoken), {
    type: "final_utterance",
    id: "yes",
    text: "بله",
    now: LATER,
  });
  assert.equal(accepted.proposal, null);
  assert.equal(accepted.memories.length, 1);
  assert.equal(accepted.memories[0].id, card.id);
  assert.equal(accepted.memories[0].text, card.text);
  assert.equal(accepted.memories[0].readBack, card.text);
  assert.equal(accepted.memories[0].scope, "preview_browser");
  const readback = accepted.transcript.find((turn) => turn.disposition === "readback");
  assert.ok(readback);
  assert.match(readback.text, new RegExp(card.text));
});

test("بله، و به علی هم زنگ بزن does not approve, write, or dial", () => {
  const proposed = reply(start("local_reviewer"), "یادت باشد که جواب کوتاه می‌خواهم", "u1");
  const waiting = listen(proposed.spoken);
  const expanded = reduce(waiting, {
    type: "final_utterance",
    id: "exp",
    text: "بله، و به علی هم زنگ بزن",
    now: LATER,
  });
  assert.equal(expanded.phase, "listening");
  assert.equal(expanded.memories.length, 0);
  assert.equal(expanded.proposal?.id, waiting.proposal?.id);
  assert.equal(expanded.tools.length, 0);
  assert.match(expanded.note ?? "", /Ambiguous approval/);
  assert.equal("dial" in expanded, false);
});

test("rejected and cancelled utterances do not write memory", () => {
  const proposed = reply(start("local_reviewer"), "یادت باشد که قرار شد کوتاه جواب بدهی", "u1");
  const card = proposed.spoken.proposal as Proposal;
  const rejected = reduce(proposed.spoken, { type: "reject_proposal", proposalId: card.id });
  assert.equal(rejected.proposal, null);
  assert.equal(rejected.memories.length, 0);
  assert.match(rejected.note ?? "", /No memory write/);

  const cancelled = reduce(start("local_reviewer"), {
    type: "cancel_utterance",
    id: "c1",
    text: "یادت باشد که این لغو شود",
  });
  assert.equal(cancelled.memories.length, 0);
  assert.equal(cancelled.proposal, null);
  assert.equal(cancelled.transcript[0]?.disposition, "cancelled");
});

test("resume keeps accepted preview memories and drops the rest of the session", () => {
  const proposed = reply(start("local_reviewer"), "یادت باشد که جواب کوتاه می‌خواهم", "u1");
  const accepted = reduce(listen(proposed.spoken), {
    type: "accept_proposal",
    proposalId: (proposed.spoken.proposal as Proposal).id,
    now: LATER,
  });
  const resumed = reduce(accepted, { type: "resume", now: LATER, sessionId: "sess-2" });
  assert.equal(resumed.phase, "listening");
  assert.equal(resumed.memories.length, 1);
  assert.equal(resumed.memories[0].text, accepted.memories[0].text);
  assert.equal(resumed.transcript.length, 0);
  assert.equal(resumed.tools.length, 0);
  assert.equal(resumed.proposal, null);
  assert.match(resumed.note ?? "", /1 accepted preview memory/);
});

test("repeated public-context requests and reconnect do not execute the mock tool twice", () => {
  const first = reply(start("local_reviewer"), "وضعیت مخزن Ella-Brain چیست؟", "c1");
  assert.equal(first.spoken.tools.length, 1);
  assert.equal(first.spoken.tools[0].duplicate, false);
  assert.equal(first.spoken.tools[0].name, "retrieve_public_context");

  const second = reply(listen(first.spoken), "دوباره وضعیت پروژه را بگو", "c2");
  assert.equal(second.spoken.tools.length, 2);
  assert.equal(second.spoken.tools[1].duplicate, true);
  assert.equal(second.spoken.tools[1].summary, first.spoken.tools[0].summary);
  assert.equal(second.spoken.tools[1].key, first.spoken.tools[0].key);

  const reconnected = reduce(reduce(second.spoken, { type: "reconnect" }), { type: "reconnect_settled" });
  assert.equal(reconnected.tools.length, 2);
  assert.deepEqual(
    reconnected.tools.map((item) => item.duplicate),
    [false, true],
  );
  assert.match(reconnected.note ?? "", /No duplicate tool execution/);
});

test("microphone denial leaves typed interaction usable", () => {
  const listening = start("local_reviewer");
  const note = noteAfterMicrophone(false);
  assert.match(note, /Type the utterance/);
  assert.equal(listening.phase, "listening");
  const typed = reduce(listening, {
    type: "final_utterance",
    id: "typed",
    text: "سلام",
    now: LATER,
  });
  assert.equal(typed.phase, "thinking");
});

test("speech failure does not freeze the interface", () => {
  const proposed = reply(start("local_reviewer"), "سلام", "u1");
  assert.equal(proposed.spoken.phase, "speaking");
  const failed = afterSpokenAudioFailure(proposed.spoken, proposed.spoken.epoch);
  assert.equal(failed.phase, "listening");
  assert.match(failed.note ?? "", /text reply stands/);
  const typed = reduce(failed, {
    type: "final_utterance",
    id: "after",
    text: "یادت باشد که هنوز می‌نویسم",
    now: LATER,
  });
  assert.equal(typed.phase, "thinking");
});

test("stop, interrupt, end, and kill cancel the pending activity", () => {
  const thinking = reduce(start("local_reviewer"), {
    type: "final_utterance",
    id: "u1",
    text: "سلام",
    now: LATER,
  });
  assert.equal(thinking.phase, "thinking");
  const epoch = thinking.epoch;

  const stopped = reduce(thinking, { type: "stop" });
  assert.equal(stopped.phase, "idle");
  assert.equal(stopped.partial, "");
  const staleAfterStop = reduce(stopped, {
    type: "reply_ready",
    epoch,
    sessionId: thinking.sessionId ?? "",
    utteranceId: "u1",
    reply: "باید حذف شود",
    proposal: null,
    tool: null,
  });
  assert.equal(staleAfterStop.phase, "idle");
  assert.match(staleAfterStop.note ?? "", /Stale reply dropped/);

  const speaking = reply(start("local_reviewer"), "سلام دوباره", "u2").spoken;
  const interrupted = reduce(speaking, { type: "interrupt" });
  assert.equal(interrupted.phase, "listening");
  const staleAfterInterrupt = reduce(interrupted, {
    type: "speak_done",
    epoch: speaking.epoch,
    sessionId: speaking.sessionId ?? "",
  });
  assert.equal(staleAfterInterrupt.phase, "listening");

  const proposed = reply(start("local_reviewer"), "یادت باشد که این باید بماند", "u3");
  const ended = reduce(proposed.spoken, { type: "end" });
  assert.equal(ended.phase, "ended");
  assert.equal(ended.proposal, null);
  assert.equal(ended.memories.length, 0);

  const killed = reduce(proposed.spoken, { type: "kill" });
  assert.equal(killed.phase, "unavailable");
  assert.equal(killed.proposal, null);
  const duringKill = reduce(killed, {
    type: "reply_ready",
    epoch: killed.epoch,
    sessionId: killed.sessionId ?? "",
    utteranceId: "u3",
    reply: "نباید اجرا شود",
    proposal: null,
    tool: { key: "public-context:sess-1", name: "retrieve_public_context", summary: "no" },
  });
  assert.equal(duringKill.phase, "unavailable");
  assert.equal(duringKill.tools.length, 0);
  assert.match(duringKill.note ?? "", /No tool ran/);
});

test("an old-session reply arriving during a new-session turn does not commit", () => {
  const old = reduce(start("local_reviewer"), {
    type: "final_utterance",
    id: "old",
    text: "سلام",
    now: NOW,
  });
  assert.equal(old.phase, "thinking");
  const restarted = reduce(old, { type: "start", now: LATER, sessionId: "sess-2" });
  const neu = reduce(restarted, {
    type: "final_utterance",
    id: "new",
    text: "وضعیت مخزن Ella-Brain چیست؟",
    now: LATER,
  });
  assert.equal(neu.sessionId, "sess-2");
  assert.equal(neu.phase, "thinking");
  const leaked = reduce(neu, {
    type: "reply_ready",
    epoch: old.epoch,
    sessionId: "sess-1",
    utteranceId: "old",
    reply: "از جلسهٔ قبلی",
    proposal: {
      id: "mem-old",
      memoryClass: "fact",
      text: "نباید بنشیند",
      utteranceId: "old",
      action: "memory.write",
      resource: "preview_browser_memory",
    },
    tool: { key: "public-context:sess-1", name: "retrieve_public_context", summary: "old" },
  });
  assert.equal(leaked.phase, "thinking");
  assert.equal(leaked.sessionId, "sess-2");
  assert.equal(leaked.tools.length, 0);
  assert.equal(leaked.proposal, null);
  assert.equal(leaked.memories.length, 0);
  assert.equal(leaked.transcript.some((turn) => turn.role === "ella"), false);
  assert.equal(leaked.transcript.some((turn) => turn.disposition === "dropped"), true);

  const sameEpochWrongSession = reduce(
    { ...neu, epoch: old.epoch },
    {
      type: "reply_ready",
      epoch: old.epoch,
      sessionId: "sess-1",
      utteranceId: "old",
      reply: "نباید با شمارهٔ دورهٔ برابر بنشیند",
      proposal: null,
      tool: { key: "public-context:sess-1", name: "retrieve_public_context", summary: "old" },
    },
  );
  assert.equal(sameEpochWrongSession.tools.length, 0);
  assert.equal(sameEpochWrongSession.phase, "thinking");
});

test("reviewer to guest while a reply is pending drops that work", () => {
  const thinking = reduce(start("local_reviewer"), {
    type: "final_utterance",
    id: "pend",
    text: "یادت باشد که جواب کوتاه می‌خواهم",
    now: LATER,
  });
  assert.equal(thinking.phase, "thinking");
  assert.equal(thinking.turnPrincipal, "local_reviewer");
  const guest = reduce(thinking, { type: "set_principal", principal: "guest" });
  const dropped = reduce(guest, {
    type: "reply_ready",
    epoch: guest.epoch,
    sessionId: guest.sessionId ?? "",
    utteranceId: "pend",
    reply: "نباید برای مهمان ذخیره شود",
    proposal: {
      id: "mem-pend",
      memoryClass: "preference",
      text: "جواب کوتاه می‌خواهم",
      utteranceId: "pend",
      action: "memory.write",
      resource: "preview_browser_memory",
    },
    tool: { key: "public-context:sess-1", name: "retrieve_public_context", summary: "hidden" },
  });
  assert.equal(dropped.principal, "guest");
  assert.equal(dropped.phase, "listening");
  assert.equal(dropped.proposal, null);
  assert.equal(dropped.tools.length, 0);
  assert.equal(dropped.memories.length, 0);
  assert.equal(dropped.transcript.some((turn) => turn.role === "ella"), false);
  assert.match(dropped.note ?? "", /Principal changed/);
  const typed = reduce(dropped, {
    type: "final_utterance",
    id: "after",
    text: "سلام",
    now: LATER,
  });
  assert.equal(typed.phase, "thinking");
  assert.equal(typed.turnPrincipal, "guest");
});

test("stop ignores a delayed utterance and a delayed card acceptance", () => {
  const proposed = reply(start("local_reviewer"), "یادت باشد که جواب کوتاه می‌خواهم", "u1");
  const card = proposed.spoken.proposal as Proposal;
  const stopped = reduce(proposed.spoken, { type: "stop" });
  assert.equal(stopped.phase, "idle");
  assert.equal(stopped.proposal, null);
  const lateAccept = reduce(stopped, {
    type: "accept_proposal",
    proposalId: card.id,
    now: LATER,
  });
  assert.equal(lateAccept.memories.length, 0);
  assert.match(lateAccept.note ?? "", /No write/);
  const lateUtterance = reduce(stopped, {
    type: "final_utterance",
    id: "late",
    text: "بله",
    now: LATER,
  });
  assert.equal(lateUtterance.phase, "idle");
  assert.equal(lateUtterance.memories.length, 0);
  assert.match(lateUtterance.note ?? "", /Delayed utterance ignored/);
});

test("audio unavailable still accepts a later typed utterance", () => {
  const listening = start("local_reviewer");
  const down = reduce(listening, { type: "provider_unavailable" });
  assert.equal(down.phase, "listening");
  assert.match(down.note ?? "", /Typed input still works/);
  const typed = reduce(down, {
    type: "final_utterance",
    id: "typed",
    text: "سلام",
    now: LATER,
  });
  assert.equal(typed.phase, "thinking");
  assert.equal(typed.turnPrincipal, "local_reviewer");
  const planned = planTurn(typed, "typed", "سلام");
  const spoken = reduce(typed, {
    type: "reply_ready",
    epoch: typed.epoch,
    sessionId: typed.sessionId ?? "",
    utteranceId: "typed",
    reply: planned.reply,
    proposal: planned.proposal,
    tool: planned.tool,
  });
  assert.equal(spoken.phase, "speaking");
  assert.equal(spoken.transcript.some((turn) => turn.role === "ella"), true);
});

