---
id: resource-bound-telemetry-identity
title: Resource-Bound Telemetry Identity
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-opentelemetry-specification/
related:
  - telemetry-signal-model
  - semantic-conventions-as-telemetry-schema
  - semantic-attribute-registry-reuse
  - context-propagation-with-carriers
  - llm-observability
  - microservices
  - collector-resource-detection-and-enrichment
  - observer-driven-dynamic-receivers
tags:
  - observability
  - opentelemetry
  - distributed-systems
---

# Resource-Bound Telemetry Identity

- **One-sentence definition**: Resource-bound telemetry identity attaches stable metadata about the producing service, process, host, container, or cloud resource to its telemetry.
- **Why it exists / what problem it solves**: A span or metric is hard to act on when it does not say which deployed workload emitted it.
- **Keywords**: resource, service.name, host, container, cloud, identity
- **Related concepts**: [[telemetry-signal-model]], [[semantic-conventions-as-telemetry-schema]], [[semantic-attribute-registry-reuse]], [[context-propagation-with-carriers]], [[llm-observability]], [[microservices]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/opentelemetry-specification

## Summary

A resource describes the thing producing telemetry, not the request it is currently handling. Typical fields include a service name, service version, deployment environment, host name, container ID, and cloud account. An SDK binds this information to every signal emitted by its provider.

Keeping resource identity separate from request context prevents repeated fields and makes grouping reliable. A dashboard can filter all spans and metrics from `checkout-api` in production even when they come from many short-lived containers.

## Example

Three replicas of `payments-api` emit the same `http.server.duration` metric. Resource attributes label every point with `service.name=payments-api`, `deployment.environment=production`, and the current container identity. An on-call engineer can group by service, then narrow to one unhealthy replica.

## Relationship to existing concepts

- [[telemetry-signal-model]]: Resources provide the producer identity shared by all telemetry signals.
- [[semantic-conventions-as-telemetry-schema]]: Standard resource attribute names let tools and teams interpret identity consistently.
- [[semantic-attribute-registry-reuse]]: The registry provides the reusable definitions for resource fields such as `service.name`.
- [[context-propagation-with-carriers]]: Resource identity stays with the producer, while context follows an individual request.
- [[llm-observability]]: Model and tool traces become more actionable when linked to the deployed service and environment.
- [[microservices]]: Resources make service ownership and deployment context visible across many independent workloads.
- [[collector-resource-detection-and-enrichment]]: Detectors supply runtime attributes for resource identity.
- [[observer-driven-dynamic-receivers]]: Discovery metadata identifies the targets that dynamic receivers collect from.

## Open questions

- Which resource attributes should be required in every production service?
- How can teams keep ephemeral container and cloud metadata accurate without exposing sensitive infrastructure details?
