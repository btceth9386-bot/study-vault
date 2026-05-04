---
id: react-agentic-loop
title: ReAct Agentic Loop
depth: 2
last_reviewed: 2026-05-04
review_due: 2026-05-07
sources:
  - sources/repos/stanfordnlp-dspy
related:
  - dspy-module-composition
  - few-shot-bootstrapping
  - llm-observability
  - metric-driven-llm-optimization
  - adapter-based-llm-optimization
  - langchain-tool-schema-contract
tags:
  - llm-engineering
  - dspy
  - agents
  - tool-use
---

# ReAct Agentic Loop

- **One-sentence definition**: The ReAct loop lets an LLM alternate between reasoning, calling tools, and reading tool results until it has enough information to answer.
- **Why it exists / what problem it solves**: A single LLM call cannot fetch fresh data, run code, or query external systems by itself. ReAct gives the model a structured way to decide which tool to use, observe the result, and continue.
- **Keywords**: ReAct, agent, tool use, thought, action, observation, trajectory
- **Related concepts**: [[dspy-module-composition]], [[few-shot-bootstrapping]], [[llm-observability]], [[metric-driven-llm-optimization]], [[adapter-based-llm-optimization]], [[langchain-tool-schema-contract]]
- **Depth**: 2/4
- **Last updated**: 2026-05-04
- **Source**: sources/repos/stanfordnlp-dspy

## Summary

ReAct stands for reasoning and acting. The model first thinks about what it needs, then chooses an action such as calling a search tool, then receives an observation from that tool. It repeats this loop until it can produce the final answer.

In DSPy, `dspy.ReAct` packages this pattern as a module. The signature defines the final task, the tools define what the agent can do, and the loop is bounded so it cannot run forever. The resulting trajectory is useful for debugging and for optimization because it shows not only the final answer, but also the steps that led there.

## Example

```python
def search_docs(query: str) -> str:
    """Search internal documentation and return the most relevant passage."""
    ...

agent = dspy.ReAct("question -> answer", tools=[search_docs], max_iters=5)
result = agent(question="Which setting controls retries?")
```

The agent can ask the search tool for missing information before answering, instead of guessing from the original prompt alone.

## Relationship to existing concepts

- [[dspy-module-composition]]: ReAct is a DSPy module with internal predictors and loop state.
- [[few-shot-bootstrapping]]: Successful ReAct traces can teach the model useful tool-calling sequences.
- [[llm-observability]]: The thought, action, and observation steps are exactly the kind of trace data an LLM system should record.
- [[metric-driven-llm-optimization]]: A metric can score the final answer or the full tool-use trajectory.
- [[adapter-based-llm-optimization]]: Agent adapters can expose tool descriptions and system prompts as optimizable components.
- [[langchain-tool-schema-contract]]: LangChain's tool-call schema is one concrete way to carry the Action and Observation parts of a tool loop through model and tool messages.

## Open questions

- Which tool errors should be retried, and which should stop the loop immediately?
- How should a metric judge a correct final answer reached through inefficient tool use?
