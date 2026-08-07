---
id: kubernetes-collector-placement-modes
title: Kubernetes Collector Placement Modes
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-opentelemetry-collector-contrib/
related:
  - collector-pipeline-architecture
  - microservices
tags:
  - observability
  - opentelemetry
  - collector
---

# Kubernetes Collector Placement Modes

- **One-sentence definition**: Kubernetes Collector placement chooses node-local agents, centralized gateways, or both based on where telemetry can be observed and processed.
- **Why it exists / what problem it solves**: Node logs and host metrics need local access, while aggregation and controlled egress work better in a shared tier.
- **Keywords**: Kubernetes, DaemonSet, Deployment, agent, gateway, placement
- **Related concepts**: [[collector-pipeline-architecture]], [[microservices]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/opentelemetry-collector-contrib

## Summary

Placement decides what a Collector can see. A DaemonSet runs one Collector on every node, so it can read node-local logs, host metrics, and local metadata. A Deployment runs a smaller central group of Collectors, which is better for aggregation, routing, and sending data outside the cluster. A common design uses both: agents collect locally and gateways handle shared processing.

## Example

Each node runs a DaemonSet Collector that tails container logs and collects host metrics. It forwards the data to a three-replica gateway Deployment, which removes sensitive fields and exports the result to the observability backend.

## Relationship to existing concepts

- [[collector-pipeline-architecture]]: Placement determines where the pipeline's receive, process, and export stages run.
- [[microservices]]: A shared collection design makes evidence from many independently deployed services easier to operate.

## Open questions

- Which telemetry needs node access and cannot be collected through a gateway?
- Where should expensive processing happen when clusters span several regions?
