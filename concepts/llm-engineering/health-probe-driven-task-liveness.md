---
id: health-probe-driven-task-liveness
title: Health-Probe-Driven Task Liveness
depth: 2
lab_status: not-started
last_reviewed: 2026-09-26
review_due: 2026-09-29
sources:
  - sources/papers/bedrock-agentcore-multi-agent
related:
  - microvm-session-isolation-lifecycle
  - temporal-session-aware-policy-conditions
tags:
  - aws
  - agentcore
  - async-agents
  - reliability
---

# Health-Probe-Driven Task Liveness

- **One-sentence definition**: Health-probe-driven task liveness overloads a health-check endpoint to report "busy with real work" rather than just "alive," so a platform's existing idle-timeout logic automatically leaves a long-running background task alone without any separate task-tracking system.
- **Why it exists / what problem it solves**: A long background task (say, a multi-minute data-processing job) needs the session to stay alive until it finishes, but a fixed idle timeout (e.g., 15 minutes with no new requests) would kill it partway through. Building a whole separate system to track "is this task still running" and exempt it from cleanup is extra infrastructure most teams don't want to write. AgentCore's answer reuses the health check that already exists: the `/ping` endpoint returns `"Healthy"` when idle and `"HealthyBusy"` when a background task is in progress, and the platform simply skips the idle timeout whenever it sees `"HealthyBusy"`. Clients don't need to distinguish sync from async calls, and developers only need `add_async_task`/`complete_async_task` calls or a custom ping handler — no bespoke scheduler.
- **Keywords**: health check, ping endpoint, HealthyBusy, idle timeout, async task tracking
- **Related concepts**: [[microvm-session-isolation-lifecycle]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: Amazon Bedrock AgentCore Developer Guide — Multi-agent runtime, A2A, shared memory, and Agent Registry

## Summary

It's the difference between a doctor's waiting room sign that just says "Open" versus one that says "Open — Currently With a Patient." A plain heartbeat only tells the platform the process hasn't crashed; a busy-aware heartbeat tells it *why* it shouldn't be cleaned up yet. AgentCore leans on this: instead of building a separate job-tracking service, it lets the existing `/ping` health check carry that one extra bit of information, and reuses the idle-timeout machinery it already has to make the right call.

## Example

An agent kicks off a 3-minute background data-export job. It calls `add_async_task("export")` before starting a background thread, and `complete_async_task(task_id)` when the thread finishes. During those 3 minutes, `/ping` automatically reports `"HealthyBusy"`, so even though the client made no new requests, the platform's normal 15-minute idle timeout never fires — the session stays up exactly as long as needed and no longer.

## Relationship to existing concepts

- [[microvm-session-isolation-lifecycle]]: That concept defines the session states (Active, Idle, Stopped) and the default timeouts that would otherwise end a session. This concept explains the specific signal — a busy health probe — that lets a legitimate long-running task legally bypass that default timeout. The technique itself (encoding business state in a health check's return value, not just a boolean) generalizes beyond AgentCore to any platform with liveness probes.
- [[temporal-session-aware-policy-conditions]]: A family resemblance rather than a duplicate — both extend a normally stateless, per-request mechanism with session-scoped memory, but for different purposes: this concept tracks liveness status to decide whether a session should stay alive, while that concept tracks authorization-relevant history to decide whether an action is permitted.

## My questions

- What happens if a task legitimately needs to run longer than the maximum session lifetime (e.g., 8 hours), even with `HealthyBusy` reported the whole time?
- Is there a risk of a buggy agent reporting `HealthyBusy` forever and silently consuming session quota, and how would a team detect that?
