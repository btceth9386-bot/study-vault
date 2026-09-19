---
id: iterative-adversarial-testing-loop
title: Iterative Adversarial Testing Loop
depth: 2
lab_status: not-started
last_reviewed: 2026-09-19
review_due: 2026-09-22
sources:
  - sources/repos/promptfoo-promptfoo
related:
  - react-agentic-loop
tags:
  - llm-engineering
  - agents
  - red-teaming
  - testing
---

# Iterative Adversarial Testing Loop

- **One-sentence definition**: An iterative adversarial testing loop lets an attacker propose an input, observes the target response, and uses a judge score to adapt the next attack.
- **Why it exists / what problem it solves**: Static probes miss failures that need conversation setup, a response to a refusal, alternative branches, or a retry from an earlier point.
- **Keywords**: attacker, target, judge, multi-turn, backtracking, attack budget
- **Related concepts**: [[react-agentic-loop]]
- **Depth**: 2/4
- **Last updated**: 2026-09-19
- **Source**: promptfoo/promptfoo

## Summary

Some vulnerabilities only appear after a conversation develops. In this loop, an attacker makes an attempt, the target responds, and a judge scores whether the attempt made progress. The next attacker message can use that feedback instead of starting over blindly.

The loop needs firm stopping rules: a success score, a maximum number of turns, a depth limit for branches, or an overall attempt budget. Backtracking lets the attacker abandon a refusal path and retry from an earlier part of the conversation.

## Example

An attacker asks an assistant for a restricted internal policy and receives a refusal. The judge gives the attempt a low score. The attacker then changes the framing, or returns to an earlier turn and tries a different route. Testing stops when the score reaches the configured success threshold or the ten-turn budget is exhausted.

## Relationship to existing concepts

- [[react-agentic-loop]]: This is a specialized loop where observations are target responses and judge scores, actions are revised attacks, and budgets terminate the run.

## My questions

- How can a judge distinguish a genuine security failure from a harmless but persuasive-looking response?
- Which attack budgets produce useful exploration without causing runaway test cost?
