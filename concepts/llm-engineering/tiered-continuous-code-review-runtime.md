---
id: tiered-continuous-code-review-runtime
title: Tiered Continuous Code Review Runtime
depth: 2
lab_status: not-started
last_reviewed: 2026-09-26
review_due: 2026-09-29
sources:
  - sources/papers/day-5-v3
related:
  - agentic-engineering-tco-curve
  - natural-language-cron-agent-automation
tags:
  - agentic-engineering
  - coding-agents
---

# Tiered Continuous Code Review Runtime

- **One-sentence definition**: Choose a managed, CI-hosted custom, or fully owned stateful code reviewer based on policy specificity, memory needs, and the cost of failure.
- **Why it exists / what problem it solves**: Continuous review must keep up with machine-generated changes, but a custom runtime and its memory, evaluation, and on-call burden are wasteful when a simpler reviewer catches the real risks.
- **Keywords**: continuous review, managed reviewer, CI, codebase memory, runtime ownership
- **Related concepts**: [[agentic-engineering-tco-curve]], [[natural-language-cron-agent-automation]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: Spec-Driven Production Grade Development in the Age of Vibe Coding

## Summary

Start with the smallest review runtime that catches the risks that matter. A managed reviewer is fast to enable but uses vendor-defined criteria. A CI-hosted reviewer lets a team commit its own skill, prompt, and checks without owning the runtime; this is the practical middle ground for most teams. Build a fully owned, stateful reviewer only when it needs durable cross-change memory, deep codebase understanding, or must protect against severe outcomes such as regressions or secret leaks.

## Example

A fintech team's managed reviewer repeatedly flags approved boilerplate but misses unmasked personal data in logs. The team moves to a CI job that runs a short repository-owned compliance-review skill on each pull request. It does not build a graph-backed Tier 3 system because the CI reviewer catches the actual issue without a custom runtime's operating cost.

## Relationship to existing concepts

- [[agentic-engineering-tco-curve]]: The three tiers make the trade between initial control and ongoing ownership cost concrete for repository review.
- [[natural-language-cron-agent-automation]]: A CI event or schedule can trigger the reviewer without a developer invoking it manually.

## My questions

- Which missed review findings would justify moving from CI-hosted review to a stateful runtime?
- How should a team measure false positives before increasing a reviewer's complexity?
