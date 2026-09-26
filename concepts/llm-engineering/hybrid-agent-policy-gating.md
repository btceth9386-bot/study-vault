---
id: hybrid-agent-policy-gating
title: Hybrid Agent Policy Gating
depth: 2
lab_status: not-started
last_reviewed: 2026-09-26
review_due: 2026-09-29
sources:
  - sources/papers/day-5-v3
related:
  - zero-ambient-authority-for-agents
  - context-aware-high-stakes-agent-approval
  - untrusted-content-isolation-for-agents
tags:
  - coding-agents
  - security
  - authorization
---

# Hybrid Agent Policy Gating

- **One-sentence definition**: Hybrid policy gating checks both whether an agent may use a tool and whether its proposed use is safe before the tool runs.
- **Why it exists / what problem it solves**: Role permissions can allow a tool without recognizing a harmful request, while a probabilistic semantic judge should not replace fast, auditable deny-by-default rules.
- **Keywords**: policy server, structural gating, semantic gating, tool authorization, deny by default
- **Related concepts**: [[zero-ambient-authority-for-agents]], [[context-aware-high-stakes-agent-approval]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: Spec-Driven Production Grade Development in the Age of Vibe Coding

## Summary

Think of a tool call passing two checkpoints. The first is a traffic light: deterministic role and environment rules decide whether the agent may use that tool at all. The second is an intelligent referee: a separate model checks the proposed action and arguments against policies that need language understanding. Run the tool only when both pass; otherwise return the violation so the agent can correct itself or stop.

## Example

A support agent with the `viewer` role tries to call `send_email`. Structural gating rejects it immediately. An administrator may use `send_email`, but semantic gating rejects an action that contains an unmasked customer email address or attempts to message the whole database. A risky but policy-compliant action can then be escalated for human approval.

## Relationship to existing concepts

- [[zero-ambient-authority-for-agents]]: Task-scoped authority provides the narrow permissions that structural gating enforces at the tool boundary.
- [[context-aware-high-stakes-agent-approval]]: A flagged action can be explained and sent to a person for action-specific approval instead of being executed automatically.
- [[untrusted-content-isolation-for-agents]]: Prevents tool and retrieval content from becoming authority before policy gating evaluates an action.

## My questions

- Which semantic policy violations should always fail closed rather than ask a person?
- How should a team evaluate the semantic gate for bypasses and false positives?
