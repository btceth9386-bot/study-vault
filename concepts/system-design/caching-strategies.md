---
id: caching-strategies
title: Caching Strategies
depth: 2
last_reviewed: 2026-04-30
review_due: 2026-05-03
sources:
  - sources/repos/system-design-primer
related:
  - cap-theorem
  - async-processing
  - horizontal-scaling
tags:
  - system-design
  - performance
---

# Caching Strategies

- **One-sentence definition**: Storing frequently accessed data in fast memory layers so you don't have to hit the slow database every time, with different update patterns depending on whether you prioritize speed or freshness.
- **Why it exists / what problem it solves**: Databases are slow under hot-spot traffic. A memory read (~100 ns) is orders of magnitude faster than a disk seek (~10 ms). Caching absorbs uneven loads and traffic spikes, but the hard part is keeping cached data in sync with the source of truth.
- **Keywords**: cache-aside, write-through, write-behind, refresh-ahead, Redis, Memcached, TTL, cache invalidation
- **Related concepts**: [[cap-theorem]], [[async-processing]], [[horizontal-scaling]]
- **Depth**: 2/4
- **Last updated**: 2026-04-30
- **Source**: sources/repos/system-design-primer

## Summary

Caches sit at multiple layers: browser → CDN → reverse proxy → application (Redis/Memcached) → database query cache. The closer to the user, the faster.

The key decision is the **update pattern** — how the cache stays in sync with the database:

1. **Cache-aside** (lazy loading): App checks cache first. On miss, reads from DB, writes result to cache. Simple and only caches what's actually requested, but a miss costs 3 round trips and data can go stale.
2. **Write-through**: Every write goes to cache first, then cache synchronously writes to DB. Reads are always fresh, but writes are slower and most cached data may never be read.
3. **Write-behind** (write-back): Writes go to cache, which asynchronously flushes to DB in batches. Fast writes, but if the cache crashes before flushing, data is lost.
4. **Refresh-ahead**: Cache proactively refreshes entries before they expire based on predicted access. Great when predictions are accurate; wasteful when they're not.

## Example

A social media app's user profile page:

- **Cache-aside**: First visitor loads profile from DB (slow), stores in Redis. Next 10,000 visitors get it from Redis in <1ms. After the user updates their bio, the cached version is stale until TTL expires or someone explicitly invalidates it.
- **Write-through**: When the user updates their bio, the app writes to Redis, Redis writes to Postgres synchronously. The next read is guaranteed fresh, but the write took longer.

## Relationship to other concepts

- [[cap-theorem]]: Cache-aside accepts eventual consistency (stale reads); write-through provides stronger consistency at the cost of write latency.
- [[async-processing]]: Write-behind is essentially async processing applied to database writes — same trade-off of speed vs data-loss risk.
- [[horizontal-scaling]]: Caching absorbs uneven traffic that would otherwise overwhelm horizontally scaled servers.

## Open questions

- When is it better to use short TTLs vs explicit cache invalidation on writes?
- How do distributed cache clusters (Redis Cluster) handle cache invalidation across nodes?
