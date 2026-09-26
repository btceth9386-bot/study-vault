---
id: llm-security-red-teaming
title: "LLM Security Red Teaming: From Reusable Probes to Multi-Turn Attacks"
description: Build a repeatable LLM security-testing practice by separating the risk being tested from its delivery method, then using adaptive attacker-target-judge loops for failures that require multiple turns.
---

## Overview

An LLM security test should be reproducible evidence, not a one-off clever jailbreak. This path starts by separating the vulnerability you want to test from the strategy used to deliver the attack. It then covers adaptive, multi-turn attacks for cases where a single prompt cannot reveal the failure.

Use this path alongside [LLM Quality and Evaluation Pipeline](../topics/llm-quality-evaluation-pipeline.md) to build the evaluation matrix, assertions, and trace collection that report red-team results. It focuses only on generating adversarial coverage.

**Estimated study time:** 2–3 hours
**Prerequisites:** Basic familiarity with LLM prompts and evaluation. The LLM Quality and Evaluation Pipeline path is recommended.

---

## Concepts in Order

### 1. [Composable LLM Red-Team Testing](../concepts/llm-engineering/composable-llm-red-team-testing.md)
Start with the test design: define the security or policy failure to probe independently from the way an attacker delivers it. This lets one privacy-leakage probe run as a direct request, encoded wording, prompt injection, or a multi-turn conversation without duplicating the risk definition.

### 2. [Iterative Adversarial Testing Loop](../concepts/llm-engineering/iterative-adversarial-testing-loop.md)
Some failures only emerge after the target refuses, reveals context, or takes a tool action. Learn the attacker-target-judge loop, where each attempt is scored and the next attack adapts or backtracks. Set explicit turn, branch-depth, success, and cost limits so security exploration stays bounded.

---

### 3. [Hallucinated-Package Slopsquatting Defense](../concepts/llm-engineering/hallucinated-package-slopsquatting-defense.md)
Prevent an agent from turning a fabricated package name into a malware installation by using trusted registries and provenance gates.

### 4. [Agentic Security Response Triad](../concepts/llm-engineering/agentic-security-response-triad.md)
Combine proactive probes, behavioral anomaly detection, and state-preserving containment into a continuous security response.

### 5. [Runtime Agent Bill of Materials](../concepts/llm-engineering/runtime-agent-bill-of-materials.md)
Track the live tools, data, models, and credentials that determine an agent's active blast radius.

## What You'll Be Able to Do

- Build reusable security probes that can be tested with multiple attack strategies
- Identify when a static prompt is sufficient and when a multi-turn attack loop is needed
- Bound adversarial exploration with measurable success, turn, depth, and cost limits
- Connect red-team probes to a regular evaluation pipeline for comparable, reviewable results
