---
id: a2a-agent-card-registry-discovery
title: A2A Agent Card and Registry Discovery
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/agent-tools---interoperability-day-2/
related:
  - protocol-based-agent-access-surface
  - agent-space-access-boundary
tags:
  - llm-engineering
  - a2a
  - interoperability
---

# A2A Agent Card and Registry Discovery

- **One-sentence definition**: An A2A Agent Card is a machine-readable profile of an agent, and a registry is the governed directory that lets other agents find that profile.
- **Why it exists / what problem it solves**: A specialist agent cannot be reused if callers must already know its address, capabilities, security rules, and message format. Cards and registries make those details discoverable.
- **Keywords**: A2A, Agent Card, registry, discovery, capabilities, interaction schema
- **Related concepts**: [[protocol-based-agent-access-surface]], [[agent-space-access-boundary]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: Agent Tools & Interoperability — Day 2

## Summary

An Agent Card is like a professional profile that software can read. It says what an agent can do, what security or compliance rules apply, and how another agent should talk to it. A registry is the directory that stores those profiles, whether it is a public marketplace or a private company catalog. Together, they let an orchestrator discover a specialist instead of relying on private knowledge of every endpoint.

## Example

An expense-report orchestrator needs a tax specialist. It searches the company registry, reads a candidate's Agent Card, sees that it handles tax classification and requires a finance role, then delegates only after the access boundary grants that role.

## Relationship to existing concepts

- [[protocol-based-agent-access-surface]]: An Agent Card explains how to use an A2A access surface and makes that surface discoverable.
- [[agent-space-access-boundary]]: Discovery does not grant access; the access boundary still limits what the chosen agent may use.

## My questions

- Which Agent Card fields should be mandatory before an agent can be listed in a private registry?
- How should a registry show that an agent's capabilities or security requirements have changed?
