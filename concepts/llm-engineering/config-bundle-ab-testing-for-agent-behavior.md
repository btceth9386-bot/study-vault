---
id: config-bundle-ab-testing-for-agent-behavior
title: Config-Bundle A/B Testing for Agent Behavior
depth: 2
lab_status: not-started
last_reviewed: 2026-09-26
review_due: 2026-09-29
sources:
  - sources/papers/bedrock-agentcore-agentops
related:
  - agentcore-insights-triage-loop
  - immutable-versioned-endpoints-for-agent-config
tags:
  - aws
  - agentcore
  - experimentation
  - reliability
---

# Config-Bundle A/B Testing for Agent Behavior

- **One-sentence definition**: AgentCore's A/B testing splits live production traffic between a control and treatment variant at the Gateway — sticky by session ID, so a given session always sees the same variant — scores each session with online evaluation, and reports statistical significance so a team can decide whether to promote the treatment, with variants defined either as versions of an immutable configuration bundle (for prompt, model-ID, or tool-description changes) or as entirely different Gateway targets (for code or framework changes).
- **Why it exists / what problem it solves**: A prompt or config change that scores well on an offline batch evaluation can still behave differently once it meets the full messiness of real production traffic, and eyeballing a metric before and after a full rollout can't distinguish a genuine improvement from ordinary variance or a coincidental shift in traffic mix. Routing a controlled slice of live traffic to each variant, scoring both with the same online evaluators, and only trusting a difference once it clears a significance threshold (a p-value below 0.05, in AWS's documented convention) turns "we think this is better" into a validated decision. Splitting variant definition into two patterns — a configuration bundle when only the prompt, model ID, or tool descriptions change, versus a Gateway target when the change involves different code or an entirely different runtime — lets the same statistical process cover both a small config tweak and a larger implementation change, without forcing every change through a full redeploy just to test it.
- **Keywords**: A/B testing, configuration bundle, statistical significance, sticky session routing, online evaluation
- **Related concepts**: [[agentcore-insights-triage-loop]], [[immutable-versioned-endpoints-for-agent-config]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: Amazon Bedrock AgentCore Developer Guide — Operations, reliability, and governance

## Summary

Picture a taste test run at scale: instead of asking one chef whether their new recipe tastes better, you serve both the old and new recipe to different tables of real customers, keep track of which table got which recipe, and only declare the new one better once enough tables have weighed in that the difference clearly isn't just noise. AgentCore's A/B testing does exactly this for agent behavior. The Gateway is the host that seats customers (sessions) at a table (variant) and keeps them there for the whole meal (sticky routing by session ID); online evaluators are the taste scorers; and the statistical significance calculation is what stops the team from declaring victory after just a handful of good reviews.

## Example

A team suspects a revised system prompt reduces a specific tool-calling error. They package the revised prompt into a new configuration bundle version and start an A/B test with 50% of traffic on the original bundle (control) and 50% on the new one (treatment), using an online evaluator that scores exactly that error type. After a few days of live traffic, the results show the treatment's mean error-free rate is higher with a p-value of 0.02 — below the 0.05 threshold — so the team promotes the treatment variant, and 100% of traffic moves to the new bundle.

## Relationship to existing concepts

- [[agentcore-insights-triage-loop]]: That concept's triage-then-recommend-then-validate loop describes running an A/B test at a high level, as its final validation step. This concept is the actual mechanism underneath that step — the Gateway-level sticky routing, the two variant patterns, and the statistical-significance computation — and it is a general-purpose validation tool any config change can use, not only one produced by Insights' diagnosis pipeline.
- [[immutable-versioned-endpoints-for-agent-config]]: Configuration bundles are a more specialized instance of that concept's general immutable-snapshot idea, applied specifically so that A/B test variants can be swapped without a redeploy.

## My questions

- How does a team choose the traffic split ratio (e.g., 50/50 versus 90/10) when a bad treatment variant could meaningfully harm user experience during the test?
- What happens to sessions that were already assigned to a variant if the test is stopped or the losing variant is retired — do they finish on their original variant?
