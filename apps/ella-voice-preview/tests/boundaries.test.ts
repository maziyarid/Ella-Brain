import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const app = (path: string) => readFileSync(new URL(`../${path}`, import.meta.url), "utf8");

test("dev and preview servers bind to loopback by default", () => {
  const scripts = (JSON.parse(app("package.json")) as { scripts: Record<string, string> }).scripts;
  for (const name of ["dev", "preview"]) {
    assert.doesNotMatch(scripts[name], /0\.0\.0\.0/, name);
    assert.match(scripts[name], /--host 127\.0\.0\.1/, name);
  }
  const config = app("vite.config.ts");
  assert.doesNotMatch(config, /0\.0\.0\.0/);
  assert.match(config, /server: \{ host: "127\.0\.0\.1"/);
  assert.match(config, /preview: \{ host: "127\.0\.0\.1"/);
});
