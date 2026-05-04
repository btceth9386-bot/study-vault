---
id: dspy-module-composition
title: DSPy Module Composition
depth: 2
last_reviewed: 2026-05-04
review_due: 2026-05-07
sources:
  - sources/repos/stanfordnlp-dspy
related:
  - dspy-signatures
  - metric-driven-llm-optimization
  - few-shot-bootstrapping
  - react-agentic-loop
  - prompt-version-management
  - adapter-based-llm-optimization
tags:
  - llm-engineering
  - dspy
  - architecture
  - optimization
---

# DSPy Module Composition

- **One-sentence definition**: DSPy module composition builds LLM programs from reusable modules that can contain other modules, so an optimizer can tune the whole program instead of isolated prompt strings.
- **Why it exists / what problem it solves**: Real LLM applications often need several steps, such as retrieve, reason, verify, and answer. Module composition gives those steps a program structure that can be inspected, serialized, and optimized together.
- **Keywords**: module, predictor, composition, program tree, serialization, optimizer
- **Related concepts**: [[dspy-signatures]], [[metric-driven-llm-optimization]], [[few-shot-bootstrapping]], [[react-agentic-loop]], [[prompt-version-management]], [[adapter-based-llm-optimization]]
- **Depth**: 2/4
- **Last updated**: 2026-05-04
- **Source**: sources/repos/stanfordnlp-dspy

## Summary

Think of a DSPy module like a small machine in an assembly line. One module may generate a search query, another may read retrieved context, and another may write the final answer. Because each piece is a module, DSPy can walk the whole program tree, find the predictors inside it, and optimize them together.

This is different from keeping several prompt strings in separate files. The program structure is explicit in Python, and the optimized state can be saved and loaded. That makes a complex LLM workflow easier to reproduce and reason about.

## Example

```python
import dspy

class MultiStepQA(dspy.Module):
    def __init__(self):
        self.make_query = dspy.Predict("question -> search_query")
        self.answer = dspy.ChainOfThought("question, context -> answer")

    def forward(self, question):
        query = self.make_query(question=question).search_query
        context = retrieve_documents(query)
        return self.answer(question=question, context=context)
```

An optimizer can inspect this module, find both predictors, and compile a better version of the full program.

## Relationship to existing concepts

- [[dspy-signatures]]: Signatures define each module's task contract.
- [[metric-driven-llm-optimization]]: Optimization depends on being able to discover and tune predictors across the module tree.
- [[few-shot-bootstrapping]]: Bootstrapped traces can be attached to the matching predictors inside a composed program.
- [[react-agentic-loop]]: ReAct is implemented as a module that runs a repeated reasoning-and-tool-use loop.
- [[prompt-version-management]]: A saved compiled module is a versioned behavior artifact, similar in spirit to a managed prompt version.
- [[adapter-based-llm-optimization]]: An adapter can discover components inside a module tree and map them into generic candidate text.

## Open questions

- How large can a composed LLM program become before optimization cost outweighs the benefit?
- Which module boundaries make traces easiest to debug?
