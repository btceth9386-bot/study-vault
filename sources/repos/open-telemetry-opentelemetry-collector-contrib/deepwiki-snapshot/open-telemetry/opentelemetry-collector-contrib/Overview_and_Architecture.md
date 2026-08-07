## Purpose and Scope

This document provides a high-level overview of the `opentelemetry-collector-contrib` repository architecture, explaining its role in the OpenTelemetry ecosystem and how its component-based design enables extensible telemetry collection and processing. This page covers the fundamental architecture patterns, component types, and assembly process.

For details on specific subsystems:
- Repository organization and component management: see [Repository Structure and Component Organization](#1.1)
- Component lifecycle and stability levels: see [Component Lifecycle and Stability Management](#1.2)
- Module structure and dependencies: see [Module Dependencies and Internal Architecture](#1.3)
- Binary assembly process: see [Collector Binary Assembly](#3)

**Sources:** [README.md:41-45](), [cmd/otelcontribcol/builder-config.yaml:1-14]()

## Role in the OpenTelemetry Ecosystem

The `opentelemetry-collector-contrib` repository is a community-maintained extension of the core OpenTelemetry Collector, providing over 200 additional components for telemetry collection, processing, and export [reports/distributions/contrib.yaml:4-257](). While the core collector provides the fundamental pipeline architecture and a minimal set of components, this repository contains vendor-specific receivers, exporters, processors, extensions, and connectors contributed by the community [README.md:43-45]().

**Important Note:** This repository does NOT produce the final official collector binaries. As stated in the builder configuration [cmd/otelcontribcol/builder-config.yaml:2-7]() and `go.mod` [go.mod:3-9]():

> This builder configuration is NOT used to build any official binary. To see the builder manifests used for official binaries, check https://github.com/open-telemetry/opentelemetry-collector-releases

Official distributions are managed in the [opentelemetry-collector-releases](https://github.com/open-telemetry/opentelemetry-collector-releases) repository, which references components from this repository as dependencies [README.md:45-46]().

**Sources:** [README.md:41-48](), [cmd/otelcontribcol/builder-config.yaml:1-14](), [go.mod:3-9]()

## Component Type Architecture

### Five Component Types

The collector architecture is built around five component types that form a processing pipeline:

```mermaid
graph LR
    subgraph "Data Sources"
        ["SRC1"]:::label
        SRC1["Applications<br/>Infrastructure<br/>Cloud Services"]
    end

    subgraph "OpenTelemetry Collector Pipeline"
        ["REC"]:::label
        REC["Receivers<br/>100+ types<br/>Ingest telemetry"]
        ["PROC"]:::label
        PROC["Processors<br/>25+ types<br/>Transform data"]
        ["CONN"]:::label
        CONN["Connectors<br/>10+ types<br/>Route between pipelines"]
        ["EXP"]:::label
        EXP["Exporters<br/>60+ types<br/>Send to backends"]
        ["EXT"]:::label
        EXT["Extensions<br/>30+ types<br/>Cross-cutting capabilities"]
    end

    subgraph "Backends"
        ["BACK"]:::label
        BACK["Monitoring Systems<br/>Storage<br/>Analytics Platforms"]
    end

    SRC1 --> REC
    REC --> PROC
    PROC --> CONN
    CONN --> PROC
    PROC --> EXP
    EXP --> BACK
    EXT -.-> REC
    EXT -.-> PROC
    EXT -.-> EXP
```

**Component Type Overview**

| Component Type | Purpose | Examples |
|---------------|---------|----------|
| **Receivers** | Ingest telemetry data from various sources | `jaeger`, `prometheus`, `kafka`, `host_metrics` |
| **Processors** | Transform, filter, and enrich telemetry | `batch`, `attributes`, `resource_detection`, `tail_sampling` |
| **Exporters** | Send telemetry to backend systems | `datadog`, `prometheus`, `elasticsearch`, `kafka` |
| **Extensions** | Provide cross-cutting capabilities | `health_check`, `pprof`, `oauth2client`, `file_storage` |
| **Connectors** | Route data between pipelines | `routing`, `span_metrics`, `datadog`, `count` |

**Sources:** [reports/distributions/contrib.yaml:5-257](), [.chloggen/config.yaml:18-245](), [cmd/otelcontribcol/builder-config.yaml:16-310]()

### Component Categories by Integration

```mermaid
graph TB
    subgraph "Cloud Providers"
        ["AWS"]:::label
        AWS["AWS Components<br/>awscontainerinsightreceiver<br/>awsxrayreceiver<br/>awsemfexporter"]
        ["GCP"]:::label
        GCP["GCP Components<br/>googlecloudspannerreceiver<br/>googlecloudpubsubreceiver<br/>googlecloudexporter"]
        ["AZURE"]:::label
        AZURE["Azure Components<br/>azure_event_hub_receiver<br/>azuremonitor_exporter"]
        ["DD"]:::label
        DD["Datadog Integration<br/>datadog_receiver<br/>datadog_connector<br/>datadog_exporter"]
    end

    subgraph "Data Stores"
        ["SQL"]:::label
        SQL["SQL Databases<br/>sqlquery_receiver<br/>sqlserver_receiver<br/>oracledb_receiver"]
        ["NOSQL"]:::label
        NOSQL["NoSQL & Search<br/>mongodb_receiver<br/>redis_receiver<br/>elasticsearch_exporter"]
        ["TSDB"]:::label
        TSDB["Time Series<br/>prometheus_receiver<br/>prometheus_exporter<br/>influxdb_exporter"]
    end

    subgraph "Message Queues"
        ["KAFKA"]:::label
        KAFKA["Kafka Ecosystem<br/>kafka_receiver<br/>kafka_exporter<br/>kafka_metrics_receiver"]
        ["OTHER"]:::label
        OTHER["Other Queues<br/>pulsar_receiver<br/>rabbitmq_exporter"]
    end
```

**Sources:** [reports/distributions/contrib.yaml:18-240](), [.github/CODEOWNERS:19-400]()

## Component Factory and Registry Pattern

Each component type implements a factory pattern for registration and instantiation. The build system uses these factories to assemble the final service.

```mermaid
graph TD
    subgraph "Component Definition"
        ["A"]:::label
        A[".yaml files<br/>(e.g., metadata.yaml, config.yaml)"]
        ["B"]:::label
        B["Go Factory<br/>(e.g., NewFactory() in factory.go)"]
        ["C"]:::label
        C["Go Config Struct<br/>(e.g., Config in config.go)"]
        ["D"]:::label
        D["Go Component Logic<br/>(e.g., Start(), Shutdown() methods)"]
    end

    subgraph "Code Generation & Build"
        ["E"]:::label
        E["mdatagen tool<br/>(generates boilerplate)"]
        ["F"]:::label
        F["builder-config.yaml<br/>(component selection)"]
        ["G"]:::label
        G["OpenTelemetry Collector Builder (ocb)<br/>(assembles binary)"]
        ["H"]:::label
        H["components.go<br/>(generated component registry)"]
        ["I"]:::label
        I["otelcontribcol binary<br/>(final executable)"]
    end

    A -- "Defines component metadata" --> E
    B -- "Implements component creation" --> G
    C -- "Defines configuration structure" --> B
    D -- "Contains core functionality" --> B

    E -- "Generates code based on metadata" --> B
    F -- "Specifies components to include" --> G
    G -- "Uses factories to register components" --> H
    H -- "Used by main to run collector" --> I
```

**Key Code Entities:**

- **Factory Functions**: Each component exports a `NewFactory()` function that returns a `component.Factory` instance.
- **metadata.yaml**: Defines component type, stability levels for different signals (traces, metrics, logs), and telemetry schema [README.md:47-48]().
- **builder-config.yaml**: Lists the specific modules to include in a distribution (e.g., [cmd/otelcontribcol/builder-config.yaml:16-310]()).

**Sources:** [cmd/otelcontribcol/builder-config.yaml:9-14](), [.github/CODEOWNERS:19-400](), [README.md:47-48]()

## Repository Structure

The repository is organized primarily by component type with supporting infrastructure:

| Directory | Purpose |
|-----------|---------|
| `receiver/` | Components that ingest telemetry data [reports/distributions/contrib.yaml:139]() |
| `processor/` | Components that transform telemetry [reports/distributions/contrib.yaml:103]() |
| `exporter/` | Components that send telemetry to backends [reports/distributions/contrib.yaml:18]() |
| `extension/` | Cross-cutting functionality like auth and storage [reports/distributions/contrib.yaml:64]() |
| `connector/` | Components that bridge pipelines [reports/distributions/contrib.yaml:5]() |
| `internal/` | Shared code used by multiple components (not public API) [.chloggen/config.yaml:127-148]() |
| `pkg/` | Public packages providing utilities like `ottl` or `stanza` [.chloggen/config.yaml:149-183]() |
| `cmd/` | Binary entry points and CLI tools (e.g., `telemetrygen`, `opampsupervisor`) [.chloggen/config.yaml:11-16]() |

**Sources:** [.github/CODEOWNERS:19-400](), [.chloggen/config.yaml:9-245]()

## Component Assembly Process

The collector binary is assembled through the OpenTelemetry Collector Builder (`ocb`). The configuration at [cmd/otelcontribcol/builder-config.yaml:9-14]() defines the distribution:

```yaml
dist:
  module: github.com/open-telemetry/opentelemetry-collector-contrib/cmd/otelcontribcol
  name: otelcontribcol
  description: Local OpenTelemetry Collector Contrib binary, testing only.
  version: 0.155.0-dev
  output_path: ./cmd/otelcontribcol
```

Components are included by referencing their Go module paths and versions:
- **Extensions:** [cmd/otelcontribcol/builder-config.yaml:16-62]()
- **Exporters:** [cmd/otelcontribcol/builder-config.yaml:64-136]()
- **Processors:** [cmd/otelcontribcol/builder-config.yaml:138-175]()
- **Receivers:** [cmd/otelcontribcol/builder-config.yaml:177-281]()
- **Connectors:** [cmd/otelcontribcol/builder-config.yaml:283-298]()

**Sources:** [cmd/otelcontribcol/builder-config.yaml:1-310](), [CONTRIBUTING.md:9-17]()

## Component Ownership and Governance

The repository uses a distributed ownership model where each component has designated code owners defined in [.github/CODEOWNERS]().

- **Approvers**: Repository-wide maintainers listed in [.github/CODEOWNERS:12]().
- **Component Owners**: Individual contributors or vendors responsible for specific directories (e.g., `@mx-psi` for `cmd/telemetrygen/` [.github/CODEOWNERS:26]()).
- **Unmaintained Components**: Tracked via specific issue templates and labels [.github/ISSUE_TEMPLATE/unmaintained.yaml:1-4]().

**Sources:** [.github/CODEOWNERS:1-400](), [README.md:57-64]()

## Versioning and Module Management

The repository manages hundreds of Go modules with coordinated versioning. The `versions.yaml` file and internal tools ensure that the massive dependency graph across 200+ modules remains consistent during releases.

**Sources:** [go.mod:1-11](), [versions.yaml:4-7]()