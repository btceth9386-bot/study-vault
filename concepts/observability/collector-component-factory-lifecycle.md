---
id: collector-component-factory-lifecycle
title: Collector Component Factory and Lifecycle
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-opentelemetry-collector/
related:
  - collector-pipeline-architecture
  - collector-connectors
  - collector-extensions
  - collector-configuration-providers
  - opentelemetry-collector-builder-distributions
  - metadata-driven-component-stability
  - observer-driven-dynamic-receivers
  - opamp-supervised-collector-fleet-management
tags:
  - observability
  - opentelemetry
  - collector
---

# Collector Component Factory and Lifecycle

- **One-sentence definition**: Collector factories turn configuration into components, and a shared lifecycle lets the service start and stop them safely.
- **Why it exists / what problem it solves**: One runtime can consistently manage receivers, processors, exporters, connectors, and extensions even though they do different work.
- **Keywords**: factory, configuration, start, shutdown, component, lifecycle
- **Related concepts**: [[collector-pipeline-architecture]], [[collector-connectors]], [[collector-extensions]], [[collector-configuration-providers]], [[opentelemetry-collector-builder-distributions]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/opentelemetry-collector

## Summary

A factory is a recipe card: it supplies default settings and knows how to build the right kind of component from user configuration. The service does not need special startup code for every component type because each follows the same `Start` and `Shutdown` contract.

This is useful because a Collector is assembled from plug-in pieces. The service can create them, start supporting services first, run pipelines, and shut everything down in a controlled order.

## Example

When configuration enables an OTLP receiver and an OTLP exporter, their factories create those components. The service starts the receiver only after its dependencies are ready, then calls shutdown during a restart so connections and background work are released cleanly.

## Relationship to existing concepts

- [[collector-pipeline-architecture]]: Factories supply the components used in pipelines.
- [[collector-connectors]]: Connector factories create components that play two pipeline roles.
- [[collector-extensions]]: Extensions use the same lifecycle while serving outside the data path.
- [[collector-configuration-providers]]: Resolved configuration is the input to factory creation.
- [[opentelemetry-collector-builder-distributions]]: A custom distribution chooses which factories are registered.
- [[metadata-driven-component-stability]]: Metadata records the maturity and ownership of factory-created components.
- [[observer-driven-dynamic-receivers]]: Dynamic discovery creates and stops receiver instances through the shared lifecycle.
- [[opamp-supervised-collector-fleet-management]]: A Supervisor manages the Collector runtime that operates component lifecycles.

## Open questions

- Which startup dependencies must be explicit when writing a custom component?
- How should a component report a partial startup failure so the service can shut down safely?
