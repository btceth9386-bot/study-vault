---
id: sticky-sessions
title: Sticky Sessions
depth: 2
last_reviewed: 2026-04-30
review_due: 2026-05-03
sources:
  - sources/videos/cs75-summer-2012-lecture-9-scalability-harvard-web-development-david-malan
related:
  - load-balancing
  - horizontal-scaling
  - caching-strategies
tags:
  - system-design
  - scalability
---

# Sticky Sessions

- **One-sentence definition**: Routing all of a user's requests to the same backend server so that server-side session data (login state, shopping cart) isn't lost when requests cross a load-balanced cluster.
- **Why it exists / what problem it solves**: When you add multiple servers behind a load balancer, session data stored locally on one server is invisible to the others. Without sticky sessions, a user logs in on Server A, their next request hits Server B, and they appear logged out.
- **Keywords**: sticky sessions, session affinity, session persistence, shared session store, stateless
- **Related concepts**: [[load-balancing]], [[horizontal-scaling]], [[caching-strategies]]
- **Depth**: 2/4
- **Last updated**: 2026-04-30
- **Source**: sources/videos/cs75-summer-2012-lecture-9-scalability-harvard-web-development-david-malan

## Summary

Imagine a hospital where you see a different doctor every visit and they have no shared medical records. You'd have to re-explain your history every time. Sticky sessions are like always routing you to the same doctor.

There are several approaches, each with trade-offs:
1. **LB-inserted cookie**: The load balancer sets a cookie mapping the user to a specific backend. Simple, but that server becomes a SPOF for that user.
2. **Shared session store**: Move sessions to a central database or Redis/Memcached. Any server can serve any user. Adds a dependency but is the cleanest solution.
3. **Client-side sessions**: Store all state in encrypted cookies. No server-side storage needed, but limited by cookie size and raises privacy concerns.

The modern best practice is option 2 — externalize sessions to a shared store and make servers fully stateless, eliminating the need for sticky routing entirely.

## Example

A PHP app stores sessions in `/tmp` on each server. Behind a round-robin load balancer with 3 servers:
- User logs in → request hits Server A → session file created at `/tmp/sess_abc123` on Server A.
- Next request → LB sends to Server B → no session file → user appears logged out.
- **Fix with sticky sessions**: LB inserts a cookie `SERVERID=A`, always routes this user to Server A.
- **Better fix**: Move sessions to Redis. All 3 servers read/write sessions from the same Redis instance. No sticky routing needed.

## Relationship to other concepts

- [[load-balancing]]: Sticky sessions are a load balancer feature — the LB decides which server gets each request.
- [[horizontal-scaling]]: The session problem only appears when you scale horizontally. Stateless servers with shared session stores are the clean solution.
- [[caching-strategies]]: Redis/Memcached serve double duty as both session stores and application caches.

## Open questions

- When is sticky sessions (option 1) actually preferable to shared session stores (option 2)?
- How do JWT tokens change the session management landscape compared to server-side sessions?
