PostgreSQL serves as the primary metadata and configuration database for Langfuse. It stores organizational structures, user accounts, project settings, evaluation configurations, dataset definitions, and prompt versions. While high-volume observability events are stored in ClickHouse, PostgreSQL maintains the relational integrity of the platform's configuration and management layer.

For information about the dual-database architecture, see [3.1 Database Overview](). For the ClickHouse schema containing observability events, see [3.3 ClickHouse Schema]().

## Schema Overview

The PostgreSQL schema is managed via Prisma ORM, defined in [packages/shared/prisma/schema.prisma:1-1637](). It utilizes advanced PostgreSQL features such as JSONB for flexible metadata, GIN indexes for efficient searching, and partial indexes for optimized query performance.

**Key Technical Characteristics:**
- **ORM**: Prisma Client with support for `views`, `relationJoins`, and `metrics` [packages/shared/prisma/schema.prisma:4-7]().
- **Multi-tenancy**: Strictly enforced via `Organization` and `Project` hierarchies.
- **Auditability**: Extensive audit logging for sensitive resource changes [web/src/features/audit-logs/auditLog.ts:7-46]().
- **Backward Compatibility**: Legacy observability tables (`LegacyPrismaTrace`, `LegacyPrismaObservation`, `LegacyPrismaScore`) are maintained for historical data and specific migration paths [packages/shared/prisma/schema.prisma:148-150]().

Sources: [packages/shared/prisma/schema.prisma:1-150](), [web/src/features/audit-logs/auditLog.ts:7-46]()

## Multi-Tenancy and Access Control

Langfuse employs a nested multi-tenant model. Organizations serve as the billing and top-level administrative unit, while Projects serve as the operational silo for observability data.

### Organizational Hierarchy

**Natural Language Space to Code Entity Space: Access Control**
```mermaid
graph TD
    subgraph "Identity_and_Auth"
        User["User model<br/>(packages/shared/prisma/schema.prisma:48)"]
        Account["Account model<br/>(packages/shared/prisma/schema.prisma:17)"]
    end

    subgraph "Tenant_Structure"
        Org["Organization model<br/>(packages/shared/prisma/schema.prisma:91)"]
        Project["Project model<br/>(packages/shared/prisma/schema.prisma:113)"]
    end

    subgraph "Membership_and_RBAC"
        OrgMem["OrganizationMembership<br/>(packages/shared/prisma/schema.prisma:214)"]
        ProjMem["ProjectMembership<br/>(packages/shared/prisma/schema.prisma:243)"]
        RoleEnum["Role Enum<br/>(OWNER, ADMIN, MEMBER, VIEWER)"]
    end

    User -->|"1:N"| Account
    User -->|"1:N"| OrgMem
    Org -->|"1:N"| OrgMem
    Org -->|"1:N"| Project
    
    OrgMem -->|"1:N"| ProjMem
    Project -->|"1:N"| ProjMem
    User -->|"1:N"| ProjMem
    
    OrgMem -.->|"assigns"| RoleEnum
    ProjMem -.->|"overrides"| RoleEnum
```

- **Organization**: Manages cloud billing (`cloudBillingCycleAnchor`), usage limits (`cloudCurrentCycleUsage`), and enterprise features like `aiFeaturesEnabled` [packages/shared/prisma/schema.prisma:98-102]().
- **Project**: Scopes API keys, traces, and configurations. It includes a `retentionDays` setting to manage data lifecycle [packages/shared/prisma/schema.prisma:120]().
- **User**: Stores profile information and global `admin` status [packages/shared/prisma/schema.prisma:49-55]().

Sources: [packages/shared/prisma/schema.prisma:17-262]()

### API Key Authentication

The `ApiKey` model facilitates programmatic access to the Langfuse API. Keys can be scoped to an entire organization or a specific project.

| Field | Description |
| :--- | :--- |
| `publicKey` | The identifier used in API requests [packages/shared/prisma/schema.prisma:194](). |
| `hashedSecretKey` | A secure hash of the secret key for verification [packages/shared/prisma/schema.prisma:195](). |
| `scope` | `ORGANIZATION` or `PROJECT` [packages/shared/prisma/schema.prisma:197](). |

Sources: [packages/shared/prisma/schema.prisma:190-212]()

## Configuration Tables

### Score Configurations

Score configurations define the validation logic and UI representation for metrics (e.g., user feedback, model evaluations).

- **ScoreConfig**: Defines the `dataType` (`NUMERIC`, `CATEGORICAL`, `BOOLEAN`) and metadata like `minValue`, `maxValue`, or categorical `categories` [packages/shared/prisma/schema.prisma:1052-1065]().
- **Integration**: The `appRouter` exposes these via `scoreConfigs` [web/src/server/api/root.ts:73]().

Sources: [packages/shared/prisma/schema.prisma:1052-1077](), [web/src/server/api/root.ts:73]()

### Prompt Management

Prompts are managed as versioned entities, allowing users to deploy specific versions to production using labels.

- **Prompt**: Stores the template content as JSON, supporting both text and chat formats [packages/shared/prisma/schema.prisma:763-770]().
- **Labels**: Versions can be tagged with labels (e.g., "production") for dynamic retrieval by SDKs [packages/shared/prisma/schema.prisma:774]().
- **PromptDependency**: Tracks relationships between prompts for complex template resolution [packages/shared/prisma/schema.prisma:792-810]().
- **LlmSchema & LlmTool**: Reusable structured definitions for prompt variables and tool-calling capabilities. `LlmSchema` stores JSON schema definitions for structured outputs, while `LlmTool` stores tool/function definitions [packages/shared/prisma/schema.prisma:152-153]().

Sources: [packages/shared/prisma/schema.prisma:763-810](), [packages/shared/prisma/schema.prisma:152-153]()

### Model and Pricing

The `Model` table stores definitions for LLMs, including regex patterns for matching model names in traces and pricing details.

- **Model**: Includes `matchPattern` for identification and `unit` (e.g., TOKENS, CHARACTERS) for cost calculation [packages/shared/prisma/schema.prisma:825-831]().
- **PricingTier**: Allows for complex pricing models based on conditions (e.g., tiered pricing based on context window size) [packages/shared/prisma/schema.prisma:868-886]().

Sources: [packages/shared/prisma/schema.prisma:825-886]()

## Evaluation and Automation

Langfuse uses PostgreSQL to coordinate background evaluation jobs and automations.

- **EvalTemplate**: Stores the prompt and configuration for LLM-as-a-judge evaluations [packages/shared/prisma/schema.prisma:920-945]().
- **JobConfiguration**: Defines which traces or observations should be evaluated, including filters and sampling rates [packages/shared/prisma/schema.prisma:967-975]().
- **JobExecution**: Tracks the lifecycle of an evaluation job (e.g., `PENDING`, `COMPLETED`, `ERROR`) [packages/shared/prisma/schema.prisma:1004-1014]().
- **Automation**: Maps triggers (like `trace-create`) to actions (like `webhook` or `slack`) [packages/shared/prisma/schema.prisma:1454-1560]().

Sources: [packages/shared/prisma/schema.prisma:920-1042](), [packages/shared/prisma/schema.prisma:1454-1560]()

## Datasets and Experiments

Datasets allow users to create golden sets for testing and benchmarking.

- **Dataset**: The top-level container for items [packages/shared/prisma/schema.prisma:590-611]().
- **DatasetItem**: Represents a single test case, using `validFrom` and `validTo` for versioning [packages/shared/prisma/schema.prisma:613-624]().
- **DatasetRun**: Groups the results of running a dataset through a specific model or prompt version [packages/shared/prisma/schema.prisma:647-664]().

Sources: [packages/shared/prisma/schema.prisma:590-686]()

## Integrations and Audit Logs

### External Integrations

PostgreSQL stores configurations for syncing data to third-party platforms.

- **BlobStorageIntegration**: Configures exports to S3 or Azure Blob Storage, including `exportFrequency` and `exportMode` [packages/shared/prisma/schema.prisma:1105-1132]().
- **Analytics**: Stores settings for **PosthogIntegration** and **MixpanelIntegration** [packages/shared/prisma/schema.prisma:1079-1103]().

### Audit Logging

Langfuse maintains an immutable record of significant changes via the `AuditLog` model.

- **AuditLog**: Captures the `resourceType` (e.g., `prompt`, `apiKey`), the `action` (e.g., `create`, `update`), and `before`/`after` states [packages/shared/prisma/schema.prisma:894-918]().
- **Implementation**: The `auditLog` function in the web layer standardizes log creation across the codebase [web/src/features/audit-logs/auditLog.ts:80-117]().

**Data Flow: Audit Log Creation**
```mermaid
graph LR
    subgraph "Application_Layer"
        Router["tRPC Router<br/>(web/src/server/api/root.ts)"]
        AuditFn["auditLog() function<br/>(web/src/features/audit-logs/auditLog.ts)"]
    end

    subgraph "Database_Layer"
        AuditTable["AuditLog Table<br/>(packages/shared/prisma/schema.prisma)"]
    end

    Router -->|"calls"| AuditFn
    AuditFn -->|"creates record"| AuditTable
```

Sources: [packages/shared/prisma/schema.prisma:894-918](), [packages/shared/prisma/schema.prisma:1105-1169](), [web/src/features/audit-logs/auditLog.ts:1-117](), [web/src/server/api/root.ts:1-121]()