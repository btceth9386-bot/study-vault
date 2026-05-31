---
id: mcp-extension-negotiation-framework
title: MCP Extension Negotiation Framework
depth: 2
lab_status: not-started
last_reviewed: 2026-05-31
review_due: 2026-06-03
sources:
  - sources/repos/modelcontextprotocol-modelcontextprotocol/
related:
  - mcp-capability-negotiation-handshake
  - mcp-schema-generation-pipeline
tags:
  - llm-engineering
  - mcp
  - extensions
  - interoperability
---

# MCP Extension Negotiation Framework

- **One-sentence definition**: MCP extensions add optional protocol features through named, governed capabilities that both client and server must declare before use.
- **Why it exists / what problem it solves**: Protocols need room to evolve, but ad hoc vendor behavior fragments interoperability. MCP extensions provide a controlled path for official, experimental, and unofficial additions without forcing every feature into the core.
- **Keywords**: extension, capability negotiation, vendor prefix, official extension, experimental extension
- **Related concepts**: [[mcp-capability-negotiation-handshake]], [[mcp-schema-generation-pipeline]]
- **Depth**: 2/4
- **Last updated**: 2026-05-31
- **Source**: sources/repos/modelcontextprotocol-modelcontextprotocol/

## Summary

Extensions are optional add-ons with stable names. A client and server advertise the extensions they understand during initialization. They use an extension only when both sides agree. This lets MCP grow while preserving a predictable core for simpler implementations.

## Example

```json
{
  "capabilities": {
    "extensions": {
      "io.modelcontextprotocol/apps": {
        "mimeTypes": ["text/html;profile=mcp-app"]
      }
    }
  }
}
```

A client that does not advertise `io.modelcontextprotocol/apps` should continue using the core protocol without interactive app resources.

## Relationship to existing concepts

- [[mcp-capability-negotiation-handshake]]: Extension support is negotiated as part of initialization.
- [[mcp-schema-generation-pipeline]]: Extension evolution needs the same discipline as core protocol evolution.

## Open questions

- When should a widely adopted extension graduate into the MCP core?
- How should clients present unsupported extension behavior to users?
