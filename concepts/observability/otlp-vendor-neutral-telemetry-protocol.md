---
id: otlp-vendor-neutral-telemetry-protocol
title: OTLP as a Vendor-Neutral Telemetry Protocol
depth: 2
lab_status: scaffolded
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-opentelemetry-specification/
related:
  - opentelemetry-api-sdk-separation
  - telemetry-signal-model
  - semantic-conventions-as-telemetry-schema
  - llm-observability
  - collector-pipeline-architecture
  - collector-exporter-resilience
  - opentelemetry-collector-builder-distributions
  - genai-observability-dashboard-abstraction
tags:
  - observability
  - opentelemetry
  - distributed-systems
---

# OTLP as a Vendor-Neutral Telemetry Protocol

- **One-sentence definition**: OTLP is OpenTelemetry's standard wire protocol for moving traces, metrics, and logs between SDKs, collectors, and backends.
- **Why it exists / what problem it solves**: Instrumentation stays portable only when exported telemetry also has a common encoding, endpoint model, and transport behavior.
- **Keywords**: OTLP, gRPC, HTTP, protobuf, collector, exporter
- **Related concepts**: [[opentelemetry-api-sdk-separation]], [[telemetry-signal-model]], [[semantic-conventions-as-telemetry-schema]], [[llm-observability]], [[collector-pipeline-architecture]], [[collector-exporter-resilience]], [[opentelemetry-collector-builder-distributions]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/opentelemetry-specification

## Summary

OTLP is the delivery language for OpenTelemetry data. An SDK encodes telemetry and sends it to a collector or backend over supported transports such as gRPC or HTTP with protobuf. The receiving system can then process, route, transform, or store the data.

OTLP standardizes transport, while semantic conventions standardize meaning. That distinction matters: two systems can exchange bytes successfully yet still disagree about what an attribute means unless they share the same schema.

## Example

A Python service sends traces over OTLP/gRPC to an OpenTelemetry Collector. The collector batches them and forwards the same trace data to a hosted backend. Later, the team changes backends by editing collector configuration, not by rewriting instrumentation in every service.

## Relationship to existing concepts

- [[opentelemetry-api-sdk-separation]]: The SDK side of the split uses OTLP as one export option.
- [[telemetry-signal-model]]: OTLP carries the different telemetry signals through one family of protocol definitions.
- [[semantic-conventions-as-telemetry-schema]]: Shared schemas make OTLP payloads useful across tools.
- [[llm-observability]]: LLM traces can travel through a collector without coupling the application to a monitoring vendor.
- [[collector-pipeline-architecture]]: Collector pipelines receive and export OTLP telemetry.
- [[collector-exporter-resilience]]: OTLP delivery needs queues and retries when a backend is unavailable.
- [[opentelemetry-collector-builder-distributions]]: A custom distribution must include OTLP modules to support this protocol.
- [[genai-observability-dashboard-abstraction]]: CloudWatch's generative-AI observability page presents OTLP-shaped telemetry through an agent-specific view without changing the underlying vendor-neutral transport.

## Open questions

- When is a direct SDK-to-backend OTLP connection sufficient, and when does a collector add needed control?
- Which reliability settings are needed when an OTLP destination is temporarily unavailable?
