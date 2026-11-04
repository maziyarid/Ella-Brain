import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { MIC_OPEN_NOTE } from "../src/lib/ella/speech-boundary.ts";

const read = (path: string) => readFileSync(new URL(path, import.meta.url), "utf8");
const OVERCLAIM = /audio is not uploaded|no uploaded audio|audio in this prototype is not uploaded/i;

test("audio copy claims only what this app does, and names browser recognition", () => {
  assert.doesNotMatch(MIC_OPEN_NOTE, OVERCLAIM);
  assert.match(MIC_OPEN_NOTE, /This app does not upload or store audio/);
  assert.match(MIC_OPEN_NOTE, /browser/i);
  for (const doc of ["../README.md", "../../../docs/voice/open-decisions.md"]) {
    assert.doesNotMatch(read(doc), OVERCLAIM, doc);
  }
});
