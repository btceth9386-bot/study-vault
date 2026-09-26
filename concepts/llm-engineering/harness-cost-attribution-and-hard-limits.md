---
id: harness-cost-attribution-and-hard-limits
title: Harness Cost Attribution and Hard Limits
depth: 2
lab_status: not-started
last_reviewed: 2026-09-26
review_due: 2026-09-29
sources:
  - sources/papers/bedrock-agentcore-agentops
related:
  - agent-loop-termination-policy
tags:
  - aws
  - agentcore
  - cost-management
  - reliability
---

# Harness Cost Attribution and Hard Limits

- **One-sentence definition**: AgentCore's harness bills per second for the actual CPU and peak memory an agent consumes — not for wall-clock invocation time — and separately lets an operator cap a runaway agent with hard limits on iterations, wall-clock time, tokens, and session lifetime, enforced regardless of whatever stopping logic the agent itself implements.
- **Why it exists / what problem it solves**: An agent loop's cost is easy to misjudge in both directions. Estimating cost from wall-clock invocation duration overstates it, because model and tool I/O waits don't consume CPU. But assuming idle time is free underestimates it, because a held-open session still bills for memory even while waiting. On top of that, an agent's own judgment about when to stop is not something an operator should have to trust unconditionally — a bug, a bad prompt, or an adversarial input could make a reasoning loop run far longer than intended. AgentCore addresses both problems together: billing reflects actual consumed vCPU-seconds and peak-memory-seconds rather than provisioned time, and hard caps (`maxIterations` default 75, `timeoutSeconds` default 3600, `maxTokens`, `idleRuntimeSessionTimeout` default 900, `maxLifetime` default 28800) act as an outer, platform-enforced bound that holds no matter what the agent's own logic decides.
- **Keywords**: per-second billing, cost attribution, hard limits, maxIterations, timeoutSeconds, idle timeout
- **Related concepts**: [[agent-loop-termination-policy]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: Amazon Bedrock AgentCore Developer Guide — Operations, reliability, and governance

## Summary

Think of two separate meters on the same machine. One meter tracks exactly how much electricity (CPU and memory) the machine actually used, second by second — not how long its "on" light was lit — so a slow network call that keeps a session open but uses no CPU costs less than a tight reasoning loop that burns CPU the whole time. The other is a physical governor bolted onto the machine that cuts power once it hits a preset ceiling — a maximum number of cycles, a maximum runtime, a maximum token spend — no matter what the machine's own control logic thinks it should do next. AgentCore gives an agent both: a billing model that reflects real consumption, and a set of hard caps that exist specifically because you shouldn't have to trust the agent to know when to stop.

## Example

A team runs a research agent with `maxIterations` left at its default of 75 and `timeoutSeconds` set to 1800. A prompt-injected tool result tries to trick the agent into looping indefinitely, re-querying the same source over and over. Instead of running forever and generating an unbounded bill, the agent is cut off automatically after 75 reasoning cycles or 30 minutes, whichever comes first — a limit the platform enforces independent of whether the agent's own logic ever recognized it was stuck.

## Relationship to existing concepts

- [[agent-loop-termination-policy]]: That concept is about the agent's own internal logic for recognizing when work is done and combining step, time, token, and cost limits from the inside. This concept is the platform's external, don't-trust-the-agent enforcement of the same kind of limits, functioning as a second, independent line of defense rather than a replacement for the agent's own termination logic. The cost-attribution half of this concept — per-second billing based on actual consumption, plus tag propagation for cost allocation — is a distinct operational concern that concept doesn't cover at all.

## My questions

- How should a team choose `maxIterations` versus `timeoutSeconds` as the binding constraint for a given workload — which one tends to trigger first in practice, and does that matter?
- Does a shorter `idleRuntimeSessionTimeout` actually save money in aggregate once the cost of more frequent cold starts is included, or does that depend heavily on traffic patterns?
