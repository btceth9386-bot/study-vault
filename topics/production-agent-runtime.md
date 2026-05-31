---
id: production-agent-runtime
title: "Production Agent Runtime: From Prototype to Multi-Platform Deployment"
description: A path for developers who have built a working LLM agent and need to make it production-ready — covering tool surface organization, protocol-based client integration, session persistence, context management, scheduled automation, and self-improvement.
---

## Overview

A working agent in a notebook is not a production agent. Production requires answering a different set of questions: How are tools organized and selectively exposed? How does the agent serve IDEs, CLI, and messaging platforms without duplicating logic? What happens to sessions when the process restarts? How do you handle context limits in long-running conversations? Can the agent run unattended on a schedule? And how does it accumulate experience instead of starting from scratch each session?

This path covers the eight patterns that answer those questions, drawn from the Hermes agent reference implementation. The patterns are independent of any specific agent framework; they apply whether you are building on LangGraph, a custom loop, or another runtime.

For the protocol mechanics behind MCP-based integrations, study [MCP Protocol Foundations](../topics/mcp-protocol-foundations.md) first or use it as a companion path. For the internal mechanics of LangGraph state machines, checkpoints, and interrupts, see [LangGraph Application Development](../topics/langgraph-application-development.md). For evaluation pipelines and quality measurement, see [LLM Quality and Evaluation Pipeline](../topics/llm-quality-evaluation-pipeline.md).

**Estimated study time:** 5–7 hours  
**Prerequisites:** Built at least one working LLM agent with tool calling. No specific framework required.

---

## Concepts in Order

### 1. [Toolsets and MCP Unified Tool Surface](../concepts/llm-engineering/toolsets-and-mcp-unified-tool-surface.md)
Before exposing an agent to any client, you need coherent control over what tools it can reach. A unified tool surface registers both built-in tools and externally provided MCP tools into the same discovery and invocation system, then groups them into configurable toolsets. Study this first because every subsequent pattern — IDE integration, multi-platform serving, cron automation, evaluation — depends on being able to selectively compose what a given agent session can do. Without toolsets, tool access is all-or-nothing, which makes safe multi-client deployment impossible.

### 2. [ACP Agent Backend for IDEs](../concepts/llm-engineering/acp-agent-backend-for-ides.md)
IDEs need a structured protocol to open sessions, stream updates, and trigger completions without coupling to a specific agent implementation. The Agent Client Protocol (ACP) translates IDE lifecycle events — initialize, session creation, prompt execution, streaming — into internal agent operations. Study this second because it introduces the first concrete deployment surface: the IDE as a structured client. The session model introduced here (a session tied to a working directory, surviving across requests) is the foundation that the persistence and restoration concepts build on.

### 3. [Multi-Platform Agent Gateway](../concepts/llm-engineering/multi-platform-agent-gateway.md)
One core agent runtime should serve CLI, Telegram, Discord, Slack, and IDE clients rather than maintaining separate bots with separate state. A gateway layer routes platform-specific messages into a common agent interface while centralizing memory, tool access, and automation. Study after ACP because the IDE backend is one concrete gateway implementation; the gateway pattern generalizes it to arbitrary channels. Understanding this prevents the common mistake of duplicating agent logic across platforms.

### 4. [Persistent Agent Session Restoration](../concepts/llm-engineering/persistent-agent-session-restoration.md)
Session state stored only in process memory is lost when the process restarts. Persistent session restoration saves conversation history and session metadata to a shared database, then reloads it on demand — including ACP sessions tied to a specific working directory. Study here because the multi-platform gateway from step 3 requires each channel to be able to pick up sessions that started on a different channel or after a restart. This is the durability layer for session continuity.

### 5. [Surgical Context Compression](../concepts/llm-engineering/surgical-context-compression.md)
Tool-using agents accumulate large conversation histories quickly. Blunt truncation discards context indiscriminately. Surgical context compression preserves the head and tail of the interaction — system instructions and recent turns — while summarizing the middle when token usage crosses a threshold. Hermes also prunes expensive tool outputs and protects key turns from summarization. Study after session persistence because compression decisions are only well-defined when history is durable; you need to know what is safe to compress vs. what must survive intact.

### 6. [Natural-Language Cron Agent Automation](../concepts/llm-engineering/natural-language-cron-agent-automation.md)
An interactive agent that can only respond to explicit user messages is limited to synchronous work. Cron automation turns scheduled work into a first-class agent feature: jobs are defined as agent prompts or scripts, scheduled declaratively, executed in isolated runs with explicit delivery targets (messaging channels, storage), and given their own toolset scopes. Study here because scheduled automation requires both the gateway (for delivery routing) and session persistence (for isolated execution state) established in earlier steps — and it is the mechanism that extends an agent from assistant to unattended operator.

### 7. [Self-Improving Agent Skill Memory Loop](../concepts/llm-engineering/self-improving-agent-skill-memory-loop.md)
An agent that treats every session as a fresh start cannot improve. A self-improving skill memory loop closes this gap: the agent stores useful knowledge from completed tasks, creates or updates reusable skills, and uses that accumulated experience when working on similar problems later. Study here because the loop depends on persistent session storage (step 4) for the memory substrate and on cron-style automation (step 6) for the periodic knowledge consolidation nudge that keeps skills current.

### 8. [Probabilistic Toolset Distributions](../concepts/llm-engineering/probabilistic-toolset-distributions.md)
When evaluating or training an agent, always exposing the same full tool surface produces uniform trajectories that do not reflect real-world variation in available capabilities. Probabilistic toolset distributions sample which toolsets the agent receives across batch runs, generating diverse trajectories for benchmarking and training data collection. Study last because this is an evaluation-time concern that requires a working toolset system (step 1) and is most relevant once the runtime patterns above are in place and you need to measure agent quality honestly across varying capability environments.

---

## What You'll Be Able to Do

- Organize built-in and MCP tools into a unified registry with configurable toolsets that can be selectively exposed per session
- Expose an agent over ACP so IDEs can open sessions, stream responses, and resume conversations across restarts
- Route multiple platform clients (CLI, messaging apps, IDEs) through one core agent runtime without duplicating logic
- Persist session state to a database so conversations survive process restarts and can be resumed across interfaces
- Compress long agent conversations without losing continuity by preserving head/tail and summarizing the middle
- Define recurring agent jobs declaratively with isolated toolset scopes and explicit delivery routing
- Build a feedback loop that converts task experience into reusable skills the agent applies in future sessions
- Vary tool access across evaluation runs to generate realistic trajectories instead of overfitting to a single capability regime
