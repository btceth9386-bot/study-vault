---
id: mcp-schema-generation-pipeline
title: MCP Schema Generation Pipeline
depth: 2
lab_status: not-started
last_reviewed: 2026-05-31
review_due: 2026-06-03
sources:
  - sources/repos/modelcontextprotocol-modelcontextprotocol/
related:
  - mcp-bidirectional-json-rpc-substrate
  - mcp-extension-negotiation-framework
tags:
  - llm-engineering
  - mcp
  - schema
  - protocol
---

# MCP Schema Generation Pipeline

- **One-sentence definition**: The MCP schema generation pipeline keeps TypeScript protocol definitions as the source of truth and derives machine-readable JSON Schema plus human-readable MDX documentation from them.
- **Why it exists / what problem it solves**: Protocol docs, validation schemas, and source types drift if people edit them independently. Generating downstream artifacts and checking them in CI keeps implementers aligned.
- **Keywords**: TypeScript, JSON Schema, MDX, generation, CI validation, source of truth
- **Related concepts**: [[mcp-bidirectional-json-rpc-substrate]], [[mcp-extension-negotiation-framework]]
- **Depth**: 2/4
- **Last updated**: 2026-05-31
- **Source**: sources/repos/modelcontextprotocol-modelcontextprotocol/

## Summary

The TypeScript schema is the master blueprint. JSON Schema is generated for machines that need validation, and MDX documentation is generated for humans who need a reference. CI compares generated output with committed files. If someone changes the blueprint but forgets to rebuild the derived artifacts, the checks fail.

## Example

```text
schema/draft/schema.ts
        |
        +--> schema/draft/schema.json
        |
        +--> docs/specification/draft/schema.mdx
```

After editing `schema.ts`, a contributor runs schema generation and validation before opening a pull request.

## Relationship to existing concepts

- [[mcp-bidirectional-json-rpc-substrate]]: The generated schema defines the JSON-RPC messages MCP participants exchange.
- [[mcp-extension-negotiation-framework]]: Schema discipline matters when core protocol and extensions evolve independently.

## Open questions

- Which compatibility checks should block a new stable protocol release?
- How should extension schemas integrate with core schema validation?
