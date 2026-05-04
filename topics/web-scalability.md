---
id: web-scalability
title: "Web Scalability: From Single Server to Production"
description: A practical, chronological journey through every decision a team faces when their web application outgrows a single machine — from the first hardware upgrade to a fully redundant multi-tier architecture.
---

## Overview

This path follows the natural growth arc of a successful web application. Each concept appears at the moment you would actually need it: vertical scaling comes first because it requires no architectural change, horizontal scaling comes when vertical hits its ceiling, and high availability comes last because it only makes sense after the other layers are solid. The through-line is the "fix one problem, expose the next" pattern — each solution introduces a new single point of failure that the following concept addresses.

**Estimated study time:** 6–8 hours  
**Prerequisites:** Basic familiarity with how HTTP and databases work.

---

## Concepts in Order

### 1. [Vertical Scaling](../concepts/system-design/vertical-scaling.md)
The default first move: upgrade CPU, RAM, and disks on one machine. Understand this first because it is always the simplest option — and understanding *why* it runs out of runway is what motivates everything that follows.

### 2. [Horizontal Scaling](../concepts/system-design/horizontal-scaling.md)
When vertical hits the ceiling, add more machines. This step introduces the core requirement for everything downstream: servers must be **stateless**. If a server holds any local state, requests can't freely roam across the fleet.

### 3. [Load Balancing](../concepts/system-design/load-balancing.md)
With multiple servers, you need something to distribute traffic. Covers round-robin vs. least-connections, Layer 4 vs. Layer 7, health checks, and how SSL termination fits into this layer.

### 4. [Sticky Sessions](../concepts/system-design/sticky-sessions.md)
The first practical problem that emerges from load balancing: PHP sessions (and any server-local state) break when requests bounce between machines. Study the three solutions — LB cookies, shared session stores, client-side sessions — and understand why externalizing state to Redis is the correct long-term answer.

### 5. [Caching Strategies](../concepts/system-design/caching-strategies.md)
Databases become the new bottleneck once horizontal scaling absorbs the request-per-second problem. Cache-aside, write-through, write-behind, and refresh-ahead are the four patterns. Understanding write-through vs. write-behind sets up the consistency trade-offs covered in the distributed systems path.

### 6. [Database Replication](../concepts/system-design/database-replication.md)
Scale database reads and add a failover target. Master-slave is the right choice for read-heavy web apps; master-master eliminates the write single point of failure at the cost of conflict resolution complexity.

### 7. [Database Sharding](../concepts/system-design/database-sharding.md)
When even a replicated database can't keep up with write volume or data size, split the rows across independent instances. Covers hash-based, geographic, and consistent hashing strategies — and the trade-offs (cross-shard JOINs, routing logic, rebalancing).

### 8. [RAID Storage](../concepts/system-design/raid-storage.md)
Disk-level redundancy within each server node. RAID sits below the application layer — it protects against hardware failure without any code changes. Study RAID 1, 5, 10 for databases; understand why RAID 0 belongs only in read-only or scratch workloads.

### 9. [Single Point of Failure](../concepts/system-design/single-point-of-failure.md)
A design discipline, not a technology. After adding each layer above, ask: "what can die next and bring everything down?" This concept names that question and provides a systematic way to answer it across every tier: servers, load balancers, databases, switches, power, data center.

### 10. [High Availability](../concepts/system-design/high-availability.md)
The answer to every SPOF found in the previous step. Active-active and active-passive configurations, heartbeat monitoring, automatic failover, and how this pattern scales from LB pairs to multi-AZ deployments.

### 11. [SSL Termination](../concepts/system-design/ssl-termination.md)
The final operational concern: centralizing certificate management and crypto overhead at the load balancer layer. A natural conclusion because you need the load balancer (step 3) and high-availability LB pairs (step 10) in place before this decision makes full sense.

---

## What You'll Be Able to Do

- Trace the complete scaling journey and explain *why* each step comes when it does
- Identify every SPOF in a multi-tier architecture diagram
- Choose the right caching pattern given consistency and latency requirements
- Decide between replication and sharding for a given database workload
- Design a load balancer configuration with session affinity and SSL termination
