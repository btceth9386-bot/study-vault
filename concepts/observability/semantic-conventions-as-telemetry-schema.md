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
  - otlp-vendor-neutral-telemetry-protocol
  - llm-observability
  - microservices
tags:
  - observability
  - opentelemetry
  - distributed-systems
---

# Semantic Conventions as Telemetry Schema

- **One-sentence definition**: Semantic conventions are shared rules for the names and meanings of telemetry attributes, events, and metric fields.
- **Why it exists / what problem it solves**: Dashboards and alerts cannot be portable when every team uses different labels for the same HTTP method, database operation, or service identity.
- **Keywords**: schema, attributes, naming, service.name, HTTP, interoperability
- **Related concepts**: [[telemetry-signal-model]], [[resource-bound-telemetry-identity]], [[otlp-vendor-neutral-telemetry-protocol]], [[llm-observability]], [[microservices]]
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
- [[otlp-vendor-neutral-telemetry-protocol]]: OTLP moves telemetry; semantic conventions make the moved fields interpretable.
- [[llm-observability]]: Comparable model traces require stable names for model, prompt, tool, and evaluation data.
- [[microservices]]: A common vocabulary keeps cross-service dashboards from becoming a collection of custom translations.

## Open questions

- When should a team propose a shared convention rather than create a private attribute?
- How should dashboards handle convention changes during a schema migration?
