---
id: mcp-protocol-foundations
title: "MCP Protocol Foundations: From JSON-RPC Messages to Extensible Agent Integrations"
description: A focused path for developers building or operating MCP clients and servers, covering bidirectional JSON-RPC, capability negotiation, transports, roots, elicitation, HTTP authorization discovery, schema generation, and extension negotiation.
---

## Overview

The Model Context Protocol (MCP) gives AI applications a standard way to connect to tools, resources, and prompts. Building a reliable integration requires more than exposing a list of tools: clients and servers must agree on capabilities, exchange messages over an appropriate transport, preserve security boundaries, and evolve without breaking older implementations.

This path develops that protocol-level model in layers. Start with the bidirectional JSON-RPC substrate, then learn the initialization handshake and transport options. Continue with client-facing capabilities such as roots and elicitation, examine OAuth discovery for HTTP deployments, and finish with the schema and extension mechanisms that keep the protocol maintainable as it grows.

For an operational view of how MCP fits into a deployed agent, continue with [Production Agent Runtime](../topics/production-agent-runtime.md).

**Estimated study time:** 4–6 hours  
**Prerequisites:** Familiarity with JSON APIs and client-server systems. OAuth terminology is helpful for the authorization section.

---

## Concepts in Order

### 1. [MCP Bidirectional JSON-RPC Substrate](../concepts/llm-engineering/mcp-bidirectional-json-rpc-substrate.md)
Begin with MCP's message model. Learn why both peers can send requests, responses, and notifications, and how this differs from a one-directional API client.

### 2. [MCP Capability Negotiation Handshake](../concepts/llm-engineering/mcp-capability-negotiation-handshake.md)
Study the initialization exchange that lets clients and servers advertise supported features before using them. This handshake is the compatibility boundary for the rest of the protocol.

### 3. [MCP Transport Separation](../concepts/llm-engineering/mcp-transport-separation.md)
Separate protocol semantics from message delivery. Compare local standard I/O connections with remote Streamable HTTP deployments and understand what remains invariant across both.

### 4. [MCP Roots as Advisory Boundaries](../concepts/llm-engineering/mcp-roots-advisory-boundaries.md)
Learn how clients describe filesystem roots to servers. Treat roots as useful scope hints while preserving enforcement in the host environment and server implementation.

### 5. [MCP Elicitation for Structured User Input](../concepts/llm-engineering/mcp-elicitation-for-structured-user-input.md)
Explore how a server can request typed user input through the client instead of inventing a custom interaction channel. This extends MCP beyond passive tool execution.

### 6. [MCP OAuth Protected Resource Discovery](../concepts/llm-engineering/mcp-oauth-protected-resource-discovery.md)
Move from local integrations to protected HTTP deployments. Follow the metadata-driven OAuth discovery flow and identify the trust decisions a client must make.

### 7. [MCP Schema Generation Pipeline](../concepts/llm-engineering/mcp-schema-generation-pipeline.md)
Examine how a protocol project keeps TypeScript types, JSON Schema, and documentation aligned. Use the pipeline as a model for maintaining machine-readable contracts without documentation drift.

### 8. [MCP Extension Negotiation Framework](../concepts/llm-engineering/mcp-extension-negotiation-framework.md)
Finish with protocol evolution. Learn how optional extensions build on negotiated capabilities so new behavior can be added without silently breaking older peers.

---

## What You'll Be Able to Do

- Explain MCP as a bidirectional protocol rather than a tool-list API
- Design initialization and capability checks before invoking optional features
- Choose an MCP transport based on deployment boundaries
- Distinguish advisory filesystem scope from enforceable sandboxing
- Add structured user interaction and OAuth discovery to appropriate integrations
- Maintain protocol schemas and documentation from a shared source of truth
- Evaluate extension proposals for backward-compatible negotiation

