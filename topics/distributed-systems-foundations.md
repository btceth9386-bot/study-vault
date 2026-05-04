---
id: distributed-systems-foundations
title: "Distributed Systems Foundations: Consistency, Messaging, and Architecture"
description: The theoretical and architectural principles behind systems that span multiple machines — covering the fundamental trade-offs, messaging patterns, and decomposition strategies that every distributed system must confront.
---

## Overview

This path starts with the theoretical constraint that governs all distributed systems (CAP), then works through the practical consequences (eventual consistency, async messaging), the architectural style that maximizes those properties (microservices), and finally the data architecture decisions that make it all hold together at scale. Unlike the Web Scalability path — which follows a chronological growth story — this path builds a mental framework for reasoning about *any* distributed system, including ones you didn't build yourself.

**Estimated study time:** 5–6 hours  
**Prerequisites:** Comfortable reading about databases and network communication. The Web Scalability path is useful but not required.

---

## Concepts in Order

### 1. [CAP Theorem](../concepts/system-design/cap-theorem.md)
The foundation. All distributed systems must decide what to do when a network partition isolates their nodes. The theorem proves you cannot simultaneously guarantee consistency and availability under partition. Study this first because it gives you the vocabulary — CP vs. AP, ACID vs. BASE — that every subsequent concept refers back to.

### 2. [Eventual Consistency](../concepts/system-design/eventual-consistency.md)
The direct consequence of choosing availability in CAP. Replicas will converge, but reads during the propagation window may return stale data. Covers the three levels (strong, eventual, weak), the BASE model, and DNS propagation as the canonical example. After this, you understand *why* NoSQL databases (Cassandra, DynamoDB) make the trade-offs they do.

### 3. [Asynchronous Processing](../concepts/system-design/async-processing.md)
The primary tool for building eventually consistent, resilient systems. Message queues decouple the "accept the request" step from "do the work," enabling independent scaling of producers and consumers. Covers BullMQ/SQS/RabbitMQ patterns, back pressure, exponential backoff, and dead letter queues. Study before microservices because async messaging is what makes inter-service communication reliable.

### 4. [Microservices](../concepts/system-design/microservices.md)
The architectural style that applies the distributed systems trade-offs intentionally — decomposing a monolith into independently deployable services, each owning its own data store. Critically: without the async-processing and eventual-consistency concepts, microservices look like a solution; with them, you can see the cost clearly (no cross-service transactions, debugging spans multiple services, each network call can fail).

### 5. [Database Replication](../concepts/system-design/database-replication.md)
How data stays consistent across nodes when writes happen. Revisit replication here from the distributed systems angle: propagation lag is a form of eventual consistency, master-slave is a CP choice (writes block until the master commits), and master-master requires conflict resolution that is fundamentally an AP trade-off. The CAP and eventual-consistency concepts make these choices legible.

### 6. [Database Sharding](../concepts/system-design/database-sharding.md)
How data is partitioned across independent nodes when a single database — even a replicated one — can't hold the load. Covers hash-based, geographic, and consistent hashing strategies. Cross-shard JOINs are painful because partitions are essentially independent CP subsystems. Study after replication because sharding is the next step when replication alone isn't enough.

### 7. [OLTP/OLAP Database Split](../concepts/llm-engineering/oltp-olap-split.md)
A different kind of database distribution: choosing different database technologies for different *workload profiles* rather than splitting by data range. PostgreSQL for relational, transactional metadata; ClickHouse or BigQuery for high-volume analytical queries. This is not sharding — it's workload-appropriate database selection. A natural capstone for this path because it requires understanding both what OLTP systems (covered throughout) and OLAP systems optimize for, and why you can't force both onto the same engine.

---

## What You'll Be Able to Do

- Apply the CAP theorem to explain the design decisions in any distributed database (Cassandra, DynamoDB, Postgres, Redis)
- Reason about what "eventual consistency" means in a specific system and whether it's acceptable for a given use case
- Design an async processing pipeline with correct error handling, back pressure, and retry logic
- Articulate the real costs of microservices (not just the benefits) and when a monolith is the right choice
- Choose between replication, sharding, and OLTP/OLAP split for a given data scaling problem
