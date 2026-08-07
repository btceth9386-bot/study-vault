---
id: collector-connectors
title: OpenTelemetry Collector Connectors
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-opentelemetry-collector/
related:
  - collector-pipeline-architecture
  - collector-component-factory-lifecycle
  - telemetry-signal-model
tags:
  - observability
  - opentelemetry
  - collector
---

# OpenTelemetry Collector Connectors

- **One-sentence definition**: A connector sends data out of one Collector pipeline and receives it into another, sometimes changing the signal type on the way.
- **Why it exists / what problem it solves**: It supports in-process routing, aggregation, and signal conversion without an external service or an oversized pipeline.
- **Keywords**: connector, receiver, exporter, routing, transformation, pipeline
- **Related concepts**: [[collector-pipeline-architecture]], [[collector-component-factory-lifecycle]], [[telemetry-signal-model]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/opentelemetry-collector

## Summary

A normal exporter ends a pipeline by sending data outside the Collector. A connector is different: it is an exporter from the first pipeline's point of view and a receiver from the next pipeline's point of view. This makes the hand-off visible in configuration and keeps related stages separate.

Because the two sides can use different signal types, a connector can turn trace information into metrics or route selected data into a specialized pipeline.

## Example

A connector receives traces from an application pipeline, calculates request-duration metrics, and passes those metrics into a metrics pipeline. The metrics pipeline can then apply its own processors and exporters without mixing that work into trace delivery.

## Relationship to existing concepts

- [[collector-pipeline-architecture]]: A connector is the explicit bridge between two pipelines.
- [[collector-component-factory-lifecycle]]: Connector factories create both sides of this dual-role component.
- [[telemetry-signal-model]]: Connectors can route or convert among telemetry signal types.

## Open questions

- Is a connector clearer than a processor for this transformation?
- How should teams prevent connector graphs from becoming hard to follow?
