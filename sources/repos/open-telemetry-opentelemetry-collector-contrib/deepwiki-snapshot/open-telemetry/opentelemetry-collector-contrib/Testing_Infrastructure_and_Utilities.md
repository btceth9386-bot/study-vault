## Purpose and Scope

This document provides an overview of the comprehensive testing infrastructure and utilities employed within the OpenTelemetry Collector Contrib repository. This infrastructure ensures that components meet quality and reliability standards through multiple verification layers, including synthetic telemetry data generation, end-to-end testing, integration testing, and performance benchmarking.

The page serves as a high-level guide to the major testing subsystems and how they interrelate, with pointers to more detailed child pages:

- For the telemetry generation tool and its testing, see [Telemetry Generator (telemetrygen)](#13.1).
- For the end-to-end testing architecture, testbed framework, and Kubernetes-based testing, see [End-to-End Testing Framework](#13.2).
- For test utilities such as golden files and `pdatatest` used in integration tests, see [Test Utilities: Golden Files and pdatatest](#13.3).

---

## Testing Layers and Strategy

The repository employs a layered testing strategy to cover component correctness, integration, resource usage, and behavior under load. Each layer focuses on a particular aspect of validation and combines automated tooling, synthetic data generation, and real deployment scenarios.

### Layered Testing Architecture

```mermaid
graph TB
    subgraph "Code Quality Gates"
        LINT["golangci-lint<br/>~50 linters"]
        VULN["govulncheck<br/>CVE scanning"]
        CHECKS["Automated Checks<br/>metadata/API/format"]
    end

    subgraph "Unit Testing Layer"
        UT_LINUX["Linux Unit Tests<br/>make gotest<br/>16 component groups"]
        UT_WIN["Windows Unit Tests<br/>windows-2025, windows-11-arm"]
        UT_MAC["macOS Unit Tests<br/>macos-14, macos-15"]
        UT_ARM["ARM Unit Tests<br/>ubuntu-22.04-arm"]
    end

    subgraph "Integration Testing Layer"
        INT_DOCKER["Docker Integration<br/>make gointegration-test<br/>testcontainers-go"]
        INT_SUDO["Privileged Tests<br/>mod-integration-sudo-test"]
    end

    subgraph "E2E Testing Layer"
        E2E_K8S["Kubernetes Tests<br/>3 K8s versions<br/>kind clusters"]
        E2E_SUPERVISOR["OpAMP Supervisor<br/>supervisor e2e tests"]
    end

    subgraph "Performance & Correctness Layer"
        TESTBED["Testbed Framework<br/>make -C testbed run-tests"]
        CORRECTNESS_TRACES["Correctness Traces<br/>run-correctness-traces-tests"]
        CORRECTNESS_METRICS["Correctness Metrics<br/>run-correctness-metrics-tests"]
    end

    subgraph "Specialized Testing"
        PROM_COMPLIANCE["Prometheus Compliance<br/>Remote Write validation"]
        GOLDEN["Golden File Tests<br/>pkg/golden"]
        PDATATEST["pdata Comparison<br/>pkg/pdatatest"]
    end

    LINT --> UT_LINUX
    VULN --> UT_LINUX
    CHECKS --> UT_LINUX

    UT_LINUX --> INT_DOCKER
    UT_WIN --> INT_DOCKER
    UT_MAC --> INT_DOCKER
    UT_ARM --> INT_DOCKER

    INT_DOCKER --> E2E_K8S
    INT_DOCKER --> E2E_SUPERVISOR

    E2E_K8S --> TESTBED
    E2E_SUPERVISOR --> TESTBED

    TESTBED --> CORRECTNESS_TRACES
    TESTBED --> CORRECTNESS_METRICS
```

This layered approach starts with static analysis and unit testing across Linux, Windows, macOS, and ARM platforms to catch early regressions. It progresses to integration tests running in containers and privileged modes for more realistic environments. End-to-end (E2E) tests execute on Kubernetes clusters to validate real deployment scenarios and remote management via the OpAMP supervisor.

The `testbed` framework plays a central role in performance benchmarking and correctness validation, coordinating load generation, collector execution, and telemetry verification. Specialized tests include Prometheus remote write protocol compliance and golden-file-based output validation.

**Sources:** [.github/workflows/build-and-test.yml:1-631](), [.github/workflows/e2e-tests.yml:1-158](), [.github/workflows/load-tests.yml:1-118]()

---

## Telemetry Generation Tools

### telemetrygen Overview

`telemetrygen` is a dedicated CLI tool designed to generate synthetic OpenTelemetry telemetry signals (traces, metrics, logs). It supports exporting over OTLP gRPC and HTTP with features such as exponential histogram metrics [cmd/telemetrygen/pkg/metrics/worker.go:182-202]().

```mermaid
graph LR
    subgraph "telemetrygen Binary"
        CLI["telemetrygen CLI<br/>cmd/telemetrygen"]
        TRACES["Traces Generator<br/>OTLP gRPC/HTTP"]
        METRICS["Metrics Generator<br/>OTLP gRPC/HTTP"]
        LOGS["Logs Generator<br/>OTLP gRPC/HTTP"]
    end

    subgraph "E2E Test Module"
        E2E["e2etest Package<br/>cmd/telemetrygen/internal/e2etest"]
        RECEIVER["otlpreceiver<br/>consumertest.TracesSink"]
    end

    CLI --> TRACES
    CLI --> METRICS
    CLI --> LOGS

    E2E --> RECEIVER
    RECEIVER --> CLI
```

Key capabilities include:

- **Multi-protocol support**: OTLP exporters over gRPC and HTTP ensuring compatibility with standard collector receivers [cmd/telemetrygen/go.mod:12-18]().
- **Signal Diversity**: Generation of diverse telemetry signals including traces, metrics (with exponential histogram support), and logs [cmd/telemetrygen/go.mod:6-10]().
- **Self-Validation**: Internal e2e tests within the `internal/e2etest` module ensure tool correctness by sending generated telemetry to a real `otlpreceiver` and validating the reception [cmd/telemetrygen/internal/e2etest/go.mod:6-14]().

**Sources:** [cmd/telemetrygen/go.mod:1-30](), [cmd/telemetrygen/internal/e2etest/go.mod:1-15](), [cmd/telemetrygen/pkg/metrics/worker.go:182-202]()

For details, see [Telemetry Generator (telemetrygen)](#13.1).

---

## Testbed Framework

The `testbed` framework is the cornerstone of performance benchmarking and correctness testing. It orchestrates running the OpenTelemetry Collector as a separate process (or in-process), injecting synthetic telemetry, and verifying results and resource usage.

### Core Testbed Components

| Code Entity | File Path | Role |
| :--- | :--- | :--- |
| `TestCase` | [testbed/testbed/test_case.go:22-59]() | Manages test lifecycle: load generation, agent start, validation. |
| `DataSender` | [testbed/testbed/senders.go]() | Interface for synthetic data producers (senders). |
| `DataReceiver` | [testbed/testbed/receivers.go:25-35]() | Interface for receivers that collect data from collector exporters. |
| `MockBackend` | [testbed/testbed/mock_backend.go]() | Sink to receive telemetry, enabling validation. |
| `OtelcolRunner` | [testbed/testbed/otelcol_runner.go]() | Interface for managing the OpenTelemetry Collector execution. |

### Performance Scenario Example

The testbed supports scenarios such as `Scenario10kItemsPerSecond` that simulate sending 10k telemetry data items per second through the collector while resource usage is measured [testbed/tests/scenarios.go:138-194]().

```mermaid
graph TD
    subgraph "Testbed Execution"
        TC["testbed.TestCase"]
        LOAD["LoadGenerator (e.g., telemetrygen)"]
        COL["OtelcolRunner (Collector)"]
        BACK["MockBackend (Telemetry Sink)"]
    end

    TC -->|"StartAgent()"| COL
    TC -->|"StartBackend()"| BACK
    TC -->|"StartLoad()"| LOAD
    LOAD -->|"Generates OTLP/Jaeger/Zipkin data"| COL
    COL -->|"Exports Telemetry"| BACK
    TC -->|"ValidateData()"| BACK
```

The framework allows for dynamic configuration generation, where the `createConfigYaml` function builds a collector configuration based on the specific `DataSender` and `DataReceiver` used in the test [testbed/tests/scenarios.go:43-135]().

**Sources:** [testbed/testbed/test_case.go:67-129](), [testbed/tests/scenarios.go:138-194](), [testbed/testbed/receivers.go:25-35]()

For detailed architecture and usage, see [End-to-End Testing Framework](#13.2).

---

## Test Utilities: Golden Files and pdatatest

To facilitate precise validation of telemetry data, the repository offers specialized test utilities.

### pkg/pdatatest

The `pdatatest` package enables deep comparisons of OpenTelemetry `pdata` structures representing metrics, logs, traces, and profiles. It provides semantically rich diff outputs that annotate differences and can ignore irrelevant fields (e.g., timestamps).

### pkg/golden

The `golden` package assists with reading and writing reference ("golden") YAML files for expected telemetry output. These golden files serve as canonical references that component tests compare runtime outputs against.

---

## Specialized Integration Tests

Beyond standard testbed scenarios, the repository includes targeted integration tests for specific features:

- **Prometheus Receiver Staleness Markers**: Validates that the Prometheus receiver correctly emits staleness markers when timeseries metrics intermittently disappear. This test runs a full collector instance and checks the output via the `prometheusremotewriteexporter` [receiver/prometheusreceiver/internal/staleness_end_to_end_test.go:45-77]().
- **Elasticsearch Exporter Integration**: Employs a `recreatableOtelCol` test harness to simulate Collector lifecycle events and failures while verifying Elasticsearch exporter behavior [exporter/elasticsearchexporter/integrationtest/collector.go:120-157]().

**Sources:** [receiver/prometheusreceiver/internal/staleness_end_to_end_test.go:45-77](), [exporter/elasticsearchexporter/integrationtest/collector.go:38-101]()

---

## Summary Diagram: Infrastructure to Code Entities

```mermaid
graph LR
    subgraph "Telemetrygen Tool"
        TELEMETRYGEN_CLI["cmd/telemetrygen/"]
        E2ETEST_MODULE["cmd/telemetrygen/internal/e2etest/"]
        OTLP_RECEIVER["otlpreceiver"]
    end

    subgraph "Testbed Framework"
        TEST_CASE["testbed/testbed/test_case.go: TestCase"]
        DATA_SENDERS["testbed/testbed/senders.go: DataSender"]
        DATA_RECEIVERS["testbed/testbed/receivers.go: DataReceiver"]
        MOCK_BACKEND["testbed/testbed/mock_backend.go: MockBackend"]
        OTELCOL_RUNNER["testbed/testbed/otelcol_runner.go: OtelcolRunner"]
    end

    subgraph "Test Utilities"
        PDATATEST["pkg/pdatatest"]
        GOLDEN["pkg/golden"]
    end

    TELEMETRYGEN_CLI -->|generates synthetic data| DATA_SENDERS
    DATA_SENDERS -->|push data to collector| OTELCOL_RUNNER
    OTELCOL_RUNNER -->|exports data collected| DATA_RECEIVERS
    DATA_RECEIVERS -->|sink for validation| MOCK_BACKEND
    MOCK_BACKEND -->|used in| TEST_CASE
    E2ETEST_MODULE -->|validates telemetrygen| OTLP_RECEIVER

    GOLDEN -- used in --> TEST_CASE
    PDATATEST -- used in --> TEST_CASE
```

---

## Related Child Pages

- [Telemetry Generator (telemetrygen)](#13.1)
- [End-to-End Testing Framework](#13.2)
- [Test Utilities: Golden Files and pdatatest](#13.3)