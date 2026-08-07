---
id: mcp-client-server-trace-correlation
title: MCP Client-Server Trace Correlation
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-semantic-conventions-genai/
related:
  - context-propagation-with-carriers
  - mcp-bidirectional-json-rpc-substrate
  - mcp-transport-separation
tags:
  - observability
  - opentelemetry
  - mcp
  - tracing
  - json-rpc
---

# MCP Client-Server Trace Correlation

- **One-sentence definition**: MCP client-server trace correlation joins the client and server work for one JSON-RPC method through propagated trace context.
- **Why it exists / what problem it solves**: Without shared context, an agent trace ends at the MCP client and cannot reveal the server work or protocol failure that followed.
- **Keywords**: MCP, JSON-RPC, client span, server span, propagation, trace
- **Related concepts**: [[context-propagation-with-carriers]], [[mcp-bidirectional-json-rpc-substrate]], [[mcp-transport-separation]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: OpenTelemetry Semantic Conventions for Generative AI

## Summary

An MCP method call crosses a boundary: one process sends the request and another performs the work. The client creates a client span, sends the current trace context with the request, and the server extracts that context before creating its server span.

The result is one trace across local stdio or remote HTTP, with stable method semantics on both sides.

## Example

An agent calls `tools/call` on an MCP server. The client span records the outgoing JSON-RPC operation, and the server span records the tool execution. Because the trace context is propagated, both spans appear under the agent request that triggered the call.

## Relationship to existing concepts

- [[context-propagation-with-carriers]]: Injection and extraction carry the trace across the client-server boundary.
- [[mcp-bidirectional-json-rpc-substrate]]: Correlation follows the JSON-RPC methods that MCP exchanges.
- [[mcp-transport-separation]]: The same correlation model works over stdio and HTTP.

## My questions

- Which MCP identifiers can be safely recorded to make retries and errors easier to diagnose?
- How should trace context be handled for server-initiated MCP requests?
