---
id: opentelemetry-foundations
title: "OpenTelemetry Foundations: Portable Telemetry for Distributed Systems"
description: A focused path for engineers who need to instrument, correlate, shape, and export telemetry across services without coupling applications to a specific observability backend.
---

## Overview

OpenTelemetry is a shared operating model for answering a practical production question: what happened inside a request, which service produced the evidence, and how can that evidence move between tools without losing its meaning? It separates application instrumentation from runtime configuration, then joins traces, metrics, logs, and baggage with common identity, schema, propagation, and transport rules.

This path starts with the data model before introducing the API and SDK boundary. It then establishes producer identity and field vocabulary, follows context across service boundaries, and finishes with delivery, metric cost control, and coherent distributed-trace sampling. The result is a complete foundation for operating microservices, AI backends, and other distributed applications.

For application-level uses of the telemetry data, continue with [LLM Observability](../concepts/llm-engineering/llm-observability.md). For the broader trade-offs behind distributed systems, continue with [Distributed Systems Foundations](../topics/distributed-systems-foundations.md).

**Estimated study time:** 6-8 hours
**Prerequisites:** Familiarity with HTTP requests and basic service-to-service communication. Experience with logs or metrics is helpful but not required.

---

## Concepts in Order

### 1. [Telemetry Signal Model](../concepts/observability/telemetry-signal-model.md)
Start by separating the jobs of traces, metrics, logs, and baggage. This gives you the vocabulary for deciding what evidence a production question requires instead of treating telemetry as one undifferentiated stream of events.

### 2. [OpenTelemetry API-SDK Separation](../concepts/observability/opentelemetry-api-sdk-separation.md)
Learn why libraries create telemetry through stable APIs while applications select SDK behavior such as sampling, processors, and exporters. This boundary is what makes instrumentation reusable and backend-neutral.

### 3. [Resource-Bound Telemetry Identity](../concepts/observability/resource-bound-telemetry-identity.md)
Add stable producer identity to every signal. Resource attributes distinguish the service, deployment environment, container, host, or cloud entity that emitted data from the request-level work being observed.

### 4. [Semantic Conventions as Telemetry Schema](../concepts/observability/semantic-conventions-as-telemetry-schema.md)
Standardize the meaning of common telemetry fields. Study this after resource identity so you can see how names such as `service.name` and HTTP attributes make dashboards and queries portable across services and backends.

### 5. [Context Propagation with Carriers](../concepts/observability/context-propagation-with-carriers.md)
Follow a trace through network boundaries. Learn how propagators inject trace context and baggage into HTTP headers or other carriers, then extract it on the receiving side to preserve one distributed operation.

### 6. [OTLP as a Vendor-Neutral Telemetry Protocol](../concepts/observability/otlp-vendor-neutral-telemetry-protocol.md)
Move from local instrumentation to a telemetry pipeline. OTLP defines how SDKs, collectors, and backends exchange the signals whose structure and meaning you established in the earlier steps.

### 7. [Metrics Views and Aggregations](../concepts/observability/metrics-views-and-aggregations.md)
Control the operational cost and shape of metrics without rewriting application instrumentation. Views teach you how to keep useful dimensions, remove high-cardinality attributes, and choose aggregations that support real alerts and dashboards.

### 8. [Consistent Probability Sampling](../concepts/observability/consistent-probability-sampling.md)
Finish with trace cost control that preserves investigative value. Coordinated randomness and thresholds keep retained distributed traces coherent, avoiding a collection of disconnected spans from independently sampled services.

### 9. [OpenTelemetry Collector Pipeline Architecture](../concepts/observability/collector-pipeline-architecture.md)
Turn portable telemetry into an operating data path: receive, process, and export each signal without changing application instrumentation.

### 10. [Collector Component Factory and Lifecycle](../concepts/observability/collector-component-factory-lifecycle.md)
Learn how one service constructs and safely operates the plug-in components that make up a Collector.

### 11. [Collector Configuration Providers and Resolution](../concepts/observability/collector-configuration-providers.md)
Keep deployment-specific values outside the binary while understanding how the Collector resolves configuration sources.

### 12. [OpenTelemetry Collector Connectors](../concepts/observability/collector-connectors.md)
Connect pipelines in-process when telemetry must be routed or converted into a different signal.

### 13. [Collector pdata Ownership at Fan-Out](../concepts/observability/collector-pdata-ownership-at-fanout.md)
Protect correctness and performance when one telemetry batch is sent down more than one branch.

### 14. [Collector Extensions](../concepts/observability/collector-extensions.md)
Add shared operational services such as health checks, authentication, and storage without putting them in the data path.

### 15. [Collector Exporter Resilience](../concepts/observability/collector-exporter-resilience.md)
Make the final delivery step survive short downstream failures with bounded, explicit trade-offs.

### 16. [Custom Distributions with the OpenTelemetry Collector Builder](../concepts/observability/opentelemetry-collector-builder-distributions.md)
Build a reproducible Collector binary that contains only the components and configuration providers an environment needs.

---

## What You'll Be Able to Do

- Choose the right telemetry signal for a request-level, trend-level, or event-level question
- Instrument libraries without tying them to one vendor or exporter
- Attach reliable service and deployment identity to telemetry
- Use shared field conventions so dashboards and alerts work across teams
- Preserve trace correlation through HTTP and other service boundaries
- Route telemetry through OTLP and collectors without rewriting applications
- Control metric cardinality and trace volume without losing the evidence needed for debugging
