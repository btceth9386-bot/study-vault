---
id: langchain-core-message-model-for-langgraph-state
title: LangChain Message Model for LangGraph State
source: sources/repos/langchain-ai-langchain
status: draft
created_at: 2026-05-05
---

- **One-sentence definition**: LangChain's `BaseMessage` hierarchy is a provider-neutral conversation record format that lets LangGraph store, route, checkpoint, and replay user, model, and tool interactions as structured state.
- **Why it matters**: LangGraph applications commonly keep a `messages` list in graph state. Using `HumanMessage`, `AIMessage`, and `ToolMessage` instead of raw strings preserves role, ID, provider metadata, tool calls, invalid tool calls, token usage, and the `tool_call_id` needed to connect a tool result to the model request that caused it. This makes a graph's state durable across checkpoints and portable across model providers. It also gives routing logic a stable surface: a node can inspect the latest `AIMessage.tool_calls` to decide whether to execute tools, then append `ToolMessage` results before returning control to the model. `RemoveMessage` is LangGraph-specific and exists for deleting stored messages by ID, reinforcing that the message model is not just formatting but state mutation vocabulary.
- **Relationship to other concepts**: This concept is adjacent to `react-agentic-loop`, but it is lower-level and does not depend on the legacy ReAct agent constructor. It is the state substrate consumed by provider-chat-model-wrappers-in-langgraph-nodes and langchain-tool-schema-contract. standardized-message-content-blocks refines the `content` field inside each message.
