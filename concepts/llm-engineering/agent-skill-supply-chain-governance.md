---
id: agent-skill-supply-chain-governance
title: Agent Skill Supply-Chain Governance
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/agent-skills-day-3
related:
  - secure-mcp-consumption-lifecycle
  - agent-space-access-boundary
  - hallucinated-package-slopsquatting-defense
tags:
  - agent-skills
  - llm-engineering
  - security
  - supply-chain
---

# Agent Skill Supply-Chain Governance

- **One-sentence definition**: Agent skill supply-chain governance treats installed skills as software dependencies that need trusted sources, pinned versions, review, scanning, ownership, and regression tests.
- **Why it exists / what problem it solves**: A skill can run code and use privileged tools, so an unreviewed or silently changing package can become a security or operational risk.
- **Keywords**: provenance, version pinning, code review, security scan, ownership, dependencies
- **Related concepts**: [[secure-mcp-consumption-lifecycle]], [[agent-space-access-boundary]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: Agent Skills

## Summary

Installing a skill is closer to adding a library than copying a note. It may bring scripts, dependencies, and instructions that steer an agent with real access. Prefer first-party or organization-curated sources, pin the exact version, scan and review changes, and assign an owner. Testing after adoption catches both security surprises and behavior that changes under a new release.

## Example

Before adding a community deployment skill, a team checks its publisher, pins its version, scans bundled scripts and dependencies, reviews it in a pull request, and runs its regression suite with read-only staging credentials. The platform team owns future updates.

## Relationship to existing concepts

- [[secure-mcp-consumption-lifecycle]]: Both apply provenance, least privilege, verification, and observation to agent integrations.
- [[agent-space-access-boundary]]: Runtime access limits reduce the damage a compromised or flawed skill can cause.
- [[hallucinated-package-slopsquatting-defense]]: Applies the same dependency-governance controls to packages proposed by a coding agent.

## My questions

- Which skill changes require a fresh human security review rather than an automated update?
- How should a team revoke a skill version that is already installed across many agents?
