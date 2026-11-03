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

export async function postGateOp(
  session: GateSession,
  requestId: string,
  text: string,
): Promise<GateResult> {
  const response = await fetch("/v1/ops", {
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
  return (await response.json()) as GateResult;
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
