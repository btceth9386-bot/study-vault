---
id: bounded-agent-cognitive-state
title: Bounded Agent Cognitive State
depth: 2
lab_status: not-started
last_reviewed: 2026-09-26
review_due: 2026-09-29
sources:
  - sources/papers/comprehensive-agent-engineering-guide-2026
related:
  - surgical-context-compression
  - persistent-agent-session-restoration
tags:
  - llm-engineering
  - agents
  - context-engineering
---

# Bounded Agent Cognitive State

- **One-sentence definition**: Bounded agent cognitive state keeps a fixed-size, schema-constrained record of the goal, constraints, facts, decisions, artifacts, questions, and next actions as the agent's persistent state across turns.
- **Why it exists / what problem it solves**: Appending or repeatedly summarizing chat history still grows noisy over time. A bounded state makes memory cost predictable and forces deliberate choices about what to retain.
- **Keywords**: bounded state, schema, eviction, constraints, agent memory
- **Related concepts**: [[surgical-context-compression]], [[persistent-agent-session-restoration]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: The Comprehensive Guide to AI Agent Engineering

## Summary

Think of this state as a small, carefully maintained task board rather than a pile of old chat messages. It has named slots for the facts and decisions the agent needs, and each slot has a limit. When new information arrives, the agent updates the board and deliberately drops the least important item if the board is full. This avoids unbounded context growth, but the schema matters: an important kind of information that has no slot can be lost.

## Example

An incident-response agent stores one current goal, at most ten active constraints, twenty key facts, fifteen recent decisions, artifact paths, five open questions, and five next actions. After a tool result shows a suspected cause is false, it removes that fact and records the decision instead of keeping every past log in its prompt.

## Relationship to existing concepts

- [[surgical-context-compression]]: Compression reduces a growing history; bounded cognitive state replaces that history with a fixed schema.
- [[persistent-agent-session-restoration]]: Durable storage can preserve the bounded state across a restart without restoring an entire transcript.

## My questions

- Which fields are essential for the agents I build, and which should be deliberately excluded?
- How can an agent detect that an eviction decision discarded information it will need later?
