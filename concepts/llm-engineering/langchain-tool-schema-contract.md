---
id: langchain-tool-schema-contract
title: LangChain Tool Schema Contract
depth: 2
last_reviewed: 2026-05-05
review_due: 2026-05-08
sources:
  - sources/repos/langchain-ai-langchain
related:
  - provider-chat-model-wrappers-in-langgraph-nodes
  - standardized-message-content-blocks
  - retrievers-vector-stores-for-langgraph-rag
  - react-agentic-loop
  - langgraph-stategraph-state-schema
tags:
  - llm-engineering
  - langchain
  - langgraph
  - tools
  - tool-use
---

# LangChain Tool Schema Contract

- **One-sentence definition**: The LangChain tool schema contract is the shared format that turns Python tools into model-readable choices and turns model tool requests into executable `ToolCall` records.
- **Why it exists / what problem it solves**: A model cannot safely call a Python function by sending informal text like "search for this." The tool schema contract gives the model a named tool, validated inputs, and a call ID that downstream code can execute and answer with a matching `ToolMessage`.
- **Keywords**: BaseTool, StructuredTool, ToolCall, ToolMessage, args_schema, bind_tools
- **Related concepts**: [[provider-chat-model-wrappers-in-langgraph-nodes]], [[standardized-message-content-blocks]], [[retrievers-vector-stores-for-langgraph-rag]], [[react-agentic-loop]], [[langgraph-stategraph-state-schema]]
- **Depth**: 2/4
- **Last updated**: 2026-05-05
- **Source**: sources/repos/langchain-ai-langchain

## Summary

Think of a LangChain tool schema as a menu card for the model. The card says what tools exist, what each tool is called, and what ingredients each tool needs. In code, the `@tool` decorator, `BaseTool`, `StructuredTool`, type hints, docstrings, and explicit `args_schema` fields help build that menu.

When a provider chat model is bound to tools, the model can return an `AIMessage` with structured `tool_calls`. Each call includes the tool name, arguments, ID, and type. A graph tool node can then look up the matching `BaseTool`, run it, and append a `ToolMessage` that uses the same `tool_call_id`, so the model can connect the result back to its original request.

## Example

```python
from langchain_core.tools import tool

@tool
def lookup_policy(topic: str) -> str:
    """Return the current internal policy for a topic."""
    return policy_store[topic]

model_with_tools = model.bind_tools([lookup_policy])
response = model_with_tools.invoke(messages)

for call in response.tool_calls:
    result = lookup_policy.invoke(call)
    # The result can be returned as a ToolMessage tied to call["id"].
```

The important part is not the decorator alone. It is the full loop: describe the tool, let the model request it in a structured way, execute the matching tool, and return the result with the same call ID.

## Relationship to existing concepts

- [[provider-chat-model-wrappers-in-langgraph-nodes]]: Provider wrappers expose `.bind_tools()` and return `AIMessage.tool_calls` in the common LangChain shape.
- [[standardized-message-content-blocks]]: Tool use can also appear inside structured content blocks instead of plain text.
- [[retrievers-vector-stores-for-langgraph-rag]]: A retriever can be exposed as a tool when the model should decide when to fetch external context.
- [[react-agentic-loop]]: ReAct describes the higher-level thought/action/observation loop; the LangChain tool contract is the lower-level message and schema layer that can carry actions and observations.
- [[langgraph-stategraph-state-schema]]: Tool calls and tool results commonly travel through LangGraph state as message updates.

## Open questions

- When should a retrieval function be a graph node chosen by code, and when should it be a tool chosen by the model?
- How strict should tool schemas be when provider support for structured tool calling differs?
