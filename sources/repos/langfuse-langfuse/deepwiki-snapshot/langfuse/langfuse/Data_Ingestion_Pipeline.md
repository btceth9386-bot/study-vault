## Purpose and Scope

This document describes the data ingestion system responsible for receiving, validating, and storing observability events in Langfuse. The ingestion pipeline handles two primary input formats: native Langfuse SDK events and OpenTelemetry (OTLP) traces, converting both into a unified event format for storage and querying.

The pipeline is designed for high-volume data processing using a decoupled architecture where the web layer handles initial acceptance and durability (S3), while background workers handle heavy processing, model cost calculation, and persistence.

**Scope:**
- HTTP API endpoints for event ingestion (`/api/public/ingestion`) [web/src/pages/api/public/ingestion.ts:50-53]()
- Event validation and multi-tenant authentication via `ApiAuthService` [web/src/pages/api/public/ingestion.ts:76-88]()
- S3-based durability layer and deduplication logic [web/src/pages/api/public/ingestion.ts:42-45]()
- Queue-based asynchronous processing via BullMQ [web/src/pages/api/public/ingestion.ts:44-45]()
- OpenTelemetry span conversion and mapping via `OtelIngestionProcessor`
- Event propagation from staging tables to the final ClickHouse tables [worker/src/services/IngestionService/index.ts:155-156]()

## Architecture Overview

The ingestion architecture spans from the public API handlers in the `web` service to background workers that process and persist data. Langfuse utilizes an event-sourcing pattern where raw observations are staged and then propagated to a unified events table.

### System Flow Diagram
The following diagram illustrates the flow from external SDKs to internal code entities and storage.

```mermaid
graph TB
    subgraph "Ingestion Endpoints [web/src/pages/api/public]"
        [SDK] -->|"POST /ingestion"| [ingestion.ts_handler]
        [OTel_Collector] -->|"POST /otel/v1/traces"| [otel_traces_handler]
    end
    
    subgraph "Validation & Auth [web/src/features/public-api/server]"
        [ingestion.ts_handler] --> [ApiAuthService_verifyAuthHeaderAndReturnScope]
        [ApiAuthService_verifyAuthHeaderAndReturnScope] --> [RateLimitService_rateLimitRequest]
    end
    
    subgraph "Shared Processing [packages/shared/src/server]"
        [ingestion.ts_handler] --> [processEventBatch]
        [processEventBatch] --> [S3_StorageService]
    end
    
    subgraph "Queue Layer [Redis/BullMQ]"
        [processEventBatch] --> [IngestionQueue]
    end
    
    subgraph "Worker Processing [worker/src/services]"
        [IngestionQueue] --> [IngestionWorker]
        [IngestionWorker] --> [IngestionService_mergeAndWrite]
        [IngestionService_mergeAndWrite] --> [IngestionService_createEventRecord]
    end

    subgraph "ClickHouse Storage"
        [IngestionService_mergeAndWrite] --> [TableName_Observations]
        [IngestionService_mergeAndWrite] --> [TableName_Traces]
        [IngestionService_mergeAndWrite] --> [TableName_Scores]
    end
```

**Sources:**
- [web/src/pages/api/public/ingestion.ts:50-138]()
- [worker/src/services/IngestionService/index.ts:149-195]()
- [worker/src/services/IngestionService/index.ts:212-218]()
- [web/src/features/public-api/server/apiAuth.ts:86-102]()

## Ingestion Endpoints

### Native SDK Ingestion Endpoint
**Route:** `POST /api/public/ingestion`
The native ingestion endpoint accepts batches of Langfuse events. It uses `ApiAuthService` to verify project-level API keys and `RateLimitService` to enforce ingestion quotas [web/src/pages/api/public/ingestion.ts:76-111](). The `bodyParser` is configured to handle up to 4.5mb payloads [web/src/pages/api/public/ingestion.ts:26-32]().

### OpenTelemetry (OTLP) Endpoint
**Route:** `POST /api/public/otel/v1/traces`
This endpoint (detailed in child pages) accepts OTLP traces. The system is instrumented with OpenTelemetry internally to monitor this pipeline, using a `NodeSDK` configuration that includes instrumentations for `Http`, `Express`, `Prisma`, `IORedis`, and `BullMQ` [worker/src/instrumentation.ts:26-69]().

## Event Processing and Validation

### processEventBatch
This function is the primary entry point for processing event batches in the web layer. It performs initial validation, uploads the raw events to S3 for durability, and dispatches jobs to the asynchronous ingestion queue [web/src/pages/api/public/ingestion.ts:42-49]().

### IngestionService
The `IngestionService` in the worker layer is responsible for the final transformation of loose event data into strict ClickHouse records. It performs:
- **Prompt Lookups:** Matching events to prompt versions [worker/src/services/IngestionService/index.ts:221-233]().
- **Model Enrichment:** Identifying models and calculating costs [worker/src/services/IngestionService/index.ts:234-236]().
- **Usage Normalization:** Converting various usage formats (e.g., OpenAI tokens) into the standard Langfuse `Usage` schema [packages/shared/src/server/ingestion/types.ts:45-69]().

### Data Validation
Ingestion data is strictly validated using Zod schemas. Key schemas include:
- `idSchema`: Validates IDs (1-800 characters) for S3 compatibility [packages/shared/src/server/ingestion/types.ts:10-16]().
- `Usage`: Validates token and cost metrics [packages/shared/src/server/ingestion/types.ts:20-28]().
- `UsageDetails`: Handles complex token breakdowns from providers like OpenAI [packages/shared/src/server/ingestion/types.ts:217-223]().

## Event Propagation System

Langfuse utilizes a dual-write and propagation architecture to manage high-throughput writes and eventual consistency.

1.  **Direct Write:** The `IngestionService` writes processed records directly to ClickHouse tables such as `traces`, `observations`, and `scores` [worker/src/services/IngestionService/index.ts:161-194]().
2.  **Staging:** Some event types are written to staging tables before being merged into the primary `events` table to support the V4 "events-first" architecture [worker/src/services/IngestionService/index.ts:176-177]().
3.  **Deduplication:** The system uses `eventBodyId` and `id` within the event envelope to ensure that updates to existing entities (like updating a span's end time) are handled correctly [worker/src/services/IngestionService/index.ts:152-159]().

### Data Entity Association Diagram
This diagram shows how code entities interact with the ingestion and storage layers.

```mermaid
graph TD
    subgraph "Ingestion Logic"
        [processEventBatch]
        [IngestionService]
        [PromptService]
    end

    subgraph "Storage & Queues"
        [S3_Bucket]
        [Redis_BullMQ_Queue]
        [ClickhouseWriter]
    end

    [processEventBatch] -->|"uploadJson"| [S3_Bucket]
    [processEventBatch] -->|"add to queue"| [Redis_BullMQ_Queue]
    [Redis_BullMQ_Queue] --> [IngestionService]
    [IngestionService] -->|"getPrompt"| [PromptService]
    [IngestionService] -->|"flush"| [ClickhouseWriter]
```

**Sources:**
- [worker/src/services/IngestionService/index.ts:137-147]()
- [worker/src/services/IngestionService/index.ts:149-195]()
- [web/src/pages/api/public/ingestion.ts:134-137]()

## Child Pages
For detailed implementation specifics, refer to the following sub-pages:
- [Ingestion Overview](#6.1) — Detailed flow from API request through S3 and Queue.
- [Ingestion API Endpoints](#6.2) — Documentation of `/api/public/ingestion` and event types.
- [Event Processing & Validation](#6.3) — Details on `processEventBatch`, deduplication, and Zod validation.
- [Event Enrichment & Masking](#6.4) — PII masking, tokenization, and cost calculation logic.
- [Event Propagation System](#6.5) — The staging-to-events propagation mechanics and consistency guarantees.
- [OpenTelemetry Ingestion](#6.6) — Mapping OTLP spans to Langfuse entities.