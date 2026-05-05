---
id: microservices
title: Microservices Architecture
depth: 2
last_reviewed: 2026-04-30
review_due: 2026-05-03
sources:
  - sources/repos/system-design-primer
related:
  - horizontal-scaling
  - load-balancing
  - async-processing
  - eventual-consistency
  - langgraph-remotegraph-server-execution
tags:
  - system-design
  - architecture
---

# Microservices Architecture

- **One-sentence definition**: Breaking a big application into small, independent services that each do one thing, deploy separately, and talk to each other over the network.
- **Why it exists / what problem it solves**: In a monolith, one team's change can break everything, scaling means scaling the whole app, and a single bug can take down the entire system. Microservices let teams own, deploy, and scale their piece independently.
- **Keywords**: microservices, monolith, service discovery, independent deployment, fault isolation, distributed complexity
- **Related concepts**: [[horizontal-scaling]], [[load-balancing]], [[async-processing]], [[eventual-consistency]], [[langgraph-remotegraph-server-execution]]
- **Depth**: 2/4
- **Last updated**: 2026-04-30
- **Source**: sources/repos/system-design-primer

## Summary

A monolith is like one giant kitchen where every chef shares the same stove, fridge, and counter. If the dishwasher breaks, nobody can cook. Microservices split this into separate food stations — sushi bar, grill, salad prep — each with its own equipment and staff. One station going down doesn't stop the others.

Each microservice runs its own process, owns its own data store, and communicates via lightweight protocols (HTTP/REST for external APIs, RPC for internal calls, message queues for async work). A **service discovery** system (Consul, Etcd, Zookeeper) keeps track of where each service instance lives as they scale up and down.

The trade-offs are significant: network calls replace in-process function calls (slower, can fail), there are no cross-service ACID transactions (you must accept eventual consistency), and you need distributed logging, tracing, and monitoring to debug issues that span multiple services. Microservices make sense for large organizations with multiple teams; for a small team, a monolith is usually simpler and faster to develop.

## Example

Pinterest's architecture decomposed into microservices:
- **User Profile Service** — manages accounts and profile data
- **Follower Service** — tracks who follows whom
- **Feed Service** — generates the home feed by calling User and Follower services
- **Search Service** — indexes and searches pins
- **Photo Upload Service** — handles image upload, resizing, storage

Each service scales independently: the Feed Service might need 50 instances during peak hours while the Photo Upload Service needs only 10. If Search goes down, users can still browse their feed.

## Relationship to other concepts

- [[horizontal-scaling]]: Each microservice scales out independently based on its own load profile.
- [[load-balancing]]: Each service sits behind its own load balancer to distribute traffic across instances.
- [[async-processing]]: Services communicate asynchronously via message queues to avoid tight coupling and blocking calls.
- [[eventual-consistency]]: Without cross-service transactions, data consistency between services is eventual by nature.
- [[langgraph-remotegraph-server-execution]]: A deployed LangGraph can act as a service boundary while still exposing graph-native operations.

## Open questions

- What's the right granularity for a microservice — how small is too small?
- How do you handle distributed transactions that span multiple services (saga pattern, two-phase commit)?
