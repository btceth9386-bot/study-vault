---
id: pareto-efficient-candidate-selection
title: Pareto-Efficient Candidate Selection
depth: 2
last_reviewed: 2026-05-04
review_due: 2026-05-07
sources:
  - sources/repos/gepa-ai-gepa
related:
  - metric-driven-llm-optimization
  - reflective-mutation-proposer
  - system-aware-candidate-merge
  - sparse-validation-evaluation
tags:
  - llm-engineering
  - optimization
  - evaluation
---

# Pareto-Efficient Candidate Selection

- **One-sentence definition**: Pareto-efficient candidate selection keeps candidates that are best on different examples or objectives, instead of keeping only the candidate with the best average score.
- **Why it exists / what problem it solves**: LLM systems often fail unevenly. One prompt may be best at tool use, another at formatting, and another at hard reasoning. Pareto selection preserves these specialists so future mutations and merges can reuse their strengths.
- **Keywords**: Pareto frontier, candidate, objective, validation example, specialist, selection
- **Related concepts**: [[metric-driven-llm-optimization]], [[reflective-mutation-proposer]], [[system-aware-candidate-merge]], [[sparse-validation-evaluation]]
- **Depth**: 2/4
- **Last updated**: 2026-05-04
- **Source**: sources/repos/gepa-ai-gepa

## Summary

Averaging can hide useful behavior. If one candidate solves every formatting case and another solves every math case, the average-best candidate may not teach you what either specialist learned. A Pareto frontier keeps candidates that are not dominated by others for the examples or objectives they handle well.

In GEPA, this gives the optimizer a richer population to work from. The system can choose a frontier candidate for reflective mutation, or later merge two candidates that improved in different places.

## Example

Suppose three candidates score this way:

| Candidate | Math cases | JSON format cases |
|---|---:|---:|
| A | 90% | 40% |
| B | 50% | 95% |
| C | 70% | 70% |

Candidate C may look balanced, but A and B each contain useful specialized behavior. Pareto selection keeps A and B because each is best on a different slice.

## Relationship to existing concepts

- [[metric-driven-llm-optimization]]: Pareto selection decides how metric results shape the search population.
- [[reflective-mutation-proposer]]: Reflective mutation often starts from a candidate on the Pareto frontier.
- [[system-aware-candidate-merge]]: Merge uses frontier candidates that may have complementary improvements.
- [[sparse-validation-evaluation]]: Sparse validation records partial scores that can still support frontier tracking.

## Open questions

- How long should a specialist candidate stay alive if it performs poorly on most other examples?
- Which frontier type is best when optimizing accuracy, cost, and latency together?
