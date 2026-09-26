---
id: agent-loop-termination-policy
title: Agent Loop Termination Policy
depth: 2
lab_status: not-started
last_reviewed: 2026-09-26
review_due: 2026-09-29
sources:
  - sources/papers/comprehensive-agent-engineering-guide-2026
related:
  - react-agentic-loop
  - trace-aware-agent-evaluation
  - harness-cost-attribution-and-hard-limits
tags:
  - llm-engineering
  - agents
  - tool-use
---

# Agent Loop Termination Policy

- **One-sentence definition**: An agent loop termination policy combines a completion signal with hard operational limits and optional goal verification to decide when autonomous work must stop.
- **Why it exists / what problem it solves**: An agent can stop before finishing, repeat work indefinitely, or keep taking actions after the useful work is done. Explicit boundaries prevent needless cost and harmful extra actions.
- **Keywords**: termination, max steps, budget, goal verification, final answer
- **Related concepts**: [[react-agentic-loop]], [[trace-aware-agent-evaluation]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: The Comprehensive Guide to AI Agent Engineering

## Summary

An agent loop needs a clear rule for putting down its tools. A model saying “I am done” is useful, but it is not enough on its own: it may be mistaken or keep exploring. A sound policy layers that signal with limits on steps, time, tokens, or cost, and can ask a separate verifier whether the goal was actually met. The result is a controlled stop: the agent finishes when it has evidence of completion, or stops safely when its budget is exhausted.

## Example

A bug-fixing agent may call `submit` when its tests pass. Its runtime still enforces a 40-step and $2 budget, then asks a verifier whether the reported fix addresses the original failing test. If the agent reaches the budget first, it returns its evidence and escalates instead of continuing unchecked.

## Relationship to existing concepts

- [[react-agentic-loop]]: This policy supplies the runtime boundary that stops a ReAct loop from running indefinitely.
- [[trace-aware-agent-evaluation]]: A trace or verifier can provide evidence that a claimed completion really satisfied the goal.
- [[harness-cost-attribution-and-hard-limits]]: A concrete managed-platform counterpart at a different layer — this concept covers the agent's own internal stopping logic, while that concept is a platform-enforced outer bound that holds regardless of what the agent's own logic decides, acting as a second, independent line of defense.

## My questions

- Which tasks need independent goal verification rather than a model-declared final answer?
- What should the agent return when a safety limit ends work before completion?
