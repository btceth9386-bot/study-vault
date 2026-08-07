---
id: collector-pdata-ownership-at-fanout
title: Collector pdata Ownership at Fan-Out
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-opentelemetry-collector/
related:
  - collector-pipeline-architecture
  - telemetry-signal-model
tags:
  - observability
  - opentelemetry
  - collector
---

# Collector pdata Ownership at Fan-Out

- **One-sentence definition**: At a fan-out point, the Collector shares telemetry data with read-only branches and copies it only for branches that need to change it.
- **Why it exists / what problem it solves**: This avoids needless copying while preventing one branch from corrupting data another branch is still using.
- **Keywords**: pdata, ownership, mutation, fan-out, clone, concurrency
- **Related concepts**: [[collector-pipeline-architecture]], [[telemetry-signal-model]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/opentelemetry-collector

## Summary

`pdata` is the Collector's in-memory form of telemetry. When a pipeline sends one batch to several destinations, it would be wasteful to copy the batch for every branch. Instead, each component declares whether it may mutate its input.

Read-only branches can safely share the same batch. If a branch needs to add, remove, or edit data, it receives its own copy. The rule is both a performance optimization and a safety boundary.

## Example

A traces pipeline sends a batch to two exporters. The first immediately transmits it unchanged, so it can use the shared batch. The second removes customer IDs before sending to an external vendor, so it must receive a clone before redaction.

## Relationship to existing concepts

- [[collector-pipeline-architecture]]: Ownership rules apply whenever a pipeline branches to multiple consumers.
- [[telemetry-signal-model]]: The protected batches contain the traces, metrics, or logs described by the signal model.

## Open questions

- How can a custom processor prove that it does not mutate its input?
- Where do copies become expensive enough to change the pipeline topology?
