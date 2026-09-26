---
id: multidimensional-coding-agent-evaluation
title: Multidimensional Coding-Agent Evaluation
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/vibe-coding-agent-security-and-evaluation-day-4
related:
  - configuration-driven-llm-evaluation-matrix
  - hybrid-llm-output-assertions
  - trace-aware-agent-evaluation
tags:
  - coding-agents
  - evaluation
  - software-quality
  - testing
---

# Multidimensional Coding-Agent Evaluation

- **One-sentence definition**: Multidimensional coding-agent evaluation measures intent satisfaction, functional and visual correctness, efficiency, convention fit, trajectory quality, and self-repair with complementary methods.
- **Why it exists / what problem it solves**: One passing test or benchmark can hide unsafe reasoning, poor usability, high cost, style violations, or brittle recovery.
- **Keywords**: intent satisfaction, functional correctness, trajectory, self-repair, evaluation portfolio
- **Related concepts**: [[configuration-driven-llm-evaluation-matrix]], [[hybrid-llm-output-assertions]], [[trace-aware-agent-evaluation]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: Vibe Coding Agent Security and Evaluation

## Summary

Evaluating a coding agent is like inspecting a house: passing the electrical test does not prove that the roof, layout, cost, and construction process were good. Different questions need different evidence, including tests, security scans, browser checks, model judges, trace inspection, and focused human review. A production evaluation combines these methods because no one score can cover the whole task.

## Example

For a generated checkout page, automated tests check payment logic, browser testing checks the rendered form, a cost limit catches wasteful retries, a style check verifies project conventions, and trace inspection confirms the agent did not call an unapproved payment tool.

## Relationship to existing concepts

- [[configuration-driven-llm-evaluation-matrix]]: Organizes repeatable dimensions and methods into comparable cases.
- [[hybrid-llm-output-assertions]]: Combines deterministic and model-based evidence.
- [[trace-aware-agent-evaluation]]: Covers the execution path and repair behavior.

## My questions

- Which dimensions should be release blockers for a high-risk change?
- How should teams balance broad evaluation coverage against cost and delay?
