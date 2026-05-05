---
id: langgraph-runtime-dependency-injection
title: LangGraph Runtime Dependency Injection
source: sources/repos/langchain-ai-langgraph
status: draft
created_at: 2026-05-05
---

- **One-sentence definition**: LangGraph runtime dependency injection supplies nodes and tools with run-scoped context, persistent store access, stream writers, and execution metadata without manually threading those values through graph state.
- **Why it matters**: Not every value a node needs belongs in persisted graph state. A user ID, database handle, current attempt number, stream writer, or server metadata may be execution context rather than domain state. LangGraph's `Runtime` object and injectable parameters let node signatures request these dependencies directly. This keeps graph state focused on the workflow while still giving nodes access to cross-cutting services such as memory, streaming, retries, and server information.
- **Relationship to existing concepts**: This complements `langgraph-store-long-term-memory`, because `Runtime.store` is one way nodes access the store. It also connects to `provider-chat-model-wrappers-in-langgraph-nodes`, where runtime context can select model configuration or route provider behavior inside a node.
- **Source notes**: `Runtime_and_Dependency_Injection.md`, `Pregel_Execution_Engine.md`, `Prebuilt_Components.md`.
