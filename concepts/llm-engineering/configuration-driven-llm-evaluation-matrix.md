---
id: configuration-driven-llm-evaluation-matrix
title: Configuration-Driven LLM Evaluation Matrix
depth: 2
lab_status: not-started
last_reviewed: 2026-09-19
review_due: 2026-09-22
sources:
  - sources/repos/promptfoo-promptfoo
related:
  - skill-description-as-routing-interface
  - agent-skill-evaluation-coverage
  - prompt-version-management
  - metric-driven-llm-optimization
  - llm-as-judge-evaluation
  - sparse-validation-evaluation
  - agentic-software-factory-model
  - multidimensional-coding-agent-evaluation
tags:
  - llm-engineering
  - evaluation
  - testing
---

# Configuration-Driven LLM Evaluation Matrix

- **One-sentence definition**: A configuration-driven LLM evaluation matrix runs every selected prompt, provider, and test case as its own scored comparison cell.
- **Why it exists / what problem it solves**: Informal prompt tests are hard to repeat or compare. A declarative matrix makes shared tests repeatable and retains the evidence behind each result.
- **Keywords**: configuration, matrix, regression test, provider comparison, cost, latency
- **Related concepts**: [[skill-description-as-routing-interface]], [[agent-skill-evaluation-coverage]], [[prompt-version-management]], [[metric-driven-llm-optimization]], [[llm-as-judge-evaluation]], [[sparse-validation-evaluation]], [[agentic-software-factory-model]]
- **Depth**: 2/4
- **Last updated**: 2026-09-19
- **Source**: promptfoo/promptfoo

## Summary

Instead of clicking through a few prompts by hand, write down the prompts, providers, and tests in configuration. The evaluator expands those lists into a grid: every prompt-provider-test combination gets run and scored separately.

Each cell can render its variables, call a provider, transform the output, run assertions, and retain result details such as cost, latency, and token use. This turns a model or prompt change into regression evidence that another person can reproduce.

## Example

A team has two versions of a refund-answer prompt, two models, and ten support questions. The evaluation matrix produces 40 cells. It can show that version 2 improves correctness on one model but costs more and becomes slower on the other.

## Relationship to existing concepts

- [[skill-description-as-routing-interface]]: The matrix tests positive and negative cases for a skill's routing contract.
- [[agent-skill-evaluation-coverage]]: A matrix captures repeatable trigger, execution, regression, and cost cases.
- [[prompt-version-management]]: The matrix compares prompt versions under the same test conditions.
- [[metric-driven-llm-optimization]]: Cell scores provide measurements that can guide an optimization loop.
- [[llm-as-judge-evaluation]]: A judge rubric can grade cells whose quality is not captured by an exact rule.
- [[sparse-validation-evaluation]]: A large matrix can evaluate a selected subset when full coverage is too costly.
- [[agentic-software-factory-model]]: The matrix supplies repeatable evidence for a factory's quality gates.
- [[multidimensional-coding-agent-evaluation]]: A matrix organizes the complementary checks needed across evaluation dimensions.

## My questions

- Which dimensions should remain fixed when comparing a prompt change?
- How should a team set a budget before expanding a large evaluation matrix?
