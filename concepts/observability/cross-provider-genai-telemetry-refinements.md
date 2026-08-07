---
id: cross-provider-genai-telemetry-refinements
title: Cross-Provider GenAI Telemetry Refinements
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-semantic-conventions-genai/
related:
  - semantic-attribute-registry-reuse
  - domain-owned-semantic-conventions
tags:
  - observability
  - opentelemetry
  - generative-ai
  - semantic-conventions
  - provider-integrations
---

# Cross-Provider GenAI Telemetry Refinements

- **One-sentence definition**: Cross-provider refinements keep a shared GenAI telemetry core while adding fields for capabilities that only some providers expose.
- **Why it exists / what problem it solves**: A lowest-common-denominator schema loses useful details, but separate schemas make instrumentation and dashboards impossible to reuse.
- **Keywords**: provider, shared schema, extensions, interoperability, attributes
- **Related concepts**: [[semantic-attribute-registry-reuse]], [[domain-owned-semantic-conventions]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: OpenTelemetry Semantic Conventions for Generative AI

## Summary

The shared `gen_ai.*` vocabulary is the common language used by every provider. A refinement adds a provider-specific field only when the capability is genuinely different, rather than renaming the common fields.

That lets a dashboard compare model latency across providers while still exposing details such as an AWS Bedrock guardrail or knowledge-base identifier when present.

## Example

An application emits `gen_ai.provider.name` and `gen_ai.operation.name` for every inference call. For a Bedrock call using a guardrail, it also records `aws.bedrock.guardrail.id`. Generic queries use the shared fields; Bedrock troubleshooting can use the extra field.

## Relationship to existing concepts

- [[semantic-attribute-registry-reuse]]: Refinements reuse shared fields instead of copying or redefining them.
- [[domain-owned-semantic-conventions]]: Provider experts own the extra fields while shared governance protects interoperability.

## My questions

- What evidence shows that a provider detail is stable enough to standardize?
- How should dashboards behave when a provider-specific attribute is absent?
