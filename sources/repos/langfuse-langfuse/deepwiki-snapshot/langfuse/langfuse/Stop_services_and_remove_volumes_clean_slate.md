pnpm run infra:dev:prune
```

The `infra:dev:up` command is configured to pull images and wait for health checks to ensure service readiness before application startup [package.json:15]().

**Diagram: Infrastructure Startup Sequence**

```mermaid
graph TB
    subgraph "Startup_Orchestration"
        [ComposeUp] --> ["pnpm run infra:dev:up"]
    end
    
    subgraph "Code_Entity_Space"
        [PG] --> ["postgres:17<br/>container: langfuse-postgres"]
        [CH] --> ["clickhouse/clickhouse-server:25.8<br/>container: langfuse-clickhouse"]
        [Redis] --> ["redis:7.2.4<br/>container: langfuse-redis"]
        [MinIO] --> ["chainguard/minio<br/>container: langfuse-minio"]
    end
    
    subgraph "Health_Checks"
        [PGHealth] --> ["pg_isready -U postgres"]
        [CHHealth] --> ["wget --spider http://localhost:8123/ping"]
    end
    
    [ComposeUp] --> [PG]
    [ComposeUp] --> [CH]
    [ComposeUp] --> [Redis]
    [ComposeUp] --> [MinIO]
    
    [PG] -.-> [PGHealth]
    [CH] -.-> [CHHealth]
```

Sources: [package.json:15-17](), [web/Dockerfile:131-137](), [worker/Dockerfile:82-87]()

---

### Database Migrations and Seeding

**PostgreSQL Migrations**
Database schema migrations are managed by Prisma. In development, the `db:migrate` script runs `turbo run db:migrate` which executes `prisma migrate dev` within the `@langfuse/shared` package [package.json:19](), [packages/shared/package.json:58]().

**ClickHouse Migrations**
ClickHouse migrations are handled via the `migrate` (golang-migrate) CLI [web/Dockerfile:151](). The scripts are located in the `packages/shared/clickhouse` directory. Developers can reset ClickHouse tables using `pnpm run ch:reset` which executes a sequence of down/up/seed scripts [packages/shared/package.json:71]().

**Seeding Data**
Langfuse provides a comprehensive seeding system to populate the development environment with realistic data [packages/shared/scripts/seeder/seed-postgres.ts:42-115]().

```bash