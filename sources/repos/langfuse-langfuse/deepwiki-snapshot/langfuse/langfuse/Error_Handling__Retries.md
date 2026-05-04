This document describes the error handling and retry mechanisms in Langfuse's queue-based worker system and API layer. It covers retry strategies used across different failure modes, error classification, and the management of failed jobs.

## Overview

Langfuse implements multiple layers of retry logic to handle transient failures while failing fast on unrecoverable errors. The system distinguishes between four main categories of failures:

1.  **Data Availability Issues**: Missing observations or traces due to eventual consistency in ClickHouse when evaluations are triggered.
2.  **External Service Rate Limits**: LLM provider 429/5xx responses during evaluations or Stripe API limits during metering.
3.  **Validation & Logic Errors**: Invalid request data, missing project IDs, or incorrect evaluation configurations.
4.  **Infrastructure Errors**: Redis connection loss, ClickHouse connection issues, S3 timeouts, or tokenization memory errors.

Each category uses a distinct retry strategy optimized for its failure characteristics, primarily managed within the `WorkerManager`, specific queue processors, and API handlers.

Sources: [worker/src/queues/workerManager.ts:161-185](), [packages/shared/src/server/llm/errors.ts:1-10](), [worker/src/features/tokenisation/usage.ts:51-54]()

## Error Classification and Retry Decision Flow

The system uses a hierarchical decision tree to determine if a failed job should be retried, delayed, or marked as a permanent error.

### Job Failure Decision Logic
The following diagram illustrates how individual processors handle different error types using specialized retry utilities and BullMQ worker listeners.

Title: "Job Failure Decision Logic"
```mermaid
graph TD
    ["Job Fails in Worker"] --> CheckObsNotFound["Is it ObservationNotFoundError?"]
    CheckObsNotFound -->|Yes| CheckRetryObs["retryObservationNotFound()"]
    CheckRetryObs -->|Scheduled| CompleteSuccess["Complete Job (Success)"]
    CheckRetryObs -->|Max Attempts| CompleteWarn["Complete Job (Log Warning)"]
    
    CheckObsNotFound -->|No| CheckLLMRetryable{"Is it LLMCompletionError with isRetryable=true?"}
    
    CheckLLMRetryable -->|Yes| CallRetryLLM["retryLLMRateLimitError()"]
    CallRetryLLM -->|Outcome: scheduled| SetDelayed["Set Status: DELAYED"]
    CallRetryLLM -->|Outcome: skipped (too_old)| SetErrorTimeout["Set Status: ERROR (Job Timeout)"]
    
    CheckLLMRetryable -->|No| CheckUnrecoverable{"Is it UnrecoverableError?"}
    CheckUnrecoverable -->|Yes| SetError["Set Status: ERROR (No Retry)"]
    CheckUnrecoverable -->|No| BullMQRetry["BullMQ Default Retry (WorkerManager Listener)"]
```
Sources: [worker/src/queues/workerManager.ts:161-184](), [packages/shared/src/server/llm/errors.ts:1-10](), [worker/src/app.ts:179-193]()

## Error Type Definitions

The system defines custom error classes and uses standard exceptions to enable fine-grained control:

| Error Type | Retryable | Strategy | Use Case |
| :--- | :--- | :--- | :--- |
| `ObservationNotFoundError` | Yes | Custom Exponential Backoff | Observation not yet available in ClickHouse due to propagation delay. |
| `LLMCompletionError` (429/5xx) | Yes | Custom Delay Function | LLM provider rate limiting or temporary service outage. |
| `UnrecoverableError` | No | Immediate Failure | Configuration errors that cannot be fixed by retrying (e.g. invalid JSONPath). |
| `LangfuseNotFoundError` | No | Skip Job | Resources (like a Batch Export) deleted before the worker processed them. |
| `ZodError` | No | 400 Bad Request | Schema validation failures for incoming API payloads (e.g. Ingestion API). |
| `S3SlowDownError` | Yes | Project-level Tracking | Detected during event batch processing to apply backpressure. |

Sources: [packages/shared/src/server/llm/errors.ts:1-10](), [packages/shared/src/server/ingestion/processEventBatch.ts:151-167](), [packages/shared/src/server/ingestion/processEventBatch.ts:34-36]()

## Retry Strategies

### 1. LLM Rate Limits (429s)
LLM evaluations and judge executions often hit provider rate limits. These are treated as transient failures.

*   **Implementation**: Centralized in `retryLLMRateLimitError`.
*   **Maximum Job Age**: Typically 24 hours. If a job exceeds this, it is skipped to prevent stale processing.
*   **Mechanism**: It adds a new job to the specified queue with a calculated delay and increments an attempt counter in the metadata.

### 2. S3 Backpressure (SlowDown)
During high-volume ingestion, S3 may return `SlowDown` errors. Langfuse tracks these per project to mitigate impact.

*   **Implementation**: `markProjectS3Slowdown` is called when `isS3SlowDownError` is true during `processEventBatch`.
*   **Mechanism**: Uses Redis to track slowdown state for specific projects [packages/shared/src/server/ingestion/processEventBatch.ts:34-36]().

### 3. Queue-Level Retries (BullMQ)
The `WorkerManager` configures the underlying BullMQ workers.

*   **Implementation**: Configured in `WorkerManager.register` [worker/src/queues/workerManager.ts:127-131]().
*   **Trace Upsert**: Uses `LANGFUSE_TRACE_UPSERT_QUEUE_ATTEMPTS` (default 2) for trace upsert operations [packages/shared/src/env.ts:129]().
*   **Concurrency Control**: Different queues have specific concurrency and rate limits to prevent cascading failures, such as `LANGFUSE_EVAL_CREATOR_WORKER_CONCURRENCY` [worker/src/env.ts:108-111]().

### 4. Runtime Timeouts
For LLM operations, Langfuse enforces runtime timeouts to prevent hung requests from blocking worker slots indefinitely.

*   **Mechanism**: `fetchLLMCompletion` handles internal timeouts and maps them to retryable errors where appropriate [packages/shared/src/server/index.ts:28-29]().

## Dead Letter Queue (DLQ) Management

Langfuse monitors failed jobs through metrics and provides administrative tools for retry management.

*   **Monitoring**: `WorkerManager` records `failed` and `error` metrics via `recordIncrement` whenever a job fails [worker/src/queues/workerManager.ts:161-184]().
*   **Manual Retries**: An internal API endpoint `/api/admin/bullmq` allows Langfuse Cloud administrators to bulk retry or remove failed jobs from specific queues [web/src/pages/api/admin/bullmq/index.ts:32-47]().
*   **DLQ Service**: The `DlqRetryService` handles specialized dead letter retry logic [worker/src/app.ts:74]().

## Monitoring and Observability

All errors are instrumented for tracking and alerting:

*   **Exception Tracking**: `traceException(err)` is called in the `WorkerManager` failure listeners to report errors to Sentry/OpenTelemetry [worker/src/queues/workerManager.ts:166-178]().
*   **Logging**: `logger.error` provides detailed context including job ID and queue name [worker/src/queues/workerManager.ts:162-174]().
*   **Queue Lengths**: `WorkerManager` samples queue depth gauges (`length`, `dlq_length`, `active`) to provide visibility into backlog and failure rates [worker/src/queues/workerManager.ts:70-96]().

Title: "Error Handling Code Entity Mapping"
```mermaid
graph LR
    subgraph "Worker Infrastructure"
        ["WorkerManager (worker/src/queues/workerManager.ts)"]
        ["DlqRetryService (worker/src/services/dlq/dlqRetryService.ts)"]
    end

    subgraph "Retry Logic"
        ["retryLLMRateLimitError (retry-handler.ts)"]
        ["ingestionQueueProcessor (worker/src/queues/ingestionQueue.ts)"]
    end

    subgraph "Error Types"
        ["LLMCompletionError (packages/shared/src/server/llm/errors.ts)"]
        ["S3SlowDownError (packages/shared/src/server/redis/s3SlowdownTracking.ts)"]
    end

    ["WorkerManager (worker/src/queues/workerManager.ts)"] -- "listens for" --> ["LLMCompletionError (packages/shared/src/server/llm/errors.ts)"]
    ["ingestionQueueProcessor (worker/src/queues/ingestionQueue.ts)"] -- "handles" --> ["S3SlowDownError (packages/shared/src/server/redis/s3SlowdownTracking.ts)"]
    ["DlqRetryService (worker/src/services/dlq/dlqRetryService.ts)"] -- "retries jobs in" --> ["WorkerManager (worker/src/queues/workerManager.ts)"]
```
Sources: [worker/src/queues/workerManager.ts:161-184](), [packages/shared/src/server/llm/errors.ts:1-10](), [worker/src/app.ts:74-79](), [packages/shared/src/server/ingestion/processEventBatch.ts:34-36]()

Sources:
- [worker/src/queues/workerManager.ts:1-187]()
- [packages/shared/src/server/llm/errors.ts:1-10]()
- [worker/src/env.ts:70-138]()
- [packages/shared/src/env.ts:125-130]()
- [web/src/pages/api/admin/bullmq/index.ts:1-180]()
- [worker/src/app.ts:125-200]()
- [packages/shared/src/server/ingestion/processEventBatch.ts:1-120]()