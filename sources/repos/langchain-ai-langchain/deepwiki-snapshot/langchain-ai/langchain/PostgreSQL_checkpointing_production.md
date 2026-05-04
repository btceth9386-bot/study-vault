agent = create_agent(
    model="openai:gpt-4o",
    checkpointer=PostgresSaver.from_conn_string("postgresql://...")
)
```

**Thread-based Conversation Persistence**

```python
# Each thread_id maintains separate conversation state
config = {"configurable": {"thread_id": "user-alice-123"}}

agent.invoke(
    {"messages": [{"role": "user", "content": "My name is Alice"}]},
    config=config
)

# Later invocation with same thread_id
agent.invoke(
    {"messages": [{"role": "user", "content": "What's my name?"}]},
    config=config
)
# Agent remembers: "Your name is Alice"
```

Sources: [libs/langchain_v1/langchain/agents/factory.py:625-632]()

### Store for Cross-Thread Data

While checkpointers persist per-thread history, stores from [libs/langchain_v1/langchain/agents/factory.py:629-634]() enable sharing data across threads:

```python
from langgraph.store.memory import InMemoryStore

agent = create_agent(
    model="openai:gpt-4o",
    store=InMemoryStore(),
    checkpointer=MemorySaver()
)