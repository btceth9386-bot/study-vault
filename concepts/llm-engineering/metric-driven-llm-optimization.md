---
id: metric-driven-llm-optimization
title: Metric-Driven LLM Optimization
depth: 2
last_reviewed: 2026-05-04
review_due: 2026-05-07
sources:
  - sources/repos/stanfordnlp-dspy
related:
  - dspy-signatures
  - dspy-module-composition
  - few-shot-bootstrapping
  - react-agentic-loop
  - llm-as-judge-evaluation
  - prompt-version-management
tags:
  - llm-engineering
  - dspy
  - optimization
  - evaluation
---

# Metric-Driven LLM Optimization

- **One-sentence definition**: Metric-driven LLM optimization improves an LLM program by defining what success means, then letting an optimizer search for better instructions and examples.
- **Why it exists / what problem it solves**: Manual prompt editing is guesswork. A metric turns "better" into something testable, so the system can compare candidates and compile a stronger program.
- **Keywords**: metric, optimizer, compile, MIPROv2, SIMBA, demonstrations, instructions
- **Related concepts**: [[dspy-signatures]], [[dspy-module-composition]], [[few-shot-bootstrapping]], [[react-agentic-loop]], [[llm-as-judge-evaluation]], [[prompt-version-management]]
- **Depth**: 2/4
- **Last updated**: 2026-05-04
- **Source**: sources/repos/stanfordnlp-dspy

## Summary

Metric-driven optimization treats an LLM program more like a trainable system than a fixed prompt. You write the program, provide examples, and define a scoring function. DSPy optimizers then try different instructions, demonstrations, or rules and keep the version that scores best.

Different optimizers search in different ways. `BootstrapFewShot` searches for useful examples. `MIPROv2` searches over instructions and demonstration choices. `SIMBA` uses trace comparisons to create improvement rules. The common idea is simple: stop changing words by hand and let measured performance guide the next version.

## Example

```python
def metric(example, prediction, trace=None):
    return float(example.answer.lower() == prediction.answer.lower())

optimizer = dspy.MIPROv2(metric=metric)
compiled = optimizer.compile(program, trainset=trainset, valset=valset)
compiled.save("compiled_program.json")
```

The metric defines the target. The optimizer searches for a better compiled program, and the saved artifact records the optimized behavior.

## Relationship to existing concepts

- [[dspy-signatures]]: Signatures define the fields and instructions that optimizers can work with.
- [[dspy-module-composition]]: Composed modules give the optimizer a program tree to tune.
- [[few-shot-bootstrapping]]: Bootstrapping supplies metric-approved demonstrations.
- [[react-agentic-loop]]: Tool-use trajectories can be scored and optimized, not only final text responses.
- [[llm-as-judge-evaluation]]: A judge can be used as the scoring function when exact answers are not enough.
- [[prompt-version-management]]: Both help control LLM behavior changes, but optimization happens during development while prompt versioning controls deployment.

## Open questions

- How should a metric balance correctness, latency, cost, and safety?
- How much validation data is enough before trusting a compiled program?
