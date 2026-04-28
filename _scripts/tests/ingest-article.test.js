/**
 * Tests for ingest-article.js
 *
 * Feature: personal-knowledge-base
 * Covers: HTML→Markdown conversion, meta.yaml fields, error handling
 */

import { describe, it, expect } from "vitest";
import { extractArticle, htmlToMarkdown, slugify } from "../ingest-article.js";

// ── slugify ───────────────────────────────────────────────────────────────────

describe("slugify", () => {
  it("lowercases and replaces spaces with hyphens", () => {
    expect(slugify("Hello World")).toBe("hello-world");
  });

  it("strips special characters", () => {
    expect(slugify("Hello, World! (2024)")).toBe("hello-world-2024");
  });

  it("collapses multiple hyphens", () => {
    expect(slugify("foo  --  bar")).toBe("foo-bar");
  });

  it("truncates to 60 characters", () => {
    const long = "a".repeat(80);
    expect(slugify(long).length).toBeLessThanOrEqual(60);
  });
});

// ── htmlToMarkdown ────────────────────────────────────────────────────────────

describe("htmlToMarkdown", () => {
  it("converts headings", () => {
    const md = htmlToMarkdown("<h1>Title</h1>");
    expect(md).toContain("# Title");
  });

  it("converts paragraphs", () => {
    const md = htmlToMarkdown("<p>Hello world</p>");
    expect(md).toContain("Hello world");
  });

  it("converts links", () => {
    const md = htmlToMarkdown('<a href="https://example.com">link</a>');
    expect(md).toContain("[link](https://example.com)");
  });

  it("converts code blocks with fenced style", () => {
    const md = htmlToMarkdown("<pre><code>const x = 1;</code></pre>");
    expect(md).toContain("```");
    expect(md).toContain("const x = 1;");
  });

  it("converts bold and italic", () => {
    const md = htmlToMarkdown("<strong>bold</strong> and <em>italic</em>");
    expect(md).toContain("**bold**");
    expect(md).toContain("_italic_");
  });
});

// ── extractArticle ────────────────────────────────────────────────────────────

const ARTICLE_HTML = `<!DOCTYPE html>
<html>
<head><title>Test Article</title></head>
<body>
  <article>
    <h1>Test Article</h1>
    <p>This is the first paragraph of the article with enough content to pass readability checks.</p>
    <p>This is the second paragraph with more content to ensure the article is detected properly.</p>
    <p>Third paragraph adds more substance to the article body for readability parsing.</p>
  </article>
</body>
</html>`;

describe("extractArticle", () => {
  it("extracts title from article HTML", () => {
    const article = extractArticle(ARTICLE_HTML, "https://example.com/test");
    expect(article.title).toBeTruthy();
  });

  it("extracts content from article HTML", () => {
    const article = extractArticle(ARTICLE_HTML, "https://example.com/test");
    expect(article.content).toBeTruthy();
    expect(article.content.length).toBeGreaterThan(0);
  });

  it("throws on empty content (login wall / non-article)", () => {
    const loginHtml = `<!DOCTYPE html><html><body><form><input type="password"/></form></body></html>`;
    expect(() => extractArticle(loginHtml, "https://example.com/login")).toThrow(
      /No article content found/
    );
  });

  it("throws on blank page", () => {
    const blank = `<!DOCTYPE html><html><body></body></html>`;
    expect(() => extractArticle(blank, "https://example.com/blank")).toThrow(
      /No article content found/
    );
  });
});

// ── meta.yaml field coverage ──────────────────────────────────────────────────

describe("meta.yaml required fields", () => {
  // Verify that extractArticle returns the data needed to populate all required fields.
  // The actual file writing is tested via integration; here we confirm the data shape.
  it("article object has title for meta.yaml title field", () => {
    const article = extractArticle(ARTICLE_HTML, "https://example.com/test");
    expect(typeof article.title).toBe("string");
    expect(article.title.length).toBeGreaterThan(0);
  });
});
