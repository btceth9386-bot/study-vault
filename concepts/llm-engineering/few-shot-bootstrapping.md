---
id: few-shot-bootstrapping
title: Few-Shot Bootstrapping
depth: 2
last_reviewed: 2026-05-04
review_due: 2026-05-07
sources:
  - sources/repos/stanfordnlp-dspy
related:
  - metric-driven-llm-optimization
  - dspy-module-composition
  - react-agentic-loop
  - llm-as-judge-evaluation
tags:
  - llm-engineering
  - dspy
  - optimization
  - evaluation
---

# Few-Shot Bootstrapping

- **One-sentence definition**: Few-shot bootstrapping automatically creates example demonstrations by running a teacher program and keeping the traces that pass a metric.
- **Why it exists / what problem it solves**: Hand-picking examples is slow and biased. Bootstrapping lets the training data and success metric decide which examples are good enough to teach the student program.
- **Keywords**: bootstrapping, demonstrations, teacher program, student program, metric, traces
- **Related concepts**: [[metric-driven-llm-optimization]], [[dspy-module-composition]], [[react-agentic-loop]], [[llm-as-judge-evaluation]]
- **Depth**: 2/4
- **Last updated**: 2026-05-04
- **Source**: sources/repos/stanfordnlp-dspy

## Summary

Few-shot examples are like worked examples in a textbook: they show the model what a good answer looks like. The hard part is choosing those examples. DSPy bootstrapping does this by running a teacher program on training examples, checking the result with a metric, and saving successful traces as demonstrations.

Those demonstrations can then be attached to the student program. Instead of trusting a developer's intuition about which examples look representative, the system uses measured success to build the few-shot set.

## Example

A question-answering program has 500 training questions. Bootstrapping runs the teacher program on them and scores each answer with an exact-match or judge metric. If 120 traces pass the threshold, the optimizer can sample from those traces to build demonstration sets for the student program.

```python
optimizer = dspy.BootstrapFewShot(metric=answer_is_correct)
compiled_program = optimizer.compile(program, trainset=train_examples)
```

## Relationship to existing concepts

- [[metric-driven-llm-optimization]]: Bootstrapping is one way DSPy searches for better program behavior.
- [[dspy-module-composition]]: In a composed program, bootstrapped traces can be assigned to the predictors that produced each step.
- [[react-agentic-loop]]: ReAct demonstrations can include full tool-use trajectories, not just final answers.
- [[llm-as-judge-evaluation]]: A judge-style metric can decide which generated traces are good enough to become demonstrations.

## Open questions

- What metric threshold keeps enough examples without letting weak demonstrations into the compiled program?
- When should bootstrapped examples be refreshed as the dataset or model changes?
