---
id: system-aware-candidate-merge
title: System-Aware Candidate Merge
depth: 2
last_reviewed: 2026-05-04
review_due: 2026-05-07
sources:
  - sources/repos/gepa-ai-gepa
related:
  - pareto-efficient-candidate-selection
  - reflective-mutation-proposer
  - metric-driven-llm-optimization
tags:
  - llm-engineering
  - optimization
  - architecture
---

# System-Aware Candidate Merge

- **One-sentence definition**: System-aware candidate merge combines useful text components from related candidate variants so improvements discovered separately can be tested together.
- **Why it exists / what problem it solves**: One mutation may improve retrieval instructions while another improves answer formatting. If those changes came from related candidates, merging can produce a stronger candidate than either parent alone.
- **Keywords**: merge, candidate, lineage, common ancestor, crossover, Pareto frontier
- **Related concepts**: [[pareto-efficient-candidate-selection]], [[reflective-mutation-proposer]], [[metric-driven-llm-optimization]]
- **Depth**: 2/4
- **Last updated**: 2026-05-04
- **Source**: sources/repos/gepa-ai-gepa

## Summary

System-aware merge is like combining two edited drafts of the same document. If one editor improved the introduction and another improved the examples, you may want a version that uses both edits. GEPA does this with candidates made of named text components.

The merge proposer looks for successful candidates with a common ancestor, chooses component values from the descendants, and evaluates the merged candidate on a small sample. This avoids assuming that every combination is good; the merged version still has to prove itself.

## Example

A RAG system has two components:

```text
query_rewriter
answer_generator
```

Candidate A improves `query_rewriter` and retrieves better documents. Candidate B improves `answer_generator` and writes clearer answers. A merge candidate may take A's `query_rewriter` and B's `answer_generator`, then test whether the combined system is better.

## Relationship to existing concepts

- [[pareto-efficient-candidate-selection]]: Pareto frontiers reveal candidates that are strong in different places.
- [[reflective-mutation-proposer]]: Reflective mutation creates the improved descendants that merge can later recombine.
- [[metric-driven-llm-optimization]]: The merged candidate is still accepted or rejected by measured performance.

## Open questions

- When do two prompt improvements interfere with each other instead of combining cleanly?
- How should merge choose between two changed versions of the same component?
