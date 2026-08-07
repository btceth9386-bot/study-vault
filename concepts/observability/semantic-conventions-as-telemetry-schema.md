---
id: semantic-conventions-as-telemetry-schema
title: Semantic Conventions as Telemetry Schema
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-opentelemetry-specification/
related:
  - telemetry-signal-model
  - resource-bound-telemetry-identity
  - semantic-convention-model-as-source-of-truth
  - semantic-attribute-registry-reuse
  - telemetry-schema-migration-mappings
  - domain-owned-semantic-conventions
  - otlp-vendor-neutral-telemetry-protocol
  - llm-observability
  - microservices
  - collector-resource-detection-and-enrichment
  - genai-operation-span-taxonomy
tags:
  - observability
  - opentelemetry
  - distributed-systems
---

# Semantic Conventions as Telemetry Schema

- **One-sentence definition**: Semantic conventions are shared rules for the names and meanings of telemetry attributes, events, and metric fields.
- **Why it exists / what problem it solves**: Dashboards and alerts cannot be portable when every team uses different labels for the same HTTP method, database operation, or service identity.
- **Keywords**: schema, attributes, naming, service.name, HTTP, interoperability
- **Related concepts**: [[telemetry-signal-model]], [[resource-bound-telemetry-identity]], [[semantic-convention-model-as-source-of-truth]], [[semantic-attribute-registry-reuse]], [[telemetry-schema-migration-mappings]], [[domain-owned-semantic-conventions]], [[otlp-vendor-neutral-telemetry-protocol]], [[llm-observability]], [[microservices]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/opentelemetry-specification

## Summary

Semantic conventions are a shared dictionary for telemetry. They say not only that an attribute should be called `http.request.method`, for example, but also what the value means and where it belongs. They turn raw key-value data into a dependable schema.

The conventions do not replace application-specific fields. They standardize the common vocabulary first, so tools can provide reusable dashboards and queries while teams add their own domain attributes where needed.

## Example

Without a convention, one team records `method=GET`, another uses `http_method=GET`, and a third uses `verb=GET`. A shared dashboard must special-case all three. With a semantic convention, all emit `http.request.method=GET`, so one query works across services and vendors.

## Relationship to existing concepts

- [[telemetry-signal-model]]: Signal data becomes easier to query when its fields have common meanings.
- [[resource-bound-telemetry-identity]]: Resource attributes such as `service.name` are part of the shared schema.
- [[semantic-convention-model-as-source-of-truth]]: A machine-readable model makes the shared schema the source for derived artifacts.
- [[semantic-attribute-registry-reuse]]: A registry prevents domains from redefining common fields.
- [[telemetry-schema-migration-mappings]]: Versioned mappings translate the schema during a rollout.
- [[domain-owned-semantic-conventions]]: Domain experts and global reviewers govern schema changes together.
- [[otlp-vendor-neutral-telemetry-protocol]]: OTLP moves telemetry; semantic conventions make the moved fields interpretable.
- [[llm-observability]]: Comparable model traces require stable names for model, prompt, tool, and evaluation data.
- [[microservices]]: A common vocabulary keeps cross-service dashboards from becoming a collection of custom translations.
- [[collector-resource-detection-and-enrichment]]: Detected resource fields need standard names and meanings.
- [[genai-operation-span-taxonomy]]: The taxonomy applies shared schema rules to model, retrieval, memory, and tool spans.

## Open questions

- When should a team propose a shared convention rather than create a private attribute?
- How should dashboards handle convention changes during a schema migration?
