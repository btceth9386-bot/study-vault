---
id: temporal-session-aware-policy-conditions
title: Temporal Session-Aware Policy Conditions
depth: 2
lab_status: not-started
last_reviewed: 2026-09-26
review_due: 2026-09-29
sources:
  - sources/papers/bedrock-agentcore-agentops
related:
  - cedar-policy-gateway-authorization
  - health-probe-driven-task-liveness
tags:
  - aws
  - agentcore
  - authorization
  - governance
---

# Temporal Session-Aware Policy Conditions

- **One-sentence definition**: While a standard Cedar policy evaluates each request in isolation, a temporal policy — written in Dogwood, a Cedar-compatible language — can additionally reason over what already happened earlier in the same policy session, expressing rules like "require a prior approval before this action," "block an action after it has run N times," or "keep a running total under a budget," and can also consult live information providers such as Guardrails for a content-safety or prompt-attack score at evaluation time.
- **Why it exists / what problem it solves**: Many real authorization rules for an autonomous, multi-step agent aren't expressible as a judgment about one isolated request. "This agent may issue a refund" is a different — and often unsafe — question from "this agent may issue a refund, but only once a human has already approved this specific case, and only if it hasn't already refunded three times this session." Because standard Cedar policies are stateless, expressing that kind of rule would otherwise require building custom state-tracking logic entirely outside the policy system. Dogwood closes that gap without discarding existing investment: every valid Cedar policy is also a valid Dogwood policy, so temporal capability is additive rather than a rewrite. Temporal conditions are evaluated against a "policy session" — a sequence of related Gateway invocations grouped by a caller-supplied session ID header — so the history a condition can reason about is scoped to one session, not the caller's entire lifetime.
- **Keywords**: Dogwood, temporal policy, policy session, prior approval, running total, information provider
- **Related concepts**: [[cedar-policy-gateway-authorization]], [[health-probe-driven-task-liveness]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: Amazon Bedrock AgentCore Developer Guide — Operations, reliability, and governance

## Summary

A stateless Cedar policy is like a bank teller who only ever sees the transaction in front of them and has no memory of the customer's earlier visits that same day — they can check "is this withdrawal under the daily limit as stated on this one slip," but they can't catch "this is actually the fourth withdrawal today and together they exceed the real daily limit" unless someone hands them a running tally. A temporal Dogwood policy is that running tally: it lets the teller's decision depend on everything that happened earlier in the same visit (the policy session), not just the transaction slip currently in hand.

## Example

A finance-approval agent's policy allows it to process a wire transfer only if an `ApprovalGranted` event was recorded earlier in the same policy session, and only if the running total of transfers processed in that session stays under $50,000. Even if the agent is manipulated into attempting a transfer without a prior approval event, the temporal condition — which looks at the session's actual history rather than trusting the agent's claim that approval happened — denies the request, because no matching approval event exists in that session's record.

## Relationship to existing concepts

- [[cedar-policy-gateway-authorization]]: This concept extends that one specifically on the dimension plain Cedar can't cover — cross-request, within-session history and live external signals — rather than being a separate authorization mechanism. Every Dogwood policy remains a superset capability layered on top of the same Gateway-enforced, default-deny, forbid-wins evaluation.
- [[health-probe-driven-task-liveness]]: A family resemblance rather than a duplicate — both extend a normally stateless, per-request mechanism with session-scoped memory, but for different purposes: this concept tracks authorization-relevant history (approvals, counts, running totals) to decide whether an action is permitted, while that concept tracks task-liveness status to decide whether a session should stay alive.

## My questions

- How long does a policy session's history persist, and what happens to temporal conditions if a session spans an unusually long time or an unusually large number of events?
- Can a temporal condition reference history from a *different*, related session (e.g., a prior day's session with the same actor), or is it strictly scoped to the current session only?
