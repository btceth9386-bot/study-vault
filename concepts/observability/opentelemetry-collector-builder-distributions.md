---
id: opentelemetry-collector-builder-distributions
title: Custom Distributions with the OpenTelemetry Collector Builder
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-opentelemetry-collector/
related:
  - collector-component-factory-lifecycle
  - collector-configuration-providers
  - collector-pipeline-architecture
  - otlp-vendor-neutral-telemetry-protocol
tags:
  - observability
  - opentelemetry
  - collector
---

# Custom Distributions with the OpenTelemetry Collector Builder

- **One-sentence definition**: The OpenTelemetry Collector Builder creates a reproducible Collector binary from a YAML list of the components and configuration providers it should include.
- **Why it exists / what problem it solves**: Teams can ship only the capabilities they need instead of deploying a larger binary with unused components.
- **Keywords**: ocb, distribution, manifest, module, Go, reproducible build
- **Related concepts**: [[collector-component-factory-lifecycle]], [[collector-configuration-providers]], [[collector-pipeline-architecture]], [[otlp-vendor-neutral-telemetry-protocol]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/opentelemetry-collector

## Summary

The Collector Builder, often called `ocb`, is a build tool for making a tailored Collector distribution. Its YAML manifest names the receivers, processors, exporters, connectors, extensions, configuration providers, and module versions to include. It then generates the Go project and component registration needed to build that exact binary.

This makes the deployed capability set explicit and repeatable. A configuration cannot use a component that was not included in the distribution, which reduces footprint and limits what the binary can do.

## Example

A team that only receives OTLP and exports to one backend can build a distribution with the OTLP receiver, a batch processor, that exporter, and environment and file configuration providers. The resulting binary omits unrelated receivers and exporters.

## Relationship to existing concepts

- [[collector-component-factory-lifecycle]]: The builder registers the factories available to the service.
- [[collector-configuration-providers]]: The manifest selects which configuration URI schemes the binary can resolve.
- [[collector-pipeline-architecture]]: The generated binary hosts the pipelines declared in runtime configuration.
- [[otlp-vendor-neutral-telemetry-protocol]]: OTLP support exists only when the appropriate receiver or exporter modules are selected.

## Open questions

- Which components are required by every environment, and which should be environment-specific?
- How should teams test that a new manifest still includes every production dependency?
