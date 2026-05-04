---
id: optimize-anything-pattern
title: Optimize Anything Pattern
depth: 2
last_reviewed: 2026-05-04
review_due: 2026-05-07
sources:
  - sources/repos/gepa-ai-gepa
related:
  - adapter-based-llm-optimization
  - actionable-side-information
  - metric-driven-llm-optimization
  - prompt-version-management
tags:
  - llm-engineering
  - optimization
  - prompts
---

# Optimize Anything Pattern

- **One-sentence definition**: The optimize-anything pattern improves any text artifact by wrapping it in an evaluator that returns a score and useful feedback.
- **Why it exists / what problem it solves**: Not every valuable instruction lives in a normal prompt framework. Some targets are rubrics, config strings, tool descriptions, policies, or code-like artifacts. If the artifact can be scored, GEPA can treat it as a candidate and optimize it.
- **Keywords**: optimize_anything, evaluator, text artifact, ASI, wrapper, candidate
- **Related concepts**: [[adapter-based-llm-optimization]], [[actionable-side-information]], [[metric-driven-llm-optimization]], [[prompt-version-management]]
- **Depth**: 2/4
- **Last updated**: 2026-05-04
- **Source**: sources/repos/gepa-ai-gepa

## Summary

The optimize-anything pattern starts with a simple question: can we write a function that tries this text and gives it a score? If yes, the text can enter an optimization loop.

GEPA's `optimize_anything()` wraps user evaluators, captures side information through `oa.log()`, stdout, stderr, and returned metadata, then turns that feedback into reflection examples. This gives teams a fast path before writing a full custom adapter.

## Example

A team wants to improve a customer-support escalation policy:

```python
def evaluator(policy_text, example):
    decision = run_policy(policy_text, example.ticket)
    if decision != example.expected_decision:
        oa.log(f"Wrong escalation reason: expected {example.expected_decision}, got {decision}")
    return float(decision == example.expected_decision)
```

The policy text is not a normal prompt module, but it is still a scored text artifact. `optimize_anything()` can propose improved policy wording from the failure logs.

## Relationship to existing concepts

- [[adapter-based-llm-optimization]]: `optimize_anything()` is a general adapter-like entry point for custom text targets.
- [[actionable-side-information]]: The evaluator's logs and metadata become side information for reflection.
- [[metric-driven-llm-optimization]]: The evaluator score defines what "better" means.
- [[prompt-version-management]]: Optimized text artifacts still need safe versioning before production use.

## Open questions

- What kinds of text artifacts are too unconstrained for this pattern to optimize reliably?
- How should teams validate an optimized artifact before deploying it?
