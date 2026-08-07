---
id: opamp-supervised-collector-fleet-management
title: OpAMP-Supervised Collector Fleet Management
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-opentelemetry-collector-contrib/
related:
  - collector-configuration-providers
  - collector-component-factory-lifecycle
tags:
  - observability
  - opentelemetry
  - collector
---

# OpAMP-Supervised Collector Fleet Management

- **One-sentence definition**: An OpAMP Supervisor is a local process that connects a remote control plane to one managed Collector.
- **Why it exists / what problem it solves**: Large fleets need consistent remote configuration and health feedback without direct ad hoc control of every host process.
- **Keywords**: OpAMP, supervisor, fleet, remote configuration, health, control plane
- **Related concepts**: [[collector-configuration-providers]], [[collector-component-factory-lifecycle]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/opentelemetry-collector-contrib

## Summary

The OpAMP Supervisor is a local manager between a remote operations service and a Collector process. It receives approved configuration changes, manages the Collector's identity and lifecycle, and reports health back to the control plane. This gives fleet operators one managed path for change while keeping the control plane from directly poking every Collector process.

## Example

An operations team publishes a new exporter endpoint. Each Supervisor receives it, builds the effective configuration, reloads or restarts its Collector, and reports whether the new process became healthy. The control plane can then identify failures without logging into each host.

## Relationship to existing concepts

- [[collector-configuration-providers]]: Remote configuration becomes an input to the Collector's configuration-resolution process.
- [[collector-component-factory-lifecycle]]: The Supervisor starts, reloads, and checks the runtime that manages Collector components.

## Open questions

- Which configuration changes are safe to reload without a full restart?
- How should a fleet roll back a change that passes validation but fails under load?
