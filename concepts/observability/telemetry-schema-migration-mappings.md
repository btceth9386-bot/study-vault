---
id: telemetry-schema-migration-mappings
title: Telemetry Schema Migration Mappings
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-semantic-conventions/
related:
  - semantic-conventions-as-telemetry-schema
  - semantic-convention-stability-lifecycle
  - ottl-declarative-telemetry-transformation
tags:
  - observability
  - opentelemetry
  - semantic-conventions
---

# Telemetry Schema Migration Mappings

- **One-sentence definition**: Telemetry schema migration mappings are versioned, machine-readable rules that translate renamed attributes and metrics from one convention version to another.
- **Why it exists / what problem it solves**: Producers and backends upgrade at different times, so a shared translation plan keeps data queryable during the transition.
- **Keywords**: migration, schema URL, rename, compatibility, translation, versioning
- **Related concepts**: [[semantic-conventions-as-telemetry-schema]], [[semantic-convention-stability-lifecycle]], [[ottl-declarative-telemetry-transformation]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/semantic-conventions

## Summary

A migration mapping is a labeled bridge between two versions of a telemetry vocabulary. It records exactly how an old field or metric becomes a new one, so a collector or backend can understand both versions while systems upgrade at different speeds. The mapping is data that tools can apply, not an informal note buried in release documentation.

Versioned mappings make schema evolution operational. They preserve useful queries without forcing every service, agent, collector, and dashboard to change on the same day.

## Example

Version 1 sends `http.method`; version 2 sends `http.request.method`. A mapping for the version change renames the old attribute to the new one before a dashboard query runs. The dashboard can use the new name while older services are still being deployed.

## Relationship to Existing Concepts

- [[semantic-conventions-as-telemetry-schema]]: Mappings evolve the shared telemetry contract safely.
- [[semantic-convention-stability-lifecycle]]: Stability policy determines when breaking changes and migrations are acceptable.
- [[ottl-declarative-telemetry-transformation]]: A transformation system can apply a mapping to in-flight telemetry.

## My Questions

- When should a mapping duplicate a field versus rename it in place?
- How can dashboards show a mix of old and new schema versions during a rollout?
