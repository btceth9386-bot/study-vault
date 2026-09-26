---
id: layered-agent-memory
title: Layered Agent Memory
depth: 2
lab_status: not-started
last_reviewed: 2026-09-26
review_due: 2026-09-29
sources:
  - sources/papers/comprehensive-agent-engineering-guide-2026
related:
  - langgraph-store-long-term-memory
  - persistent-agent-session-restoration
  - self-improving-agent-skill-memory-loop
tags:
  - llm-engineering
  - agents
  - memory
---

# Layered Agent Memory

- **One-sentence definition**: Layered agent memory separates working context, session state, long-term knowledge, episodic experience, and discrete observations by lifetime, structure, and retrieval purpose.
- **Why it exists / what problem it solves**: Treating every memory as chat history overloads active context and loses useful long-lived knowledge. Layers keep immediate work small while preserving reusable information elsewhere.
- **Keywords**: working memory, session memory, long-term memory, episodic memory, observations
- **Related concepts**: [[langgraph-store-long-term-memory]], [[persistent-agent-session-restoration]], [[self-improving-agent-skill-memory-loop]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: The Comprehensive Guide to AI Agent Engineering

## Summary

Agent memory is more useful when it behaves like a workspace, a notebook, a library, and a lessons-learned log rather than one giant transcript. Working memory holds the current request; session memory carries one conversation; long-term memory holds reusable facts across conversations; episodic memory records what worked or failed; and observational memory stores small extracted facts. Each layer answers a different retrieval question and has a different cost. Separating them prevents short-term noise from crowding out durable knowledge.

## Example

A support agent keeps the current customer case in working memory, a compact case summary in session state, verified account preferences in long-term storage, a record that a prior escalation path failed in episodic memory, and individual invoice facts as observations. A new case retrieves only the preferences and relevant observations, not every old conversation.

## Relationship to existing concepts

- [[langgraph-store-long-term-memory]]: A persistent store implements the layer for knowledge reused across conversations.
- [[persistent-agent-session-restoration]]: Session restoration preserves one conversation's continuity across process restarts.
- [[self-improving-agent-skill-memory-loop]]: Episodic lessons can become reusable skills after evaluation and consolidation.

## My questions

- Which memory layer should own a fact that is useful now but may change tomorrow?
- How should privacy and retention policies differ across memory layers?
