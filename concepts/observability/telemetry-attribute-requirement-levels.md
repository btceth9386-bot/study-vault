---
id: telemetry-attribute-requirement-levels
title: Telemetry Attribute Requirement Levels
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-semantic-conventions/
related:
  - semantic-attribute-registry-reuse
  - telemetry-signal-model
  - semantic-convention-stability-lifecycle
tags:
  - observability
  - opentelemetry
  - semantic-conventions
---

# Telemetry Attribute Requirement Levels

- **One-sentence definition**: Requirement levels say whether an instrumentation field is required, conditionally required, recommended, or opt-in in a specific context.
- **Why it exists / what problem it solves**: A field name alone does not tell an implementer when emitting it is necessary, useful, or too costly.
- **Keywords**: required, conditional, recommended, opt-in, cardinality, privacy
- **Related concepts**: [[semantic-attribute-registry-reuse]], [[telemetry-signal-model]], [[semantic-convention-stability-lifecycle]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/semantic-conventions

## Summary

Requirement levels are instructions for when to fill in a telemetry field. Required means the field is part of the minimum useful record. Conditionally required means it must appear when a stated situation applies. Recommended makes a record richer when available, while opt-in means an implementation should collect it only when a user deliberately enables it.

They balance usefulness against cost, privacy, and high-cardinality data. Requirement level is about presence, not whether a convention is safe from future breaking changes.

## Example

For an HTTP server span, `http.request.method` can be required because every request has a method. A full request body should be opt-in because it may be large or contain sensitive data. A client address might be conditionally required only when the runtime can obtain it safely.

## Relationship to Existing Concepts

- [[semantic-attribute-registry-reuse]]: A registry supplies the shared field; a requirement level says when to emit it.
- [[telemetry-signal-model]]: Requirement levels apply to fields on every kind of telemetry signal.
- [[semantic-convention-stability-lifecycle]]: Stability promises compatibility, while requirement level specifies expected presence.

## My Questions

- Which recommended attributes are worth collecting in a high-volume production path?
- How should teams review opt-in fields that could expose personal data?
