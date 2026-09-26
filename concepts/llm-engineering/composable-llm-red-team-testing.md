---
id: composable-llm-red-team-testing
title: Composable LLM Red-Team Testing
depth: 2
lab_status: not-started
last_reviewed: 2026-09-19
review_due: 2026-09-22
sources:
  - sources/repos/promptfoo-promptfoo
related:
  - hybrid-llm-output-assertions
  - model-agnostic-evaluation-provider-abstraction
  - agentic-security-response-triad
tags:
  - llm-engineering
  - evaluation
  - red-teaming
  - security
---

# Composable LLM Red-Team Testing

- **One-sentence definition**: Composable LLM red-team testing keeps the risk being tested separate from the way an attack is delivered, then combines them against a target.
- **Why it exists / what problem it solves**: A data-leakage test and a prompt-injection technique are different things. Separating them avoids duplicate tests and makes it easier to extend coverage.
- **Keywords**: red team, vulnerability, attack strategy, prompt injection, jailbreak, coverage
- **Related concepts**: [[hybrid-llm-output-assertions]], [[model-agnostic-evaluation-provider-abstraction]]
- **Depth**: 2/4
- **Last updated**: 2026-09-19
- **Source**: promptfoo/promptfoo

## Summary

Think of a red-team test as choosing both a lock to test and a tool to test it with. A vulnerability plugin chooses the problem to probe, such as private-data leakage or harmful content. An attack strategy chooses the delivery method, such as encoding, prompt injection, or a multi-turn conversation.

Because those choices are independent, one risk can be tested through several delivery methods without copying the risk definition. The resulting cases can carry severity and compliance mappings, then use the normal evaluation and provider layers to run against models, HTTP applications, or agents.

## Example

To check whether a support agent leaks account data, define one privacy-leakage probe. Run it once as a plain request, once with encoded wording, and once in a multi-turn conversation. The team can compare which delivery method succeeds without redefining the privacy risk three times.

## Relationship to existing concepts

- [[hybrid-llm-output-assertions]]: Red-team cases use the same combined grading result as ordinary evaluations.
- [[model-agnostic-evaluation-provider-abstraction]]: The same probes can target a model, an HTTP application, or an agent runtime through one provider boundary.

## My questions

- Which combinations of risks and strategies give useful coverage without making a suite too expensive?
- When should a red-team finding require human review before it is reported as a vulnerability?

## Promotion backlinks

- [[agentic-security-response-triad]]: Uses reusable adversarial probes for its Red role.
