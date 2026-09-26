---
id: agentic-coding-80-percent-problem
title: The 80% Problem in Agentic Coding
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/google-day-1-v3
related:
  - trace-aware-agent-evaluation
  - hybrid-llm-output-assertions
  - change-specific-release-testing
tags:
  - agentic-engineering
  - coding-agents
  - verification
  - edge-cases
  - software-quality
---

# The 80% Problem in Agentic Coding

- **One-sentence definition**: The 80% problem is when a coding agent quickly produces the obvious bulk of a feature but leaves the difficult edge cases, integrations, and correctness decisions unfinished.
- **Why it exists / what problem it solves**: Code that looks plausible can still embody a wrong business assumption or omit a failure path, so teams need to focus human judgment and verification on the final, risk-heavy portion.
- **Keywords**: coding agents, edge cases, integration, ambiguity, verification, correctness
- **Related concepts**: [[trace-aware-agent-evaluation]], [[hybrid-llm-output-assertions]], [[change-specific-release-testing]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: The New SDLC with Vibe Coding: From Ad-hoc Prompting to Agentic Engineering

## Summary

A coding agent can assemble the familiar parts of a feature very quickly, much like a contractor who can build the visible rooms before the plumbing, permits, and unusual corners are settled. The missing work is often not more typing: it is deciding what an ambiguous rule means, handling a rare failure, and checking that the new code fits the rest of the system.

That makes a basic green test suite an incomplete signal. The practical response is to use agents for clear, bounded implementation while deliberately spending human attention on requirements, architecture, and verification of the risky paths.

## Example

An agent adds a "refund order" endpoint and passes tests for a valid, paid order. The remaining 20% includes partial refunds, already-refunded orders, a timeout from the payment provider, and the rule that a shipped order needs approval. A developer adds those cases to the acceptance criteria and verifies the endpoint's external calls as well as its final response.

## Relationship to existing concepts

- [[trace-aware-agent-evaluation]]: Trace checks can expose an apparently correct feature that used an unsafe or incomplete action path.
- [[hybrid-llm-output-assertions]]: Combined deterministic, model-based, and trace checks give broader evidence than a basic test alone.
- [[change-specific-release-testing]]: Targeted tests focus verification on the edge cases and integrations affected by a specific change.

## My questions

- Which kinds of requirements should always be made explicit before an agent begins implementation?
- How can a team identify the risk-heavy final 20% early enough to plan verification work?
