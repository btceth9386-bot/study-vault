---
id: context-engineering-for-coding-agents
title: Context Engineering for Coding Agents
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/google-day-1-v3
related:
  - agent-skill-progressive-disclosure
  - coding-agent-harness-engineering
  - executable-specification-as-architectural-north-star
tags:
  - agentic-engineering
  - coding-agents
  - verification
---

# Context Engineering for Coding Agents

- **One-sentence definition**: Context engineering deliberately provides an agent with the instructions, knowledge, memory, examples, tools, and guardrails needed for a task.
- **Why it exists / what problem it solves**: A clever prompt cannot replace missing project rules, architecture, or boundaries.
- **Keywords**: instructions, knowledge, memory, examples, tools, guardrails
- **Related concepts**: [[agent-skill-progressive-disclosure]], [[coding-agent-harness-engineering]], [[executable-specification-as-architectural-north-star]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: The New SDLC with Vibe Coding: From Ad-hoc Prompting to Agentic Engineering

## Summary

Give an agent what a capable new teammate needs to act safely: the goal, relevant facts, examples, available actions, and boundaries. Good context is structured and task-appropriate, not merely a longer prompt.

## Example

For a billing change, provide the API contract, refund rules, relevant tests, repository conventions, and a sandboxed test tool—rather than pasting the whole repository.

## Relationship to existing concepts

- [[agent-skill-progressive-disclosure]]: The three-layer loading pattern makes specialized context available without loading it for every task.
- [[coding-agent-harness-engineering]]: Context is a core harness component.
- [[executable-specification-as-architectural-north-star]]: A versioned specification is durable structured context for both implementation and verification.

## My questions

- Which task facts must always be explicit?
