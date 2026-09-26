---
id: agentcore-trust-boundary-hardening
title: AgentCore Trust-Boundary Hardening
depth: 2
lab_status: not-started
last_reviewed: 2026-09-26
review_due: 2026-09-29
sources:
  - sources/papers/bedrock-agentcore-agentops
related:
  - cedar-policy-gateway-authorization
tags:
  - aws
  - agentcore
  - security
  - iam
---

# AgentCore Trust-Boundary Hardening

- **One-sentence definition**: Securing an AgentCore Runtime's trust boundary requires several separate controls working together, not any single one alone — a trust-policy condition (`aws:SourceArn`/`aws:SourceAccount`) that stops another AWS service from impersonating a legitimate caller to assume the execution role (confused-deputy prevention), joint evaluation of resource-based policies on both the runtime and its endpoint with explicit deny always winning, and closing off direct access to a Runtime that's meant to be reachable only through a policy-enforcing Gateway.
- **Why it exists / what problem it solves**: Three distinct trust failures are each easy to overlook independently, precisely because each looks "secure enough" in isolation. First, the confused-deputy problem: if an execution role's trust policy only checks that the caller is the `bedrock-agentcore.amazonaws.com` service principal, any AgentCore resource in any AWS account could potentially trigger that role — adding `aws:SourceArn` and `aws:SourceAccount` conditions restricts which specific resource is actually allowed to invoke it. Second, a related but separate failure: cross-account access to a runtime requires resource-based policies on *both* the runtime and its endpoint, and if either resource lacks an explicit allow, the request is denied — a team that configures only one of the two believes they've opened access when they haven't. Third, a compounding case: putting a policy-enforcing Gateway in front of a Runtime only protects traffic that actually flows through the Gateway — if the Runtime can still be reached directly, every policy, guardrail, and interceptor on the Gateway is trivially bypassed, so the Runtime's own inbound authorization must independently be restricted to accept only the Gateway's identity.
- **Keywords**: confused deputy, aws:SourceArn, resource-based policy, explicit deny, gateway bypass
- **Related concepts**: [[cedar-policy-gateway-authorization]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: Amazon Bedrock AgentCore Developer Guide — Operations, reliability, and governance

## Summary

Imagine a building with a front desk that's supposed to be the only way in, plus a side door that's technically still unlocked. Adding a great front-desk check (the Gateway's policies) does nothing if the side door (direct Runtime access) is never bolted shut. Separately, imagine a delivery worker's badge that only checks "are you wearing a delivery uniform" rather than "are you the specific delivery company we contracted with" — any delivery worker from any company gets in (the confused-deputy gap), until the badge check is tightened to a specific, named company. And imagine a vault that needs two separate keys turned at once (the runtime and its endpoint) — if only one key is ever configured, the vault is still locked, even though someone thinks they've opened it. All three failures share the same shape: a control that looks complete on its own but silently has a gap unless a second, easy-to-forget piece is also in place.

## Example

A platform team fronts their AgentCore Runtime with a Gateway that enforces Cedar policies, believing this fully governs access. Months later, a security review discovers the Runtime's own resource-based policy still allows direct invocation from any IAM principal in the account — the Gateway's policies were never the only path in. The team closes the gap by restricting the Runtime's inbound authorization to accept invocations only from the Gateway's execution role, at which point the Gateway's Cedar policies become the actual, sole enforcement point they were always assumed to be.

## Relationship to existing concepts

- [[cedar-policy-gateway-authorization]]: That concept describes the authorization logic enforced at the Gateway; this concept is the prerequisite plumbing that makes the Gateway's enforcement actually meaningful — without closing direct Runtime access and correctly scoping trust and resource policies, Cedar policies at the Gateway can be silently bypassed no matter how well-written they are.

## My questions

- How would a team detect, as an ongoing operational check rather than a one-time audit, that a Runtime's direct-access path has been accidentally reopened by a later configuration change?
- Are there legitimate cases where a Runtime genuinely needs to accept both direct invocation and Gateway-routed invocation, and if so, how should the security tradeoff be documented?
