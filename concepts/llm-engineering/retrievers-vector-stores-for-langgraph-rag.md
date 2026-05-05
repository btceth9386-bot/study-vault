---
id: retrievers-vector-stores-for-langgraph-rag
title: Retrievers and Vector Stores for LangGraph RAG
depth: 2
last_reviewed: 2026-05-05
review_due: 2026-05-08
sources:
  - sources/repos/langchain-ai-langchain
related:
  - provider-chat-model-wrappers-in-langgraph-nodes
  - langchain-tool-schema-contract
  - langgraph-store-long-term-memory
tags:
  - llm-engineering
  - langchain
  - langgraph
  - rag
  - retrieval
---

# Retrievers and Vector Stores for LangGraph RAG

- **One-sentence definition**: Retrievers and vector stores are the LangChain pieces that let a LangGraph RAG workflow find relevant documents before sending grounded context to a chat model.
- **Why it exists / what problem it solves**: A model only knows what is in its prompt and parameters. Retrieval-augmented generation, or RAG, adds a search step so the model can answer with evidence from external documents.
- **Keywords**: RAG, retriever, vector store, embeddings, similarity search, documents
- **Related concepts**: [[provider-chat-model-wrappers-in-langgraph-nodes]], [[langchain-tool-schema-contract]], [[langgraph-store-long-term-memory]]
- **Depth**: 2/4
- **Last updated**: 2026-05-05
- **Source**: sources/repos/langchain-ai-langchain

## Summary

Imagine asking a coworker a question and handing them the right folder before they answer. A vector store is the filing cabinet: it stores documents along with embeddings, which are numeric fingerprints of meaning. A retriever is the clerk: it takes a query, searches the cabinet, and returns the most relevant documents.

In LangChain, a `VectorStore` exposes similarity search methods and can be wrapped with `.as_retriever()` into a `VectorStoreRetriever`. In LangGraph, retrieval can be a normal graph node chosen by application control flow, or it can be exposed as a tool that the model chooses when it needs context. Either way, retrieval stays separate from the provider chat model wrapper: search finds evidence, and the graph decides how that evidence becomes model input.

## Example

```python
def retrieve_context(state: dict) -> dict:
    docs = retriever.invoke(state["question"])
    return {"context": docs}

def answer_with_context(state: dict) -> dict:
    messages = [
        ("system", "Answer using the provided context."),
        ("human", f"Context: {state['context']}\n\nQuestion: {state['question']}")
    ]
    return {"messages": [model.invoke(messages)]}
```

The graph can decide that retrieval always happens before answering. For a more flexible agent, the same retrieval function could be exposed through the tool schema contract and called only when the model asks for it.

## Relationship to existing concepts

- [[provider-chat-model-wrappers-in-langgraph-nodes]]: Retrieved documents are usually fed into a provider chat model wrapper as context for generation.
- [[langchain-tool-schema-contract]]: Retrieval can be wrapped as a tool when the model should decide whether external context is needed.
- [[langgraph-store-long-term-memory]]: LangGraph store can provide persistent, namespaced memory that complements retrievers and vector stores.

## Open questions

- Should retrieval be a fixed graph step for predictability, or a model-selected tool for flexibility?
- What metadata should retrieved documents carry so downstream model calls can cite or filter them correctly?
