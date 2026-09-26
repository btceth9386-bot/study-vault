---
id: hybrid-llm-output-assertions
title: Hybrid LLM Output Assertions
depth: 2
lab_status: not-started
last_reviewed: 2026-09-19
review_due: 2026-09-22
sources:
  - sources/repos/promptfoo-promptfoo
related:
  - agent-skill-evaluation-coverage
  - llm-as-judge-evaluation
  - llm-observability
  - sparse-validation-evaluation
  - composable-llm-red-team-testing
  - agentic-coding-80-percent-problem
  - a2ui-layout-ownership-patterns
  - multidimensional-coding-agent-evaluation
  - domain-expert-calibrated-agent-validation
tags:
  - llm-engineering
  - evaluation
  - testing
---

# Hybrid LLM Output Assertions

- **One-sentence definition**: Hybrid LLM output assertions combine exact rules, model-assisted judgments, and execution-trace checks into one grade.
- **Why it exists / what problem it solves**: Generative systems have both objective constraints and subjective quality goals, so one kind of evaluator cannot reliably cover format, meaning, budgets, safety, and agent behavior.
- **Keywords**: assertions, deterministic checks, LLM judge, traces, grading, thresholds
- **Related concepts**: [[agent-skill-evaluation-coverage]], [[llm-as-judge-evaluation]], [[llm-observability]], [[sparse-validation-evaluation]], [[composable-llm-red-team-testing]], [[agentic-coding-80-percent-problem]], [[domain-expert-calibrated-agent-validation]]
- **Depth**: 2/4
- **Last updated**: 2026-09-19
- **Source**: promptfoo/promptfoo

## Summary

Checking an LLM answer is more like inspecting a product than checking a single arithmetic answer. A deterministic assertion checks facts a program can decide exactly, such as JSON shape, a required phrase, latency, or cost. A model-graded assertion asks an LLM to apply a rubric when quality depends on meaning.

Trace-aware assertions add a third view: they inspect what an agent actually did, such as which tool it called and in what order. Combining the evidence produces one grading result while keeping each check suited to the question it can answer well.

## Example

For an agent that files expense reports, require valid JSON and a cost below a limit with deterministic checks. Use a judge rubric to assess whether the explanation is clear. Then verify from the trace that the agent queried the approved expense-policy tool before submitting a claim.

## Relationship to existing concepts

- [[agent-skill-evaluation-coverage]]: Hybrid assertions provide evidence for several coverage conditions.
- [[llm-as-judge-evaluation]]: Judge rubrics provide the model-assisted branch for subjective quality.
- [[llm-observability]]: Trace checks need recorded tool calls, spans, and operational measurements.
- [[sparse-validation-evaluation]]: Selective evaluation can limit the cost of model-graded assertions.
- [[composable-llm-red-team-testing]]: Security probes flow through the same grading model.
- [[agentic-coding-80-percent-problem]]: Hybrid evidence helps test the subtle correctness gaps that plausible generated code can conceal.
- [[a2ui-layout-ownership-patterns]]: Schema and deterministic assertions are especially useful before an LLM-owned UI layout reaches a renderer.
- [[multidimensional-coding-agent-evaluation]]: Hybrid assertions provide complementary evidence for different quality dimensions.
- [[domain-expert-calibrated-agent-validation]]: Qualified expert judgments set the domain-specific ground truth that the combined checks must keep matching.

## My questions

- Which checks should be hard gates, and which should contribute to a weighted score?
- How often should a model-graded assertion be calibrated against human reviewers?
