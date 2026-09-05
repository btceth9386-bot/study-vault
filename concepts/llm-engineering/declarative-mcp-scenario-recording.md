---
id: declarative-mcp-scenario-recording
title: Declarative MCP Scenario Recording
depth: 2
lab_status: not-started
last_reviewed: 2026-08-09
review_due: 2026-08-12
sources:
  - sources/repos/devhelmhq-mcp-recorder/
related:
  - mcp-transport-separation
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

# Declarative MCP Scenario Recording

- **One-sentence definition**: Declarative MCP scenario recording turns a versioned YAML list of MCP actions into repeatable, separately saved interaction cassettes.
- **Why it exists / what problem it solves**: Manual proxy sessions are hard to reproduce and audit. A scenario makes the target, inputs, redaction policy, and action order explicit enough for automation and CI.
- **Keywords**: YAML, scenario, recording, automation, cassette, CI
- **Related concepts**: [[mcp-transport-separation]], [[mcp-interaction-cassette]], [[mcp-record-replay-verify-cycle]], [[replay-safe-cassette-scrubbing]], [[cassette-backed-mcp-pytest-fixtures]]
- **Depth**: 2/4
- **Last updated**: 2026-08-09
- **Source**: sources/repos/devhelmhq-mcp-recorder/

## Summary

A scenario is a recipe for producing a cassette. Instead of clicking through an MCP session by hand, a YAML file names the server target and lists actions such as listing tools, calling a tool, or reading a resource. The recorder runs those steps through its proxy, applies the declared redaction rules, and saves the result. Keeping the recipe in version control makes a refreshed cassette explainable and repeatable.

## Example

```yaml
target: stdio:python server.py
actions:
  - list_tools
  - call_tool: {name: add, arguments: {a: 2, b: 3}}
redact_env: [API_KEY]
```

Running this scenario creates a cassette that includes a predictable `add` call and does not retain the API key.

## Relationship to existing concepts

- [[mcp-transport-separation]]: A scenario can target a local stdio process or a remote HTTP service.
- [[mcp-interaction-cassette]]: The scenario's output is a persisted interaction cassette.
- [[mcp-record-replay-verify-cycle]]: It automates the record phase of the larger testing cycle.
- [[replay-safe-cassette-scrubbing]]: The declared redaction policy is applied before the cassette is saved.
- [[cassette-backed-mcp-pytest-fixtures]]: Generated cassettes can be consumed by standard pytest tests.

## Open questions

- Which scenarios should be fast enough to run on every pull request?
- How should environment-specific targets be supplied without making scenarios opaque?
