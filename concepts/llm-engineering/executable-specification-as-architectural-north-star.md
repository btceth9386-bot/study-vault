---
id: executable-specification-as-architectural-north-star
title: Executable Specification as an Architectural North Star
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/day-5-v3
related:
  - agentic-software-factory-model
  - context-engineering-for-coding-agents
tags:
  - agentic-engineering
  - coding-agents
---

# Executable Specification as an Architectural North Star

- **One-sentence definition**: An executable specification is a versioned, shared blueprint that tells people and coding agents what to build and how to verify it.
- **Why it exists / what problem it solves**: Fast code generation magnifies ambiguous intent; a durable specification stops each agent session from filling missing details with new guesses.
- **Keywords**: specification, source of truth, BDD, contracts, behavioral scenarios
- **Related concepts**: [[agentic-software-factory-model]], [[context-engineering-for-coding-agents]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: Spec-Driven Production Grade Development in the Age of Vibe Coding

## Summary

Treat the specification as the map, and generated code as one route drawn from it. Keep the map in version control with the technical design, constraints, rationale, contracts, diagrams, and scenarios that show what success and failure look like. A behavioral scenario can use Given/When/Then: it states the starting condition, action, and expected result in plain language. With this shared source of truth, an agent can implement and test without relying on a stale conversation or a vague request.

## Example

Before building payment retries, a team adds `specs/payment_retry.md` with the API contract, retry limits, a sequence diagram, and this scenario: “Given a declined payment, when the provider recovers within three attempts, then charge the customer once and record the successful attempt.” The agent uses that same file to write code and failing tests.

## Relationship to existing concepts

- [[agentic-software-factory-model]]: The specification is the factory's durable input that directs implementation and quality gates.
- [[context-engineering-for-coding-agents]]: It provides structured task context instead of asking an agent to infer requirements from a short prompt.

## My questions

- Which changes require an updated behavioral scenario before implementation starts?
- How should a team keep a specification concise while retaining essential edge cases?
