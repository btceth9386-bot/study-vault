---
id: llm-as-judge-evaluation
title: LLM-as-Judge Evaluation
depth: 2
last_reviewed: 2026-05-04
review_due: 2026-05-07
sources:
  - sources/repos/langfuse-langfuse
related:
  - llm-observability
  - prompt-version-management
  - async-processing
  - few-shot-bootstrapping
  - metric-driven-llm-optimization
tags:
  - llm-engineering
  - evaluation
  - quality
---

# LLM-as-Judge Evaluation

- **One-sentence definition**: LLM-as-judge evaluation uses one LLM to score another LLM application's output against a rubric.
- **Why it exists / what problem it solves**: Human review is slow and expensive, but LLM products need continuous quality checks. A judge model can apply a reusable rubric to many traces, observations, or dataset items so teams can catch regressions and compare changes at scale.
- **Keywords**: evaluator, rubric, scores, job configuration, eval template, trace quality
- **Related concepts**: [[llm-observability]], [[prompt-version-management]], [[async-processing]], [[few-shot-bootstrapping]], [[metric-driven-llm-optimization]]
- **Depth**: 2/4
- **Last updated**: 2026-05-04
- **Source**: sources/repos/langfuse-langfuse

## Summary

Imagine a teacher grading essays with a rubric. LLM-as-judge does something similar for AI outputs: it sends the original input, output, and context to a separate model, asks it to apply a scoring template, and stores the result as a score. The judge is not perfect, but it is fast enough to run on many examples and consistent enough to reveal trends.

In Langfuse, this is modeled as a pipeline. A `JobConfiguration` decides what should be evaluated and when. An `EvalTemplate` defines the prompt and expected output format. Background queues execute the jobs, call the configured LLM provider, validate the result, and write scores back to the observability data.

## Example

A team wants to monitor whether its chatbot answers are helpful. They create an evaluator with this rubric:

- Score 1 if the answer ignores the question.
- Score 3 if the answer is partially useful.
- Score 5 if the answer directly solves the user's problem.

Every new support trace enters an evaluation queue. The judge model reads the user question and chatbot answer, returns a structured score and reasoning, and Langfuse stores that score. If the average helpfulness drops after a prompt change, the team can roll back or investigate.

## Relationship to existing concepts

- [[llm-observability]]: The evaluator reads trace, observation, and dataset data as its inputs.
- [[prompt-version-management]]: The judge prompt itself should be versioned, because changing the rubric changes the meaning of future scores.
- [[async-processing]]: Evaluation runs in background queues so user-facing requests do not wait for judge model calls.
- [[few-shot-bootstrapping]]: Judge metrics can filter which generated traces become demonstrations.
- [[metric-driven-llm-optimization]]: A judge can serve as the metric that guides compile-time optimization.

## Open questions

- When should an LLM judge be calibrated against human reviewers?
- Which evaluation criteria are safe to automate, and which require human annotation?
