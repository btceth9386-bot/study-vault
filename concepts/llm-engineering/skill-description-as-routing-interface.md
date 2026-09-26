---
id: skill-description-as-routing-interface
title: Skill Description as a Routing Interface
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/agent-skills-day-3
related:
  - configuration-driven-llm-evaluation-matrix
  - static-vs-dynamic-agent-context
tags:
  - agent-skills
  - llm-engineering
  - routing
  - context-engineering
---

# Skill Description as a Routing Interface

- **One-sentence definition**: A skill description is a compact routing contract that says what a skill does, when it should activate, and when it must stay inactive.
- **Why it exists / what problem it solves**: The best instructions cannot help if routing never loads them, and vague overlaps load irrelevant context and create library regressions.
- **Keywords**: description, routing, triggers, anti-triggers, metadata, activation
- **Related concepts**: [[configuration-driven-llm-evaluation-matrix]], [[static-vs-dynamic-agent-context]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: Agent Skills

## Summary

The description is the sign on a skill's door. It has to identify the job clearly enough that the agent opens the right door, and it must say which nearby jobs do not belong there. Concrete positive triggers and explicit non-triggers make the description an interface, not marketing copy. Because it controls activation, it also controls which dynamic context enters a turn.

## Example

Instead of describing a skill as "helps with databases," write: "Use for PostgreSQL schema migrations; do not use for read-only SQL analysis or data cleanup." The first description can activate in many wrong situations; the second gives routing test cases.

## Relationship to existing concepts

- [[configuration-driven-llm-evaluation-matrix]]: Positive and negative trigger cases make routing behavior repeatable to test.
- [[static-vs-dynamic-agent-context]]: The description decides whether this skill's dynamic context becomes active.

## My questions

- Which negative triggers prevent the most costly false activations?
- How should two skills be revised when their descriptions match the same requests?
