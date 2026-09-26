---
id: runtime-agent-bill-of-materials
title: Runtime Agent Bill of Materials
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/vibe-coding-agent-security-and-evaluation-day-4
related:
  - llm-observability
  - trace-aware-agent-evaluation
  - effective-trust-for-agents
tags:
  - coding-agents
  - observability
  - security
  - inventory
---

# Runtime Agent Bill of Materials

- **One-sentence definition**: A Runtime Agent Bill of Materials is a live inventory of the models, tools, data sources, credentials, and external associations active during an agent run.
- **Why it exists / what problem it solves**: Static inventories become stale when agents discover tools and generate subgoals, hiding the current blast radius and intent drift.
- **Keywords**: AgBOM, runtime inventory, blast radius, intent drift, tools
- **Related concepts**: [[llm-observability]], [[trace-aware-agent-evaluation]], [[effective-trust-for-agents]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: Vibe Coding Agent Security and Evaluation

## Summary

A normal software bill of materials is a parts list made before shipment. An agent needs a live version because its active parts can change from one moment to the next. The Runtime Agent Bill of Materials (AgBOM) records the models, tools, data, credentials, and external links currently in use so operators can see the real blast radius and reassess whether the run remains authorized.

## Example

A research agent begins with a search API and a public document store. When it requests a new CRM connector, the AgBOM records that connector and its credential immediately. Effective-trust controls can then stop the run because the new data source is outside the assigned research task.

## Relationship to existing concepts

- [[llm-observability]]: Records the runtime events that populate the inventory.
- [[trace-aware-agent-evaluation]]: Uses the resulting trajectory to judge whether tool use was acceptable.
- [[effective-trust-for-agents]]: Uses the live inventory when deciding whether continued execution remains authorized.

## My questions

- How detailed should an AgBOM be without collecting unnecessary sensitive data?
- What change in the inventory should trigger immediate human review?
