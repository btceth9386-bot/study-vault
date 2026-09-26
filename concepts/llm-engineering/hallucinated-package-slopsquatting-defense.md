---
id: hallucinated-package-slopsquatting-defense
title: Hallucinated-Package Slopsquatting Defense
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/vibe-coding-agent-security-and-evaluation-day-4
related:
  - agent-skill-supply-chain-governance
tags:
  - coding-agents
  - security
  - supply-chain
  - dependencies
---

# Hallucinated-Package Slopsquatting Defense

- **One-sentence definition**: Hallucinated-package slopsquatting defense prevents an agent from installing an attacker-published package under a dependency name invented by a model.
- **Why it exists / what problem it solves**: A coding agent can turn a fabricated name into a malware installation before anyone notices that the package was never legitimate.
- **Keywords**: slopsquatting, dependencies, package registry, SBOM, version pinning
- **Related concepts**: [[agent-skill-supply-chain-governance]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: Vibe Coding Agent Security and Evaluation

## Summary

Models sometimes confidently name packages that do not exist. Attackers can watch for those invented names and publish malware under them, hoping an agent installs it later; this is called slopsquatting. Defend against it by allowing dependencies only from vetted providers or internal registries, pinning exact versions, and making CI verify the bill of materials and signatures before release.

## Example

An agent suggests installing `fast-json-streamer`, a package absent from the team's approved registry. Dependency policy rejects it instead of fetching it from the public internet. The agent must use an approved alternative or request a reviewed dependency addition.

## Relationship to existing concepts

- [[agent-skill-supply-chain-governance]]: Applies the same provenance, review, pinning, and ownership discipline to agent skills.

## My questions

- How can a dependency policy distinguish a legitimate new package from a model-invented one?
- Which signature and SBOM checks should be mandatory before production?
