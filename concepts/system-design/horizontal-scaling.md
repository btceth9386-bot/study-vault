---
id: horizontal-scaling
title: Horizontal Scaling
depth: 2
last_reviewed: 2026-04-30
review_due: 2026-05-03
sources:
  - sources/repos/system-design-primer
related:
  - load-balancing
  - database-sharding
  - microservices
tags:
  - system-design
  - scalability
---

# Horizontal Scaling

- **One-sentence definition**: Adding more machines to share the work instead of making one machine bigger.
- **Why it exists / what problem it solves**: A single server has a hard ceiling on CPU, RAM, and disk. Upgrading it (vertical scaling) gets exponentially expensive and still has a max. Horizontal scaling sidesteps this by spreading load across many cheap commodity machines.
- **Keywords**: scale out, stateless, session externalization, commodity hardware, vertical scaling
- **Related concepts**: [[load-balancing]], [[database-sharding]], [[microservices]]
- **Depth**: 2/4
- **Last updated**: 2026-04-30
- **Source**: sources/repos/system-design-primer

## Summary

Vertical scaling is like replacing your sedan with a sports car — faster, but there's a fastest car money can buy. Horizontal scaling is like adding more sedans and splitting passengers across them — you can keep adding cars.

The catch: every server must be **stateless**. If Server A stores a user's shopping cart in local memory and the next request lands on Server B, the cart is gone. So you move session data to a shared store like Redis or Memcached. Now any server can handle any request.

You also need a **load balancer** in front to distribute traffic, and your downstream systems (databases, caches) must handle the increased connection count from all those extra servers.

## Example

A startup's API runs on one EC2 `m5.xlarge`. Traffic doubles after a product launch:

1. **Vertical approach**: Upgrade to `m5.4xlarge` (4× cost, still one machine, still a single point of failure).
2. **Horizontal approach**: Keep the `m5.xlarge`, add two more behind an ALB. Move sessions to ElastiCache Redis. Total cost ~3× but now any instance can die without downtime.

The horizontal path also sets up the next scaling steps: read replicas, sharding, CDN, multi-region.

## Relationship to other concepts

- [[load-balancing]]: The mechanism that distributes traffic across horizontally scaled servers.
- [[database-sharding]]: Extends horizontal scaling to the data layer when a single DB becomes the bottleneck.
- [[microservices]]: Applies horizontal scaling at the application layer — each service scales independently.

## Open questions

- At what traffic level does horizontal scaling's operational complexity (deployment, monitoring N instances) outweigh vertical scaling's simplicity?
- How do stateful workloads (e.g., WebSocket connections, in-memory game state) adapt to horizontal scaling?
