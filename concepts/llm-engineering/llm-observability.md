---
id: llm-observability
title: LLM Observability
depth: 2
lab_status: scaffolded
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/langfuse-langfuse
  - sources/repos/open-telemetry-semantic-conventions-genai/
related:
  - llm-as-judge-evaluation
  - prompt-version-management
  - oltp-olap-split
  - dspy-signatures
  - react-agentic-loop
  - actionable-side-information
  - langgraph-human-in-the-loop-interrupts
  - devops-agent-topology-context
  - autonomous-incident-investigation
  - proactive-incident-prevention-loop
  - opentelemetry-api-sdk-separation
  - telemetry-signal-model
  - context-propagation-with-carriers
  - resource-bound-telemetry-identity
  - semantic-conventions-as-telemetry-schema
  - otlp-vendor-neutral-telemetry-protocol
  - metrics-views-and-aggregations
  - consistent-probability-sampling
  - collector-pipeline-architecture
  - genai-operation-span-taxonomy
  - genai-streaming-telemetry-lifecycle
tags:
  - llm-engineering
  - observability
  - analytics
---

# LLM Observability

- **One-sentence definition**: LLM observability is structured monitoring for AI applications: it records each request as a trace, each step as an observation, and each quality signal as a score.
- **Why it exists / what problem it solves**: LLM apps are not a single database query or API call. They often involve prompts, tools, retrieval, model calls, retries, and non-deterministic output. Without structured traces, teams cannot explain why a response was slow, expensive, wrong, or different from yesterday.
- **Keywords**: traces, observations, scores, generations, sessions, token usage, latency
- **Related concepts**: [[llm-as-judge-evaluation]], [[prompt-version-management]], [[oltp-olap-split]], [[dspy-signatures]], [[react-agentic-loop]], [[actionable-side-information]], [[langgraph-human-in-the-loop-interrupts]], [[devops-agent-topology-context]], [[autonomous-incident-investigation]], [[proactive-incident-prevention-loop]]
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
- [[actionable-side-information]]: Trace data becomes more useful for optimization when it is distilled into feedback the reflection model can act on.
- [[langgraph-human-in-the-loop-interrupts]]: Paused graph runs expose human decisions and state snapshots that should be traceable.
- [[devops-agent-topology-context]]: Operational telemetry is easier to interpret when it is attached to services, dependencies, and request paths.
- [[autonomous-incident-investigation]]: Incident agents depend on observability data as their evidence base.
- [[proactive-incident-prevention-loop]]: Prevention recommendations need historical operational signals to find recurring failure modes.
- [[opentelemetry-api-sdk-separation]]: OpenTelemetry keeps AI instrumentation independent from the runtime exporter and backend.
- [[telemetry-signal-model]]: Traces, metrics, logs, and baggage provide the general observability model beneath LLM-specific data.
- [[context-propagation-with-carriers]]: Context propagation keeps an AI workflow trace intact across services and tool calls.
- [[resource-bound-telemetry-identity]]: Resource attributes identify the service and deployment that emitted a trace or metric.
- [[semantic-conventions-as-telemetry-schema]]: Shared attribute names keep telemetry portable and comparable across systems.
- [[otlp-vendor-neutral-telemetry-protocol]]: OTLP carries LLM telemetry to collectors and backends without application-level vendor lock-in.
- [[metrics-views-and-aggregations]]: Views control the cost and shape of exported LLM latency and token metrics.
- [[consistent-probability-sampling]]: Consistent sampling preserves complete distributed traces while limiting observability cost.
- [[collector-pipeline-architecture]]: Collector pipelines route AI telemetry to one or more backends without changing application instrumentation.

## Open questions

- Which LLM fields should be captured by default, and which should be redacted for privacy?
- How should teams balance full trace visibility against storage cost and sensitive-data risk?

## OpenTelemetry GenAI refinements

OpenTelemetry adds a portable way to break an AI request into spans for inference, retrieval, memory, and tool work. For streaming responses, one inference span stays open until the final chunk so it can include both time to first chunk and final usage data.

Content capture should be opt-in. Prompts, responses, tool arguments, retrieved documents, and memory records can expose private data or create large telemetry payloads; ordinary operational fields remain useful even when that content is omitted.

- [[genai-operation-span-taxonomy]]: Supplies distinct boundaries for the operations inside an AI request.
- [[genai-streaming-telemetry-lifecycle]]: Preserves both perceived responsiveness and completed-stream facts.
