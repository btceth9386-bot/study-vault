---
id: langgraph-application-development
title: "LangGraph Application Development: From Model Primitives to Stateful Agents"
description: A focused path for developers building production LangGraph applications — covering the essential LangChain model layer, LangGraph's state machine runtime, durable execution features, and server deployment, in the order you'll actually need them.
---

## Overview

LangGraph is an explicit state machine framework for LLM applications: you define nodes, edges, state channels, and routing logic rather than relying on a hidden agent loop. This path moves from the LangChain model and tool primitives that every LangGraph node depends on, through the runtime model that explains when writes become visible and why reducers matter, to the production features — checkpoints, human-in-the-loop pauses, long-term memory, and remote graph deployment — that make LangGraph useful beyond toy demos.

This path is a focused extract from the broader [Production LLM Engineering](../topics/production-llm-engineering.md) path. Study this first if you specifically want to build LangGraph applications; read the full path when you also need observability, DSPy optimization, and durable event pipelines.

**Estimated study time:** 6–8 hours  
**Prerequisites:** Comfortable with Python and basic LLM API usage (`openai.chat.completions.create` or equivalent). Familiarity with `async/await` is helpful for the server execution step.

---

## Concepts in Order

### 1. [Provider Chat Model Wrappers in LangGraph Nodes](../concepts/llm-engineering/provider-chat-model-wrappers-in-langgraph-nodes.md)
Every LangGraph node that calls a model goes through a provider wrapper — `ChatOpenAI`, `ChatAnthropic`, or equivalent. These hide provider wire-format differences behind a common interface: messages go in, an `AIMessage` comes out. Start here because all subsequent graph code depends on this interface; understanding it prevents confusion when switching providers or when tool calls appear in the response.

### 2. [Standardized Message Content Blocks](../concepts/llm-engineering/standardized-message-content-blocks.md)
Messages carry more than text — tool calls, tool results, images, audio, and reasoning blocks all travel through graph state as structured content blocks. Study this second because LangGraph state is a conversation history at its core: before writing nodes that inspect or route on message content, you need to know what's actually inside each message.

### 3. [LangChain Tool Schema Contract](../concepts/llm-engineering/langchain-tool-schema-contract.md)
Tool schemas are the contract between a model's requested action and the Python code that executes it. Tool calls appear in `AIMessage.tool_calls`; results return as `ToolMessage` objects bound by `tool_call_id`. Study this before building any tool-executing node, because the schema definition, call dispatch, and result routing are tightly coupled.

### 4. [LangGraph StateGraph State Schema](../concepts/llm-engineering/langgraph-stategraph-state-schema.md)
The state schema defines the shared typed keys that nodes read from and write to. A plain field uses replace-on-write semantics; an annotated field carries a reducer that controls how concurrent writes merge. Study this before the runtime because the schema is the contract that compilation turns into channels — without understanding it, the runtime's behavior around parallel writes and channel types is hard to reason about.

### 5. [LangGraph Pregel BSP Execution](../concepts/llm-engineering/langgraph-pregel-bsp-execution.md)
LangGraph executes graphs in Bulk Synchronous Parallel supersteps: plan runnable nodes, run them concurrently, then apply all their writes together. This explains several behaviors that are otherwise surprising — why nodes in the same step can't see each other's output, how reducers resolve conflicting writes, and where checkpoints fit in the execution cycle. Study this before control flow primitives so routing decisions feel like explicit graph mechanics rather than hidden magic.

### 6. [LangGraph Send and Command Control Flow](../concepts/llm-engineering/langgraph-send-command-control-flow.md)
Static edges, conditional edges, `Send` for dynamic fan-out, and `Command` for node-local routing decisions are the full graph wiring vocabulary. Study this after the runtime because routing determines which nodes enter Pregel's next superstep — the two concepts are inseparable in practice. `Send` is especially important for map-reduce patterns: dispatch a list of items to a node with per-item state.

### 7. [ReAct Agentic Loop](../concepts/llm-engineering/react-agentic-loop.md)
The ReAct pattern — Thought → Action (tool call) → Observation (tool result) → repeat — is the standard LangGraph tool-using agent structure. Study this after control flow primitives because in LangGraph, ReAct is just explicit conditional routing: call model, check for tool calls, either execute tools and loop or exit. Understanding it as graph wiring (not a magic loop) is what lets you add interrupts, parallel tool execution, and observability cleanly.

### 8. [LangGraph Checkpoint Time Travel and Forking](../concepts/llm-engineering/langgraph-checkpoint-time-travel-forking.md)
Checkpoints persist graph state after each superstep — channel values, version counters, pending tasks, and metadata. This enables resuming crashed runs, inspecting execution history, replaying from any historical point, and forking alternative branches via `update_state()`. Study before interrupts because human-in-the-loop pauses are only useful when the graph can safely persist and resume state across the pause.

### 9. [LangGraph Human-in-the-Loop Interrupts](../concepts/llm-engineering/langgraph-human-in-the-loop-interrupts.md)
Interrupts pause graph execution for approval, correction, or user input — either at compile-time node boundaries (`interrupt_before`/`interrupt_after`) or dynamically from inside a node via `interrupt()`. The critical implementation detail: dynamic interrupt nodes re-execute from the beginning on resume, so node logic around `interrupt()` calls must be idempotent. Study after checkpoints because interrupts require a checkpointer to persist the paused state.

### 10. [LangGraph Store Long-Term Memory](../concepts/llm-engineering/langgraph-store-long-term-memory.md)
Checkpoints persist per-thread execution state; the store persists data that should survive across threads and graph runs — user preferences, learned facts, shared documents, semantic search indexes. `BaseStore` provides `get`, `put`, `search`, and `delete` with sync/async variants. Study here because cross-thread memory is a production concern that complements rather than replaces per-thread state; confusing the two leads to over-engineering one or ignoring the other.

### 11. [LangGraph RemoteGraph and Server Execution](../concepts/llm-engineering/langgraph-remotegraph-server-execution.md)
LangGraph Server exposes deployed graphs through Assistants, Threads, Runs, Cron Jobs, and Store APIs. `RemoteGraph` wraps those APIs behind the same interface as a local graph: state reads, updates, streaming, interrupts, and parent commands all work identically. Study last because it operationalizes everything above — checkpoints become thread state, the store becomes the Server's persistent memory, and interrupts become the pause-and-resume API surface.

---

## What You'll Be Able to Do

- Build LangGraph nodes that call models, inspect message content, and dispatch tool calls cleanly
- Define a state schema with the right channel semantics for each field — replace, append, or custom merge
- Explain why nodes in the same Pregel superstep can't read each other's writes, and what that means for graph ordering
- Wire a ReAct tool loop as explicit conditional graph routing instead of a black-box agent executor
- Add checkpointing so a graph can survive worker crashes and resume from saved state
- Insert human-in-the-loop approval gates at compile-time boundaries or with dynamic `interrupt()` calls
- Separate per-thread checkpoint state from cross-thread store memory and choose the right one for each use case
- Deploy a graph to LangGraph Server and call it as a `RemoteGraph` from another service
