---
id: state-externalized-skill-composition
title: State-Externalized Skill Composition
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/agent-skills-day-3
related:
  - langgraph-stategraph-state-schema
  - langgraph-channels-and-reducers
  - surgical-context-compression
  - artifact-based-agent-handoffs
tags:
  - agent-skills
  - llm-engineering
  - state-management
  - orchestration
---

# State-Externalized Skill Composition

- **One-sentence definition**: State-externalized skill composition coordinates multi-step capabilities through structured files, schemas, or message buses instead of accumulated natural-language context.
- **Why it exists / what problem it solves**: Passing raw model output between stages hides state, compounds errors, consumes attention, and makes runs hard to reproduce or debug.
- **Keywords**: structured state, message bus, DAG, schemas, context debt, reproducibility
- **Related concepts**: [[langgraph-stategraph-state-schema]], [[langgraph-channels-and-reducers]], [[surgical-context-compression]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: Agent Skills

## Summary

In a multi-step workflow, the context window should not be the database or message bus. Put intermediate state in a structured place that each skill can read and update under an explicit schema. This makes the handoff inspectable and repeatable while leaving the model's attention for the current decision. It also prevents one vague text output from becoming the fragile source of truth for every later step.

## Example

A research skill writes `{ "claims": [...], "citations": [...] }` to a validated JSON file. A writing skill consumes that file and writes a separate draft artifact. If the draft is wrong, the team can inspect each handoff instead of replaying a long conversation.

## Relationship to existing concepts

- [[langgraph-stategraph-state-schema]]: Explicit schemas define the structured state that workflow nodes may read and update.
- [[langgraph-channels-and-reducers]]: Channels and reducers give concurrent state updates well-defined merge semantics.
- [[surgical-context-compression]]: Both protect attention by retaining only the information needed for the current work.
- [[artifact-based-agent-handoffs]]: Typed deliverables are a practical structured-state contract between agents or workflow stages.

## My questions

- Which intermediate artifacts should be immutable for auditability?
- When is a simple file sufficient, and when does a workflow need a message bus?
