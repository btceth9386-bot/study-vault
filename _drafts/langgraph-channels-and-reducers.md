---
id: langgraph-channels-and-reducers
title: LangGraph Channels and Reducers
source: sources/repos/langchain-ai-langgraph
status: draft
created_at: 2026-05-05
---

- **One-sentence definition**: LangGraph channels are per-state-field containers that define how values are read, updated, merged, checkpointed, and used to trigger later nodes.
- **Why it matters**: Channels are the difference between safe parallel graph execution and accidental state corruption. `LastValue` is appropriate when only one writer should update a field in a superstep; it raises an error for conflicting multi-writer updates. `BinaryOperatorAggregate` uses a reducer to merge multiple writes, such as appending messages or combining dictionaries. `Topic`, `EphemeralValue`, `UntrackedValue`, and barrier channels provide specialized behavior for accumulation, transient signals, non-persisted values, and synchronization. Choosing the wrong channel semantics can make a graph nondeterministic or fail at runtime.
- **Relationship to existing concepts**: This refines `langgraph-stategraph-state-schema`, because the schema is compiled into these channel objects. It also explains why `langchain-core-message-model-for-langgraph-state` often needs a reducer-backed `messages` field instead of a simple replace-on-write field.
- **Source notes**: `State_Management_and_Channels.md`, `Pregel_Execution_Engine.md`.
