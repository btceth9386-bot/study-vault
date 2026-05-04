---
id: provider-chat-model-wrappers-in-langgraph-nodes
title: Provider Chat Model Wrappers in LangGraph Nodes
depth: 2
last_reviewed: 2026-05-05
review_due: 2026-05-08
sources:
  - sources/repos/langchain-ai-langchain
related:
  - langchain-tool-schema-contract
  - standardized-message-content-blocks
  - retrievers-vector-stores-for-langgraph-rag
tags:
  - llm-engineering
  - langchain
  - langgraph
  - provider-integrations
---

# Provider Chat Model Wrappers in LangGraph Nodes

- **One-sentence definition**: Provider chat model wrappers adapt APIs such as OpenAI and Anthropic to LangChain's common chat model interface, so a LangGraph node can send messages and receive an `AIMessage` without owning provider-specific wiring.
- **Why it exists / what problem it solves**: Each model provider has a different wire format, client setup, streaming behavior, and tool-calling shape. Wrappers such as `ChatOpenAI` and `ChatAnthropic` hide those differences behind the same `BaseChatModel` and `Runnable` surface.
- **Keywords**: ChatOpenAI, ChatAnthropic, BaseChatModel, Runnable, AIMessage, bind_tools
- **Related concepts**: [[langchain-tool-schema-contract]], [[standardized-message-content-blocks]], [[retrievers-vector-stores-for-langgraph-rag]]
- **Depth**: 2/4
- **Last updated**: 2026-05-05
- **Source**: sources/repos/langchain-ai-langchain

## Summary

A LangGraph node should usually care about application state: read the current messages, call a model, and return the next state update. It should not need to know every detail of OpenAI's or Anthropic's HTTP payloads. A provider chat model wrapper is the adapter that handles those details.

In LangChain, wrappers like `ChatOpenAI` and `ChatAnthropic` implement the same modern chat model interface. They accept LangChain messages, convert them to the provider's format, handle provider options, and return common message objects such as `AIMessage`. Because these wrappers are also `Runnable` objects, the same model can support `.invoke()`, `.ainvoke()`, `.stream()`, `.bind_tools()`, and `.with_structured_output()` where the integration supports them.

LCEL expressions such as `prompt | model | parser` explain why these objects compose, but this concept is not about old chain abstractions. In a LangGraph application, the graph owns control flow; the provider wrapper is the model-call dependency inside a node.

## Example

```python
from langchain_openai import ChatOpenAI

def call_model(state: dict) -> dict:
    model = ChatOpenAI(model="gpt-4o-mini")
    ai_message = model.invoke(state["messages"])
    return {"messages": [ai_message]}
```

The node does not manually convert messages into OpenAI request dictionaries. The wrapper handles that conversion and returns a LangChain `AIMessage` that the graph can append to state.

## Relationship to existing concepts

- [[langchain-tool-schema-contract]]: Wrappers expose tool binding and return parsed tool calls when the model asks to use a tool.
- [[standardized-message-content-blocks]]: Wrappers translate provider-specific content formats into LangChain's common message content structure.
- [[retrievers-vector-stores-for-langgraph-rag]]: Retrieval results become useful only when a graph node feeds them into a model wrapper as context or messages.

## Open questions

- Which provider-specific options should stay inside the wrapper configuration, and which should be exposed as graph state?
- How should a graph handle fallback between providers when their tool-calling or content-block support differs?
