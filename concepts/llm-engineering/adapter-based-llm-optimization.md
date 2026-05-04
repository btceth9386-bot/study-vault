---
id: adapter-based-llm-optimization
title: Adapter-Based LLM Optimization
depth: 2
last_reviewed: 2026-05-04
review_due: 2026-05-07
sources:
  - sources/repos/gepa-ai-gepa
related:
  - metric-driven-llm-optimization
  - dspy-signatures
  - dspy-module-composition
  - react-agentic-loop
  - optimize-anything-pattern
  - reflective-mutation-proposer
tags:
  - llm-engineering
  - architecture
  - optimization
---

# Adapter-Based LLM Optimization

- **One-sentence definition**: Adapter-based LLM optimization lets a generic optimizer improve many kinds of systems by asking each system adapter to handle execution, scoring, and trace formatting.
- **Why it exists / what problem it solves**: A prompt optimizer should not need custom engine logic for every framework. An adapter boundary lets GEPA optimize single prompts, DSPy programs, RAG pipelines, MCP tools, and custom evaluators through the same core loop.
- **Keywords**: adapter, evaluation, traces, reflective dataset, candidate, integration
- **Related concepts**: [[metric-driven-llm-optimization]], [[dspy-signatures]], [[dspy-module-composition]], [[react-agentic-loop]], [[optimize-anything-pattern]], [[reflective-mutation-proposer]]
- **Depth**: 2/4
- **Last updated**: 2026-05-04
- **Source**: sources/repos/gepa-ai-gepa

## Summary

Think of GEPA as a coach and the adapter as a translator. The coach knows how to run an optimization loop, but it does not know the rules of every game. The adapter explains how to run the current system, how to score it, and how to turn its traces into feedback.

This separation keeps the engine reusable. The same optimizer can work on a DSPy module, a tool-using agent, or an arbitrary text artifact because each adapter maps that domain into candidates, evaluations, and reflective examples.

## Example

A custom RAG adapter might define:

```python
def evaluate(batch, candidate, capture_traces):
    pipeline = build_rag_pipeline(
        query_prompt=candidate["query_rewriter"],
        answer_prompt=candidate["answer_generator"],
    )
    return run_and_score(batch, pipeline, capture_traces=capture_traces)
```

GEPA does not need to know how the vector store works. It only needs the adapter to return scores, outputs, and optional traces.

## Relationship to existing concepts

- [[metric-driven-llm-optimization]]: The adapter supplies the metric data that drives optimization.
- [[dspy-signatures]]: DSPy adapters can treat signature instructions as optimizable candidate components.
- [[dspy-module-composition]]: Adapters can discover and update components inside a composed program.
- [[react-agentic-loop]]: Agent adapters can optimize tool descriptions and system prompts from tool-use traces.
- [[optimize-anything-pattern]]: `optimize_anything()` is a broad adapter pattern for arbitrary scored text artifacts.
- [[reflective-mutation-proposer]]: Reflective mutation depends on the adapter to evaluate candidates and format trace feedback.

## Open questions

- What trace format is rich enough for reflection but small enough to store cheaply?
- When is `optimize_anything()` enough, and when should a team write a custom adapter?
