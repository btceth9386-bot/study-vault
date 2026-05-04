---
id: reflective-mutation-proposer
title: Reflective Mutation Proposer
depth: 2
last_reviewed: 2026-05-04
review_due: 2026-05-07
sources:
  - sources/repos/gepa-ai-gepa
related:
  - actionable-side-information
  - metric-driven-llm-optimization
  - adapter-based-llm-optimization
  - pareto-efficient-candidate-selection
  - system-aware-candidate-merge
tags:
  - llm-engineering
  - optimization
  - prompts
---

# Reflective Mutation Proposer

- **One-sentence definition**: A reflective mutation proposer creates a better text candidate by studying a current candidate's failures, then asking an LLM to rewrite the relevant component.
- **Why it exists / what problem it solves**: Blindly changing prompts wastes evaluations. Reflective mutation uses real examples, scores, and traces to decide what should change, then tests the mutated candidate before accepting it.
- **Keywords**: reflection, mutation, proposer, minibatch, traces, candidate, feedback
- **Related concepts**: [[actionable-side-information]], [[metric-driven-llm-optimization]], [[adapter-based-llm-optimization]], [[pareto-efficient-candidate-selection]], [[system-aware-candidate-merge]]
- **Depth**: 2/4
- **Last updated**: 2026-05-04
- **Source**: sources/repos/gepa-ai-gepa

## Summary

Think of reflective mutation as a careful prompt edit with a lab notebook open. The system first runs the current candidate on a small batch and captures what happened. It then turns those traces into feedback for a reflection model.

The reflection model proposes new text, such as a revised instruction or tool description. GEPA evaluates the new candidate on the same batch and only sends it forward if it improves. This keeps the candidate pool focused on changes that have at least some measured evidence behind them.

## Example

A candidate system prompt says:

```text
Answer math questions directly.
```

On a minibatch, the trace shows wrong answers when the problem needs several steps. The reflective proposer may rewrite the component to:

```text
Break the problem into steps, compute each step carefully, then give the final answer.
```

If the revised candidate scores better on the same examples, it can be accepted for broader validation.

## Relationship to existing concepts

- [[actionable-side-information]]: Reflection needs diagnostic feedback to explain what went wrong.
- [[metric-driven-llm-optimization]]: The proposed mutation is judged by a metric, not by intuition.
- [[adapter-based-llm-optimization]]: The adapter supplies the evaluation traces and reflective dataset.
- [[pareto-efficient-candidate-selection]]: Candidate selection decides which existing variant should be mutated.
- [[system-aware-candidate-merge]]: Merge is the complementary proposal path that recombines successful mutations.

## Open questions

- When should reflection update one component versus several components at once?
- How large should a minibatch be before the feedback is trustworthy?
