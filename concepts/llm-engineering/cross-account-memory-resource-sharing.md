---
id: cross-account-memory-resource-sharing
title: Cross-Account Memory Resource Sharing
depth: 2
lab_status: not-started
last_reviewed: 2026-09-26
review_due: 2026-09-29
sources:
  - sources/papers/bedrock-agentcore-multi-agent
related:
  - memory-namespace-multi-tenant-isolation
tags:
  - aws
  - agentcore
  - agent-memory
  - iam
  - multi-account
---

# Cross-Account Memory Resource Sharing

- **One-sentence definition**: Cross-account memory resource sharing lets a principal in one AWS account call another account's memory data-plane APIs directly, or lets that memory resource deliver its data to a destination (S3, SNS, Kinesis) sitting in a different account — all through resource-based policies rather than copying data.
- **Why it exists / what problem it solves**: Different teams inside one company often own separate AWS accounts, but a multi-agent system may need those teams' agents to share the same customer memory — a support agent and a sales agent both need the same customer's long-term memory, for example. Copying that memory into every account that needs it is both a security risk and a consistency nightmare (which copy is current?). Cross-account access instead keeps the memory resource in exactly one account and lets other accounts' agents call it directly: AWS checks both the resource-based policy attached to the memory resource and the identity-based policy of the calling principal, and only allows the call when both agree.
- **Keywords**: resource-based policy, cross-account IAM, data plane, execution role, delivery destination
- **Related concepts**: [[memory-namespace-multi-tenant-isolation]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: Amazon Bedrock AgentCore Developer Guide — Multi-agent runtime, A2A, shared memory, and Agent Registry

## Summary

Think of it like a shared filing cabinet that stays in one office (Account A) but has a rule posted on it saying "employees from Office B may open this drawer." Account B's agent doesn't get its own copy of the cabinet — it reaches into the original one, and AWS checks two locks before letting it in: the cabinet's own rule (the resource-based policy) and Account B's own ID badge permissions (its identity-based policy). There's a second pattern too: instead of another account reaching in to read, the cabinet itself can be configured to mail copies of new documents out to a mailbox (S3, SNS, or Kinesis) that lives in another account — that direction is set up with an execution role in the source account plus a policy on the destination resource that allows that role in.

## Example

A customer-support team (Account A) owns the AgentCore Memory resource holding customer preferences. A sales team (Account B) wants their upsell agent to read those same preferences without duplicating them. Account A attaches a resource-based policy to the memory resource granting `RetrieveMemoryRecords` to a specific IAM role in Account B. The sales agent, assuming that role, calls the memory API directly using the full ARN of Account A's resource — no data ever leaves Account A's memory store.

## Relationship to existing concepts

- [[memory-namespace-multi-tenant-isolation]]: Namespaces solve isolation *within* one account's memory resource (which actor or agent owns which slice of data); this concept solves the separate problem of who *outside* that account may reach the resource at all. A real multi-agent, multi-team deployment typically needs both — namespaced organization inside the resource, and a resource-based policy controlling which accounts can touch it.

## My questions

- How should a team audit which cross-account grants on a shared memory resource are still actually in use versus stale?
- Does cross-account access interact with the namespace-scoped IAM conditions, e.g., can Account B be granted access to only one namespace inside Account A's memory resource?
