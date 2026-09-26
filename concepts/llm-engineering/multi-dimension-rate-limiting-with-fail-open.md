---
id: multi-dimension-rate-limiting-with-fail-open
title: Multi-Dimension Rate Limiting with Fail-Open Defaults
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
  - reliability
  - rate-limiting
---

# Multi-Dimension Rate Limiting with Fail-Open Defaults

- **One-sentence definition**: An AgentCore Gateway rate limit groups traffic into buckets using up to ten ordered dimension keys — a caller's JWT claim, IAM principal, target name, tool name, or model ID — enforces every active rate limit with AND logic so a request must pass all of them, and, critically, fails open by default: if the rate-limit service is unavailable or a dimension can't be resolved, the request is allowed through rather than blocked.
- **Why it exists / what problem it solves**: A single global rate limit can't express real operational needs like "cap this one caller's tokens per minute" or "block this specific tool for everyone except one team." Dimension keys let a limit be scoped to exactly the traffic slice that matters, and multiple rate limits can be layered so a request must clear all of them, not just one. The fail-open default exists for a specific reason: a rate limiter that fails closed would turn its own unavailability into an outage for all traffic, which is usually a worse outcome than briefly losing the throttle. But that tradeoff has a sharp edge — the documentation explicitly warns that rate limits should never be relied on as a security boundary, only as a throughput control, because an attacker who can trigger dimension-resolution failures, or who simply catches the service during an outage, passes through completely unthrottled.
- **Keywords**: rate limit, dimension keys, fail-open, throughput control, JWT claim, IAM principal
- **Related concepts**: [[cedar-policy-gateway-authorization]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: Amazon Bedrock AgentCore Developer Guide — Operations, reliability, and governance

## Summary

Think of a nightclub with several separate bouncers, each checking a different thing — one caps how many people from any one company can enter per hour, another caps how many people can use the VIP entrance, and a third caps total entries for one specific event. A guest must pass every bouncer who's on duty to get in (AND logic across active limits). But if the club's ID-scanning system goes down entirely, the doors default to open rather than turning everyone away — useful for keeping the night going, but it also means anyone who can make the scanner fail (or times their arrival to an outage) walks in unchecked. That's the tradeoff: rate limits keep normal traffic orderly, but they were never designed to be the lock on the door.

## Example

A gateway operator sets a rate limit dimensioned on `$.context.jwt.team`, capping each team to 1,000 requests per minute, and a second rate limit dimensioned on `toolName`, capping a specific expensive tool to 50 calls per minute across everyone. A request from a caller in the `platform` team calling that expensive tool must pass both checks. If the service that resolves JWT claims briefly goes down, requests bypass the team-based limit (fail open) but still respect the tool-based limit as long as that dimension resolves normally — illustrating that a rate limit's protection is only as reliable as the dimension resolution behind it.

## Relationship to existing concepts

- [[cedar-policy-gateway-authorization]]: This is a concrete, AWS-specific instance of the general availability-versus-strictness tradeoff every rate limiter must make — fail open to preserve availability, or fail closed to preserve the guarantee — but with an explicit caveat that the guarantee here is only throughput shaping, not access control. It should never substitute for that concept's deny-by-default Cedar semantics, which fail closed by design because they exist specifically to be a security boundary.

## My questions

- How would a team monitor for and alert on rate-limit fail-open events specifically, so a service outage doesn't silently remove throttling without anyone noticing?
- When multiple rate limits are layered with AND logic, how does a caller diagnose which specific limit rejected their request?
