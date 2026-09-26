---
id: bounded-tool-calls-vs-agent-delegation
title: Bounded Tool Calls vs. Agent Delegation
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/agent-tools---interoperability-day-2/
related:
  - mcp-bidirectional-json-rpc-substrate
  - protocol-based-agent-access-surface
  - ucp-ap2-commerce-payment-separation
tags:
  - llm-engineering
  - mcp
  - a2a
---

# Bounded Tool Calls vs. Agent Delegation

- **One-sentence definition**: A bounded tool call requests a structured result, while agent delegation assigns responsibility for an evolving task that may need clarification, negotiation, interruption, and resumption.
- **Why it exists / what problem it solves**: Treating every specialist as a synchronous tool hides long-running state inside an interface built for one request and one response, turning the caller into an accidental workflow engine.
- **Keywords**: tool call, delegation, workflow, multi-turn, interruption, responsibility
- **Related concepts**: [[mcp-bidirectional-json-rpc-substrate]], [[protocol-based-agent-access-surface]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: Agent Tools & Interoperability — Day 2

## Summary

Use a tool call when the caller can describe the work completely and needs a result back, such as converting currency. Use delegation when the other agent must own a task that can unfold over time, ask questions, pause, or negotiate trade-offs. The practical test is simple: does the caller need a result, or another participant to take responsibility? The second case needs collaboration semantics instead of a thin tool wrapper.

## Example

`get_exchange_rate("USD", "TWD")` is a bounded tool call. “Resolve this vendor-contract dispute within the approved budget” is a delegation: the legal agent may ask for clarification, present options, wait for approval, and resume later.

## Relationship to existing concepts

- [[mcp-bidirectional-json-rpc-substrate]]: MCP supports structured request-and-response tool interactions.
- [[protocol-based-agent-access-surface]]: A protocol access surface can expose both tool and agent-to-agent entry points; this concept decides which kind of interaction fits.
- [[ucp-ap2-commerce-payment-separation]]: UCP and AP2 are structured transactional operations, not a substitute for delegating an evolving task.

## My questions

- Which task signals should automatically route work from a tool call to a delegated agent?
- How should a delegator set budgets and cancellation rules without taking back responsibility for the workflow?
