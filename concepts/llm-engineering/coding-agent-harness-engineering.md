---
id: coding-agent-harness-engineering
title: Coding Agent Harness Engineering
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/google-day-1-v3
related:
  - skills-as-unit-of-agent-improvement
  - toolsets-and-mcp-unified-tool-surface
  - agent-space-access-boundary
  - llm-observability
  - conductor-orchestrator-developer-modes
  - context-engineering-for-coding-agents
  - agent-specialization-as-scaling-mechanism
  - effective-trust-for-agents
  - ephemeral-agent-execution-sandbox
  - agentcore-harness-vs-runtime-tradeoff
tags:
  - agentic-engineering
  - coding-agents
  - verification
  - observability
---

# Coding Agent Harness Engineering

- **One-sentence definition**: Coding-agent harness engineering designs the rules, tools, sandboxes, orchestration, hooks, and observability that make a raw model a constrained software worker.
- **Why it exists / what problem it solves**: Agent failures often come from missing boundaries, feedback, or tools, so replacing the model alone does not reliably improve safety or performance.
- **Keywords**: harness, tools, sandbox, orchestration, hooks, observability
- **Related concepts**: [[toolsets-and-mcp-unified-tool-surface]], [[agent-space-access-boundary]], [[llm-observability]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: The New SDLC with Vibe Coding: From Ad-hoc Prompting to Agentic Engineering

## Summary

A model is the engine, not the whole vehicle. The harness is the surrounding machinery that gives it instructions, safe places to execute code, tools, feedback, and a way to inspect what happened. Designing that machinery is often more useful than changing models.

## Example

Before an agent can edit a service, its harness gives it a read-only code-search tool, a sandboxed test runner, a rule that blocks secrets from commits, and trace logging. A failed test returns to the agent for one bounded retry; a sensitive write requires human approval.

## Relationship to existing concepts

- [[skills-as-unit-of-agent-improvement]]: A harness discovers, loads, and constrains skills as independently improved capabilities.
- [[toolsets-and-mcp-unified-tool-surface]]: Tool surfaces define the actions available inside the harness.
- [[agent-space-access-boundary]]: Access boundaries constrain which accounts, tools, and data an agent may use.
- [[llm-observability]]: Observability shows whether the harness is safe, effective, and cost-controlled.
- [[conductor-orchestrator-developer-modes]]: The harness supplies the controls and evidence used in either developer mode.
- [[context-engineering-for-coding-agents]]: Context design supplies the instructions and information used by the harness.
- [[agent-specialization-as-scaling-mechanism]]: The harness enforces the routing and tool boundaries that let specialists remain focused.
- [[effective-trust-for-agents]]: The harness continuously measures and enforces the agent's authorization to continue.
- [[ephemeral-agent-execution-sandbox]]: A disposable isolated runner is a concrete harness control for generated code.
- [[agentcore-harness-vs-runtime-tradeoff]]: A concrete commercial split of this concept's general principle — buy the whole orchestration loop as configuration, or write it yourself and buy only the infrastructure underneath it.

## My questions

- Which harness guardrails must be deterministic rather than prompt-based?
