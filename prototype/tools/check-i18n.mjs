// Checks that the three language tables stay in sync with the page:
// every key the HTML uses exists in every language, the tables share one key
// set, and the Russian text baked into index.html (the no-JS fallback)
// matches the Russian table.
//
// Usage: node tools/check-i18n.mjs

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const html = readFileSync(join(root, "index.html"), "utf8");
const sandbox = { window: {} };
vm.runInNewContext(readFileSync(join(root, "i18n.js"), "utf8"), sandbox);
const tables = sandbox.window.SFERI_I18N;
const langs = Object.keys(tables);
const problems = [];

const decode = (s) => s
  .replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">")
  .replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/\s+/g, " ").trim();

const used = new Set();
for (const m of html.matchAll(/data-i18n(?:-aria)?="([^"]+)"/g)) used.add(m[1]);
for (const key of used) {
  for (const lang of langs) {
    if (!(key in tables[lang])) problems.push(`missing key "${key}" in ${lang}`);
  }
}

for (const lang of langs) {
  const keys = Object.keys(tables[lang]);
  for (const k of Object.keys(tables.ru)) if (!keys.includes(k)) problems.push(`${lang} lacks "${k}"`);
  for (const k of keys) if (!(k in tables.ru)) problems.push(`${lang} has extra "${k}"`);
  for (const [k, v] of Object.entries(tables[lang])) if (!String(v).trim()) problems.push(`${lang} "${k}" is empty`);
}

// inline Russian fallback must equal the table (elements without child tags)
for (const m of html.matchAll(/<([a-z0-9]+)[^>]*\sdata-i18n="([^"]+)"[^>]*>([^<]*)<\/\1>/g)) {
  const [, , key, text] = m;
  const inline = decode(text);
  if (inline && tables.ru[key] !== undefined && inline !== tables.ru[key]) {
    problems.push(`inline RU for "${key}" differs:\n    html:  ${inline}\n    table: ${tables.ru[key]}`);
  }
}

const unused = Object.keys(tables.ru).filter((k) =>
  !used.has(k) && !["htmlLang", "title", "description"].includes(k) &&
  !/^(nav\.close|proto\.show|form\.sending|form\.err)/.test(k));

if (unused.length) console.log(`note: keys not referenced by the page: ${unused.join(", ")}`);
if (problems.length) {
  console.error(`${problems.length} problem(s):\n- ` + problems.join("\n- "));
  process.exit(1);
}
console.log(`ok: ${used.size} keys used, ${langs.length} languages in sync`);
