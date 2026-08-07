This document explains the shared module dependencies and the data transformation pipeline used by the Datadog integration components (`datadogexporter`, `datadogreceiver`, `datadogconnector`). It covers the internal utility modules, dependencies on Datadog Agent packages (e.g., config, logging, tagging, forwarding, obfuscation, serialization), OTLP mapping implementations, and the complete data flow from OpenTelemetry Protocol (OTLP) format to Datadog's native formats.

For details on the component-specific architecture, see [Datadog Components Architecture]().

## Overview of Shared Modules

The Datadog integration is architected around two shared modules that provide common functionality consumed by exporter, receiver, and connector components.

### Module Hierarchy

```mermaid
graph TB
    subgraph "Datadog Integration Components"
        DDE["datadogexporter<br/>exporter/datadogexporter"]
        DDR["datadogreceiver<br/>receiver/datadogreceiver"]
        DDC["datadogconnector<br/>connector/datadogconnector"]
    end

    subgraph "Shared Internal Modules"
        INTERNAL_DD["internal/datadog<br/>Internal utilities"]
        PKG_DD["pkg/datadog<br/>Public package"]
    end

    subgraph "External Dependencies"
        DD_AGENT["Datadog Agent Packages<br/>github.com/DataDog/datadog-agent"]
        DD_PAYLOAD["Agent Payload<br/>github.com/DataDog/agent-payload/v5"]
        DD_API["Datadog API Client<br/>github.com/DataDog/datadog-api-client-go/v2"]
        DD_SKETCHES["Sketches Library<br/>github.com/DataDog/sketches-go"]
    end

    DDE --> INTERNAL_DD
    DDE --> PKG_DD
    DDR --> INTERNAL_DD
    DDR --> PKG_DD
    DDC --> DDE
    DDC --> PKG_DD

    DDE --> DD_AGENT
    DDE --> DD_PAYLOAD
    DDE --> DD_API

    DDR --> DD_AGENT
    DDR --> DD_PAYLOAD
    DDR --> DD_SKETCHES

    INTERNAL_DD --> DD_AGENT
    PKG_DD --> DD_AGENT
```

This diagram highlights how Datadog integration components depend on shared internal utilities, public `pkg/datadog` packages, and core Datadog Agent libraries for telemetry enrichment, serialization, and communication.

Sources: [exporter/datadogexporter/go.mod:6-30](), [connector/datadogconnector/go.mod:6-7](), [receiver/datadogreceiver/go.mod:6-20]().

### internal/datadog Module

The `internal/datadog` module encapsulates internal helpers and utilities specifically tailored for Datadog integration. It provides platform-specific metadata detection (for AWS, GCP, Kubernetes), hostname validation, and utilities closely integrated with the Datadog Agent ecosystem.

Key characteristics:

| Functionality | Details | Usage |
|---------------|---------|-------|
| **Platform Metadata Detection** | Integrates with AWS SDK, GCP detectors, and Kubernetes config internally | Used to enrich telemetry with cloud and orchestrator metadata |
| **Hostname Validation** | Utilizes Datadog Agent's hostname validation logic | Ensures consistent resource identity across pipelines |
| **Cloud Providers Support** | AWS ECS utilities and Kubernetes config detection | Leverages internal/ aws/ecsutil and internal/k8sconfig |

This module is not exposed publicly and serves as a foundation for higher-level components.

Sources: [internal/datadog/go.mod:7-21](), [exporter/datadogexporter/go.mod:29-29](), [receiver/datadogreceiver/go.mod:16-16]().

### pkg/datadog Module

The `pkg/datadog` module is a public shared package that contains common configurations, constants, and helper types used across Datadog receiver, exporter, and connector components. It covers configuration domains for metrics, traces, and host metadata.

Representative files:

| File | Purpose | Lines |
|-------|---------|-------|
| `pkg/datadog/config/config.go` | Base configuration structures and helpers | [pkg/datadog/config/config.go:1-50]() |
| `pkg/datadog/config/metrics.go` | Datadog metrics-specific configuration | [pkg/datadog/config/metrics.go:1-40]() |
| `pkg/datadog/config/traces.go` | Trace-specific configuration and constants | [pkg/datadog/config/traces.go:1-40]() |
| `pkg/datadog/config/host.go` | Configuration for host metadata enrichment | [pkg/datadog/config/host.go:1-30]() |

This public package provides reusable abstractions for other components to build upon.

Sources: [pkg/datadog/go.mod:1-20](), [exporter/datadogexporter/go.mod:30-30](), [connector/datadogconnector/go.mod:7-7](), [receiver/datadogreceiver/go.mod:19-19]().

## Datadog Agent Package Dependencies

Datadog components rely heavily on the official Datadog Agent packages for internal data representation, protocol handling, serialization, and enrichment capabilities.

### OpenTelemetry Mapping Packages

The conversion from OpenTelemetry's data model (pdata) to Datadog's native internal representations is handled by specialized mapping packages, mostly provided by the Datadog Agent.

```mermaid
graph LR
    subgraph "OTLP Data Types"
        OTLP_METRICS["pdata.Metrics"]
        OTLP_TRACES["pdata.Traces"]
        OTLP_LOGS["pdata.Logs"]
    end

    subgraph "Mapping Packages"
        MAP_METRICS["pkg/opentelemetry-mapping-go/otlp/metrics"]
        MAP_ATTRIBUTES["pkg/opentelemetry-mapping-go/otlp/attributes"]
        MAP_INFRA["pkg/opentelemetry-mapping-go/inframetadata"]
    end

    subgraph "Datadog Formats"
        DD_METRICS["Datadog Metrics"]
        DD_TRACES["Datadog Traces"]
        DD_INFRA["Datadog Infrastructure Metadata"]
    end

    OTLP_METRICS --> MAP_METRICS
    OTLP_TRACES --> MAP_ATTRIBUTES

    MAP_METRICS --> DD_METRICS
    MAP_ATTRIBUTES --> DD_TRACES
    MAP_INFRA --> DD_INFRA
```

The mapping packages:

| Package | Responsibility | Used By |
|---------|----------------|---------|
| `otlp/metrics` | Converts pdata.Metrics to Datadog metrics representations | `datadogexporter` |
| `otlp/attributes` | Maps OTLP attributes to Datadog tags for traces and metrics | `datadogexporter` and `datadogreceiver` |
| `inframetadata` | Enrich metrics and traces with host and orchestrator metadata | `datadogexporter` and `internal/datadog` |

These packages implement core translation logic tuned for Datadog's telemetry data formats.

Sources: [exporter/datadogexporter/go.mod:18-20](), [receiver/datadogreceiver/go.mod:48-49](), [internal/datadog/go.mod:7-8]().

### Protocol and Serialization Packages

The Datadog components utilize packages mainly from the agent repository to handle protocol payloads, compression, and data obfuscation:

| Package | Purpose | Components Using |
|---------|---------|------------------|
| `agent-payload/v5` | Protocol buffer definitions and serialization of agent payloads | Exporter, Receiver, Connector |
| `pkg/proto` | Protobuf message definitions for traces and metrics | Exporter, Receiver, Connector |
| `pkg/obfuscate` | Obfuscation of sensitive data in trace spans | `datadogreceiver` |
| `pkg/trace/stats` | Span statistics computation | `datadogreceiver` |
| `pkg/trace/traceutil` | Trace utilities for manipulation and enhancement | `datadogreceiver` |
| `comp/serializer/logscompression` | Compression for logs payloads (gzip, zstd) | `datadogexporter` |
| `comp/trace/compression/impl-gzip` | Gzip compression for trace payloads | `datadogexporter` |

These dependencies provide foundational agent protocol capabilities and data sanitation.

Sources: [exporter/datadogexporter/go.mod:6-25](), [receiver/datadogreceiver/go.mod:6-11]().

## Data Flow Architecture

This section describes the end-to-end data flow from incoming OTLP signals through transformation layers to outgoing Datadog native payloads.

### Complete Data Flow Pipeline

```mermaid
graph TB
    subgraph "Input Stage"
        OTLP_IN["OTLP Data<br/>pdata.Traces / Metrics / Logs"]
    end

    subgraph "Internal Utilities"
        COREINTERNAL["internal/coreinternal<br/>Core utilities"]
        INTERNAL_DD["internal/datadog<br/>Datadog-specific helpers"]
    end

    subgraph "Mapping & Enrichment"
        ATTR_MAPPING["attribute mapping<br/>OTLP → Datadog tags"]
        METRIC_MAPPING["metric mapping<br/>OTLP → Datadog metrics"]
        TRACE_MAPPING["trace span processing<br/>OTLP → Datadog traces"]
        INFRA_META["inframetadata enrichment<br/>host/container metadata"]
        HOSTNAME["hostname resolution"]
    end

    subgraph "Serialization"
        PROTOBUF["protobuf serialization<br/>agent-payload/v5"]
        COMPRESSION["compression<br/>gzip / zstd"]
    end

    subgraph "Output"
        HTTP_CLIENT["HTTP Client<br/>confighttp"]
        DATADOG_API["Datadog API endpoint"]
    end

    OTLP_IN --> COREINTERNAL
    COREINTERNAL --> INTERNAL_DD

    INTERNAL_DD --> ATTR_MAPPING
    INTERNAL_DD --> METRIC_MAPPING
    INTERNAL_DD --> TRACE_MAPPING

    ATTR_MAPPING --> INFRA_META
    METRIC_MAPPING --> INFRA_META
    TRACE_MAPPING --> INFRA_META

    INFRA_META --> HOSTNAME
    HOSTNAME --> PROTOBUF
    PROTOBUF --> COMPRESSION
    COMPRESSION --> HTTP_CLIENT
    HTTP_CLIENT --> DATADOG_API
```

This pipeline starts with OTLP-formatted telemetry entering the components. It passes through core utilities and Datadog-specific helpers that apply platform metadata. Signals are then mapped into Datadog's internal representation formats enriched with infra metadata and hostname resolution. Finally, data is serialized and compressed before being sent out via configured HTTP clients to Datadog's backend.

Sources: [exporter/datadogexporter/go.mod:28-49](), [exporter/datadogexporter/hostmetadata.go:1-50]().

### Metrics Data Flow

The metrics path performs detailed translation of OTLP metric points to Datadog metric types with support for distribution representations.

```mermaid
graph TB
    subgraph "OTLP Metrics Input"
        PDATA_METRICS["pdata.Metrics"]
        GAUGE["Gauge"]
        SUM["Sum"]
        HISTOGRAM["Histogram"]
    end

    subgraph "Mapping Layer"
        OTLP_METRICS_PKG["pkg/opentelemetry-mapping-go/otlp/metrics"]
    end

    subgraph "Datadog Metric Types"
        DD_GAUGE["Datadog Gauge"]
        DD_COUNT["Datadog Count"]
        DD_DISTRIBUTION["Datadog Distribution<br/>DDSketch"]
    end

    subgraph "Serialization"
        SKETCH_LIB["sketches-go<br/>DDSketch compression"]
        METRICS_PAYLOAD["MetricPayload<br/>agent-payload"]
    end

    PDATA_METRICS --> OTLP_METRICS_PKG
    GAUGE --> OTLP_METRICS_PKG
    SUM --> OTLP_METRICS_PKG
    HISTOGRAM --> OTLP_METRICS_PKG

    OTLP_METRICS_PKG --> DD_GAUGE
    OTLP_METRICS_PKG --> DD_COUNT
    OTLP_METRICS_PKG --> DD_DISTRIBUTION

    DD_DISTRIBUTION --> SKETCH_LIB
    SKETCH_LIB --> METRICS_PAYLOAD
    DD_GAUGE --> METRICS_PAYLOAD
    DD_COUNT --> METRICS_PAYLOAD
```

The mapping package converts various OTLP metric types (gauges, sums, histograms) into Datadog metric formats, utilizing the DDSketch library (`sketches-go`) for compressing distribution metrics. Finally, metrics are encapsulated into an agent-payload `MetricPayload`.

Sources: [exporter/datadogexporter/go.mod:20-25](), [receiver/datadogreceiver/go.mod:13-13](), [pkg/datadog/config/metrics.go:1-40]().

### Traces Data Flow

The trace pipeline processes OTLP spans with additional obfuscation and statistics before serialization.

```mermaid
graph TB
    subgraph "OTLP Traces Input"
        PDATA_TRACES["pdata.Traces"]
        SPANS["Spans"]
    end

    subgraph "Receiver Processing"
        OBFUSCATE["pkg/obfuscate<br/>Sensitive data sanitization"]
        STATS_COMPUTE["pkg/trace/stats<br/>Trace statistics computation"]
    end

    subgraph "Datadog Format"
        DD_SPANS["Datadog Spans<br/>pkg/proto.Span"]
        TRACE_PAYLOAD["TracePayload<br/>agent-payload"]
    end

    subgraph "Serialization"
        MSGPACK["MessagePack serialization"]
        GZIP["gzip compression"]
    end

    PDATA_TRACES --> SPANS
    SPANS --> OBFUSCATE
    OBFUSCATE --> STATS_COMPUTE

    STATS_COMPUTE --> DD_SPANS
    DD_SPANS --> TRACE_PAYLOAD
    TRACE_PAYLOAD --> MSGPACK
    MSGPACK --> GZIP
```

Here OTLP traces are converted into Datadog's `pkg/proto.Span` format after applying obfuscation of sensitive fields and computing trace-level statistics. The trace payload is then serialized using MessagePack and compressed using gzip before transmission.

Sources: [receiver/datadogreceiver/go.mod:7-11](), [exporter/datadogexporter/go.mod:22-23](), [pkg/datadog/config/traces.go:1-40]().

## Connector Data Flow

The `datadogconnector` component analyzes trace spans to generate Datadog-style APM statistics which are then fed into the metrics pipeline.

```mermaid
graph TB
    subgraph "Input"
        TRACES_IN["Traces Pipeline"]
    end

    subgraph "Connector Processing"
        DDC["datadogconnector<br/>Trace and span analyzer"]
        TAIL_SAMPLER["tailsamplingprocessor<br/>Trace sampling"]
    end

    subgraph "Output"
        METRICS_OUT["Metrics Pipeline"]
        DD_EXPORTER["datadogexporter"]
    end

    TRACES_IN --> DDC
    DDC --> TAIL_SAMPLER
    TAIL_SAMPLER --> METRICS_OUT
    METRICS_OUT --> DD_EXPORTER
```

This flow shows how incoming trace data is processed by the `datadogconnector` to emit derived metrics (e.g., APM stats), leveraging tail sampling before forwarding metrics downstream to the exporter.

Sources: [connector/datadogconnector/go.mod:6-8](), [connector/datadogconnector/factory.go:1-30]().

## Integration Test Infrastructure

The Datadog integration test suite uses a combination of real components and mock implementations to validate the full data path from source to Datadog backend.

| Component | Role | Package Reference |
|-----------|------|-------------------|
| `hostmetricsreceiver` | Provides realistic host metrics | `receiver/hostmetricsreceiver` [exporter/datadogexporter/integrationtest/go.mod:14-14]() |
| `datadogconnector` | Validates APM stats generation | `connector/datadogconnector` [exporter/datadogexporter/integrationtest/go.mod:9-9]() |
| `tailsamplingprocessor` | Verifies trace sampling correctness | `processor/tailsamplingprocessor` [exporter/datadogexporter/integrationtest/go.mod:13-13]() |
| `mockdatadogagentexporter` | Mocks Datadog Agent API endpoints for integration tests | `testbed/mockdatasenders` [testbed/go.mod:32-32]() |
| `testutil` | OTLP test helpers from Datadog Agent libraries | `comp/otelcol/otlp/testutil` [internal/datadog/go.mod:6-6]() |

These components enable end-to-end testing scenarios covering metrics and traces in the Datadog integration context.

Sources: [exporter/datadogexporter/integrationtest/go.mod:6-14](), [testbed/go.mod:32-32](), [internal/datadog/go.mod:6-6]().

---

This page has detailed the Datadog integration's shared module dependencies, core data transformation pipeline, key function groups, and how OpenTelemetry signals are eventually converted and exported to Datadog. It also outlined the major dependencies on Datadog Agent libraries and the internal/pkg module split that enables modular and maintainable integration components.