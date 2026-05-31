---
id: mcp-bidirectional-json-rpc-substrate
title: MCP Bidirectional JSON-RPC Substrate
depth: 2
lab_status: not-started
last_reviewed: 2026-05-31
review_due: 2026-06-03
sources:
  - sources/repos/modelcontextprotocol-modelcontextprotocol/
related:
  - mcp-capability-negotiation-handshake
  - mcp-transport-separation
  - mcp-schema-generation-pipeline
  - toolsets-and-mcp-unified-tool-surface
tags:
  - llm-engineering
  - mcp
  - json-rpc
  - protocol
---

# MCP Bidirectional JSON-RPC Substrate

- **One-sentence definition**: MCP uses JSON-RPC 2.0 as a two-way message layer so clients and servers can both send requests, responses, and notifications.
- **Why it exists / what problem it solves**: A simple tool API assumes the client always asks and the server always answers. Agent systems need more: a server may ask the host to run a model, collect user input, or report progress. MCP uses one shared message format for both directions.
- **Keywords**: MCP, JSON-RPC, request, response, notification, bidirectional
- **Related concepts**: [[mcp-capability-negotiation-handshake]], [[mcp-transport-separation]], [[mcp-schema-generation-pipeline]], [[toolsets-and-mcp-unified-tool-surface]]
- **Depth**: 2/4
- **Last updated**: 2026-05-31
- **Source**: sources/repos/modelcontextprotocol-modelcontextprotocol/

## Summary

Think of JSON-RPC as a shared envelope format. The envelope says whether a message asks for work, answers a request, or announces an event. MCP lets both sides send those envelopes. That matters because an MCP server is not limited to acting like a passive function library.

## Example

```json
{"jsonrpc":"2.0","id":1,"method":"tools/list"}
{"jsonrpc":"2.0","id":1,"result":{"tools":[]}}
{"jsonrpc":"2.0","method":"notifications/tools/list_changed"}
```

The first line asks for available tools, the second answers, and the third announces that the tool list changed.

## Relationship to existing concepts

- [[mcp-capability-negotiation-handshake]]: The handshake decides which bidirectional operations are allowed.
- [[mcp-transport-separation]]: The same JSON-RPC messages can travel over different transports.
- [[mcp-schema-generation-pipeline]]: The schema pipeline defines and validates the messages exchanged over JSON-RPC.
- [[toolsets-and-mcp-unified-tool-surface]]: A unified tool surface is one higher-level use of MCP messages.

## Open questions

- Which server-to-client requests are worth enabling in a minimal MCP client?
- What logging makes JSON-RPC failures easy to trace without exposing sensitive payloads?
