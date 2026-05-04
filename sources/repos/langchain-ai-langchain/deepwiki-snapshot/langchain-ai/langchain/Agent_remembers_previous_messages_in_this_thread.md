```

For cross-conversation data (e.g., user preferences, facts), use a store:

```python
from langgraph.store.memory import InMemoryStore

agent = create_agent(
    model="openai:gpt-4o",
    store=InMemoryStore(),
    checkpointer=MemorySaver()
)

# Middleware can access store via runtime.store to persist/retrieve data
```

Sources: [libs/langchain_v1/langchain/agents/factory.py:625-632]()

## Summary

LangChain's modern application development is centered on the `create_agent` factory, which produces a LangGraph StateGraph that orchestrates:

1. **Agent loop**: Model → tool calls → tool execution → model (repeat until complete)
2. **Middleware hooks**: Extension points for custom logic at each stage
3. **Structured output**: Automatic parsing of model responses into typed schemas
4. **State management**: Typed state with message history and custom fields
5. **Persistence**: Checkpointers for conversation memory, stores for cross-conversation data

Key architectural patterns:
- Immutable request objects (`ModelRequest.override()`)
- Composable middleware with well-defined hook points
- Automatic tool loop creation when tools are provided
- Provider-agnostic structured output with fallback strategies
- Type-safe state schemas with merge semantics

For detailed middleware implementation patterns, see [Middleware Architecture](#4.2). For legacy chain patterns and backwards compatibility, see [Legacy Application Patterns](#4.3).

Sources: [libs/langchain_v1/langchain/agents/factory.py:541-1337](), [libs/langchain_v1/langchain/agents/middleware/types.py:1-1503]()