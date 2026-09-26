---
id: memory-namespace-multi-tenant-isolation
title: Memory Namespace Multi-Tenant Isolation
depth: 2
lab_status: not-started
last_reviewed: 2026-09-26
review_due: 2026-09-29
sources:
  - sources/papers/bedrock-agentcore-multi-agent
related:
  - layered-agent-memory
  - langgraph-store-long-term-memory
  - cross-account-memory-resource-sharing
  - memory-poisoning-defense-in-agent-systems
tags:
  - aws
  - agentcore
  - agent-memory
  - multi-tenancy
  - access-control
---

# Memory Namespace Multi-Tenant Isolation

- **One-sentence definition**: A memory namespace is a hierarchical, slash-delimited, trailing-slash-terminated path (like `/strategy/{id}/actor/{id}/session/{id}/`) that organizes long-term memory records so one memory resource can be safely shared across many actors or agents without their data mixing — and the same path doubles as an IAM condition key for access control.
- **Why it exists / what problem it solves**: A multi-agent system that shares one memory resource — say, a team of agents jointly managing supply-chain inventory — needs a way to keep each actor's or agent's data from bleeding into another's, or one agent's extracted insights from silently overwriting a different agent's. Namespaces solve this by encoding ownership directly into where a memory record lives, using variables (`actorId`, `sessionId`, `strategyId`) that get substituted in at write time, with four selectable granularities from global (`/`) down to per-session. The design also closes a subtle bug: a namespace must end in a trailing slash (`/actors/Alice/`, not `/actors/Alice`) so that a prefix match doesn't accidentally treat `Alice2` as part of `Alice`'s data. Because the exact same path string is also usable as an IAM policy condition key (`bedrock-agentcore:namespace` / `namespacePath`), the organizational scheme becomes an enforceable access boundary, not just a filing convention.
- **Keywords**: namespace, hierarchical path, trailing slash, actor ID, IAM condition key, multi-tenancy
- **Related concepts**: [[layered-agent-memory]], [[langgraph-store-long-term-memory]], [[cross-account-memory-resource-sharing]], [[memory-poisoning-defense-in-agent-systems]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: Amazon Bedrock AgentCore Developer Guide — Multi-agent runtime, A2A, shared memory, and Agent Registry

## Summary

Think of a namespace as a labeled folder structure in a shared filing cabinet, where the label itself can also be checked by a security guard. A path like `/strategy/summarization-93483043/actor/actor-9830m2w3/session/session-9330sds8/` tells the system exactly which strategy, which user, and which conversation a memory record belongs to — and a team can choose to file records at any level of that hierarchy, from "everything, globally" down to "just this one session." The trailing slash matters for the same reason a folder name matters in a filesystem: without it, a search for `Alice` would also match a folder named `Alice2`, silently leaking data across what should be separate tenants.

## Example

A memory strategy is configured with the namespace template `/strategy/{memoryStrategyId}/actor/{actorId}/`. Two customer-support agents share the same AgentCore Memory resource but serve different customers. Customer A's extracted preferences land under `/strategy/support-summarizer/actor/customer-A/`, and Customer B's under `/strategy/support-summarizer/actor/customer-B/`. An IAM policy condition restricting `bedrock-agentcore:namespace` to `customer-A`'s path means even a bug in the agent's code can't accidentally retrieve Customer B's memories — the isolation is enforced by the platform, not just by careful coding.

## Relationship to existing concepts

- [[layered-agent-memory]]: That concept organizes memory by lifecycle (working, session, long-term, episodic). This concept is a concrete organizational scheme for the long-term layer specifically, needed once that layer must be safely shared across many actors or agents instead of belonging to a single conversation.
- [[langgraph-store-long-term-memory]]: LangGraph's store uses a similar idea — a namespaced, path-based key-value layer for long-term memory. The difference here is that AgentCore additionally wires the namespace into IAM conditions, turning a logical partition into an enforced access boundary rather than just an organizational convention.
- [[cross-account-memory-resource-sharing]]: Namespaces solve isolation *within* one account's memory resource; cross-account sharing solves the separate problem of which *other AWS accounts* may reach that resource at all. A real deployment typically needs both.
- [[memory-poisoning-defense-in-agent-systems]]: Namespacing limits the blast radius of a poisoning attack — if one actor's conversation is compromised, namespace isolation keeps the corrupted content from being retrieved into a different actor's context.

## My questions

- How granular should a namespace be by default — per-session for maximum isolation, or per-actor for simpler retrieval, and what's the cost of choosing wrong early?
- Can a namespace be restructured after records already exist under the old hierarchy, or does that require a migration?
