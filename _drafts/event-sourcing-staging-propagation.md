---
id: event-sourcing-staging-propagation
title: Event Sourcing with Staging Propagation
source: sources/repos/langfuse-langfuse
status: draft
created_at: 2026-05-04
---

- **One-sentence definition**: A write pattern where events land first in short-lived staging tables, then a background propagation job denormalizes and merges them into final analytical tables — separating write durability from read-optimized materialization.
- **Why it matters**: OLAP stores like ClickHouse are extremely fast at reading pre-joined, denormalized rows but slow at executing ad-hoc JOINs across large tables. By running a propagation job that joins `observations_batch_staging` with the `traces` table and writes the result into `events_full` (with `user_id`, `session_id`, `tags` inlined), query-time JOINs are eliminated entirely. Staging tables use short TTLs (12 hours) so they don't accumulate indefinitely. A Redis cursor (`LAST_PROCESSED_PARTITION_KEY`) tracks which 3-minute partitions have been propagated, enabling exactly-once processing. This pattern trades write complexity for read simplicity — the downstream benefit is sub-second analytical queries over billions of rows.
- **Relationship to other concepts**: This is a concrete implementation of the event-sourcing architectural style applied to OLAP systems. It is the bridge between the async-processing pipeline (events arrive asynchronously) and the oltp-olap-split (final tables in ClickHouse). The Redis cursor is a form of distributed state management, connecting to high-availability concerns. The staging TTL relates to eventual-consistency — during the propagation window, newly ingested events are not yet visible in final tables.
