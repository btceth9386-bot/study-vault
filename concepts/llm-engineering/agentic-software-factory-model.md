---
id: agentic-software-factory-model
title: Agentic Software Factory Model
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/google-day-1-v3
related:
  - metric-driven-llm-optimization
  - configuration-driven-llm-evaluation-matrix
  - prompt-version-management
  - vibe-coding-to-agentic-engineering-spectrum
  - executable-specification-as-architectural-north-star
tags:
  - agentic-engineering
  - coding-agents
  - software-factory
  - quality-gates
  - feedback-loops
---

# Agentic Software Factory Model

- **One-sentence definition**: The agentic software factory model makes the developer's product a repeatable system: specifications direct agents, quality gates verify output, and feedback loops send failures back for correction.
- **Why it exists / what problem it solves**: When generating code is cheap, repeatedly directing each small implementation detail does not scale; reusable success criteria let people focus on system design and quality control.
- **Keywords**: specifications, agents, quality gates, feedback loops, guardrails, success criteria
- **Related concepts**: [[metric-driven-llm-optimization]], [[configuration-driven-llm-evaluation-matrix]], [[prompt-version-management]], [[executable-specification-as-architectural-north-star]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: The New SDLC with Vibe Coding: From Ad-hoc Prompting to Agentic Engineering

## Summary

Think of a factory manager who designs an assembly line instead of building every item by hand. In this model, a developer defines what good looks like, gives agents the necessary context, and puts checks around their work. The agents implement; tests and evaluations decide whether the result meets the standard; failures become useful feedback for the next attempt.

The model changes the human role from issuing every instruction to designing a reliable production system. It still requires human judgment for architecture and the meaning of quality.

## Example

A team defines a feature contract, supplies its agent with the relevant API and architecture notes, and requires unit tests, a security check, and a review summary. A failing integration test returns its error to the agent for one bounded correction attempt. The developer reviews the final change and improves the contract or quality gate if the same failure recurs.

## Relationship to existing concepts

- [[metric-driven-llm-optimization]]: Metrics provide the signal that lets the factory improve its instructions or agent behavior over time.
- [[configuration-driven-llm-evaluation-matrix]]: A repeatable evaluation matrix turns quality gates into comparable evidence.
- [[prompt-version-management]]: Versioned instructions make the factory's behavior reproducible and reversible.
- [[vibe-coding-to-agentic-engineering-spectrum]]: The factory model is a structured practice at the agentic end of the spectrum.
- [[executable-specification-as-architectural-north-star]]: The specification is the shared blueprint that directs the factory's agents and verifies their output.

## My questions

- Which quality gates should block a change, and which should provide feedback only?
- How should a team detect that a repeated failure is a system-design problem rather than an agent mistake?
