---
id: mcp-record-replay-testing
title: "MCP Record-Replay Testing: From Live Sessions to Reliable Contract Tests"
description: Build dependable MCP integration tests by capturing real interactions, replaying them deterministically, safely scrubbing sensitive data, verifying live behavior, and integrating the workflow with pytest and CI.
---

## Overview

MCP integrations are stateful, asynchronous conversations, so unit-test mocks often miss failures at the protocol boundary. This path turns a known-good live session into a reusable test asset: capture it as a cassette, replay it for fast client tests, and verify it against a live server to detect regressions.

Start with the cassette and the full record-replay-verify loop. Then make replay deterministic, protect recorded data without breaking it, compare live results while allowing known runtime variation, and automate capture and test execution. For MCP message and transport fundamentals, first complete [MCP Protocol Foundations](../topics/mcp-protocol-foundations.md).

**Estimated study time:** 3–4 hours
**Prerequisites:** Familiarity with JSON-RPC and pytest. MCP Protocol Foundations is recommended.

---

## Concepts in Order

### 1. [MCP Interaction Cassette](../concepts/llm-engineering/mcp-interaction-cassette.md)
Learn the shared artifact: a versioned recording of requests, responses, notifications, and session details from one MCP conversation.

### 2. [MCP Record-Replay-Verify Cycle](../concepts/llm-engineering/mcp-record-replay-verify-cycle.md)
Place the cassette in its full workflow: record a known-good session, replay it for deterministic client tests, and verify it against the current live server.

### 3. [Deterministic MCP Replay Matching](../concepts/llm-engineering/deterministic-mcp-replay-matching.md)
Choose how incoming requests select recorded responses, accounting for changing request IDs, repeated calls, and tests that require strict fidelity.

### 4. [Replay-Safe Cassette Scrubbing](../concepts/llm-engineering/replay-safe-cassette-scrubbing.md)
Remove configured secrets while keeping the request identity that replay matching depends on, so cassettes remain both safe to commit and useful to run.

### 5. [Volatility-Aware Structural Verification](../concepts/llm-engineering/volatility-aware-structural-verification.md)
Compare a cassette with a live server response after excluding only known volatile fields, surfacing real contract changes without timestamp noise.

### 6. [Declarative MCP Scenario Recording](../concepts/llm-engineering/declarative-mcp-scenario-recording.md)
Make recording repeatable with versioned YAML scenarios that declare the target, actions, and redaction policy for CI-friendly capture.

### 7. [Cassette-Backed MCP Pytest Fixtures](../concepts/llm-engineering/cassette-backed-mcp-pytest-fixtures.md)
Finish by exposing replay and live verification through ordinary pytest fixtures, keeping test functions focused on expected client or server behavior.

---

## What You'll Be Able to Do

- Capture real MCP conversations as reviewable, versioned test evidence
- Build offline, deterministic MCP client tests without a live server
- Select replay matchers that tolerate expected request variation without hiding errors
- Commit cassettes without leaking secrets or damaging replay behavior
- Detect meaningful live-server contract regressions while ignoring known runtime noise
- Automate recording, replay, and verification with declarative scenarios and pytest
