---
id: agentcore-session-trace-span-hierarchy
title: AgentCore Session-Trace-Span Hierarchy
depth: 2
lab_status: not-started
last_reviewed: 2026-09-26
review_due: 2026-09-29
sources:
  - sources/papers/bedrock-agentcore-observability-evals/
related:
  - agentcore-managed-service-telemetry-defaults
  - genai-observability-dashboard-abstraction
  - agentcore-external-agent-observability-onboarding
  - agentic-workflow-span-hierarchy
  - genai-operation-span-taxonomy
  - llm-observability
tags:
  - llm-engineering
  - observability
  - aws
  - agentcore
  - tracing
---

# AgentCore Session-Trace-Span Hierarchy

- **One-sentence definition**: Amazon Bedrock AgentCore models agent observability as a three-tier hierarchy — a session (a complete user-agent interaction context) contains multiple traces (one request-response execution path, possibly spanning multiple agents), and each trace contains multiple spans (a single measurable operation such as a tool call or model inference).
- **Why it exists / what problem it solves**: A single agent conversation can involve many turns, multiple cooperating agents, and repeated tool or model calls. Flat logs cannot support drilling from "how is overall usage trending" down to "which specific tool call caused the latency spike." Naming three distinct tiers gives each level of analysis a clear scope, so troubleshooting can proceed from coarse to fine without manually reconstructing causality from unstructured logs.
- **Keywords**: session, trace, span, observability hierarchy, AgentCore, request-response cycle
- **Related concepts**: [[agentcore-managed-service-telemetry-defaults]], [[genai-observability-dashboard-abstraction]], [[agentic-workflow-span-hierarchy]], [[genai-operation-span-taxonomy]], [[llm-observability]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: sources/papers/bedrock-agentcore-observability-evals/

## Summary

Think of the hierarchy as three nested zoom levels on the same conversation. A **session** is the whole story: one user's complete back-and-forth with an agent, from the first message to the last. Inside that story, each turn where the agent actually does something — reads a question, calls a tool, produces an answer — is a **trace**: one request-response cycle, which can itself fan out to other agents. Inside a trace, every individual step the agent takes is a **span**: one tool call, one model inference, one discrete unit of work, each with its own start time, end time, and parent-child position in the trace. Zooming out from spans to traces to sessions lets an engineer ask progressively broader questions — "why was this one tool call slow," "why did this request fail," "how is this user's overall experience trending" — using the same underlying data at different resolutions.

## Example

A support agent session starts when a customer asks about a delayed order. That single session contains three traces: the customer's first question and its answer, a follow-up question about a refund, and a final "thanks" exchange. The refund trace itself contains four spans: a span for the model deciding to look up the order, a span for the tool call that queries the order database, a span for the model deciding to check the refund policy, and a span for generating the final response. If the customer complains the refund answer was slow, an engineer opens that one trace, sees the database-lookup span took four seconds, and knows exactly where to look — without reading the whole session's raw logs.

## Relationship to existing concepts

- [[agentcore-managed-service-telemetry-defaults]]: Describes which tier of this hierarchy is emitted automatically for which AgentCore resource, and which requires instrumentation.
- [[genai-observability-dashboard-abstraction]]: The CloudWatch generative-AI observability view is the interface that renders this session/trace/span data.
- [[agentcore-external-agent-observability-onboarding]]: Agents hosted outside AgentCore Runtime must be instrumented to populate this same hierarchy.
- [[agentic-workflow-span-hierarchy]]: Describes the general OpenTelemetry span-nesting model within a single trace; this concept is AWS's platform-specific naming and data model layered on top of that standard, spanning session and trace tiers as well.
- [[genai-operation-span-taxonomy]]: Supplies the underlying operation-boundary definitions (inference, tool, retrieval) that AgentCore's span classification draws on.
- [[llm-observability]]: This concept's trace/observation/score model is the general pattern; AgentCore's session/trace/span naming is one platform's concrete implementation of it for its managed services.

## Open questions

- How does AgentCore correlate spans across agent-to-agent calls within one trace when multiple agents are involved?
- At what session length or trace volume does browsing this hierarchy in the CloudWatch console stop being practical, and programmatic querying become necessary?
