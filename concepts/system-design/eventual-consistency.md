---
id: eventual-consistency
title: Eventual Consistency
depth: 2
last_reviewed: 2026-04-30
review_due: 2026-05-03
sources:
  - sources/repos/system-design-primer
related:
  - cap-theorem
  - caching-strategies
  - async-processing
tags:
  - system-design
  - distributed-systems
---

# Eventual Consistency

- **One-sentence definition**: After a write, all replicas will converge to the same value given enough time, but reads during the propagation window may return stale data.
- **Why it exists / what problem it solves**: Strong consistency requires every replica to confirm a write before responding, which is slow and reduces availability. Eventual consistency trades immediate accuracy for speed and uptime — the right choice when brief staleness is acceptable.
- **Keywords**: eventual consistency, strong consistency, weak consistency, AP, BASE, replication lag, propagation window
- **Related concepts**: [[cap-theorem]], [[caching-strategies]], [[async-processing]]
- **Depth**: 2/4
- **Last updated**: 2026-04-30
- **Source**: sources/repos/system-design-primer

## Summary

When you post a photo on social media, your friend in another country might not see it for a few seconds. That's eventual consistency — the data is replicating asynchronously across servers, and different users may briefly see different versions.

There are three consistency levels:
- **Strong**: After a write, every read sees it immediately. Used in banking (RDBMS with ACID). Slowest.
- **Eventual**: After a write, reads *will* see it — typically within milliseconds. Used in DNS, email, Cassandra, DynamoDB. Fast and highly available.
- **Weak**: After a write, reads *may or may not* see it. Best-effort only. Used in memcached, VoIP, live video. Fastest.

Eventual consistency is formalized in the **BASE** model (Basically Available, Soft state, Eventual consistency), which contrasts with ACID. It's the natural result of choosing availability over consistency in the CAP theorem.

## Example

DNS propagation is a classic example. You update your domain's A record from IP `1.2.3.4` to `5.6.7.8`:

1. Your authoritative DNS server has the new IP immediately.
2. Your ISP's caching resolver still has the old IP (TTL hasn't expired).
3. A user in Japan queries a different resolver that also has the old cached value.
4. Over the next few minutes to hours (depending on TTL), all resolvers expire their caches and fetch the new value.
5. Eventually, every DNS resolver worldwide returns `5.6.7.8`.

During the propagation window, some users reach the old server and some reach the new one.

## Relationship to other concepts

- [[cap-theorem]]: Eventual consistency is what you get when you choose AP (availability + partition tolerance) over CP.
- [[caching-strategies]]: Cache-aside naturally produces eventual consistency — the cache may hold stale data until TTL expires or it's explicitly invalidated.
- [[async-processing]]: Async workers introduce propagation delay by design — the result isn't available until the worker finishes.

## Open questions

- How do you design UIs that feel consistent to the user who just made a write (read-your-own-writes) while the backend is eventually consistent?
- What's the practical difference between "eventual consistency within milliseconds" (Cassandra) vs "eventual consistency within hours" (DNS)?
