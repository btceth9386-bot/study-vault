---
id: agentic-workflow-span-hierarchy
title: Agentic Workflow Span Hierarchy
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-semantic-conventions-genai/
related:
  - react-agentic-loop
  - devops-agent-topology-context
  - context-propagation-with-carriers
tags:
  - observability
  - opentelemetry
  - generative-ai
  - agents
  - tracing
---

# Agentic Workflow Span Hierarchy

- **One-sentence definition**: An agentic workflow span hierarchy nests workflow, agent, plan, model, retrieval, and tool spans to show how a multi-step run fits together.
- **Why it exists / what problem it solves**: A flat list of model calls cannot explain which plan led to a tool call or where a workflow went wrong.
- **Keywords**: workflow, agent, plan, parent span, child span, tracing
- **Related concepts**: [[react-agentic-loop]], [[devops-agent-topology-context]], [[context-propagation-with-carriers]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: OpenTelemetry Semantic Conventions for Generative AI

## Summary

Think of the trace as a folder tree: the workflow is the top folder, an agent invocation sits inside it, and planning, model calls, retrieval, and tool calls sit beneath the agent. Parent-child links preserve the reason each piece of work happened.

The hierarchy is especially useful when an agent loops or delegates. It turns a long run into an inspectable story instead of unrelated timestamps.

## Example

For "find the current refund policy," `invoke_workflow` is the parent span. It contains an internal agent invocation, a plan span, a retrieval span for the policy document, an inference span for the answer, and a tool span for creating a support ticket.

## Relationship to existing concepts

- [[react-agentic-loop]]: Each reasoning, action, and observation step can appear in this trace hierarchy.
- [[devops-agent-topology-context]]: Topology adds service and dependency context to the work shown by the hierarchy.
- [[context-propagation-with-carriers]]: Propagation preserves parent-child context when a child operation runs in another process.

## My questions

- When should a planning step be a span instead of an event on the agent span?
- How much hierarchy is useful before a trace viewer needs summary spans?
