---
id: vibe-coding-to-agentic-engineering-spectrum
title: Vibe Coding to Agentic Engineering Spectrum
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/google-day-1-v3
related:
  - agentic-software-factory-model
  - underspecification-gap-in-agent-evaluation
tags:
  - agentic-engineering
  - coding-agents
  - verification
---

# Vibe Coding to Agentic Engineering Spectrum

- **One-sentence definition**: This spectrum classifies AI-assisted development by the specification, verification, constraints, and human judgment around generated code.
- **Why it exists / what problem it solves**: Disposable experiments and production systems have different failure consequences, so they need different levels of discipline.
- **Keywords**: vibe coding, agentic engineering, verification, risk, specifications
- **Related concepts**: [[agentic-software-factory-model]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: The New SDLC with Vibe Coding: From Ad-hoc Prompting to Agentic Engineering

## Summary

The important question is not whether a team uses AI. It is how much structure surrounds the output. Informal prompting can suit low-stakes exploration; higher-stakes software needs explicit intent, repeatable verification, and accountable human review.

## Example

Using a chatbot to sketch a personal webpage is near the vibe end. Generating a payment-service change from a formal contract with tests, access controls, and review is near the agentic end.

## Relationship to existing concepts

- [[agentic-software-factory-model]]: The factory model describes the structured system used at the agentic end.
- [[underspecification-gap-in-agent-evaluation]]: Incomplete natural-language intent is a reason to add specification and verification rigor.

## My questions

- What consequence of failure warrants moving toward the agentic end?
