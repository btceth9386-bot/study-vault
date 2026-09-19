---
id: context-propagation-with-carriers
title: Context Propagation with Carriers
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-opentelemetry-specification/
related:
  - telemetry-signal-model
  - consistent-probability-sampling
  - llm-observability
  - microservices
  - agentic-workflow-span-hierarchy
  - mcp-client-server-trace-correlation
  - trace-aware-agent-evaluation
tags:
  - observability
  - opentelemetry
  - distributed-systems
---

# Context Propagation with Carriers

- **One-sentence definition**: Context propagation keeps request-scoped trace state and baggage intact by injecting it into, and extracting it from, transport-specific carriers such as HTTP headers.
- **Why it exists / what problem it solves**: A trace becomes disconnected when a downstream service cannot recover the upstream request identity or the metadata that should travel with it.
- **Keywords**: context, carrier, inject, extract, headers, baggage
- **Related concepts**: [[telemetry-signal-model]], [[consistent-probability-sampling]], [[llm-observability]], [[microservices]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/opentelemetry-specification

## Summary

Context is a small immutable package attached to the current operation. Before a service calls another service, a propagator injects the relevant context into a carrier, such as HTTP request headers. The receiving service extracts it and makes it the current context before starting its own work.

This is what turns local spans into one distributed trace. It can also carry baggage: application-defined key-value data such as a tenant identifier, used carefully because it crosses trust and network boundaries.

## Example

Service A receives a request with trace ID `abc`, starts a span, and calls Service B. Its HTTP client injects trace context into `traceparent`. Service B extracts that header, so its database span becomes a child of Service A's request instead of a separate trace.

## Relationship to existing concepts

- [[telemetry-signal-model]]: Propagation is the correlation mechanism shared by several telemetry signals.
- [[consistent-probability-sampling]]: Sampling decisions need propagation so downstream services make compatible decisions.
- [[llm-observability]]: Tool calls and service requests in an AI workflow need shared context to remain traceable.
- [[microservices]]: Network boundaries are exactly where propagation prevents distributed debugging from breaking apart.
- [[agentic-workflow-span-hierarchy]]: Propagation preserves parent-child context when agent work crosses processes.
- [[mcp-client-server-trace-correlation]]: MCP client and server spans depend on injection and extraction across their boundary.
- [[trace-aware-agent-evaluation]]: Propagation keeps distributed tool calls together so their full trajectory can be tested.

## Open questions

- Which baggage values are safe to send to downstream services and external vendors?
- How should a service handle malformed or untrusted incoming propagation headers?
