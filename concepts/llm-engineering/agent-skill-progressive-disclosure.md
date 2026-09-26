---
id: agent-skill-progressive-disclosure
title: Progressive Disclosure for Agent Skills
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/agent-skills-day-3
related:
  - static-vs-dynamic-agent-context
  - context-engineering-for-coding-agents
tags:
  - agent-skills
  - llm-engineering
  - context-engineering
---

# Progressive Disclosure for Agent Skills

- **One-sentence definition**: Progressive disclosure keeps skill metadata visible for routing, loads instructions after the skill is chosen, and loads bundled resources only when needed.
- **Why it exists / what problem it solves**: It gives an agent a large skill library without stuffing every procedure into every context window.
- **Keywords**: metadata, routing, lazy loading, SKILL.md, resources, context budget
- **Related concepts**: [[static-vs-dynamic-agent-context]], [[context-engineering-for-coding-agents]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: Agent Skills

## Summary

Think of a skill library as a workshop. The labels on all drawers are visible, but the agent opens only the drawer relevant to its job and takes out a tool only when that tool is needed. For skills, these are metadata, the instruction body, and bundled scripts, references, or assets. The result is a smaller active context without hiding available capabilities.

## Example

For an EPUB import, an agent can see a short description saying the book-ingestion skill exists. Only after the request mentions an EPUB does it load that skill's `SKILL.md`; it runs a conversion script only if the source is actually an EPUB file.

## Relationship to existing concepts

- [[static-vs-dynamic-agent-context]]: This applies the general on-demand loading strategy as a three-layer skill mechanism.
- [[context-engineering-for-coding-agents]]: Progressive disclosure keeps task context focused while still making specialized know-how available.

## My questions

- How detailed can always-visible metadata become before it defeats the context-saving goal?
- Which resource types should always be loaded with a skill because deferring them would be unsafe?
