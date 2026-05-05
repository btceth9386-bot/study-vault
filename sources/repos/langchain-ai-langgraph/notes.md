# langchain-ai/langgraph — DeepWiki Notes

Source: https://deepwiki.com/langchain-ai/langgraph

LangGraph is a low-level orchestration framework for building stateful, multi-actor LLM applications. Its core value is not prompt abstraction; it is durable execution, explicit control flow, persistence, human intervention, and memory for long-running agent workflows. The main local programming model is `StateGraph`, where developers define typed state, add node functions, connect nodes with edges, and compile the builder into a runnable `Pregel` runtime.

The execution engine is based on the Pregel / Bulk Synchronous Parallel model. Execution advances in supersteps: the runtime plans which nodes should run from previous channel updates, executes eligible nodes concurrently, then atomically applies their writes to channels. This matters because writes from nodes in the same superstep are not visible to one another until the next step, and concurrent writes must be resolved by channel semantics.

State is represented through channels. Ordinary fields map to `LastValue`, which rejects conflicting multi-writer updates in a single step. Annotated fields can use reducers such as `operator.add` through `BinaryOperatorAggregate`, while `Topic`, `EphemeralValue`, `UntrackedValue`, and barrier-style channels support specialized data-flow behavior. Checkpoints persist channel values and versions after execution steps, enabling resume, replay, state inspection, and branching.

Control flow is explicit: static edges define unconditional scheduling, conditional edges route from state, `Send` enables dynamic fan-out with custom per-task state, and `Command` lets a node update state and choose the next destination in one return value. Human-in-the-loop workflows use static interrupts or dynamic `interrupt()` calls; both rely on checkpoints and resume through subsequent invocations, commonly with `Command(resume=...)`.

LangGraph also includes runtime dependency injection, long-term store APIs, server-side resources, and remote execution. `Runtime` injects context, store, stream writer, and execution metadata into nodes. `BaseStore` provides cross-thread memory with hierarchical namespaces and optional vector search. LangGraph Server organizes deployed execution around Assistants, Threads, Runs, Cron Jobs, and Store resources, while `RemoteGraph` lets a remote graph behave like a local runnable graph.
