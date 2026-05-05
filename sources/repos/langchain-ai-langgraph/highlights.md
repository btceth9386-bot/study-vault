# langchain-ai/langgraph — Highlights

Source: https://deepwiki.com/langchain-ai/langgraph

## Core Runtime

- `Overview.md`: LangGraph is positioned as infrastructure for stateful, multi-actor LLM applications, with durable execution, human-in-the-loop support, and memory as first-class capabilities.
- `Core_Execution_System.md`: Both `StateGraph` and the Functional API compile down to the same `Pregel` runtime, so `invoke`, `stream`, `ainvoke`, and `astream` share one execution model.
- `Pregel_Execution_Engine.md`: Execution uses Plan, Execute, and Update phases. This is the key mental model for understanding why parallel nodes cannot observe each other's writes until the next superstep.

## State And Channels

- `State_Management_and_Channels.md`: State schema fields compile into channel objects such as `LastValue`, `BinaryOperatorAggregate`, `Topic`, `EphemeralValue`, and `UntrackedValue`.
- `State_Management_and_Channels.md`: `LastValue` rejects multiple writes in one step, while reducer-backed channels intentionally merge concurrent updates. This is one of the most important correctness rules for graph design.
- `State_Management_and_Channels.md`: Channel versions are stored in checkpoints and help determine which nodes should trigger from changed inputs.

## Control Flow

- `Control_Flow_Primitives.md`: Static edges schedule fixed successors; conditional edges route from state; `Send` performs dynamic fan-out with custom state; `Command` combines state update and routing.
- `Control_Flow_Primitives.md`: `START` and `END` are virtual sentinels used in edge declarations, not executable nodes.

## Persistence, Human Review, And Replay

- `Human-in-the-Loop_and_Interrupts.md`: Static interrupts are configured at compile time, while dynamic interrupts are raised from inside node logic with `interrupt()`.
- `Human-in-the-Loop_and_Interrupts.md`: Dynamic interrupts re-execute the node on resume; deterministic interrupt IDs and checkpoint scratchpad state allow the resumed call to return the human-provided value.
- `Time_Travel_and_State_Forking.md`: Replay invokes from a historical checkpoint in the same lineage; forking uses `update_state()` to create a new branch before continuing.

## Runtime, Memory, And Deployment

- `Runtime_and_Dependency_Injection.md`: `Runtime` injects run-scoped context, store, stream writer, execution metadata, and server metadata into node functions.
- `Store_System.md`: `BaseStore` is separate from graph checkpoints. It provides cross-thread, long-term key-value memory with namespaces, optional vector search, and TTL.
- `Server_API.md`: LangGraph Server exposes Assistants, Threads, Runs, Cron Jobs, and Store resources; Threads hold stateful checkpoint history, while Runs execute an Assistant against a Thread.
- `RemoteGraph.md`: `RemoteGraph` implements the same protocol as local Pregel graphs, so remote graphs can be composed into local graphs while preserving state, streaming, interrupts, and parent commands.
- `Prebuilt_Components.md`: `ToolNode`, `tools_condition`, and injection helpers remain active prebuilt components. `create_react_agent` is documented as deprecated in favor of `langchain.agents.create_agent`.
