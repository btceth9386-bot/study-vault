---
id: observer-driven-dynamic-receivers
title: Observer-Driven Dynamic Receivers
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-opentelemetry-collector-contrib/
related:
  - collector-component-factory-lifecycle
  - resource-bound-telemetry-identity
tags:
  - observability
  - opentelemetry
  - collector
---

# Observer-Driven Dynamic Receivers

- **One-sentence definition**: Observer-driven collection turns discovered endpoints into receiver instances that start and stop with those endpoints.
- **Why it exists / what problem it solves**: Containers, pods, services, and ports change too quickly for a fixed scrape-target list.
- **Keywords**: observer, discovery, receiver, endpoint, dynamic configuration
- **Related concepts**: [[collector-component-factory-lifecycle]], [[resource-bound-telemetry-identity]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/opentelemetry-collector-contrib

## Summary

An observer watches an environment and reports when an endpoint appears, changes, or disappears. Rules turn those events into validated receiver configuration, and the Receiver Creator starts or stops the matching receiver. This is like a hotel assigning and clearing rooms as guests arrive and leave: the Collector only collects from targets that currently exist, while retaining the metadata that says what each target is.

## Example

When Kubernetes creates a pod exposing a metrics port, an observer reports the endpoint. A rule creates a Prometheus receiver for that port and attaches pod labels; when the pod ends, the receiver is stopped automatically.

## Relationship to existing concepts

- [[collector-component-factory-lifecycle]]: Dynamic receivers use the same creation and shutdown lifecycle as static components.
- [[resource-bound-telemetry-identity]]: Discovery metadata helps identify the workload that produced the collected telemetry.

## Open questions

- Which discovery events should be debounced to avoid receiver churn?
- How should invalid endpoint templates be reported without stopping unrelated receivers?
