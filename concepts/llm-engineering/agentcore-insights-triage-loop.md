---
id: agentcore-insights-triage-loop
title: AgentCore Insights Triage-to-Optimization Loop
depth: 2
lab_status: not-started
last_reviewed: 2026-09-26
review_due: 2026-09-29
sources:
  - sources/papers/bedrock-agentcore-observability-evals/
related:
  - continuous-online-agent-evaluation
  - trace-derived-evaluation-field-contract
  - actionable-side-information
  - reflective-mutation-proposer
  - optimize-anything-pattern
  - config-bundle-ab-testing-for-agent-behavior
tags:
  - llm-engineering
  - evaluation
  - observability
  - aws
  - agentcore
---

# AgentCore Insights Triage-to-Optimization Loop

- **One-sentence definition**: AgentCore Insights (preview) extends evaluation scoring with diagnosis: it clusters session failures into categories, subcategories, and root causes, groups user intents and execution patterns across sessions, and lets those findings be passed to the Recommendations API to generate a candidate system prompt, which can then be validated against the original through A/B testing.
- **Why it exists / what problem it solves**: A quality score alone — "this session scored low" — tells a team *that* something is wrong, but not *why*, not what to do about it, and not whether many sessions share one root cause or each session has a distinct problem. Manually triaging failures at scale — reading transcripts, spotting patterns, drafting a fix, then verifying that fix actually worked — does not scale past a handful of sessions. Insights automates the diagnostic step, clustering failures into a root-cause hierarchy with fix recommendations, and connects it to the optimization step, generating and validating a revised prompt, closing what would otherwise be a manual, ad hoc loop between "we know it's broken" and "we've shipped and verified a fix."
- **Keywords**: failure clustering, root-cause analysis, user-intent extraction, system-prompt recommendation, A/B testing
- **Related concepts**: [[continuous-online-agent-evaluation]], [[trace-derived-evaluation-field-contract]], [[actionable-side-information]], [[reflective-mutation-proposer]], [[optimize-anything-pattern]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: sources/papers/bedrock-agentcore-observability-evals/

## Summary

Picture a support team that gets a dashboard saying "12% of sessions failed" every week, with no further detail — useful for tracking a trend, but useless for fixing anything, because "failed" could mean a hundred different things. AgentCore Insights is what happens when that dashboard is replaced with an actual diagnosis: it reads a batch of sessions, sorts the failures into a taxonomy (tool errors, hallucinations, wrong reasoning, repetitive behavior, and more), traces each failure category back to the specific spans that caused it, and separately clusters what users were actually trying to do across all those sessions. Optionally, a team can take those clustered findings and hand them to the Recommendations API, which drafts a revised system prompt intended to address the diagnosed issues — and instead of trusting that draft blindly, the team runs an A/B test comparing the original prompt against the revised one on live traffic before fully switching over.

## Example

A team runs a weekly batch Insights job over the past seven days of sessions. The failure-analysis output shows that 40% of failures fall under "tool errors," and drilling into the root-cause clusters reveals that almost all of them come from one specific tool being called with a malformed date format. Rather than guessing at a fix, the team calls the Recommendations API with the current system prompt and the same traces, gets back a revised prompt that adds explicit date-formatting instructions for that tool, and sets up an A/B test splitting live traffic between the original and revised prompts. A week later, the revised prompt shows a measurably lower rate of that specific tool error, and the team promotes it to 100% of traffic.

## Relationship to existing concepts

- [[continuous-online-agent-evaluation]]: Insights can be triggered by a recurring clustering schedule attached to an online evaluation configuration, or run once via batch evaluation over a fixed time range.
- [[trace-derived-evaluation-field-contract]]: Insights' failure-to-span root-cause tracing relies on the same field-extraction contract that makes generic evaluation possible in the first place.
- [[actionable-side-information]]: Both concepts are about distilling raw trace data into feedback that a system can act on for optimization, though Insights is a specific managed-service feature with its own taxonomy and API surface rather than a general optimization technique.
- [[reflective-mutation-proposer]]: A framework-agnostic pattern (as in GEPA) for turning evaluation signal into a candidate improvement; Insights is AWS's own concrete, managed-service version of that same idea for system prompts.
- [[optimize-anything-pattern]]: Insights' triage-then-recommend-then-validate sequence is one specific instance of the broader "optimize anything with evaluation feedback" pattern.
- [[config-bundle-ab-testing-for-agent-behavior]]: The concrete mechanism underneath this loop's final validation step — the Gateway-level sticky routing, variant patterns, and statistical-significance computation that a triggered A/B test actually runs on.

## Open questions

- How reliable is the automatic root-cause clustering when failure categories are ambiguous or overlapping — does a human still need to review the taxonomy before acting on it?
- Does the Recommendations API's generated prompt account for trade-offs (fixing one failure category while risking a regression in another), or does that judgment stay with the A/B test alone?
