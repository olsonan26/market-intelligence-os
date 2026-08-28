import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname } from "node:path";

const sourceCommit = "935695493723815540daa4995544602bd5f2cc10";
const sourceRoot = `https://raw.githubusercontent.com/olsonan26/market-intelligence-os/${sourceCommit}`;

const assets = [
  {
    path: "public/brand/fox-trading-mark.png",
    sha256: "d2f008ce995c931282c53375bad1488fa92a183ad0068d20e0a7a5f4c6669443",
  },
  {
    path: "app/icon.png",
    sha256: "d2f008ce995c931282c53375bad1488fa92a183ad0068d20e0a7a5f4c6669443",
  },
  {
    path: "app/apple-icon.png",
    sha256: "b8d01b9734c54d9197cb91be9e6a15cbaad8833a05cbf4d713a2db8d829a27f5",
  },
];

const digest = (content) => createHash("sha256").update(content).digest("hex");

for (const asset of assets) {
  let content;

  try {
    content = await readFile(asset.path);
  } catch (error) {
    if (error?.code !== "ENOENT") throw error;
    const response = await fetch(`${sourceRoot}/${asset.path}`);
    if (!response.ok) throw new Error(`Could not retrieve ${asset.path}: HTTP ${response.status}`);
    content = Buffer.from(await response.arrayBuffer());
    await mkdir(dirname(asset.path), { recursive: true });
    await writeFile(asset.path, content);
  }

  const actual = digest(content);
  if (actual !== asset.sha256) {
    throw new Error(`Brand integrity failure for ${asset.path}: expected ${asset.sha256}, received ${actual}`);
  }
}

console.log("FOX TRADING Option 2 brand assets verified.");
