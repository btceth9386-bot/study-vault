This page is the entry point for developers setting up a local Langfuse development environment. It covers the prerequisites, the overall service topology, and points to sub-pages for detailed installation ([Installation & Setup](#2.1)), environment configuration ([Environment Configuration](#2.2)), and running services ([Running Services](#2.3)).

For background on what Langfuse is and how the system is architected, see [Overview](#1) and [System Architecture](#1.1). For the monorepo layout and package structure, see [Monorepo Structure](#1.2).

---

## Prerequisites

Before starting, ensure the following tools are installed and at the correct versions:

| Tool | Required Version | Notes |
|------|-----------------|-------|
| Node.js | 24 | Specified in `.nvmrc` and `CONTRIBUTING.md` [CONTRIBUTING.md:113]() |
| pnpm | 10.33.0 | Specified in `CONTRIBUTING.md` and setup scripts [CONTRIBUTING.md:114](), [scripts/codex/setup.sh:22]() |
| Docker | Any recent version | Required to run the database and infrastructure locally [CONTRIBUTING.md:115]() |
| Clickhouse client | Latest | Required for manual database interaction [CONTRIBUTING.md:116]() |

The repository uses [pnpm](https://pnpm.io/) workspaces to manage dependencies [CONTRIBUTING.md:99](). You can also run the environment in a **GitHub Codespace** via the provided `.devcontainer` [CONTRIBUTING.md:118](), or an **OpenAI Codex** cloud environment using the provided bootstrap scripts [CONTRIBUTING.md:120-124]().

Sources: [CONTRIBUTING.md:111-124](), [scripts/codex/setup.sh:22](), [.devcontainer/Dockerfile:19]()

---

## Repository Overview

The codebase is a monorepo managed with `pnpm` and `turbo` [CONTRIBUTING.md:99]().

**Monorepo Package Dependency Graph:**

```mermaid
graph TB
    ["web (Next.js App)"] -- "depends on" --> ["@langfuse/shared"]
    ["web (Next.js App)"] -- "depends on" --> ["@langfuse/ee"]
    ["worker (Async Processing)"] -- "depends on" --> ["@langfuse/shared"]
    ["@langfuse/ee"] -- "depends on" --> ["@langfuse/shared"]
    
    subgraph "Packages"
        ["@langfuse/shared"]
        ["@langfuse/ee"]
    end
    
    subgraph "Applications"
        ["web (Next.js App)"]
        ["worker (Async Processing)"]
    end
```

**Package Roles:**

| Package | Purpose | Key Technologies |
|---------|---------|------------------|
| `web` | Main application: Frontend, tRPC, and Public REST APIs [CONTRIBUTING.md:101]() | Next.js, NextAuth.js, tRPC, Prisma [CONTRIBUTING.md:45-48]() |
| `worker` | Asynchronous task processing and queue consumption [CONTRIBUTING.md:102]() | BullMQ, Express, Node.js [CLAUDE.md:68](), [CONTRIBUTING.md:69,71]() |
| `shared` | Shared domain logic, Prisma schema, and DB contracts [CONTRIBUTING.md:104]() | Prisma, ClickHouse migrations [CONTRIBUTING.md:95,104]() |
| `ee` | Enterprise Edition features [CONTRIBUTING.md:107]() | Consumed by `web` [CLAUDE.md:70,77]() |

Sources: [CONTRIBUTING.md:45-52, 99-107](), [CLAUDE.md:63-80]()

---

## Infrastructure Services

A local environment requires several infrastructure services. The dual-service architecture (Web and Worker) communicates with transactional and analytical databases.

**Development Environment Topology:**

```mermaid
flowchart TB
    subgraph "Local Node Processes"
        ["web (Next.js Server)"]
        ["worker (BullMQ Worker)"]
    end

    subgraph "Infrastructure (External Services)"
        ["postgres (PostgreSQL 17)"]
        ["clickhouse (ClickHouse Server)"]
        ["redis (Redis 7)"]
        ["minio (S3 Blob Storage)"]
    end

    ["web (Next.js Server)"] --> ["postgres (PostgreSQL 17)"]
    ["web (Next.js Server)"] --> ["clickhouse (ClickHouse Server)"]
    ["web (Next.js Server)"] --> ["redis (Redis 7)"]
    ["web (Next.js Server)"] --> ["minio (S3 Blob Storage)"]
    
    ["worker (BullMQ Worker)"] --> ["postgres (PostgreSQL 17)"]
    ["worker (BullMQ Worker)"] --> ["clickhouse (ClickHouse Server)"]
    ["worker (BullMQ Worker)"] --> ["redis (Redis 7)"]
    ["worker (BullMQ Worker)"] --> ["minio (S3 Blob Storage)"]
```

**Service Details:**

| Service | Code Entity / Identifier | Purpose |
|---------|--------------------------|---------|
| `Postgres` | `DATABASE_URL` | OLTP: Transactional data (Users, Orgs, Projects) [CONTRIBUTING.md:70](), [docker-compose.yml:23]() |
| `Clickhouse` | `CLICKHOUSE_URL` | OLAP: Observability data (Traces, Observations, Scores) [CONTRIBUTING.md:72](), [docker-compose.yml:29]() |
| `Redis` | `REDIS_HOST` | Cache and `BullMQ` Queue management [CONTRIBUTING.md:71](), [docker-compose.yml:61]() |
| `Minio` | `LANGFUSE_S3_EVENT_UPLOAD_ENDPOINT` | S3-compatible storage for raw events and media [CONTRIBUTING.md:73](), [docker-compose.yml:40]() |

Sources: [CONTRIBUTING.md:64-89](), [docker-compose.yml:7-154]()

---

## First-Run Quickstart

To initialize the development environment from scratch:

```bash