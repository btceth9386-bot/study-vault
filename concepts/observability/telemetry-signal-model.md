---
id: telemetry-signal-model
title: Telemetry Signal Model
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-opentelemetry-specification/
related:
  - opentelemetry-api-sdk-separation
  - context-propagation-with-carriers
  - resource-bound-telemetry-identity
  - semantic-conventions-as-telemetry-schema
  - semantic-convention-model-as-source-of-truth
  - telemetry-attribute-requirement-levels
  - otlp-vendor-neutral-telemetry-protocol
  - llm-observability
  - collector-pipeline-architecture
  - collector-pdata-ownership-at-fanout
  - collector-connectors
  - ottl-declarative-telemetry-transformation
  - genai-streaming-telemetry-lifecycle
tags:
  - observability
  - opentelemetry
---

# Telemetry Signal Model

- **One-sentence definition**: The telemetry signal model gives traces, metrics, logs, and baggage different jobs while letting them describe the same running system.
- **Why it exists / what problem it solves**: A latency question, a capacity trend, an error event, and request-scoped metadata need different data shapes; forcing them into one signal makes analysis unclear and expensive.
- **Keywords**: traces, metrics, logs, baggage, correlation, observability
- **Related concepts**: [[opentelemetry-api-sdk-separation]], [[context-propagation-with-carriers]], [[resource-bound-telemetry-identity]], [[semantic-conventions-as-telemetry-schema]], [[semantic-convention-model-as-source-of-truth]], [[telemetry-attribute-requirement-levels]], [[otlp-vendor-neutral-telemetry-protocol]], [[llm-observability]], [[collector-pipeline-architecture]], [[collector-pdata-ownership-at-fanout]], [[collector-connectors]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/opentelemetry-specification

## Summary

Telemetry is not one giant log file. A trace follows one request through its work, a metric summarizes measurements over time, and a log records an individual event. Baggage is small context that can travel with a request so downstream work can use the same business metadata.

The signals remain useful together because they share correlation and identity mechanisms. A trace ID can connect a log to a request, while resource metadata explains which service emitted both the trace and the metric.

## Example

For a slow checkout, a trace shows which service spent two seconds on a database call. A metric shows that database latency has been rising all hour, and logs show a connection-pool timeout. Each signal answers a different part of the same investigation.

## Relationship to existing concepts

- [[opentelemetry-api-sdk-separation]]: APIs and SDKs provide the common way to create and process these signals.
- [[context-propagation-with-carriers]]: Propagation keeps trace context and baggage connected across service boundaries.
- [[resource-bound-telemetry-identity]]: Resources identify the producer behind every signal.
- [[semantic-conventions-as-telemetry-schema]]: Shared field names make signals understandable across tools.
- [[semantic-convention-model-as-source-of-truth]]: The model defines the signal-specific fields from which artifacts are derived.
- [[telemetry-attribute-requirement-levels]]: Requirement levels specify which signal fields are expected in each context.
- [[otlp-vendor-neutral-telemetry-protocol]]: OTLP carries signals between SDKs, collectors, and backends.
- [[llm-observability]]: LLM traces and evaluation scores are a domain-specific use of this general model.
- [[collector-pipeline-architecture]]: Collector pipelines move each signal through configurable routes.
- [[collector-pdata-ownership-at-fanout]]: Ownership rules protect signal batches when pipelines branch.
- [[collector-connectors]]: Connectors can route or convert telemetry signals between pipelines.
- [[ottl-declarative-telemetry-transformation]]: OTTL reads and changes signal fields through context-aware paths.
- [[genai-streaming-telemetry-lifecycle]]: Streaming uses spans for the complete operation, events for chunk details, and metrics for fleet-wide latency.

## Open questions

- Which signals provide enough evidence for a given service without creating unnecessary storage cost?
- How should trace IDs be recorded in logs that are written outside an instrumentation library?
