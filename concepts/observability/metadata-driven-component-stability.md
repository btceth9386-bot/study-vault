---
id: metadata-driven-component-stability
title: Metadata-Driven Component Stability
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-opentelemetry-collector-contrib/
related:
  - collector-component-factory-lifecycle
  - opentelemetry-collector-builder-distributions
  - semantic-convention-stability-lifecycle
tags:
  - observability
  - opentelemetry
  - collector
---

# Metadata-Driven Component Stability

- **One-sentence definition**: Component metadata records maturity, supported signals, ownership, and distribution membership so tooling can enforce them consistently.
- **Why it exists / what problem it solves**: A large plug-in ecosystem needs machine-checkable promises instead of scattered, hand-maintained lifecycle labels.
- **Keywords**: metadata, stability, maturity, ownership, signals, automation
- **Related concepts**: [[collector-component-factory-lifecycle]], [[opentelemetry-collector-builder-distributions]], [[semantic-convention-stability-lifecycle]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/opentelemetry-collector-contrib

## Summary

Metadata-driven stability is a product label that automation can read. One component file records who owns a component, which signals it supports, and whether each signal is experimental, beta, or stable. Repository tools then use that one record to generate constants, tests, ownership settings, and release controls. A receiver can therefore be stable for metrics while still experimental for logs.

## Example

A receiver declares stable metrics support and beta logs support in its metadata. A generated status page and validation test report those levels separately, so a distribution does not advertise the whole receiver as fully stable by mistake.

## Relationship to existing concepts

- [[collector-component-factory-lifecycle]]: Metadata describes the components that factories create and the service operates.
- [[opentelemetry-collector-builder-distributions]]: Distribution tooling can use metadata to decide which components are suitable to include.
- [[semantic-convention-stability-lifecycle]]: Both record maturity, but component metadata and convention compatibility are separate promises.

## Open questions

- What evidence should be required before a signal moves from beta to stable?
- How should metadata changes be reviewed when they change a public support promise?
