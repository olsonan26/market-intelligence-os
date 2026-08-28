import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import test from "node:test";

const read = (path) => readFile(new URL(`../${path}`, import.meta.url), "utf8");

test("the console exposes every required operator workspace", async () => {
  const source = await read("components/operator-console.tsx");
  for (const view of [
    "Market Pulse",
    "Markets",
    "Time Machine",
    "Research Lab",
    "Decision Center",
    "Risk & Execution",
    "System Memory",
    "System Health",
  ]) {
    assert.match(source, new RegExp(view.replace("&", "&")), `missing ${view}`);
  }
});

test("novices get guidance, explanations, and persistent fixture safety", async () => {
  const source = await read("components/operator-console.tsx");
  assert.match(source, /New here\? Read the dashboard in this order\./);
  assert.match(source, /Plain-English answer/);
  assert.match(source, /No real orders can be placed\./);
  assert.match(source, /Explain this decision/);
  assert.match(source, /Every number opens to its evidence/);
});

test("the visual system keeps semantic tokens and responsive states", async () => {
  const [baseCss, consoleCss] = await Promise.all([
    read("web/styles/mios.css"),
    read("app/globals.css"),
  ]);
  for (const token of ["--verified", "--caution", "--halt", "--signal", "--surface-0"]) {
    assert.ok(baseCss.includes(token) || consoleCss.includes(token), `missing ${token}`);
  }
  assert.match(consoleCss, /@media \(max-width: 68rem\)/);
  assert.match(consoleCss, /\.evidence-drawer/);
  assert.match(consoleCss, /:focus-visible/);
});

test("deployment is explicitly configured for Next.js", async () => {
  const config = JSON.parse(await read("vercel.json"));
  assert.equal(config.framework, "nextjs");
  assert.equal(config.buildCommand, "npm run build");
});

test("FOX TRADING branding is present and uses a production image asset", async () => {
  const [consoleSource, layout, logo, appIcon] = await Promise.all([
    read("components/operator-console.tsx"),
    read("app/layout.tsx"),
    readFile(new URL("../public/brand/fox-trading-mark.png", import.meta.url)),
    readFile(new URL("../app/icon.png", import.meta.url)),
  ]);
  assert.match(consoleSource, /FOX<\/span> TRADING/);
  assert.match(consoleSource, /\/brand\/fox-trading-mark\.png/);
  assert.match(consoleSource, /width=\{48\} height=\{48\} priority/);
  assert.match(layout, /default: "FOX TRADING"/);
  assert.equal(logo.readUInt32BE(16), 512, "fox mark must retain its approved width");
  assert.equal(logo.readUInt32BE(20), 512, "fox mark must retain its approved height");
  assert.equal(
    createHash("sha256").update(logo).digest("hex"),
    "d2f008ce995c931282c53375bad1488fa92a183ad0068d20e0a7a5f4c6669443",
    "fox mark must remain byte-for-byte identical to approved Option 2",
  );
  assert.deepEqual(appIcon, logo, "browser icon must use the approved fox mark");
});

test("the canvas chart uses colors its parser supports", async () => {
  const chart = await read("components/market-chart.tsx");
  assert.doesNotMatch(chart, /color:\s*"oklch\(/);
  assert.doesNotMatch(chart, /Color:\s*"oklch\(/);
});

test("global search covers markets and feature navigation", async () => {
  const source = await read("components/operator-console.tsx");
  assert.match(source, /marketMatches/);
  assert.match(source, /featureMatches/);
  assert.match(source, /event\.metaKey \|\| event\.ctrlKey/);
  assert.match(source, /No matching market or feature/);
});
