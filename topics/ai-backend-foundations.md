---
id: ai-backend-foundations
title: "AI Backend Foundations: What Changes When You Add LLM Features"
description: A path for web developers who understand standard backends — databases, HTTP, queues, caches — and need to understand the specific patterns that emerge when LLM inference, observability, and evaluation enter the stack.
---

## Overview

A developer who can build a production web application already knows most of what's needed to support an LLM feature: databases for persistence, HTTP for APIs, queues for background work, caches for performance. What they often don't know is the handful of patterns that are specific to LLM workloads — patterns driven by inference latency (500ms–30s), inference cost ($0.001–$0.10 per request), bursty event volumes from observability, and the need to separately track transactional config data and analytical event data.

This path adds exactly those patterns on top of existing web development knowledge. It is not a general introduction to distributed systems; it is a targeted answer to the question: "I can already build web backends. What's genuinely different about AI backends?"

For a deeper treatment of reliability, high availability, and SPOF analysis applied to AI infrastructure, see [Reliability Engineering for AI Backends](../topics/reliability-engineering-for-ai-backends.md). For the data model you'll be storing and querying, see [LLM Observability](../concepts/llm-engineering/llm-observability.md) or the full [Production LLM Engineering](../topics/production-llm-engineering.md) path.

**Estimated study time:** 4–5 hours  
**Prerequisites:** Comfortable with web backends: relational databases, HTTP request-response, and at least one message queue system (Redis, RabbitMQ, SQS, etc.). No prior LLM experience required.

---

## Concepts in Order

### 1. [Caching Strategies](../concepts/system-design/caching-strategies.md)
The first and most impactful lever for AI backend cost and latency. A new LLM call costs $0.001–$0.10 and takes 500ms–30s; a cache hit costs fractions of a cent and takes under 1ms. Cache-aside is the standard pattern for caching generated responses. Write-through keeps prompt metadata fresh without stale reads. The AI-specific wrinkle is **prompt-version-aware cache invalidation**: when a prompt version is promoted to `production`, all cached responses for the previous version must be invalidated, because the same user input now maps to a different prompt. Provider-side prefix caching (Anthropic/OpenAI cache the KV for repeated system prompts) is a second layer that works transparently — but only if you keep system prompts stable across requests.

### 2. [Asynchronous Processing](../concepts/system-design/async-processing.md)
LLM inference (500ms–30s), automated evaluation (seconds to minutes per example), and batch embedding generation (minutes to hours) are all too slow for the HTTP request-response path. These workloads belong in background queues — BullMQ, Celery, SQS — that accept the task immediately, process when resources are available, and write results back to storage. For an AI backend, this means: the API endpoint accepts a trace ingestion request and returns 200 immediately; a worker asynchronously evaluates the trace and writes a score back to the observability store. Study this early because every subsequent infrastructure pattern depends on having a queue layer to work with.

### 3. [S3-First Durability Pattern](../concepts/llm-engineering/s3-first-durability.md)
AI applications generate high-volume, bursty observability events — potentially thousands of trace records per second. If you enqueue those events directly and a queue crashes before the workers process them, the data is gone. The S3-first pattern solves this: persist the raw event payload to object storage before enqueuing a processing task. The queue becomes a processing hint rather than the source of truth, and any worker failure can be recovered by replaying from S3. Study after async-processing because S3-first is the answer to the durability gap that pure queue-based designs leave open — the gap that you won't notice until a production incident.

### 4. [LLM Observability](../concepts/llm-engineering/llm-observability.md)
The specific data model your AI backend must emit and store. Traces (one per end-to-end request), observations (spans, LLM calls, tool calls nested inside), and scores (quality signals attached at any level) are the three core entities. Understanding this data model tells you what your ingestion pipeline is processing, what your analytical queries will look like, and why standard application logging (unstructured strings, APM spans) doesn't serve AI monitoring well. Study here — after the infrastructure concepts — because the observability data model is the load your pipeline must handle and the schema your databases must serve.

### 5. [Prompt Version Management](../concepts/llm-engineering/prompt-version-management.md)
Prompts change application behavior as much as code changes — but they typically deploy without a deployment pipeline, version number, or rollback procedure. Prompt version management fixes this: every prompt has an auto-incrementing version, a deployment label (`production`, `staging`), and a history that links it to the traces it produced. For a web developer, this is the AI equivalent of database migrations: a discipline for making configuration changes safely and reversibly, without deploying new application code. Study after observability because the payoff — correlating trace quality with the specific prompt version that produced it — only makes sense once you understand the trace data model.

### 6. [OLTP/OLAP Database Split](../concepts/llm-engineering/oltp-olap-split.md)
An AI backend generates two fundamentally different data workloads simultaneously. Application metadata — users, projects, API keys, prompt configurations, evaluator settings — is low-volume, ACID-requiring, and naturally fits a relational database like PostgreSQL. Observability events — millions of trace records, generation logs, and evaluation scores per day — are high-volume, analytical, and naturally fit a columnar OLAP store like ClickHouse. Forcing both into PostgreSQL makes analytical queries slow; the standard answer is to route each workload to a database designed for it. Study here because this split is the most important single data architecture decision in an AI backend, and it follows directly from understanding the observability data model (step 4) and the event pipeline (steps 2–3).

### 7. [Database Replication](../concepts/system-design/database-replication.md)
The transactional PostgreSQL database (user accounts, project config, prompt definitions) needs the same reliability treatment as any production database: read replicas to scale dashboard query traffic off the primary, and a failover target for HA. For an AI backend this matters because evaluation pipelines write scores back to Postgres concurrently with application writes — a single unprotected primary under that combined write load is a reliability risk. Master-slave replication handles the read scale and gives you a failover target; master-master eliminates the write single point of failure if you need zero-RPO. Study last because replication is the operational complement to the OLTP/OLAP split: once you've separated the databases, each one needs its own HA strategy.

---

## What You'll Be Able to Do

- Apply prompt-version-aware cache invalidation on top of standard cache-aside and write-through patterns
- Move LLM inference tasks, evaluation jobs, and embedding generation into background queues rather than the HTTP request path
- Design an event ingestion pipeline that survives worker crashes using S3-first durability
- Explain the LLM observability data model (traces / observations / scores) and why it differs from standard APM tracing
- Treat prompts as versioned, labeled configuration artifacts with rollback capability — not anonymous strings
- Decide what belongs in PostgreSQL vs. ClickHouse for an AI backend and explain the workload reasoning
- Configure read replicas and failover for the PostgreSQL metadata store to handle combined application + evaluation write traffic
