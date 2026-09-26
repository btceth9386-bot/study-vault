---
id: execution-mode-specific-agent-prompting
title: Execution-Mode-Specific Agent Prompting
depth: 2
lab_status: not-started
last_reviewed: 2026-09-26
review_due: 2026-09-29
sources:
  - sources/papers/day-5-v3
related:
  - conductor-orchestrator-developer-modes
  - change-specific-release-testing
tags:
  - agentic-engineering
  - coding-agents
---

# Execution-Mode-Specific Agent Prompting

- **One-sentence definition**: Change an agent's evidence, constraints, and work sequence to match whether it is designing a project, adding a feature, fixing a bug, maintaining documentation, or handling data.
- **Why it exists / what problem it solves**: “Write code” hides different risks: projects need an agreed architecture, features need local convention matching, bugs need evidence, and data work needs auditable commands.
- **Keywords**: execution mode, project generation, feature work, bug diagnosis, documentation, data engineering
- **Related concepts**: [[conductor-orchestrator-developer-modes]], [[change-specific-release-testing]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: Spec-Driven Production Grade Development in the Age of Vibe Coding

## Summary

An agent needs a different brief for a new house than for repairing a leaking tap. For a new project, require an architecture and plan before code; for a feature, point to local conventions and review the diff. For a bug, start with logs and a failing reproduction, then constrain the repair to the root cause. Keep documentation synchronized with code, and make data work show the exact query or command used so someone else can inspect it.

## Example

Instead of telling an agent “fix checkout,” provide the failing curl command, the error log, and the constraint “repair only the root cause; do not refactor unrelated code.” The agent first preserves the failure as a test, then makes the smallest change that passes it. A new checkout project would instead begin with a reviewed architecture and API contracts.

## Relationship to existing concepts

- [[conductor-orchestrator-developer-modes]]: Those modes choose how closely a person guides the agent; execution modes choose the task-specific evidence and constraints.
- [[change-specific-release-testing]]: A mode-specific prompt states what must be verified, while change-specific testing focuses that verification on the current risk.

## My questions

- Which execution modes should be encoded as reusable skills in this repository?
- What evidence is sufficient before a bug-fix agent may edit code?
