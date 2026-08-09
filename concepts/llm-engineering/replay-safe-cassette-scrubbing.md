---
id: replay-safe-cassette-scrubbing
title: Replay-Safe Cassette Scrubbing
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
  - mcp-record-replay-verify-cycle
  - declarative-mcp-scenario-recording
tags:
  - llm-engineering
  - mcp
  - testing
  - record-replay
---

# Replay-Safe Cassette Scrubbing

- **One-sentence definition**: Replay-safe cassette scrubbing removes configured secrets from cassette metadata and responses while preserving the request fields needed to replay the conversation.
- **Why it exists / what problem it solves**: Cassettes should be safe to review and commit, but indiscriminate redaction can destroy the request identity that deterministic replay uses.
- **Keywords**: redaction, secrets, cassette, replay, request identity, review
- **Related concepts**: [[mcp-interaction-cassette]], [[deterministic-mcp-replay-matching]], [[volatility-aware-structural-verification]], [[mcp-record-replay-verify-cycle]], [[declarative-mcp-scenario-recording]]
- **Depth**: 2/4
- **Last updated**: 2026-08-09
- **Source**: sources/repos/devhelmhq-mcp-recorder/

## Summary

Scrubbing is the safety pass after recording. It replaces explicitly configured secrets in metadata and responses, so a cassette can be stored without exposing credentials. It intentionally does not rewrite request bodies because replay may use them to identify the matching interaction. A sensitive value in a request should trigger review and a safer test design, not silent mutation that makes the cassette unreliable.

## Example

```text
response.headers.authorization: "Bearer secret-token" → "<REDACTED>"
request.params.query: "customer report"               → unchanged
```

The secret is removed, while the request stays usable as a replay key.

## Relationship to existing concepts

- [[mcp-interaction-cassette]]: Scrubbing protects the stored interaction data.
- [[deterministic-mcp-replay-matching]]: Replay needs the original request identity to remain intact.
- [[volatility-aware-structural-verification]]: Scrubbing removes secrets; verification separately ignores expected changing values.
- [[mcp-record-replay-verify-cycle]]: It prepares captured evidence for safe reuse.
- [[declarative-mcp-scenario-recording]]: A scenario defines redaction policy alongside its actions.

## Open questions

- Which request fields should make a recorder fail instead of only warning?
- How can teams test authenticated flows with disposable, non-sensitive credentials?
