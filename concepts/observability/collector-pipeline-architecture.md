---
id: collector-pipeline-architecture
title: OpenTelemetry Collector Pipeline Architecture
depth: 2
lab_status: scaffolded
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-opentelemetry-collector/
related:
  - telemetry-signal-model
  - otlp-vendor-neutral-telemetry-protocol
  - collector-component-factory-lifecycle
  - collector-pdata-ownership-at-fanout
  - collector-connectors
  - collector-extensions
  - collector-exporter-resilience
  - collector-configuration-providers
  - opentelemetry-collector-builder-distributions
  - llm-observability
  - microservices
  - collector-authentication-extensions
  - kubernetes-collector-placement-modes
  - ottl-declarative-telemetry-transformation
  - genai-observability-dashboard-abstraction
tags:
  - observability
  - opentelemetry
  - collector
---

# OpenTelemetry Collector Pipeline Architecture

- **One-sentence definition**: A Collector pipeline is a named route for one kind of telemetry: it accepts data, optionally changes it, and sends it to one or more destinations.
- **Why it exists / what problem it solves**: It lets operators change where telemetry goes and how it is handled without changing application instrumentation.
- **Keywords**: receiver, processor, exporter, signal, routing, pipeline
- **Related concepts**: [[telemetry-signal-model]], [[otlp-vendor-neutral-telemetry-protocol]], [[collector-component-factory-lifecycle]], [[collector-pdata-ownership-at-fanout]], [[collector-connectors]], [[collector-extensions]], [[collector-exporter-resilience]], [[collector-configuration-providers]], [[opentelemetry-collector-builder-distributions]], [[llm-observability]], [[microservices]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/opentelemetry-collector

## Summary

Think of a pipeline as a mailroom for one kind of telemetry. Receivers accept incoming traces, metrics, or logs; processors can filter, enrich, or batch them; exporters deliver the result. A pipeline has one signal type and a name, so one Collector can run separate routes for traces and metrics.

This separation keeps applications independent of operational choices. An application sends standard telemetry once; the Collector configuration decides whether to forward it, sample it, or send copies to multiple backends.

## Example

A `traces` pipeline can receive OTLP from several services, remove sensitive attributes in a processor, then export the cleaned data to both a debugging backend and long-term storage. No application code changes when the storage destination changes.

## Relationship to existing concepts

- [[telemetry-signal-model]]: Pipelines carry the traces, metrics, and logs defined by the signal model.
- [[otlp-vendor-neutral-telemetry-protocol]]: OTLP is a common way receivers accept and exporters send pipeline data.
- [[collector-component-factory-lifecycle]]: Factories create the components that form each pipeline.
- [[collector-pdata-ownership-at-fanout]]: Fan-out must protect shared pipeline data from unsafe mutation.
- [[collector-connectors]]: Connectors join one pipeline to another inside the Collector.
- [[collector-extensions]]: Extensions provide services around, rather than inside, the data path.
- [[collector-exporter-resilience]]: Exporters need bounded failure handling at the end of a pipeline.
- [[collector-configuration-providers]]: Configuration resolution declares and supplies settings for pipeline components.
- [[opentelemetry-collector-builder-distributions]]: A custom distribution determines which pipeline components are available.
- [[llm-observability]]: Collector pipelines can route AI application telemetry without vendor-specific application code.
- [[microservices]]: Pipelines collect evidence that helps debug work spanning many services.
- [[collector-authentication-extensions]]: Authentication extensions protect pipeline boundaries.
- [[kubernetes-collector-placement-modes]]: Placement decides where pipeline stages can access and process telemetry.
- [[ottl-declarative-telemetry-transformation]]: OTTL applies configurable transformations within a pipeline.
- [[genai-observability-dashboard-abstraction]]: A managed platform's domain-specific dashboard is one kind of destination this generic pipeline architecture can route the same telemetry toward.

## Open questions

- Which processing should happen centrally in the Collector, and which belongs in the application?
- When is a second pipeline clearer than adding another exporter to the first one?
