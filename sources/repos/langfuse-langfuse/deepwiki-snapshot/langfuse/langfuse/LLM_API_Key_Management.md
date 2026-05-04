## Purpose and Scope

The LLM API key management system in Langfuse allows users to securely store and manage credentials for various Large Language Model (LLM) providers. These keys enable features such as automated evaluations, the LLM Playground, and prompt testing directly within the Langfuse interface. By using their own API keys, projects maintain control over their LLM usage, data privacy, and provider-specific configurations.

The system supports a wide range of adapters including OpenAI, Anthropic, Azure OpenAI, AWS Bedrock, and Google Vertex AI.

---

## Data Architecture

The management system relies on the `LlmApiKeys` model in PostgreSQL to store connection metadata and encrypted credentials.

### LlmApiKeys Model

Each record represents a unique connection between a Langfuse project and an LLM provider.

| Field | Type | Purpose |
|-------|------|---------|
| `id` | String | Unique identifier (CUID). |
| `projectId` | String | Foreign key to the Project. |
| `provider` | String | User-defined name for the connection (e.g., "MyOpenRouter"). [web/src/features/llm-api-key/types.ts:11-14]() |
| `adapter` | LLMAdapter | The technical interface used (OpenAI, Anthropic, etc.). [packages/shared/src/server/llm/types.ts:318-326]() |
| `secretKey` | String | The AES-256 encrypted API key or service account JSON. [web/src/features/llm-api-key/server/router.ts:29]() |
| `displaySecretKey` | String | A masked version for UI display (e.g., "...a1b2"). [web/src/features/llm-api-key/server/router.ts:44-54]() |
| `baseURL` | String? | Optional override for the API endpoint (e.g., for Azure or local LLMs). [web/src/features/llm-api-key/types.ts:16]() |
| `config` | Json? | Adapter-specific settings like AWS Region or GCP Location. [packages/shared/src/interfaces/customLLMProviderConfigSchemas.ts:11-41]() |
| `customModels` | String[] | List of model IDs available for this connection. [web/src/features/llm-api-key/types.ts:18]() |
| `extraHeaders` | String? | Encrypted JSON of additional HTTP headers to send with requests. [web/src/features/llm-api-key/server/router.ts:29-40]() |

Sources: [web/src/features/llm-api-key/types.ts:9-21](), [web/src/features/llm-api-key/server/router.ts:44-54](), [packages/shared/src/server/llm/types.ts:318-326]()

---

## System Entities and Logic Flow

The following diagram illustrates the relationship between the UI components, the server-side router, and the encryption layer.

### API Key Management Flow

```mermaid
graph TD
    subgraph "Web_UI_Next.js"
        UI_Form["CreateLLMApiKeyForm"]
        UI_Dialog["CreateLLMApiKeyDialog"]
    end

    subgraph "Backend_tRPC_Router"
        Router["llmApiKeyRouter"]
        TestFunc["testLLMConnection"]
        AuthCheck["throwIfNoProjectAccess"]
    end

    subgraph "Shared_Utilities"
        Encrypt["encrypt"]
        Decrypt["decrypt"]
        FetchLLM["fetchLLMCompletion"]
    end

    subgraph "Storage"
        DB[("PostgreSQL_LlmApiKeys_Prisma")]
    end

    UI_Dialog -->|"Renders"| UI_Form
    UI_Form -->|"Calls mutation"| Router
    Router -->|"Validates Access"| AuthCheck
    Router -->|"Protects Key"| Encrypt
    Encrypt -->|"Saves"| DB
    UI_Form -->|"Tests Connection"| TestFunc
    TestFunc -->|"Uses"| FetchLLM
    FetchLLM -->|"Calls"| ExternalAPI["LLM_Provider_API"]

    style UI_Form stroke-dasharray: 5 5
    style UI_Dialog stroke-dasharray: 5 5
```

Sources: [web/src/features/llm-api-key/server/router.ts:100-169](), [web/src/features/public-api/components/CreateLLMApiKeyForm.tsx:1-50](), [packages/shared/src/server/llm/fetchLLMCompletion.ts:171-205](), [web/src/features/public-api/components/CreateLLMApiKeyDialog.tsx:15-54]()

---

## Provider Adapters and Configuration

Langfuse uses a repository of adapters to normalize requests across different LLM providers.

### Supported Adapters
The `LLMAdapter` enum defines the supported interfaces:
- `OpenAI`: Standard OpenAI-compatible API.
- `Anthropic`: Anthropic Messages API.
- `Azure`: Azure OpenAI Service.
- `Bedrock`: AWS Bedrock (supports Access Keys, Bearer Tokens, and Default Credentials). [packages/shared/src/server/llm/fetchLLMCompletion.ts:103-146]()
- `VertexAI`: Google Cloud Vertex AI.
- `GoogleAIStudio`: Google AI Studio (Gemini).

Sources: [packages/shared/src/server/llm/types.ts:318-326](), [web/src/features/public-api/components/CreateLLMApiKeyForm.tsx:9-12]()

### Specialized Configuration
Certain adapters require complex configuration objects stored in the `config` field:
- **AWS Bedrock**: Validated via `BedrockConfigSchema`, requiring a `region`. [packages/shared/src/interfaces/customLLMProviderConfigSchemas.ts:11]()
- **Google Vertex AI**: Validated via `VertexAIConfigSchema`, requiring a `location`. [packages/shared/src/interfaces/customLLMProviderConfigSchemas.ts:35-41]()

### Default Credentials (Self-Hosted)
In self-hosted environments, Langfuse supports using the host's environment credentials (e.g., IAM roles or Application Default Credentials) using sentinel values:
- `BEDROCK_USE_DEFAULT_CREDENTIALS`: `__BEDROCK_DEFAULT_CREDENTIALS__` [packages/shared/src/interfaces/customLLMProviderConfigSchemas.ts:4-5]()
- `VERTEXAI_USE_DEFAULT_CREDENTIALS`: `__VERTEXAI_DEFAULT_CREDENTIALS__` [packages/shared/src/interfaces/customLLMProviderConfigSchemas.ts:8-9]()

These are strictly prohibited in Langfuse Cloud to ensure multi-tenant isolation. [web/src/features/llm-api-key/server/router.ts:208-234]()

Sources: [packages/shared/src/interfaces/customLLMProviderConfigSchemas.ts:4-9](), [web/src/features/llm-api-key/server/router.ts:44-50]()

---

## Credential Security and Encryption

### Encryption at Rest
API keys and extra headers are never stored in plaintext. The `llmApiKeyRouter` uses the shared `encrypt` function before persisting data to the database. This requires a valid `ENCRYPTION_KEY` environment variable. [web/src/features/llm-api-key/server/router.ts:29]()

Sources: [web/src/features/llm-api-key/server/router.ts:29](), [web/src/__tests__/server/llm-api-key.servertest.ts:15-16]()

### Base URL Validation
To prevent SSRF (Server-Side Request Forgery), Langfuse validates `baseURL` inputs via `validateLlmConnectionBaseURL`. It blocks local hostnames (e.g., `localhost`, `127.0.0.1`) and enforces HTTPS on Langfuse Cloud. [web/src/features/llm-api-key/server/router.ts:171-190]()

Sources: [web/src/features/llm-api-key/server/router.ts:171-190]()

### Masking in UI
The `getDisplaySecretKey` utility generates a safe string for display by showing only the last few characters of the key. For complex keys like JSON service accounts, it extracts a small identifying slice. [web/src/features/llm-api-key/server/router.ts:44-54]()

---

## Playground Integration

The managed API keys are utilized by the `fetchLLMCompletion` function, which acts as the central gateway for all LLM interactions within Langfuse, including the Playground.

### Data Flow for LLM Completion

```mermaid
sequenceDiagram
    participant UI as "ModelParameters (web/src/components/ModelParameters/index.tsx)"
    participant Router as "llmApiKeyRouter (web/src/features/llm-api-key/server/router.ts)"
    participant DB as "PostgreSQL (Prisma)"
    participant Shared as "fetchLLMCompletion (packages/shared/src/server/llm/fetchLLMCompletion.ts)"
    participant Provider as "LLM_Provider_API"

    UI->>Router: Request Completion (ProjectID, ModelParams)
    Router->>DB: Query LlmApiKeys (ProjectID, Provider)
    DB-->>Router: Encrypted Key + Config
    Router->>Shared: Call with Decrypted Key
    Shared->>Shared: Map to LangChain Adapter (e.g. ChatOpenAI, ChatAnthropic)
    Shared->>Provider: HTTP Request (API Key in Headers)
    Provider-->>Shared: Completion Response
    Shared-->>Router: Normalized Result
    Router-->>UI: Display Text/Tool Calls
```

Sources: [packages/shared/src/server/llm/fetchLLMCompletion.ts:171-205](), [web/src/components/ModelParameters/index.tsx:93-110]()

### Implementation Details
- **Decryption**: The `fetchLLMCompletion` function decrypts the `secretKey` and `extraHeaders` immediately before the request is dispatched using `decrypt`. [packages/shared/src/server/llm/fetchLLMCompletion.ts:219-220]()
- **Model Selection**: The UI filters available models based on configured `customModels` and `withDefaultModels`. [web/src/components/ModelParameters/index.tsx:57-89]()
- **Thinking/Reasoning**: For Gemini 2.5+ models, the system supports `maxReasoningTokens` to control model "thinking" budgets and reasoning extraction. [web/src/components/ModelParameters/index.tsx:179-194](), [packages/shared/src/server/llm/fetchLLMCompletion.ts:69-76]()
- **Structured Output**: The system uses `structuredOutputSchema` to enforce JSON formats for evaluations and playground testing. [packages/shared/src/server/llm/fetchLLMCompletion.ts:183-189]()

Sources: [packages/shared/src/server/llm/fetchLLMCompletion.ts:171-220](), [web/src/components/ModelParameters/index.tsx:140-195]()