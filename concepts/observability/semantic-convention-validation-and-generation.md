---
id: semantic-convention-validation-and-generation
title: Semantic Convention Validation and Generation
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-semantic-conventions/
  - sources/repos/open-telemetry-semantic-conventions-genai/
related:
  - semantic-convention-model-as-source-of-truth
  - semantic-attribute-registry-reuse
  - telemetry-schema-migration-mappings
  - domain-owned-semantic-conventions
tags:
  - observability
  - opentelemetry
  - semantic-conventions
---

# Semantic Convention Validation and Generation

- **One-sentence definition**: Semantic convention validation and generation checks one declarative model and produces synchronized documentation, registries, tables, and code artifacts from it.
- **Why it exists / what problem it solves**: Automation catches incompatible definitions before release and prevents hand-copied versions of a convention from drifting apart.
- **Keywords**: validation, generation, CI, policy, templates, declarative model
- **Related concepts**: [[semantic-convention-model-as-source-of-truth]], [[semantic-attribute-registry-reuse]], [[telemetry-schema-migration-mappings]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/semantic-conventions

## Summary

Validation and generation treat the semantic model like a checked blueprint. Validators look for missing fields, invalid types, broken references, and incompatible changes. Generators then turn the same approved blueprint into reference pages, attribute registries, tables, and other artifacts.

The result is a short feedback loop: a change either proves that it fits the contract or fails before people must discover the mismatch in production.

## Example

A contributor adds a span attribute but gives it a type that conflicts with its registry entry. CI rejects the model. After the contributor fixes the definition, generation refreshes the documentation table automatically, so reviewers do not need to compare copied values by hand.

## Relationship to Existing Concepts

- [[semantic-convention-model-as-source-of-truth]]: The model is the input that validators check and generators render.
- [[semantic-attribute-registry-reuse]]: Validation confirms that domain models reference shared attributes correctly.
- [[telemetry-schema-migration-mappings]]: Evolution rules can be checked alongside a model change.

## My Questions

- Which generated artifacts should be committed versus created only during release?
- How can validation give contributors a clear fix instead of only reporting a failed rule?

## Executable reference scenarios

Model validation checks the blueprint, but runnable reference scenarios check whether a real SDK can honestly emit it. Deterministic mock providers exercise public request and response APIs, then compare the emitted telemetry with the declared convention and report per-library coverage.

- [[domain-owned-semantic-conventions]]: Domain owners can use scenario coverage to spot gaps between a specification and supported SDKs.
