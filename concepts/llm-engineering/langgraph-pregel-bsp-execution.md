---
id: langgraph-pregel-bsp-execution
title: LangGraph Pregel BSP Execution
depth: 2
last_reviewed: 2026-05-05
review_due: 2026-05-08
sources:
  - sources/repos/langchain-ai-langgraph
related:
  - langgraph-stategraph-state-schema
  - async-processing
  - langgraph-send-command-control-flow
  - langgraph-checkpoint-time-travel-forking
tags:
  - llm-engineering
  - langgraph
  - orchestration
  - stateful-workflows
---

# LangGraph Pregel BSP Execution

- **One-sentence definition**: LangGraph's Pregel runtime executes graph work in Bulk Synchronous Parallel supersteps: choose runnable nodes, run them in parallel, then apply their writes together.
- **Why it exists / what problem it solves**: Agent graphs can branch, run parallel nodes, and merge results. Pregel gives those updates a predictable timing model, so developers know when a write becomes visible and why concurrent writes need reducers.
- **Keywords**: Pregel, BSP, superstep, plan, execute, update, checkpoint
- **Related concepts**: [[langgraph-stategraph-state-schema]], [[async-processing]], [[langgraph-send-command-control-flow]], [[langgraph-checkpoint-time-travel-forking]]
- **Depth**: 2/4
- **Last updated**: 2026-05-05
- **Source**: sources/repos/langchain-ai-langgraph

## Summary

Pregel is the engine underneath compiled LangGraph workflows. It works like a classroom exercise: first decide which students should work, let them all write their answers without looking at each other's papers, then collect and publish the answers at the end of the round.

LangGraph calls those rounds supersteps. In the plan phase, the runtime decides which nodes are ready. In the execute phase, those nodes run concurrently. In the update phase, their writes are applied to channels, making the new state visible to the next superstep.

This explains a common debugging surprise: two nodes in the same superstep cannot read each other's new writes. Their outputs become visible only after the update phase.

## Example

```text
Superstep 1
  Plan: A and B are runnable
  Execute: A writes {"score": 1}; B writes {"score": 2}
  Update: reducer merges or channel rejects conflicting writes

Superstep 2
  Nodes can now read the updated score
```

If `score` is a plain replace-on-write field, concurrent writes may be invalid. If it has a reducer, LangGraph can merge the writes safely.

## Relationship to existing concepts

- [[langgraph-stategraph-state-schema]]: The schema determines which channels receive Pregel writes.
- [[async-processing]]: Both concepts separate work execution from immediate visibility, but Pregel is a graph runtime model rather than a queue architecture.
- [[langgraph-send-command-control-flow]]: Edges, `Send`, and `Command` decide which tasks Pregel schedules into future supersteps.
- [[langgraph-checkpoint-time-travel-forking]]: Checkpoints are naturally tied to Pregel step boundaries, where state has been consistently updated.

## Open questions

- How should graph tests assert behavior that depends on superstep boundaries?
- Which node outputs should be designed for parallel fan-out from the beginning?
