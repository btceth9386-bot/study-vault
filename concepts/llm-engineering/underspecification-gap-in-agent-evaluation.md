---
id: underspecification-gap-in-agent-evaluation
title: Underspecification Gap in Agent Evaluation
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/vibe-coding-agent-security-and-evaluation-day-4
related:
  - vibe-coding-to-agentic-engineering-spectrum
  - llm-as-judge-evaluation
tags:
  - coding-agents
  - evaluation
  - requirements
  - intent
---

# Underspecification Gap in Agent Evaluation

- **One-sentence definition**: The underspecification gap is the distance between a user's incomplete natural-language request and the unstated requirements an agent must infer to deliver an acceptable result.
- **Why it exists / what problem it solves**: Coding prompts often omit operational, aesthetic, and project-specific expectations, so functional correctness alone cannot prove that the intended result was delivered.
- **Keywords**: requirements, intent, acceptance criteria, natural language, LLM judge
- **Related concepts**: [[vibe-coding-to-agentic-engineering-spectrum]], [[llm-as-judge-evaluation]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: Vibe Coding Agent Security and Evaluation

## Summary

Traditional tests assume someone wrote down the target. With vibe coding, “make the dashboard better” leaves much of that target unsaid: the project style, accessibility, loading behavior, and what “better” means. Evaluation must therefore check whether the agent reconstructed a reasonable hidden specification, often by deriving an intent rubric from the session and applying human or model judgment where deterministic tests cannot.

## Example

A user says, “Add a clean filter panel.” The generated panel works, but it hides keyboard focus, ignores the application's existing spacing, and resets selected filters on refresh. A functional test passes, yet an intent rubric reveals that the agent did not bridge the underspecification gap.

## Relationship to existing concepts

- [[vibe-coding-to-agentic-engineering-spectrum]]: Explains when informal intent needs stronger structure and verification.
- [[llm-as-judge-evaluation]]: Can score inferred acceptance criteria that exact tests cannot express.

## My questions

- Which unstated requirements should an agent ask about instead of inferring?
- How can a team calibrate an intent rubric against real user acceptance?
