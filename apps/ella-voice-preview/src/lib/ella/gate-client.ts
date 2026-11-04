export const GATE_PHRASES = {
  roundtrip: "کار مصنوعی را ثبت کن",
  invalid_dependency: "وابستگی نامعتبر را امتحان کن",
} as const;

export type BackendAccess = "guest" | "operator";

export interface GateSession {
  session_id: string;
  token: string;
  access: BackendAccess;
  principal_ignored: true;
}

export interface GateResult {
  ok: boolean;
  duplicate?: boolean;
  read_back: string;
  error?: string;
  version?: number | null;
}

export function gatePhrase(text: string): keyof typeof GATE_PHRASES | null {
  const normalized = text.replace(/\s+/g, " ").trim();
  if (normalized === GATE_PHRASES.roundtrip) return "roundtrip";
  if (normalized === GATE_PHRASES.invalid_dependency) return "invalid_dependency";
  return null;
}

export async function openGateSession(access: BackendAccess): Promise<GateSession> {
  const response = await fetch("/v1/sessions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ access, principal: "ignored" }),
  });
  if (!response.ok) throw new Error("gate session refused");
  return (await response.json()) as GateSession;
}

/** No usable reply: the adapter may or may not have written. Never claim "nothing written" here. */
export const OUTCOME_UNKNOWN_READ_BACK =
  "پاسخ درگاه نرسید. نتیجه نامعلوم است؛ شاید نوشته شده باشد و شاید نه. پیش از تکرار، وضعیت را بررسی کن.";

export function outcomeUnknown(): GateResult {
  return { ok: false, error: "outcome_unknown", read_back: OUTCOME_UNKNOWN_READ_BACK };
}

/** Server JSON is returned as-is. Network errors and non-JSON replies are an unknown outcome. */
export async function postGateOp(
  session: GateSession,
  requestId: string,
  text: string,
): Promise<GateResult> {
  let response: Response;
  try {
    response = await fetch("/v1/ops", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.token}`,
      },
      body: JSON.stringify({
        session_id: session.session_id,
        request_id: requestId,
        text,
      }),
    });
  } catch {
    return outcomeUnknown();
  }
  try {
    const result = (await response.json()) as GateResult;
    return typeof result?.read_back === "string" ? result : outcomeUnknown();
  } catch {
    return outcomeUnknown();
  }
}

export async function cancelGateOp(session: GateSession, requestId: string): Promise<void> {
  await fetch("/v1/cancel", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${session.token}`,
    },
    body: JSON.stringify({ session_id: session.session_id, request_id: requestId }),
  });
}
