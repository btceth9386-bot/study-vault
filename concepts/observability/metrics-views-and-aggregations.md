---
id: metrics-views-and-aggregations
title: Metrics Views and Aggregations
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-opentelemetry-specification/
related:
  - opentelemetry-api-sdk-separation
  - telemetry-signal-model
  - resource-bound-telemetry-identity
  - llm-observability
tags:
  - observability
  - opentelemetry
---

# Metrics Views and Aggregations

- **One-sentence definition**: Metrics views and aggregations let an SDK reshape raw measurements into the names, attributes, buckets, and summaries exported to a backend.
- **Why it exists / what problem it solves**: Instrumentation should describe what happened once, while operations teams need control over cost, cardinality, and reporting without repeatedly changing application code.
- **Keywords**: metrics, view, aggregation, histogram, cardinality, exporter
- **Related concepts**: [[opentelemetry-api-sdk-separation]], [[telemetry-signal-model]], [[resource-bound-telemetry-identity]], [[llm-observability]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/opentelemetry-specification

## Summary

An instrument records a raw measurement, such as a request duration. A view is an SDK rule that decides how that measurement should appear after collection: it can rename it, select attributes, change histogram boundaries, choose an aggregation, or drop it. The application keeps its instrumentation while the exported shape changes.

This is a practical safety valve. High-cardinality attributes such as user IDs can make metric storage explode, while a well-chosen histogram preserves useful latency trends at a manageable cost.

## Example

An API records `http.server.duration` with `http.route`, `status_code`, and `user.id`. A production view keeps the route and status code, removes `user.id`, and uses latency buckets suited to the service objective. The team gets an actionable latency chart without creating one metric series per user.

## Relationship to existing concepts

- [[opentelemetry-api-sdk-separation]]: Views are SDK configuration, not a responsibility of instrumentation API callers.
- [[telemetry-signal-model]]: Views shape the metrics branch of the broader signal model.
- [[resource-bound-telemetry-identity]]: Resource attributes identify the service even when views filter measurement attributes.
- [[llm-observability]]: Metric views can control the cost and usefulness of model latency, token, and tool-call measurements.

## Open questions

- Which attributes must remain for useful alerting, and which create unbounded cardinality?
- How should histogram buckets be chosen from a service-level objective rather than guessed?
