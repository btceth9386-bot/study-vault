---
id: database-sharding
title: Database Sharding
depth: 2
last_reviewed: 2026-04-30
review_due: 2026-05-03
sources:
  - sources/repos/system-design-primer
related:
  - horizontal-scaling
  - cap-theorem
  - database-replication
  - oltp-olap-split
tags:
  - system-design
  - databases
---

# Database Sharding

- **One-sentence definition**: Splitting a database's rows across multiple independent database instances (shards) so each one handles only a slice of the data.
- **Why it exists / what problem it solves**: When a single database can't keep up with read/write volume or data size — even after adding read replicas and caching — sharding distributes the load across multiple machines, each with smaller indexes and better cache hit rates.
- **Keywords**: horizontal partitioning, shard key, hash-based sharding, geographic sharding, consistent hashing, denormalization, federation
- **Related concepts**: [[horizontal-scaling]], [[cap-theorem]], [[oltp-olap-split]]
- **Depth**: 2/4
- **Last updated**: 2026-04-30
- **Source**: sources/repos/system-design-primer

## Summary

Imagine a library with one giant card catalog. As the collection grows, searching gets slow. Sharding is like splitting the catalog into A–M and N–Z, each in its own cabinet — lookups are faster because you search a smaller set.

Common sharding strategies:
- **Hash-based**: `shard = hash(user_id) % num_shards` — even distribution but hard to do range queries.
- **Geographic**: US users → US shard, EU users → EU shard — lower latency but uneven load.
- **Consistent hashing**: Minimizes data movement when adding/removing shards.

The trade-offs are real: your application must know which shard to query (routing logic), cross-shard JOINs are painful or impossible (often solved with denormalization), data can become lopsided (power users on one shard), and rebalancing is complex. **Federation** (splitting by function — users DB, orders DB, products DB) is a simpler alternative when tables are naturally independent.

## Example

A chat app with 100M users shards by `user_id % 4`:

| Shard | Users | Data |
|-------|-------|------|
| 0 | user_id % 4 == 0 | Messages, profiles for those users |
| 1 | user_id % 4 == 1 | ... |
| 2 | user_id % 4 == 2 | ... |
| 3 | user_id % 4 == 3 | ... |

Fetching one user's messages hits exactly one shard. But "find all messages containing keyword X across all users" requires a scatter-gather query to all 4 shards.

## Relationship to other concepts

- [[horizontal-scaling]]: Sharding is horizontal scaling applied to the data layer.
- [[cap-theorem]]: Sharding inherently introduces partitions across nodes, forcing the consistency vs availability trade-off.
- [[oltp-olap-split]]: Sharding divides one database workload across nodes; an OLTP/OLAP split separates transactional and analytical workloads into different systems.

## Open questions

- How do you handle shard rebalancing in production without downtime?
- When should you choose federation (functional partitioning) over sharding (horizontal partitioning)?
