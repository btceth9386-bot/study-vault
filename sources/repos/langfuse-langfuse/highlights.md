# Highlights

- `Overview.md` Dual-service monorepo: Web Service (Next.js) for UI + API ingestion; Worker Service (Express) for BullMQ background jobs — resource-intensive tasks never compete with user requests
- `System_Architecture.md` S3-first ingestion: raw event batches persisted to S3 before being enqueued in BullMQ — enables replay on worker crash with no data loss
- `System_Architecture.md` Complete request flow: SDK POST → API auth → rate limit → S3 upload → BullMQ enqueue → Worker dequeue → IngestionService enrichment → ClickhouseWriter batch flush
- `Database_Overview.md` Dual-database: PostgreSQL (Prisma ORM) for transactional metadata; ClickHouse (ReplacingMergeTree) for high-volume observability events — different databases optimized for different access patterns
- `Events_Table__Dual-Write_Architecture.md` Staging table propagation: observations written to `observations_batch_staging` (3-min partition TTL) → `handleEventPropagationJob` JOINs with traces → denormalized into `events_full` with trace metadata inlined — eliminates JOIN cost at query time
- `Glossary.md` Core data model: **Trace** (top-level request container) → **Observation** (span/generation/event/tool) → **Score** (evaluation metric); **Session** groups related traces; **Generation** = observation specifically tracking an LLM call with token usage
- `Prompts__Templates.md` Prompt versioning: auto-incrementing version integer + deployment labels (e.g., "production") + folder paths (`marketing/emails/welcome`) + epoch-based Redis cache for fast SDK resolution
- `Prompts__Templates.md` Prompt dependencies: `{{LANGFUSE_PROMPT:name}}` syntax for recursive prompt composition; stored in `PromptDependency` table linking parent version to child by name/label/version
- `Evaluation_System.md` LLM-as-judge: `JobConfiguration` (PostgreSQL) → `EvalExecutionQueue` (BullMQ) → `fetchLLMCompletion` (encrypted credential decrypt + LLM call) → `Score` record written to ClickHouse
- `LLM_API_Key_Management.md` AES-256 encrypted LLM API key storage with `displaySecretKey` masking; `validateLlmConnectionBaseURL` prevents SSRF; default credential sentinels for self-hosted Bedrock/VertexAI
- `RBAC__Permissions.md` Hierarchical RBAC: org role + optional project override; effective role = `max(org_role, project_role)` via `orderedRoles` comparison; scopes formatted as `resource:action` (e.g., `prompts:CUD`)
- `Queue__Worker_System.md` Queue sharding: `ingestion-queue` and `trace-upsert` queues sharded by `projectId` — prevents one high-traffic project from starving others; `WorkerManager` tracks per-queue metrics (depth, wait time, DLQ length)
- `Data_Ingestion_Pipeline.md` 207 Multi-Status response for batch ingestion: each event in a batch gets its own success/error result — partial batch failures are reported without failing the entire request
- `Scores__Scoring.md` Score sources: `ANNOTATION` (human), `API` (programmatic), `EVAL` (automated LLM-as-judge); `CORRECTION` special type for human corrections to model outputs; stored in ClickHouse with `ScoreConfig` constraints in PostgreSQL
- `OpenTelemetry_Ingestion.md` OpenTelemetry support: OTLP format via `/api/public/otel/v1/traces` — Langfuse translates OTel spans to its native trace/observation model, enabling use with any OTel-instrumented SDK
