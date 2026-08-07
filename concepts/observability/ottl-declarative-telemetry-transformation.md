---
id: ottl-declarative-telemetry-transformation
title: OTTL Declarative Telemetry Transformation
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-opentelemetry-collector-contrib/
related:
  - collector-pipeline-architecture
  - telemetry-signal-model
  - telemetry-schema-migration-mappings
tags:
  - observability
  - opentelemetry
  - collector
---

# OTTL Declarative Telemetry Transformation

- **One-sentence definition**: OTTL is a small language for filtering and changing telemetry using paths, functions, and optional conditions.
- **Why it exists / what problem it solves**: It lets operators normalize, redact, enrich, or route telemetry without writing a custom processor for every policy.
- **Keywords**: OTTL, transformation, filter, redact, condition, telemetry
- **Related concepts**: [[collector-pipeline-architecture]], [[telemetry-signal-model]], [[telemetry-schema-migration-mappings]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/opentelemetry-collector-contrib

## Summary

OTTL is a rule language for editing telemetry in a Collector. A statement selects a value through a context-aware path, calls a function to change or inspect it, and can add a `where` condition to limit when the rule runs. Think of it as a set of spreadsheet formulas for traces, metrics, and logs: configuration describes the policy, while the Collector applies it consistently.

## Example

Before exporting logs, an OTTL rule can replace a `user.email` attribute with `"redacted"` only when it exists. The privacy rule lives in Collector configuration, so every service receives the same protection without a code change.

## Relationship to existing concepts

- [[collector-pipeline-architecture]]: OTTL commonly runs in a processor stage of a telemetry pipeline.
- [[telemetry-signal-model]]: Its paths and functions operate on the attributes and fields of telemetry signals.
- [[telemetry-schema-migration-mappings]]: Transformations can apply version-to-version schema translations to telemetry in flight.

## Open questions

- Which transformations should be applied at collection time rather than in the backend?
- How can a team test an OTTL rule against representative telemetry before deployment?
