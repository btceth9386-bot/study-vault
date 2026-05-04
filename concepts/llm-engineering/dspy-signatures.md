---
id: dspy-signatures
title: DSPy Signatures
depth: 2
last_reviewed: 2026-05-04
review_due: 2026-05-07
sources:
  - sources/repos/stanfordnlp-dspy
related:
  - dspy-module-composition
  - metric-driven-llm-optimization
  - prompt-version-management
  - llm-observability
tags:
  - llm-engineering
  - dspy
  - prompts
  - structured-output
---

# DSPy Signatures

- **One-sentence definition**: A DSPy Signature describes an LLM task as named input and output fields, plus instructions, so the program says what it needs instead of hand-writing the full prompt.
- **Why it exists / what problem it solves**: Raw prompts mix the task, formatting rules, examples, and model-specific details into one fragile string. Signatures separate the stable task definition from the adapter and optimizer that decide how to format and improve it.
- **Keywords**: signature, input field, output field, adapter, typed output, task contract
- **Related concepts**: [[dspy-module-composition]], [[metric-driven-llm-optimization]], [[prompt-version-management]], [[llm-observability]]
- **Depth**: 2/4
- **Last updated**: 2026-05-04
- **Source**: sources/repos/stanfordnlp-dspy

## Summary

Think of a Signature like a form for an LLM call. Instead of writing a paragraph that says "read this question and return an answer," you define fields such as `question -> answer`. DSPy can then turn that form into a model-specific prompt, parse the response back into Python values, and let optimizers add better instructions or examples.

This matters because the task stays stable even when the prompt wording changes. A Signature can also use typed fields, such as enums or structured objects, so the rest of the program receives data with a clearer shape than a plain string.

## Example

```python
import dspy

class AnswerQuestion(dspy.Signature):
    """Answer the user's question using the provided context."""

    context: str = dspy.InputField()
    question: str = dspy.InputField()
    answer: str = dspy.OutputField()

qa = dspy.Predict(AnswerQuestion)
```

The Signature defines the contract: the module receives `context` and `question`, then returns `answer`. DSPy decides how to format that contract for the configured model.

## Relationship to existing concepts

- [[dspy-module-composition]]: Modules wrap Signatures and combine them into larger LLM programs.
- [[metric-driven-llm-optimization]]: Optimizers use Signature fields to know what can be improved and where examples belong.
- [[prompt-version-management]]: Both treat prompt behavior as something worth managing explicitly, but Signatures keep the task contract in code.
- [[llm-observability]]: Clear input and output fields make traces easier to inspect and compare.

## Open questions

- How strict should output types be before they start making useful model responses fail validation?
- When should a team change a Signature versus only optimizing its instructions and examples?
