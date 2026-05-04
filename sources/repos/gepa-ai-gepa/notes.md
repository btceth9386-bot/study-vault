# gepa-ai/gepa

## Summary

GEPA (Genetic-Pareto) is a framework for optimizing textual components of AI systems, including prompts, signatures, tool descriptions, configuration strings, and even code-like artifacts. Its main claim is that text optimization should not rely only on scalar rewards. Instead, GEPA feeds rich execution traces, errors, logs, intermediate reasoning, and evaluator feedback into an LLM-based proposer so each mutation is targeted at a diagnosed failure. The core loop starts from a seed candidate, evaluates it, selects candidates and batches, captures traces, asks a reflection model to propose improved text, and accepts the proposal only when it improves on the relevant sample. GEPA keeps a population of candidates rather than a single best prompt, using Pareto frontiers so variants that perform well on different examples or objectives can survive. A merge proposer can later combine complementary descendants from a shared ancestor.

The architecture is deliberately adapter-based. The GEPA engine does not know whether it is optimizing a single prompt, a DSPy module, an MCP tool description, a RAG pipeline, or an arbitrary evaluator wrapped by `optimize_anything()`. Adapters own evaluation, trace capture, and reflective dataset construction. State management adds lineage, sparse validation coverage, caching, persistence, and resumability. The result is a practical optimization pattern for LLM systems where failures are inspectable, metrics are available, and text components are easier to mutate than model weights.

## Knowledge Map

- Textual candidates are dictionaries of named components, such as `system_prompt`, `query_rewriter`, or DSPy predictor instructions.
- Actionable Side Information gives the reflection model diagnostic feedback beyond a numeric score.
- Pareto frontiers preserve candidates that specialize on different validation examples or objectives.
- Reflective mutation and merge proposals provide two complementary evolutionary operators.
- Adapters isolate domain-specific execution from GEPA's generic optimization engine.
- Sparse validation, caching, and stopping conditions keep optimization cost bounded.

## Key Takeaways

- GEPA is closest to metric-driven LLM optimization, but its distinctive mechanism is trace-informed textual evolution.
- The quality of the evaluator and side information determines how useful reflection can be.
- The adapter boundary is the main extension point; custom systems integrate by implementing evaluation and reflective dataset construction.
- Pareto management matters because the globally best average prompt may hide useful specialists.
- Production use cases emphasize budgeted optimization, resumable runs, and deployment through existing prompt or agent platforms.
