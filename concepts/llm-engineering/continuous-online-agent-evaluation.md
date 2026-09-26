---
id: continuous-online-agent-evaluation
title: Continuous Online Agent Evaluation
depth: 2
lab_status: not-started
last_reviewed: 2026-09-26
review_due: 2026-09-29
sources:
  - sources/papers/bedrock-agentcore-observability-evals/
related:
  - session-convergence-evaluation
  - trace-aware-agent-evaluation
  - proactive-incident-prevention-loop
  - autonomous-incident-investigation
  - agentcore-insights-triage-loop
tags:
  - llm-engineering
  - evaluation
  - observability
  - aws
  - agentcore
---

# Continuous Online Agent Evaluation

- **One-sentence definition**: Online evaluation is a standing configuration — which evaluators to apply, which live data sources to monitor, and evaluation parameters — that continuously scores an agent's real production traffic, as opposed to on-demand evaluation (a single run you trigger manually) or batch evaluation (a run over a fixed historical time range or dataset).
- **Why it exists / what problem it solves**: Agent quality can drift after deployment: a model update, a prompt change, a data-source change, or simply a new kind of user request can silently degrade behavior that passed every pre-deployment test. A one-time evaluation, whether on-demand or batch, only tells you about the traffic you happened to sample at the moment you chose to run it — it cannot catch a regression that appears three weeks later. A standing online configuration turns evaluation into an ongoing production signal, similar in spirit to an SLO or a health check, so quality regressions surface close to when they actually happen instead of at the next manual audit.
- **Keywords**: online evaluation, production monitoring, continuous scoring, quality drift, evaluation configuration
- **Related concepts**: [[session-convergence-evaluation]], [[trace-aware-agent-evaluation]], [[proactive-incident-prevention-loop]], [[autonomous-incident-investigation]], [[agentcore-insights-triage-loop]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: sources/papers/bedrock-agentcore-observability-evals/

## Summary

Most evaluation work happens like a scheduled exam: you pick a dataset or a time window, run the evaluators, get a score, and move on until the next time you remember to check. Online evaluation instead works like a continuous health monitor: you configure it once — which evaluators to run, which live traffic to sample, what counts as a pass or fail — and it keeps scoring new production requests as they happen, indefinitely, without anyone triggering a fresh run. This matters because agents do not stay still after launch. A model provider ships an update, someone tweaks a system prompt, or users start asking questions the agent was never tested against — and a one-off evaluation from launch day tells you nothing about any of that. A standing configuration means a quality drop shows up in the data close to when it actually starts, not whenever someone next remembers to run a check.

## Example

A team ships an agent after it passes a thorough batch evaluation against a curated test set. Two weeks later, the underlying model provider silently updates the model version behind the scenes. With only the original batch evaluation, the team would have no signal until a customer complaint surfaced. Because they had also configured online evaluation — the same evaluators, now running continuously against live traffic — the average correctness score dips visibly in their evaluation dashboard within a day of the model update, well before any customer notices, letting the team investigate immediately.

## Relationship to existing concepts

- [[session-convergence-evaluation]]: Another evaluation modality, focused on whether a session resolves the user's need rather than on the continuous-vs-triggered distinction this concept makes.
- [[trace-aware-agent-evaluation]]: Turns recorded trajectories into explicit behavioral tests; online evaluation is one deployment mode for running that kind of scoring continuously rather than once.
- [[proactive-incident-prevention-loop]]: Shares the underlying idea of converting ongoing production signal into standing monitoring rather than one-off inspection, though that concept concerns operational incidents rather than agent output quality.
- [[autonomous-incident-investigation]]: Both rely on always-on production telemetry as their evidence base, applied to different questions (incident cause vs. quality score).
- [[agentcore-insights-triage-loop]]: Insights' recurring clustering schedule is configured on top of an online evaluation configuration, making this concept the input mechanism that loop depends on.

## Open questions

- How does an online evaluation configuration balance evaluation cost against sampling every request, especially for high-volume agents?
- What is the right response when an online evaluator itself starts producing unreliable scores — does the platform detect evaluator drift, or only agent drift?
