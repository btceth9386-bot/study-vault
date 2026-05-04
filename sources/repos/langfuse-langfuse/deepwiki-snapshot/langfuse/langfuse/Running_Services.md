This page documents how to start and run the Langfuse services in both development and production environments. It covers infrastructure setup, database migrations, service startup commands, and data seeding.

For information about configuring environment variables, see [Environment Configuration (2.2)](). For details about the monorepo structure and package organization, see [Monorepo Structure (1.2)]().

---

## Development Environment

### Infrastructure Services

Langfuse requires several infrastructure services (PostgreSQL, ClickHouse, Redis, S3/MinIO) for local development. These are managed via Docker Compose using the `docker-compose.dev.yml` file.

**Starting Infrastructure**
The root `package.json` defines scripts to manage infrastructure containers:

```bash