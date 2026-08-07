---
id: semantic-attribute-registry-reuse
title: Semantic Attribute Registry Reuse
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-semantic-conventions/
related:
  - semantic-conventions-as-telemetry-schema
  - resource-bound-telemetry-identity
  - semantic-convention-model-as-source-of-truth
  - cross-provider-genai-telemetry-refinements
tags:
  - observability
  - opentelemetry
  - semantic-conventions
---

# Semantic Attribute Registry Reuse

- **One-sentence definition**: A semantic attribute registry defines reusable telemetry fields once so domain models can reference them instead of creating local copies.
- **Why it exists / what problem it solves**: Reuse keeps field names, types, and meanings consistent across signals and technology domains.
- **Keywords**: registry, attributes, reuse, inheritance, schema, interoperability
- **Related concepts**: [[semantic-conventions-as-telemetry-schema]], [[resource-bound-telemetry-identity]], [[semantic-convention-model-as-source-of-truth]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/semantic-conventions

## Summary

The registry is a shared parts catalog for telemetry fields. Instead of every HTTP, database, or messaging model writing its own version of a service or network attribute, it points to the same registered definition. A domain can still say when that attribute is needed, but it does not get to change what the attribute means.

This saves more than typing. It keeps tools from having to guess whether similarly named fields hold the same kind of value.

## Example

Both an HTTP span and a resource model need a service name. They reference the registry definition for `service.name`, so both use the same name and meaning. The HTTP model can mark it as recommended without redefining the field.

## Relationship to Existing Concepts

- [[semantic-conventions-as-telemetry-schema]]: The registry provides the common fields that make the schema consistent.
- [[resource-bound-telemetry-identity]]: Resource identity is built from registered attributes such as `service.name`.
- [[semantic-convention-model-as-source-of-truth]]: The registry is part of the model from which artifacts are derived.
- [[cross-provider-genai-telemetry-refinements]]: Provider extensions reuse the shared GenAI fields before adding a genuinely unique one.

## My Questions

- When is a new attribute general enough to belong in the shared registry?
- How should a domain document a temporary exception without creating a permanent duplicate?
