---
id: mcp-record-replay-verify-cycle
title: MCP Record-Replay-Verify Cycle
depth: 2
lab_status: not-started
last_reviewed: 2026-08-09
review_due: 2026-08-12
sources:
  - sources/repos/devhelmhq-mcp-recorder/
related:
  - mcp-interaction-cassette
  - deterministic-mcp-replay-matching
  - volatility-aware-structural-verification
  - replay-safe-cassette-scrubbing
  - declarative-mcp-scenario-recording
  - cassette-backed-mcp-pytest-fixtures
tags:
  - llm-engineering
  - mcp
  - testing
  - record-replay
---

# MCP Record-Replay-Verify Cycle

- **One-sentence definition**: The MCP record-replay-verify cycle captures a live session once, replays it for deterministic client tests, and runs it against a live server to find regressions.
- **Why it exists / what problem it solves**: Client tests should not require a live server, but server tests still need proof that behavior has not drifted. One cassette provides evidence for both jobs.
- **Keywords**: record, replay, verify, regression, cassette, deterministic test
- **Related concepts**: [[mcp-interaction-cassette]], [[deterministic-mcp-replay-matching]], [[volatility-aware-structural-verification]], [[replay-safe-cassette-scrubbing]], [[declarative-mcp-scenario-recording]], [[cassette-backed-mcp-pytest-fixtures]]
- **Depth**: 2/4
- **Last updated**: 2026-08-09
- **Source**: sources/repos/devhelmhq-mcp-recorder/

## Summary

This cycle turns a real MCP exchange into a reusable contract test. First, record a successful session in a cassette. Next, replay it so a client can be tested quickly and without network uncertainty. Finally, send the recorded requests to a live server and compare the results, allowing only known volatile values to differ. The three stages serve different purposes, so replay is not a replacement for verification.

## Example

```text
record: call a live calculator server and save calculator.json
replay: test a client against calculator.json with no live server
verify: run calculator.json against the current server release
```

A changed tool response is harmless during replay but appears as a regression during verification.

## Relationship to existing concepts

- [[mcp-interaction-cassette]]: The cycle shares one recorded conversation between its stages.
- [[deterministic-mcp-replay-matching]]: Replay needs a clear rule for finding the stored response.
- [[volatility-aware-structural-verification]]: Verification identifies meaningful differences without failing on expected noise.
- [[replay-safe-cassette-scrubbing]]: Recorded evidence must be safe to store and review.
- [[declarative-mcp-scenario-recording]]: Scenarios make the record stage repeatable in CI.
- [[cassette-backed-mcp-pytest-fixtures]]: Fixtures make replay and verification ordinary tests.

## Open questions

- Which user journeys deserve recorded contract tests rather than unit tests?
- When should a cassette be deliberately re-recorded after a reviewed behavior change?
