---
id: langchain-core-message-model-for-langgraph-state
title: LangChain Message Model for LangGraph State
depth: 2
last_reviewed: '2026-05-13'
review_due: '2026-05-16'
sources:
- sources/repos/langchain-ai-langchain/
related:
- react-agentic-loop
tags:
- llm-engineering
- langchain
- langgraph
- rag
---

# LangChain Message Model for LangGraph State

- **一句話定義**：LangChain's `BaseMessage` hierarchy is a provider-neutral conversation record format that lets LangGraph store, route, checkpoint, and replay user, model, and tool interactions as structured state.
- **為什麼存在 / 解決什麼問題**：LangGraph applications commonly keep a `messages` list in graph state. Using `HumanMessage`, `AIMessage`, and `ToolMessage` instead of raw strings preserves role, ID, provider metadata, tool calls, invalid tool calls, token usage, and the `tool_call_id` needed to connect a tool result to the model request that caused it. This makes a graph's state durable across checkpoints and portable across model providers. It also gives routing logic a stable surface: a node can inspect the latest `AIMessage.tool_calls` to decide whether to execute tools, then append `ToolMessage` results before returning control to the model. `RemoveMessage` is LangGraph-specific and exists for deleting stored messages by ID, reinforcing that the message model is not just formatting but state mutation vocabulary.
- **關鍵字**：llm-engineering, langchain, langgraph, rag
- **相關概念**：[[react-agentic-loop]]
- **深度等級**：2/4
- **最後更新**：2026-05-13
- **來源**：langchain-ai/langchain

## 摘要

Think of LangChain Message Model for LangGraph State as a design pattern for making agent or backend systems easier to operate. LangChain's `BaseMessage` hierarchy is a provider-neutral conversation record format that lets LangGraph store, route, checkpoint, and replay user, model, and tool interactions as structured state. It matters because the simple version of the system usually works only in demos; production systems need state, boundaries, recovery, and observability. LangGraph applications commonly keep a `messages` list in graph state.

## 範例

Suppose an engineering team is turning an agent prototype into a service used every day. Instead of treating LangChain Message Model for LangGraph State as theory, they ask: what breaks if this piece is missing? The answer is visible in the source, **langchain-ai/langchain**: LangGraph applications commonly keep a `messages` list in graph state. That makes the concept a design check the team can apply before the system reaches production.

## 與既有概念的關聯

- [[react-agentic-loop]]: langchain-core-message-model-for-langgraph-state connects to react-agentic-loop because both describe a nearby part of the same learning path or system design problem.

## 我的疑問

- What examples would make this concept easier to recognize in future sources?
- When would this concept be misleading or too broad?
