---
id: agentic-software-engineering
title: "Agentic Software Engineering: From Vibe Coding to a Verified Delivery System"
description: A focused path for turning AI-assisted coding into a reliable engineering practice, from choosing the right level of rigor through context and harness design to verification, delegation, and total-cost decisions.
---

## Overview

AI can make implementation fast without making requirements, architecture, or verification disappear. This path shows how to choose an appropriate level of rigor for the consequences of failure, then build the context, operating harness, quality gates, and human review needed to make coding agents useful in production. It closes by addressing the hard final portion of a change and the total cost of the system over time.

For detailed evaluation design, use [LLM Quality and Evaluation Pipeline](../topics/llm-quality-evaluation-pipeline.md) as a companion path. For the runtime patterns behind tool surfaces, sessions, and multi-client agents, see [Production Agent Runtime](../topics/production-agent-runtime.md).

**Estimated study time:** 5–6 hours  
**Prerequisites:** Experience building or reviewing a small software feature. Familiarity with LLM APIs is helpful but not required.

---

## Concepts in Order

### 1. [Vibe Coding to Agentic Engineering Spectrum](../concepts/llm-engineering/vibe-coding-to-agentic-engineering-spectrum.md)
Start by matching the amount of specification, verification, and human oversight to the consequence of failure. This prevents applying production process to a disposable experiment—or treating a high-stakes system like a quick prototype.

### 2. [AI-Compressed Software Development Lifecycle](../concepts/llm-engineering/ai-compressed-sdlc.md)
AI speeds implementation much more than requirements, architecture, and verification. Study this next to see where the real bottleneck moves and why fast generation needs a tighter feedback loop rather than fewer decisions.

### 3. [Agentic Software Factory Model](../concepts/llm-engineering/agentic-software-factory-model.md)
Turn the shifted workflow into a repeatable system: specifications direct agents, quality gates evaluate their output, and feedback improves the next attempt. This supplies the operating model for the context and harness decisions that follow.

### 4. [Executable Specification as an Architectural North Star](../concepts/llm-engineering/executable-specification-as-architectural-north-star.md)
Create a versioned blueprint with the technical design, contracts, rationale, and behavioral scenarios that agents use to implement and verify a change.

### 5. [Context Engineering for Coding Agents](../concepts/llm-engineering/context-engineering-for-coding-agents.md)
An agent needs the goal, relevant knowledge, memory, examples, available tools, and guardrails—not simply a longer prompt. Study this before harness design because context is one of the harness's most important controls.

### 6. [Static vs. Dynamic Agent Context](../concepts/llm-engineering/static-vs-dynamic-agent-context.md)
Decide which universal rules must be loaded every time and which specialized material should be retrieved only when needed. This refines the previous concept into a practical strategy that keeps context useful and affordable.

### 7. [Agent Instruction Placement by Scope](../concepts/llm-engineering/agent-instruction-placement-by-scope.md)
Put each instruction in the durable layer that matches its audience: chat for the current session, specifications for a task, skills for repeatable procedures, and project or global files for stable rules. This makes the loading strategy concrete and reproducible.

### 8. [Execution-Mode-Specific Agent Prompting](../concepts/llm-engineering/execution-mode-specific-agent-prompting.md)
Match the prompt to the job: require architecture before a new project, local conventions for features, reproducible evidence for bugs, synchronized documentation, and auditable data commands.

### 9. [Coding Agent Harness Engineering](../concepts/llm-engineering/coding-agent-harness-engineering.md)
Build the surrounding system of rules, tools, sandboxes, orchestration, hooks, and observability that turns a model into a constrained software worker. Study it after context design because the harness is where that context, along with deterministic boundaries and feedback, becomes operational.

### 10. [Risk-Focused High-Velocity Code Review](../concepts/llm-engineering/risk-focused-high-velocity-code-review.md)
Use automated checks and concise risk summaries to make human review focus on architecture, behavior, and likely breakage rather than mechanical style details.

### 11. [Tiered Continuous Code Review Runtime](../concepts/llm-engineering/tiered-continuous-code-review-runtime.md)
Use the smallest continuously triggered review runtime that catches the team's real risks: managed first, CI-hosted custom review when needed, and a stateful owned runtime only for justified scale or impact.

### 12. [Conductor and Orchestrator Developer Modes](../concepts/llm-engineering/conductor-orchestrator-developer-modes.md)
Choose between hands-on, real-time direction for uncertain work and asynchronous delegation for well-specified work. The harness from the previous step supplies the evidence and controls needed in both modes.

### 13. [The 80% Problem in Agentic Coding](../concepts/llm-engineering/agentic-coding-80-percent-problem.md)
Agents often finish the obvious bulk while leaving edge cases, integrations, ambiguity, and architectural correctness unresolved. Study this after delegation to learn where human judgment and targeted verification remain most valuable.

### 14. [Agentic Engineering Total-Cost Curve](../concepts/llm-engineering/agentic-engineering-tco-curve.md)
Close by comparing cheap-looking, ad-hoc generation with upfront investment in context, tests, and guardrails. The right measure is the cost of safely shipping and maintaining successive changes, not the time to generate the first one.

---

### 15. [Effective Trust for Agents](../concepts/llm-engineering/effective-trust-for-agents.md)
Treat authorization as a live decision rather than a deployment-time badge. This adds the runtime evidence and intent-drift controls needed when a coding agent can change its tools and goals during a task.

### 16. [Ephemeral Agent Execution Sandbox](../concepts/llm-engineering/ephemeral-agent-execution-sandbox.md)
Run generated code in a disposable, isolated workspace so a bad script cannot persist or spread to the host.

### 17. [Context-Aware Approval for High-Stakes Agent Actions](../concepts/llm-engineering/context-aware-high-stakes-agent-approval.md)
Require a plain-language intent-to-action explanation before approving a consequential action, so review remains meaningful.

### 18. [Approval-Fatigue-Resistant Agent Oversight](../concepts/llm-engineering/approval-fatigue-resistant-agent-oversight.md)
Route only consequential or out-of-bound actions to people, protect their attention from routine alerts, and use recurring insights to improve the system.

### 19. [Zero Ambient Authority for Agents](../concepts/llm-engineering/zero-ambient-authority-for-agents.md)
Finish by making authority temporary and task-specific, so an agent never inherits broad developer privilege.

### 20. [Hybrid Agent Policy Gating](../concepts/llm-engineering/hybrid-agent-policy-gating.md)
Enforce task-scoped tool permissions with fast structural rules, then inspect allowed actions semantically before they reach external systems.

## What You'll Be Able to Do

- Match agent autonomy and verification rigor to a change's risk
- Design high-signal static and on-demand context for coding agents
- Define a coding-agent harness with useful tools, deterministic boundaries, and feedback
- Choose when to guide work interactively and when to delegate it asynchronously
- Focus review and testing on edge cases, integrations, and ambiguous requirements
- Evaluate AI-assisted development by long-term operating cost rather than initial generation speed
