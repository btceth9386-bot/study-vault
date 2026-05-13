---
id: langgraph-toolnode-prebuilt-components
title: LangGraph ToolNode and Prebuilt Components
depth: 2
last_reviewed: '2026-05-13'
review_due: '2026-05-16'
sources:
- sources/repos/langchain-ai-langgraph/
related:
- langgraph-channels-and-reducers
- langgraph-runtime-dependency-injection
tags:
- llm-engineering
- langgraph
- langchain
- agents
- orchestration
- stateful-workflows
- human-in-the-loop
---

# LangGraph ToolNode and Prebuilt Components

- **一句話定義**：LangGraph prebuilt components provide reusable tool-execution building blocks, especially `ToolNode`, `tools_condition`, and tool injection helpers, while older `create_react_agent` helpers are deprecated.
- **為什麼存在 / 解決什麼問題**：Tool execution has recurring mechanics: parse model tool calls, inject hidden state or store values, run tools in parallel, handle errors, and return `ToolMessage` or `Command` outputs. `ToolNode` packages these mechanics as a graph node that understands LangChain tools and LangGraph runtime context. `InjectedState`, `InjectedStore`, and `ToolRuntime` keep private runtime values out of the model-visible tool schema. The source material also warns that `create_react_agent` is deprecated in favor of `langchain.agents.create_agent`, so this concept should emphasize the active lower-level tool components rather than teaching the deprecated factory as the recommended API.
- **關鍵字**：llm-engineering, langgraph, langchain, agents, orchestration, stateful-workflows, human-in-the-loop
- **相關概念**：[[langgraph-channels-and-reducers]], [[langgraph-runtime-dependency-injection]]
- **深度等級**：2/4
- **最後更新**：2026-05-13
- **來源**：langchain-ai/langgraph

## 摘要

Think of LangGraph ToolNode and Prebuilt Components as a design pattern for making agent or backend systems easier to operate. LangGraph prebuilt components provide reusable tool-execution building blocks, especially `ToolNode`, `tools_condition`, and tool injection helpers, while older `create_react_agent` helpers are deprecated. It matters because the simple version of the system usually works only in demos; production systems need state, boundaries, recovery, and observability. Tool execution has recurring mechanics: parse model tool calls, inject hidden state or store values, run tools in parallel, handle errors, and return `ToolMessage` or `Command` outputs.

## 範例

Suppose an engineering team is turning an agent prototype into a service used every day. Instead of treating LangGraph ToolNode and Prebuilt Components as theory, they ask: what breaks if this piece is missing? The answer is visible in the source, **langchain-ai/langgraph**: Tool execution has recurring mechanics: parse model tool calls, inject hidden state or store values, run tools in parallel, handle errors, and return `ToolMessage` or `Command` outputs. That makes the concept a design check the team can apply before the system reaches production.

## 與既有概念的關聯

- [[langgraph-channels-and-reducers]]: langgraph-toolnode-prebuilt-components connects to langgraph-channels-and-reducers because both describe a nearby part of the same learning path or system design problem.
- [[langgraph-runtime-dependency-injection]]: langgraph-toolnode-prebuilt-components connects to langgraph-runtime-dependency-injection because both describe a nearby part of the same learning path or system design problem.

## 我的疑問

- What examples would make this concept easier to recognize in future sources?
- When would this concept be misleading or too broad?
