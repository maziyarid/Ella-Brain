import assert from "node:assert/strict";
import test from "node:test";
import { postGateOp, type GateSession } from "../src/lib/ella/gate-client.ts";

const session: GateSession = { session_id: "s", token: "t", access: "operator", principal_ignored: true };
const NOTHING_WRITTEN = /نوشته نشد/;

async function withFetch(impl: typeof fetch, run: () => Promise<void>) {
  const original = globalThis.fetch;
  globalThis.fetch = impl;
  try {
    await run();
  } finally {
    globalThis.fetch = original;
  }
}

test("transport failure on /v1/ops reports an unknown outcome, not nothing written", async () => {
  const failures: (typeof fetch)[] = [
    async () => {
      throw new TypeError("network down");
    },
    async () => new Response("Bad Gateway", { status: 502 }),
  ];
  for (const impl of failures) {
    await withFetch(impl, async () => {
      const result = await postGateOp(session, "req-1", "کار مصنوعی را ثبت کن");
      assert.equal(result.ok, false);
      assert.equal(result.error, "outcome_unknown");
      assert.doesNotMatch(result.read_back, NOTHING_WRITTEN);
      assert.match(result.read_back, /نامعلوم/);
    });
  }
});

test("a server-confirmed rejection keeps its own read-back", async () => {
  const body = { ok: false, error: "guest_denied", read_back: "مهمان اجازهٔ این کار را ندارد. هیچ نسخه‌ای نوشته نشد." };
  await withFetch(async () => Response.json(body, { status: 403 }), async () => {
    const result = await postGateOp(session, "req-2", "کار مصنوعی را ثبت کن");
    assert.deepEqual(result, body);
  });
});
