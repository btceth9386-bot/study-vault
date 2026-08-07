---
id: semantic-convention-model-as-source-of-truth
title: Semantic Convention Model as Source of Truth
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-semantic-conventions/
related:
  - semantic-conventions-as-telemetry-schema
  - telemetry-signal-model
  - semantic-convention-validation-and-generation
tags:
  - observability
  - opentelemetry
  - semantic-conventions
---

# Semantic Convention Model as Source of Truth

- **One-sentence definition**: A semantic convention model is a machine-readable description of telemetry fields and signals that every derived document or artifact uses as its starting point.
- **Why it exists / what problem it solves**: It prevents documentation, code, and attribute tables from quietly describing different versions of the same telemetry contract.
- **Keywords**: model, YAML, schema, source of truth, generation, telemetry
- **Related concepts**: [[semantic-conventions-as-telemetry-schema]], [[telemetry-signal-model]], [[semantic-convention-validation-and-generation]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/semantic-conventions

## Summary

Think of the model as the master recipe for telemetry. It states an attribute's name, type, meaning, and where it belongs in a structured format that tools can read. Documentation and language-specific artifacts can then be produced from that one recipe instead of copied by hand.

This makes a change visible everywhere it matters. If a field is renamed in the model, validation, generated reference pages, and implementation helpers can all follow the same definition.

## Example

An HTTP model defines `http.request.method` as a string on a server span. A generator creates the reference table from that model, while validation rejects a proposed definition that uses a conflicting type. The team updates one model rather than three separate documents.

## Relationship to Existing Concepts

- [[semantic-conventions-as-telemetry-schema]]: The model is the executable form of the shared telemetry vocabulary.
- [[telemetry-signal-model]]: It describes fields for traces, metrics, logs, events, and resources.
- [[semantic-convention-validation-and-generation]]: Validation and generation consume this model.

## My Questions

- Which model changes should require a migration mapping rather than a simple documentation update?
- How can generated artifacts make their source model easy to trace?
