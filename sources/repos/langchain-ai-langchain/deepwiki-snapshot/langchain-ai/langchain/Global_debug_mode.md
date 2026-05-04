from langchain_core.globals import set_debug
set_debug(True)  # Enables console logging globally
```

**LangSmith Tracing**

```python
import os

# Enable automatic LangSmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-api-key"

# All invocations are automatically traced
result = agent.invoke({"messages": [...]})
```

For detailed coverage of callback handlers, custom implementations, and event streaming patterns, see [Callbacks and Tracing](#4.3).

Sources: [libs/langchain_v1/langchain/agents/factory.py:543-688]()

## Persistence and State Management

Agents are built on LangGraph's `StateGraph`, which provides checkpointing for conversation persistence and stores for cross-thread data.

### Checkpointing

Checkpointers from [libs/langchain_v1/langchain/agents/factory.py:625-632]() save state after each step:

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver