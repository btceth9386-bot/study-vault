---
id: production-agent-runtime
title: "Production Agent Runtime: From Prototype to Multi-Platform Deployment"
description: A path for developers who have built a working LLM agent and need to make it production-ready — covering tool and skill organization, protocol-based client integration, durable state, context management, scheduled automation, and governed self-improvement.
---

## Overview

A working agent in a notebook is not a production agent. Production requires answering a different set of questions: How are tools and reusable skills organized and selectively exposed? How does the agent serve IDEs, CLI, and messaging platforms without duplicating logic? What happens to sessions when the process restarts? How do you handle context limits in long-running conversations? Can the agent run unattended on a schedule? And how does it accumulate experience without giving unproven procedures too much authority?

This path covers the patterns that answer those questions, drawn from the Hermes agent reference implementation and complementary sources on agent skills and interoperability. The patterns are independent of any specific agent framework; they apply whether you are building on LangGraph, a custom loop, or another runtime.

For the protocol mechanics behind MCP-based integrations, study [MCP Protocol Foundations](../topics/mcp-protocol-foundations.md) first or use it as a companion path. For the internal mechanics of LangGraph state machines, checkpoints, and interrupts, see [LangGraph Application Development](../topics/langgraph-application-development.md). For evaluation pipelines and quality measurement, see [LLM Quality and Evaluation Pipeline](../topics/llm-quality-evaluation-pipeline.md).

A closing case study applies the session, memory, and hosting decisions above to a real managed multi-agent platform, Amazon Bedrock AgentCore, showing a config-vs-code hosting tradeoff, infrastructure-enforced session isolation, a health-probe pattern for long-running tasks, shared memory safely namespaced across many agents, and a durable-memory-specific security concern that single-turn content isolation doesn't cover. A second case-study wave then covers the operational and governance layer on top of that architecture: per-second cost attribution and hard runaway-agent limits, immutable versioned deployment, two concrete AWS-documented security failure modes and their fixes, gateway rate limiting with an explicit fail-open caveat, Cedar-based deterministic policy authorization with session-aware temporal extensions and safe shadow-testing, and statistically validated A/B testing for rolling out a behavior change.

**Estimated study time:** 16–19 hours
**Prerequisites:** Built at least one working LLM agent with tool calling. No specific framework required.

---

## Concepts in Order

### 1. [Toolsets and MCP Unified Tool Surface](../concepts/llm-engineering/toolsets-and-mcp-unified-tool-surface.md)
Before exposing an agent to any client, you need coherent control over what tools it can reach. A unified tool surface registers both built-in tools and externally provided MCP tools into the same discovery and invocation system, then groups them into configurable toolsets. Study this first because every subsequent pattern — IDE integration, multi-platform serving, cron automation, evaluation — depends on being able to selectively compose what a given agent session can do. Without toolsets, tool access is all-or-nothing, which makes safe multi-client deployment impossible.

### 2. [Skills as the Unit of Agent Improvement](../concepts/llm-engineering/skills-as-unit-of-agent-improvement.md)
Treat a skill as a small, owned, versioned capability rather than another global-prompt edit or a new specialist agent. Study this after toolsets because both define the conditional capability surface the runtime can expose.

### 3. [Agent Skills as Procedural Memory](../concepts/llm-engineering/agent-skills-as-procedural-memory.md)
Skills retain reusable ways of doing a task without permanently expanding an agent's prompt. This gives the runtime a practical form of procedural memory before you decide how a skill is routed and loaded.

### 4. [Skill Description as a Routing Interface](../concepts/llm-engineering/skill-description-as-routing-interface.md)
Write clear positive triggers and explicit non-triggers so the right procedure loads for the right job. Study this before progressive disclosure because routing decides which skill instructions may enter the active context.

### 5. [Progressive Disclosure for Agent Skills](../concepts/llm-engineering/agent-skill-progressive-disclosure.md)
Keep skill metadata available for routing, load instructions only after selection, and load resources only when needed. This makes a large library usable without charging every turn for every procedure.

### 6. [Authority-Tiered Agent Skills](../concepts/llm-engineering/authority-tiered-agent-skills.md)
Separate read-only, draft-only, and action-allowed skills, increasing evidence and review requirements with potential harm. This turns selective capability exposure into a concrete release policy before clients invoke skills against real systems.

### 7. [State-Externalized Skill Composition](../concepts/llm-engineering/state-externalized-skill-composition.md)
Pass multi-step work through structured files, schemas, or message buses rather than an ever-growing conversation. Study this before multi-client deployment because reproducible handoffs make skill runs inspectable across sessions and interfaces.

### 8. [ACP Agent Backend for IDEs](../concepts/llm-engineering/acp-agent-backend-for-ides.md)
IDEs need a structured protocol to open sessions, stream updates, and trigger completions without coupling to a specific agent implementation. The Agent Client Protocol (ACP) translates IDE lifecycle events — initialize, session creation, prompt execution, streaming — into internal agent operations. It introduces the first concrete deployment surface: the IDE as a structured client. The session model introduced here (a session tied to a working directory, surviving across requests) is the foundation that the persistence and restoration concepts build on.

### 9. [Multi-Platform Agent Gateway](../concepts/llm-engineering/multi-platform-agent-gateway.md)
One core agent runtime should serve CLI, Telegram, Discord, Slack, and IDE clients rather than maintaining separate bots with separate state. A gateway layer routes platform-specific messages into a common agent interface while centralizing memory, tool access, and automation. Study after ACP because the IDE backend is one concrete gateway implementation; the gateway pattern generalizes it to arbitrary channels. Understanding this prevents the common mistake of duplicating agent logic across platforms.

### 10. [Layered Agent Memory](../concepts/llm-engineering/layered-agent-memory.md)
Use separate layers for current work, one-session state, long-lived knowledge, experience, and discrete observations. This gives the agent the right information without turning every old conversation into active context.

### 11. [Persistent Agent Session Restoration](../concepts/llm-engineering/persistent-agent-session-restoration.md)
Session state stored only in process memory is lost when the process restarts. Persistent session restoration saves conversation history and session metadata to a shared database, then reloads it on demand — including ACP sessions tied to a specific working directory. Study here because the multi-platform gateway requires each channel to be able to pick up sessions that started on a different channel or after a restart. This is the durability layer for session continuity.

### 12. [Surgical Context Compression](../concepts/llm-engineering/surgical-context-compression.md)
Tool-using agents accumulate large conversation histories quickly. Blunt truncation discards context indiscriminately. Surgical context compression preserves the head and tail of the interaction — system instructions and recent turns — while summarizing the middle when token usage crosses a threshold. Hermes also prunes expensive tool outputs and protects key turns from summarization. Study after session persistence because compression decisions are only well-defined when history is durable; you need to know what is safe to compress vs. what must survive intact.

### 13. [Context-Rot-Aware Context Management](../concepts/llm-engineering/context-rot-aware-context-management.md)
Keep context useful, not merely below the model's token limit. Monitor quality signals such as relevance, instruction adherence, noise, and repetition, then compact or prune before the agent drifts.

### 14. [Bounded Agent Cognitive State](../concepts/llm-engineering/bounded-agent-cognitive-state.md)
For very long-running work, keep a fixed, schema-constrained task state rather than letting summaries and chat history grow forever. This makes memory use predictable, but requires careful decisions about what information deserves a slot.

### 15. [Natural-Language Cron Agent Automation](../concepts/llm-engineering/natural-language-cron-agent-automation.md)
An interactive agent that can only respond to explicit user messages is limited to synchronous work. Cron automation turns scheduled work into a first-class agent feature: jobs are defined as agent prompts or scripts, scheduled declaratively, executed in isolated runs with explicit delivery targets (messaging channels, storage), and given their own toolset scopes. Study here because scheduled automation requires both the gateway (for delivery routing) and session persistence (for isolated execution state) established in earlier steps — and it is the mechanism that extends an agent from assistant to unattended operator.

### 16. [Self-Improving Agent Skill Memory Loop](../concepts/llm-engineering/self-improving-agent-skill-memory-loop.md)
An agent that treats every session as a fresh start cannot improve. A self-improving skill memory loop closes this gap: the agent stores useful knowledge from completed tasks, creates or updates reusable skills, and uses that accumulated experience when working on similar problems later. Study here because the loop depends on persistent session storage for the memory substrate and on cron-style automation for the periodic knowledge consolidation nudge that keeps skills current.

### 17. [Agent Specialization as a Scaling Mechanism](../concepts/llm-engineering/agent-specialization-as-scaling-mechanism.md)
As an agent accumulates tools, instructions, and responsibilities, its search space and failure blast radius grow. Split work into domain-focused specialists only when a generalist has become overloaded; each specialist should receive a narrower context and toolset, while the runtime supplies routing and guardrails. Study this after establishing durable sessions and automation, since those capabilities provide the state and operational controls that coordinated specialists require.

### 18. [Artifact-Based Agent Handoffs](../concepts/llm-engineering/artifact-based-agent-handoffs.md)
Specialists should exchange typed, inspectable deliverables rather than whole conversation transcripts. This makes multi-agent work easier to audit, resume, and debug.

### 19. [Untrusted Content Isolation for Agents](../concepts/llm-engineering/untrusted-content-isolation-for-agents.md)
Treat retrieved files, web pages, and tool output as data rather than instructions. Keep authority in the runtime, then combine isolation with policy gates, scoped credentials, and sandboxes before any side effect occurs.

### 20. [Code-as-Action Agent Loop](../concepts/llm-engineering/code-as-action-agent-loop.md)
When a task needs tool composition, variables, and control flow, an agent can write code as one action. Treat it as a higher-risk action layer: execute it in an ephemeral sandbox with narrowly scoped authority.

### 21. [Agent Loop Termination Policy](../concepts/llm-engineering/agent-loop-termination-policy.md)
An agent must know both when success is credible and when autonomous work has reached an operational limit. Combine a completion signal with step, time, token, or cost limits, and use goal verification where a false success is expensive.

### 22. [Probabilistic Toolset Distributions](../concepts/llm-engineering/probabilistic-toolset-distributions.md)
When evaluating or training an agent, always exposing the same full tool surface produces uniform trajectories that do not reflect real-world variation in available capabilities. Probabilistic toolset distributions sample which toolsets the agent receives across batch runs, generating diverse trajectories for benchmarking and training data collection. Study last because this is an evaluation-time concern that requires a working toolset system (step 1) and is most relevant once the runtime patterns above are in place and you need to measure agent quality honestly across varying capability environments.

---

## Case Study: Amazon Bedrock AgentCore's Session, Hosting, and Shared-Memory Model

Everything above describes runtime patterns as engineering decisions you implement yourself. This closing case study looks at how one managed multi-agent platform, Amazon Bedrock AgentCore, makes the same hosting, session, and memory decisions concretely — and where a managed default still needs a security control you must add.

### 23. [AgentCore Harness vs. Runtime Tradeoff](../concepts/llm-engineering/agentcore-harness-vs-runtime-tradeoff.md)
The entry point into the case study: a config-driven managed orchestration loop (Harness) versus infrastructure underneath orchestration code you write yourself (Runtime). Study this first because it is the hosting decision everything else in the case study sits inside — AWS frames these as complementary, not competing, options.

### 24. [microVM Session Isolation and Lifecycle](../concepts/llm-engineering/microvm-session-isolation-lifecycle.md)
The infrastructure layer under either hosting choice: every session gets its own dedicated microVM, moves through Active/Idle/Stopped states, and is destroyed with its memory sanitized by default. Study this after the hosting tradeoff, and alongside step 11's persistent session restoration, as the opposite default assumption — sessions are ephemeral and isolated unless you deliberately make them durable.

### 25. [Health-Probe-Driven Task Liveness](../concepts/llm-engineering/health-probe-driven-task-liveness.md)
A specific mechanism sitting underneath step 24's session lifecycle: overloading a health-check endpoint to report "busy with real work" so the platform's existing idle timeout skips a legitimate long-running task, with no separate task-tracking system required. Study this right after session isolation because it only makes sense once you know what default timeout it's designed to bypass.

### 26. [Memory Namespace Multi-Tenant Isolation](../concepts/llm-engineering/memory-namespace-multi-tenant-isolation.md)
Moves from session infrastructure to shared memory: a hierarchical, trailing-slash-terminated path scheme that lets one memory resource be safely shared across many actors or agents, doubling as an IAM condition key so the organizational scheme becomes an enforced access boundary. Study this after step 10's layered memory model, as the concrete answer to organizing the long-term layer once multiple agents share it.

### 27. [Cross-Account Memory Resource Sharing](../concepts/llm-engineering/cross-account-memory-resource-sharing.md)
Extends namespace isolation across AWS account boundaries: resource-based policies let a principal in another account call memory APIs directly, or let the memory resource deliver data to another account's S3, SNS, or Kinesis. Study this right after namespace isolation, since a real multi-team deployment typically needs both — namespacing within an account and policy-based sharing across accounts.

### 28. [Long-Term Memory vs. RAG Boundary](../concepts/llm-engineering/long-term-memory-vs-rag-boundary.md)
A design-boundary concept for the memory layer: long-term memory holds personalized, evolving state about a specific user, while RAG retrieves current, authoritative knowledge from a shared repository. Study this after the namespace and cross-account concepts because it clarifies which content should even be routed into the shared memory system you just designed, versus a separate retrieval pipeline.

### 29. [Memory Poisoning Defense in Agent Systems](../concepts/llm-engineering/memory-poisoning-defense-in-agent-systems.md)
Closes the case study by returning to step 19's untrusted-content isolation with a longer time horizon: because long-term memory extraction runs asynchronously through an LLM, poisoned input becomes a persistent, repeatedly-retrieved corruption rather than a single-turn hijack, so the defense has to sit at the write boundary, before persistence, not after. Study this last because it depends on understanding the memory pipeline (steps 26–28) that poisoned content would actually flow through.

---

## Case Study: Amazon Bedrock AgentCore's Operational Controls and Policy Governance

The first case study covered architecture — hosting, sessions, and memory. This second wave covers what it takes to actually operate that architecture safely at scale: cost and runaway-agent limits, safe deployment, concrete documented security failure modes, and a governance layer for controlling what agents are allowed to do.

### 30. [Harness Cost Attribution and Hard Limits](../concepts/llm-engineering/harness-cost-attribution-and-hard-limits.md)
Start with the operational basics that apply to any deployed harness, following naturally from step 23's hosting choice: billing reflects actual per-second CPU and memory consumption rather than wall-clock time, and hard caps (max iterations, timeout, token budget, idle and max session lifetime) bound a runaway agent regardless of the agent's own stopping logic from step 21.

### 31. [Immutable Versioned Endpoints for Agent Config](../concepts/llm-engineering/immutable-versioned-endpoints-for-agent-config.md)
The second operational basic: every configuration change creates a new, complete, immutable version, and a named endpoint only moves to a new version when explicitly repointed. Study this alongside cost and limits as the other prerequisite for operating any harness safely — it's what makes promoting a change to production, and rolling it back, a deliberate, low-risk act rather than an implicit side effect of redeploying.

### 32. [Structured Payload Injection via Type Confusion](../concepts/llm-engineering/structured-payload-injection-via-type-confusion.md)
Moves into concrete, documented security failure modes. If an agent's entrypoint doesn't enforce that its `prompt` field is actually a string, a caller can smuggle a structured `toolUse` block that some frameworks execute directly, bypassing the model and its guardrails entirely. Study this first among the security concepts because it's the most surprising failure — a type-checking omission, not a sophisticated attack — and the easiest to fix once known.

### 33. [AgentCore Trust-Boundary Hardening](../concepts/llm-engineering/agentcore-trust-boundary-hardening.md)
Widens the security lens from the entrypoint to the surrounding IAM and network trust boundary: confused-deputy trust-policy conditions, resource-based policies that must be configured on both a runtime and its endpoint, and closing direct Runtime access so a gateway's policies can't be trivially bypassed. Study this after the payload vulnerability as the next layer of AgentCore-specific hardening a team needs to check.

### 34. [Multi-Dimension Rate Limiting with Fail-Open Defaults](../concepts/llm-engineering/multi-dimension-rate-limiting-with-fail-open.md)
A Gateway-level throughput control that groups traffic by caller, tool, or model and fails open by default — allowed through if the rate-limit service is unavailable. Study this right after trust-boundary hardening as an explicit caveat: this control protects availability, not authorization, and must never be treated as the security boundary that step 33's hardening actually provides.

### 35. [Cedar Policy Gateway Authorization](../concepts/llm-engineering/cedar-policy-gateway-authorization.md)
The governance centerpiece: Policy in AgentCore intercepts every tool call at the Gateway boundary and evaluates it against Cedar policies with default-deny and forbid-wins semantics, moving authorization outside the agent's own code so it can't be bypassed by manipulating the agent. Study this once the surrounding trust boundary (step 33) and rate limiting (step 34) are both understood, since this is the actual access-control mechanism those Gateway-level controls sit alongside.

### 36. [Temporal Session-Aware Policy Conditions](../concepts/llm-engineering/temporal-session-aware-policy-conditions.md)
Extends step 35 specifically where plain Cedar can't reach: rules that depend on what already happened earlier in the same session, such as requiring a prior approval or capping a running total. Study this immediately after Cedar policy authorization as its most consequential extension for multi-step, stateful agent workflows.

### 37. [Shadow-Mode Policy Testing with Decision-Flip Telemetry](../concepts/llm-engineering/shadow-mode-policy-testing-with-decision-flip-telemetry.md)
A safety mechanism for deploying new policies from step 35 or step 36: a `LOG_ONLY` policy or engine evaluates against real traffic without ever affecting the returned decision, and decision-flip telemetry shows whether promoting it to enforcement would actually change outcomes. Study this once you have policies worth testing, as the safe on-ramp to enforcing them.

### 38. [Config-Bundle A/B Testing for Agent Behavior](../concepts/llm-engineering/config-bundle-ab-testing-for-agent-behavior.md)
Closes both case studies with the general-purpose validation mechanism for any behavior change: live traffic is split between a control and treatment variant — built on step 31's immutable versioning for configuration-only changes — scored by online evaluation, and promoted only once a statistically significant improvement is confirmed. Study this last because it is the rollout mechanism that every other change discussed in this path — a new prompt, a new policy, a new tool — should ultimately pass through before reaching all production traffic.

---

## What You'll Be Able to Do

- Organize built-in and MCP tools into a unified registry with configurable toolsets that can be selectively exposed per session
- Package, route, progressively load, compose, and release skills as bounded reusable capabilities
- Expose an agent over ACP so IDEs can open sessions, stream responses, and resume conversations across restarts
- Route multiple platform clients (CLI, messaging apps, IDEs) through one core agent runtime without duplicating logic
- Persist session state to a database so conversations survive process restarts and can be resumed across interfaces
- Compress long agent conversations without losing continuity by preserving head/tail and summarizing the middle
- Define recurring agent jobs declaratively with isolated toolset scopes and explicit delivery routing
- Build a feedback loop that converts task experience into reusable skills the agent applies in future sessions
- Split an overloaded generalist into focused agents without widening their tool or access boundaries
- Vary tool access across evaluation runs to generate realistic trajectories instead of overfitting to a single capability regime
- Evaluate the config-vs-code tradeoff between a managed orchestration loop and infrastructure-only hosting for a multi-agent deployment
- Design infrastructure-enforced session isolation and a health-probe pattern that safely extends a session's lifetime for long-running background tasks
- Namespace shared long-term memory across many actors or agents, and extend that isolation across AWS account boundaries with resource-based policies
- Decide which content belongs in long-term memory versus a RAG pipeline, and defend a shared memory store against poisoning at the point of persistence
- Attribute agent cost to actual per-second consumption and bound a runaway agent with platform-enforced hard limits, independent of the agent's own stopping logic
- Deploy agent configuration changes as immutable, named-endpoint-pinned versions so promotion and rollback are explicit, low-risk acts
- Recognize and fix a type-confusion payload vulnerability, and harden an AgentCore Runtime's trust boundary against confused-deputy and gateway-bypass failures
- Apply Gateway rate limiting as a throughput control (with its fail-open caveat) and distinguish it from a real, fail-closed authorization boundary
- Move tool-call authorization outside agent code with Cedar policies, extend it with session-aware temporal conditions, and safely test a new policy with LOG_ONLY shadow mode before enforcing it
- Validate a prompt, policy, or config change with a statistically significant live A/B test before routing all traffic to it
