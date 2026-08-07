---
id: collector-extensions
title: OpenTelemetry Collector Extensions
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-opentelemetry-collector/
related:
  - collector-component-factory-lifecycle
  - collector-pipeline-architecture
  - collector-exporter-resilience
tags:
  - observability
  - opentelemetry
  - collector
---

# OpenTelemetry Collector Extensions

- **One-sentence definition**: Extensions are lifecycle-managed support services for a Collector that work beside, rather than inside, telemetry pipelines.
- **Why it exists / what problem it solves**: They make shared operational capabilities reusable without pretending that diagnostics, authentication, or storage are telemetry transformations.
- **Keywords**: extension, health check, authentication, storage, middleware, lifecycle
- **Related concepts**: [[collector-component-factory-lifecycle]], [[collector-pipeline-architecture]], [[collector-exporter-resilience]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/opentelemetry-collector

## Summary

Extensions are the Collector's supporting cast. They can expose health checks, provide authentication, host diagnostics, or offer storage, but they do not receive, process, or export traces, metrics, or logs as part of a pipeline.

The service manages extensions through the same lifecycle contract as other components. That lets a pipeline use a shared service for its whole lifetime without embedding the service inside each processor or exporter.

## Example

A storage extension provides durable space for an exporter's sending queue. The exporter uses it when a backend is unavailable, while a health-check extension separately reports whether the Collector is running.

## Relationship to existing concepts

- [[collector-component-factory-lifecycle]]: Extensions are created, started, and shut down through the common component contract.
- [[collector-pipeline-architecture]]: Extensions support pipelines while remaining outside their data path.
- [[collector-exporter-resilience]]: A storage extension can preserve queued exports across restarts.

## Open questions

- Which shared capability belongs in an extension rather than an exporter or receiver?
- What should happen when a required extension fails before pipelines start?
