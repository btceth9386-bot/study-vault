---
id: langgraph-stategraph-state-schema
title: LangGraph StateGraph State Schema
depth: 2
last_reviewed: 2026-05-05
review_due: 2026-05-08
sources:
  - sources/repos/langchain-ai-langgraph
related:
  - provider-chat-model-wrappers-in-langgraph-nodes
  - langchain-tool-schema-contract
  - standardized-message-content-blocks
  - langgraph-pregel-bsp-execution
tags:
  - llm-engineering
  - langgraph
  - stateful-workflows
  - orchestration
---

# LangGraph StateGraph State Schema

- **One-sentence definition**: A LangGraph `StateGraph` state schema is the typed contract that says what shared state fields exist and how node outputs update those fields.
- **Why it exists / what problem it solves**: Multi-step LLM workflows become hard to debug when every node passes loose dictionaries around. The schema makes graph state explicit, so nodes agree on field names, value types, and merge behavior.
- **Keywords**: StateGraph, state schema, TypedDict, channels, reducers, graph state
- **Related concepts**: [[provider-chat-model-wrappers-in-langgraph-nodes]], [[langchain-tool-schema-contract]], [[standardized-message-content-blocks]], [[langgraph-pregel-bsp-execution]]
- **Depth**: 2/4
- **Last updated**: 2026-05-05
- **Source**: sources/repos/langchain-ai-langgraph

## Summary

Think of a LangGraph state schema as the shared notebook for a workflow. Every node can read from the notebook, and each node returns updates for specific pages in it. If the schema says there is a `messages` field, model nodes, tool nodes, and routing nodes can all use the same field instead of inventing their own shapes.

In LangGraph, the schema is often a `TypedDict`, Pydantic model, or dataclass. During compilation, each state field becomes a runtime channel. A normal field is usually replaced by the latest write, while an annotated field can use a reducer to merge multiple writes, such as appending new messages.

The important point is that the schema is not just documentation. It controls how node return values become durable graph state.

## Example

```python
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    approved: bool

def call_model(state: AgentState) -> dict:
    response = model.invoke(state["messages"])
    return {"messages": [response]}
```

The `messages` field can merge new messages into the existing list. The `approved` field is simpler: a node can replace it with `True` or `False`.

## Relationship to existing concepts

- [[provider-chat-model-wrappers-in-langgraph-nodes]]: Provider wrappers are often called inside nodes that read and write fields from the state schema.
- [[langchain-tool-schema-contract]]: Tool calls and tool results usually move through state as structured messages.
- [[standardized-message-content-blocks]]: Message fields can contain provider-normalized content blocks that graph nodes can inspect.
- [[langgraph-pregel-bsp-execution]]: Pregel is the runtime that applies schema-based state updates at superstep boundaries.

## Open questions

- Which state fields should be durable checkpoints, and which should stay temporary inside one node?
- When should a field use reducer merge semantics instead of replace-on-write semantics?
