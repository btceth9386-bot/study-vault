---
id: opentelemetry-foundations
title: "OpenTelemetry Foundations: Portable Telemetry for Distributed Systems"
description: A focused path for engineers who need to instrument, correlate, shape, and export telemetry across services without coupling applications to a specific observability backend.
---

## Overview

OpenTelemetry is a shared operating model for answering a practical production question: what happened inside a request, which service produced the evidence, and how can that evidence move between tools without losing its meaning? It separates application instrumentation from runtime configuration, then joins traces, metrics, logs, and baggage with common identity, schema, propagation, and transport rules.

This path starts with the data model before introducing the API and SDK boundary. It then establishes producer identity and field vocabulary, follows context across service boundaries, and moves into Collector deployment, transformation, durability, and fleet operations. The result is a complete foundation for operating microservices, AI backends, and other distributed applications.

For application-level uses of the telemetry data, continue with [LLM Observability](../concepts/llm-engineering/llm-observability.md). For the broader trade-offs behind distributed systems, continue with [Distributed Systems Foundations](../topics/distributed-systems-foundations.md).

**Estimated study time:** 10-12 hours
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

### 16. [OTTL Declarative Telemetry Transformation](../concepts/observability/ottl-declarative-telemetry-transformation.md)
Apply consistent filtering, redaction, enrichment, and routing policies in Collector configuration instead of duplicating them across services. Study this after the pipeline structure so it is clear where those policies run.

### 17. [Collector Resource Detection and Enrichment](../concepts/observability/collector-resource-detection-and-enrichment.md)
Enrich portable application telemetry with the cloud, host, container, and Kubernetes identity that is only available where the Collector runs.

### 18. [Observer-Driven Dynamic Receivers](../concepts/observability/observer-driven-dynamic-receivers.md)
Discover short-lived endpoints and create or stop receivers as workloads change. This extends the component lifecycle from static configuration to dynamic environments.

### 19. [Kubernetes Collector Placement Modes](../concepts/observability/kubernetes-collector-placement-modes.md)
Choose node-local agents, centralized gateways, or a combined deployment based on what telemetry must be observed locally and where shared processing belongs.

### 20. [Collector Authentication Extensions](../concepts/observability/collector-authentication-extensions.md)
Secure the pipeline boundaries with reusable server and client authentication services rather than embedding credential logic in every receiver and exporter.

### 21. [Collector Storage Extensions](../concepts/observability/collector-storage-extensions.md)
Add durable, scoped state for queues and checkpoints so components can preserve work across restarts and downstream outages.

### 22. [OpAMP-Supervised Collector Fleet Management](../concepts/observability/opamp-supervised-collector-fleet-management.md)
Operate a large Collector fleet through a managed path for remote configuration, lifecycle control, and health reporting.

### 23. [Metadata-Driven Component Stability](../concepts/observability/metadata-driven-component-stability.md)
Evaluate component maturity, ownership, supported signals, and distribution suitability through machine-readable metadata.

### 24. [Custom Distributions with the OpenTelemetry Collector Builder](../concepts/observability/opentelemetry-collector-builder-distributions.md)
Finish by building a reproducible Collector binary from the components and configuration providers whose capabilities and stability you have evaluated.

## Semantic Convention Evolution

- [Semantic Convention Model as Source of Truth](../concepts/observability/semantic-convention-model-as-source-of-truth.md): Start with the machine-readable definition that drives telemetry artifacts.
- [Semantic Attribute Registry Reuse](../concepts/observability/semantic-attribute-registry-reuse.md): Reuse shared attribute definitions across technology domains.
- [Telemetry Attribute Requirement Levels](../concepts/observability/telemetry-attribute-requirement-levels.md): Decide which fields are mandatory, conditional, recommended, or opt-in.
- [Semantic Convention Stability Lifecycle](../concepts/observability/semantic-convention-stability-lifecycle.md): Understand the compatibility promise behind a convention's maturity label.
- [Telemetry Schema Migration Mappings](../concepts/observability/telemetry-schema-migration-mappings.md): Translate telemetry safely while producers and consumers upgrade at different speeds.
- [Semantic Convention Validation and Generation](../concepts/observability/semantic-convention-validation-and-generation.md): Check the model and derive synchronized documentation and artifacts.
- [Domain-Owned Semantic Conventions](../concepts/observability/domain-owned-semantic-conventions.md): Balance technology-specific expertise with ecosystem-wide review.

## GenAI Telemetry

- [GenAI Operation Span Taxonomy](../concepts/observability/genai-operation-span-taxonomy.md): Separate inference, retrieval, memory, and tool work so a trace can explain an AI request.
- [Agentic Workflow Span Hierarchy](../concepts/observability/agentic-workflow-span-hierarchy.md): Nest workflow, agent, plan, and operation spans into one causal story.
- [GenAI Streaming Telemetry Lifecycle](../concepts/observability/genai-streaming-telemetry-lifecycle.md): Preserve both time to first chunk and final response facts on one stream span.
- [Cross-Provider GenAI Telemetry Refinements](../concepts/observability/cross-provider-genai-telemetry-refinements.md): Keep a portable core while recording genuinely provider-specific details.
- [MCP Client-Server Trace Correlation](../concepts/observability/mcp-client-server-trace-correlation.md): Follow an MCP method from client to server across stdio or HTTP.
- [LLM Observability](../concepts/llm-engineering/llm-observability.md): Apply trace, metric, and content-capture practices to complete AI applications.

---

## What You'll Be Able to Do

- Choose the right telemetry signal for a request-level, trend-level, or event-level question
- Instrument libraries without tying them to one vendor or exporter
- Attach reliable service and deployment identity to telemetry
- Use shared field conventions so dashboards and alerts work across teams
- Preserve trace correlation through HTTP and other service boundaries
- Route telemetry through OTLP and collectors without rewriting applications
- Control metric cardinality and trace volume without losing the evidence needed for debugging
- Deploy Collectors across Kubernetes and dynamic environments with the right placement and discovery model
- Apply shared transformation, authentication, storage, and fleet-management policies to production telemetry
- Choose Collector components and distributions based on explicit stability and ownership metadata
