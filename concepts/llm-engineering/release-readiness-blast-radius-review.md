---
id: release-readiness-blast-radius-review
title: Release Readiness Blast-Radius Review
depth: 2
lab_status: not-started
last_reviewed: 2026-07-11
review_due: 2026-07-14
sources:
  - sources/articles/aws-devops-agent-docs/
related:
  - devops-agent-topology-context
  - change-specific-release-testing
  - system-aware-candidate-merge
  - agent-space-access-boundary
  - ai-compressed-sdlc
  - risk-focused-high-velocity-code-review
tags:
  - llm-engineering
  - aws
  - devops-agent
  - release-management
  - risk-review
---

# Release Readiness Blast-Radius Review

- **One-sentence definition**: Release readiness blast-radius review is a pre-production agent review that evaluates code and infrastructure changes against dependencies, permissions, policies, and affected services.
- **Why it exists / what problem it solves**: A pull request can look safe locally while breaking another repository, widening permissions, or affecting a critical downstream service. Blast-radius review asks what the change touches before it reaches production.
- **Keywords**: release readiness, blast radius, dependency impact, permissions, policy review
- **Related concepts**: [[devops-agent-topology-context]], [[change-specific-release-testing]], [[system-aware-candidate-merge]], [[agent-space-access-boundary]], [[ai-compressed-sdlc]], [[risk-focused-high-velocity-code-review]]
- **Depth**: 2/4
- **Last updated**: 2026-07-11
- **Source**: sources/articles/aws-devops-agent-docs/

## Summary

Release readiness review is like asking an experienced operator to read a change before it ships. The operator does not only ask whether the code compiles. They ask which services depend on it, whether permissions changed, whether policy rules are violated, and whether the deployment path is safe. AWS DevOps Agent uses environment context and connected repositories to make that review more systematic.

## Example

A pull request changes an IAM policy for a service that writes invoices. The code diff is small, but the review detects that the policy grants broader database write access than the service needs. It also checks the topology and sees that two downstream billing jobs depend on the service. The result is a caution or block before the release reaches production.

## Relationship to existing concepts

- [[devops-agent-topology-context]]: Topology provides the dependency map needed for blast-radius reasoning.
- [[change-specific-release-testing]]: Risky areas found during readiness review become good targets for focused tests.
- [[system-aware-candidate-merge]]: Both concepts judge local changes in the context of broader system behavior.
- [[agent-space-access-boundary]]: Review quality depends on the accounts, repositories, and integrations available inside the Agent Space.
- [[ai-compressed-sdlc]]: Readiness review helps manage deployment risk in faster development cycles.
- [[risk-focused-high-velocity-code-review]]: Blast-radius findings become a concise risk summary that helps reviewers prioritize scarce attention.

## Open questions

- Which release risks should automatically block a merge versus only warn reviewers?
- How should an agent explain blast radius clearly enough for a release owner to trust it?
