---
id: trace-aware-agent-evaluation
title: Trace-Aware Agent Evaluation
depth: 2
lab_status: not-started
last_reviewed: 2026-09-19
review_due: 2026-09-22
sources:
  - sources/repos/promptfoo-promptfoo
related:
  - authority-tiered-agent-skills
  - agent-skill-evaluation-coverage
  - llm-observability
  - agentic-workflow-span-hierarchy
  - context-propagation-with-carriers
  - agentic-coding-80-percent-problem
  - multidimensional-coding-agent-evaluation
  - runtime-agent-bill-of-materials
  - session-convergence-evaluation
  - agent-loop-termination-policy
  - trace-derived-evaluation-field-contract
  - continuous-online-agent-evaluation
tags:
  - llm-engineering
  - evaluation
  - observability
  - agents
  - tracing
---

# Trace-Aware Agent Evaluation

- **One-sentence definition**: Trace-aware agent evaluation grades the execution path by checking recorded tool use, arguments, order, spans, and goal completion alongside the final response.
- **Why it exists / what problem it solves**: An agent can give a plausible answer through an unsafe, unauthorized, inefficient, or wrong sequence of actions, so output-only grading can hide process failures.
- **Keywords**: trajectory, tools, spans, trace assertions, goal completion, agent evaluation
- **Related concepts**: [[authority-tiered-agent-skills]], [[agent-skill-evaluation-coverage]], [[llm-observability]], [[agentic-workflow-span-hierarchy]], [[context-propagation-with-carriers]], [[agentic-coding-80-percent-problem]]
- **Depth**: 2/4
- **Last updated**: 2026-09-19
- **Source**: promptfoo/promptfoo

## Summary

For an agent, the final text is only part of the result. A trace-aware evaluation reads the recorded path to see which tools were used, whether their arguments were safe, whether the calls happened in the intended order, how many spans occurred, and whether the whole trajectory met its goal.

The raw spans are first normalized into a trajectory, a simple sequence of meaningful steps. Assertions then turn that telemetry into pass/fail evidence. This exposes cases where an agent happened to answer correctly but took an unacceptable route.

## Example

A customer-support agent correctly tells a user that a refund is available. A trace-aware test still fails it because the agent called the payment API before it checked the customer's identity. A passing test requires the identity tool first, the policy tool second, and no payment action until both succeed.

## Relationship to existing concepts

- [[authority-tiered-agent-skills]]: More consequential action tiers need stronger trace evidence for their execution paths.
- [[agent-skill-evaluation-coverage]]: Coverage adds trigger, regression, and context-budget evidence around trace checks.
- [[llm-observability]]: Observability captures and stores the spans and tool calls that the evaluator reads.
- [[agentic-workflow-span-hierarchy]]: Span hierarchy explains how individual agent actions fit inside the wider workflow.
- [[context-propagation-with-carriers]]: Propagated context keeps distributed tool calls correlated in one trace.
- [[agentic-coding-80-percent-problem]]: Trace checks provide evidence for the subtle, high-risk paths that can remain after rapid code generation.
- [[multidimensional-coding-agent-evaluation]]: Trajectory quality and self-repair are dimensions this evaluation can inspect.
- [[runtime-agent-bill-of-materials]]: The live inventory adds context about the resources active in a trajectory.
- [[session-convergence-evaluation]]: Full-session traces provide the evidence needed to measure convergence.
- [[agent-loop-termination-policy]]: Goal verification can use trace evidence before an agent is allowed to stop.
- [[trace-derived-evaluation-field-contract]]: AgentCore's documented span-classification and field-extraction rules are one concrete mechanism for turning a raw trace into the structured evidence this evaluation style needs.
- [[continuous-online-agent-evaluation]]: This trajectory-grading approach can run as a one-time check or, in AgentCore's online evaluation mode, continuously against live production traffic.

## My questions

- Which trajectory requirements are universal safety rules, and which are specific to one workflow?
- How should tests handle legitimate parallel tool calls when order is not fully deterministic?
