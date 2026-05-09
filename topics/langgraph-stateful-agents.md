---
id: langgraph-stateful-agents
title: "Building Stateful Agents with LangGraph"
description: A hands-on path from LangChain's model and tool primitives through LangGraph's execution model to production deployment — covering everything needed to build agents that persist state, pause for human review, maintain long-term memory, and run at scale.
---

## Overview

The ReAct agentic loop works for simple tool-using tasks, but breaks down when you need agents that survive crashes, pause for human approval, maintain memory across conversations, or compose with other agents. LangGraph solves these problems by modeling agents as graphs: state is explicit and typed, execution is deterministic, and persistence is built in.

This path starts with the LangChain primitives that any LangGraph node depends on, shows why a raw loop falls short, then builds through LangGraph's execution model, routing, persistence, human oversight, long-term memory, and production server APIs. By the end you will be able to design and deploy a stateful agent that handles real production concerns.

**Estimated study time:** 8–10 hours  
**Prerequisites:** Basic Python and LLM API experience. Familiarity with [Asynchronous Processing](../concepts/system-design/async-processing.md) is helpful for the deployment concepts.

---

## Concepts in Order

### 1. [Provider Chat Model Wrappers in LangGraph Nodes](../concepts/llm-engineering/provider-chat-model-wrappers-in-langgraph-nodes.md)
The model interface inside a node: `ChatOpenAI`, `ChatAnthropic`, and similar wrappers hide provider-specific wire formats behind a single `.invoke(messages)` → `AIMessage` interface. Start here because every subsequent concept either passes messages into a model wrapper or reads the output it produces.

### 2. [Standardized Message Content Blocks](../concepts/llm-engineering/standardized-message-content-blocks.md)
Messages carry more than text: images, audio, reasoning blocks, tool calls, and tool results travel as typed content blocks inside `HumanMessage`, `AIMessage`, and `ToolMessage`. Understanding this structure is the prerequisite for writing node logic that inspects or routes based on what a model returned.

### 3. [LangChain Tool Schema Contract](../concepts/llm-engineering/langchain-tool-schema-contract.md)
Tools bridge model decisions and Python execution. The `@tool` decorator attaches a JSON schema to a function; the model's tool call request includes schema-validated arguments in `AIMessage.tool_calls`; tool results return as `ToolMessage` objects tied to the call ID. Study before the agentic loop because tool calls flow through the message structure covered in step 2.

### 4. [ReAct Agentic Loop](../concepts/llm-engineering/react-agentic-loop.md)
The Thought → Action → Observation loop is the simplest form of a tool-using agent. Study it here to understand what it gets right (multi-step reasoning, iterative tool use) and where it falls short: no state persistence, no human pause points, no memory across conversations. These limitations motivate the LangGraph concepts ahead.

### 5. [Retrievers and Vector Stores for LangGraph RAG](../concepts/llm-engineering/retrievers-vector-stores-for-langgraph-rag.md)
Retrieval can be either a fixed graph node or a model-selected tool. Retrievers abstract over vector stores and provide a standard `.invoke(query)` → `Document[]` interface. Study before LangGraph state because RAG adds a retrieval step whose results need to flow through graph state alongside messages.

### 6. [LangGraph StateGraph State Schema](../concepts/llm-engineering/langgraph-stategraph-state-schema.md)
A LangGraph graph is built around an explicit state schema — a `TypedDict` or Pydantic model defining what data every node reads and may update. The schema controls how the compiler creates channels for each field, which determines update semantics: replace-on-write for scalar values, reducer-based merge for lists. This is the structural foundation everything else builds on.

### 7. [LangGraph Pregel BSP Execution](../concepts/llm-engineering/langgraph-pregel-bsp-execution.md)
LangGraph's runtime runs in Bulk Synchronous Parallel supersteps: select runnable nodes, execute them concurrently, apply their writes atomically, then advance. This model explains why concurrent nodes can't see each other's writes within a step, how reducers resolve multi-writer conflicts, and where checkpoint boundaries fall. Understanding the execution model is the mental model you need before reasoning about routing and state updates.

### 8. [LangGraph Send and Command Control Flow](../concepts/llm-engineering/langgraph-send-command-control-flow.md)
Routing in LangGraph is explicit and developer-controlled: static edges express fixed sequencing, conditional edges choose destinations from state, `Send` schedules the same node multiple times with different per-task state (the map-reduce primitive), and `Command` lets a node decide its own next destination. These primitives replace the hidden loop inside a `ReAct` executor with visible, auditable control flow.

### 9. [LangGraph Checkpoint, Time Travel, and Forking](../concepts/llm-engineering/langgraph-checkpoint-time-travel-forking.md)
Checkpoints persist graph state after each superstep, making long-running agents recoverable from crashes. The checkpoint lineage enables time travel (inspect historical state at any step), replay (re-execute from a past checkpoint), and forking (branch from a historical state to explore alternatives). This is the persistence layer that makes production agents debuggable and auditable.

### 10. [LangGraph Human-in-the-Loop Interrupts](../concepts/llm-engineering/langgraph-human-in-the-loop-interrupts.md)
Static interrupts pause before or after named nodes at compile time. Dynamic `interrupt()` calls pause from inside node logic and surface a value to the caller for approval or correction. Resuming a dynamic interrupt re-executes the interrupted node from the start — so node code must tolerate re-execution. This is what makes approval gates and user-correction workflows possible without leaving the graph execution model.

### 11. [LangGraph Store: Long-Term Memory](../concepts/llm-engineering/langgraph-store-long-term-memory.md)
Checkpoints store one thread's execution state. The store persists data across threads, conversations, and sessions — user preferences, learned facts, shared documents. `BaseStore` provides namespaced key-value access with optional vector search and TTL. Long-term memory belongs in the store, not in graph state, because it outlives any single run.

### 12. [LangGraph RemoteGraph and Server Execution](../concepts/llm-engineering/langgraph-remotegraph-server-execution.md)
The LangGraph Server exposes deployed graphs through Assistants, Threads, Runs, Cron Jobs, and Store APIs. `RemoteGraph` wraps those APIs behind the same protocol as a local graph, so a local agent can call a remote deployed graph as a node without changing its execution model. This is how multi-agent architectures scale to distributed services.

---

## What You'll Be Able to Do

- Build a LangGraph node around any LangChain chat model and inspect `AIMessage` tool calls and content blocks
- Define a `@tool` with proper schema and wire it into a graph as an executable node
- Design a `TypedDict` state schema with both replace-on-write and reducer-backed fields
- Explain what the Pregel superstep model means for concurrent node writes and reducer behavior
- Route graph execution using static edges, conditional edges, `Send`, and `Command`
- Add checkpointing to make a graph recoverable and inspectable via `get_state_history()`
- Insert human approval gates using static or dynamic interrupts and handle resume correctly
- Configure a persistent store for cross-thread agent memory with namespace-scoped keys
- Expose a deployed graph through the LangGraph Server API and call it via `RemoteGraph`
