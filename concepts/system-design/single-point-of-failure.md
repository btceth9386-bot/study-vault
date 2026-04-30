---
id: single-point-of-failure
title: Single Point of Failure
depth: 2
last_reviewed: 2026-04-30
review_due: 2026-05-03
sources:
  - sources/videos/cs75-summer-2012-lecture-9-scalability-harvard-web-development-david-malan
related:
  - high-availability
  - load-balancing
  - database-replication
tags:
  - system-design
  - reliability
---

# Single Point of Failure

- **One-sentence definition**: Any component whose failure alone would take down the entire system — the weakest link that makes all other redundancy pointless.
- **Why it exists / what problem it solves**: SPOF analysis is a thinking discipline, not a technology. Every time you solve one scaling problem, you risk creating a new SPOF. Identifying them is the first step to building resilient systems.
- **Keywords**: SPOF, redundancy, failover, resilience, fault tolerance
- **Related concepts**: [[high-availability]], [[load-balancing]], [[database-replication]]
- **Depth**: 2/4
- **Last updated**: 2026-04-30
- **Source**: sources/videos/cs75-summer-2012-lecture-9-scalability-harvard-web-development-david-malan

## Summary

A chain is only as strong as its weakest link. In system design, a SPOF is that link. The tricky part: fixing one SPOF often creates another.

You have one web server — it's a SPOF. You add a second behind a load balancer — now the load balancer is the SPOF. You add a second load balancer — now the network switch connecting them might be the SPOF. You add redundant switches — now the data center itself is the SPOF. You add a second data center...

The discipline is to keep asking "what can die next?" at every layer: servers, load balancers, databases, network gear, power supplies, entire buildings. The answer is always redundancy — but each layer of redundancy adds cost and complexity.

## Example

Tracing SPOFs through a typical web stack:

| Layer | SPOF | Fix |
|-------|------|-----|
| Web server | Single server | Add servers + load balancer |
| Load balancer | Single LB | Active-passive LB pair |
| Session storage | Single Redis | Redis with replica + failover |
| Database | Single master | Master-master replication |
| Data center | Single building | Multi-AZ / multi-region deployment |

Each row's "fix" eliminates that SPOF but the next row reveals the new one.

## Relationship to other concepts

- [[high-availability]]: HA is the solution pattern for SPOFs — redundant pairs with automatic failover.
- [[load-balancing]]: A single load balancer is itself a SPOF; production deployments use LB pairs.
- [[database-replication]]: Eliminates the database as a SPOF via master-slave or master-master setups.

## Open questions

- How do you prioritize which SPOFs to fix first when budget is limited?
- Can a system ever be truly free of SPOFs, or is there always a "last SPOF" (e.g., DNS root servers, cloud provider outage)?
