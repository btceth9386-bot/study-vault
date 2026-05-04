---
id: oltp-olap-split
title: OLTP/OLAP Database Split
depth: 2
last_reviewed: 2026-05-04
review_due: 2026-05-07
sources:
  - sources/repos/langfuse-langfuse
related:
  - llm-observability
  - database-sharding
  - async-processing
tags:
  - databases
  - analytics
  - architecture
---

# OLTP/OLAP Database Split

- **One-sentence definition**: An OLTP/OLAP split uses one database for transactional application state and another database for large analytical queries.
- **Why it exists / what problem it solves**: A product database and an analytics database are optimized for different jobs. User accounts, projects, API keys, and prompt metadata need relational integrity and fast point writes. Millions or billions of trace events need fast filtering, grouping, and aggregation.
- **Keywords**: OLTP, OLAP, PostgreSQL, ClickHouse, analytics, transactional metadata
- **Related concepts**: [[llm-observability]], [[database-sharding]], [[async-processing]]
- **Depth**: 2/4
- **Last updated**: 2026-05-04
- **Source**: sources/repos/langfuse-langfuse

## Summary

OLTP means "online transaction processing": small, precise operations like creating a user, updating a project, or checking an API key. OLAP means "online analytical processing": large scans and aggregations like "average latency by model over the last 30 days." Trying to force both workloads into one database usually makes one side suffer.

Langfuse uses PostgreSQL for relational metadata and configuration, while ClickHouse stores high-volume observability data such as traces, observations, scores, and events. PostgreSQL is good at consistency and relationships. ClickHouse is good at scanning columns and aggregating huge datasets quickly. The cost is extra operational complexity: the application must know where each type of data belongs and how to join meaning across systems.

## Example

In an LLM monitoring product:

- PostgreSQL stores `Project`, `User`, `ApiKey`, `Prompt`, and evaluator configuration records.
- ClickHouse stores millions of generation events with model name, tokens, latency, cost, and score fields.

When a dashboard asks "Which model had the highest average latency this week?", ClickHouse can answer by scanning analytical columns. When a user changes a project setting, PostgreSQL handles the transaction safely.

## Relationship to existing concepts

- [[llm-observability]]: Observability produces the high-volume event data that makes analytical storage necessary.
- [[database-sharding]]: Sharding splits one workload horizontally; OLTP/OLAP splitting separates fundamentally different workloads.
- [[async-processing]]: Background workers often bridge the split by moving validated events into the analytical store.

## Open questions

- Which data should be duplicated into the analytical store for faster reads?
- How should a system handle consistency lag between the transactional and analytical stores?
