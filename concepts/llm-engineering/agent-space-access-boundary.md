---
id: agent-space-access-boundary
title: Agent Space Access Boundary
depth: 2
lab_status: not-started
last_reviewed: 2026-07-11
review_due: 2026-07-14
sources:
  - sources/articles/aws-devops-agent-docs/
related:
  - authority-tiered-agent-skills
  - agent-skill-supply-chain-governance
  - hierarchical-rbac
  - toolsets-and-mcp-unified-tool-surface
  - protocol-based-agent-access-surface
  - release-readiness-blast-radius-review
  - coding-agent-harness-engineering
  - a2a-agent-card-registry-discovery
  - secure-mcp-consumption-lifecycle
  - ucp-ap2-commerce-payment-separation
  - effective-trust-for-agents
  - ephemeral-agent-execution-sandbox
  - zero-ambient-authority-for-agents
  - agent-resource-registry-governance
tags:
  - llm-engineering
  - aws
  - devops-agent
  - ai-agent
  - access-control
---

# Agent Space Access Boundary

- **One-sentence definition**: An Agent Space access boundary is a named operational scope that defines which accounts, integrations, identities, and permissions an AI operations agent can use.
- **Why it exists / what problem it solves**: A DevOps agent needs enough visibility to inspect incidents, deployments, repositories, telemetry, and tickets, but giving one global agent access to everything is unsafe. Agent Spaces make the boundary explicit.
- **Keywords**: Agent Space, access boundary, IAM, integrations, operational scope
- **Related concepts**: [[authority-tiered-agent-skills]], [[agent-skill-supply-chain-governance]], [[hierarchical-rbac]], [[toolsets-and-mcp-unified-tool-surface]], [[protocol-based-agent-access-surface]], [[release-readiness-blast-radius-review]], [[coding-agent-harness-engineering]]
- **Depth**: 2/4
- **Last updated**: 2026-07-11
- **Source**: sources/articles/aws-devops-agent-docs/

## Summary

Think of an Agent Space as a workspace with a locked tool cabinet. The agent can only use the accounts, tools, credentials, integrations, and permissions that have been placed inside that workspace. This matters because operational agents are powerful: they can inspect infrastructure, correlate incident data, and trigger workflows. A clear access boundary lets a team create different operational scopes for different applications, environments, or teams instead of relying on one unrestricted agent.

## Example

A platform team manages production payments and a separate internal analytics application. They create one Agent Space for payments with access to payment CloudWatch metrics, PagerDuty incidents, GitHub repositories, and strict IAM roles. They create another Agent Space for analytics with different accounts and Slack channels. When the payments agent investigates an incident, it cannot accidentally inspect or act on analytics resources.

## Relationship to existing concepts

- [[authority-tiered-agent-skills]]: Access boundaries constrain the systems and permissions available at each authority tier.
- [[agent-skill-supply-chain-governance]]: Access boundaries limit the blast radius of untrusted or flawed skill packages.
- [[hierarchical-rbac]]: Both concepts define how access is scoped across nested operational boundaries.
- [[toolsets-and-mcp-unified-tool-surface]]: Tool surfaces need an access boundary so available tools match the current operational context.
- [[protocol-based-agent-access-surface]]: External clients should connect through a scoped Agent Space rather than invoking an unrestricted agent.
- [[release-readiness-blast-radius-review]]: Release review can only inspect the repositories, accounts, and integrations available inside the relevant Agent Space.
- [[coding-agent-harness-engineering]]: Access boundaries are enforceable constraints in an agent harness.
- [[a2a-agent-card-registry-discovery]]: Discovering an agent does not override the access boundary governing it.
- [[secure-mcp-consumption-lifecycle]]: Scoped credentials and permissions are a core step in secure MCP consumption.
- [[ucp-ap2-commerce-payment-separation]]: Merchant and payment capabilities should remain inside a least-privilege access boundary.
- [[effective-trust-for-agents]]: The boundary is one input to the live decision about whether an agent may continue.
- [[ephemeral-agent-execution-sandbox]]: Sandboxes receive only the resources permitted by the boundary.
- [[zero-ambient-authority-for-agents]]: Task-scoped credentials enforce the boundary without inherited privilege.
- [[agent-resource-registry-governance]]: A registry answers whether a resource can be found; the access boundary still governs whether the discovering agent may use it.

## Open questions

- When should a team split one broad Agent Space into several smaller spaces?
- How should Agent Space boundaries map to environments such as development, staging, and production?
