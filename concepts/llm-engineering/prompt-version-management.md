---
id: prompt-version-management
title: Prompt Version Management
depth: 2
last_reviewed: 2026-05-04
review_due: 2026-05-07
sources:
  - sources/repos/langfuse-langfuse
related:
  - llm-observability
  - llm-as-judge-evaluation
  - caching-strategies
tags:
  - llm-engineering
  - prompts
  - deployment
---

# Prompt Version Management

- **One-sentence definition**: Prompt version management treats prompts as tracked, deployable artifacts instead of anonymous strings inside application code.
- **Why it exists / what problem it solves**: Prompt edits can change product behavior as much as code changes. Without versions, labels, history, and rollback, teams cannot safely test, deploy, or explain why an LLM response changed.
- **Keywords**: prompt version, label, production, latest, cache epoch, prompt dependency
- **Related concepts**: [[llm-observability]], [[llm-as-judge-evaluation]], [[caching-strategies]]
- **Depth**: 2/4
- **Last updated**: 2026-05-04
- **Source**: sources/repos/langfuse-langfuse

## Summary

A prompt is part of the application, even if it looks like plain text. Prompt version management gives it the same basic safety tools as code: a version number, a change history, labels such as `production`, and the ability to compare or roll back changes.

In Langfuse, prompts can be text or chat templates, can live in folder paths, and can be fetched by exact version or by label. Labels work like movable pointers: production can point to version 7 today and version 8 tomorrow. Redis caching makes reads fast, while an epoch-based invalidation strategy prevents old cached prompt mappings from living forever after a prompt changes.

## Example

A team has a customer-support prompt:

- Version 4 is stable and labeled `production`.
- Version 5 adds a stricter refund-policy instruction and is tested internally.
- If version 5 improves evaluator scores, the team moves the `production` label to version 5.
- If support quality drops, they move `production` back to version 4 without redeploying application code.

Each generation can record the prompt version it used, so later debugging can compare behavior across versions.

## Relationship to existing concepts

- [[llm-observability]]: Observability connects model outputs back to the prompt version that produced them.
- [[llm-as-judge-evaluation]]: Judge rubrics are prompts too, so evaluator behavior should be versioned.
- [[caching-strategies]]: Prompt lookup uses caching, but cache invalidation must be tied to prompt changes.

## Open questions

- Should prompt labels be mutable by anyone with edit access, or protected like production deploys?
- How should recursive prompt dependencies be tested before promotion?
