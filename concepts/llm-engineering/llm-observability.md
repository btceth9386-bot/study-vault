---
id: llm-observability
title: LLM Observability
depth: 2
last_reviewed: 2026-05-04
review_due: 2026-05-07
sources:
  - sources/repos/langfuse-langfuse
related:
  - llm-as-judge-evaluation
  - prompt-version-management
  - oltp-olap-split
  - dspy-signatures
  - react-agentic-loop
tags:
  - llm-engineering
  - observability
  - analytics
---

# LLM Observability

- **One-sentence definition**: LLM observability is structured monitoring for AI applications: it records each request as a trace, each step as an observation, and each quality signal as a score.
- **Why it exists / what problem it solves**: LLM apps are not a single database query or API call. They often involve prompts, tools, retrieval, model calls, retries, and non-deterministic output. Without structured traces, teams cannot explain why a response was slow, expensive, wrong, or different from yesterday.
- **Keywords**: traces, observations, scores, generations, sessions, token usage, latency
- **Related concepts**: [[llm-as-judge-evaluation]], [[prompt-version-management]], [[oltp-olap-split]], [[dspy-signatures]], [[react-agentic-loop]]
- **Depth**: 2/4
- **Last updated**: 2026-05-04
- **Source**: sources/repos/langfuse-langfuse

## Summary

Think of LLM observability as a flight recorder for an AI product. A normal log might say "request failed"; an LLM trace shows the user input, prompt version, model, tool calls, token usage, latency, cost, and output quality. A **trace** represents the whole user request or workflow. An **observation** is one step inside it, such as a span, generation, or tool call. A **score** records feedback or evaluation, such as relevance, correctness, or human approval.

This matters because LLM behavior changes with model versions, prompt edits, retrieval data, and user context. Observability turns those moving parts into queryable data, so a team can debug regressions, compare prompt versions, control cost, and measure quality over time.

## Example

A support chatbot answers a customer question incorrectly. With only application logs, you might know the endpoint returned HTTP 200. With LLM observability, you can inspect the trace and see:

1. The user asked about refund policy.
2. The retrieval step returned an outdated policy document.
3. The generation used prompt version 12 and model `gpt-4o`.
4. The call consumed 2,000 input tokens and took 4 seconds.
5. An evaluator attached a low correctness score.

The fix is no longer guesswork: update retrieval data, compare prompt version 12 against another version, and watch future correctness scores.

## Relationship to existing concepts

- [[llm-as-judge-evaluation]]: Automated evaluators need traces and observations as the raw material to score.
- [[prompt-version-management]]: Prompt versions become much more useful when each generation records which version produced it.
- [[oltp-olap-split]]: High-volume observability data needs analytical storage so teams can query millions of traces quickly.
- [[dspy-signatures]]: Structured task fields make LLM calls easier to log, inspect, and compare.
- [[react-agentic-loop]]: ReAct produces step-by-step tool-use trajectories that benefit from observability.

## Open questions

- Which LLM fields should be captured by default, and which should be redacted for privacy?
- How should teams balance full trace visibility against storage cost and sensitive-data risk?
