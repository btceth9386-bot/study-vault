# langchain-ai/langchain

## Summary

This focused pass treats LangChain as supporting infrastructure for LangGraph application development, not as a source for legacy chains or prebuilt agent templates. The durable concepts are the abstractions that make graph nodes interoperable: `langchain-core` message objects, provider chat model wrappers, tool schemas/tool calls, and optional retrieval primitives for RAG agents. `BaseMessage` and its concrete `HumanMessage`, `AIMessage`, and `ToolMessage` types form a provider-neutral conversation log that LangGraph can keep in state, checkpoint, route over, and pass back into chat models. Content blocks extend that log beyond plain text so multimodal inputs, reasoning, tool-use blocks, and provider-specific payloads can be normalized before nodes inspect them.

Provider packages such as `langchain-openai` and `langchain-anthropic` adapt OpenAI and Anthropic APIs to the same `BaseChatModel`/`Runnable` interface. In a LangGraph node, this means code can call `ChatOpenAI` or `ChatAnthropic` with a list of messages and receive an `AIMessage`, including parsed tool calls when tools are bound. The same Runnable interface also explains why LCEL expressions like `prompt | model | parser` exist, but LCEL is only background here: graph nodes and edges own the application flow.

The tool abstraction is the bridge between Python functions and model-selected actions. The `@tool` decorator, `BaseTool`, inferred schemas, and provider conversion utilities produce a standard tool-call contract that a LangGraph `ToolNode` can execute and convert back into `ToolMessage` results. For RAG agents, retrievers and vector stores are supporting infrastructure: they store/search documents and can be wrapped as retrieval nodes or tools inside a graph.

Explicitly skipped: `AgentExecutor`, legacy ReAct/OpenAI Functions agent constructors, `Chain`/`LLMChain`/`SequentialChain`, and high-level application templates not required for LangGraph.

## Knowledge Map

- LangChain messages as the state payload for LangGraph conversations and tool loops.
- Provider chat wrappers as graph-node dependencies for model calls.
- Tool schemas and tool-call messages as the execution contract consumed by ToolNode-like graph nodes.
- Vector stores and retrievers as optional RAG infrastructure, not as the main graph abstraction.

## Key Takeaways

- LangGraph state benefits from `BaseMessage` objects because they preserve roles, provider metadata, tool-call IDs, and normalized content across turns.
- `ChatOpenAI` and `ChatAnthropic` hide provider wire-format differences while preserving a common `AIMessage` output surface.
- Tools should be exposed through `@tool`/`BaseTool` schemas so model output can be parsed into structured `ToolCall` objects and answered with `ToolMessage`.
- LCEL composition is useful context for why these objects are `Runnable`, but graph topology should remain in LangGraph rather than old chain abstractions.
- Retrieval belongs at the infrastructure edge of LangGraph RAG agents: vector store search or retriever invocation supplies context to graph nodes.
