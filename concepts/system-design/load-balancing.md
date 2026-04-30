---
id: load-balancing
title: Load Balancing
depth: 2
last_reviewed: 2026-04-30
review_due: 2026-05-03
sources:
  - sources/repos/system-design-primer
related:
  - horizontal-scaling
  - microservices
  - sticky-sessions
  - single-point-of-failure
  - high-availability
  - ssl-termination
tags:
  - system-design
  - scalability
  - infrastructure
---

# Load Balancing

- **One-sentence definition**: A load balancer sits between clients and a group of servers, forwarding each request to a healthy server so no single machine gets overwhelmed and there's no single point of failure.
- **Why it exists / what problem it solves**: One server can only handle so much traffic, and if it dies everything goes down. A load balancer spreads requests across multiple servers, checks which ones are healthy, and can handle SSL encryption so backend servers don't have to.
- **Keywords**: load balancer, Layer 4, Layer 7, health check, horizontal scaling, HAProxy, NGINX
- **Related concepts**: [[horizontal-scaling]]
- **Depth**: 2/4
- **Last updated**: 2026-04-30
- **Source**: sources/repos/system-design-primer

## Summary

Imagine a restaurant with one cashier — when the line gets long, everyone waits. Add three cashiers and a host who directs customers to whichever register is free, and the line moves much faster. A load balancer is that host.

It distributes incoming network requests across a pool of backend servers using algorithms like round-robin (take turns), least connections (pick the least busy), or weighted routing (send more to stronger machines). It continuously pings servers with health checks and stops sending traffic to any that fail.

There are two main flavors. A **Layer 4** load balancer works at the transport level — it looks only at IP addresses and ports, then forwards packets via NAT. It's fast and simple. A **Layer 7** load balancer works at the application level — it can read HTTP headers, cookies, and URL paths, then make smarter routing decisions like sending `/api/video` requests to video-optimized servers and `/api/billing` to security-hardened ones.

Load balancers also handle **SSL termination** (decrypting HTTPS so backend servers deal only with plain HTTP) and **session persistence** (using cookies to keep a user's requests going to the same server when needed).

## Example

A web app runs on 3 identical servers behind an Application Load Balancer (ALB) on AWS:

1. User sends `GET /dashboard` → ALB receives the request.
2. ALB checks health: Server A ✅, Server B ✅, Server C ❌ (failed health check 10s ago).
3. ALB picks Server A (least active connections) and forwards the request.
4. Server A responds → ALB relays the response to the user.
5. Server C recovers, passes the next health check, and starts receiving traffic again.

If the ALB itself needs redundancy, you deploy two in an **active-passive** pair — one handles traffic while the other monitors via heartbeat and takes over if the primary fails.

## Relationship to other concepts

- [[horizontal-scaling]]: Load balancing is the mechanism that makes horizontal scaling work — without it, there's no way to distribute traffic across the added machines.
- [[microservices]]: Each microservice sits behind its own load balancer to distribute traffic across its instances.

## Open questions

- When does Layer 7 inspection overhead become a real bottleneck vs the routing flexibility it provides?
- How do modern service meshes (Envoy, Istio) change the role of traditional load balancers?
