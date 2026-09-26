---
id: shadow-mode-policy-testing-with-decision-flip-telemetry
title: Shadow-Mode Policy Testing with Decision-Flip Telemetry
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
  - authorization
  - reliability
  - testing
---

# Shadow-Mode Policy Testing with Decision-Flip Telemetry

- **One-sentence definition**: `LOG_ONLY` mode exists at two independent levels — a single policy can be set to evaluate against real traffic and report its outcome without ever affecting the returned decision, and a whole policy engine can be set the same way — and in both cases the system separately reports which `LOG_ONLY` policies would have changed the outcome had they been active, giving a direct signal for how much a new policy would disrupt current traffic if enforced.
- **Why it exists / what problem it solves**: Deploying a new authorization or guardrail policy directly into enforcement carries the same risk as deploying any new logic directly into production — if the policy is wrong, it either blocks legitimate traffic it shouldn't or fails to block what it was meant to, and there's no way to know which before it's already live and already causing harm. Policy-level `LOG_ONLY` mode solves this by evaluating the new policy against every real request exactly as if it were active, but routing its outcome only to traces and CloudWatch metrics — the decision actually returned to the caller is computed only from `ACTIVE` policies, so a `LOG_ONLY` policy can never affect what any caller experiences. The signal for judging rollout risk is decision-flipping: the system tracks which `LOG_ONLY` policies, evaluated independently of each other but against the current set of `ACTIVE` policies, would have changed the outcome if enforced. A policy that rarely or never flips a decision during a representative observation window is less likely to disrupt current traffic if promoted — though a low flip rate shows low observed impact, not proof the policy is logically correct. Engine-level `LOG_ONLY` is a coarser, higher-precedence switch: it makes an entire policy engine non-enforcing regardless of any individual policy's own mode, useful for observing a whole policy set before enabling any of it.
- **Keywords**: LOG_ONLY, shadow testing, decision-flip telemetry, policy promotion, dark launch
- **Related concepts**: [[cedar-policy-gateway-authorization]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: Amazon Bedrock AgentCore Developer Guide — Operations, reliability, and governance

## Summary

Picture a new security guard shadowing an experienced one for a week: the trainee watches every visitor and privately writes down what decision they *would* make, but the actual gate is still operated entirely by the experienced guard — nobody is turned away or let in based on the trainee's private notes. At the end of the week, someone compares the trainee's notes against what actually happened and asks, "how often would this trainee's decision have been different?" A trainee whose notes rarely disagree is a much safer bet to actually put on the gate. That comparison — "how often would this have changed the outcome?" — is exactly what decision-flip telemetry gives a team deciding whether to promote a new policy from `LOG_ONLY` to `ACTIVE`.

## Example

A team writes a new Cedar policy that would forbid a specific tool call pattern they suspect is being misused, but they're not confident it won't also catch legitimate traffic. They deploy it with `enforcementMode` set to `LOG_ONLY`. Over a week of real production traffic, the policy matches on 200 requests, and the decision-flip telemetry shows only 3 of those would have actually changed the outcome (the other 197 were already denied by an existing `ACTIVE` policy). Confident the new policy adds precise, low-disruption coverage, the team promotes it to `ACTIVE`.

## Relationship to existing concepts

- [[cedar-policy-gateway-authorization]]: This is a specific mechanism operating within that concept's broader Cedar authorization system — a way to shadow-test a policy before trusting it in enforcement — rather than a separate authorization mechanism. It mirrors the shadow-deployment, dark-launch, and canary-analysis ideas used broadly in software delivery (evaluate new logic against real traffic without letting it affect real outcomes, then use an explicit signal to decide whether to promote it), but is distinct from a general A/B test because both the active and log-only sides see the exact same traffic rather than a split — appropriate here specifically because the log-only side must never have a user-visible effect.

## My questions

- How long should a team typically observe a policy in `LOG_ONLY` mode before treating a low decision-flip rate as sufficient evidence to promote it?
- Since a low flip rate doesn't prove correctness, what complementary check (manual review, targeted test cases) should accompany decision-flip telemetry before promotion?
