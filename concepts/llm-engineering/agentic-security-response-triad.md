---
id: agentic-security-response-triad
title: Agentic Security Response Triad
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/vibe-coding-agent-security-and-evaluation-day-4
related:
  - composable-llm-red-team-testing
  - llm-observability
tags:
  - agentic-engineering
  - coding-agents
  - security
  - incident-response
---

# Agentic Security Response Triad

- **One-sentence definition**: An agentic security response triad uses Red agents to probe for weaknesses, Blue agents to spot unusual behavior, and Green agents to safely contain and repair a compromised workflow.
- **Why it exists / what problem it solves**: Agents can generate and run changing code faster than a manual security team can inspect it, so testing, detection, and recovery need to keep up with the same speed.
- **Keywords**: red team, behavioral analytics, quarantine, auto-refactoring, incident response
- **Related concepts**: [[composable-llm-red-team-testing]], [[llm-observability]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: Vibe Coding Agent Security and Evaluation

## Summary

Think of this as a fire service for autonomous software. The Red role tries to start a controlled fire by sending adversarial prompts or inputs. The Blue role watches the agent's normal execution path and raises an alarm when behavior stops matching it. The Green role freezes the agent's ability to change the outside world while preserving its short-term state for investigation, then repairs the unsafe workflow.

## Example

A Red agent tries to make a release agent use an unapproved deployment tool. Blue notices the new tool call is outside the normal release path. Green revokes that agent's deployment token, saves its trace and working memory for review, and proposes a patch that permits only the approved tool.

## Relationship to existing concepts

- [[composable-llm-red-team-testing]]: Supplies reusable probes for the Red role.
- [[llm-observability]]: Supplies the traces and baselines the Blue role needs.

## My questions

- Which deviations should trigger an immediate quarantine rather than a request for human review?
- How can an automated repair be tested before Green restores an agent's authority?
