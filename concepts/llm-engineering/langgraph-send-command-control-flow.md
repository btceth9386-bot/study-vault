---
id: langgraph-send-command-control-flow
title: LangGraph Send and Command Control Flow
depth: 2
last_reviewed: 2026-05-05
review_due: 2026-05-08
sources:
  - sources/repos/langchain-ai-langgraph
related:
  - langgraph-pregel-bsp-execution
  - react-agentic-loop
tags:
  - llm-engineering
  - langgraph
  - orchestration
  - agents
---

# LangGraph Send and Command Control Flow

- **One-sentence definition**: LangGraph control flow uses edges, conditional routing, `Send`, and `Command` to decide which nodes run next and what state they receive.
- **Why it exists / what problem it solves**: Agent workflows should not hide routing inside a black-box loop. LangGraph lets developers make routing explicit, while still supporting dynamic fan-out and node-local navigation decisions.
- **Keywords**: static edges, conditional edges, Send, Command, START, END, routing
- **Related concepts**: [[langgraph-pregel-bsp-execution]], [[react-agentic-loop]]
- **Depth**: 2/4
- **Last updated**: 2026-05-05
- **Source**: sources/repos/langchain-ai-langgraph

## Summary

LangGraph control flow is the traffic plan for a workflow. Static edges are fixed roads. Conditional edges are intersections that choose a road based on state. `START` and `END` are virtual entry and exit points.

`Send` is useful when one node needs to fan out into many tasks. For example, a graph can send each document chunk to the same summarizer node with a different slice of state. `Command` is useful when a node should both update state and choose the next destination, instead of splitting that decision into a separate router function.

The key idea is that LangGraph makes the loop visible. You can express agent behavior as graph routing rather than relying on an older high-level agent executor.

## Example

```python
from langgraph.types import Send, Command

def fan_out(state):
    return [Send("summarize_chunk", {"chunk": chunk}) for chunk in state["chunks"]]

def decide_next(state) -> Command:
    if state["needs_tool"]:
        return Command(update={"status": "tooling"}, goto="call_tool")
    return Command(update={"status": "done"}, goto="final_answer")
```

`Send` creates several parallel tasks. `Command` makes a node's state update and next step part of one return value.

## Relationship to existing concepts

- [[langgraph-pregel-bsp-execution]]: Control-flow primitives decide which work Pregel schedules into supersteps.
- [[react-agentic-loop]]: A ReAct-style loop can be modeled as explicit graph routing between model, tool, and answer nodes.

## Open questions

- When is a separate conditional edge clearer than returning `Command` from inside a node?
- How much dynamic fan-out is safe before the graph needs explicit rate limits or batching?
