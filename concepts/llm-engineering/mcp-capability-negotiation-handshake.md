---
id: mcp-capability-negotiation-handshake
title: MCP Capability Negotiation Handshake
depth: 2
lab_status: not-started
last_reviewed: 2026-05-31
review_due: 2026-06-03
sources:
  - sources/repos/modelcontextprotocol-modelcontextprotocol/
related:
  - mcp-bidirectional-json-rpc-substrate
  - mcp-transport-separation
  - mcp-roots-advisory-boundaries
  - mcp-elicitation-for-structured-user-input
  - mcp-oauth-protected-resource-discovery
  - mcp-extension-negotiation-framework
tags:
  - llm-engineering
  - mcp
  - protocol
  - interoperability
---

# MCP Capability Negotiation Handshake

- **One-sentence definition**: MCP starts with an `initialize` exchange where client and server agree on protocol version and optional features before normal work begins.
- **Why it exists / what problem it solves**: MCP implementations do not all support the same feature set. The handshake makes support explicit so each side can avoid calling features the other side cannot handle.
- **Keywords**: initialize, initialized, capabilities, protocol version, graceful degradation
- **Related concepts**: [[mcp-bidirectional-json-rpc-substrate]], [[mcp-transport-separation]], [[mcp-roots-advisory-boundaries]], [[mcp-elicitation-for-structured-user-input]], [[mcp-oauth-protected-resource-discovery]], [[mcp-extension-negotiation-framework]]
- **Depth**: 2/4
- **Last updated**: 2026-05-31
- **Source**: sources/repos/modelcontextprotocol-modelcontextprotocol/

## Summary

The handshake is like checking which plugs are available before connecting equipment. The client sends its protocol version, capabilities, and identity. The server replies with the version and capabilities it supports. The client then sends `notifications/initialized`, which signals that ordinary requests can begin.

## Example

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-11-25",
    "capabilities": {"roots": {}, "elicitation": {"form": {}}},
    "clientInfo": {"name": "study-client", "version": "1.0.0"}
  }
}
```

A server that does not advertise `tools` should not receive `tools/call` requests.

## Relationship to existing concepts

- [[mcp-bidirectional-json-rpc-substrate]]: The handshake configures the message exchange that follows.
- [[mcp-transport-separation]]: Both stdio and Streamable HTTP sessions use the same logical initialization handshake.
- [[mcp-roots-advisory-boundaries]]: Roots are one optional client capability.
- [[mcp-elicitation-for-structured-user-input]]: Elicitation is another optional client capability.
- [[mcp-oauth-protected-resource-discovery]]: Remote clients complete authorization before relying on the negotiated MCP session.
- [[mcp-extension-negotiation-framework]]: Extensions reuse the capability negotiation mechanism.

## Open questions

- How should clients expose degraded behavior when a server lacks a desired capability?
- Which capability mismatches should be warnings versus hard failures?
