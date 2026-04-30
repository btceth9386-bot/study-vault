---
id: high-availability
title: High Availability
depth: 2
last_reviewed: 2026-04-30
review_due: 2026-05-03
sources:
  - sources/videos/cs75-summer-2012-lecture-9-scalability-harvard-web-development-david-malan
related:
  - single-point-of-failure
  - load-balancing
  - database-replication
  - raid-storage
tags:
  - system-design
  - reliability
---

# High Availability

- **One-sentence definition**: Designing every layer of a system with redundant pairs and automatic failover so the service stays up even when individual components die.
- **Why it exists / what problem it solves**: Redundant servers are useless if the single load balancer in front of them dies. HA ensures that no single component failure takes down the system, at every layer from disks to data centers.
- **Keywords**: high availability, active-active, active-passive, heartbeat, failover, redundancy, availability zones
- **Related concepts**: [[single-point-of-failure]], [[load-balancing]], [[database-replication]], [[raid-storage]]
- **Depth**: 2/4
- **Last updated**: 2026-04-30
- **Source**: sources/videos/cs75-summer-2012-lecture-9-scalability-harvard-web-development-david-malan

## Summary

HA is the answer to every single point of failure. The pattern is always the same: take the component that can fail, duplicate it, and add automatic switchover.

Two configurations:
- **Active-active**: Both units handle traffic simultaneously. If one dies, the other absorbs its share. More efficient (both units work all the time) but more complex (both must stay in sync). Example: master-master database replication.
- **Active-passive**: One unit handles traffic while the other sits on standby, monitoring via heartbeat packets. When the heartbeat stops, the passive unit promotes itself. Simpler but wastes the standby's capacity during normal operation. Example: a standby load balancer.

This pattern applies at every layer: load balancer pairs, database replicas, redundant network switches, dual power supplies, and even multiple data centers (AWS availability zones and regions).

## Example

An HA load balancer setup:
1. Two HAProxy instances: LB-A (active) and LB-B (passive).
2. LB-B sends heartbeat pings to LB-A every second.
3. LB-A handles all traffic, forwarding to the backend server pool.
4. LB-A's process crashes → LB-B detects 3 missed heartbeats → LB-B takes over LB-A's virtual IP address → traffic flows to LB-B within seconds.
5. LB-A is repaired and comes back as the new passive.

Users experience at most a few seconds of disruption instead of a full outage.

## Relationship to other concepts

- [[single-point-of-failure]]: HA is the direct solution to SPOFs — every SPOF is fixed by adding a redundant pair with failover.
- [[load-balancing]]: Production load balancers are deployed in HA pairs (active-passive or active-active).
- [[database-replication]]: Master-master replication is active-active HA for databases.
- [[raid-storage]]: RAID provides HA at the disk level within a single machine.

## Open questions

- What's the real-world difference in downtime between active-active and active-passive configurations?
- How do cloud availability zones change the HA calculus compared to managing your own redundant hardware?
