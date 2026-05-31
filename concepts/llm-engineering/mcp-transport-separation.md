---
id: mcp-transport-separation
title: MCP Transport Separation
depth: 2
lab_status: not-started
last_reviewed: 2026-05-31
review_due: 2026-06-03
sources:
  - sources/repos/modelcontextprotocol-modelcontextprotocol/
related:
  - mcp-bidirectional-json-rpc-substrate
  - mcp-capability-negotiation-handshake
  - mcp-oauth-protected-resource-discovery
tags:
  - llm-engineering
  - mcp
  - protocol
  - transport
---

# MCP Transport Separation

- **One-sentence definition**: MCP keeps its message contract separate from transport, so the same protocol can run through local stdio or remote Streamable HTTP.
- **Why it exists / what problem it solves**: Local IDE tools and hosted services have different networking needs. Keeping transport separate prevents the ecosystem from inventing a new logical protocol for every deployment style.
- **Keywords**: stdio, Streamable HTTP, SSE, local process, remote server, transport
- **Related concepts**: [[mcp-bidirectional-json-rpc-substrate]], [[mcp-capability-negotiation-handshake]], [[mcp-oauth-protected-resource-discovery]]
- **Depth**: 2/4
- **Last updated**: 2026-05-31
- **Source**: sources/repos/modelcontextprotocol-modelcontextprotocol/

## Summary

Transport is the delivery truck, not the package. A local MCP client can launch a subprocess and exchange newline-delimited JSON through stdin and stdout. A remote client can send the same kind of messages over HTTP and receive streaming events. The protocol meaning stays stable while the delivery mechanism changes.

## Example

```text
Local IDE       -> stdio subprocess       -> filesystem MCP server
Hosted client   -> Streamable HTTP + SSE  -> remote MCP server
```

Both servers can expose `tools/list` and `tools/call`; only the transport setup differs.

## Relationship to existing concepts

- [[mcp-bidirectional-json-rpc-substrate]]: JSON-RPC is the transport-independent package format.
- [[mcp-capability-negotiation-handshake]]: Both transports begin with the same logical initialization phase.
- [[mcp-oauth-protected-resource-discovery]]: Remote HTTP deployments need a discoverable authorization model.

## Open questions

- When is a local stdio server preferable to a remote HTTP service?
- Which transport-level failures should an MCP client retry automatically?
