import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { EVAL_PACK } from "../src/lib/ella/pack.ts";

const packPath = new URL("../../../evals/persian/fa-IR-conversational-baseline-v0/pack.json", import.meta.url);

test("Persian pack is the unscored 18-item development set", () => {
  const data = JSON.parse(readFileSync(packPath, "utf8")) as {
    id: string;
    status: string;
    held_out: boolean;
    criteria: string[];
    items: { id: string; stimulus: string }[];
    pass_scores: null;
    qalam_profile: null;
  };
  assert.equal(data.id, "fa-IR-conversational-baseline-v0");
  assert.equal(data.status, "unscored_development_material");
  assert.equal(data.held_out, false);
  assert.equal(data.pass_scores, null);
  assert.equal(data.qalam_profile, null);
  assert.equal(data.criteria.length, 8);
  assert.equal(data.items.length, 18);
  assert.equal(EVAL_PACK.items.length, 18);
  assert.equal(EVAL_PACK.criteria.length, 8);
  assert.equal(EVAL_PACK.heldOut, false);
  assert.equal(EVAL_PACK.qalamProfile, null);
  assert.equal(EVAL_PACK.passScores, null);
  assert.deepEqual(
    EVAL_PACK.items.map((item) => item.stimulus),
    data.items.map((item) => item.stimulus),
  );
  assert.equal(
    data.items.find((item) => item.id === "fa-016")?.stimulus,
    "بله، و به علی هم زنگ بزن.",
  );
});
