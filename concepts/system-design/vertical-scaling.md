---
id: vertical-scaling
title: Vertical Scaling
depth: 2
last_reviewed: 2026-04-30
review_due: 2026-05-03
sources:
  - sources/videos/cs75-summer-2012-lecture-9-scalability-harvard-web-development-david-malan
related:
  - horizontal-scaling
  - database-replication
tags:
  - system-design
  - scalability
---

# Vertical Scaling

- **One-sentence definition**: Making a single machine more powerful — more RAM, faster CPUs, better disks — instead of adding more machines.
- **Why it exists / what problem it solves**: When your server is slow, the simplest fix is upgrading its hardware. No code changes, no architectural redesign. But there's a ceiling: the biggest machine money can buy still has limits, and costs grow exponentially near the top.
- **Keywords**: scale up, vertical scaling, SAS, SSD, hardware ceiling, single machine
- **Related concepts**: [[horizontal-scaling]], [[database-replication]]
- **Depth**: 2/4
- **Last updated**: 2026-04-30
- **Source**: sources/videos/cs75-summer-2012-lecture-9-scalability-harvard-web-development-david-malan

## Summary

Vertical scaling is like moving from a compact car to a truck — you carry more, but there's a biggest truck that exists. At some point you need a fleet of cars instead (horizontal scaling).

Typical vertical upgrades include swapping HDDs for SSDs, adding RAM so more data fits in memory, or upgrading to faster CPUs. For databases, moving from 7200 RPM SATA drives to 15K RPM SAS drives or SSDs can dramatically reduce query latency. It's the right first move because it's simple and fast — but it's always a temporary fix.

## Example

A MySQL database on a `db.t3.medium` (2 vCPU, 4 GB RAM) starts hitting slow queries as the dataset grows. Vertical scaling path:
1. Upgrade to `db.r5.xlarge` (4 vCPU, 32 GB RAM) — dataset fits in memory, queries speed up.
2. Later upgrade to `db.r5.4xlarge` (16 vCPU, 128 GB RAM) — buys another 6 months.
3. `db.r5.24xlarge` is the ceiling. After that, you need read replicas (database-replication) or sharding.

## Relationship to other concepts

- [[horizontal-scaling]]: The alternative when vertical scaling hits its ceiling. Together they form the two fundamental scaling strategies.
- [[database-replication]]: Once you can't make the database server bigger, you add read replicas to distribute read load.

## Open questions

- At what cost ratio does vertical scaling stop making sense vs horizontal scaling for a typical web app?
- How do cloud providers' instance families (compute-optimized, memory-optimized, storage-optimized) map to different vertical scaling bottlenecks?
