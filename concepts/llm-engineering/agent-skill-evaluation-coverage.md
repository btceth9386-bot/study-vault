---
id: agent-skill-evaluation-coverage
title: Agent Skill Evaluation Coverage
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/agent-skills-day-3
related:
  - evaluation-gated-meta-skills
  - trace-aware-agent-evaluation
  - hybrid-llm-output-assertions
  - configuration-driven-llm-evaluation-matrix
tags:
  - agent-skills
  - llm-engineering
  - evaluation
  - context-engineering
---

# Agent Skill Evaluation Coverage

- **One-sentence definition**: Agent skill evaluation coverage is proof that a skill activates when appropriate, performs safely, stays compatible with the rest of the library, and fits its context budget.
- **Why it exists / what problem it solves**: A passing happy-path answer can hide a skill that never triggers, takes an unsafe route, breaks another skill, or consumes too much shared context.
- **Keywords**: triggering, execution, regression, token budget, trajectories, evaluation
- **Related concepts**: [[evaluation-gated-meta-skills]], [[trace-aware-agent-evaluation]], [[hybrid-llm-output-assertions]], [[configuration-driven-llm-evaluation-matrix]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: Agent Skills

## Summary

Testing a skill is like testing a new employee, not just checking one finished task. It must be called for the right jobs, follow the right working steps, coexist with its teammates, and not crowd out the instructions needed for the job. These four checks cover triggering, execution, regression, and token budget. A skill is not ready merely because it gives a good answer once.

## Example

A database-migration skill produces correct SQL for a test request. Its coverage is still incomplete until tests show that it triggers for schema changes but not for ordinary bug fixes, uses the approved migration tool, still works when other skills are loaded, and remains within the context budget.

## Relationship to existing concepts

- [[evaluation-gated-meta-skills]]: Meta-generated changes need the same complete evidence before promotion.
- [[trace-aware-agent-evaluation]]: This adds routing, regression, and context-cost checks to trajectory inspection.
- [[hybrid-llm-output-assertions]]: Mixed deterministic, semantic, and trace assertions can supply the evidence.
- [[configuration-driven-llm-evaluation-matrix]]: A repeatable matrix makes the four coverage conditions comparable across cases.

## My questions

- Which co-loaded skills best represent the realistic context pressure for a library?
- What token budget should block promotion rather than trigger an optimization task?
