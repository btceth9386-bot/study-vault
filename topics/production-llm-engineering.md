---
id: production-llm-engineering
title: "Production LLM Engineering: Observability, Evaluation, and Durable Pipelines"
description: The infrastructure and engineering patterns specific to LLM applications in production — covering how to make AI behavior visible, how to evaluate and iterate safely, and how to build the data pipelines that make both possible at scale.
---

## Overview

LLM applications fail in ways that don't show up in standard monitoring: a model returns a plausible but wrong answer, a prompt change silently degrades quality, or token costs quietly spiral. This path covers the engineering disciplines that address those failure modes — starting with structured observability (making LLM behavior queryable), then prompt lifecycle management (deploying changes safely), then automated evaluation (catching regressions without human review per trace), and finally the infrastructure patterns that keep high-volume event pipelines reliable. Two concepts borrowed from the system design paths (caching strategies, async processing) appear here in their LLM-specific context.

**Estimated study time:** 4–5 hours  
**Prerequisites:** Basic familiarity with LLM APIs (OpenAI/Anthropic). Optionally, review [Asynchronous Processing](../concepts/system-design/async-processing.md) and [Caching Strategies](../concepts/system-design/caching-strategies.md) from the distributed systems or scalability paths first.

---

## Concepts in Order

### 1. [LLM Observability](../concepts/llm-engineering/llm-observability.md)
The foundation of the entire path. Before you can evaluate, iterate, or optimize, you need structured records of what your LLM application actually did. Introduces the core data model: **traces** (one per request), **observations** (spans, generations, tool calls), and **scores** (quality signals). Every other concept in this path builds on having this data available.

### 2. [Prompt Version Management](../concepts/llm-engineering/prompt-version-management.md)
Prompts change application behavior as much as code changes — but most teams treat them as anonymous strings. Version management gives prompts a version number, a deployment label (e.g., `production`), a change history, and the ability to roll back. Study this second because the payoff — being able to correlate trace quality with prompt version — only makes sense once you understand the observability data model from step 1.

### 3. [LLM-as-Judge Evaluation](../concepts/llm-engineering/llm-as-judge-evaluation.md)
Once you have traces (step 1) and versioned prompts (step 2), you can automate quality measurement. A judge LLM applies a rubric to each production trace and writes a score back to the observability store. This closes the feedback loop: prompt change → new traces → automated scores → compare versions → roll back or promote. Without steps 1 and 2, there is nothing to evaluate and no way to attribute score changes to prompt versions.

### 4. [Caching Strategies](../concepts/system-design/caching-strategies.md)
LLM inference is expensive and slow. Caching addresses both: semantically identical or identical prompts can return cached responses at ~1ms instead of calling the model at ~500ms–2s. The LLM-specific wrinkle is prompt version caching (invalidate when the prompt changes) and the write-through pattern for keeping prompt metadata fresh. This is the same concept from the scalability path, but studied here in the context of cost and latency optimization for AI workloads.

### 5. [Asynchronous Processing](../concepts/system-design/async-processing.md)
LLM evaluation jobs, batch experiments, and embedding generation are all too slow to run synchronously in the request path. Background queues (BullMQ, Celery, SQS) accept the work, process it when resources are available, and write results back to the observability store. This is the same concept from the distributed systems path, applied here to: evaluation execution queues, ingestion pipelines, and automated scoring workers.

### 6. [S3-First Durability Pattern](../concepts/llm-engineering/s3-first-durability.md)
High-volume LLM event ingestion (thousands of traces per second) must survive worker crashes, queue overflows, and downstream outages. Saving raw payloads to object storage before enqueuing them means the original data is never lost — workers can replay from S3. Study after async-processing because the S3-first pattern directly solves the durability gap in pure queue-based architectures: messages can disappear if a queue crashes before a worker processes them; S3 objects cannot.

### 7. [OLTP/OLAP Database Split](../concepts/llm-engineering/oltp-olap-split.md)
The data architecture capstone for LLM infrastructure. Application metadata (users, projects, API keys, prompt configs, evaluator settings) lives in PostgreSQL — OLTP workload. The millions of trace events, generation records, and scores that observability generates live in ClickHouse or a similar OLAP engine — analytical workload. A single database cannot efficiently serve both. Study last because it requires understanding the full data flow: events arrive via the durable async pipeline (steps 5–6), need to be queried analytically (step 1), and reference config data that must stay transactionally consistent (steps 2–3).

---

## What You'll Be Able to Do

- Design a structured observability schema (traces, observations, scores) for any LLM application
- Implement prompt versioning with labels and rollback capability — without deploying new application code
- Set up an LLM-as-judge evaluation pipeline that runs automatically on production traces
- Apply caching at the prompt resolution and response layers to reduce LLM costs
- Architect an event ingestion pipeline that guarantees durability under worker and downstream failures
- Decide what data belongs in PostgreSQL vs. ClickHouse (or equivalent OLAP store) for an LLM monitoring system
