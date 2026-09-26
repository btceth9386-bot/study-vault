---
id: mcp-protocol-foundations
title: "MCP Protocol Foundations: From JSON-RPC Messages to Extensible Agent Integrations"
description: A focused path for developers building or operating MCP clients and servers, covering interoperability economics, bidirectional JSON-RPC, capability negotiation, transports, roots, elicitation, HTTP authorization discovery, secure consumption, skill supply-chain governance, schema generation, and extension negotiation.
---

## Overview

The Model Context Protocol (MCP) gives AI applications a standard way to connect to tools, resources, and prompts. Building a reliable integration requires more than exposing a list of tools: clients and servers must agree on capabilities, exchange messages over an appropriate transport, preserve security boundaries, and evolve without breaking older implementations.

This path develops that protocol-level model in layers. Start with why a shared protocol reduces integration work, then learn the bidirectional JSON-RPC substrate, initialization handshake, and transport options. Continue with client-facing capabilities such as roots and elicitation, examine OAuth discovery and secure consumption for remote deployments, govern skills that can use those integrations, and finish with the schema and extension mechanisms that keep the protocol maintainable as it grows.

For an operational view of how MCP fits into a deployed agent, continue with [Production Agent Runtime](../topics/production-agent-runtime.md).

**Estimated study time:** 5–7 hours
**Prerequisites:** Familiarity with JSON APIs and client-server systems. OAuth terminology is helpful for the authorization section.

---

## Concepts in Order

### 1. [MCP N-plus-M Integration Scaling](../concepts/llm-engineering/mcp-n-plus-m-integration-scaling.md)
See why a shared protocol avoids a separate model-to-tool adapter for every pair as the ecosystem grows.

### 2. [MCP Bidirectional JSON-RPC Substrate](../concepts/llm-engineering/mcp-bidirectional-json-rpc-substrate.md)
Begin with MCP's message model. Learn why both peers can send requests, responses, and notifications, and how this differs from a one-directional API client.

### 3. [MCP Capability Negotiation Handshake](../concepts/llm-engineering/mcp-capability-negotiation-handshake.md)
Study the initialization exchange that lets clients and servers advertise supported features before using them. This handshake is the compatibility boundary for the rest of the protocol.

### 4. [MCP Transport Separation](../concepts/llm-engineering/mcp-transport-separation.md)
Separate protocol semantics from message delivery. Compare local standard I/O connections with remote Streamable HTTP deployments and understand what remains invariant across both.

### 5. [MCP Roots as Advisory Boundaries](../concepts/llm-engineering/mcp-roots-advisory-boundaries.md)
Learn how clients describe filesystem roots to servers. Treat roots as useful scope hints while preserving enforcement in the host environment and server implementation.

### 6. [MCP Elicitation for Structured User Input](../concepts/llm-engineering/mcp-elicitation-for-structured-user-input.md)
Explore how a server can request typed user input through the client instead of inventing a custom interaction channel. This extends MCP beyond passive tool execution.

### 7. [MCP OAuth Protected Resource Discovery](../concepts/llm-engineering/mcp-oauth-protected-resource-discovery.md)
Move from local integrations to protected HTTP deployments. Follow the metadata-driven OAuth discovery flow and identify the trust decisions a client must make.

### 8. [Secure MCP Consumption Lifecycle](../concepts/llm-engineering/secure-mcp-consumption-lifecycle.md)
Connect only to trustworthy servers, scope credentials, verify capabilities, and make consequential calls visible and auditable.

### 9. [Agent Skill Supply-Chain Governance](../concepts/llm-engineering/agent-skill-supply-chain-governance.md)
Treat installed skills as dependencies: use trusted sources, pin versions, review and scan changes, assign ownership, and run regression tests. Study this after secure MCP consumption because a skill can package instructions, scripts, and privileged MCP usage into one adoptable unit.

### 10. [MCP Schema Generation Pipeline](../concepts/llm-engineering/mcp-schema-generation-pipeline.md)
Examine how a protocol project keeps TypeScript types, JSON Schema, and documentation aligned. Use the pipeline as a model for maintaining machine-readable contracts without documentation drift.

### 11. [MCP Extension Negotiation Framework](../concepts/llm-engineering/mcp-extension-negotiation-framework.md)
Finish with protocol evolution. Learn how optional extensions build on negotiated capabilities so new behavior can be added without silently breaking older peers.

---

## What You'll Be Able to Do

- Explain MCP as a bidirectional protocol rather than a tool-list API
- Explain how a shared protocol changes integration growth from N × M toward N + M
- Design initialization and capability checks before invoking optional features
- Choose an MCP transport based on deployment boundaries
- Distinguish advisory filesystem scope from enforceable sandboxing
- Add structured user interaction and OAuth discovery to appropriate integrations
- Onboard MCP servers with provenance checks, least privilege, confirmation, and auditability
- Govern installed skills as reviewed, pinned, owned dependencies when they can direct or invoke MCP tools
- Maintain protocol schemas and documentation from a shared source of truth
- Evaluate extension proposals for backward-compatible negotiation
