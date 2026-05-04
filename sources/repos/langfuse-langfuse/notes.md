# langfuse/langfuse

## Summary

Langfuse is an open-source LLM engineering platform that helps teams develop, monitor, evaluate, and debug AI applications. It is built as a TypeScript monorepo with two services: a **Web Service** (Next.js) handling the UI, authentication, and ingestion API, and a **Worker Service** (Express + BullMQ) executing background processing, automated evaluations, and data propagation.

The core data model follows LLM observability conventions: a **Trace** is the top-level container for one request or conversation; **Observations** (spans, generations, events, tool calls) are granular steps within a trace; **Scores** are evaluation metrics attached to traces or observations; and **Sessions** group related traces from a user conversation thread. SDKs POST batches of these events to `/api/public/ingestion`, and OpenTelemetry is supported as an alternative protocol via `/api/public/otel`.

Data storage is split by workload profile: **PostgreSQL** (via Prisma ORM) holds relational metadata — users, organizations, projects, prompts, score configs, job configurations; **ClickHouse** stores high-volume observability data — traces, observations, scores — with batched async writes and ReplacingMergeTree tables for idempotent upserts. **Redis** backs BullMQ queues and rate-limiting counters; **S3/blob storage** captures raw ingestion batches before processing for durability and replay.

The ingestion pipeline uses an **S3-first durability pattern**: raw payloads are persisted to object storage before a job is enqueued, so no data is lost even if the queue fails. Workers process events asynchronously, enrich them (prompt lookups, model cost calculations), then buffer writes through `ClickhouseWriter` before flushing to ClickHouse in batches. A separate event propagation job denormalizes staging table data into final analytical tables by joining observations with trace metadata (user_id, session_id, tags) at write time — eliminating expensive join queries later.

**Prompt management** is first-class: prompts are versioned, labeled (e.g., "production", "latest"), folder-organized, and support recursive dependencies. An epoch-based Redis cache minimizes DB lookups. **LLM-as-judge evaluation** uses job configurations stored in PostgreSQL and execution queues backed by BullMQ; external LLM providers (OpenAI, Anthropic, Bedrock, Vertex AI) are called via an encrypted credential store with AES-256 key encryption and SSRF-safe URL validation.

Access control uses a **hierarchical RBAC** model with roles at both organization and project levels — effective access equals the maximum of the two roles, enabling granular per-project overrides without complexity.

## Knowledge Map

- LLM observability data model: traces, observations (generations, spans), scores, sessions
- Dual-service architecture: web (Next.js) vs. worker (Express + BullMQ)
- Dual-database strategy: PostgreSQL (OLTP metadata) + ClickHouse (OLAP analytics)
- S3-first durability: persist raw events before enqueuing for replay safety
- Event sourcing with staging propagation: staging tables → denormalized final ClickHouse tables
- BullMQ queue system: 20+ specialized queues, sharded by projectId, with DLQ and backoff
- Prompt version management: versioning, labels, folder paths, Redis caching, recursive deps
- LLM-as-judge evaluation: automated scoring pipeline with external LLM provider integration
- Hierarchical RBAC: org roles + project-level overrides, scope-based fine-grained permissions
- LLM API key management: AES-256 encrypted credentials, multi-provider support

## Key Takeaways

- Langfuse's core insight: treat LLM application runs as structured traces (like distributed tracing), then layer evaluation and cost tracking on top
- The OLTP/OLAP split (PostgreSQL for config, ClickHouse for events) is the key architectural decision enabling both fast writes and analytical queries at scale
- S3-first durability decouples ingestion reliability from queue/worker health — if a worker crashes, events are replayed from S3
- Staging table propagation avoids expensive ClickHouse JOINs at query time by denormalizing trace metadata into observations at write time (a classic OLAP pre-aggregation pattern)
- Prompt versioning with labels ("production", "staging") is essential for safe LLM application deployments — it mirrors blue/green deployment ideas applied to prompts
- LLM-as-judge with encrypted credential management allows automated eval without exposing API keys in plaintext
- Queue sharding by projectId enables horizontal worker scaling without hot spots on high-traffic projects
