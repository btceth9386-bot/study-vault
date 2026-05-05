---
id: langgraph-checkpoint-time-travel-forking
title: LangGraph Checkpoint Time Travel and Forking
depth: 2
last_reviewed: 2026-05-05
review_due: 2026-05-08
sources:
  - sources/repos/langchain-ai-langgraph
related:
  - langgraph-pregel-bsp-execution
  - langgraph-human-in-the-loop-interrupts
  - langgraph-remotegraph-server-execution
tags:
  - llm-engineering
  - langgraph
  - durability
  - stateful-workflows
---

# LangGraph Checkpoint Time Travel and Forking

- **One-sentence definition**: LangGraph checkpoints persist graph execution state so a run can resume, be inspected historically, replay from an earlier point, or fork into an alternative branch.
- **Why it exists / what problem it solves**: Long-running agents can fail, pause for humans, call tools, and produce surprising intermediate states. Checkpoints give developers recoverability and a way to debug "what happened here?" without relying only on final output logs.
- **Keywords**: checkpoint, state history, replay, fork, update_state, resume, threads
- **Related concepts**: [[langgraph-pregel-bsp-execution]], [[langgraph-human-in-the-loop-interrupts]], [[langgraph-remotegraph-server-execution]]
- **Depth**: 2/4
- **Last updated**: 2026-05-05
- **Source**: sources/repos/langchain-ai-langgraph

## Summary

A checkpoint is a saved game for a graph. It records enough state to continue later, inspect the route taken, or try a different route from the same point.

LangGraph checkpoints can store channel values, versions, pending tasks, and metadata. State history exposes the chain of checkpoints. Replay starts from an older checkpoint and reruns later work. Forking uses `update_state()` at a selected checkpoint to create a new branch, then continues from the modified state.

This is especially useful for agent debugging. Instead of rerunning the whole conversation from scratch, you can jump back to a meaningful state and test a different decision.

## Example

```python
history = list(graph.get_state_history(config))
old = history[-3]

graph.update_state(
    old.config,
    {"approved": False},
)

result = graph.invoke(None, old.config)
```

The updated checkpoint becomes a new branch. The original history remains available for comparison.

## Relationship to existing concepts

- [[langgraph-pregel-bsp-execution]]: Pregel superstep boundaries provide natural points where checkpointed state is consistent.
- [[langgraph-human-in-the-loop-interrupts]]: Interrupts depend on checkpoints to pause and resume safely.
- [[langgraph-remotegraph-server-execution]]: LangGraph Server exposes thread state and history through remote APIs.

## Open questions

- How much checkpoint history should be retained for cost, privacy, and debugging value?
- Which external side effects need compensation when replaying or forking a graph?
