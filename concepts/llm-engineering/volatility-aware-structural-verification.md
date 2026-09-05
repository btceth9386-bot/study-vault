---
id: volatility-aware-structural-verification
title: Volatility-Aware Structural Verification
depth: 2
lab_status: not-started
last_reviewed: 2026-08-09
review_due: 2026-08-12
sources:
  - sources/repos/devhelmhq-mcp-recorder/
related:
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

# Volatility-Aware Structural Verification

- **One-sentence definition**: Volatility-aware structural verification removes known changing fields, then recursively compares recorded and live responses for meaningful differences.
- **Why it exists / what problem it solves**: Literal equality fails on timestamps, generated IDs, formatting, and key order, while broad exclusions can hide real behavior changes.
- **Keywords**: verification, regression, structural comparison, volatile fields, JSON, diff
- **Related concepts**: [[mcp-interaction-cassette]], [[mcp-record-replay-verify-cycle]], [[replay-safe-cassette-scrubbing]], [[cassette-backed-mcp-pytest-fixtures]]
- **Depth**: 2/4
- **Last updated**: 2026-08-09
- **Source**: sources/repos/devhelmhq-mcp-recorder/

## Summary

Verification asks a current MCP server to repeat requests from a cassette. Before comparing answers, it removes only fields known to change every run, such as timestamps or generated IDs. It then walks nested JSON values to find actual structural differences, including JSON that was serialized into a string. This keeps tests quiet about expected noise but loud about a changed schema or result.

## Example

```json
{"result": {"run_id": "a1", "items": ["blue"]}}
{"result": {"run_id": "b2", "items": ["green"]}}
```

If `run_id` is an explicit ignored field, verification still reports that `items` changed from `blue` to `green`.

## Relationship to existing concepts

- [[mcp-interaction-cassette]]: The cassette supplies the expected responses.
- [[mcp-record-replay-verify-cycle]]: This is the cycle's live-server regression stage.
- [[replay-safe-cassette-scrubbing]]: It differs from scrubbing, which protects secrets rather than ignoring runtime variation.
- [[cassette-backed-mcp-pytest-fixtures]]: The verification fixture returns the structural differences to a test.

## Open questions

- Which ignored fields should be global defaults and which should stay test-specific?
- How should verification display a nested JSON difference so it is easy to diagnose?
