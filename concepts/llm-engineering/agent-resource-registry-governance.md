---
id: agent-resource-registry-governance
title: Agent Resource Registry Governance
depth: 2
lab_status: not-started
last_reviewed: 2026-09-26
review_due: 2026-09-29
sources:
  - sources/papers/bedrock-agentcore-multi-agent
related:
  - a2a-agent-card-registry-discovery
  - agent-space-access-boundary
tags:
  - aws
  - agentcore
  - agent-registry
  - governance
  - multi-agent-systems
---

# Agent Resource Registry Governance

- **One-sentence definition**: An agent resource registry is a centralized, curated catalog where teams publish MCP servers, agents, and skills through an approval workflow so both people and other agents can find and reuse them instead of rebuilding what already exists.
- **Why it exists / what problem it solves**: Once an organization has more than a handful of teams building agents, resources go dark — nobody outside the team that built a tool knows it exists, so it gets rebuilt, and nobody can vouch for whether it meets security or quality standards. A registry fixes both problems at once: a publish → review → approve/deprecate workflow keeps only vetted resources discoverable, and hybrid (semantic + keyword) search plus a native MCP endpoint let both humans and other agents actually find them.
- **Keywords**: agent registry, discovery, approval workflow, hybrid search, MCP endpoint, governance, deprecation
- **Related concepts**: [[a2a-agent-card-registry-discovery]], [[agent-space-access-boundary]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: Amazon Bedrock AgentCore Developer Guide — Multi-agent runtime, A2A, shared memory, and Agent Registry

## Summary

Think of a registry as a moderated app store for internal agents and tools, not a wiki page anyone can edit unchecked. A publisher submits a record describing what their MCP server, agent, or skill does; a curator (or an auto-approval rule in a dev environment) reviews it before it becomes searchable. Once approved, it shows up in both keyword search ("weather-api-v2") and natural-language search ("find a tool that can book flights"), and it's also reachable through the registry's own MCP endpoint, so an agent can query the catalog the same way it would call any other MCP tool. If a resource is later found to be unsafe or obsolete, a curator deprecates it — it disappears from search without breaking whatever already depends on it.

## Example

A platform team stands up one company-wide registry. The payments team publishes their fraud-check MCP server as a record; it sits pending until a curator approves it. Six months later, a new hire building a checkout agent searches the registry for "detect fraudulent transactions," finds the approved fraud-check server through semantic search, and wires it in — without ever asking around or rebuilding a duplicate.

## Relationship to existing concepts

- [[a2a-agent-card-registry-discovery]]: That concept describes the general idea of an Agent Card plus a registry that stores it. This concept is AWS's concrete productization of that idea, adding the governance layer on top — an approval/deprecation workflow, EventBridge notifications that plug into existing review pipelines, and a choice between IAM and JWT authorization for who can search and invoke the registry.
- [[agent-space-access-boundary]]: A registry answers "can this resource be found?" An access boundary answers "can the caller actually use it once found?" A complete multi-agent governance story needs both — discovery without an access boundary would let anyone invoke anything they find.

## My questions

- How should a registry signal that an approved resource's capabilities or security posture changed since it was last approved?
- At what team size does the overhead of a review workflow start paying for itself versus auto-approval?
