---
id: cassette-backed-mcp-pytest-fixtures
title: Cassette-Backed MCP Pytest Fixtures
depth: 2
lab_status: not-started
last_reviewed: 2026-08-09
review_due: 2026-08-12
sources:
  - sources/repos/devhelmhq-mcp-recorder/
related:
  - mcp-interaction-cassette
  - mcp-record-replay-verify-cycle
  - deterministic-mcp-replay-matching
  - volatility-aware-structural-verification
  - declarative-mcp-scenario-recording
tags:
  - llm-engineering
  - mcp
  - testing
  - record-replay
---

# Cassette-Backed MCP Pytest Fixtures

- **One-sentence definition**: Cassette-backed MCP pytest fixtures connect a test marker to either a temporary replay server for client tests or a verification result for live-server regression tests.
- **Why it exists / what problem it solves**: Protocol testing is easier to adopt when server lifecycle, free-port allocation, cassette loading, matcher selection, and cleanup fit ordinary test functions.
- **Keywords**: pytest, fixture, cassette, replay, verification, test lifecycle
- **Related concepts**: [[mcp-interaction-cassette]], [[mcp-record-replay-verify-cycle]], [[deterministic-mcp-replay-matching]], [[volatility-aware-structural-verification]], [[declarative-mcp-scenario-recording]]
- **Depth**: 2/4
- **Last updated**: 2026-08-09
- **Source**: sources/repos/devhelmhq-mcp-recorder/

## Summary

Fixtures turn cassette testing into normal pytest code. A marker names a cassette and may select a matching strategy or verification ignore rules. The replay fixture starts a local server and gives the client a URL, so the test does not need a real MCP server. The verification fixture sends the cassette's requests to a configured live target and returns the differences for the test to assert on.

## Example

```python
@pytest.mark.mcp_cassette("cassettes/calculator.json", match="method_params")
async def test_calculator(mcp_replay_url):
    async with Client(mcp_replay_url) as client:
        assert await client.call_tool("add", {"a": 2, "b": 3})
```

The fixture handles the local replay server; the test focuses on the client behavior.

## Relationship to existing concepts

- [[mcp-interaction-cassette]]: The marker selects the cassette used by a test.
- [[mcp-record-replay-verify-cycle]]: Fixtures expose its replay and verification stages.
- [[deterministic-mcp-replay-matching]]: The marker or command line can choose a matching strategy.
- [[volatility-aware-structural-verification]]: Verification ignores can be set for the specific test.
- [[declarative-mcp-scenario-recording]]: Scenarios can create the cassettes consumed by fixtures.

## Open questions

- When should a test use replay rather than run against a live integration target?
- Which marker settings should be shared as a project default?
