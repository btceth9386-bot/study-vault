---
id: cap-theorem
title: CAP Theorem
depth: 2
last_reviewed: 2026-04-30
review_due: 2026-05-03
sources:
  - sources/repos/system-design-primer
related:
  - eventual-consistency
  - database-sharding
  - caching-strategies
  - database-replication
tags:
  - system-design
  - distributed-systems
---

# CAP Theorem

- **One-sentence definition**: In a distributed system, when a network partition happens you must choose between consistency (every read gets the latest write) and availability (every request gets a response).
- **Why it exists / what problem it solves**: Distributed systems spread data across multiple machines, and networks between them can fail. CAP forces you to consciously decide what your system does during a failure instead of hoping for the best.
- **Keywords**: CAP, consistency, availability, partition tolerance, CP, AP, ACID, BASE
- **Related concepts**: [[eventual-consistency]], [[database-sharding]], [[caching-strategies]]
- **Depth**: 2/4
- **Last updated**: 2026-04-30
- **Source**: sources/repos/system-design-primer

## Summary

Think of two bank branches that share an account ledger. If the phone line between them goes down (a "partition"), they have two choices: (1) stop processing transactions until the line is restored — that's choosing **consistency** over availability (CP), or (2) keep processing independently and reconcile later — that's choosing **availability** over consistency (AP).

The CAP theorem says you can't avoid this choice. Network partitions are a fact of life, so the real decision is: do you want every read to be accurate (CP), or do you want the system to always respond even if the data might be slightly stale (AP)?

**CP systems** (e.g., traditional RDBMS with ACID transactions) are used where correctness is critical — banking, inventory. **AP systems** (e.g., Cassandra, DynamoDB, DNS) are used where uptime matters more than perfect freshness — social feeds, product catalogs. AP systems follow the BASE model: Basically Available, Soft state, Eventual consistency.

## Example

An e-commerce site tracks inventory. Two data centers each have a copy of the stock count.

- **CP choice**: When a network partition occurs between data centers, the system returns errors for stock queries rather than risk selling an item that's already sold. Users see "temporarily unavailable" but never get oversold.
- **AP choice**: Both data centers keep accepting orders independently. When the partition heals, they reconcile — but two customers may have bought the last item. The system stays up but risks inconsistency.

## Relationship to other concepts

- [[eventual-consistency]]: The consistency model that AP systems adopt — reads converge over time but may be stale during propagation.
- [[database-sharding]]: Sharding distributes data across nodes, inherently introducing partition risk and forcing CAP trade-offs.
- [[caching-strategies]]: Cache-aside reads can return stale data (eventual consistency); write-through maintains stronger consistency at the cost of write latency.

## Open questions

- How do systems like Google Spanner claim to offer "effectively CP with high availability" — what engineering tricks bend the CAP constraints?
- In practice, how often do real network partitions occur within a single cloud region vs across regions?
