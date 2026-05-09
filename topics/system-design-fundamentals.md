---
id: system-design-fundamentals
title: "System Design Fundamentals: From Single Server to Distributed Systems"
description: A complete grounding in system design — starting from the simplest possible deployment and progressively solving each bottleneck until you understand the full toolkit covering scaling, reliability, data architecture, and distributed systems theory.
---

## Overview

Every production system started simple and grew from there. This path follows that growth story: a single server handles everything, then traffic overwhelms it, then the database becomes the bottleneck, then reliability becomes the priority, and finally you need the theoretical tools to reason about tradeoffs at scale. By studying each concept at the moment it solves a real problem, you build intuition rather than vocabulary alone.

**Estimated study time:** 8–10 hours  
**Prerequisites:** Basic familiarity with web applications (HTTP, databases).

---

## Concepts in Order

### 1. [Vertical Scaling](../concepts/system-design/vertical-scaling.md)
The first instinct when traffic grows: buy a bigger server. Understand what vertical scaling buys you, when it stops being enough, and why it is often the right first move before adding architectural complexity.

### 2. [Horizontal Scaling](../concepts/system-design/horizontal-scaling.md)
When you can no longer buy a bigger machine, add more machines. The fundamental shift in how you think about capacity — and the new problems it introduces: statelessness requirements, coordination overhead, and the need for a traffic distributor.

### 3. [Load Balancing](../concepts/system-design/load-balancing.md)
Horizontal scaling requires something to distribute traffic across instances. Load balancers sit at the entry point and route requests using round-robin, least-connections, or Layer 7 rules. This is the enabling layer for horizontal scale.

### 4. [Sticky Sessions](../concepts/system-design/sticky-sessions.md)
Load balancing breaks server-side session state — a user may land on a different server on each request. Sticky sessions are one solution; shared session stores are another. Understand when each approach is appropriate and why client-side sessions eliminate the problem entirely.

### 5. [Caching Strategies](../concepts/system-design/caching-strategies.md)
Reading from the database on every request is slow and expensive. Caching layers (cache-aside, write-through, write-behind, refresh-ahead) serve frequently-read data from memory at sub-millisecond latency. A key distinction: caching solves read load, not write load.

### 6. [Database Replication](../concepts/system-design/database-replication.md)
When the database becomes the read bottleneck, add read replicas. Master-slave replication routes writes to the primary and reads to replicas. Master-master allows writes to any node but introduces conflict resolution complexity.

### 7. [Database Sharding](../concepts/system-design/database-sharding.md)
When the database becomes the write bottleneck, no amount of replication helps — the data must be partitioned across multiple primaries. Hash-based, range-based, and geographic sharding each solve different problems. Consistent hashing reduces rebalancing cost when adding nodes.

### 8. [RAID Storage](../concepts/system-design/raid-storage.md)
Hardware disks fail. RAID (Redundant Array of Independent Disks) protects data at the storage level: stripe, mirror, or parity-protect data across multiple disks to survive individual drive failures. Understanding RAID 0, 1, 5, 6, and 10 tradeoffs is a prerequisite for designing storage tiers.

### 9. [Single Point of Failure](../concepts/system-design/single-point-of-failure.md)
Any component whose failure brings down the whole system is a single point of failure. Before designing for reliability, you must learn to identify SPOFs in a system topology — load balancer, database primary, DNS server, and power supply are all common examples.

### 10. [High Availability](../concepts/system-design/high-availability.md)
The systematic answer to SPOFs: redundancy and automatic failover. Active-active distributes load and tolerates node failure. Active-passive keeps a standby that takes over when the primary fails. Heartbeats detect failures; health checks trigger failover.

### 11. [SSL Termination](../concepts/system-design/ssl-termination.md)
TLS decryption is computationally expensive. Terminating SSL at the load balancer offloads that work from application servers, centralizes certificate management, and allows the internal network to use unencrypted HTTP — a deliberate tradeoff between performance and defense-in-depth.

### 12. [CAP Theorem](../concepts/system-design/cap-theorem.md)
The theoretical foundation for reasoning about distributed data systems. A distributed system can guarantee at most two of three properties: Consistency, Availability, and Partition tolerance. CAP doesn't give you rules to follow — it gives you a language for the tradeoffs you're already making.

### 13. [Eventual Consistency](../concepts/system-design/eventual-consistency.md)
The consistency model that most large-scale distributed systems actually use. Eventual consistency trades immediate consistency for availability and partition tolerance: all replicas will converge to the same state, but reads may return stale data during the convergence window.

### 14. [Microservices](../concepts/system-design/microservices.md)
When a monolith grows large enough, it becomes a deployment and scaling bottleneck. Microservices decompose a system into independently deployable services. The cost: distributed system complexity — network calls, service discovery, distributed tracing, and consistency challenges between service boundaries.

### 15. [Asynchronous Processing](../concepts/system-design/async-processing.md)
Some work is too slow for the HTTP request-response path. Message queues decouple the caller from the worker: the API accepts the job, enqueues it, and returns immediately. Workers process at their own rate. This pattern enables retry logic, backpressure, and burst absorption — and is the foundation of every reliable event pipeline.

---

## What You'll Be Able to Do

- Trace the architecture evolution from single server to horizontally-scaled distributed system
- Identify single points of failure in a given system topology
- Choose the right replication and sharding strategy for a given data access pattern
- Apply CAP theorem reasoning to evaluate consistency vs. availability tradeoffs in a design
- Design a basic high-availability configuration for a web application
- Decide when a monolith should be decomposed into microservices and at what cost
