---
id: sparse-validation-evaluation
title: Sparse Validation Evaluation
depth: 2
last_reviewed: 2026-05-04
review_due: 2026-05-07
sources:
  - sources/repos/gepa-ai-gepa
related:
  - metric-driven-llm-optimization
  - pareto-efficient-candidate-selection
  - caching-strategies
  - llm-as-judge-evaluation
tags:
  - llm-engineering
  - evaluation
  - optimization
---

# Sparse Validation Evaluation

- **One-sentence definition**: Sparse validation evaluation scores each candidate on selected validation examples while tracking which examples were actually evaluated.
- **Why it exists / what problem it solves**: Full validation can be too expensive when every example requires LLM calls or tool execution. Sparse validation gives the optimizer useful comparison data without paying for a full validation pass on every candidate.
- **Keywords**: sparse scores, validation, batch, evaluation policy, coverage, budget
- **Related concepts**: [[metric-driven-llm-optimization]], [[pareto-efficient-candidate-selection]], [[caching-strategies]], [[llm-as-judge-evaluation]]
- **Depth**: 2/4
- **Last updated**: 2026-05-04
- **Source**: sources/repos/gepa-ai-gepa

## Summary

Imagine grading every student answer against every possible test case after each tiny edit. It would be accurate, but expensive. Sparse validation checks a smaller set and keeps careful notes about what was checked.

GEPA's state stores per-candidate scores by validation example. Evaluation policies decide which examples to evaluate next; for example, round-robin sampling can prioritize examples that have been tested least often. This helps the optimizer balance budget and coverage.

## Example

A validation set has 1,000 examples, but each evaluation costs money. Instead of scoring a new prompt on all 1,000 examples, the policy selects 20 under-tested examples. The state records:

```text
candidate_7:
  example_004: 0.0
  example_112: 1.0
  example_391: 0.5
```

Later policies can choose examples that have less coverage and avoid repeatedly measuring the same slice.

## Relationship to existing concepts

- [[metric-driven-llm-optimization]]: Sparse validation is one way to get metric signal under a limited budget.
- [[pareto-efficient-candidate-selection]]: Frontier tracking can use per-example sparse scores.
- [[caching-strategies]]: Evaluation caching prevents repeated candidate-example checks from consuming budget again.
- [[llm-as-judge-evaluation]]: Judge-based metrics can be expensive, making sparse validation especially useful.

## Open questions

- How much sparse coverage is enough before choosing a best candidate?
- When should the optimizer force a full validation pass despite the cost?
