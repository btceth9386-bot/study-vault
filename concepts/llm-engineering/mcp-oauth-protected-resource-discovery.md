---
id: mcp-oauth-protected-resource-discovery
title: MCP OAuth Protected Resource Discovery
depth: 2
lab_status: not-started
last_reviewed: 2026-05-31
review_due: 2026-06-03
sources:
  - sources/repos/modelcontextprotocol-modelcontextprotocol/
related:
  - mcp-transport-separation
  - mcp-capability-negotiation-handshake
tags:
  - llm-engineering
  - mcp
  - oauth
  - security
---

# MCP OAuth Protected Resource Discovery

- **One-sentence definition**: MCP OAuth protected resource discovery lets a remote client learn where and how to authenticate by reading metadata advertised by the HTTP MCP server.
- **Why it exists / what problem it solves**: Remote MCP servers need secure access without requiring every client to be manually configured for every authorization server. Metadata discovery gives clients a standard path from an unauthenticated request to the correct OAuth flow.
- **Keywords**: OAuth 2.1, protected resource metadata, authorization server, bearer token, audience
- **Related concepts**: [[mcp-transport-separation]], [[mcp-capability-negotiation-handshake]]
- **Depth**: 2/4
- **Last updated**: 2026-05-31
- **Source**: sources/repos/modelcontextprotocol-modelcontextprotocol/

## Summary

Think of the MCP server as a protected building. When a client arrives without a badge, the server does not just say “no.” It points the client to metadata that explains where badges are issued and which permissions are needed. The client then follows an OAuth flow and returns with a token meant for that resource server.

## Example

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource"
```

The client fetches that metadata, discovers the authorization server, obtains a token, and retries the MCP request.

## Relationship to existing concepts

- [[mcp-transport-separation]]: This authorization path applies to remote HTTP transport, not local stdio.
- [[mcp-capability-negotiation-handshake]]: Authentication happens before the normal MCP capability exchange can be trusted.

## Open questions

- How should clients cache metadata without hiding authorization configuration changes?
- What audit data should a remote MCP server retain for tool calls?
