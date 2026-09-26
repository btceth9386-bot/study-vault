---
id: model-agnostic-evaluation-provider-abstraction
title: Model-Agnostic Evaluation Provider Abstraction
depth: 2
lab_status: not-started
last_reviewed: 2026-09-19
review_due: 2026-09-22
sources:
  - sources/repos/promptfoo-promptfoo
related:
  - standardized-message-content-blocks
  - provider-chat-model-wrappers-in-langgraph-nodes
  - composable-llm-red-team-testing
  - trace-derived-evaluation-field-contract
tags:
  - llm-engineering
  - architecture
  - provider-integrations
---

# Model-Agnostic Evaluation Provider Abstraction

- **One-sentence definition**: A model-agnostic evaluation provider abstraction gives a test engine one call contract while adapters handle each model, API, script, or agent runtime.
- **Why it exists / what problem it solves**: Evaluation code should compare systems without spreading vendor authentication, message formats, tool conventions, errors, and usage accounting through the runner.
- **Keywords**: provider, adapter, interface, registry, API, evaluation engine
- **Related concepts**: [[standardized-message-content-blocks]], [[provider-chat-model-wrappers-in-langgraph-nodes]], [[composable-llm-red-team-testing]]
- **Depth**: 2/4
- **Last updated**: 2026-09-19
- **Source**: promptfoo/promptfoo

## Summary

An evaluation runner needs to ask many kinds of targets for an answer. Rather than learning every vendor's request format, it calls one provider contract. Each adapter translates that common call into the target's own authentication, request shape, response parsing, error behavior, and usage reporting.

A registry chooses the right adapter from configuration. This keeps the comparison and grading logic the same whether the target is a hosted model, a generic HTTP endpoint, a local script, or an agent SDK.

## Example

One test suite compares a hosted model with an internal agent endpoint. The runner calls both through the same provider interface. The hosted-model adapter attaches its API key and parses token usage; the HTTP adapter builds the internal request and extracts its response. The test and its assertions do not change.

## Relationship to existing concepts

- [[standardized-message-content-blocks]]: Both normalize provider differences, but content blocks standardize message payloads while this abstraction standardizes the execution boundary.
- [[provider-chat-model-wrappers-in-langgraph-nodes]]: Both use adapters; this one serves an evaluation engine rather than a graph node.
- [[composable-llm-red-team-testing]]: The provider boundary lets one set of red-team probes run against different target types.
- [[trace-derived-evaluation-field-contract]]: Abstracts over the model provider answering a call, while that concept abstracts over the agent framework that produced the trace being evaluated — a different axis of the same generic-support idea.

## My questions

- Which provider capabilities belong in the common contract, and which should remain adapter-specific?
- How should an evaluator report a comparison when providers expose incompatible usage data?
