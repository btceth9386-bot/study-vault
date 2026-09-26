---
id: session-convergence-evaluation
title: Session Convergence Evaluation
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/vibe-coding-agent-security-and-evaluation-day-4
related:
  - trace-aware-agent-evaluation
  - llm-observability
  - continuous-online-agent-evaluation
tags:
  - coding-agents
  - evaluation
  - observability
  - user-feedback
---

# Session Convergence Evaluation

- **One-sentence definition**: Session convergence evaluation measures whether a multi-turn agent interaction reaches a user-accepted result, how many corrections it needs, its cost, and whether the user abandons it.
- **Why it exists / what problem it solves**: Turn-level accuracy can call one reply correct even when cumulative code changes never solve the user's actual task.
- **Keywords**: convergence, multi-turn, abandonment, corrections, cost
- **Related concepts**: [[trace-aware-agent-evaluation]], [[llm-observability]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: Vibe Coding Agent Security and Evaluation

## Summary

The useful question is not “was turn four correct?” but “did the conversation end with something the user wanted?” Session convergence treats the whole interaction as the unit of success. It tracks the accepted result, turns and corrections needed to get there, money or tokens spent, and whether the user walked away; corrections also become labeled examples of what failed.

## Example

Two agents both produce a valid component on their first turn. One reaches the user's desired page after one clarification and $0.10 of work; the other needs six corrections, changes unrelated files, and is abandoned. Session convergence marks the first experience as successful and turns the latter's corrections into evaluation data.

## Relationship to existing concepts

- [[trace-aware-agent-evaluation]]: Provides the full-session execution record.
- [[llm-observability]]: Supplies the cost and latency measurements.
- [[continuous-online-agent-evaluation]]: Another evaluation modality distinguished by being continuous rather than session-scoped; both treat the whole interaction, not a single turn, as the unit worth measuring.

## My questions

- How should a team identify a user-accepted result without adding intrusive prompts?
- When do many short correction turns signal healthy collaboration rather than failure?
