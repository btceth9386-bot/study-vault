---
id: langgraph-store-long-term-memory
title: LangGraph Store Long-Term Memory
depth: 2
last_reviewed: 2026-05-05
review_due: 2026-05-08
sources:
  - sources/repos/langchain-ai-langgraph
related:
  - retrievers-vector-stores-for-langgraph-rag
  - langgraph-remotegraph-server-execution
tags:
  - llm-engineering
  - langgraph
  - memory
  - rag
---

# LangGraph Store Long-Term Memory

- **One-sentence definition**: LangGraph's store is a persistent, namespaced key-value memory layer for information that should survive across graph runs, threads, or conversations.
- **Why it exists / what problem it solves**: Checkpoints preserve one thread's execution state, but agents also need reusable memory such as user preferences, learned facts, shared documents, and semantic search records. The store keeps that memory separate from per-run state.
- **Keywords**: BaseStore, namespace, long-term memory, key-value store, vector search, TTL
- **Related concepts**: [[retrievers-vector-stores-for-langgraph-rag]], [[langgraph-remotegraph-server-execution]]
- **Depth**: 2/4
- **Last updated**: 2026-05-05
- **Source**: sources/repos/langchain-ai-langgraph

## Summary

Checkpoints are like a saved tab for one conversation. The LangGraph store is more like an address book or shared filing cabinet that many conversations can use.

The store API provides operations such as `get`, `put`, `search`, `delete`, and namespace listing. Implementations can be in-memory for tests, SQLite for local persistence, or PostgreSQL for production. Optional vector search and TTL support let the store act as semantic memory, not only exact key lookup.

Keeping store memory separate from checkpoints avoids stuffing every long-lived fact into a single thread's state.

## Example

```python
def remember_preference(state, runtime):
    user_id = runtime.context["user_id"]
    runtime.store.put(
        ("users", user_id, "preferences"),
        "timezone",
        {"value": state["timezone"]},
    )
    return {}
```

Another thread for the same user can read the preference later without depending on the original conversation checkpoint.

## Relationship to existing concepts

- [[retrievers-vector-stores-for-langgraph-rag]]: Both can support retrieval, but the LangGraph store is runtime memory that can be namespaced and shared across graph executions.
- [[langgraph-remotegraph-server-execution]]: LangGraph Server exposes store APIs so deployed graphs can use persistent memory remotely.

## Open questions

- What belongs in long-term memory versus thread-local checkpoint state?
- Which memories should expire automatically, and which should require explicit deletion?
