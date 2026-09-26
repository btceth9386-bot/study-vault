---
id: approval-fatigue-resistant-agent-oversight
title: Approval-Fatigue-Resistant Agent Oversight
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/day-5-v3
related:
  - context-aware-high-stakes-agent-approval
tags:
  - agentic-engineering
  - coding-agents
  - human-in-the-loop
---

# Approval-Fatigue-Resistant Agent Oversight

- **One-sentence definition**: Design agent oversight so people see fewer low-value approval requests and reserve attention for consequential decisions.
- **Why it exists / what problem it solves**: A nonstop stream of tiny confirmations trains reviewers to click “approve” without checking, turning nominal human control into burnout and rubber-stamping.
- **Keywords**: approval fatigue, human oversight, risk checkpoint, quiet hours, agent insight session
- **Related concepts**: [[context-aware-high-stakes-agent-approval]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: Spec-Driven Production Grade Development in the Age of Vibe Coding

## Summary

Human review is limited attention, not an unlimited safety mechanism. Let routine, low-risk work pass through established boundaries, and interrupt people when an action has meaningful impact or falls outside those boundaries. Protect that attention with practices such as quiet hours and regular sessions that turn recurring agent findings into shared knowledge. This is about the health of the whole approval stream; it complements, rather than replaces, a clear explanation for one risky action.

## Example

An agent may automatically apply formatting fixes and run tests, but it must ask before changing production permissions or sending customer email. The team suppresses non-urgent approval alerts after hours and reviews the week's recurring findings together on Friday, instead of generating dozens of one-click prompts each day.

## Relationship to existing concepts

- [[context-aware-high-stakes-agent-approval]]: That concept makes one important approval understandable; this one decides which actions deserve human attention and how to keep that attention sustainable.

## My questions

- Which signals show that an approval queue is causing people to rubber-stamp?
- How should a team revisit its definition of low-risk work after an incident?
