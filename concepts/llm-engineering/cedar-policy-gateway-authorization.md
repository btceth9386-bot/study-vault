---
id: cedar-policy-gateway-authorization
title: Cedar Policy Gateway Authorization
depth: 2
lab_status: not-started
last_reviewed: 2026-09-26
review_due: 2026-09-29
sources:
  - sources/papers/bedrock-agentcore-agentops
related:
  - hybrid-agent-policy-gating
  - multi-dimension-rate-limiting-with-fail-open
  - shadow-mode-policy-testing-with-decision-flip-telemetry
  - temporal-session-aware-policy-conditions
  - agentcore-trust-boundary-hardening
tags:
  - aws
  - agentcore
  - authorization
  - security
  - governance
---

# Cedar Policy Gateway Authorization

- **One-sentence definition**: Policy in AgentCore intercepts every tool call at the Gateway boundary — outside the agent's own code — and evaluates it against Cedar policies (an open-source, human-readable authorization language) with default-deny and forbid-wins semantics, so authorization is deterministic and enforced consistently no matter how the agent itself is implemented or manipulated.
- **Why it exists / what problem it solves**: An agent that dynamically decides which tools to call and with what arguments can misinterpret business rules or be manipulated into acting outside its intended authority — and if the only enforcement lives inside the agent's own prompt or code, a successful manipulation of the agent bypasses that enforcement entirely, because the thing being manipulated is also the thing supposedly guarding against manipulation. Moving authorization outside the agent, to a Gateway that intercepts every request regardless of how it was generated, removes that failure mode. The policy engine auto-generates a Cedar schema directly from the Gateway's own tool definitions — mapping each tool to an action with typed parameters — and validates every policy against that schema before it can be deployed, catching mistakes before they reach production. It applies default-deny (nothing is allowed unless a policy explicitly permits it) plus forbid-wins (a single matching forbid overrides any permit), so the outcome is always deterministic. Because writing Cedar by hand has a learning curve, a developer can instead describe a rule in plain English; a policy-authoring service converts it to Cedar, validates it against the schema, and runs automated reasoning to flag policies that are always-allow, always-deny, or contain conditions that can never be satisfied.
- **Keywords**: Cedar, policy engine, default-deny, forbid-wins, auto-generated schema, natural-language authoring
- **Related concepts**: [[hybrid-agent-policy-gating]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: Amazon Bedrock AgentCore Developer Guide — Operations, reliability, and governance

## Summary

Think of the Gateway as airport security rather than a rule printed on the airline ticket. If the rule about what you can bring on board only lived on your ticket (inside the agent), a forged or altered ticket would bypass it entirely. Airport security instead checks every passenger at one physical checkpoint, applying the same rules no matter what any individual ticket claims — and by default, if a rule doesn't explicitly allow something, it's not allowed. Cedar policies are that checkpoint's rulebook: written once, validated against a schema so a typo can't create a silent security hole, and enforceable in plain English if a security officer would rather describe a rule than write formal code for it.

## Example

A refund-processing agent has a Cedar policy: "permit the `IssueRefund` action only when `resource.amount <= 500` and `principal` has the `support-agent` role." Even if the agent is prompt-injected into attempting a $5,000 refund, the Gateway's policy engine evaluates the actual tool call against this rule at the boundary — outside and after whatever reasoning led the agent there — and denies it, because no policy permits an amount above 500. The agent's internal state was compromised, but the enforcement point never trusted that state in the first place.

## Relationship to existing concepts

- [[hybrid-agent-policy-gating]]: A general, two-stage (structural-then-semantic) pattern any team could implement themselves. This concept is AWS's specific, managed productization of a gateway policy boundary — Cedar for deterministic structural authorization, with its Cedar-compatible Dogwood extension available for information-provider signals such as content-safety guardrails — enforced by Gateway interception rather than by application-level plumbing the team has to build and maintain.
- [[multi-dimension-rate-limiting-with-fail-open]]: A separate Gateway-level control that must not be mistaken for this concept's authorization guarantee — rate limits fail open by design to preserve availability, while this concept's default-deny Cedar semantics fail closed because they exist specifically to be a security boundary.
- [[shadow-mode-policy-testing-with-decision-flip-telemetry]]: A specific mechanism for safely testing a new Cedar policy against real traffic before trusting it in enforcement, using decision-flip telemetry rather than a live traffic split as the promotion signal.
- [[temporal-session-aware-policy-conditions]]: Extends this concept's stateless, per-request Cedar evaluation with session-scoped history and live information-provider signals, for rules that a single isolated request genuinely can't express.
- [[agentcore-trust-boundary-hardening]]: The prerequisite plumbing this concept's Gateway enforcement depends on — Cedar policies only govern access if direct Runtime access is also closed and the surrounding trust and resource policies are correctly scoped, otherwise the Gateway's enforcement can be silently bypassed.

## My questions

- How does a team decide the right granularity for Cedar policies — one broad policy per role, or many narrow policies per tool — as the number of tools and roles grows?
- What happens to in-flight requests if a policy update is deployed mid-session — does the new policy apply immediately, or only to new sessions?
