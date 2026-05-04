---
id: s3-first-durability
title: S3-First Durability Pattern
depth: 2
last_reviewed: 2026-05-04
review_due: 2026-05-07
sources:
  - sources/repos/langfuse-langfuse
related:
  - async-processing
  - high-availability
  - eventual-consistency
tags:
  - reliability
  - durability
  - async-processing
---

# S3-First Durability Pattern

- **One-sentence definition**: S3-first durability saves raw event payloads to durable object storage before handing them to queues or workers.
- **Why it exists / what problem it solves**: Queues and workers are good for throughput, but they are not always enough as the source of truth. If raw events are saved first, the system can survive worker crashes, downstream outages, and some processing bugs because the original payload can be replayed.
- **Keywords**: S3, blob storage, write-ahead log, replay, ingestion queue, durability
- **Related concepts**: [[async-processing]], [[high-availability]], [[eventual-consistency]]
- **Depth**: 2/4
- **Last updated**: 2026-05-04
- **Source**: sources/repos/langfuse-langfuse

## Summary

Think of S3-first durability as writing the receipt before starting the work. When an SDK sends observability events, the system first stores the raw payload in durable blob storage such as S3. Only after that does it enqueue work for background processing. If the worker fails, the queue retries, or ClickHouse is temporarily unavailable, the original event still exists.

This pattern is especially useful for high-volume ingestion systems. It separates "we safely received your data" from "we have finished transforming and indexing your data." The trade-off is extra latency and storage cost, but the system gains replayability and a stronger recovery story.

## Example

An LLM tracing SDK sends a batch of generation events:

1. The web API authenticates and validates the request.
2. The raw event payload is uploaded to S3 or compatible blob storage.
3. A queue job stores the S3 reference.
4. A worker later reads the payload, enriches it, and writes analytical rows to ClickHouse.

If ClickHouse is down during step 4, the event is not lost. The worker can retry later because the raw payload is still in object storage.

## Relationship to existing concepts

- [[async-processing]]: S3-first durability makes an asynchronous queue pipeline safer by keeping a durable source copy.
- [[high-availability]]: Durable object storage reduces the chance that one failed component causes permanent data loss.
- [[eventual-consistency]]: The API can accept data before it appears in analytical tables, creating a short propagation window.

## Open questions

- How long should raw event payloads be retained after successful processing?
- What metadata is needed to replay events safely without creating duplicates?
