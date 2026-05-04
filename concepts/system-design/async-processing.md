---
id: async-processing
title: Asynchronous Processing
depth: 2
last_reviewed: 2026-04-30
review_due: 2026-05-03
sources:
  - sources/repos/system-design-primer
related:
  - microservices
  - caching-strategies
  - eventual-consistency
  - llm-as-judge-evaluation
  - oltp-olap-split
  - s3-first-durability
tags:
  - system-design
  - performance
---

# Asynchronous Processing

- **One-sentence definition**: Instead of making the user wait while the server does something slow, accept the request immediately, put the work on a queue, and let a background worker handle it.
- **Why it exists / what problem it solves**: Slow operations (image resizing, sending emails, crunching analytics) block request threads and kill throughput. Async processing decouples the "accept the request" step from the "do the work" step, so the system stays responsive under load.
- **Keywords**: message queue, task queue, Redis, RabbitMQ, SQS, Celery, back pressure, exponential backoff
- **Related concepts**: [[microservices]], [[caching-strategies]], [[eventual-consistency]], [[llm-as-judge-evaluation]], [[oltp-olap-split]], [[s3-first-durability]]
- **Depth**: 2/4
- **Last updated**: 2026-04-30
- **Source**: sources/repos/system-design-primer

## Summary

Imagine a coffee shop. Synchronous: you order, the barista makes your drink while you stand at the counter, then serves you. If 20 people order at once, the line is brutal. Asynchronous: you order, get a receipt number, sit down. The barista works through orders and calls your number when it's ready. The counter never blocks.

In software, this uses **message queues** (Redis, RabbitMQ, Amazon SQS) that hold jobs until workers pick them up. **Task queues** like Celery add scheduling, retries, and result tracking on top.

The safety valve is **back pressure**: when the queue fills up, the system returns HTTP 503 ("try again later") instead of accepting more work than it can handle. Clients retry with **exponential backoff** (wait 1s, then 2s, then 4s...) to avoid a thundering herd.

Trade-offs: results aren't available immediately (the user may need to poll for status), debugging spans multiple components, messages can be lost if the queue crashes before workers process them, and ordering isn't guaranteed in standard queues.

## Example

Twitter's fanout service when a user posts a tweet:

1. User posts tweet → Write API stores it in the database and returns "tweet posted" immediately.
2. Write API enqueues a fanout job to the message queue.
3. Fanout workers pull the job, look up the user's followers, and insert the tweet into each follower's timeline cache (Redis).
4. A user with 10M followers? The fanout takes minutes, but the poster got their response in milliseconds.

## Relationship to other concepts

- [[microservices]]: Async queues are the primary way microservices communicate without blocking each other.
- [[caching-strategies]]: Write-behind caching is async processing applied to database writes — the cache batches and flushes asynchronously.
- [[eventual-consistency]]: Async processing inherently introduces a delay between write and visibility, making the system eventually consistent.
- [[llm-as-judge-evaluation]]: LLM judge runs should execute in background queues so user-facing requests do not wait for model grading.
- [[oltp-olap-split]]: Async workers often move validated events from transactional ingestion paths into analytical storage.
- [[s3-first-durability]]: Saving raw payloads before queue processing makes async pipelines recoverable after worker or downstream failures.

## Open questions

- When should you use a simple message queue (SQS) vs a full task framework (Celery)?
- How do you guarantee exactly-once processing when queues offer at-least-once delivery?
