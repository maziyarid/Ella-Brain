import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { GATE_PHRASES, gatePhrase } from "../src/lib/ella/gate-client.ts";

test("gate phrases match the backend pack and are not memory commands", () => {
  const pack = JSON.parse(
    readFileSync(new URL("../../../ella_channel/phrases.json", import.meta.url), "utf8"),
  ) as { roundtrip: string; invalid_dependency: string };
  assert.equal(GATE_PHRASES.roundtrip, pack.roundtrip);
  assert.equal(GATE_PHRASES.invalid_dependency, pack.invalid_dependency);
  assert.equal(gatePhrase(`  ${pack.roundtrip}  `), "roundtrip");
  assert.equal(gatePhrase(pack.invalid_dependency), "invalid_dependency");
  assert.equal(gatePhrase("یادت باشد که جواب کوتاه می‌خواهم"), null);
});
