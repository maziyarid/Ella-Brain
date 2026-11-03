import type { ChannelState, MemoryClass, Proposal, ToolReceipt } from "./machine.ts";

export const PUBLIC_CONTEXT =
  "Public GitHub main of maziyarid/Ella-Brain is still cea47fabecd1eb3ac4d5c2427afa2d09e2f98868. Writes go through get and mutate only. This browser does not read people files or private memory.";

const FIXTURE_NOTE = "نمونهٔ ثابت محلی است، نه ارزیابی زبان و نه نمایهٔ قلم.";

export interface TurnPlan {
  reply: string;
  proposal: Proposal | null;
  tool: Omit<ToolReceipt, "duplicate"> | null;
}

function classify(text: string): MemoryClass {
  if (/شاید|احتمالا|فکر می‌کنم|might|maybe/i.test(text)) return "hypothesis";
  if (/تصمیم|قرار شد|decision/i.test(text)) return "decision";
  if (/نمی‌دانم|نمیدانم|کدام|which|unresolved|\?/.test(text)) return "unresolved";
  if (/دوست دارم|ترجیح|می‌خواهم|می خواهم|می‌خوام|prefer/i.test(text)) return "preference";
  return "fact";
}

function wantsMemory(text: string): boolean {
  return /یادت (باشد|باشه|بمونه|بماند)|یادته|remember/i.test(text);
}

function wantsContext(text: string): boolean {
  return /مخزن|پروژه|ella-brain|وضعیت|context|repository/i.test(text);
}

export function planTurn(state: ChannelState, utteranceId: string, text: string): TurnPlan {
  const reviewer = state.principal === "local_reviewer";
  if (wantsContext(text)) {
    if (!reviewer) {
      return {
        reply: `زمینهٔ پروژه برای مهمان بسته است. ${FIXTURE_NOTE}`,
        proposal: null,
        tool: null,
      };
    }
    const key = `public-context:${state.sessionId}`;
    const already = state.tools.some((item) => item.key === key);
    return {
      reply: already
        ? `همان زمینهٔ عمومی جلسه را دوباره اجرا نمی‌کنم. ${PUBLIC_CONTEXT}`
        : `${PUBLIC_CONTEXT} ${FIXTURE_NOTE}`,
      proposal: null,
      tool: {
        key,
        name: "retrieve_public_context",
        summary: PUBLIC_CONTEXT,
      },
    };
  }
  if (wantsMemory(text)) {
    if (!reviewer) {
      return {
        reply: `مهمان نمی‌تواند پیشنهاد حافظه بسازد. ${FIXTURE_NOTE}`,
        proposal: null,
        tool: null,
      };
    }
    const memoryText = text
      .replace(/یادت (باشد|باشه|بمونه|بماند) که/g, "")
      .replace(/remember that/gi, "")
      .trim();
    const proposal: Proposal = {
      id: `mem-${utteranceId}`,
      memoryClass: classify(memoryText || text),
      text: memoryText || text,
      utteranceId,
      action: "memory.write",
      resource: "preview_browser_memory",
    };
    return {
      reply: "این فقط یک پیشنهاد است. تا خودت همین کارت را تأیید نکنی چیزی ذخیره نمی‌شود. «بله» با جملهٔ اضافه مجوز نیست.",
      proposal,
      tool: null,
    };
  }
  const remembered = state.memories.length
    ? `حافظهٔ تأییدشدهٔ همین مرورگر: ${state.memories.map((item) => item.text).join(" | ")}.`
    : "حافظهٔ تأییدشده‌ای در این مرورگر نیست.";
  return {
    reply: `${remembered} اگر چیزی باید بماند، صریح بگو «یادت باشد». ${FIXTURE_NOTE}`,
    proposal: null,
    tool: null,
  };
}
