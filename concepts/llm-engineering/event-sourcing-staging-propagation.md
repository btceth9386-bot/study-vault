---
id: event-sourcing-staging-propagation
title: Event Sourcing with Staging Propagation
depth: 2
lab_status: not-started
last_reviewed: '2026-05-13'
review_due: '2026-05-16'
sources:
- sources/repos/langfuse-langfuse/
related:
- hierarchical-rbac
tags:
- llm-engineering
- llm
- observability
- tracing
- evaluation
- prompt-management
- open-source
---

# Event Sourcing with Staging Propagation

- **一句話定義**：A write pattern where events land first in short-lived staging tables, then a background propagation job denormalizes and merges them into final analytical tables — separating write durability from read-optimized materialization.
- **為什麼存在 / 解決什麼問題**：OLAP stores like ClickHouse are extremely fast at reading pre-joined, denormalized rows but slow at executing ad-hoc JOINs across large tables. By running a propagation job that joins `observations_batch_staging` with the `traces` table and writes the result into `events_full` (with `user_id`, `session_id`, `tags` inlined), query-time JOINs are eliminated entirely. Staging tables use short TTLs (12 hours) so they don't accumulate indefinitely. A Redis cursor (`LAST_PROCESSED_PARTITION_KEY`) tracks which 3-minute partitions have been propagated, enabling exactly-once processing. This pattern trades write complexity for read simplicity — the downstream benefit is sub-second analytical queries over billions of rows.
- **關鍵字**：llm-engineering, llm, observability, tracing, evaluation, prompt-management, open-source
- **相關概念**：[[hierarchical-rbac]]
- **深度等級**：2/4
- **最後更新**：2026-05-13
- **來源**：langfuse/langfuse

## 摘要

Think of Event Sourcing with Staging Propagation as a design pattern for making agent or backend systems easier to operate. A write pattern where events land first in short-lived staging tables, then a background propagation job denormalizes and merges them into final analytical tables — separating write durability from read-optimized materialization. It matters because the simple version of the system usually works only in demos; production systems need state, boundaries, recovery, and observability. OLAP stores like ClickHouse are extremely fast at reading pre-joined, denormalized rows but slow at executing ad-hoc JOINs across large tables.

## 範例

Suppose an engineering team is turning an agent prototype into a service used every day. Instead of treating Event Sourcing with Staging Propagation as theory, they ask: what breaks if this piece is missing? The answer is visible in the source, **langfuse/langfuse**: OLAP stores like ClickHouse are extremely fast at reading pre-joined, denormalized rows but slow at executing ad-hoc JOINs across large tables. That makes the concept a design check the team can apply before the system reaches production.

## 與既有概念的關聯

- [[hierarchical-rbac]]: event-sourcing-staging-propagation connects to hierarchical-rbac because both describe a nearby part of the same learning path or system design problem.

## 我的疑問

- What examples would make this concept easier to recognize in future sources?
- When would this concept be misleading or too broad?
