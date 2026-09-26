---
id: effective-trust-for-agents
title: Effective Trust for Agents
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/vibe-coding-agent-security-and-evaluation-day-4
related:
  - coding-agent-harness-engineering
  - llm-observability
  - agent-space-access-boundary
  - runtime-agent-bill-of-materials
tags:
  - agentic-engineering
  - coding-agents
  - security
  - observability
---

# Effective Trust for Agents

- **One-sentence definition**: Effective trust is a continuously updated decision about whether an agent may keep acting, based on its identity, supply chain, runtime behavior, tools, data, and task context.
- **Why it exists / what problem it solves**: A valid login proves only a past identity check; it does not prove that a non-deterministic agent still follows the authorized intent.
- **Keywords**: continuous trust, intent drift, runtime context, assurance, authorization
- **Related concepts**: [[coding-agent-harness-engineering]], [[llm-observability]], [[agent-space-access-boundary]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: Vibe Coding Agent Security and Evaluation

## Summary

Trust in an agent is more like a live driving assessment than a badge at the door. A system keeps checking what the agent is using, what it is doing, and whether those actions still fit the assigned task. If the agent gains an unexpected tool, changes direction, or behaves suspiciously, its effective trust drops and the harness can narrow or stop its authority.

## Example

An agent is authorized to update a documentation site. It starts by editing Markdown, then unexpectedly requests a production database credential. The runtime records the new request, recognizes that it is outside the task's access boundary, and blocks the action until a human reviews it.

## Relationship to existing concepts

- [[coding-agent-harness-engineering]]: Provides the controls that measure and enforce trust at runtime.
- [[llm-observability]]: Provides the evidence used to reassess trust.
- [[agent-space-access-boundary]]: Defines part of the allowed operational scope.
- [[runtime-agent-bill-of-materials]]: The live inventory shows the resources that affect the current trust decision.

## My questions

- Which runtime signals should lower trust immediately?
- How can teams explain a trust decision clearly enough to audit or appeal it?
