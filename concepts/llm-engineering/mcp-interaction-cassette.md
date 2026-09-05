---
id: mcp-interaction-cassette
title: MCP Interaction Cassette
depth: 2
lab_status: not-started
last_reviewed: 2026-08-09
review_due: 2026-08-12
sources:
  - sources/repos/devhelmhq-mcp-recorder/
related:
  - mcp-bidirectional-json-rpc-substrate
  - mcp-capability-negotiation-handshake
  - mcp-transport-separation
  - mcp-record-replay-verify-cycle
  - deterministic-mcp-replay-matching
  - replay-safe-cassette-scrubbing
  - volatility-aware-structural-verification
  - declarative-mcp-scenario-recording
  - cassette-backed-mcp-pytest-fixtures
tags:
  - llm-engineering
  - mcp
  - testing
  - record-replay
---

# MCP Interaction Cassette

- **One-sentence definition**: An MCP interaction cassette is a versioned file that records the requests, responses, notifications, and session details from one MCP conversation.
- **Why it exists / what problem it solves**: MCP sessions are stateful and asynchronous, so ordinary test setup cannot reliably recreate them. A cassette keeps the actual wire-level conversation as reviewable test data.
- **Keywords**: cassette, JSON-RPC, request, response, notification, session
- **Related concepts**: [[mcp-bidirectional-json-rpc-substrate]], [[mcp-capability-negotiation-handshake]], [[mcp-transport-separation]], [[mcp-record-replay-verify-cycle]], [[deterministic-mcp-replay-matching]], [[replay-safe-cassette-scrubbing]], [[volatility-aware-structural-verification]], [[declarative-mcp-scenario-recording]], [[cassette-backed-mcp-pytest-fixtures]]
- **Depth**: 2/4
- **Last updated**: 2026-08-09
- **Source**: sources/repos/devhelmhq-mcp-recorder/

## Summary

Think of a cassette as a flight recorder for one MCP session. It stores the messages that crossed the boundary, not just a hand-written mock of what someone expected. That lets a client replay a known server conversation or lets a server be checked against a known-good conversation. The cassette must keep protocol details that affect behavior, while later steps remove secrets and ignore only known unstable values.

## Example

```json
{
  "request": {"method": "tools/call", "params": {"name": "weather"}},
  "response": {"result": {"content": [{"type": "text", "text": "Sunny"}]}}
}
```

This entry lets a test reproduce one `tools/call` exchange without contacting the original server.

## Relationship to existing concepts

- [[mcp-bidirectional-json-rpc-substrate]]: The cassette stores the JSON-RPC messages exchanged by both peers.
- [[mcp-capability-negotiation-handshake]]: A recorded session includes the initialization needed before normal calls.
- [[mcp-transport-separation]]: The same cassette model works for HTTP/SSE and stdio sessions.
- [[mcp-record-replay-verify-cycle]]: The cassette is the shared artifact used by each phase.
- [[deterministic-mcp-replay-matching]]: A matcher uses cassette requests to select a recorded response.
- [[replay-safe-cassette-scrubbing]]: Scrubbing makes a cassette safe to review without damaging replay.
- [[volatility-aware-structural-verification]]: Verification compares stored responses with fresh ones.
- [[declarative-mcp-scenario-recording]]: A scenario can produce cassettes consistently.
- [[cassette-backed-mcp-pytest-fixtures]]: Pytest fixtures load a cassette for replay or verification.

## Open questions

- Which transport details are essential to keep for useful replay?
- How should cassette format versions be migrated without losing old test evidence?
