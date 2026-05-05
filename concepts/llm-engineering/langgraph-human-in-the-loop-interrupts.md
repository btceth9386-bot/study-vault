---
id: langgraph-human-in-the-loop-interrupts
title: LangGraph Human-in-the-Loop Interrupts
depth: 2
last_reviewed: 2026-05-05
review_due: 2026-05-08
sources:
  - sources/repos/langchain-ai-langgraph
related:
  - langgraph-checkpoint-time-travel-forking
  - llm-observability
tags:
  - llm-engineering
  - langgraph
  - human-in-the-loop
  - durability
---

# LangGraph Human-in-the-Loop Interrupts

- **One-sentence definition**: LangGraph interrupts pause graph execution so a human or external system can inspect, approve, edit, or resume a workflow.
- **Why it exists / what problem it solves**: Production agents often need approval before taking risky actions, user input after a workflow starts, or manual correction after a bad intermediate result. Interrupts make those pauses part of the runtime instead of an ad hoc stop button.
- **Keywords**: interrupts, checkpointing, approval, resume, human review, re-execution
- **Related concepts**: [[langgraph-checkpoint-time-travel-forking]], [[llm-observability]]
- **Depth**: 2/4
- **Last updated**: 2026-05-05
- **Source**: sources/repos/langchain-ai-langgraph

## Summary

An interrupt is like putting a bookmark in a workflow and handing the book to a reviewer. The graph stops at a known point, exposes enough state for a decision, and can continue later.

LangGraph supports static interrupts around configured nodes and dynamic `interrupt()` calls inside node logic. Dynamic interrupts are powerful because a node can pause exactly where it needs user input. The trade-off is that, on resume, the node re-executes from the beginning and the `interrupt()` call returns the resume value.

Because of that re-execution behavior, code around dynamic interrupts must be safe to run again. Side effects should be guarded, delayed, or made idempotent.

## Example

```python
from langgraph.types import interrupt

def approve_email(state):
    decision = interrupt({
        "draft": state["email_draft"],
        "question": "Send this email?"
    })
    return {"approved": decision == "yes"}
```

The graph can pause with the draft visible to a human. When resumed with `"yes"`, the node continues and records approval.

## Relationship to existing concepts

- [[langgraph-checkpoint-time-travel-forking]]: Interrupts require persisted execution state so the graph can resume after a pause.
- [[llm-observability]]: Interrupted runs expose state snapshots and decisions that should be traceable for debugging and audit.

## Open questions

- Which side effects should happen before an interrupt, and which should wait until after approval?
- What review UI should expose state without leaking sensitive prompt or user data?
