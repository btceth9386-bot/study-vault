---
id: zero-ambient-authority-for-agents
title: Zero Ambient Authority for Agents
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/vibe-coding-agent-security-and-evaluation-day-4
related:
  - agent-space-access-boundary
  - secure-mcp-consumption-lifecycle
  - hybrid-agent-policy-gating
tags:
  - coding-agents
  - security
  - authorization
  - least-privilege
---

# Zero Ambient Authority for Agents

- **One-sentence definition**: Zero ambient authority gives an agent no inherited general-purpose privilege and issues only short-lived credentials scoped to the exact user, intent, resources, and time window of a task.
- **Why it exists / what problem it solves**: A confused or prompt-injected agent should not be able to reuse a developer's broad identity to reach secrets, unrelated files, or production systems.
- **Keywords**: least privilege, JIT downscoping, credentials, deny by default, confused deputy
- **Related concepts**: [[agent-space-access-boundary]], [[secure-mcp-consumption-lifecycle]], [[hybrid-agent-policy-gating]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: Vibe Coding Agent Security and Evaluation

## Summary

An agent should start with no spare keys. For each task, the system creates a fresh credential that grants only the specific data and action needed, then expires it when the task ends. This prevents the “confused deputy” failure where a tricked agent uses its operator's broad authority for an unrelated request.

## Example

For a task to update one staging configuration file, the agent receives a token that can write only that file in staging for fifteen minutes. A prompt injection asking it to read production secrets fails because its token has no access to the secrets store or production environment.

## Relationship to existing concepts

- [[agent-space-access-boundary]]: Defines the operational scope that task-specific credentials enforce.
- [[secure-mcp-consumption-lifecycle]]: Applies least privilege to connected tools and their authorization flows.
- [[hybrid-agent-policy-gating]]: Enforces task-scoped permission at each tool call and adds a semantic check for unsafe allowed uses.

## My questions

- How can a task request be translated into a safe resource scope automatically?
- Which operations should always require a fresh human-authorized credential?
