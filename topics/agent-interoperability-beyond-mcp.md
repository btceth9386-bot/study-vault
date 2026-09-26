---
id: agent-interoperability-beyond-mcp
title: "Agent Interoperability Beyond MCP: Delegation, UI, and Governed Commerce"
description: Learn how interoperating agents choose tool calls or delegation, discover specialists, render safe user interfaces, and keep payment authority constrained.
---

## Overview

MCP standardizes an agent's connection to tools, but interoperability also covers when an agent should hand work to another agent, how it discovers that agent, how a client safely renders an agent-driven interface, and how autonomous shopping stays separate from permission to pay.

This path starts by choosing the right interaction model, then makes delegated specialists discoverable through A2A. It continues with A2UI's trusted rendering boundary and layout-ownership decision, and closes with UCP and AP2's separation of commerce from payment authorization. Complete [MCP Protocol Foundations](../topics/mcp-protocol-foundations.md) first for MCP's transport, negotiation, and security mechanics. A closing case study grounds the general Agent Card and registry ideas from step 2 in a real managed platform, Amazon Bedrock AgentCore, showing its concrete A2A wire contract and a governed, approval-workflow registry for discovering agents and tools at organizational scale.

**Estimated study time:** 3–4 hours  
**Prerequisites:** Familiarity with tool calling and JSON-based APIs. MCP Protocol Foundations is recommended.

---

## Concepts in Order

### 1. [Bounded Tool Calls vs. Agent Delegation](../concepts/llm-engineering/bounded-tool-calls-vs-agent-delegation.md)
Decide whether work has a complete request-and-response shape or needs another agent to own an evolving, interruptible task. This choice determines whether a tool interface is sufficient before you design discovery or collaboration.

### 2. [A2A Agent Card and Registry Discovery](../concepts/llm-engineering/a2a-agent-card-registry-discovery.md)
Learn how an Agent Card advertises a specialist's capabilities, interaction contract, and security requirements, while a registry makes it discoverable. Discovery identifies a candidate; authorization remains a separate boundary.

### 3. [A2UI Trusted Catalog Rendering](../concepts/llm-engineering/a2ui-trusted-catalog-rendering.md)
Move from agent-to-agent interaction to agent-to-user interaction. Use approved declarative components that each client renders natively instead of executing model-generated frontend code.

### 4. [A2UI Layout Ownership Patterns](../concepts/llm-engineering/a2ui-layout-ownership-patterns.md)
Choose the layout owner: let the model compose an interface for changing intent, or let a deterministic tool return a stable view for known inputs. Both options retain the same trusted component boundary.

### 5. [UCP and AP2 Commerce-Payment Separation](../concepts/llm-engineering/ucp-ap2-commerce-payment-separation.md)
Finish with a high-consequence example: an agent can discover goods and construct an order through UCP, while AP2 separately verifies a signed, limited human authorization to pay. This preserves useful autonomy without granting open-ended spending power.

---

## Case Study: Amazon Bedrock AgentCore's A2A Contract and Agent Registry

Step 2 introduced Agent Cards and registries as a general idea — a machine-readable capability profile plus a directory that stores it. This case study looks at how one managed platform, Amazon Bedrock AgentCore, turns that general idea into a testable wire contract and a governed catalog with an approval workflow.

### 6. [AgentCore A2A Protocol Contract](../concepts/llm-engineering/agentcore-a2a-protocol-contract.md)
AgentCore's concrete productization of the Agent Card half of step 2: a fixed, testable contract — JSON-RPC 2.0 over HTTP, an ARM64 container on port 9000, a `/.well-known/agent-card.json` discovery endpoint, and a `/ping` health check. Study this first in the case study because it shows what "discoverable and callable" looks like as an enforceable specification rather than a general principle.

### 7. [Agent Resource Registry Governance](../concepts/llm-engineering/agent-resource-registry-governance.md)
AgentCore's concrete productization of the registry half of step 2, adding the governance layer a real organization needs: a publish-review-approve-deprecate workflow, hybrid semantic-and-keyword search, EventBridge notifications that plug into existing review pipelines, and a native MCP endpoint so other agents can query the catalog directly. Study this last because it shows why a registry needs more than a lookup table once many teams are publishing into it.

---

## What You'll Be Able to Do

- Choose a bounded tool call or a delegated agent based on whether the work can evolve over time
- Make specialist agents discoverable without treating discovery as authorization
- Render agent-driven UI through a trusted, client-owned component catalog
- Assign layout decisions to a model or deterministic tool based on what determines the interface
- Keep agentic commerce separate from constrained human payment authorization
- Implement an A2A server against a concrete, testable wire contract instead of an ad hoc message format
- Evaluate whether a registry needs an approval workflow, and design one with curation, notifications, and MCP-native discovery
