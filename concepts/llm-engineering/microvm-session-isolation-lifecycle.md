---
id: microvm-session-isolation-lifecycle
title: microVM Session Isolation and Lifecycle
depth: 2
lab_status: not-started
last_reviewed: 2026-09-26
review_due: 2026-09-29
sources:
  - sources/papers/bedrock-agentcore-multi-agent
related:
  - ephemeral-agent-execution-sandbox
  - persistent-agent-session-restoration
  - health-probe-driven-task-liveness
tags:
  - aws
  - agentcore
  - session-isolation
  - sandboxing
  - multi-agent-systems
---

# microVM Session Isolation and Lifecycle

- **One-sentence definition**: AgentCore Runtime gives every user session its own dedicated microVM (with its own compute, memory, and filesystem), moves it through Active, Idle, and Stopped states, and by default destroys the whole machine and sanitizes its memory after 15 minutes idle or 8 hours total.
- **Why it exists / what problem it solves**: A multi-user agent system sharing one execution environment risks one user's agent touching another user's data — and because AI agents behave non-deterministically, that boundary is much harder to guarantee purely through application logic than it is for a traditional stateless function. Per-session microVM isolation pushes the security boundary down into infrastructure instead: whatever unpredictable path an agent's reasoning takes, it's physically confined to a machine that gets torn down and wiped when the session ends, so isolation doesn't depend on the agent behaving correctly. Sessions stay attached to the same microVM through a protocol-specific session header (e.g., `Mcp-Session-Id` or `X-Amzn-Bedrock-AgentCore-Runtime-Session-Id`), so reusing the same session ID is what lets a conversation build on prior context. Without extra configuration, anything on that machine disappears once it's Stopped — persisting files across stop/resume needs session storage, and persisting structured knowledge needs AgentCore Memory.
- **Keywords**: microVM, session isolation, Active/Idle/Stopped, session header, sticky routing, ephemeral by default
- **Related concepts**: [[ephemeral-agent-execution-sandbox]], [[persistent-agent-session-restoration]], [[health-probe-driven-task-liveness]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: Amazon Bedrock AgentCore Developer Guide — Multi-agent runtime, A2A, shared memory, and Agent Registry

## Summary

Imagine every hotel guest getting their own room built fresh at check-in and demolished at checkout, rather than everyone sharing one common room and trusting each guest to only touch their own belongings. That's the difference a microVM per session makes: instead of hoping an agent's logic never crosses a boundary it shouldn't, the boundary is a physical machine. A session is "Active" while it's handling a request or a background task, "Idle" once it's done but still available, and "Stopped" once the microVM is torn down — by default after 15 minutes of no activity or 8 hours of total runtime, whichever comes first. Send the same session ID again after a stop, and a fresh microVM spins up to continue that logical session, but anything that was only in the old machine's memory or disk is gone unless it was explicitly persisted.

## Example

Two customers are chatting with the same deployed support agent at the same time. Customer A's conversation runs in microVM #1, Customer B's runs in microVM #2 — separate compute, memory, and filesystem for each, so even if Customer A's agent somehow tried to read local files it shouldn't, there's nothing of Customer B's on that machine to find. When Customer A goes quiet for 20 minutes, their microVM is stopped and its memory sanitized; if they come back and reuse the same session ID, a new microVM is provisioned, and only whatever was saved to AgentCore Memory or session storage survives the gap.

## Relationship to existing concepts

- [[ephemeral-agent-execution-sandbox]]: That concept is about containing *untrusted generated code* in a disposable sandbox to limit the damage a malicious or buggy script could do. This concept is about isolating *legitimate multi-turn conversation sessions* from each other for multi-tenancy reasons — the threat model is different (data leakage between real users, not malicious code) even though both use a "destroy the environment when done" strategy.
- [[persistent-agent-session-restoration]]: These two concepts are complementary opposites: this one establishes that a session is short-lived by default, and that concept covers the deliberate techniques for making state survive beyond a single session when the application actually needs it to.
- [[health-probe-driven-task-liveness]]: A specific mechanism that sits underneath this concept's lifecycle — it explains exactly how a legitimate long-running background task can signal the platform to skip the default idle timeout that would otherwise stop the session prematurely.

## My questions

- How does an application layer maintain the mapping between a real user and their session ID, given that AgentCore itself doesn't enforce that binding?
- What's the tradeoff of setting a shorter idle timeout (faster cost savings, more cold starts) versus a longer one (fewer cold starts, more idle compute cost)?
