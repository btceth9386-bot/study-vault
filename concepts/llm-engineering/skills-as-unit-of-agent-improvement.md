---
id: skills-as-unit-of-agent-improvement
title: Skills as the Unit of Agent Improvement
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/agent-skills-day-3
related:
  - coding-agent-harness-engineering
  - prompt-version-management
tags:
  - agent-skills
  - llm-engineering
  - versioning
  - agent-improvement
---

# Skills as the Unit of Agent Improvement

- **One-sentence definition**: A skill is a small, conditional, versioned, owned capability that improves an agent without changing its model or global prompt.
- **Why it exists / what problem it solves**: Model changes are slow or centralized, while global-prompt changes tax every turn and can regress unrelated work; a skill limits both the change and where it activates.
- **Keywords**: conditional, composable, ownership, versioning, capability boundary, context tax
- **Related concepts**: [[coding-agent-harness-engineering]], [[prompt-version-management]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: Agent Skills

## Summary

Improving an agent does not always mean changing the model. A skill gives a team a small unit to own, test, version, and load only for the work it addresses. Compared with editing a universal prompt, it reduces the risk that a local improvement affects every task. Compared with retraining, it can be changed and reviewed by the team that owns the procedure.

## Example

To improve database-migration work, a team versions a migration skill with its checks and scripts. It tests the skill's trigger and execution cases, then releases that version. Unrelated agents do not pay the context cost or risk a behavior change because the skill does not load for their tasks.

## Relationship to existing concepts

- [[coding-agent-harness-engineering]]: The harness provides the runtime that discovers, loads, and constrains a skill.
- [[prompt-version-management]]: Both version behavior artifacts, but a skill is a narrower conditional capability than a global prompt.

## My questions

- When is a capability small enough to remain one skill instead of being split?
- Which ownership signals should be required before a team may publish a shared skill?
