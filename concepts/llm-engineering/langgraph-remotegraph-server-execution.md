---
id: langgraph-remotegraph-server-execution
title: LangGraph RemoteGraph and Server Execution
depth: 2
last_reviewed: 2026-05-05
review_due: 2026-05-08
sources:
  - sources/repos/langchain-ai-langgraph
related:
  - langgraph-checkpoint-time-travel-forking
  - langgraph-store-long-term-memory
  - microservices
tags:
  - llm-engineering
  - langgraph
  - deployment
  - orchestration
---

# LangGraph RemoteGraph and Server Execution

- **One-sentence definition**: LangGraph Server exposes deployed graphs through APIs for assistants, threads, runs, scheduled jobs, and store memory, while `RemoteGraph` lets a remote graph behave like a local graph object.
- **Why it exists / what problem it solves**: Production graphs often need to run outside the current Python process, keep durable thread state, stream results, schedule work, and compose with other services. Server execution gives those workflows an operational boundary without abandoning the graph model.
- **Keywords**: LangGraph Server, RemoteGraph, assistants, threads, runs, cron, store
- **Related concepts**: [[langgraph-checkpoint-time-travel-forking]], [[langgraph-store-long-term-memory]], [[microservices]]
- **Depth**: 2/4
- **Last updated**: 2026-05-05
- **Source**: sources/repos/langchain-ai-langgraph

## Summary

Running a graph locally is useful for development, but production often needs a service. LangGraph Server turns graph execution into API resources: assistants represent configured graph versions, threads hold stateful sessions, runs execute work, cron jobs schedule work, and the store holds long-term memory.

`RemoteGraph` is the client-side bridge. It wraps the server API behind a graph-like interface, so code can invoke, stream, inspect state, update state, and handle interrupts against a remote deployment.

This lets a local graph call a remote graph as one of its steps, which is useful when graph boundaries also need to be service boundaries.

## Example

```python
from langgraph.pregel.remote import RemoteGraph

support_graph = RemoteGraph("support-agent", url="https://graphs.example.com")
result = support_graph.invoke(
    {"messages": [("user", "I need help with billing.")]},
    config={"configurable": {"thread_id": "ticket-123"}},
)
```

The caller uses a graph-like interface, while execution, thread state, and store access live behind the LangGraph Server API.

## Relationship to existing concepts

- [[langgraph-checkpoint-time-travel-forking]]: Remote threads expose durable state and history for deployed graph runs.
- [[langgraph-store-long-term-memory]]: Server-side store APIs provide shared memory for remote graphs.
- [[microservices]]: Remote graphs can become service boundaries while preserving a graph-native invocation model.

## Open questions

- When should a graph stay in-process, and when is a remote graph boundary worth the network and operations cost?
- How should tracing and authentication propagate across local and remote graph calls?
