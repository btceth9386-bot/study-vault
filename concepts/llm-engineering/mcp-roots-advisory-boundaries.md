---
id: mcp-roots-advisory-boundaries
title: MCP Roots as Advisory Boundaries
depth: 2
lab_status: not-started
last_reviewed: 2026-05-31
review_due: 2026-06-03
sources:
  - sources/repos/modelcontextprotocol-modelcontextprotocol/
related:
  - mcp-capability-negotiation-handshake
  - toolsets-and-mcp-unified-tool-surface
tags:
  - llm-engineering
  - mcp
  - filesystem
  - security
---

# MCP Roots as Advisory Boundaries

- **One-sentence definition**: MCP roots are client-provided filesystem locations that tell servers which directories are in scope, while leaving actual enforcement to the server and operating system.
- **Why it exists / what problem it solves**: File-aware servers need a standard way to receive project boundaries. Roots provide that scope without pretending to be a sandbox.
- **Keywords**: roots, filesystem, scope, boundary, workspace, sandbox
- **Related concepts**: [[mcp-capability-negotiation-handshake]], [[toolsets-and-mcp-unified-tool-surface]]
- **Depth**: 2/4
- **Last updated**: 2026-05-31
- **Source**: sources/repos/modelcontextprotocol-modelcontextprotocol/

## Summary

Roots are like a map with highlighted work areas. The client tells the server which folders matter for the current task. A well-behaved server stays inside those areas, but the map is not a locked door. Real protection still requires filesystem permissions, containers, or another sandbox.

## Example

```json
{
  "roots": [
    {"uri": "file:///Users/chris/projects/study-vault", "name": "study-vault"}
  ]
}
```

A file-search server should search that project root instead of scanning the entire home directory.

## Relationship to existing concepts

- [[mcp-capability-negotiation-handshake]]: A client declares roots support during initialization.
- [[toolsets-and-mcp-unified-tool-surface]]: File tools are safer when their runtime scope is explicit.

## Open questions

- Which servers should reject requests outside roots rather than merely warn?
- How should roots interact with symlinks and nested mounts?
