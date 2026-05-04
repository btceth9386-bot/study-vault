---
id: actionable-side-information
title: Actionable Side Information
depth: 2
last_reviewed: 2026-05-04
review_due: 2026-05-07
sources:
  - sources/repos/gepa-ai-gepa
related:
  - metric-driven-llm-optimization
  - llm-observability
  - llm-as-judge-evaluation
  - reflective-mutation-proposer
  - optimize-anything-pattern
tags:
  - llm-engineering
  - optimization
  - evaluation
---

# Actionable Side Information

- **One-sentence definition**: Actionable Side Information is the extra diagnostic context from an evaluation run that helps an optimizer understand why an LLM system failed, not just that it failed.
- **Why it exists / what problem it solves**: A score like `0.4` says a candidate was weak, but it does not say whether the problem was bad formatting, the wrong tool, missing evidence, slow code, or a misunderstood instruction. Side information gives the reflection model useful clues for the next change.
- **Keywords**: ASI, traces, logs, errors, feedback, reflection, diagnostics
- **Related concepts**: [[metric-driven-llm-optimization]], [[llm-observability]], [[llm-as-judge-evaluation]], [[reflective-mutation-proposer]], [[optimize-anything-pattern]]
- **Depth**: 2/4
- **Last updated**: 2026-05-04
- **Source**: sources/repos/gepa-ai-gepa

## Summary

Imagine asking a teacher why your answer was wrong. A number grade helps, but a note like "you used the wrong formula in step two" is much more useful. Actionable Side Information plays that role for LLM optimization.

In GEPA, the evaluator can return logs, errors, traces, intermediate reasoning, tool-call details, or judge feedback. The reflection model reads that context and proposes a more targeted change to the candidate text. This makes optimization less like random prompt tweaking and more like debugging with evidence.

## Example

A tool-using agent receives this score and feedback:

```text
score: 0.0
log: The agent called search_users with {"name": "refund policy"}.
error: search_users expects a person name, but the query was a policy lookup.
```

A reflection model can use that side information to rewrite the tool instruction: "Use `search_docs` for policy questions; use `search_users` only for people." A score alone would not reveal the tool-selection mistake.

## Relationship to existing concepts

- [[metric-driven-llm-optimization]]: ASI adds explanation to the metric signal so the optimizer knows what to change.
- [[llm-observability]]: Observability records traces; ASI selects the parts of those traces that are useful for improvement.
- [[llm-as-judge-evaluation]]: Judge feedback can become side information for the next optimization step.
- [[reflective-mutation-proposer]]: Reflective mutation depends on side information to propose targeted text changes.
- [[optimize-anything-pattern]]: `optimize_anything()` captures `oa.log()`, stdout, stderr, and returned side information as ASI.

## Open questions

- What is the smallest amount of side information that still helps reflection?
- How should sensitive trace data be redacted before being sent to a reflection model?
