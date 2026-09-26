---
id: opentelemetry-api-sdk-separation
title: OpenTelemetry API-SDK Separation
depth: 2
lab_status: scaffolded
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-opentelemetry-specification/
related:
  - telemetry-signal-model
  - otlp-vendor-neutral-telemetry-protocol
  - llm-observability
  - agentcore-managed-service-telemetry-defaults
tags:
  - observability
  - opentelemetry
---

# OpenTelemetry API-SDK Separation

- **One-sentence definition**: OpenTelemetry keeps instrumentation interfaces separate from the SDK that processes and exports telemetry.
- **Why it exists / what problem it solves**: A library should be able to report useful telemetry without choosing a vendor or forcing an application to install one particular runtime implementation.
- **Keywords**: instrumentation, API, SDK, provider, exporter, no-op
- **Related concepts**: [[telemetry-signal-model]], [[otlp-vendor-neutral-telemetry-protocol]], [[llm-observability]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/opentelemetry-specification

## Summary

Think of the API as the standard socket and the SDK as the appliance plugged into it. A library calls a `Tracer` or `Meter` from the API to describe what happened. The application selects an SDK later to decide where data goes, what gets sampled, and which exporter sends it.

This separation lets the same library work with many telemetry backends. It also keeps instrumentation safe when an application has not installed an SDK: the API can behave as a no-op instead of making the library fail.

## Example

An HTTP library creates a span through the OpenTelemetry API when it sends a request. One application installs an SDK that exports the span to a collector; another installs no SDK and pays almost no runtime cost. The library code does not change in either case.

## Relationship to existing concepts

- [[telemetry-signal-model]]: The API exposes the instruments used to create different telemetry signals.
- [[otlp-vendor-neutral-telemetry-protocol]]: An SDK can export the API-created data through OTLP.
- [[llm-observability]]: AI applications can instrument model and tool calls without binding their code to one observability vendor.
- [[agentcore-managed-service-telemetry-defaults]]: ADOT, AWS's redistribution of the OpenTelemetry SDK, is the standard instrumentation path AgentCore documents for the traces its managed resources do not emit by default.

## Open questions

- Which instrumentation belongs in a reusable library, and which belongs only in the application that deploys it?
- When should an application prefer automatic instrumentation over explicit spans?
