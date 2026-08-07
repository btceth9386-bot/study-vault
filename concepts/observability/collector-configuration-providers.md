---
id: collector-configuration-providers
title: Collector Configuration Providers and Resolution
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-opentelemetry-collector/
related:
  - collector-component-factory-lifecycle
  - collector-pipeline-architecture
  - opentelemetry-collector-builder-distributions
tags:
  - observability
  - opentelemetry
  - collector
---

# Collector Configuration Providers and Resolution

- **One-sentence definition**: Collector configuration providers fetch values from named sources and combine them into the configuration used to build and run components.
- **Why it exists / what problem it solves**: Deployments can keep environment values, secrets, files, and remote configuration separate from the Collector binary.
- **Keywords**: confmap, provider, URI, configuration, environment, resolution
- **Related concepts**: [[collector-component-factory-lifecycle]], [[collector-pipeline-architecture]], [[opentelemetry-collector-builder-distributions]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/opentelemetry-collector

## Summary

The `confmap` resolver is a configuration reader with plug-in sources. A URI tells it where to fetch a value, such as an environment variable, a file, HTTP, HTTPS, or YAML. It can resolve nested references and preserve a value's original type when the reference fills the whole field.

Providers can also report that their source changed. The resolver can then read configuration again, which supports controlled runtime updates without hard-coding one storage mechanism.

## Example

An exporter endpoint can be written as `${env:OTLP_ENDPOINT}` in a YAML file. In staging, the deployment sets `OTLP_ENDPOINT` to the test backend; in production, it sets a different value. The same Collector configuration and binary work in both places.

## Relationship to existing concepts

- [[collector-component-factory-lifecycle]]: Resolved configuration supplies the settings factories use to create components.
- [[collector-pipeline-architecture]]: Configuration declares the receivers, processors, and exporters in each pipeline.
- [[opentelemetry-collector-builder-distributions]]: A custom distribution determines which provider implementations are available.

## Open questions

- Which values should be resolved at startup only, and which are safe to refresh dynamically?
- How can a deployment validate remote configuration before applying it?
