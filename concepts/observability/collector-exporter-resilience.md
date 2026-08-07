---
id: collector-exporter-resilience
title: Collector Exporter Resilience
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-opentelemetry-collector/
related:
  - collector-pipeline-architecture
  - otlp-vendor-neutral-telemetry-protocol
  - collector-extensions
  - collector-storage-extensions
tags:
  - observability
  - opentelemetry
  - collector
---

# Collector Exporter Resilience

- **One-sentence definition**: Exporter resilience uses bounded queues, batching, timeouts, storage, and selective retries to handle temporary downstream failures.
- **Why it exists / what problem it solves**: Telemetry backends can be slow or unavailable, so exporters need controlled ways to absorb bursts without blocking forever or retrying failures that cannot succeed.
- **Keywords**: queue, batch, retry, timeout, persistence, exporter
- **Related concepts**: [[collector-pipeline-architecture]], [[otlp-vendor-neutral-telemetry-protocol]], [[collector-extensions]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/opentelemetry-collector

## Summary

An exporter is the last step before telemetry leaves the Collector, so it must expect the destination to fail. A bounded queue absorbs a short burst but has a limit; batching sends fewer, larger requests; timeouts stop stuck requests. Optional persistent storage lets queued data survive a restart.

Retries are not a promise of delivery. The exporter retries failures that may recover, stops on permanent failures, and honors server-provided delays when it is being throttled.

## Example

If a telemetry backend returns HTTP 503 for two minutes, an exporter can queue a limited amount of data, batch it, and retry with backoff. If the queue fills, it drops additional data according to its configured policy instead of exhausting the Collector's memory.

## Relationship to existing concepts

- [[collector-pipeline-architecture]]: Resilience controls the final delivery step of a pipeline.
- [[otlp-vendor-neutral-telemetry-protocol]]: OTLP exporters apply these protections while delivering standard telemetry.
- [[collector-extensions]]: A storage extension can make an export queue durable across restarts.
- [[collector-storage-extensions]]: Storage extensions provide the persistent state used by durable queues.

## Open questions

- What loss budget is acceptable when the destination stays unavailable longer than the queue can hold?
- Which error classes should a custom exporter treat as permanent?
