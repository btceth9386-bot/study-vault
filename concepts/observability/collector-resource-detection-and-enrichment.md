---
id: collector-resource-detection-and-enrichment
title: Collector Resource Detection and Enrichment
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-opentelemetry-collector-contrib/
related:
  - resource-bound-telemetry-identity
  - semantic-conventions-as-telemetry-schema
tags:
  - observability
  - opentelemetry
  - collector
---

# Collector Resource Detection and Enrichment

- **One-sentence definition**: Resource detection finds where telemetry was produced and adds that identity as resource attributes.
- **Why it exists / what problem it solves**: Applications often do not know their final cloud, host, container, or Kubernetes environment.
- **Keywords**: resource, detector, cloud, host, container, enrichment
- **Related concepts**: [[resource-bound-telemetry-identity]], [[semantic-conventions-as-telemetry-schema]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/opentelemetry-collector-contrib

## Summary

A resource detector is like a luggage tag printer at the airport: it labels telemetry with the machine or environment it came from. The Collector can run ordered, pluggable detectors for cloud, host, container, and orchestration data, then merge their results into each signal's resource. This lets applications stay portable while operators still see useful runtime identity.

## Example

A service only sends its name. In Kubernetes, the resource detection processor adds the cluster name, node, namespace, pod, and cloud region, so an alert can identify the failing workload without changing the service.

## Relationship to existing concepts

- [[resource-bound-telemetry-identity]]: Detection supplies the identity attached to telemetry.
- [[semantic-conventions-as-telemetry-schema]]: Detected attributes need standard names so tools interpret them consistently.

## Open questions

- Which detector should win when cloud and deployment configuration disagree?
- Which resource fields may reveal more infrastructure detail than a backend should receive?
