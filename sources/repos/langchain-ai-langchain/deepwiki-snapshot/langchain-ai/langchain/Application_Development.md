This page guides developers through building LangChain applications, focusing on the agent system, middleware architecture, and observability patterns. LangChain provides a flexible framework for creating autonomous AI systems that can use tools, maintain conversation state, and adapt their behavior through composable middleware.

## Development Approaches

LangChain supports two primary application patterns:

| Pattern | Use Case | Key Features |
|---------|----------|--------------|
| **Runnable Chains** (see [2.1](#2.1)) | Deterministic pipelines | LCEL composition, streaming, predictable flow |
| **Agent Systems** | Autonomous decision-making | Tool use, dynamic routing, middleware extensibility |

This page focuses on agent-based development. For Runnable composition patterns, see [Runnable Interface and LCEL](#2.1).

## Agent System Overview

The `create_agent` factory from [libs/langchain_v1/langchain/agents/factory.py:543-688]() constructs agents as LangGraph `StateGraph` instances. Agents autonomously decide which tools to call based on conversation context, repeating until a stopping condition is met.

**Agent Creation**

```python
from langchain.agents import create_agent
from langchain_core.tools import tool

@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    return f"Results for: {query}"

agent = create_agent(
    model="openai:gpt-4o",
    tools=[search_web],
    system_prompt="You are a helpful research assistant"
)