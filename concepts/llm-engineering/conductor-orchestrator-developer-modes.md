---
id: conductor-orchestrator-developer-modes
title: Conductor and Orchestrator Developer Modes
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/google-day-1-v3
related:
  - coding-agent-harness-engineering
  - execution-mode-specific-agent-prompting
tags:
  - agentic-engineering
  - coding-agents
  - verification
---

# Conductor and Orchestrator Developer Modes

- **One-sentence definition**: Conductor mode gives an agent real-time, fine-grained direction; orchestrator mode delegates well-specified work asynchronously and evaluates the result.
- **Why it exists / what problem it solves**: Unfamiliar or subtle work needs live judgment, while bounded, patterned work can be delegated for throughput.
- **Keywords**: conductor, orchestrator, delegation, review, autonomy
- **Related concepts**: [[coding-agent-harness-engineering]], [[execution-mode-specific-agent-prompting]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: The New SDLC with Vibe Coding: From Ad-hoc Prompting to Agentic Engineering

## Summary

Use conductor mode when you need to watch and guide the work closely, such as a tricky bug or unfamiliar codebase. Use orchestrator mode when the goal, constraints, and checks are clear enough to hand off. The second mode shifts human effort from typing beside the agent to writing a good task and reviewing its evidence.

## Example

A developer conducts an agent through a payment bug because one rule is ambiguous. After clarifying it, they orchestrate ten well-specified migration tasks in parallel and review each pull request with its test results.

## Relationship to existing concepts

- [[coding-agent-harness-engineering]]: The harness supplies the tools, boundaries, and evidence needed for either working mode.
- [[execution-mode-specific-agent-prompting]]: The task type determines the evidence and constraints supplied inside either working mode.

## My questions

- What evidence should an orchestrator require before approving a delegated change?
