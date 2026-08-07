---
id: collector-storage-extensions
title: Collector Storage Extensions
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-opentelemetry-collector-contrib/
related:
  - collector-extensions
  - collector-exporter-resilience
tags:
  - observability
  - opentelemetry
  - collector
---

# Collector Storage Extensions

- **One-sentence definition**: Storage extensions give Collector components scoped, backend-neutral places to keep state across restarts.
- **Why it exists / what problem it solves**: Components need durable checkpoints and queues without embedding file, database, or Redis code.
- **Keywords**: storage, checkpoint, queue, persistence, extension
- **Related concepts**: [[collector-extensions]], [[collector-exporter-resilience]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/opentelemetry-collector-contrib

## Summary

A storage extension is a shared locker service for Collector components. A component asks for its own scoped client, then saves state without needing to know which storage backend is behind it. This makes durable behavior reusable and prevents one component's state from accidentally mixing with another's.

## Example

An exporter stores its sending queue through a storage extension. After the Collector restarts during a backend outage, it can resume sending the queued telemetry instead of starting with an empty queue.

## Relationship to existing concepts

- [[collector-extensions]]: Storage is an operational service that supports, rather than transforms, telemetry.
- [[collector-exporter-resilience]]: Persistent queues can preserve exporter work across process restarts.

## Open questions

- Which state must survive a restart, and which is safe to rebuild?
- How should storage be sized so a downstream outage cannot fill the node's disk?
