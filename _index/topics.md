# Topics Index

Curated learning paths that group related concepts into recommended study orders.

## Recommended Learning Paths

These three paths are the main suggested routes through the current concept library. Together they cover every concept currently in `concepts/`.

- [Web Scalability: From Single Server to Production](../topics/web-scalability.md) — 11 concepts · ~6–8h · Learn the chronological growth path from one server to a redundant web architecture.
- [Distributed Systems Foundations](../topics/distributed-systems-foundations.md) — 7 concepts · ~5–6h · Build the reasoning model for CAP, consistency, async messaging, microservices, and distributed data design.
- [Production LLM Engineering](../topics/production-llm-engineering.md) — 23 concepts · ~12–16h · Study observability, prompt lifecycle control, evaluation, optimization, LangGraph foundations, and durable LLM systems.

## Concept Coverage

| Concept | Web Scalability | Distributed Systems | Production LLM |
|---|:---:|:---:|:---:|
| vertical-scaling | ✓ | | |
| horizontal-scaling | ✓ | | |
| load-balancing | ✓ | | |
| sticky-sessions | ✓ | | |
| caching-strategies | ✓ | | ✓ |
| database-replication | ✓ | ✓ | |
| database-sharding | ✓ | ✓ | |
| raid-storage | ✓ | | |
| single-point-of-failure | ✓ | | |
| high-availability | ✓ | | |
| ssl-termination | ✓ | | |
| cap-theorem | | ✓ | |
| eventual-consistency | | ✓ | |
| async-processing | | ✓ | ✓ |
| microservices | | ✓ | |
| oltp-olap-split | | ✓ | ✓ |
| llm-observability | | | ✓ |
| prompt-version-management | | | ✓ |
| llm-as-judge-evaluation | | | ✓ |
| provider-chat-model-wrappers-in-langgraph-nodes | | | ✓ |
| standardized-message-content-blocks | | | ✓ |
| langchain-tool-schema-contract | | | ✓ |
| retrievers-vector-stores-for-langgraph-rag | | | ✓ |
| s3-first-durability | | | ✓ |
| dspy-signatures | | | ✓ |
| dspy-module-composition | | | ✓ |
| few-shot-bootstrapping | | | ✓ |
| metric-driven-llm-optimization | | | ✓ |
| actionable-side-information | | | ✓ |
| reflective-mutation-proposer | | | ✓ |
| pareto-efficient-candidate-selection | | | ✓ |
| system-aware-candidate-merge | | | ✓ |
| adapter-based-llm-optimization | | | ✓ |
| sparse-validation-evaluation | | | ✓ |
| optimize-anything-pattern | | | ✓ |
| react-agentic-loop | | | ✓ |

## Additional Focused Views

These existing topic files reuse concepts from the recommended paths for narrower study goals:

- [LLM Program Optimization with DSPy](../topics/llm-program-optimization-dspy.md) — focus on DSPy signatures, modules, metrics, bootstrapping, GEPA-style reflection, ReAct, and production observability.
- [Reliability Engineering for AI Backends](../topics/reliability-engineering-for-ai-backends.md) — apply scalability and reliability patterns to AI event pipelines, queues, storage, and data stores.
