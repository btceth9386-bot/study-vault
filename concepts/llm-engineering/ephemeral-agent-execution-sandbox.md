---
id: ephemeral-agent-execution-sandbox
title: Ephemeral Agent Execution Sandbox
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/vibe-coding-agent-security-and-evaluation-day-4
related:
  - coding-agent-harness-engineering
  - agent-space-access-boundary
  - risk-bounded-ai-pilot-design
  - code-as-action-agent-loop
  - untrusted-content-isolation-for-agents
tags:
  - coding-agents
  - security
  - sandboxing
  - isolation
---

# Ephemeral Agent Execution Sandbox

- **One-sentence definition**: An ephemeral agent execution sandbox runs generated code in an isolated environment with restricted host and network access, then destroys its state when the task ends.
- **Why it exists / what problem it solves**: Generated code is untrusted until proven otherwise; a persistent or host-adjacent environment lets mistakes and malicious payloads survive or spread.
- **Keywords**: sandbox, container, network isolation, host access, reset
- **Related concepts**: [[coding-agent-harness-engineering]], [[agent-space-access-boundary]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: Vibe Coding Agent Security and Evaluation

## Summary

Treat each generated program like a disposable workshop, not a room in the main building. It can receive only the files, tools, and network access needed for one task. When the task finishes, the workshop is torn down so a compromised script cannot leave behind a process, credential, or altered state for the next run.

## Example

An agent needs to test a package-install script. The harness runs it in a new network-isolated container with a read-only source checkout and no host socket. After the test report is collected, the container and its filesystem disappear—even if the script attempted to persist a backdoor.

## Relationship to existing concepts

- [[coding-agent-harness-engineering]]: A sandbox is a concrete execution control in the harness.
- [[agent-space-access-boundary]]: The boundary decides which resources a sandboxed agent can receive.
- [[risk-bounded-ai-pilot-design]]: A technical sandbox limits code execution, while a risk-bounded pilot limits business rollout scope.
- [[code-as-action-agent-loop]]: Generated multi-tool code needs the isolated execution boundary a sandbox provides.
- [[untrusted-content-isolation-for-agents]]: Contains generated code even if hostile retrieved content influenced the agent.

## My questions

- When does a task genuinely need network access, and how can that access remain narrow?
- Which evidence should survive sandbox deletion for debugging and forensics?
