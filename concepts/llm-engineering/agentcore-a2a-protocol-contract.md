---
id: agentcore-a2a-protocol-contract
title: AgentCore A2A Protocol Contract
depth: 2
lab_status: not-started
last_reviewed: 2026-09-26
review_due: 2026-09-29
sources:
  - sources/papers/bedrock-agentcore-multi-agent
related:
  - a2a-agent-card-registry-discovery
  - protocol-based-agent-access-surface
tags:
  - aws
  - agentcore
  - a2a
  - multi-agent-systems
  - protocol
---

# AgentCore A2A Protocol Contract

- **One-sentence definition**: The AgentCore A2A protocol contract is a fixed technical spec — one port, one transport, three required endpoints — that any agent-to-agent server must implement to be callable by other agents on AgentCore Runtime.
- **Why it exists / what problem it solves**: If every team invented its own message format and discovery mechanism for agent-to-agent calls, an orchestrator would need custom integration code for every specialist agent it talks to. The contract removes that variance: transport is always JSON-RPC 2.0 over HTTP, the container always listens on port 9000 as an ARM64 image, capability discovery always lives at `/.well-known/agent-card.json`, and health always reports through `/ping`. Any agent that meets the contract can be hosted and called the same way, with no per-agent glue code.
- **Keywords**: A2A, JSON-RPC 2.0, agent card, port 9000, session header, ping health check
- **Related concepts**: [[a2a-agent-card-registry-discovery]], [[protocol-based-agent-access-surface]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: Amazon Bedrock AgentCore Developer Guide — Multi-agent runtime, A2A, shared memory, and Agent Registry

## Summary

Picture a phone jack standard: any phone that has the right plug shape works in any wall socket, regardless of who made it. The A2A contract is that plug shape for agents. A server must run on `0.0.0.0:9000` as an ARM64 container, accept JSON-RPC 2.0 requests at its root path (`POST /`), publish a capability card at `GET /.well-known/agent-card.json` so a caller can learn what it does before calling it, and answer `GET /ping` so the platform knows it's alive. AgentCore Runtime automatically attaches a session header (`X-Amzn-Bedrock-AgentCore-Runtime-Session-Id`) so a multi-turn agent-to-agent conversation is routed back to the same instance every time.

## Example

An orchestrator agent needs a specialist "tax classification" agent. Because that specialist implements the A2A contract, the orchestrator can fetch its agent card, confirm it supports the `tax-classification` skill, then send a `message/send` JSON-RPC request with the transaction details — without ever needing custom code specific to that one specialist, because every A2A agent on the platform speaks the identical wire format.

## Relationship to existing concepts

- [[a2a-agent-card-registry-discovery]]: That concept is the general idea — a machine-readable capability profile plus a directory that stores it. This concept is AWS's concrete implementation of the card half of that idea: a specific, testable contract (fixed port, fixed path, fixed message schema) that a card must actually honor to interoperate on this platform.
- [[protocol-based-agent-access-surface]]: A2A is one of four wire protocols AgentCore Runtime supports (alongside HTTP, MCP, and AG-UI), each on its own port with its own message format. This concept fills in the A2A-specific details of that broader access-surface picture.

## My questions

- How does an orchestrator handle an A2A agent whose agent card advertises a skill the orchestrator's task doesn't expect?
- What's the failure mode when two agents disagree on protocol version (`protocolVersion` in the agent card)?
