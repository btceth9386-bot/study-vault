---
id: deterministic-mcp-replay-matching
title: Deterministic MCP Replay Matching
depth: 2
lab_status: not-started
last_reviewed: 2026-08-09
review_due: 2026-08-12
sources:
  - sources/repos/devhelmhq-mcp-recorder/
related:
  - mcp-bidirectional-json-rpc-substrate
  - mcp-interaction-cassette
  - mcp-record-replay-verify-cycle
  - replay-safe-cassette-scrubbing
  - cassette-backed-mcp-pytest-fixtures
tags:
  - llm-engineering
  - mcp
  - testing
  - record-replay
---

# Deterministic MCP Replay Matching

- **One-sentence definition**: Deterministic MCP replay matching selects a recorded response for a new JSON-RPC request using an explicit rule such as method-and-parameters, sequence order, or exact-body equality.
- **Why it exists / what problem it solves**: Request IDs and metadata can change between runs, repeated calls may depend on order, and some tests need exact fidelity. A single comparison rule cannot serve every replay case.
- **Keywords**: matcher, JSON-RPC, method parameters, sequential, strict, replay
- **Related concepts**: [[mcp-bidirectional-json-rpc-substrate]], [[mcp-interaction-cassette]], [[mcp-record-replay-verify-cycle]], [[replay-safe-cassette-scrubbing]], [[cassette-backed-mcp-pytest-fixtures]]
- **Depth**: 2/4
- **Last updated**: 2026-08-09
- **Source**: sources/repos/devhelmhq-mcp-recorder/

## Summary

A replay server needs to decide which saved answer belongs to an incoming request. Method-and-parameters matching ignores changing request IDs and usually fits independent tool calls. Sequential matching uses call order when the same request occurs more than once. Strict matching compares the complete request when every byte-level detail matters. Choose the least strict rule that still protects the behavior being tested.

## Example

```text
Recorded: tools/call(name="search", query="cats"), id=1
Current:  tools/call(name="search", query="cats"), id=73

method-and-parameters → match
strict full-body      → no match
```

The first rule is useful when the client generates a new JSON-RPC ID each run.

## Relationship to existing concepts

- [[mcp-bidirectional-json-rpc-substrate]]: Matching works on MCP's JSON-RPC request shape.
- [[mcp-interaction-cassette]]: The matcher searches the cassette's recorded interactions.
- [[mcp-record-replay-verify-cycle]]: Matching powers the replay stage of the cycle.
- [[replay-safe-cassette-scrubbing]]: Scrubbing must preserve fields used as replay keys.
- [[cassette-backed-mcp-pytest-fixtures]]: A test marker can choose the matcher for one test.

## Open questions

- Which requests are safe to match by method and parameters alone?
- How should replay report an ambiguous match instead of silently choosing one?
