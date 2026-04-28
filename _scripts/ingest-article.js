#!/usr/bin/env node
/**
 * ingest-article.js — Ingest a web article into sources/articles/<slug>/
 *
 * Usage: node ingest-article.js <url> [kb-root]
 *
 * Outputs:
 *   sources/articles/<slug>/meta.yaml
 *   sources/articles/<slug>/notes.md
 */

import { Readability } from "@mozilla/readability";
import TurndownService from "turndown";
import { JSDOM } from "jsdom";
import { execFileSync } from "node:child_process";
import { mkdirSync, writeFileSync, existsSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = fileURLToPath(new URL(".", import.meta.url));

// ── helpers ──────────────────────────────────────────────────────────────────

function slugify(text) {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, "")
    .trim()
    .replace(/[\s_]+/g, "-")
    .replace(/-+/g, "-")
    .slice(0, 60);
}

function today() {
  return new Date().toISOString().slice(0, 10);
}

function buildMetaYaml(fields) {
  const lines = Object.entries(fields).map(([k, v]) => {
    if (Array.isArray(v)) {
      if (v.length === 0) return `${k}: []`;
      return `${k}:\n${v.map((i) => `  - ${i}`).join("\n")}`;
    }
    // Quote strings that contain special YAML characters
    const needsQuote = typeof v === "string" && /[:#\[\]{},|>&*!'"@`]/.test(v);
    return `${k}: ${needsQuote ? `"${v.replace(/"/g, '\\"')}"` : v}`;
  });
  return lines.join("\n") + "\n";
}

async function fetchHtml(url) {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`HTTP ${res.status} ${res.statusText} — ${url}`);
  }
  return res.text();
}

function extractArticle(html, url) {
  const dom = new JSDOM(html, { url });
  const reader = new Readability(dom.window.document);
  const article = reader.parse();
  if (!article || !article.content || article.content.trim().length === 0) {
    throw new Error("No article content found — page may be a login wall or non-article page");
  }
  return article;
}

function htmlToMarkdown(html) {
  const td = new TurndownService({ headingStyle: "atx", codeBlockStyle: "fenced" });
  return td.turndown(html);
}

function validateMeta(metaPath, kbRoot) {
  const validatorPath = join(__dirname, "metadata_validator.py");
  const venv = join(kbRoot, ".venv", "bin", "python3");
  const python = existsSync(venv) ? venv : "python3";
  try {
    const result = execFileSync(python, ["-c",
      `import sys; sys.path.insert(0,'${__dirname}'); from metadata_validator import validate_source_meta; errs=validate_source_meta('${metaPath}'); [print(e) for e in errs]; sys.exit(1 if errs else 0)`
    ], { encoding: "utf-8" });
  } catch (err) {
    const msg = (err.stdout || "") + (err.stderr || "");
    throw new Error(`meta.yaml validation failed:\n${msg.trim()}`);
  }
}

// ── main ─────────────────────────────────────────────────────────────────────

async function ingestArticle(url, kbRoot) {
  // 1. Fetch
  let html;
  try {
    html = await fetchHtml(url);
  } catch (err) {
    throw new Error(`Failed to fetch URL: ${err.message}`);
  }

  // 2. Extract
  const article = extractArticle(html, url);

  // 3. Convert to Markdown
  const markdown = htmlToMarkdown(article.content);

  // 4. Build output paths
  const slug = slugify(article.title || new URL(url).hostname);
  const outDir = join(kbRoot, "sources", "articles", slug);
  mkdirSync(outDir, { recursive: true });

  // 5. Write meta.yaml
  const metaFields = {
    type: "article",
    title: article.title || url,
    url,
    authors: article.byline ? [article.byline] : [],
    language: article.lang || "en",
    date_consumed: today(),
    date_added: today(),
    status: "processed",
    related_concepts: [],
    tags: [],
  };
  const metaPath = join(outDir, "meta.yaml");
  writeFileSync(metaPath, buildMetaYaml(metaFields), "utf-8");

  // 6. Write notes.md
  const notesMd = `# ${article.title || url}\n\n${markdown}\n`;
  writeFileSync(join(outDir, "notes.md"), notesMd, "utf-8");

  // 7. Validate meta.yaml
  validateMeta(metaPath, kbRoot);

  return { slug, outDir, title: article.title };
}

// ── CLI entry ─────────────────────────────────────────────────────────────────

// Only run CLI logic when executed directly (not when imported by tests)
const isMain = process.argv[1] && fileURLToPath(import.meta.url) === resolve(process.argv[1]);

if (!isMain) { /* imported as module — skip CLI */ }
else {

const [,, url, kbRootArg] = process.argv;

if (!url) {
  console.error("Usage: node ingest-article.js <url> [kb-root]");
  process.exit(1);
}

const kbRoot = resolve(kbRootArg || process.cwd());

ingestArticle(url, kbRoot)
  .then(({ slug, outDir, title }) => {
    console.log(`✓ Ingested: ${title}`);
    console.log(`  → ${outDir}`);
    console.log(`  Next: run new-source prompt on sources/articles/${slug}/`);
  })
  .catch((err) => {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  });

}

export { ingestArticle, extractArticle, htmlToMarkdown, slugify };
