---
id: consistent-probability-sampling
title: Consistent Probability Sampling
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-opentelemetry-specification/
related:
  - context-propagation-with-carriers
  - telemetry-signal-model
  - llm-observability
  - microservices
tags:
  - observability
  - opentelemetry
  - distributed-systems
---

# Consistent Probability Sampling

- **One-sentence definition**: Consistent probability sampling uses shared randomness and threshold information so services make compatible decisions about keeping or dropping a distributed trace.
- **Why it exists / what problem it solves**: Independent sampling at each service can leave broken traces with missing downstream spans, reducing the value of the data saved for its cost.
- **Keywords**: sampling, trace, probability, threshold, randomness, cost control
- **Related concepts**: [[context-propagation-with-carriers]], [[telemetry-signal-model]], [[llm-observability]], [[microservices]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/opentelemetry-specification

## Summary

Sampling controls observability cost by retaining only some traces. Consistent probability sampling does not let each service flip an unrelated coin. Instead, it carries enough information for every service on the request path to compare the same trace value with a compatible threshold.

The result is coherent: a trace selected upstream is more likely to remain complete downstream, even when services use different sampling rates. This gives operators better evidence than a random collection of partial request fragments.

## Example

An edge service samples 10% of requests and propagates the sampling threshold with the trace context. A downstream payment service has its own policy but uses the same trace randomness. When the trace qualifies for retention, both services keep their spans, preserving one end-to-end checkout trace.

## Relationship to existing concepts

- [[context-propagation-with-carriers]]: Sampling state must travel through carriers for downstream services to make compatible decisions.
- [[telemetry-signal-model]]: Sampling preserves useful trace data while controlling the cost of the signal model.
- [[llm-observability]]: Complete traces are especially useful when analyzing multi-step model and tool workflows.
- [[microservices]]: Distributed requests cross enough services that independent sampling quickly produces misleading partial traces.

## Open questions

- What sampling rate retains enough rare failures for incident investigation?
- Which traces should be retained deterministically even when the normal probability threshold rejects them?
