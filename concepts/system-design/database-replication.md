---
id: database-replication
title: Database Replication
depth: 2
last_reviewed: 2026-04-30
review_due: 2026-05-03
sources:
  - sources/videos/cs75-summer-2012-lecture-9-scalability-harvard-web-development-david-malan
related:
  - database-sharding
  - eventual-consistency
  - cap-theorem
  - high-availability
tags:
  - system-design
  - databases
---

# Database Replication

- **One-sentence definition**: Automatically copying data from one database server (master) to one or more others so multiple servers hold identical data, enabling read scaling and failover.
- **Why it exists / what problem it solves**: A single database is both a performance bottleneck (all reads and writes hit one machine) and a single point of failure (if it dies, everything stops). Replication solves both.
- **Keywords**: master-slave, master-master, read replica, replication lag, failover, write SPOF
- **Related concepts**: [[database-sharding]], [[eventual-consistency]], [[cap-theorem]], [[high-availability]]
- **Depth**: 2/4
- **Last updated**: 2026-04-30
- **Source**: sources/videos/cs75-summer-2012-lecture-9-scalability-harvard-web-development-david-malan

## Summary

Think of a newspaper editor (master) and several printing presses (slaves). The editor writes the content; the presses produce copies for readers. If one press breaks, the others keep printing. But if the editor is unavailable, no new content gets written.

**Master-slave replication**: One master handles all writes. Slaves receive copies and handle reads. Great for read-heavy workloads (most web apps read far more than they write). Downside: the master is still a single point of failure for writes, and slaves may lag behind (eventual consistency).

**Master-master replication**: Two masters, both accept writes, replicate to each other. If one dies, the other keeps going — no write downtime. Downside: conflict resolution when both masters modify the same row simultaneously, and writes may be loosely consistent.

## Example

Facebook's early architecture (as described in CS75): the vast majority of operations are reads (viewing profiles, feeds). A master-slave setup with one write master and multiple read slaves behind a load balancer handles this well:

1. User updates profile → write goes to master.
2. Master replicates the change to 4 slaves (async, ~milliseconds).
3. User's friend views the profile → read goes to a slave via LB.
4. If the master dies → promote a slave to master (manual or automatic failover).

## Relationship to other concepts

- [[database-sharding]]: Replication copies all data for redundancy; sharding partitions data for capacity. Often used together.
- [[eventual-consistency]]: Async replication means slaves may briefly return stale data — the propagation delay is eventual consistency in action.
- [[cap-theorem]]: Master-slave is CP-leaning (writes fail if master is down); master-master is AP-leaning (both accept writes but may conflict).
- [[high-availability]]: Master-master replication is the database-level implementation of active-active HA.

## Open questions

- How do you handle the "split-brain" problem in master-master replication when both masters accept conflicting writes?
- What's the typical replication lag in production MySQL/PostgreSQL setups, and when does it become a user-visible problem?
