---
id: agent-instruction-placement-by-scope
title: Agent Instruction Placement by Scope
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/day-5-v3
related:
  - static-vs-dynamic-agent-context
tags:
  - agentic-engineering
  - coding-agents
  - context-engineering
---

# Agent Instruction Placement by Scope

- **One-sentence definition**: Put an agent instruction in the narrowest durable place that matches who needs it and how long it should last.
- **Why it exists / what problem it solves**: Repeating every rule in chat wastes context, while keeping an enduring rule only in one conversation makes later work inconsistent.
- **Keywords**: instruction scope, durable context, project rules, agent skills, system prompt
- **Related concepts**: [[static-vs-dynamic-agent-context]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: Spec-Driven Production Grade Development in the Age of Vibe Coding

## Summary

Instructions are like signs: put a temporary detour sign in the current conversation, but put a building rule at the building entrance. Use chat for a short-lived request, a checked-in specification for one task, a skill for a repeatable procedure, and project or global instructions for stable conventions. This keeps the active context smaller and makes the rule available to the people and agents who actually need it. The key choice is the rule's lifetime and audience, not merely whether an agent loads it every time.

## Example

A developer writes “generate the failing tests for scenario 3” in chat. The payment-retry API contract and scenarios live in `specs/payment_retry.md`, a documentation-maintenance workflow lives in a reusable skill, and the repository's test command belongs in `AGENTS.md`. Moving all four into the chat prompt would make the next task slower and less reproducible.

## Relationship to existing concepts

- [[static-vs-dynamic-agent-context]]: Dynamic loading decides when context is fetched; placement decides which durable home and audience a rule has.

## My questions

- Which project rules are stable enough to promote from a task specification into shared instructions?
- How can a team audit conflicting global and project-level instructions?
