---
id: langgraph-toolnode-prebuilt-components
title: LangGraph ToolNode and Prebuilt Components
source: sources/repos/langchain-ai-langgraph
status: draft
created_at: 2026-05-05
---

- **One-sentence definition**: LangGraph prebuilt components provide reusable tool-execution building blocks, especially `ToolNode`, `tools_condition`, and tool injection helpers, while older `create_react_agent` helpers are deprecated.
- **Why it matters**: Tool execution has recurring mechanics: parse model tool calls, inject hidden state or store values, run tools in parallel, handle errors, and return `ToolMessage` or `Command` outputs. `ToolNode` packages these mechanics as a graph node that understands LangChain tools and LangGraph runtime context. `InjectedState`, `InjectedStore`, and `ToolRuntime` keep private runtime values out of the model-visible tool schema. The source material also warns that `create_react_agent` is deprecated in favor of `langchain.agents.create_agent`, so this concept should emphasize the active lower-level tool components rather than teaching the deprecated factory as the recommended API.
- **Relationship to existing concepts**: This is the LangGraph execution-side companion to `langchain-tool-schema-contract`. It also relates to `react-agentic-loop`, but focuses on how LangGraph executes tool calls in graph state rather than the general reasoning/action pattern.
- **Source notes**: `Prebuilt_Components.md`, `ReAct_Agent_create_react_agent.md`, `Control_Flow_Primitives.md`.
