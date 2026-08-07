---
id: semantic-convention-stability-lifecycle
title: Semantic Convention Stability Lifecycle
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-semantic-conventions/
related:
  - semantic-convention-model-as-source-of-truth
  - telemetry-schema-migration-mappings
  - metadata-driven-component-stability
tags:
  - observability
  - opentelemetry
  - semantic-conventions
---

# Semantic Convention Stability Lifecycle

- **One-sentence definition**: A semantic convention stability lifecycle labels a convention as development, release candidate, stable, or deprecated so users know its maturity and compatibility promise.
- **Why it exists / what problem it solves**: Instrumentation authors need to know whether to expect changes and when they must plan a migration.
- **Keywords**: development, release candidate, stable, deprecated, compatibility, migration
- **Related concepts**: [[semantic-convention-model-as-source-of-truth]], [[telemetry-schema-migration-mappings]], [[metadata-driven-component-stability]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/semantic-conventions

## Summary

The stability label is a traffic light for a telemetry contract. Development conventions are still being shaped, release candidates are nearing a public promise, stable conventions should avoid breaking users, and deprecated conventions have a planned replacement. The label helps teams decide how tightly they can depend on a definition.

It is not the same as an attribute's requirement level. One describes how likely a definition is to change; the other describes whether an implementation should send a field.

## Example

A new database attribute begins in development, so a library author keeps its use isolated. Once stable, the author can rely on its name in dashboards. If it is later deprecated, a migration mapping identifies the replacement before the old field is removed.

## Relationship to Existing Concepts

- [[semantic-convention-model-as-source-of-truth]]: Stability is metadata on the model that defines the contract.
- [[telemetry-schema-migration-mappings]]: A lifecycle change can require explicit translation from an older schema.
- [[metadata-driven-component-stability]]: Both use machine-readable maturity metadata, but this lifecycle applies to conventions rather than Collector components.

## My Questions

- What evidence should move a convention from release candidate to stable?
- How long should a deprecated attribute remain supported in common tooling?
