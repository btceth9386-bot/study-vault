---
id: ai-compressed-sdlc
title: AI-Compressed Software Development Lifecycle
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/google-day-1-v3
related:
  - change-specific-release-testing
  - release-readiness-blast-radius-review
  - llm-observability
tags:
  - agentic-engineering
  - coding-agents
  - verification
  - observability
---

# AI-Compressed Software Development Lifecycle

- **One-sentence definition**: An AI-compressed SDLC speeds implementation dramatically while requirements, architecture, and verification remain constrained by human judgment.
- **Why it exists / what problem it solves**: AI does not accelerate every phase equally, so teams must redesign feedback and review around the new bottleneck instead of merely inserting faster code generation into an old process.
- **Keywords**: SDLC, implementation, requirements, architecture, verification, feedback loop
- **Related concepts**: [[change-specific-release-testing]], [[release-readiness-blast-radius-review]], [[llm-observability]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: The New SDLC with Vibe Coding: From Ad-hoc Prompting to Agentic Engineering

## Summary

AI can turn a well-specified implementation task from weeks into hours, but it cannot remove the need to decide what the product should do or whether a trade-off is acceptable. The work becomes a tighter loop: requirements, prototype, tests, review, and production signals arrive closer together. The human role shifts toward setting direction and judging quality.

## Example

An agent creates a checkout prototype in one afternoon. Before release, a developer still resolves tax and refund rules, reviews architecture, runs targeted tests, and checks production telemetry. The implementation accelerated; accountability did not disappear.

## Relationship to existing concepts

- [[change-specific-release-testing]]: Compressed cycles need focused verification of each change's risks.
- [[release-readiness-blast-radius-review]]: Readiness review helps judge deployment risk when changes arrive faster.
- [[llm-observability]]: Production signals close the loop between development and real behavior.

## My questions

- Which reviews can be automated safely, and which require a human decision?
