---
id: static-vs-dynamic-agent-context
title: Static vs. Dynamic Agent Context
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/google-day-1-v3
related:
  - skill-description-as-routing-interface
  - agent-skill-progressive-disclosure
  - context-engineering-for-coding-agents
  - agent-instruction-placement-by-scope
tags:
  - agentic-engineering
  - coding-agents
  - verification
---

# Static vs. Dynamic Agent Context

- **One-sentence definition**: Static context is loaded every time; dynamic context is retrieved only when the task needs it.
- **Why it exists / what problem it solves**: Loading everything wastes tokens and hides useful signals, while loading too little loses critical rules.
- **Keywords**: static context, dynamic context, retrieval, skills, token cost
- **Related concepts**: [[skill-description-as-routing-interface]], [[agent-skill-progressive-disclosure]], [[context-engineering-for-coding-agents]], [[agent-instruction-placement-by-scope]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: The New SDLC with Vibe Coding: From Ad-hoc Prompting to Agentic Engineering

## Summary

Keep universal rules such as safety policies and repository conventions static. Fetch specialized procedures, documents, tool results, and recent history when the work calls for them. The aim is high-signal context at a sustainable cost.

## Example

An agent always receives the repository's security rules, but loads the database-migration skill only when a task changes a schema.

## Relationship to existing concepts

- [[skill-description-as-routing-interface]]: A description determines whether a skill's dynamic context is loaded for the task.
- [[agent-skill-progressive-disclosure]]: Skills implement dynamic loading through metadata, instructions, and on-demand resources.
- [[context-engineering-for-coding-agents]]: This is the loading strategy for the broader context design.
- [[agent-instruction-placement-by-scope]]: Placement chooses the durable home and audience for a rule; this concept chooses whether it is always loaded or fetched when needed.

## My questions

- Which rules are too important to retrieve on demand?
