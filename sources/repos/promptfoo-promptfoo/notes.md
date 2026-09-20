# promptfoo/promptfoo — DeepWiki Notes

Source: https://deepwiki.com/promptfoo/promptfoo

## Summary

Promptfoo is an open-source toolkit for testing prompts, models, agents, and retrieval-augmented applications through a CLI, Node.js API, and local web interface. Its central abstraction is a declarative test suite that expands prompts, providers, and test cases into an evaluation matrix. Each cell renders variables into a prompt, invokes a provider, transforms the response, executes assertions, and persists a scored result. This makes model and prompt comparisons repeatable while retaining practical controls for concurrency, rate limits, caching, retries, and CI execution.

The assertion system deliberately combines several kinds of evidence. Deterministic checks cover exact values, regular expressions, JSON schemas, latency, and cost. Model-assisted checks apply rubrics, factuality judgments, semantic similarity, or comparative scoring. Trace-aware checks inspect an agent's actual tool calls, arguments, ordering, and spans. Assertion sets and thresholds then combine these signals into a final grade. A provider interface keeps the engine independent of any single model vendor and also supports generic HTTP, scripts, and agent SDKs.

Promptfoo applies the same evaluation machinery to security testing. Red-team plugins define which vulnerability or policy failure to probe, while strategies define how a base probe is transformed or delivered. Keeping the risk target separate from the attack method permits reusable combinations, collection expansion, severity metadata, and framework mappings. Stateful attack providers extend this model with attacker-target-judge loops, scoring, branching, memory, and backtracking for multi-turn adversarial exploration.

OpenTelemetry connects behavioral outcomes to execution evidence. Promptfoo can instrument provider calls, ingest external OTLP traces, store spans locally, and normalize them into agent trajectories. Evaluations can therefore test not only the final answer but also whether required tools were used with correct arguments and in the intended order. Across these systems, the durable design lesson is to treat evaluation as reproducible software testing: keep configuration declarative, execution provider-neutral, grading multi-layered, results traceable, and adversarial generation composable.

## Knowledge Map

- Declarative suites expand prompts, providers, and test cases into an evaluation matrix.
- Assertions combine deterministic, model-graded, and execution-trace evidence.
- A provider contract decouples evaluation logic from model vendors and runtimes.
- Red-team plugins select risks; strategies select attack delivery methods.
- Stateful attacker-target-judge loops explore multi-turn vulnerabilities.
- OpenTelemetry traces make agent behavior testable, not merely observable.

## Key Takeaways

- Evaluate prompts and models with versioned test cases instead of informal spot checks.
- Prefer deterministic assertions when possible and reserve model graders for subjective criteria.
- Keep vulnerability definitions independent from attack transformations so both remain reusable.
- Validate agent trajectories when a correct final answer could hide an unsafe or incorrect process.
- Preserve configuration, results, costs, traces, and grading reasons for reproducible comparison.

## Source Reference

The ingested DeepWiki material is preserved below for detailed review and code-level citations.


# promptfoo Documentation Index

This file contains links to all extracted documents.
Please refer to the files below for detailed information.

- [Introduction](promptfoo/Introduction.md)
- [Overview](promptfoo/Overview.md)
- [Test Suite and Configuration](promptfoo/Test_Suite_and_Configuration.md)
- [Assertions and Grading](promptfoo/Assertions_and_Grading.md)
- [Data Models and Persistence](promptfoo/Data_Models_and_Persistence.md)
- [Utilities and Output Generation](promptfoo/Utilities_and_Output_Generation.md)
- [Provider System](promptfoo/Provider_System.md)
- [Provider Loading and Registry](promptfoo/Provider_Loading_and_Registry.md)
- [AWS Bedrock Integration](promptfoo/AWS_Bedrock_Integration.md)
- [OpenAI Integration](promptfoo/OpenAI_Integration.md)
- [Python and Script Providers](promptfoo/Python_and_Script_Providers.md)
- [Agent SDK Providers](promptfoo/Agent_SDK_Providers.md)
- [Provider Ecosystem](promptfoo/Provider_Ecosystem.md)
- [CLI System](promptfoo/CLI_System.md)
- [Eval Command](promptfoo/Eval_Command.md)
- [Red Team Architecture](promptfoo/Red_Team_Architecture.md)
- [Plugins and Metadata](promptfoo/Plugins_and_Metadata.md)
- [Provider Manager and Shared Utilities](promptfoo/Provider_Manager_and_Shared_Utilities.md)
- [Web Interface](promptfoo/Web_Interface.md)
- [Filtering and Search](promptfoo/Filtering_and_Search.md)
- [Red Team Setup UI](promptfoo/Red_Team_Setup_UI.md)
- [Backend Server](promptfoo/Backend_Server.md)
- [Red Team Report UI](promptfoo/Red_Team_Report_UI.md)
- [Model Audit Sharing](promptfoo/Model_Audit_Sharing.md)
- [Telemetry and Analytics](promptfoo/Telemetry_and_Analytics.md)
- [OpenTelemetry Tracing](promptfoo/OpenTelemetry_Tracing.md)
- [Model Audit ModelAudit](promptfoo/Model_Audit_ModelAudit.md)
- [Code Scanning](promptfoo/Code_Scanning.md)
- [MCP Server](promptfoo/MCP_Server.md)
- [Development Guide](promptfoo/Development_Guide.md)
- [Build System and CICD](promptfoo/Build_System_and_CICD.md)
- [Testing Infrastructure](promptfoo/Testing_Infrastructure.md)
- [Glossary](promptfoo/Glossary.md)

This page documents the AWS Bedrock provider implementation in promptfoo, covering the `AwsBedrockGenericProvider` and `AwsBedrockCompletionProvider` classes, supported model families (Claude, Nova, Llama, Titan, etc.), the Converse API, Application Inference Profiles, extended thinking, guardrails, and multimodal inputs.

---

## Architecture Overview

The Bedrock integration is architected to support multiple AWS Bedrock APIs (InvokeModel, Converse, Async Invoke) through a common base class.

- **`AwsBedrockGenericProvider`**: The base class in `src/providers/bedrock/base.ts` that handles AWS SDK client initialization, credential resolution, and proxy configuration [[src/providers/bedrock/base.ts:16-16]]().
- **`AwsBedrockCompletionProvider`**: Implements the `InvokeModel` API in `src/providers/bedrock/index.ts`. It dispatches model-specific logic to internal handlers based on the model ID [[src/providers/bedrock/index.ts:655-655]]().
- **`AwsBedrockConverseProvider`**: Implements the unified Bedrock Converse API. It supports tool calling and guardrails across different model providers.
- **`AwsBedrockKnowledgeBaseProvider`**: A specialized provider for RAG (Retrieval Augmented Generation) that interacts with AWS Bedrock Knowledge Bases using the `RetrieveAndGenerate` API [[src/providers/bedrock/knowledgeBase.ts:71-74]]().
- **Utility Layer**: `src/providers/bedrock/util.ts` provides message parsing (e.g., `novaParseMessages`) and content extraction logic [[src/providers/bedrock/util.ts:21-21]]().

**Code Entity Mapping**

```mermaid
graph TD
  A["Provider URI prefix"] --> B["bedrock:<modelId>"]
  A --> C["bedrock:converse:<modelId>"]
  A --> D["bedrock:kb:<kbId>"]

  B --> H["AwsBedrockCompletionProvider\n(src/providers/bedrock/index.ts)"]
  C --> I["AwsBedrockConverseProvider\n(src/providers/bedrock/converse.ts)"]
  D --> J["AwsBedrockKnowledgeBaseProvider\n(src/providers/bedrock/knowledgeBase.ts)"]

  H -- extends --> K["AwsBedrockGenericProvider\n(src/providers/bedrock/base.ts)"]
  I -- extends --> K
  J -- extends --> K
```

Sources: [src/providers/bedrock/base.ts:16-16](), [src/providers/bedrock/index.ts:19-21](), [src/providers/bedrock/knowledgeBase.ts:71-74]()

---

## Core Classes and Interfaces

### `AwsBedrockGenericProvider`
The foundation for all Bedrock-based providers. Key responsibilities include:
- **Client Management**: Lazily initializes the `BedrockRuntime` client using `getBedrockInstance()` [[src/providers/bedrock/base.ts:50-50]]().
- **Retry Logic**: Configures `maxAttempts` (default 10) and `retryMode` ('adaptive') [[test/providers/bedrock/index.test.ts:192-193]]().
- **Proxy Support**: Automatically detects `HTTP_PROXY`/`HTTPS_PROXY` and configures a `ProxyAgent` via `@smithy/node-http-handler` [[test/providers/bedrock/index.test.ts:157-162]]().

### `AwsBedrockKnowledgeBaseProvider`
This class allows querying existing AWS Bedrock Knowledge Bases.
- **Configuration**: Requires a `knowledgeBaseId` [[src/providers/bedrock/knowledgeBase.ts:85-89]]().
- **RAG Execution**: Uses `RetrieveAndGenerateCommand` from the `@aws-sdk/client-bedrock-agent-runtime` package [[src/providers/bedrock/knowledgeBase.ts:116-125]]().
- **Citations**: Automatically extracts and includes citation metadata in the response [[src/providers/bedrock/knowledgeBase.ts:35-65]]().

Sources: [src/providers/bedrock/base.ts:16-140](), [src/providers/bedrock/knowledgeBase.ts:71-134](), [test/providers/bedrock/index.test.ts:180-196]()

---

## Authentication and Setup

Promptfoo resolves AWS credentials in the following order [[site/docs/providers/aws-bedrock.md:26-31]]():
1. **Config Explicit**: `accessKeyId` and `secretAccessKey` provided in the YAML `config` block [[site/docs/providers/aws-bedrock.md:47-50]]().
2. **Environment**: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.
3. **Local Files**: `~/.aws/credentials`.
4. **IAM**: Roles on EC2/ECS/Lambda.

**Bearer Token Support**: If `apiKey` is provided in the config or `AWS_BEARER_TOKEN_BEDROCK` is set, the provider uses a custom header interceptor to send `Authorization: Bearer <token>` instead of SigV4 signing [[test/providers/bedrock/index.test.ts:152-152]]().

Sources: [site/docs/providers/aws-bedrock.md:26-53](), [test/providers/bedrock/index.test.ts:198-224](), [src/providers/bedrock/knowledgeBase.ts:111-124]()

---

## Model Support and Configuration

### Supported Families
The `BedrockModelFamily` type identifies the handler logic for different foundation models [[src/providers/bedrock/index.ts:36-62]]():

| Family | Handler Example |
|---|---|
| `claude` | Anthropic Claude 3/3.5/3.7/4.x |
| `nova` | Amazon Nova Micro/Lite/Pro |
| `llama` | Meta Llama 2/3/3.1/3.2/3.3/4 |
| `mistral` | Mistral 7B, Mixtral 8x7B |
| `titan` | Amazon Titan Text Express/Lite/Premier |
| `deepseek`| DeepSeek models |

### Extended Thinking (Reasoning)
Promptfoo supports the "thinking" capabilities for modern models:
- **Claude**: Configured via the `thinking` object with `budget_tokens`. Promptfoo includes utilities to clamp tokens for thinking budgets [[src/providers/bedrock/index.ts:104-105]]() [[src/providers/anthropic/util.ts:35-35]]().
- **Nova**: Uses `novaParseMessages` and `novaOutputFromMessage` to handle specialized Nova formatting [[src/providers/bedrock/index.ts:21-21]]().

Sources: [src/providers/bedrock/index.ts:36-62](), [src/providers/bedrock/index.ts:90-105](), [src/providers/anthropic/util.ts:35-49]()

---

## Converse API Integration

The `bedrock:converse:` prefix utilizes the unified interface for Bedrock models.

**Data Flow: Converse API**

```mermaid
sequenceDiagram
  participant E as Evaluator
  participant P as AwsBedrockConverseProvider
  participant B as BedrockRuntime (SDK)

  E->>P: callApi(prompt)
  P->>P: parseMessages (via anthropic/util)
  P->>B: ConverseCommand(input)
  B-->>P: ConverseCommandOutput
  P->>P: Extract content blocks (text/toolUse/reasoning)
  P-->>E: ProviderResponse
```

### Key Converse Features
- **Extended Thinking**: Enable Claude's reasoning capabilities by setting `thinking` in the provider config [[site/docs/providers/aws-bedrock.md:173-177]]().
- **Unified Interface**: Supports a single interface for reasoning, tool calling, and guardrails across different model providers [[site/docs/providers/aws-bedrock.md:152-154]]().

Sources: [site/docs/providers/aws-bedrock.md:150-177](), [src/providers/bedrock/index.ts:1-21]()

---

## Application Inference Profiles

Inference profiles allow you to use a single ARN to access models across multiple regions for high availability [[site/docs/providers/aws-bedrock.md:55-57]]().

When using an inference profile ARN, the `inferenceModelType` must be specified in the configuration to ensure the correct request schema is used [[site/docs/providers/aws-bedrock.md:61-67]]():

```yaml
providers:
  - id: bedrock:arn:aws:bedrock:us-east-1:123456789012:application-inference-profile/my-profile
    config:
      inferenceModelType: 'claude'
      region: 'us-east-1'
```

Sources: [site/docs/providers/aws-bedrock.md:55-100](), [src/providers/bedrock/index.ts:68-70]()

---

## Multimodal and Media Support

### Vision
- **Claude/Nova**: Supports image inputs via the standard message parsing logic.
- **Llama 3.2 Vision**: Structures image and text inputs using specialized formatters like `formatPromptLlama32Vision` [[test/providers/bedrock/index.test.ts:22-22]]().

### Video Generation
Promptfoo supports video generation using models like **Amazon Nova Reel** [[examples/amazon-bedrock/README.md:9-9]](). These integrations often involve specialized async invocation paths or specific model configuration parameters.

Sources: [test/providers/bedrock/index.test.ts:17-27](), [examples/amazon-bedrock/README.md:1-9]()

# Anthropic Provider




This page documents the Anthropic provider implementation in promptfoo, covering the `anthropic:messages:*` and `anthropic:completion:*` provider families. It explains the provider's data flow, supported models, message formatting logic, tool use, extended thinking, vision support, and cost calculation.

For Claude models accessed through AWS infrastructure, see [AWS Bedrock Integration](#3.3). For how providers are loaded from configuration strings, see [Provider Loading and Registry](#3.1).

---

## Overview

The Anthropic provider integrates directly with the [Anthropic Messages API](https://docs.anthropic.com/en/api/messages) and the legacy completions API. It is primarily activated by provider IDs of the form `anthropic:messages:<model-id>`. The core utility logic lives in `src/providers/anthropic/util.ts`, with types defined in `src/providers/anthropic/types.ts`.

The Bedrock provider also reuses the Anthropic message formatting utilities. Specifically, `outputFromMessage` and `parseMessages` are imported from the Anthropic util module at `src/providers/bedrock/index.ts` [src/providers/bedrock/index.ts:15-17]().

Sources: [src/providers/anthropic/util.ts:1-50](), [src/providers/anthropic/types.ts:1-120](), [src/providers/bedrock/index.ts:15-17]()

---

## Provider ID Format

```
anthropic:messages:<model-id>
anthropic:completion:<model-id>
```

**Examples:**
```
anthropic:messages:claude-3-7-sonnet-latest
anthropic:messages:claude-3-5-sonnet-20241022
anthropic:completion:claude-2.1
```

The `anthropic:` prefix routes to the Anthropic provider family. The `messages:` segment selects the Messages API endpoint (standard for Claude 3+), while `completion:` selects the legacy text completion endpoint [src/providers/registry.ts:13-15]().

Sources: [src/providers/anthropic/messages.ts:1-40](), [src/providers/anthropic/completion.ts:1-15](), [src/providers/registry.ts:13-15]()

---

## Supported Models

The `ANTHROPIC_MODELS` constant [src/providers/anthropic/util.ts:15-187]() defines recognized models and their per-token costs.

### Current Model Roster (Selected)

| Model ID | Input Cost (per MTok) | Output Cost (per MTok) |
|---|---|---|
| `claude-fable-5` | $10.00 | $50.00 |
| `claude-opus-5` | $5.00 | $25.00 |
| `claude-sonnet-5` | $3.00 | $15.00 |
| `claude-opus-4-8` | $5.00 | $25.00 |
| `claude-opus-4-7` | $5.00 | $25.00 |
| `claude-3-7-sonnet-20250219` | $3.00 | $15.00 |
| `claude-3-5-sonnet-20241022` | $3.00 | $15.00 |
| `claude-3-5-haiku-20241022` | $0.80 | $4.00 |
| `claude-3-opus-20240229` | $15.00 | $75.00 |
| `claude-sonnet-4-6` | $3.00 | $15.00 |
| `claude-opus-4-6` | $5.00 | $25.00 |
| `claude-haiku-4-5` | $1.00 | $5.00 |
| `claude-mythos-preview` | $25.00 | $125.00 |

**Note:** Manual sampling parameters (`temperature`, `top_p`, `top_k`) are deprecated for Claude Opus 4.7+, 4.8, and Claude 5 models. `isSamplingParamsDeprecatedClaudeModel` [src/providers/anthropic/util.ts:251-274]() identifies these models to prevent invalid parameter submission.

Sources: [src/providers/anthropic/util.ts:15-187](), [src/providers/anthropic/util.ts:251-274]()

---

## Architecture and Data Flow

The `AnthropicMessagesProvider` [src/providers/anthropic/messages.ts:31]() extends `AnthropicGenericProvider` [src/providers/anthropic/generic.ts:101](), which handles shared logic like API key resolution and Claude Code OAuth authentication.

**Diagram: Anthropic Provider Request Pipeline**

```mermaid
flowchart TD
    A["Prompt String\n(raw text or JSON)"] --> B["parseMessages()"]
    B --> C["system: TextBlockParam[]"]
    B --> D["extractedMessages: MessageParam[]"]
    B --> E["thinking: ThinkingConfigParam"]

    subgraph "AnthropicMessagesProvider.callApi()"
        F["Anthropic SDK\n(messages.create)"]
        G["config.tools"] --> H["processAnthropicTools()"]
        H --> I["processedTools"]
        H --> J["requiredBetaFeatures\n(beta header strings)"]

        subgraph "Auth Logic"
            K["getApiKey()"]
            L["loadClaudeCodeCredential()"]
        end
    end

    C & D & E & I & J & K & L --> F
    F --> M["Anthropic.Messages.Message"]
    M --> N["outputFromMessage(message, showThinking)"]
    N --> O["string output"]
    M --> P["getTokenUsage()"]
    P --> Q["TokenUsage"]
    Q --> R["calculateAnthropicCost()"]
    R --> S["cost: number | undefined"]
```

Sources: [src/providers/anthropic/messages.ts:31](), [src/providers/anthropic/util.ts:46-49](), [src/providers/anthropic/generic.ts:101-188]()

---

## Authentication via Claude Code Session

Promptfoo supports reusing OAuth credentials from an active Claude Code session [src/providers/anthropic/generic.ts:148-183](). This allows Claude Pro/Max subscribers to run evaluations without a separate Console API key.

To enable this, set `apiKeyRequired: false` in the provider configuration [site/docs/providers/anthropic.md:30-37]().

**Credential Resolution Order:**
1. macOS Keychain: `Claude Code-credentials` [site/docs/providers/anthropic.md:41]().
2. File System: `$HOME/.claude/.credentials.json` on Linux/macOS or `%USERPROFILE%\.claude\.credentials.json` on Windows [site/docs/providers/anthropic.md:42]().

When using OAuth, Promptfoo injects the required `CLAUDE_CODE_IDENTITY_PROMPT` ("You are Claude Code...") [src/providers/anthropic/messages.ts:25]() and specific beta headers `CLAUDE_CODE_OAUTH_BETA_FEATURES` [src/providers/anthropic/messages.ts:26]().

Sources: [src/providers/anthropic/generic.ts:148-183](), [site/docs/providers/anthropic.md:28-49](), [src/providers/anthropic/messages.ts:25-30]()

---

## Message Formatting: `parseMessages`

`parseMessages(messages: string)` [src/providers/anthropic/util.ts:47]() converts the raw prompt string into the structure expected by the Anthropic Messages API.

**Image handling:** Image blocks are processed to extract base64 data and MIME types from data URLs using `parseDataUrl` [src/providers/anthropic/util.ts:1]().

**Diagram: `parseMessages` Entity Mapping**

```mermaid
flowchart LR
    subgraph "Natural Language Space"
        P["Prompt String"]
    end
    subgraph "Code Entity Space"
        F["parseMessages()"]
        M["Anthropic.MessageParam[]"]
        S["Anthropic.TextBlockParam[] (System)"]
        T["Anthropic.ThinkingConfigParam"]
        IMG["parseDataUrl()"]
    end
    P --> F
    F --> S
    F --> M
    F --> T
    M --> IMG
```

Sources: [src/providers/anthropic/util.ts:47](), [src/providers/anthropic/util.ts:1]()

---

## Output Processing: `outputFromMessage`

`outputFromMessage(message, showThinking)` [src/providers/anthropic/util.ts:46]() converts API response blocks back into strings.

- **Thinking Blocks:** If `showThinking` is true, reasoning is rendered in the output [src/providers/anthropic/util.ts:46]().
- **Tool Use:** Tool calls are serialized as JSON strings within the response [test/providers/anthropic/messages.test.ts:183-187]().
- **Refusal Details:** If a model refuses a request, details are extracted via `getRefusalDetails` [src/providers/anthropic/util.ts:38]().

Sources: [src/providers/anthropic/util.ts:46](), [test/providers/anthropic/messages.test.ts:183-187](), [src/providers/anthropic/util.ts:38]()

---

## Tool Use and Extended Thinking

### processAnthropicTools
This function [src/providers/anthropic/util.ts:48]() handles specialized Anthropic tools:
- **Web Tools:** Supports `web_search_20250108`, `web_fetch_20250108`, and future variants [src/providers/anthropic/types.ts:7-12]().
- **Beta Headers:** Automatically enables required beta headers based on the tools and configuration used [src/providers/anthropic/messages.ts:26]().

### Extended Thinking
Controlled via the `thinking` config [src/providers/anthropic/types.ts:81-108]().
- **Types:** `enabled`, `adaptive`, or `disabled`.
- **Budget:** Requires `budget_tokens` when enabled.
- **Normalization:** Models like Fable 5 and Mythos 5 use "always-on" adaptive thinking [src/providers/anthropic/util.ts:240-249](). Promptfoo normalizes these via `normalizeClaudeThinkingConfig` [src/providers/anthropic/util.ts:45]().

Sources: [src/providers/anthropic/util.ts:48](), [src/providers/anthropic/types.ts:7-12](), [src/providers/anthropic/util.ts:45](), [src/providers/anthropic/util.ts:240-249]()

---

## Cost Calculation

`calculateAnthropicCost` [src/providers/anthropic/util.ts:34]() handles standard and cache-aware pricing.

**Cache Pricing:**
Supports `cache_read_input_tokens` and `cache_creation_input_tokens`.
- **Cache Reads:** Typically priced at a lower rate than base input.
- **Cache Writes:** Typically priced at a higher rate than base input.

**Tiered Logic:**
The provider checks for model-specific pricing tiers defined in `ANTHROPIC_MODELS` [src/providers/anthropic/util.ts:15-187]().

Sources: [src/providers/anthropic/util.ts:34](), [src/providers/anthropic/util.ts:15-187]()

---

## Relationship to Bedrock Provider

The Bedrock provider reuses Anthropic utility functions for Claude models [src/providers/bedrock/index.ts:8-17]().

**Diagram: Bedrock vs Anthropic Provider Structure**

```mermaid
flowchart TD
    subgraph "Anthropic Module"
        AM["AnthropicMessagesProvider"]
        AU["util.ts: parseMessages"]
        AU2["util.ts: outputFromMessage"]
    end
    subgraph "Bedrock Module"
        BM["AwsBedrockGenericProvider"]
        BC["AwsBedrockConverseProvider"]
    end
    AM --> AU
    BM -->|"imports"| AU
    BC -->|"imports"| AU2
```

Sources: [src/providers/bedrock/index.ts:8-17](), [src/providers/anthropic/messages.ts:31-49]()
Agent SDK providers enable promptfoo to evaluate complex, multi-step AI agents. Unlike standard completion providers that return a single text response, these providers manage agentic execution lifecycles, including tool use, file system operations, session persistence, and multi-turn reasoning loops.

## Overview of Agentic Execution

Agent SDK providers wrap specialized SDKs (Anthropic Claude Agent SDK, OpenAI Codex SDK, and OpenCode SDK) to expose their agentic capabilities to the promptfoo evaluation engine.

### Key Capabilities
- **Working Directory Management**: Agents operate within a controlled filesystem path, allowing them to read and write files during an evaluation turn [src/providers/agentic-utils.ts:63-100]().
- **Tool & Skill Execution**: Capture and assert on tool calls (e.g., shell commands, filesystem edits, MCP tool usage) [src/providers/claude-agent-sdk.ts:158-201]().
- **Session Persistence**: Reuse session or thread IDs across multiple test cases to evaluate long-term memory and state management [src/providers/openai/codex-sdk.ts:97-101]().
- **Deep Tracing**: Integration with OpenTelemetry to record the "trajectory" of an agent's internal steps as spans [src/providers/claude-agent-sdk.ts:158-201]().

### Data Flow: Natural Language to Agentic Code Entities

The following diagram illustrates how a natural language prompt in a `promptfooconfig.yaml` is transformed into an agentic execution session.

**Agent Execution Pipeline**
```mermaid
graph TD
    subgraph "Natural Language Space"
        Config["promptfooconfig.yaml"]
        Prompt["'Refactor auth.ts to use async'"]
    end

    subgraph "Code Entity Space"
        Provider["ClaudeCodeSDKProvider\n(src/providers/claude-agent-sdk.ts)"]
        WorkingDir["resolveAgenticWorkingDir()\n(src/providers/agentic-utils.ts)"]
        Cache["initializeAgenticCache()\n(src/providers/agentic-utils.ts)"]
        SDK["@anthropic-ai/claude-agent-sdk"]
    end

    Config -->|"id: anthropic:claude-agent-sdk"| Provider
    Config -->|"config.working_dir"| WorkingDir
    Prompt -->|"callApi(prompt)"| Provider
    Provider --> WorkingDir
    Provider --> Cache
    Provider -->|"query()"| SDK
    SDK -->|"Tool Use: Write/Edit"| WorkingDir
```
Sources: [src/providers/claude-agent-sdk.ts:28-29](), [src/providers/agentic-utils.ts:63-100](), [site/docs/providers/claude-agent-sdk.md:99-112]()

---

## Claude Agent SDK Provider (`ClaudeCodeSDKProvider`)

The `ClaudeCodeSDKProvider` (aliased as `anthropic:claude-code` or `anthropic:claude-agent-sdk`) integrates the Anthropic Claude Agent SDK [src/providers/claude-agent-sdk.ts:14-16](). It supports advanced features like "Extended Thinking" and MCP (Model Context Protocol) tool integration [src/providers/claude-agent-sdk.ts:31]().

### Implementation Details
- **Class**: `ClaudeCodeSDKProvider` [src/providers/claude-agent-sdk.ts:14]().
- **Dependency**: Requires `@anthropic-ai/claude-agent-sdk` [site/docs/providers/claude-agent-sdk.md:24-28]().
- **Permissions**: Supports multiple modes including `default`, `plan`, `acceptEdits`, and `bypassPermissions` [site/docs/providers/claude-agent-sdk.md:120-132]().
- **Models**: Supports model aliases like `claude-3-5-sonnet-latest` and `claude-3-7-sonnet-latest` [src/providers/claude-agent-sdk.ts:13-16]().

### Tool Span Emission
The provider captures internal tool calls and emits them as OpenTelemetry spans using `emitToolSpan`. This allows promptfoo to visualize the agent's trajectory in the UI.

| Function | Purpose |
| :--- | :--- |
| `emitToolSpan` | Creates a child span for a tool call, including input, output, and error status [src/providers/claude-agent-sdk.ts:166-209](). |
| `appendPromptfooResourceAttrs` | Injects promptfoo trace and parent span IDs into the environment for downstream agent processes [src/providers/claude-agent-sdk.ts:109-129](). |
| `FS_READONLY_ALLOWED_TOOLS` | Defines the default set of safe tools (read, list, grep, glob) [src/providers/claude-agent-sdk.ts:15](). |

Sources: [src/providers/claude-agent-sdk.ts:109-209](), [site/docs/providers/claude-agent-sdk.md:15-21]()

---

## OpenAI Codex SDK Provider (`OpenAICodexSDKProvider`)

The `OpenAICodexSDKProvider` (aliased as `openai:codex-sdk`) provides a bridge to OpenAI's agentic coding capabilities [src/providers/openai/codex-sdk.ts:95-112](). It emphasizes thread management and Git-aware safety checks.

### Thread Management
The provider manages conversations via the `Thread` class from `@openai/codex-sdk` [src/providers/openai/codex-sdk.ts:108-112]().
- **Ephemeral Threads**: Created per call by default [src/providers/openai/codex-sdk.ts:109]().
- **Persistent Threads**: If `persist_threads` is enabled, threads are pooled by prompt template and config cache key [src/providers/openai/codex-sdk.ts:110]().
- **Thread Resumption**: Can resume a specific `thread_id` from `~/.codex/sessions` [src/providers/openai/codex-sdk.ts:111]().

### Configuration Parameters
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `sandbox_mode` | `SandboxMode` | Controls filesystem access (`read-only`, `workspace-write`, `danger-full-access`) [src/providers/openai/codex-sdk.ts:117](). |
| `reasoning_effort` | `ReasoningEffort` | Sets reasoning intensity (e.g., `minimal`, `medium`, `xhigh`, `ultra`) [src/providers/openai/codex-sdk.ts:150](). |
| `web_search_mode` | `WebSearchMode` | Controls web access (`disabled`, `cached`, `live`) [src/providers/openai/codex-sdk.ts:158](). |

Sources: [src/providers/openai/codex-sdk.ts:95-163](), [site/docs/providers/openai-codex-sdk.md:19-25]()

---

## OpenCode SDK Provider (`OpenCodeSDKProvider`)

The `OpenCodeSDKProvider` integrates OpenCode, an open-source AI coding agent supporting over 75 LLM providers [src/providers/opencode-sdk.ts:30-51]().

### Architecture
OpenCode uses a client-server model. The promptfoo provider can either connect to an existing server via `baseUrl` or manage a local server lifecycle automatically [src/providers/opencode-sdk.ts:39-44](). It uses `createOpencode` to initialize the environment [src/providers/opencode-sdk.ts:169]().

### Permissions and Rulesets
Promptfoo transforms user-friendly configuration objects into the `PermissionRuleset` array expected by the OpenCode v2 API [src/providers/opencode-sdk.ts:148-156]().

**Permission Mapping Logic**
```mermaid
graph LR
    subgraph "promptfooconfig.yaml"
        UserPerm["permission:\n  edit:\n    '*.ts': allow"]
    end

    subgraph "Internal Processing"
        Convert["convertPermissionConfigToRuleset()\n(src/providers/opencode-sdk.ts)"]
    end

    subgraph "OpenCode SDK v2"
        Rule["OpenCodePermissionRule\n{ permission: 'edit',\n  pattern: '*.ts',\n  action: 'allow' }"]
    end

    UserPerm --> Convert
    Convert --> Rule
```
Sources: [src/providers/opencode-sdk.ts:148-156](), [test/providers/opencode-sdk.test.ts:9-12]()

---

## Shared Agentic Utilities

All agentic providers share a set of core utilities in `src/providers/agentic-utils.ts` to ensure consistent behavior across different SDKs.

### Working Directory Management
`resolveAgenticWorkingDir` determines where the agent will perform its operations. If no `working_dir` is provided in the config, it creates a temporary directory using `os.tmpdir()` and `fs.mkdtempSync` that is cleaned up after execution [src/providers/agentic-utils.ts:28]().

### Caching and State
`initializeAgenticCache` sets up the caching layer for agentic runs. This allows promptfoo to skip expensive agent executions if the prompt, config, and relevant filesystem state have not changed [src/providers/agentic-utils.ts:27]().
- `generateCacheKey`: Creates a unique hash based on the provider, prompt, and configuration [src/providers/opencode-sdk.ts:14]().
- `getCachedResponse`: Retrieves previously stored agent results [src/providers/agentic-utils.ts:26]().

### Skill Comparison
Agent SDK providers enable "Skill Comparison" by pointing different providers at different `working_dir` fixtures, each containing a unique version of a `SKILL.md` file [site/docs/providers/openai-codex-sdk.md:36]().
- **Heuristic Detection**: Promptfoo infers skill usage from direct command references to `SKILL.md` [site/docs/providers/openai-codex-sdk.md:36]().
- **Metadata**: Results include `metadata.toolCalls` for debugging [src/providers/claude-agent-sdk.ts:71-78]().

Sources: [src/providers/agentic-utils.ts:1-100](), [src/providers/claude-agent-sdk.ts:25-29]()

---

## OpenTelemetry (OTEL) Integration

Agent SDK providers integrate with promptfoo's tracing system to provide visibility into the "black box" of agent execution.

### Tracing Flow
1. **Trace Propagation**: The provider retrieves the `traceparent` using `getTraceparent()` from `genaiTracer` [src/providers/claude-agent-sdk.ts:17]().
2. **Resource Attributes**: Promptfoo-specific metadata (`PROMPTFOO_RESOURCE_ATTR_TRACE_ID`, `PROMPTFOO_RESOURCE_ATTR_PARENT_SPAN_ID`) is appended to the environment via `appendPromptfooResourceAttrs` [src/providers/claude-agent-sdk.ts:109-129]().
3. **Span Wrapping**: The `callApi` logic is wrapped in `withGenAISpan` to ensure the entire agent turn is captured as a single high-level span [src/providers/claude-agent-sdk.ts:21]().
4. **Sub-spans**: Internal tool calls are emitted as child spans via `emitToolSpan`, creating a hierarchical view of the agent's reasoning and actions [src/providers/claude-agent-sdk.ts:166-209]().

Sources: [src/providers/claude-agent-sdk.ts:6-22](), [src/providers/claude-agent-sdk.ts:166-209](), [src/tracing/genaiTracer.ts:1-22]()
## Purpose and Scope

This document covers promptfoo's assertion and grading system, which validates LLM outputs against expected values or conditions. The system provides both deterministic tests (exact matches, regex patterns, JSON validation) and model-assisted evaluations (similarity scoring, LLM-rubric grading, G-Eval, and trajectory analysis). It handles the execution of individual assertions, the orchestration of assertion sets, and the calculation of final scores and metrics.

For information about the overall evaluation engine that orchestrates these assertions, see [Evaluation Engine](2.1). For configuration syntax and test case setup, see [Test Suite and Configuration](2.2).

## System Overview

The assertion system operates as a layer between the evaluation engine and the actual validation logic, processing LLM outputs through various matching strategies. The `Evaluator` class in `src/evaluator.ts` triggers the assertion engine after receiving a response from a provider.

### Diagram: Assertion Engine Architecture
This diagram bridges the evaluation orchestration in `src/evaluator.ts` to the specialized matching logic in `src/assertions/` and `src/matchers/`.

```mermaid
graph TB
    subgraph "Evaluation Engine (src/evaluator.ts)"
        runEval["runEval()"]
        evaluate["evaluate()"]
    end

    subgraph "Assertion Orchestration (src/assertions/index.ts)"
        runAssertions["runAssertions()"]
        runAssertion["runAssertion()"]
        AssertionsResult["AssertionsResult (class)"]
    end

    subgraph "Core Matchers (src/matchers/)"
        matchesSimilarity["matchesSimilarity()"]
        matchesLlmRubric["matchesLlmRubric()"]
        matchesFactuality["matchesFactuality()"]
        matchesClosedQa["matchesClosedQa()"]
    end

    subgraph "Assertion Handlers (src/assertions/)"
        handleSimilar["handleSimilar()"]
        handleJavascript["handleJavascript()"]
        handlePython["handlePython()"]
        handleEquals["handleEquals()"]
        handleLlmRubric["handleLlmRubric()"]
        handleGEval["handleGEval()"]
        handleTrajectory["handleTrajectoryToolUsed() etc."]
    end

    subgraph "Provider Integration"
        getGradingProvider["getGradingProvider()"]
        ApiProvider["ApiProvider (interface)"]
    end

    runEval --> runAssertions
    runAssertions --> runAssertion
    runAssertion --> handleSimilar
    runAssertion --> handleJavascript
    runAssertion --> handleLlmRubric
    runAssertion --> handleTrajectory

    handleSimilar --> matchesSimilarity
    handleLlmRubric --> matchesLlmRubric

    matchesSimilarity --> getGradingProvider
    matchesLlmRubric --> getGradingProvider

    getGradingProvider --> ApiProvider

    runAssertion --> AssertionsResult
```

Sources: [src/evaluator.ts:9-15](), [src/assertions/index.ts:10-20](), [src/assertions/index.ts:47-106](), [src/assertions/index.ts:354-450]()

## Core Components

### Matchers Module

The matchers provide the core logic for model-graded evaluation. Unlike deterministic checks, these functions often require an external LLM provider to compute embeddings or perform qualitative judgment.

**Key matching functions:**

| Function | Purpose | Implementation File |
|---|---|---|
| `matchesSimilarity()` | Embedding-based semantic similarity | `src/matchers/similarity.ts` |
| `matchesLlmRubric()` | Open-ended rubric evaluation via LLM | `src/matchers/llmGrading.ts` |
| `matchesFactuality()` | Factual consistency between output and reference | `src/matchers/llmGrading.ts` |
| `matchesClosedQa()` | Yes/no grading based on specific requirements | `src/matchers/llmGrading.ts` |
| `matchesSelectBest()` | Comparison of multiple outputs | `src/matchers/comparison.ts` |

Sources: [src/assertions/index.ts:10-20](), [src/matchers/llmGrading.ts:12-12](), [src/matchers/similarity.ts:20-20]()

#### `matchesSimilarity()`
Computes numeric similarity between two strings. It attempts to use the provider's `callSimilarityApi` if available; otherwise, it fetches embeddings via `callEmbeddingApi` for both strings and calculates the semantic similarity locally.
Sources: [src/matchers/similarity.ts:20-50]()

#### `matchesLlmRubric()`
Sends the LLM output and a rubric (criteria) to a grading provider. It expects a response containing qualitative judgment. The grading prompt is often context-aware, incorporating the original prompt and variables.
Sources: [src/matchers/llmGrading.ts:12-12]()

### Assertion Orchestration

The `src/assertions/index.ts` module is the entry point for all assertion logic. It manages:
1. **Concurrency**: Executes assertions in parallel up to `PROMPTFOO_ASSERTIONS_MAX_CONCURRENCY` (default 3).
2. **Trace Awareness**: Detects if assertions (like `trace-span-count` or `trajectory:*`) require OpenTelemetry trace data and fetches it if needed via `loadTraceData`.
3. **Type Dispatch**: Maps assertion types (e.g., `equals`, `llm-rubric`, `javascript`) to their respective handlers.

Sources: [src/assertions/index.ts:117-117](), [src/assertions/index.ts:139-151](), [src/assertions/index.ts:179-186]()

## Assertion Types

### Deterministic Assertions
These are logical tests that do not require an LLM to evaluate.

| Type | Description | Handler |
|---|---|---|
| `equals` | Exact string or object equality | `handleEquals` |
| `contains` | Substring check | `handleContains` |
| `regex` | Regular expression match | `handleRegex` |
| `is-json` | Validates JSON and optional schema | `handleIsJson` |
| `javascript` | Custom JS function validation | `handleJavascript` |
| `python` | Custom Python script validation | `handlePython` |
| `latency` | Checks if response time is below threshold | `handleLatency` |
| `cost` | Checks if inference cost is below threshold | `handleCost` |

Sources: [src/assertions/index.ts:47-106](), [site/docs/configuration/expected-outputs/deterministic.md:32-79]()

### Model-Graded Assertions
These require an LLM (the "grader") to determine success. Types are explicitly tracked in `MODEL_GRADED_ASSERTION_TYPES`.

| Type | Description |
|---|---|
| `llm-rubric` | Evaluates output against a human-readable criterion. |
| `factuality` | Compares output to a reference for factual agreement. |
| `g-eval` | Qualitative scoring using Chain of Thought (CoT). |
| `answer-relevance` | Measures how well the response answers the query. |
| `similar` | Semantic similarity via embeddings. |

Sources: [src/assertions/index.ts:125-137](), [site/docs/configuration/expected-outputs/model-graded/index.md:1-38]()

### Trace-Aware Assertions
Assertions that inspect the execution path (trajectory) of an agent or the spans of a trace, defined in `TRACE_AWARE_ASSERTION_TYPES`.

| Type | Description |
|---|---|
| `trajectory:tool-used` | Ensure specific tools were called. |
| `trajectory:tool-args-match` | Validate tool argument payloads. |
| `trajectory:tool-sequence` | Check the order of tool calls. |
| `trace-span-count` | Count spans matching specific patterns. |

Sources: [src/assertions/index.ts:139-151](), [src/assertions/index.ts:93-102]()

## Data Structures

### GradingConfig
The `GradingConfig` defines the environment for model-graded assertions, including the specific weights for factuality scoring and the provider to be used as a judge.

| Property | Type | Description |
|---|---|---|
| `rubricPrompt` | string \| string[] | Custom prompt for the grading LLM. |
| `provider` | string \| ApiProvider | The LLM provider used to perform the grading. |
| `factuality` | object | Weights for `subset`, `superset`, `agree`, `disagree`. |

Sources: [src/types/index.ts:165-190]()

### GradingResult
The final output of an assertion execution, containing the success status and detailed scoring metadata.

| Field | Type | Description |
|---|---|---|
| `pass` | boolean | Whether the assertion succeeded. |
| `score` | number | A value from 0 to 1. |
| `reason` | string | Explanation for the score/result. |
| `tokensUsed` | TokenUsage | Tokens consumed by the grading provider. |
| `assertion` | Assertion | The original assertion configuration. |

Sources: [src/types/index.ts:69-69](), [src/evaluator.ts:69-76]()

## Execution Flow: `runAssertion`

When `runAssertion` is called, it follows a specific data flow to transform raw LLM output and trace context into a `GradingResult`.

### Diagram: Assertion Execution Logic
This diagram shows how `runAssertion` in `src/assertions/index.ts` processes a single test requirement.

```mermaid
graph TD
    subgraph "Input Processing"
        RawOutput["Provider Response"]
        TraceData["TraceData (if required)"]
        Transform["assertion.transform (JS/Python)"]
    end

    subgraph "Execution (runAssertion)"
        ValueRes["Resolve assertion.value (Nunjucks/File)"]
        Dispatch["Handler Dispatch (handleEquals, handleLlmRubric, handleTrajectory)"]
    end

    subgraph "Result Generation"
        Inverse["Apply 'not-' inversion if needed"]
        FinalResult["GradingResult"]
    end

    RawOutput --> Transform
    TraceData --> Dispatch
    Transform --> ValueRes
    ValueRes --> Dispatch
    Dispatch --> Inverse
    Inverse --> FinalResult
```

Sources: [src/assertions/index.ts:354-450](), [src/assertions/index.ts:153-159](), [src/evaluator.ts:13-15]()

## Grouping with Assertion Sets
Assertions can be grouped using `assert-set`. An `assert-set` passes if a certain `threshold` of its child assertions pass. If no threshold is provided, all must pass.
Sources: [site/docs/configuration/expected-outputs/index.md:59-95]()
## Purpose and Scope

This document covers the backend Express 5 server that powers promptfoo's web interface. The server provides REST API endpoints for evaluation management, real-time updates via Socket.IO, and serves the React application bundle. Key responsibilities include handling eval CRUD operations, test execution, provider configuration, and red team functionality.

For information about the Results Viewer that consumes these APIs, see page 6.2. For details about real-time updates, see page 6.7.

## Server Architecture

The backend server is built with Express 5 and provides a REST API alongside real-time WebSocket communication. The server architecture follows a modular router pattern with dedicated routes for different functional areas.

### Core Server Components

"Server Architecture and Data Flow"
```mermaid
graph TB
    subgraph "Server Initialization"
        createApp["createApp()"]
        startServer["startServer()"]
        runDbMigrations["runDbMigrations()"]
    end

    subgraph "Express App [server.ts]"
        Middleware["Middleware Stack"]
        APIRoutes["API Routes"]
        StaticServer["Static File Server"]
    end

    subgraph "Real-time Communication"
        SocketIO["Socket.IO Server"]
        SignalWatcher["setupSignalWatcher()"]
        SignalFile["signal.json"]
    end

    subgraph "Route Modules [src/server/routes/]"
        evalRouter["evalRouter<br/>/api/eval"]
        providersRouter["providersRouter<br/>/api/providers"]
        redteamRouter["redteamRouter<br/>/api/redteam"]
        configsRouter["configsRouter<br/>/api/configs"]
        userRouter["userRouter<br/>/api/user"]
        modelAuditRouter["modelAuditRouter<br/>/api/model-audit"]
        tracesRouter["tracesRouter<br/>/api/traces"]
        blobsRouter["blobsRouter<br/>/api/blobs"]
        mediaRouter["mediaRouter<br/>/api/media"]
    end

    createApp --> Middleware
    createApp --> APIRoutes
    createApp --> StaticServer

    startServer --> createApp
    startServer --> SocketIO
    startServer --> runDbMigrations

    SocketIO --> SignalWatcher
    SignalWatcher --> SignalFile

    APIRoutes --> evalRouter
    APIRoutes --> providersRouter
    APIRoutes --> redteamRouter
    APIRoutes --> configsRouter
    APIRoutes --> userRouter
    APIRoutes --> modelAuditRouter
    APIRoutes --> tracesRouter
    APIRoutes --> blobsRouter
    APIRoutes --> mediaRouter
```

Sources: `src/server/server.ts:122-195`(), `src/server/server.ts:12-21`(), `src/migrate.ts:1-25`()

## Middleware Configuration

The Express application is configured with several middleware layers that process all incoming requests before they reach route handlers.

### Middleware Stack

Middleware is applied in this order inside `createApp()` [src/server/server.ts:122-131]():

| Middleware | Purpose | Configuration |
|------------|---------|---------------|
| `cors()` | Cross-Origin Resource Sharing | Allows all origins [src/server/server.ts:127]() |
| `csrfProtection` | CSRF token validation | From `src/server/middleware/csrfProtection.ts` [src/server/server.ts:128]() |
| `compression()` | Response body compression | Default settings [src/server/server.ts:129]() |
| `express.json()` | JSON body parsing | Limit: `100mb` [src/server/server.ts:130]() |
| `express.urlencoded()` | URL-encoded body parsing | Limit: `100mb`, extended mode [src/server/server.ts:131]() |
| `setJavaScriptMimeType` | JS MIME type enforcement | Sets `application/javascript` for JS extensions [src/server/server.ts:70-80]() |

The `setJavaScriptMimeType` function [src/server/server.ts:70-80]() handles extensions like `.js`, `.mjs`, and `.cjs` to prevent MIME type enforcement errors in modern browsers.

Sources: `src/server/server.ts:60-80`(), `src/server/server.ts:122-131`()

## API Routes

The server exposes multiple REST API endpoints organized by functional domain. Routes are modularized into separate router files for maintainability.

### Health and Status

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Server health check, returns version [src/server/server.ts:132-135]() |
| `/api/remote-health` | GET | Checks remote generation service availability via `checkRemoteHealth` [src/server/server.ts:137-152]() |

### Evaluation Management (`/api/eval`)

The `evalRouter` [src/server/routes/eval.ts:42]() handles the core lifecycle of evaluations.

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/job` | POST | Creates new async eval job via `evaluateWithSource` [src/server/routes/eval.ts:132-200]() |
| `/job/:id` | GET | Polls job status from `evalJobService` [src/server/routes/eval.ts:202-223]() |
| `/:id/table` | GET | Returns paginated table data with filtering and comparison [src/server/routes/eval.ts:250-310]() |
| `/:evalId/results/:id/rating` | POST | Submits human rating for a specific output [src/server/routes/eval.ts:320-350]() |

#### Table Data Optimization
The table endpoint [src/server/routes/eval.ts:44-130]() handles large responses by stripping per-cell prompts if the JSON payload exceeds string length limits (`RangeError`). It uses a binary search approach to find the maximum number of prompts that can be safely included before the payload becomes too large for `JSON.stringify` [src/server/routes/eval.ts:91-123]().

### Providers Router (`/api/providers`)

The `providersRouter` [src/server/routes/providers.ts:22]() manages LLM provider interactions.

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/config-status` | GET | Checks if custom provider configurations exist via `getAvailableProviders` [src/server/routes/providers.ts:36-47]() |
| `/test` | POST | Validates provider connectivity via `testProviderConnectivity` [src/server/routes/providers.ts:49-94]() |
| `/discover` | POST | Runs target purpose discovery via `doTargetPurposeDiscovery` [src/server/routes/providers.ts:96-135]() |
| `/http-generator` | POST | Generates HTTP provider config from examples via cloud API [src/server/routes/providers.ts:137-204]() |

### Red Team Router (`/api/redteam`)

The `redteamRouter` [src/server/routes/redteam.ts:34]() handles adversarial test generation.

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/generate-test` | POST | Generates adversarial test cases using specific plugins/strategies [src/server/routes/redteam.ts:39-182]() |

The generation process uses `redteamProviderManager` [src/server/routes/redteam.ts:92]() and applies strategies to test cases produced by plugin factories [src/server/routes/redteam.ts:97-146](). For multi-turn strategies, it utilizes the `generateMultiTurnPrompt` service [src/server/routes/redteam.ts:163-175]().

Sources: `src/server/routes/eval.ts:1-200`(), `src/server/routes/providers.ts:1-135`(), `src/server/routes/redteam.ts:1-182`()

## Request Validation and OpenAPI

The backend uses **Zod** for strict request and response validation. Schemas are centralized in `src/types/api/`.

### Validation Pattern
Route handlers use `.safeParse()` to validate incoming data. If validation fails, `replyValidationError` is used to return a formatted error message [src/server/utils/errors.ts:22-28]().

```typescript
const result = EvalSchemas.CreateJob.Request.safeParse(req.body);
if (!result.success) {
  res.status(400).json({ error: z.prettifyError(result.error) });
  return;
}
```

### OpenAPI Schema Generation
The system uses centralized Zod schemas such as `ServerSchemas` [src/types/api/server.ts]() and `EvalSchemas` [src/types/api/eval.ts]() to ensure type safety across the API surface. These schemas facilitate the generation of OpenAPI documentation.

Sources: `src/server/routes/eval.ts:133-137`(), `src/server/utils/errors.ts:22-28`(), `src/types/api/server.ts:1-100`()

## Error Handling Utilities

Standardized error handling is provided via specialized utility functions:

- **`handleServerError`**: Used during startup to log and wrap `NodeJS.ErrnoException` into `ServerError` objects [src/server/server.ts:84-92]().
- **`sendError`**: Standardized 500-series error response that logs the full error but returns a sanitized message to the client [src/server/utils/errors.ts:10-20]().
- **`replyValidationError`**: Handles Zod validation failures with a 400 status code [src/server/utils/errors.ts:22-28]().

Sources: `src/server/server.ts:84-92`(), `src/server/utils/errors.ts:1-30`()

## Red Team Generation Service

The `redteamTestCaseGenerationService` provides the underlying logic for the redteam API routes.

- **`generateMultiTurnPrompt`**: Orchestrates the creation of multi-turn adversarial dialogues [src/server/routes/redteam.ts:163-175]().
- **`extractGeneratedPrompt`**: A utility to pull the final string output from a generated `TestCase` object [src/server/routes/redteam.ts:154]().
- **`getPluginConfigurationError`**: Validates if a specific plugin is correctly configured for generation [src/server/routes/redteam.ts:60]().

Sources: `src/server/routes/redteam.ts:60-175`(), `src/server/services/redteamTestCaseGenerationService.ts:1-100`()

## Server Lifecycle and Data Flow

The following diagram associates code entities with the server's lifecycle and data persistence.

"Request Lifecycle and Entity Association"
```mermaid
graph TB
    subgraph "Process Lifecycle [server.ts]"
        Start["startServer()"]
        Migration["runDbMigrations()"]
        Signal["setupSignalWatcher()"]
        CreateApp["createApp()"]
    end

    subgraph "Data Flow [routes/]"
        Request["express.Request"]
        Zod["Zod Validation<br/>(EvalSchemas/ProviderSchemas)"]
        Handler["Route Handler<br/>(evalRouter/providersRouter)"]
        Service["Services<br/>(evalJobService/promptCacheService)"]
        Model["Models<br/>(Eval.ts / EvalResult.ts)"]
        DB["SQLite DB (via Drizzle)"]
    end

    Start --> Migration
    Start --> CreateApp
    Start --> Signal
    Request --> Zod
    Zod --> Handler
    Handler --> Service
    Service --> Model
    Model --> DB
```

Sources: `src/server/server.ts:122-195`(), `src/server/routes/eval.ts:132-200`(), `src/models/eval.ts:6-27`(), `src/server/services/evalJobService.ts:1-50`()

# Real-time Updates




This page documents the Socket.IO integration that enables the web UI to reflect in-progress evaluation results without polling. It covers the server-side signal-file mechanism, the Socket.IO event protocol (`init` and `update`), and how the React frontend subscribes and reacts to those events.

For background on the Express server that hosts the Socket.IO server, see page **6.6 Backend Server**. For the Zustand store that holds evaluation table state consumed by the UI, see page **6.3 State Management**.

---

## Overview

Promptfoo's server runs a persistent Socket.IO server alongside the Express HTTP server. As the evaluation engine writes results to the database, it updates a lightweight signal file on disk. A file-system watcher on the server detects these writes, reads the latest eval ID, and broadcasts an `update` event to all connected browser clients. The frontend reconnects to the event stream on page load (receiving an `init` event) and re-fetches evaluation data whenever it receives an `update`.

---

## Server-Side Architecture

### Signal File Mechanism

The evaluation engine and database layer use a signal file to communicate progress to the server process. When an evaluation result is saved or modified, the system calls `notifyEvaluationChanged(id)` [src/models/eval.ts:53](), which triggers `updateSignalFile(id)` [test/models/eval.test.ts:41](). This function writes the current `evalId` to a specific file on disk (typically `.promptfoo/evalId.signal`).

### Socket.IO Server Setup

`startServer` creates the HTTP server and attaches a `SocketIOServer` instance [src/server/server.ts:12]().

The server utilizes `setupSignalWatcher` [src/server/server.ts:19]() to monitor the signal file. When the watcher fires:

1. `readSignalFile()` reads the contents of the signal file [src/server/server.ts:18]().
2. The server determines if an evaluation was updated or deleted using utilities like `hasUnscopedUpdate` [src/server/server.ts:16]() or `isAllEvalsDeleted` [src/server/server.ts:17]().
3. If an update is detected, the server broadcasts to all connected clients via `io.emit('update', { evalId })`.

On new connections, the server typically sends an `init` event with the most recent eval ID so the client can render the latest state immediately.

Sources: [src/server/server.ts:12-21](), [src/models/eval.ts:51-55](), [test/models/eval.test.ts:72-85]()

---

**Diagram: Server-Side Signal and Emit Flow**

```mermaid
sequenceDiagram
    participant EE as "Eval Engine"
    participant EM as "Eval Model (src/models/eval.ts)"
    participant SF as "updateSignalFile (src/database/signal.ts)"
    participant SW as "setupSignalWatcher (src/server/server.ts)"
    participant DB as "SQLite Database (evalsTable)"
    participant SIO as "SocketIOServer (io.emit)"

    EE->>EM: "Evaluation Progress/Result"
    EM->>SF: "notifyEvaluationChanged(evalId)"
    SF-->>SW: "FS Watcher Event"
    SW->>DB: "Query latest summaries"
    DB-->>SW: "evalRecords"
    SW->>SIO: "emit('update', { evalId })"
```

Sources: [src/server/server.ts:12-26](), [src/models/eval.ts:51-55]()

---

## Frontend Architecture

### Socket.IO Client and Data Fetching

The web application establishes a Socket.IO connection to the backend to receive live updates. The data flow is managed through the `useTableStore` Zustand store [src/app/src/pages/eval/components/store.ts:12]().

The store provides a `fetchEvalData` function [src/app/src/pages/eval/components/store.ts:207]() which handles the transition between loading states and background updates.

| Parameter | Type | Description |
|-----------|------|-------------|
| `evalId` | `string` | The ID of the evaluation to fetch. |
| `options.skipLoadingState` | `boolean` | If true, updates the store without triggering the UI loading spinner. |

When an `update` event is received by the frontend, it calls `fetchEvalData` with `skipLoadingState: true`. This allows the `ResultsTable` [src/app/src/pages/eval/components/ResultsTable.tsx]() to refresh its content (e.g., updating cost, token usage, or pass rates) silently.

Sources: [src/app/src/pages/eval/components/store.ts:207-220](), [src/app/src/pages/eval/components/ResultsTable.tsx:1-42]()

---

**Diagram: Client-Side Socket Event Handling**

```mermaid
sequenceDiagram
    participant SIO as "SocketIOServer (server.ts)"
    participant UI as "React Frontend (ResultsView.tsx)"
    participant FED as "fetchEvalData() (store.ts)"
    participant API as "GET /api/results/:id (evalRouter)"

    SIO->>UI: "emit('init', { evalId })"
    UI->>FED: "fetchEvalData(id, { skipLoadingState: false })"
    FED->>API: "Fetch full eval payload"
    API-->>FED: "EvalTableDTO"
    FED-->>UI: "Update useTableStore"

    SIO->>UI: "emit('update', { evalId })"
    UI->>FED: "fetchEvalData(id, { skipLoadingState: true })"
    FED->>API: "Fetch updated results"
    API-->>FED: "Updated EvalTableDTO"
    FED-->>UI: "Silent update (no spinner)"
```

Sources: [src/app/src/pages/eval/components/store.ts:207-220](), [src/server/routes/eval.ts:182-200]()

---

## End-to-End Data Flow

**Diagram: Full Real-Time Update Pipeline**

```mermaid
flowchart TD
    A["Evaluator (evaluateWithSource)"] -->|"Update Result"| B["eval_results (SQLite Table)"]
    B -->|"Trigger"| C["notifyEvaluationChanged"]
    C -->|"File Write"| D["evalId.signal"]
    D -->|"FS Watch"| E["setupSignalWatcher"]
    E -->|"Socket.IO"| F["emit('update')"]
    F -->|"Frontend Store"| G["fetchEvalData(skipLoading=true)"]
    G -->|"HTTP GET"| H["/api/results/:id"]
    H -->|"JSON Response"| I["EvalTableDTO"]
    I -->|"Zustand Update"| J["useTableStore"]
    J -->|"Re-render"| K["ResultsTable Component"]
```

Sources: [src/server/server.ts](), [src/models/eval.ts](), [src/app/src/pages/eval/components/store.ts](), [src/server/routes/eval.ts]()

---

## Key Symbols Reference

| Symbol | File | Role |
|--------|------|------|
| `createApp` | [src/server/server.ts:122]() | Initializes Express and middleware for the backend. |
| `evalRouter` | [src/server/routes/eval.ts:42]() | Defines the API routes for fetching evaluation tables and jobs. |
| `evalJobService` | [src/server/services/evalJobService.ts]() | Manages in-memory state and progress for active evaluation jobs. |
| `fetchEvalData` | [src/app/src/pages/eval/components/store.ts:207]() | Core frontend logic for fetching evaluation data from the server. |
| `notifyEvaluationChanged` | [src/models/eval.ts:53]() | Utility to trigger the signal mechanism after database mutations. |
| `ResultsTable` | [src/app/src/pages/eval/components/ResultsTable.tsx]() | The primary UI component that renders evaluation results. |

---

## Job Progress Tracking

For evaluations started via the Web UI, the system uses a specific job tracking mechanism. The `evalRouter` handles `POST /api/eval/job` [src/server/routes/eval.ts:132](), which initializes an `evalJobService` instance [src/server/routes/eval.ts:168]().

As the evaluation progresses, the `progressCallback` updates the job status [src/server/routes/eval.ts:179-182](). The frontend can query `GET /api/eval/job/:id` [src/server/routes/eval.ts:202]() to get granular progress percentages before the final `complete` call [src/server/routes/eval.ts:187]() triggers the completion of the evaluation job.

Sources: [src/server/routes/eval.ts:132-202](), [src/server/services/evalJobService.ts]()
This page documents the GitHub Actions workflows that power promptfoo's continuous integration, automated releases, and Docker image publishing. It covers the job structure of `main.yml`, the multi-architecture Docker build pipeline in `docker.yml`, the `release-please`-driven release process, and the Tusk parallelized test runner workflows.

---

## Workflow Overview

The CI/CD system consists of several primary workflow files:

| File | Trigger | Purpose |
|---|---|---|
| `.github/workflows/main.yml` | PR, push to `main`, `workflow_dispatch` | Core CI: tests, builds, style checks, language checks |
| `.github/workflows/release-please.yml` | push to `main`, `workflow_dispatch` | Automated versioning, npm publish, Docker release |
| `.github/workflows/docker.yml` | `workflow_call`, `workflow_dispatch`, Dockerfile changes | Multi-arch Docker build, health check, GHCR publish |
| `.github/workflows/tusk-test-runner-vitest-unit-tests.yml` | `workflow_dispatch` (Tusk) | Parallelized Vitest tests for `test/` directory |
| `.github/workflows/tusk-test-runner-app-vitest-unit-tests.yml` | `workflow_dispatch` (Tusk) | Parallelized Vitest tests for `src/app/` |

Sources: [.github/workflows/main.yml:1-7](), [.github/workflows/docker.yml:19-43](), [.github/workflows/release-please.yml:1-10]()

---

## Main CI Workflow (`main.yml`)

### Concurrency and Matrix Generation

All runs under the same `github.workflow`/`github.ref` key cancel in-progress runs on PRs [[.github/workflows/main.yml:12-14]](). A dedicated `ci-config` job computes two dynamic matrices:

- **`test-matrix`**: Selects OS/Node/shard combinations. PR runs include one macOS version; `main` branch and dispatch runs expand to all macOS and additional Windows combinations [[.github/workflows/main.yml:32-62]]().
- **`build-matrix`**: PRs and main/dispatch runs select between Node `22.22` (engine floor), `24.x`, and `26.x` [[.github/workflows/main.yml:40-40]]().

**Test matrix: PR vs. main/dispatch**

| Event | Linux (Ubuntu) | macOS | Windows (sharded 1/2/3) |
|---|---|---|---|
| Pull Request | Node 22.22, 24.x, 26.x | Node 22.22 only | Node 22.22 |
| main / dispatch | Node 22.22, 24.x, 26.x | Node 22.22, 24.x | Node 22.22, 24.x, 26.x |

Sources: [.github/workflows/main.yml:32-65]()

### Job Dependency and Flow

**Main CI workflow job graph**

```mermaid
flowchart TD
  ci-config["ci-config\n(Compute matrices)"]
  test["test\n(npm run test, cross-platform)"]
  build["build\n(npm run build)"]
  style-check["style-check\n(Biome + Prettier + circular deps)"]
  python["python\n(ruff + unittest)"]
  docs["docs\n(site typecheck + build)"]
  code-scan-action["code-scan-action\n(tsc + build)"]
  site-tests["site-tests\n(npm test in site/)"]
  webui["webui\n(Vitest + Codecov frontend)"]
  integration-tests["integration-tests\n(npm run test:integration)"]
  smoke-tests["smoke-tests\n(build + test:smoke)"]
  share-test["share-test\n(eval --share + API check)"]
  redteam["redteam\n(test:redteam:integration)"]
  ruby["ruby\n(rubocop + wrapper test)"]
  golang["golang\n(go test)"]

  ci-config --> test
  ci-config --> build
  ci-config --> style-check
  ci-config --> webui
  ci-config --> python
  ci-config --> ruby
  ci-config --> golang
  build --> integration-tests
  build --> smoke-tests
  build --> share-test
  build --> redteam
```

Sources: [.github/workflows/main.yml:18-161]()

### `test` Job

- Runs the matrix produced by `ci-config` [[.github/workflows/main.yml:78-78]]().
- Installs Node `22.22.0` specifically for the `22.22` matrix lane to test the engine floor [[.github/workflows/main.yml:91-91]]().
- Installs Python 3.14.4 and Ruby (4.0.1 on Linux/macOS, 4.0.0 on Windows) [[.github/workflows/main.yml:94-103]]().
- Caches `node_modules` with a key keyed on OS, Node version, and `package-lock.json` hash [[.github/workflows/main.yml:107-112]]().
- On Node `26.x`, installs the tree without scripts then rebuilds `better-sqlite3` to avoid lifecycle script stalls [[.github/workflows/main.yml:114-121]]().
- The test command becomes `npm run test -- --shard=N/3` for Windows shards [[.github/workflows/main.yml:132-132]]().
- Coverage is collected only on Ubuntu + Node `22.22` (non-sharded) and uploaded to Codecov with the `backend` flag [[.github/workflows/main.yml:132-151]]().
- Runs `npm run test:coverage:ratchet -- --report backend` to ensure coverage does not decrease [[.github/workflows/main.yml:136-136]]().

Sources: [.github/workflows/main.yml:71-152](), [package.json:106-106]()

### `build` Job

Runs `npm run build` which executes `concurrently` to run `tsc`, `tsdown`, and `build:app` [[package.json:63-63]](). Verifies the PostHog telemetry key was inlined into `dist/src/*.js` at build time [[.github/workflows/main.yml:157-161]](). The key is injected via `tsdown` (which uses `esbuild` internally) during the build process [[package.json:63-63]](), [[package-lock.json:152-152]]().

Sources: [.github/workflows/main.yml:153-161](), [package.json:63-63]()

---

## Docker Workflow (`docker.yml`)

### Triggers

The workflow runs in four scenarios:
1. Called by `release-please.yml` via `workflow_call` with a `tag_name` input [[.github/workflows/docker.yml:19-24]]().
2. Manual `workflow_dispatch` [[.github/workflows/docker.yml:25-30]]().
3. Release `published` event (human-authored releases) [[.github/workflows/docker.yml:31-33]]().
4. PR or push to `main` where the `Dockerfile` was modified [[.github/workflows/docker.yml:34-43]]().

### Job Pipeline

**Docker workflow job graph**

```mermaid
flowchart TD
  test["test\n(amd64 build + health check)"]
  build-amd64["build-docker-and-push-digests\n(linux/amd64 on ubuntu-latest)"]
  build-arm64["build-docker-and-push-digests\n(linux/arm64 on ubuntu-24.04-arm)"]
  merge["merge-docker-digests\n(manifest list creation)"]
  attest["attest-docker-image\n(SLSA provenance)"]

  test --> build-amd64
  test --> build-arm64
  build-amd64 --> merge
  build-arm64 --> merge
  merge --> attest
```

Sources: [.github/workflows/docker.yml:65-320]()

### Dockerfile Structure

The `Dockerfile` uses a multi-stage build to minimize image size and attack surface.

**Docker Build Stages and Entities**

```mermaid
flowchart LR
  base["base\n(node:24.20.0-alpine\n+ Python 3\n+ curl)"]
  builder["builder\n(base + libc6-compat\nnpm ci + npm run build)"]
  server["server\n(base\ncopy node_modules + dist\nnpm link promptfoo)"]

  base --> builder
  base --> server
  builder -->|"COPY --from=builder"| server
  server --> entrypoint["CMD node dist/src/server/index.js"]
```

- **`base`**: Node 24.20.0 Alpine, adds Python 3, creates `promptfoo` user/group [[Dockerfile:2-18]]().
- **`builder`**: Installs all npm deps (`npm ci`), copies source, runs `npm run build` [[Dockerfile:21-53]](). It explicitly blocks lifecycle scripts during `npm ci` and rebuilds only `esbuild` and `@swc/core` [[Dockerfile:40-47]]().
- **`server`**: Copies only `node_modules`, `package.json`, and `dist` from `builder`. Sets `PROMPTFOO_SELF_HOSTED=1`. Entry point: `node dist/src/server/index.js` [[Dockerfile:55-81]]().

Sources: [Dockerfile:1-81]()

---

## Release Process (`release-please.yml`)

### Release Job Flow

The project uses `release-please` to automate versioning based on conventional commits [[.github/workflows/release-please.yml:1-10]]().

**Release pipeline and publishing**

```mermaid
flowchart TD
  push["push to main"]
  release-please["release-please job\n(Creates/updates release PR\nOutputs: release_created, tag_name)"]
  build["build job\n(npm ci + npm run build)"]
  publish-npm["publish-npm job\n(npm publish --provenance)"]
  docker["docker job\n(calls docker.yml\nwith tag_name)"]

  push --> release-please
  release-please -->|"release_created == true"| build
  build --> publish-npm
  publish-npm --> docker
```

- `npm publish` uses `--provenance` for publish attestation and `--access public` [[.github/workflows/release-please.yml:109-115]]().
- The Docker job is triggered as a `workflow_call` passing `tag_name`, ensuring version parity between npm and GHCR [[.github/workflows/release-please.yml:123-130]]().
- The version is tracked in `.release-please-manifest.json` [[.release-please-manifest.json:1-4]]().

Sources: [.github/workflows/release-please.yml:1-130](), [.release-please-manifest.json:1-4]()

---

## Tusk Parallelized Test Runner

Tusk workflows allow for file-level parallelization of the test suite to reduce overall CI time.

### `tusk-test-runner-vitest-unit-tests.yml`

Targets `test/` directory test files matching `^test/.*\.test\.(js|ts|tsx)$`.
- **`testScript`**: `npx vitest run {{file}} --reporter=verbose` [[.github/workflows/tusk-test-runner-vitest-unit-tests.yml:33-33]]().
- **`coverageScript`**: `npx vitest run {{testFilePaths}} --coverage --coverage.reporter=json-summary --coverage.reporter=json` [[.github/workflows/tusk-test-runner-vitest-unit-tests.yml:34-34]]().

### `tusk-test-runner-app-vitest-unit-tests.yml`

Targets `src/app/` test files matching `^src/app/.*\.(test|spec)\.(js|jsx|ts|tsx)$`.
- **`appDir`**: `src/app` (all commands run relative to this directory) [[.github/workflows/tusk-test-runner-app-vitest-unit-tests.yml:36-36]]().
- **`maxConcurrency`**: `1` (ensures `tsc --incremental` does not conflict) [[.github/workflows/tusk-test-runner-app-vitest-unit-tests.yml:41-41]]().

Sources: [.github/workflows/tusk-test-runner-vitest-unit-tests.yml:1-111](), [.github/workflows/tusk-test-runner-app-vitest-unit-tests.yml:1-137]()

---

## Code Scanning and Quality

- **`promptfoo-code-scan.yml`**: Runs security scans on PRs. It pins Node to `24.15.0` to avoid a Linux HTTPS slowdown regressed in newer versions [[.github/workflows/promptfoo-code-scan.yml:1-31]](), [[renovate.json:48-53]]().
- **`checkArchitectureBoundaries.ts`**: Script executed via `npm run architecture:check` to enforce modularity boundaries [[package.json:58-58]]().
- **`checkCoverageRatchets.ts`**: Script to prevent regression in test coverage by checking against current thresholds [[package.json:106-106]]().
- **`lint:ci`**: Uses Biome for fast linting and formatting checks in CI [[package.json:83-83]]().
- **`package-manifests.test.ts`**: Validates that the `contracts` subpath is correctly exported and extension-safe for ESM [[test/package-manifests.test.ts:103-136]]().

Sources: [package.json:55-112](), [.github/workflows/promptfoo-code-scan.yml:1-31](), [renovate.json:48-53](), [test/package-manifests.test.ts:1-201]()
This page documents the architecture and command surface of the `promptfoo` command-line interface — how it is bootstrapped, how commands are registered, and the global mechanisms (option propagation, logging, graceful shutdown) that apply to all commands.

For documentation on the evaluation logic that `promptfoo eval` triggers, see [Eval Command](#4.2). For the red team subcommands in detail, see [Red Team System](#5). For environment variable resolution logic and all `PROMPTFOO_` variables, see [Environment and Logging](#4.4).

---

## Entry Point

The CLI is defined in [src/main.ts](), which exports the `main()` async function and serves as the top-level entry point for the `promptfoo` binary.

The module determines whether it is being run directly using `isMainModule()` [src/mainUtils.ts:34](), which resolves symlinks correctly to handle npm global bin symlinks [src/main.ts:153-158]().

When run as the main module, the sequence is:
1.  **Environment Setup**: Call `setupEnvFilesFromArgv()` and `initializeRunLogging()` [src/main.ts:55-56]().
2.  **Infrastructure**: Check for updates via `checkForUpdates()` [src/main.ts:63]() and run database migrations via `runDbMigrations()` [src/main.ts:64]().
3.  **Config Loading**: Load the default configuration via `loadDefaultConfig()` unless skipped [src/main.ts:66-69]().
4.  **Command Registration**: Initialize the `Commander.js` program and register all commands [src/main.ts:71-135]().
5.  **Execution**: Parse arguments via `program.parseAsync()` [src/main.ts:147]().
6.  **Cleanup**: Call `shutdownGracefully()` in the `finally` block of `main()` to flush telemetry and close resources [src/mainUtils.ts:37]().

For details, see [CLI Architecture](#4.1).

Sources: [src/main.ts:53-176](), [src/mainUtils.ts:34-37]()

---

## Startup Sequence

**Diagram: main() startup sequence**

```mermaid
sequenceDiagram
    participant "process" as "Node process"
    participant "main.ts" as "main()"
    participant "logger.ts" as "initializeRunLogging()"
    participant "updates.ts" as "checkForUpdates()"
    participant "migrate.ts" as "runDbMigrations()"
    participant "config/default.ts" as "loadDefaultConfig()"
    participant "Commander" as "program: Command"
    participant "commands/*" as "command modules"

    "process"->"main.ts": "isMainModule()" = true
    "main.ts"->"logger.ts": "initializeRunLogging()"
    "main.ts"->"updates.ts": "checkForUpdates()"
    "main.ts"->"migrate.ts": "runDbMigrations()"
    "main.ts"->"config/default.ts": "loadDefaultConfig()"
    "main.ts"->"Commander": "new Command('promptfoo')"
    "main.ts"->"commands/*": register each command
    "main.ts"->"main.ts": "addCommonOptionsRecursively(program)"
    "main.ts"->"Commander": "program.parseAsync()"
```

Sources: [src/main.ts:53-147]()

---

## Command Registration

All commands are registered inside `main()` by calling module-level factory functions that receive the root `program: Command` object and, where needed, `defaultConfig` and `defaultConfigPath` [src/main.ts:87-135]().

**Diagram: command module map (factory function → registered command)**

```mermaid
graph LR
    program["program: Command"]

    subgraph "src/commands/"
        evalCommand["evalCommand()"]
        initCommand["initCommand()"]
        viewCommand["viewCommand()"]
        mcpCommand["mcpCommand()"]
        shareCommand["shareCommand()"]
        authCommand["authCommand()"]
        cacheCommand["cacheCommand()"]
        configCommand["configCommand()"]
        debugCommand["debugCommand()"]
        deleteCommand["deleteCommand()"]
        exportCommand["exportCommand()"]
        feedbackCommand["feedbackCommand()"]
        importCommand["importCommand()"]
        listCommand["listCommand()"]
        logsCommand["logsCommand()"]
        modelScanCommand["modelScanCommand()"]
        setupRetryCommand["setupRetryCommand()"]
        validateCommand["validateCommand()"]
        showCommand["showCommand()"]
        generateDatasetCommand["generateDatasetCommand()"]
        generateAssertionsCommand["generateAssertionsCommand()"]
    end

    subgraph "src/codeScan/"
        codeScansCommand["codeScansCommand()"]
    end

    subgraph "src/redteam/commands/"
        redteamInitCommand["initCommand()"]
        redteamGenerateCommand["redteamGenerateCommand()"]
        redteamRunCommand["redteamRunCommand()"]
        redteamDiscoverCommand["discoverCommand()"]
        redteamReportCommand["redteamReportCommand()"]
        redteamSetupCommand["redteamSetupCommand()"]
        redteamPluginsCommand["pluginsCommand()"]
    end

    program --> evalCommand
    program --> initCommand
    program --> viewCommand
    program --> mcpCommand
    program --> shareCommand
    program --> authCommand
    program --> cacheCommand
    program --> configCommand
    program --> debugCommand
    program --> deleteCommand
    program --> exportCommand
    program --> feedbackCommand
    program --> importCommand
    program --> listCommand
    program --> logsCommand
    program --> modelScanCommand
    program --> setupRetryCommand
    program --> validateCommand
    program --> showCommand
    program --> generateDatasetCommand
    program --> generateAssertionsCommand
    program --> codeScansCommand

    redteamBase["redteamBaseCommand: Command"]
    program --> redteamBase
    redteamBase --> redteamInitCommand
    redteamBase --> redteamGenerateCommand
    redteamBase --> redteamRunCommand
    redteamBase --> redteamDiscoverCommand
    redteamBase --> redteamReportCommand
    redteamBase --> redteamSetupCommand
    redteamBase --> redteamPluginsCommand
```

Sources: [src/main.ts:87-135]()

---

## Common Options — `addCommonOptionsRecursively`

`addCommonOptionsRecursively(command: Command)` walks the entire command tree and attaches global options and a `postAction` hook to every node [src/main.ts:137]().

| Option | Flag | Description |
|--------|------|-------------|
| Verbose | `-v, --verbose` | Show debug logs [site/docs/usage/command-line.md:75]() |
| Env file | `--env-file, --env-path <path>` | Path to a `.env` file (supports multiple) [site/docs/usage/command-line.md:74]() |
| Help | `--help` | Display help information [site/docs/usage/command-line.md:76]() |

The `postAction` hook ensures that error information is printed from `cliState.errorLogFile` and `cliState.debugLogFile` after command completion [src/main.ts:139-145]().

For details, see [CLI Architecture](#4.1).

Sources: [src/main.ts:137-145](), [site/docs/usage/command-line.md:72-77]()

---

## Command Reference

### Primary Evaluation Commands
*   **`eval`**: The core command for running evaluations. It supports extensive filtering, watch mode, and result persistence [src/commands/eval.ts:31-177]().
*   **`retry <evalId>`**: Retries failed or error-prone results from a previous evaluation [src/main.ts:111]().

For details, see [Eval Command](#4.2).

### Utility Commands
*   **`init`**: Scaffolds new projects with prompts and providers [src/commands/init.ts:16]().
*   **`view`**: Starts the local web server to visualize results [src/commands/view.ts:26]().
*   **`share`**: Generates a shareable URL for evaluation results [src/commands/share.ts:23]().
*   **`mcp`**: Starts a Model Context Protocol server to expose tools to AI agents [src/commands/mcp/index.ts:19]().
*   **`auth`**: Manages cloud authentication (login, logout, whoami) [src/commands/auth.ts:13]().
*   **`logs`**: View and list promptfoo log files [src/main.ts:108]().

For details, see [Utility Commands](#4.3).

---

## Environment and Logging

`promptfoo` uses a centralized environment variable management system. The `cliState` singleton maintains the current run's configuration, including paths to log files and the base path for relative file resolution [src/cliState.ts:10-44]().

Logging is handled by a Winston-based logger, supporting different log levels and file-based persistence for debugging [src/logger.ts:22-106](). The `initializeRunLogging()` function sets up the default logging configuration at the start of every execution [src/main.ts:56]().

For details, see [Environment and Logging](#4.4).

---

## Command Lifecycle Diagram

**Diagram: full command lifecycle from invocation to exit**

```mermaid
sequenceDiagram
    participant "shell" as "Shell"
    participant "main.ts:isMainModule" as "isMainModule()"
    participant "main.ts:main" as "main()"
    participant "main.ts:addCommonOptions" as "addCommonOptionsRecursively()"
    participant "program" as "Commander program"
    participant "command module" as "command handler"
    participant "mainUtils.ts:shutdownGracefully" as "shutdownGracefully()"

    "shell"->>"main.ts:isMainModule": "process.argv[1]"
    "main.ts:isMainModule"->>"main.ts:main": "isMain = true" → "await main()"
    "main.ts:main"->>"main.ts:main": "initializeRunLogging()"
    "main.ts:main"->>"main.ts:main": "checkForUpdates()"
    "main.ts:main"->>"main.ts:main": "runDbMigrations()"
    "main.ts:main"->>"main.ts:main": "loadDefaultConfig()"
    "main.ts:main"->>"program": "new Command('promptfoo')"
    "main.ts:main"->>"program": register commands
    "main.ts:main"->>"main.ts:addCommonOptions": "addCommonOptionsRecursively(program)"
    "main.ts:main"->>"program": "program.parseAsync(process.argv)"
    "program"->>"command module": command handler executes
    "program"->>"program": "postAction" hook: "printErrorInformation"
    "main.ts:main"->>"mainUtils.ts:shutdownGracefully": "finally" block
    "mainUtils.ts:shutdownGracefully"->>"mainUtils.ts:shutdownGracefully": "telemetry.shutdown()"
    "mainUtils.ts:shutdownGracefully"->>"mainUtils.ts:shutdownGracefully": "closeLogger()"
    "mainUtils.ts:shutdownGracefully"->>"shell": "process.exit(exitCode)"
```

Sources: [src/main.ts:53-176](), [src/mainUtils.ts:37-126]()

# CLI Architecture




## Purpose and Scope

This document describes the command-line interface architecture of promptfoo, focusing on the initialization flow, command registration system, and integration hooks. The CLI is built on [Commander.js](https://github.com/tj/commander.js/) and serves as the primary entry point for all promptfoo operations. It manages global state, environment loading, and provides a structured lifecycle for executing evaluations, red teaming operations, and utility commands.

## Entry Point and Application Lifecycle

The CLI application starts in `src/main.ts` and follows a structured initialization sequence before executing user commands.

**Initialization Flow**

```mermaid
flowchart TD
    Start["Node process starts"] --> IsMain["isMainModule(import.meta.url, process.argv[1])"]
    IsMain -->|"true"| Main["main() async function"]
    IsMain -->|"false (imported as library)"| LibEnd["Module exports used directly"]
    Main --> EnvArgv["setupEnvFilesFromArgv(argv)"]
    EnvArgv --> InitLog["initializeRunLogging()"]
    InitLog --> CICheck["Set PROMPTFOO_DISABLE_UPDATE in CI"]
    CICheck --> CheckUpdates["checkForUpdates()"]
    CheckUpdates --> Migration["runDbMigrations()"]
    Migration --> LoadConfig["loadDefaultConfig()"]
    LoadConfig --> CreateProgram["new Command('promptfoo')"]
    CreateProgram --> RegisterCommands["Register all commands (eval, init, mcp, redteam, etc.)"]
    RegisterCommands --> AddOptions["addCommonOptionsRecursively(program)"]
    AddOptions --> SetupHooks["program.hook('postAction', ...)"]
    SetupHooks --> Parse["program.parseAsync()"]
    Parse --> Finally["finally block"]
    Finally --> Shutdown["shutdownGracefully()"]
    Shutdown --> End["Process exit"]
```

Sources: [src/main.ts:53-147](), [src/main.ts:153-160]()

The `main()` function orchestrates the entire CLI lifecycle. It performs critical setup operations before parsing commands and ensures proper cleanup afterward:

| Step | Function | Purpose |
|------|----------|---------|
| 1 | `setupEnvFilesFromArgv()` | Loads environment variables from `--env-file` or `--env-path` flags before config loading [src/main.ts:55-55](), [src/mainUtils.ts:32-32]() |
| 2 | `initializeRunLogging()` | Sets up debug and error log files for the session [src/main.ts:56-56](), [src/logger.ts:224-224]() |
| 3 | CI environment check | Sets `PROMPTFOO_DISABLE_UPDATE=true` if `CI` is defined to prevent hanging [src/main.ts:58-61]() |
| 4 | `checkForUpdates()` | Checks npm registry for newer versions [src/main.ts:63-63](), [src/updates.ts:46-46]() |
| 5 | `runDbMigrations()` | Ensures SQLite database schema is current via Drizzle [src/main.ts:64-64](), [src/migrate.ts:39-39]() |
| 6 | `loadDefaultConfig()` | Loads `promptfooconfig.yaml` from default locations [src/main.ts:69-69](), [src/util/config/default.ts:47-47]() |
| 7 | `addCommonOptionsRecursively()` | Adds global flags like `--verbose` and `--env-file` to all commands [src/main.ts:137-137](), [src/mainUtils.ts:124-124]() |
| 8 | `program.parseAsync()` | Parses arguments and executes selected command [src/main.ts:147-147]() |
| 9 | `shutdownGracefully()` | Cleans up resources: telemetry, logger, DB, and worker pools [src/main.ts:178-178](), [src/mainUtils.ts:275]() |

Sources: [src/main.ts:53-178](), [src/mainUtils.ts:32-275]()

## Commander.js Program Configuration

The CLI uses Commander.js to provide a structured command hierarchy with built-in help and error handling.

**Program Setup**

```mermaid
graph TB
    Program["new Command('promptfoo')"]
    Program --> Version[".version(VERSION)"]
    Program --> Help[".showHelpAfterError()"]
    Program --> Suggest[".showSuggestionAfterError()"]
    Program --> ErrorHandler[".on('option:*', handler)"]

    Version --> VersionDisplay["Displays VERSION from src/version.ts"]
    Help --> HelpDisplay["Shows help text on command error"]
    Suggest --> SuggestionDisplay["Suggests similar commands on typo"]
    ErrorHandler --> InvalidOption["Logs error for unknown args and calls program.help()"]
```

Sources: [src/main.ts:71-85]()

The program is configured with error handling and user assistance features:
- **Version**: Displayed with `--version`, sourced from `src/version.ts` [src/main.ts:73-73]().
- **Help system**: `.showHelpAfterError()` automatically shows help text when commands fail [src/main.ts:74-74]().
- **Command suggestions**: `.showSuggestionAfterError()` suggests similar commands for typos [src/main.ts:75-75]().
- **Option validation**: A custom `option:*` listener catches invalid options, logs the error using `logger.error`, and sets `process.exitCode = 1` [src/main.ts:76-85]().

## Command Registration System

Commands are organized into functional groups and registered with the Commander program during initialization.

**Command Registration Structure**

```mermaid
graph TB
    subgraph "Core Commands"
        Eval["evalCommand()"]
        Init["initCommand()"]
        View["viewCommand()"]
        MCP["mcpCommand()"]
        Share["shareCommand()"]
    end

    subgraph "Utility Commands"
        Auth["authCommand()"]
        Cache["cacheCommand()"]
        Config["configCommand()"]
        Debug["debugCommand()"]
        Delete["deleteCommand()"]
        List["listCommand()"]
        Validate["validateCommand()"]
    end

    subgraph "Generation Commands"
        GenBase["program.command('generate')"]
        GenDataset["generateDatasetCommand()"]
        GenAssertions["generateAssertionsCommand()"]
        GenRedteam["redteamGenerateCommand()"]
    end

    subgraph "Red Team Commands"
        RTBase["program.command('redteam')"]
        RTInit["redteamInitCommand()"]
        RTRun["redteamRunCommand()"]
        RTReport["redteamReportCommand()"]
        RTDiscover["redteamDiscoverCommand()"]
        RTSetup["redteamSetupCommand()"]
    end

    RTBase --> RTInit
    RTBase --> RTRun
    RTBase --> RTReport
    RTBase --> RTDiscover
    RTBase --> RTSetup
    GenBase --> GenDataset
    GenBase --> GenAssertions
    GenBase --> GenRedteam
```

Sources: [src/main.ts:87-135]()

### MCP Server Command
The `mcpCommand` exposes promptfoo tools via the Model Context Protocol (MCP). This allows AI agents to interact with promptfoo directly.
- **Implementation**: Located in `src/commands/mcp/index.ts` [src/main.ts:19-19]().
- **Tools exposed**: Includes `runEvaluation`, `generateDataset`, `redteamGenerate`, `redteamRun`, `testProvider`, `validatePromptfooConfig`, `compareProviders`, `shareEvaluation`, and `listEvaluations` [site/docs/usage/command-line.md:43-43]().
- **Transport**: Supports both HTTP and stdio transports for agent communication [src/main.ts:92-92]().

Sources: [src/main.ts:19-19](), [src/main.ts:92-92](), [site/docs/usage/command-line.md:43-43]()

## Common Options and Lifecycle Hooks

The `addCommonOptionsRecursively()` function ensures all commands have consistent options and behavior by traversing the entire command tree.

**Common Options Injection**

| Option | Description | Logic |
|--------|-------------|-------|
| `-v, --verbose` | Enable debug logs | Sets log level to `debug` in `preAction` [src/mainUtils.ts:145-148]() |
| `--env-file` | Load `.env` files | Normalized via `normalizeEnvPaths` and loaded via `setupEnv` [src/mainUtils.ts:150-154]() |
| `--help` | Display help | Standard Commander behavior [src/mainUtils.ts:161-161]() |

Sources: [src/mainUtils.ts:124-167]()

### Lifecycle Hooks
- **`preAction`**: Registered on every command. It handles logging levels via `setLogLevel('debug')`, environment variable loading via `setupEnv`, and records telemetry for the command being used [src/mainUtils.ts:143-163]().
- **`postAction`**: Registered on the root program. It prints error/debug log locations if a failure occurred via `printErrorInformation` and executes any `cliState.postActionCallback` [src/main.ts:139-145]().

## Graceful Shutdown

`shutdownGracefully()` is called to ensure all resources are released, whether the process exits normally or via an error.

**Cleanup Sequence**

1. **Force Exit Guarantee**: A 3-second `setTimeout` is created to force exit if cleanup hangs [src/mainUtils.ts:275]().
2. **Telemetry**: Flushes and shuts down the telemetry service [src/mainUtils.ts:275]().
3. **Logger**: Sets `isLoggerShuttingDown = true` and closes log streams [src/mainUtils.ts:275]().
4. **Database**: Closes SQLite connections via `closeDbIfOpen()` [src/mainUtils.ts:275]().
5. **OTEL**: Flushes OpenTelemetry spans via `flushOtel()` [src/mainUtils.ts:275]().
6. **Worker Pools**: Destroys persistent worker pools via `destroyDispatcher()` [src/mainUtils.ts:275]().

Sources: [src/mainUtils.ts:275]()

## CLI State Management

The `cliState` singleton maintains global state across command execution, bridging the CLI entry point with the core evaluation engine.

| Field | Purpose |
|-------|---------|
| `errorLogFile` | Path to the session's error log file [src/cliState.ts:15-15]() |
| `debugLogFile` | Path to the session's debug log file [src/cliState.ts:16-16]() |
| `postActionCallback` | Deferred function to run after CLI completion (e.g., summary generation) [src/cliState.ts:24-24]() |
| `resume` | Flag indicating if the current run is resuming a previous evaluation [src/cliState.ts:20-20]() |

Sources: [src/cliState.ts:1-30](), [src/main.ts:140-143]()
The Code Scanning system in promptfoo provides automated security analysis for LLM-related code. It identifies vulnerabilities such as prompt injection, insecure output handling, and configuration flaws by analyzing source code, git diffs, and integration environments. This functionality is exposed through the `code-scans` CLI command group, a GitHub Action for CI/CD integration, and Model Context Protocol (MCP) tools for agentic workflows.

## Architecture and Data Flow

The code scanning subsystem is organized into several key layers: the core scanning logic in `src/codeScan/`, the CLI entry points in `src/codeScan/commands/`, and external wrappers like the `code-scan-action`.

### High-Level Data Flow
The scanner processes repository content and git metadata, often utilizing a Model Context Protocol (MCP) bridge to allow remote AI agents to explore the filesystem during the analysis phase.

**Code Scanning Pipeline**
```mermaid
graph TD
    subgraph "Input Space"
        A["Repository Files"]
        B["Git Diffs (Base vs Compare)"]
        C["GitHub PR Context"]
    end

    subgraph "Logic Space (Code Entities)"
        D["executeScan"]
        E["processDiff"]
        F["setupMcpBridge"]
        G["executeScanRequestWithRetry"]
    end

    subgraph "Output Space"
        H["CLI Text/Table"]
        I["JSON Output"]
        J["SARIF (GitHub Code Scanning)"]
        K["GitHub PR Comments"]
    end

    A --> D
    B --> E
    E --> D
    C --> D
    D --> F
    F --> G
    G --> H
    G --> I
    G --> J
    G --> K
```
**Sources:** [src/codeScan/scanner/index.ts:75-82](), [code-scan-action/src/main.ts:219-245]()

## CLI Command Group

The `code-scans` command group allows users to run security audits locally or in CI. It supports scanning specific directories or analyzing the git state to identify risks introduced in recent changes. The main entry point for the scanner logic is `executeScan`, which orchestrates the entire lifecycle.

### Key Options
| Option | Description | Default |
| :--- | :--- | :--- |
| `--base <ref>` | Base branch/commit to compare against | Auto-detects main/master |
| `--compare <ref>` | Branch/commit to scan | `HEAD` |
| `--diffs-only` | Scan only PR diffs without filesystem exploration | `false` |
| `-f, --format <format>` | Output format: `text`, `json`, or `sarif` | `text` |
| `--guidance <text>` | Custom instructions to tailor the scan's focus | None |

The CLI command implementation for running scans is located in `src/codeScan/commands/run.ts`, while the core logic is handled by `executeScan` in `src/codeScan/scanner/index.ts`.

**Sources:** [src/codeScan/scanner/index.ts:43-57](), [src/codeScan/scanner/index.ts:87-91](), [site/docs/code-scanning/cli.md:46-60]()

## GitHub Action (`code-scan-action`)

The `code-scan-action` is a specialized wrapper that automates scanning within GitHub Workflows. It handles OIDC authentication, fetches PR metadata, and posts findings directly as review comments.

### Implementation Details
The action's entry point is `code-scan-action/src/main.ts`. It utilizes `@actions/github` to interact with the GitHub API and `@actions/exec` to invoke the underlying `promptfoo` binary via the `code-scans run` command. The action pins the `promptfoo` version at build time to ensure consistency [code-scan-action/src/main.ts:14-18]().

**Action Execution Logic**
```mermaid
sequenceDiagram
    participant GH as GitHub Runner
    participant Action as "code-scan-action/src/main.ts"
    participant CLI as "promptfoo code-scans run"
    participant API as "GitHub REST API"

    GH->>Action: Execute Action
    Action->>Action: getActionInputs()
    Action->>Action: getGitHubOIDCToken()
    Action->>CLI: spawn("npm install promptfoo@pinned")
    Action->>CLI: spawn("promptfoo code-scans run")
    CLI-->>Action: ScanResponse (JSON)
    Action->>Action: scanResponseToSarif()
    Action->>API: postReviewComments()
    Note over Action, API: Post findings to PR lines
```
**Sources:** [code-scan-action/src/main.ts:219-245](), [code-scan-action/src/github.ts:186-193](), [test/code-scan-action/main.test.ts:182-195]()

### Key Functions
- **`getGitHubOIDCToken()`**: Retrieves a GitHub OIDC token for server authentication, allowing passwordless scans [code-scan-action/src/main.ts:30-30]().
- **`partitionReviewCommentsByDiff()`**: Translates scan findings into comments that can be placed on specific lines by checking them against the current PR diff [code-scan-action/src/github.ts:186-193]().
- **`clampCommentToValidRange()`**: Ensures that AI-generated line numbers actually exist within the PR diff by using `clampCommentLines` before attempting to post a comment [code-scan-action/src/github.ts:129-146]().
- **`prepareComments()`**: Constructs the final review body, including the "All Clear" message if no vulnerabilities are found [src/codeScan/util/github.ts:75-121]().

**Sources:** [code-scan-action/src/main.ts:30-30](), [code-scan-action/src/github.ts:129-146](), [src/codeScan/util/github.ts:75-121]()

## MCP-Based Code Scanning

The scanner uses a Model Context Protocol (MCP) bridge to provide AI agents with controlled access to the local filesystem. This is essential for "deep" scans where the agent needs to trace data flows beyond the immediate diff.

- **`setupMcpBridge`**: Orchestrates the connection between the promptfoo server (via Socket.IO) and a local MCP filesystem server [src/codeScan/scanner/index.ts:29-29](), [src/codeScan/scanner/index.ts:194-196]().
- **`stopFilesystemMcpServer`**: Ensures the local MCP server is shut down cleanly after the scan completes [src/codeScan/scanner/index.ts:28-28]().

**Sources:** [src/codeScan/scanner/index.ts:28-29](), [src/codeScan/scanner/index.ts:194-196]()

## Git Diff Analysis

The system utilizes `processDiff` to identify which files and line ranges have changed. This metadata is sent to the scanning engine to focus analysis on the most relevant code.

### File Filtering
The scanner filters files based on several criteria to optimize performance and relevance:
- **`skipReason`**: Files can be skipped if they are in a denylist (e.g., `package-lock.json`) or if the blob is too large [test/codeScans/scanner-no-files.test.ts:11-38]().
- **`includedFiles`**: The logic in `executeScan` filters the result of `processDiff` to only include files that have a patch and no `skipReason` [test/codeScans/scanner-no-files.test.ts:35-37]().

**Sources:** [src/codeScan/scanner/index.ts:26-26](), [test/codeScans/scanner-no-files.test.ts:11-38]()

## Vulnerability Detection and Reporting

Findings are categorized by severity (`critical`, `high`, `medium`, `low`) and can be output in multiple formats including TEXT, JSON, and SARIF.

### SARIF Integration
For integration with GitHub Code Scanning (the "Security" tab), promptfoo converts its internal `ScanResponse` to the SARIF 2.1.0 format.
- **`scanResponseToSarif()`**: Maps `Comment` objects to SARIF `results` [code-scan-action/src/main.ts:20-20]().
- **`hasSarifReportableFindings()`**: Determines if the scan result contains findings that should be included in a SARIF report [code-scan-action/src/main.ts:20-20]().

### Severity Mapping
| CodeScanSeverity | GitHub Display |
| :--- | :--- |
| `CRITICAL` / `HIGH` | 🔴 Error |
| `MEDIUM` | 🟡 Warning |
| `LOW` | 🔵 Note |

Severity ranks are determined by `getSeverityRank` and formatted for display using `formatSeverity`.

**Sources:** [src/codeScan/util/github.ts:7-12](), [src/codeScan/util/github.ts:84-89](), [code-scan-action/src/main.ts:20-20]()
This document covers the core data models used to represent evaluations and their results, the SQLite database schema with Drizzle ORM, and the persistence layer that manages creating, storing, and querying evaluation data. For details on how evaluations are executed and results are generated, see [Evaluation Engine](2.1). For information about how results are displayed in the web UI, see [Results Viewer](6.2).

## Core Data Models

The system uses two primary model classes to represent evaluation data: `Eval` and `EvalResult`.

### Eval Model

The `Eval` class [src/models/eval.ts:317-650]() represents a complete evaluation run with configuration, metadata, and relationships to results.

**`Eval` class — fields and static/instance methods:**

```mermaid
classDiagram
    class Eval {
        +string id
        +number createdAt
        +string? author
        +string? description
        +Partial~UnifiedConfig~ config
        +EvalResult[] results
        +string? datasetId
        +CompletedPrompt[] prompts
        +EvaluateSummaryV2? oldResults
        +boolean persisted
        +string[] vars
        +boolean _resultsLoaded
        +Partial~EvaluateOptions~? runtimeOptions
        +boolean _shared
        +number? durationMs
        +number? generationDurationMs
        +number? evaluationDurationMs
        +string? shareableUrl
        +create(config, renderedPrompts, opts?) Promise~Eval~
        +findById(id) Promise~Eval~
        +latest() Promise~Eval~
        +getMany(limit) Promise~Eval[]~
        +getPaginated(offset, limit) Promise~Eval[]~
        +getCount() Promise~number~
        +addResult(result) Promise~void~
        +getTable() Promise~EvaluateTable~
        +fetchResultsBatched(batchSize) AsyncGenerator
        +getResultsCount() Promise~number~
        +getTotalResultRowCount() Promise~number~
        +fetchResultsByTestIdx(testIdx) Promise~EvalResult[]~
        +save() Promise~void~
        +delete() Promise~void~
        +setDurationMs(ms) void
        +setGenerationDurationMs(ms) void
        +version() number
        +useOldResults() boolean
    }

    class EvalResult {
        +string id
        +string evalId
        +string promptId
        +number testIdx
        +string prompt
        +string output
        +GradingResult? gradingResult
        +number score
        +boolean success
        +ProviderResponse? response
        +AtomicTestCase testCase
        +create(evalId, result) Promise~EvalResult~
        +createFromEvaluateResult(evalId, result, opts) Promise~EvalResult~
        +findManyByEvalId(evalId, opts) Promise~EvalResult[]~
        +findManyByEvalIdBatched(evalId, opts) AsyncGenerator
        +sanitizeProvider(provider) object
    }

    Eval "1" --> "*" EvalResult : "contains"
    Eval --> UnifiedConfig : "has"
    Eval --> CompletedPrompt : "references"
```

Sources: [src/models/eval.ts:317-650](), [src/models/evalResult.ts:40-265]()

### EvalQueries Static Class

`EvalQueries` [src/models/eval.ts:160-315]() is a static class providing SQL utility queries that operate across multiple `Eval` instances, primarily for metadata and variable discovery:

| Method | Purpose |
|--------|---------|
| `getVarsFromEvals(evals)` | Returns `{evalId: string[]}` map of variable key names per eval [src/models/eval.ts:161-193]() |
| `getVarsFromEval(evalId)` | Returns distinct variable key names for a single eval [src/models/eval.ts:195-206]() |
| `getMetadataKeysFromEval(evalId, comparisonEvalIds?)` | Returns sorted, deduplicated metadata keys using `json_each` [src/models/eval.ts:217-236]() |
| `getMetadataValuesFromEval(evalId, key)` | Returns distinct values for a given metadata key using `json_extract` [src/models/eval.ts:238-274]() |

The metadata queries include safety guards: `json_valid()` checks and escaping via `escapeJsonPathKey` [src/models/eval.ts:109-111]() to prevent malformed data issues.

Sources: [src/models/eval.ts:160-315]()

### EvalResult Model

The `EvalResult` class [src/models/evalResult.ts:40-265]() represents a single test case result within an evaluation. It stores the specific prompt sent, the raw output, and the structured grading result.

| Field | Type | Description |
|-------|------|-------------|
| `evalId` | `string` | Foreign key to parent evaluation [src/models/evalResult.ts:43]() |
| `promptId` | `string` | SHA-256 hash of the prompt [src/models/evalResult.ts:44]() |
| `testIdx` | `number` | Test case index within the eval (0-based) [src/models/evalResult.ts:45]() |
| `prompt` | `string` | Sanitized prompt text sent to the provider [src/models/evalResult.ts:46]() |
| `output` | `string` | Model output text [src/models/evalResult.ts:47]() |
| `gradingResult` | `GradingResult?` | Assertion results and grading metadata [src/models/evalResult.ts:48]() |
| `success` | `boolean` | Overall pass/fail flag [src/models/evalResult.ts:50]() |
| `score` | `number` | Numeric score (0.0–1.0) [src/models/evalResult.ts:49]() |
| `namedScores` | `Record<string, number>` | Custom metric scores [src/models/evalResult.ts:51]() |
| `metadata` | `Record<string, unknown>` | Plugin IDs, strategy IDs, etc. [src/models/evalResult.ts:52]() |
| `testCase` | `AtomicTestCase` | The original test case configuration [src/models/evalResult.ts:54]() |

Sources: [src/models/evalResult.ts:40-265]()

## Database Schema

The system uses SQLite with Drizzle ORM. The schema is defined in `src/database/tables.ts` [src/database/tables.ts:1-200]().

**Database entity-relationship diagram:**

```mermaid
erDiagram
    "evalsTable" ||--o{ "evalResultsTable" : "has results"
    "evalsTable" ||--o{ "evalsToPromptsTable" : "references"
    "evalsTable" ||--o{ "evalsToDatasetsTable" : "uses"
    "evalsTable" ||--o{ "evalsToTagsTable" : "has tags"
    "promptsTable" ||--o{ "evalsToPromptsTable" : "used in"
    "datasetsTable" ||--o{ "evalsToDatasetsTable" : "contains tests"
    "tagsTable" ||--o{ "evalsToTagsTable" : "labels"

    "evalsTable" {
        text id PK
        integer createdAt
        text author
        text description
        json results
        json config
        json prompts
        json vars
        json runtimeOptions
    }

    "evalResultsTable" {
        text id PK
        text evalId FK
        integer testIdx
        text prompt
        text output
        json gradingResult
        real score
        integer success
        json namedScores
        json metadata
        json response
        json testCase
    }

    "promptsTable" {
        text id PK
        integer createdAt
        text prompt
    }

    "datasetsTable" {
        text id PK
        json tests
    }

    "tagsTable" {
        text id PK
        text name
        text value
    }
```

Sources: [src/database/tables.ts:1-200](), [src/models/eval.ts:6-16]()

## Evaluation Creation and Persistence

### Creating an Eval

Evaluations are created using `Eval.create()` [src/models/eval.ts:490-608](), which initializes the eval record and all relationships inside a single database transaction:

**`Eval.create()` transaction sequence:**

```mermaid
sequenceDiagram
    participant Caller
    participant "Eval.create()" as Eval_create
    participant "db.transaction()" as db_transaction
    participant "evalsTable" as evals_table
    participant "promptsTable" as prompts_table
    participant "datasetsTable" as datasets_table
    participant "evalResultsTable" as eval_results_table

    Caller->>Eval_create: "create(config, renderedPrompts, opts)"
    Eval_create->>Eval_create: "createEvalId(createdAt)"
    Eval_create->>db_transaction: "BEGIN"
    db_transaction->>evals_table: "INSERT"
    loop "for each prompt"
        db_transaction->>prompts_table: "INSERT ON CONFLICT DO NOTHING"
        db_transaction->>db_transaction: "INSERT evalsToPromptsTable"
    end
    db_transaction->>datasets_table: "INSERT ON CONFLICT DO NOTHING"
    opt "if opts.results"
        db_transaction->>eval_results_table: "INSERT batch"
    end
    db_transaction->>Eval_create: "COMMIT"
    Eval_create->>Caller: "new Eval instance"
```

Sources: [src/models/eval.ts:490-608]()

### Adding Results

During evaluation execution, results are added incrementally via `eval.addResult()` [src/models/eval.ts:742-755]():

**`addResult()` flow:**

```mermaid
flowchart TD
    A["evaluate() generates EvaluateResult"] --> B["eval.addResult(result)"]
    B --> C["EvalResult.createFromEvaluateResult(evalId, result, {persist})"]
    C --> D["sanitizeProvider(provider)"]
    D --> E{"eval.persisted?"}
    E -->|"Yes"| F["INSERT INTO eval_results_table"]
    E -->|"No"| G["this.results.push() in-memory only"]
    F --> H["updateSignalFile(evalId)"]
    H --> I["WebSocket notifies UI"]
```

Sources: [src/models/eval.ts:742-755](), [src/models/evalResult.ts:51-141](), [src/database/signal.ts:5]()

## Result Sanitization

Before persisting to the database, several sanitization steps run to prevent credential leaks and circular reference errors:

1.  **`sanitizeProvider()`** [src/models/evalResult.ts:93-131]() — strips circular references from provider objects and handles consistent formatting.
2.  **`sanitizeForDbWithSecrets()`** [src/models/evalResult.ts:177-187]() — redacts credential fields like `apiKey` or `token` at any depth.
3.  **`sanitizeForDb()`** [src/models/evalResult.ts:142-164]() — uses `safeJsonStringify` to handle circular structures and non-serializable values (like Node.js `Timeout` objects) gracefully [src/models/evalResult.ts:147]().
4.  **`sanitizeRuntimeOptions()`** [src/models/eval.ts:79-103]() — removes non-serializable fields from `EvaluateOptions`.

Sources: [src/models/evalResult.ts:93-187](), [src/models/eval.ts:79-103]()

## Versioning System

The system supports two data format versions:

| Version | Description | Detection |
|---------|-------------|-----------|
| **Version 3** | Legacy format — `table` is stored as a blob inside `evalsTable.results` | `oldResults?.table` exists [src/models/eval.ts:650]() |
| **Version 4** | Current format — results stored in `evalResultsTable`; table generated at query time | Default for all new evals [src/models/eval.ts:645]() |

Sources: [src/models/eval.ts:644-654]()

## Querying and Filtering

### Query Pipeline

The server builds paginated `EvaluateTable` responses by determining matching test indices and then fetching result objects.

**Two-phase query pipeline:**

```mermaid
flowchart TD
    A["API: GET /eval/:id/table"] --> B["Eval.getTable() or paginated fetch"]
    B --> C["buildFilterWhereSql(filterMode, searchQuery, filters)"]
    C --> D["Produces SQL WHERE fragment"]
    D --> E["queryTestIndicesOptimized() — Phase 1"]
    E --> F["SELECT DISTINCT test_idx WHERE ... LIMIT/OFFSET"]
    F --> G["testIndices: number[]"]
    G --> H["fetchResultsByTestIdx() — Phase 2"]
    H --> I["EvalResult.findManyByEvalId(evalId, {testIdx})"]
    I --> J["convertEvalResultsToTable()"]
```

Sources: [src/models/eval.ts:795-900](), [src/models/evalPerformance.ts:48-49](), [src/util/convertEvalResultsToTable.ts:1-100]()

### Filter Types

`buildFilterWhereSql()` [src/models/eval.ts:795-900]() translates `ResultsFilter` entries into parameterized Drizzle `SQL` fragments. It supports filtering by:
*   **Metadata**: Uses `json_extract` on the `metadata` column [src/models/eval.ts:835-843]().
*   **Variables**: Uses `json_extract` on the `test_case.vars` path [src/models/eval.ts:821-829]().
*   **Metrics**: Filters by `namedScores` keys [src/models/eval.ts:845-853]().

JSON field paths are constructed by `buildSafeJsonPath()` [src/models/eval.ts:120-122](), which handles escaping special characters via `escapeJsonPathKey` [src/models/eval.ts:109-111]().

Sources: [src/models/eval.ts:120-122](), [src/models/eval.ts:795-900]()

## Blob Storage for Media Assets

The codebase handles media (audio, images, video) via storage references or base64 strings. Media assets are detected by MIME patterns [src/app/src/pages/eval/components/ResultsTable.tsx:152-155]().

**Media Resolution Flow:**

```mermaid
flowchart TD
    A["StorageRefAudioPlayer"] --> B{"isStorageRef(data)?"}
    B -->|"Yes"| C["resolveAudioUrl(data, format)"]
    B -->|"No"| D["Inline base64 data"]
    C --> E["Fetch from /api/media or /api/blobs"]
    D --> E
    E --> F["HTML5 Media Element (audio/img/video)"]
```

Sources: [src/app/src/pages/eval/components/ResultsTable.tsx:98-144](), [src/app/src/pages/eval/components/EvalOutputCell.tsx:89-119](), [src/app/src/pages/eval/components/ResultsTable.tsx:152-155]()

## UI State Management

Evaluation data in the web UI is managed by the `useTableStore` Zustand store [src/app/src/pages/eval/components/store.ts:12-215]().

| Action | Purpose |
|--------|---------|
| `fetchEvalData` | Fetches evaluation results from the backend with pagination and filters [src/app/src/pages/eval/components/store.ts:350-420]() |
| `setTable` | Updates the table state after processing raw results [src/app/src/pages/eval/components/store.ts:310-330]() |
| `computeAvailableMetrics` | Extracts unique metric names from the table for filter dropdowns [src/app/src/pages/eval/components/store.ts:55-73]() |

The `ResultsTable` component [src/app/src/pages/eval/components/ResultsTable.tsx:84-2720]() consumes this state to render a paginated view with support for variable markdown cells [src/app/src/pages/eval/components/VariableMarkdownCell.tsx]() and detailed output dialogs [src/app/src/pages/eval/components/EvalOutputPromptDialog.tsx]().

Sources: [src/app/src/pages/eval/components/store.ts:12-420](), [src/app/src/pages/eval/components/ResultsTable.tsx:1-198]()
This document provides high-level guidance for contributors to the promptfoo codebase. It covers the development environment, build processes, testing infrastructure, and quality enforcement mechanisms.

For deep technical details on specific subsystems, please refer to the child pages linked throughout this guide.

## Build System and CI/CD

The promptfoo build system is centered around a TypeScript-to-JavaScript compilation process, while the web application is bundled via Vite. The CI/CD pipeline, managed through GitHub Actions, automates testing across multiple Node.js versions (22.22, 24.x, 26.x) and operating systems (Linux, Windows, macOS) [.github/workflows/main.yml:32-60](). The repository currently uses Node 22.22.0 as the floor for engine testing [.github/workflows/main.yml:91]().

The release process is automated using `release-please`, which handles version bumping and changelog generation for both the core `promptfoo` package and the `@promptfoo/code-scan-action` [release-please-config.json:10-28](). Deployment artifacts include npm packages published with OIDC provenance [.github/workflows/release-please.yml:111-113]() and multi-architecture Docker images published to GitHub Container Registry [.github/workflows/docker.yml:64-68]().

For details, see [Build System and CI/CD](#9.1).

**Build and Release Pipeline**

```mermaid
graph LR
    subgraph "Source_Space"
        CODE["TypeScript/React Source"]
        DOCS["Docusaurus Docs (site/)"]
    end

    subgraph "CI_Workflow [main.yml]"
        TEST["npm run test"]
        BUILD["npm run build"]
        LINT["npm run lint"]
    end

    subgraph "Release_Workflow [release-please.yml]"
        RP["release-please-action"]
        NPM["npm publish --provenance"]
        DOCKER["docker.yml (Workflow Call)"]
    end

    CODE --> TEST
    TEST --> BUILD
    BUILD --> LINT
    LINT --> RP
    RP --> NPM
    RP --> DOCKER
```

Sources: [.github/workflows/main.yml:32-60](), [.github/workflows/release-please.yml:51-55](), [.github/workflows/docker.yml:64-68](), [release-please-config.json:10-28]()

## Testing Infrastructure

Promptfoo employs a multi-tiered testing strategy to ensure reliability across its core engine and web interface. The codebase utilizes **Jest** for legacy logic and **Vitest** for the React application (`src/app`) and all new test files [site/docs/contributing.md:139-169]().

Testing categories include:
- **Unit Tests**: Isolated component testing. Vitest is mandatory for new files [test/AGENTS.md:169]().
- **Integration Tests**: Cross-component workflows, such as `test:integration` and `test:redteam:integration` [AGENTS.md:65-66]().
- **Smoke Tests**: Validating the **built CLI package** (`dist/src/main.js`) using `spawnSync` to ensure end-to-end functionality [test/AGENTS.md:203-206]().
- **Parallel Execution**: Large suites are sharded in CI [.github/workflows/main.yml:132]() and can be run via the **Tusk test runner** for high-concurrency execution using `Use-Tusk/test-runner` [.github/workflows/tusk-test-runner-app-vitest-unit-tests.yml:57-79]().

For details, see [Testing Infrastructure](#9.2).

Sources: [site/docs/contributing.md:139-149](), [AGENTS.md:63-69](), [.github/workflows/main.yml:130-136](), [test/AGENTS.md:203-206]()

## Code Quality

Code quality is enforced through a combination of linting, formatting, and architectural boundary checks. The project uses **Biome** for high-performance linting and formatting of JavaScript/TypeScript, while **Prettier** remains in use for CSS, Markdown, and YAML files [site/docs/contributing.md:177-186]().

Key quality gates include:
- **Dependency Validation**: Using `npm ci` with specific version overrides (e.g., `npm@11.11.0`) to avoid lockfile compatibility bugs in newer Node versions [.github/workflows/main.yml:124]().
- **Architecture Enforcement**: The project structure separates concerns into directories like `src/providers`, `src/redteam`, `src/commands`, and `src/server` [AGENTS.md:18-35]().
- **Type Safety**: Strict TypeScript compilation via `npm run tsc` or `tsc --build` is required [AGENTS.md:51]().
- **Security Scanning**: Automated adversarial scanning of the codebase itself via the `promptfoo/code-scan-action` which checks for LLM security vulnerabilities in code [.github/workflows/promptfoo-code-scan.yml:52-53]().

For details, see [Code Quality](#9.3).

Sources: [site/docs/contributing.md:125-126](), [AGENTS.md:54-61](), [.github/workflows/main.yml:118-129](), [.github/workflows/promptfoo-code-scan.yml:52-64]()

## Self-Hosting and Deployment

Promptfoo is designed to be easily self-hosted using containerization. The `Dockerfile` provides a build that includes both the Node.js runtime and a Python environment to support various providers.

The deployment architecture is centered on an Express server serving a React frontend and a SQLite database. Key configuration points include:
- **Persistence**: Database state and local configurations are typically stored in the `.promptfoo` directory within the user's home path [AGENTS.md:24-26]().
- **Networking**: The development server runs the Express API on port `15500` and the Vite web UI on port `3000` [site/docs/contributing.md:81-84]().
- **Health Checks**: The server provides a `/health` endpoint to ensure the application and database migrations are ready [.github/workflows/docker.yml:161-167]().

For details, see [Self-Hosting and Deployment](#9.4).

**Deployment Architecture**

```mermaid
graph TD
    subgraph "Container_Runtime [Docker]"
        EXPRESS["Express_Server (src/server/index.ts)"]
        WEB_UI["React_Frontend (src/app)"]
        SQLITE["SQLite/libSQL (src/database)"]
        PYTHON["Python_Worker (src/providers/python)"]
    end

    VOL["Persistent_Storage (.promptfoo/promptfoo.db)"]
    HEALTH["Health_Check (/health)"]

    EXPRESS --> SQLITE
    EXPRESS --> WEB_UI
    EXPRESS --> PYTHON
    SQLITE --- VOL
    EXPRESS --- HEALTH
```

Sources: [site/docs/contributing.md:81-84](), [AGENTS.md:18-35](), [.github/workflows/docker.yml:161-167]()
The eval command is the primary interface for running LLM evaluations in promptfoo. It orchestrates the evaluation workflow from configuration loading through test execution to results output. The command is implemented through the `doEval` function which handles configuration resolution, test filtering, evaluation execution, and results processing.

For the underlying evaluation engine that executes tests, see [Evaluation Engine](2.1). For command registration and global CLI architecture, see [CLI Architecture](4.1).

## Command Structure

The eval command is registered via `evalCommand()` which defines CLI options using Commander.js, and executes via `doEval()` which orchestrates the evaluation workflow.

**High-Level Command Flow**

```mermaid
graph TB
    subgraph "CLI Registration"
        evalCommand["evalCommand()"]
        programCommand["program.command('eval')"]
        options["CLI Options Definition"]
    end

    subgraph "Execution Entry"
        doEval["doEval()"]
        setupEnv["setupEnv(envPath)"]
        runEvaluation["runEvaluation()"]
    end

    subgraph "Configuration"
        resolveConfigs["resolveConfigs()"]
        loadDefaultConfig["loadDefaultConfig()"]
        TestSuiteSchema["TestSuiteSchema.safeParse()"]
    end

    subgraph "Core Execution"
        runDbMigrations["runDbMigrations()"]
        filterTests["filterTests()"]
        filterProviders["filterProviders()"]
        evaluate["evaluate()"]
    end

    subgraph "Output Handling"
        generateTable["generateTable()"]
        writeMultipleOutputs["writeMultipleOutputs()"]
        createShareableUrl["createShareableUrl()"]
        formatTokenUsage["formatTokenUsage()"]
    end

    evalCommand --> programCommand
    programCommand --> options
    options --> doEval
    doEval --> setupEnv
    doEval --> runEvaluation
    runEvaluation --> resolveConfigs
    resolveConfigs --> loadDefaultConfig
    runEvaluation --> TestSuiteSchema
    runEvaluation --> runDbMigrations
    runEvaluation --> filterTests
    runEvaluation --> filterProviders
    runEvaluation --> evaluate
    evaluate --> generateTable
    evaluate --> writeMultipleOutputs
    evaluate --> createShareableUrl
    evaluate --> formatTokenUsage
```

Sources: [src/commands/eval.ts:18-31](), [src/node/doEval.ts:7-40](), [src/main.ts:88-89]()

## Command-Line Options

The `evalCommand` function defines CLI options using Commander.js, with validation via `EvalCommandSchema` and `CommandLineOptionsSchema`.

**Option Categories**

| Category | Options | Description |
|----------|---------|-------------|
| Core Configuration | `-c, --config` | Path to configuration files or cloud config UUID [src/commands/eval.ts:36-39]() |
| | `-p, --prompts` | Paths to prompt files [src/commands/eval.ts:43]() |
| | `-r, --providers` | Provider specifications [src/commands/eval.ts:44-47]() |
| | `-t, --tests` | Path to test cases CSV/YAML [src/commands/eval.ts:48]() |
| Execution Control | `-j, --max-concurrency` | Maximum concurrent API calls [src/commands/eval.ts:88-91]() |
| | `--repeat` | Number of times to run each test [src/commands/eval.ts:92]() |
| | `--delay` | Delay between tests in milliseconds [src/commands/eval.ts:93]() |
| | `--no-cache` | Disable result caching [src/commands/eval.ts:94-98]() |
| | `--remote` | Force remote inference [src/commands/eval.ts:99]() |
| Test Filtering | `-n, --filter-first-n` | Run only first N tests [src/commands/eval.ts:102]() |
| | `--filter-pattern` | Filter tests by description regex [src/commands/eval.ts:103-106]() |
| | `--filter-providers` | Filter by provider regex [src/commands/eval.ts:115-118]() |
| | `--filter-sample` | Random sample of N tests [src/commands/eval.ts:119]() |
| | `--filter-failing` | Re-run failing tests from previous eval [src/commands/eval.ts:122-124]() |
| | `--filter-errors-only` | Re-run error tests only [src/commands/eval.ts:130-132]() |
| | `--filter-metadata` | Filter by metadata key=value [src/commands/eval.ts:133-139]() |
| Output Control | `-o, --output` | Output file paths [src/commands/eval.ts:142-145]() |
| | `--table` / `--no-table` | Display results table in CLI [src/commands/eval.ts:146-147]() |
| | `--share` / `--no-share` | Create shareable URL [src/commands/eval.ts:149-150]() |
| | `--no-write` | Skip writing to database [src/commands/eval.ts:156-160]() |
| Resume/Retry | `--resume [evalId]` | Resume paused evaluation [src/commands/eval.ts:151-154]() |
| | `--retry-errors` | Retry ERROR results from latest eval [src/commands/eval.ts:155]() |
| Other | `-w, --watch` | Watch files and re-run on changes [src/commands/eval.ts:172]() |
| | `--grader` | Override grading provider [src/commands/eval.ts:163-167]() |
| | `--var` | Set variable in key=value format [src/commands/eval.ts:71-78]() |
| | `--suggest-prompts` | Generate prompt suggestions (max 50) [src/commands/eval.ts:168-171]() |

Sources: [src/commands/eval.ts:31-180](), [src/types/index.ts:99-154](), [src/node/doEval.ts:7-10]()

## Main Execution Flow

The `doEval` function orchestrates the evaluation through an inner `runEvaluation` async function. It manages the transition from natural language configuration to code execution entities like `TestSuite` and `Eval` models.

**doEval Execution Pipeline**

```mermaid
graph TD
    doEval["doEval()"] --> setupEnv1["setupEnv(cmdObj.envPath)"]
    setupEnv1 --> runEval["runEvaluation(initialization=true)"]

    runEval --> telemetryStart["telemetry.record('command_used', 'eval - started')"]
    telemetryStart --> migrateCheck{cmdObj.write?}
    migrateCheck -->|Yes| runDbMigrations["runDbMigrations()"]
    migrateCheck -->|No| conflictCheck
    runDbMigrations --> conflictCheck

    conflictCheck{resumeRaw && retryErrors?}
    conflictCheck -->|Yes| error1["Error: Cannot use both"]
    conflictCheck -->|No| modeCheck{Which Mode?}

    modeCheck -->|resumeRaw| resumeFlow["Resume Flow"]
    modeCheck -->|retryErrors| retryFlow["Retry Errors Flow"]
    modeCheck -->|Normal| normalFlow["Normal Flow"]

    resumeFlow --> loadResume["Eval.findById() or Eval.latest()"]
    loadResume --> restoreConfig["resolveConfigs({}, resumeEval.config)"]
    restoreConfig --> restorePrompts["Restore prompts from resumeEval"]
    restorePrompts --> setResumeFlag["cliState.resume = true"]

    retryFlow --> findLatest["latestEval = await Eval.latest()"]
    findLatest --> getErrors["getErrorResultIds(latestEval.id)"]
    getErrors --> deleteErrors["deleteErrorResults(errorResultIds)"]
    deleteErrors --> recalcMetrics["recalculatePromptMetrics(latestEval)"]
    recalcMetrics --> setResumeFlag

    normalFlow --> resolveConfigs["resolveConfigs(cmdObj, defaultConfig)"]

    setResumeFlag --> setupOptions["Setup EvaluateOptions"]
    resolveConfigs --> setupOptions

    setupOptions --> filteringCheck{resumeEval?}
    filteringCheck -->|No| applyFilters["filterTests(), filterProviders()"]
    filteringCheck -->|Yes| skipFilters["Skip filtering"]

    applyFilters --> checkEmail{redteam with tests?}
    skipFilters --> checkEmail
    checkEmail -->|Yes| emailLoop["promptForEmailUnverified() loop"]
    checkEmail -->|No| checkCloud
    emailLoop --> checkCloud["checkCloudPermissions()"]

    checkCloud --> createEvalRecord["Create Eval model instance"]
    createEvalRecord --> runEvaluate["evaluate(testSuite, evalRecord, options)"]

    runEvaluate --> clearResults["evalRecord.clearResults()"]
    clearResults --> checkSharing{wantsToShare?}
    checkSharing -->|Yes| createUrl["createShareableUrl(evalRecord)"]
    checkSharing -->|No| calcMetrics
    createUrl --> calcMetrics["Calculate success/failure metrics"]

    calcMetrics --> displayTable{cmdObj.table?}
    displayTable -->|Yes| genTable["generateTable(table)"]
    displayTable -->|No| writeOutputs
    genTable --> writeOutputs["writeMultipleOutputs(paths, evalRecord)"]

    writeOutputs --> displaySummary["Display evaluation summary"]
    displaySummary --> tokenDisplay["Display token usage"]
    tokenDisplay --> telemetryEnd["telemetry.record('command_used', 'eval')"]

    telemetryEnd --> watchCheck{cmdObj.watch?}
    watchCheck -->|Yes| setupWatch["Setup chokidar watcher"]
    watchCheck -->|No| exitCodeCheck{passRate < threshold?}

    exitCodeCheck -->|Yes| setExitCode["process.exitCode = failedTestExitCode"]
    exitCodeCheck -->|No| cleanup["Cleanup provider connections"]
    setExitCode --> cleanup

    setupWatch --> watchLoop["Watch for file changes"]
    watchLoop --> onFileChange["On change: clearConfigCache(), runEvaluation()"]
```

Sources: [src/node/doEval.ts:7-40](), [src/evaluator.ts:175-220](), [src/main.ts:139-145]()

## Configuration Processing

Configuration loading follows a two-phase approach: Phase 1 loads environment from CLI args, Phase 2 loads environment from config files via `resolveConfigs`.

**Configuration Resolution Flow**

```mermaid
graph TB
    phase1["Phase 1: setupEnv(cmdObj.envPath)"]

    reloadDefault{defaultConfigPath?}
    reloadDefault -->|Yes| loadDefault["loadDefaultConfig(configDir, configName)"]
    reloadDefault -->|No| checkConfig

    loadDefault --> checkConfig{cmdObj.config?}
    checkConfig -->|Array of paths| iteratePaths["For each configPath"]
    checkConfig -->|No| conflictCheck

    iteratePaths --> isDir{Is directory?}
    isDir -->|Yes| loadDirConfig["loadDefaultConfig(configPath)"]
    isDir -->|No| nextPath
    loadDirConfig --> nextPath["Next config path"]
    nextPath --> conflictCheck

    conflictCheck{resume && retryErrors?}
    conflictCheck -->|Yes| errorOut["Error: Cannot use both together"]
    conflictCheck -->|No| resumeCheck{resumeRaw?}

    resumeCheck -->|True| checkWrite{cmdObj.write === false?}
    checkWrite -->|Yes| errorNoWrite["Error: Resume requires --write"]
    checkWrite -->|No| findEval["Eval.findById(resumeId) or Eval.latest()"]

    findEval --> resolveResume["resolveConfigs({}, resumeEval.config)"]
    resolveResume --> restorePrompts["Restore prompts from resumeEval"]

    resumeCheck -->|False| retryCheck{retryErrors?}
    retryCheck -->|True| checkWriteRetry{cmdObj.write === false?}
    checkWriteRetry -->|Yes| errorNoWriteRetry["Error: Retry requires --write"]
    checkWriteRetry -->|No| findLatest["Eval.latest()"]
    findLatest --> resolveRetry["resolveConfigs({}, latestEval.config)"]
    resolveRetry --> restorePromptsRetry["Restore prompts from latestEval"]

    retryCheck -->|False| normalResolve["resolveConfigs(cmdObj, defaultConfig)"]

    restorePrompts --> phase2
    restorePromptsRetry --> phase2
    normalResolve --> phase2["Phase 2: setupEnv(commandLineOptions.envPath)"]

    phase2 --> checkEvaluateOpts{config.evaluateOptions?}
    checkEvaluateOpts -->|Yes| mergeOpts["Merge into evaluateOptions"]
    checkEvaluateOpts -->|No| setupRuntime
    mergeOpts --> setupRuntime["Setup runtime options (repeat, cache, maxConcurrency, delay)"]

    setupRuntime --> validate["TestSuiteConfigSchema.safeParse(testSuite)"]
    validate --> warnIfInvalid{Valid?}
    warnIfInvalid -->|No| logWarning["logger.warn(validationError)"]
    warnIfInvalid -->|Yes| returnConfig
    logWarning --> returnConfig["Return config, testSuite, basePath"]
```

Sources: [src/util/config/load.ts:183-224](), [src/util/config/default.ts:31-59](), [src/types/index.ts:32-35]()

## Test and Provider Filtering

Filtering is only applied when not resuming (to preserve test indices). The command supports multiple filter types implemented in `filterTests` and `filterProviders`.

**Filtering Pipeline**

```mermaid
graph TB
    resumeCheck{resumeEval exists?}
    resumeCheck -->|Yes| skipFilters["Skip all filtering"]
    resumeCheck -->|No| buildFilterOpts["Build FilterOptions"]

    buildFilterOpts --> filterOptsList["FilterOptions:
    - failing
    - errorsOnly
    - firstN
    - metadata
    - pattern
    - sample"]

    filterOptsList --> callFilterTests["filterTests(testSuite, filterOptions)"]

    callFilterTests --> checkFilters{Which filters active?}

    checkFilters -->|filterFailing| loadPrevEval["Load previous eval by path or ID"]
    checkFilters -->|filterErrorsOnly| loadPrevEvalErr["Load previous eval by path or ID"]
    checkFilters -->|filterPattern| applyRegex["Filter by description regex"]
    checkFilters -->|filterFirstN| takeFirst["Take first N tests"]
    checkFilters -->|filterSample| randomSample["Random sample of N tests"]
    checkFilters -->|filterMetadata| matchMetadata["Match metadata key=value"]

    loadPrevEval --> getFailingIndices["Get failing test indices"]
    loadPrevEvalErr --> getErrorIndices["Get error test indices"]
    getFailingIndices --> filterByIndices
    getErrorIndices --> filterByIndices["Filter testSuite.tests by indices"]

    applyRegex --> updatedTests
    takeFirst --> updatedTests
    randomSample --> updatedTests
    matchMetadata --> updatedTests
    filterByIndices --> updatedTests["testSuite.tests = filtered"]

    updatedTests --> filterProvCheck{filterProviders or filterTargets?}
    filterProvCheck -->|Yes| callFilterProviders["filterProviders(providers, filterString)"]
    filterProvCheck -->|No| complete

    callFilterProviders --> providerRegex["Match provider.id or provider.label with regex"]
    providerRegex --> complete["Return filtered testSuite"]
```

Sources: [src/util/eval/filterTests.ts:11-125](), [src/util/eval/filterProviders.ts:8-37](), [src/util/config/load.ts:42-44]()

## Results Processing and Output

After `evaluate()` completes, `doEval` processes results for display and export. It uses `generateTable` for CLI output and persistence utilities for file export.

**Output Processing Pipeline**

```mermaid
graph TD
    evalComplete["evaluate() returns"] --> clearResults["evalRecord.clearResults()"]

    clearResults --> checkSharing{"wantsToShare?"}
    checkSharing --> determineShare["hasExplicitDisable = cmdObj.share === false || cmdObj.noShare || PROMPTFOO_DISABLE_SHARING"]
    determineShare --> wantsShare["wantsToShare = !hasExplicitDisable && (cmdObj.share || config.sharing || cloudConfig.isEnabled())"]

    wantsShare --> isSharingEnabled{isSharingEnabled(evalRecord)?}
    isSharingEnabled -->|Yes| createUrl["shareableUrl = await createShareableUrl(evalRecord)"]
    isSharingEnabled -->|No| collectMetrics
    createUrl --> setShared["evalRecord.shared = true"]
    setShared --> collectMetrics

    collectMetrics["Calculate metrics from evalRecord.prompts"] --> calcLoop["For each prompt:
    - testPassCount
    - testFailCount
    - testErrorCount
    - tokenUsage"]

    calcLoop --> totals["totalTests = successes + failures + errors
    passRate = (successes / totalTests) * 100"]

    totals --> tableCheck{cmdObj.table && totalTests < 500?}
    tableCheck -->|Yes| getTable["table = await evalRecord.getTable()"]
    tableCheck -->|No| checkOutputPaths
    getTable --> genTable["outputTable = generateTable(table)"]
    genTable --> logTable["logger.info(outputTable.toString())"]
    logTable --> checkTruncate{table.body.length > 25?}
    checkTruncate -->|Yes| logTruncate["logger.info('... N more rows not shown ...')"]
    checkTruncate -->|No| checkOutputPaths

    logTruncate --> checkOutputPaths{outputPath configured?}
    checkOutputPaths -->|Yes| filterPaths["paths = filter out .jsonl paths"]
    checkOutputPaths -->|No| printBorder1
    filterPaths --> writeMultiple["await writeMultipleOutputs(paths, evalRecord, shareableUrl)"]
    writeMultiple --> logOutput["logger.info('Writing output to ...')"]

    logOutput --> printBorder1["printBorder()"]
    printBorder1 --> displayResult{shareableUrl?}
    displayResult -->|Yes| logShare["logger.info('Evaluation complete: ' + shareableUrl)"]
    displayResult -->|No| checkWantsShare{wantsToShare?}

    checkWantsShare -->|Yes,!enabled| notCloudEnabled["notCloudEnabledShareInstructions()"]
    checkWantsShare -->|No| logComplete["logger.info('Evaluation complete. ID: ...')
    + view/share instructions"]

    logShare --> printBorder2
    notCloudEnabled --> printBorder2
    logComplete --> printBorder2["printBorder()"]
```

Sources: [src/index.ts:22-24](), [src/evaluator.ts:87-88](), [src/types/index.ts:104-106]()

## Token Usage Display

Token usage is accumulated and displayed in a hierarchical format with provider breakdown using `TokenUsageTracker`.

**Token Usage Display Structure**

```mermaid
graph TB
    accumulateTokens["accumulateTokenUsage(tokenUsage, prompt.metrics.tokenUsage)"]

    accumulateTokens --> checkTotal{tokenUsage.total > 0?}
    checkTotal -->|Yes| displayHeader["logger.info('Token Usage Summary:')"]
    checkTotal -->|No| skip["Skip token display"]

    displayHeader --> isRedteam{isRedteam?}
    isRedteam -->|Yes| displayProbes["logger.info('Probes: ' + numRequests)"]
    isRedteam -->|No| displayEval
    displayProbes --> displayEval

    displayEval["logger.info('Evaluation:')
    - Total
    - Prompt
    - Completion
    - Cached (if > 0)
    - Reasoning (if > 0)"]

    displayEval --> getProviders["providerIds = tracker.getProviderIds()"]
    getProviders --> checkMultiple{providerIds.length > 1?}

    checkMultiple -->|Yes| sortProviders["Sort providers by total token usage DESC"]
    checkMultiple -->|No| checkGrading

    sortProviders --> loopProviders["For each provider:"]
    loopProviders --> displayProvider["logger.info(provider ID + total + numRequests)"]
    displayProvider --> hasBreakdown{usage.prompt || usage.completion?}
    hasBreakdown -->|Yes| displayDetails["logger.info(breakdown string)"]
    hasBreakdown -->|No| nextProvider
    displayDetails --> nextProvider["Next provider"]
    nextProvider --> checkGrading

    checkGrading{tokenUsage.assertions.total > 0?}
    checkGrading -->|Yes| displayGrading["logger.info('Grading:')
    - Total
    - Prompt
    - Completion
    - Cached (if > 0)
    - Reasoning (if > 0)"]
    checkGrading -->|No| grandTotal

    displayGrading --> grandTotal["grandTotal = evalTokens.total + assertions.total"]
    grandTotal --> displayGrand["logger.info('Grand Total: ' + grandTotal + ' tokens')"]
    displayGrand --> printBorder["printBorder()"]
```

Sources: [src/evaluator.ts:102-111](), [src/util/tokenUsageUtils.ts:103-111](), [src/types/index.ts:4-7]()

## Resume and Retry Logic

The eval command supports two recovery modes: `--resume` for continuing evaluations and `--retry-errors` for re-running specific failures.

### Resume Mode

Resume mode loads a previous `Eval` record and sets `cliState.resume = true`, allowing the evaluator to skip already completed test cases.

```mermaid
graph TB
    resumeFlag["--resume or --resume <id>"]

    resumeFlag --> validateWrite{cmdObj.write === false?}
    validateWrite -->|Yes| error1["Error: Resume requires database persistence"]
    validateWrite -->|No| parseId["resumeId = 'latest' or specified ID"]

    parseId --> findEval{resumeId === 'latest'?}
    findEval -->|Yes| loadLatest["resumeEval = await Eval.latest()"]
    findEval -->|No| loadById["resumeEval = await Eval.findById(resumeId)"]

    loadLatest --> checkFound{resumeEval exists?}
    loadById --> checkFound
    checkFound -->|No| error2["Error: Could not find evaluation"]
    checkFound -->|Yes| logResume["logger.info('Resuming evaluation...')"]

    logResume --> resolveConfig["resolveConfigs({}, resumeEval.config)"]
    resolveConfig --> restorePrompts{resumeEval.prompts?}
    restorePrompts -->|Yes| mapPrompts["testSuite.prompts = resumeEval.prompts.map()"]
    restorePrompts -->|No| setFlag

    mapPrompts --> setFlag["cliState.resume = true"]
    setFlag --> loadRuntimeOpts["Load runtime options from resumeEval"]

    loadRuntimeOpts --> skipFiltering["Skip filterTests() and filterProviders()"]
    skipFiltering --> preserveIndices["Preserve test indices for ID matching"]
    preserveIndices --> evaluate["evaluate() skips completed tests"]
```

Sources: [src/commands/eval.ts:152-154](), [src/cliState.ts:2-5](), [src/node/doEval.ts:40]()

### Retry Errors Mode

Retry errors mode finds failing tests from the latest run and re-runs them using the resume pipeline.

```mermaid
graph TB
    retryFlag["--retry-errors"]

    retryFlag --> validateWrite{cmdObj.write === false?}
    validateWrite -->|Yes| error["Error: Retry requires database persistence"]
    validateWrite -->|No| logStart["logger.info('Retrying ERROR results...')"]

    logStart --> findLatest["latestEval = await Eval.latest()"]
    findLatest --> checkFound{latestEval exists?}
    checkFound -->|No| errorNoEval["Error: No previous evaluation found"]
    checkFound -->|Yes| getErrorIds["errorResultIds = await getErrorResultIds(latestEval.id)"]

    getErrorIds --> checkErrors{errorResultIds.length > 0?}
    checkErrors -->|No| logNoErrors["logger.info('No ERROR results found')"]
    checkErrors -->|Yes| logCount["logger.info('Found N ERROR results to retry')"]

    logCount --> deleteResults["await deleteErrorResults(errorResultIds)"]
    deleteResults --> recalcMetrics["await recalculatePromptMetrics(latestEval)"]

    recalcMetrics --> setupResume["Set resumeEval = latestEval"]
    setupResume --> resolveConfig["resolveConfigs({}, resumeEval.config)"]
    resolveConfig --> restorePrompts["Restore prompts from resumeEval"]
    restorePrompts --> setFlag["cliState.resume = true"]

    setFlag --> evaluate["evaluate() re-runs deleted test cases"]
```

Sources: [src/commands/eval.ts:155](), [src/main.ts:25](), [src/cliState.ts:2-5]()

## Watch Mode

Watch mode (`-w, --watch`) monitors configuration, prompts, and test files, triggering re-evaluation on changes.

**Watch Mode Setup**

```mermaid
graph TB
    watchCheck{cmdObj.watch && !resumeEval?}
    watchCheck -->|No| exitCodeCheck
    watchCheck -->|Yes| initCheck{initialization?}

    initCheck -->|No| exitCodeCheck
    initCheck -->|Yes| getConfigPaths["configPaths = (cmdObj.config || [defaultConfigPath]).filter(Boolean)"]

    getConfigPaths --> checkPaths{configPaths.length > 0?}
    checkPaths -->|No| errorNoPaths["logger.error('Could not locate config file(s)')
    process.exitCode = 1"]
    checkPaths -->|Yes| getBasePath["basePath = path.dirname(configPaths[0])"]

    getBasePath --> extractPromptPaths["promptPaths = config.prompts
    .filter(starts with 'file://')
    .map(resolve path)"]

    extractPromptPaths --> extractProviderPaths["providerPaths = config.providers
    .filter(starts with 'file://')
    .map(resolve path)"]

    extractVarPaths --> consolidate["watchPaths = Array.from(new Set([
    ...configPaths,
    ...promptPaths,
    ...providerPaths,
    ...varPaths
    ]))"]

    consolidate --> createWatcher["watcher = chokidar.watch(watchPaths, {
    ignored: /^\./,
    persistent: true
    })"]

    createWatcher --> registerHandlers["watcher.on('change', handler)
    watcher.on('error', handler)
    watcher.on('ready', handler)"]

    registerHandlers --> onChange["On 'change' event:"]
    onChange --> logChange["printBorder()
    logger.info('File change detected: ' + path)
    printBorder()"]
    logChange --> clearCache["clearConfigCache()"]
    clearCache --> rerun["await runEvaluation()"]
```

Sources: [src/commands/eval.ts:172](), [src/types/index.ts:126](), [src/util/config/load.ts:54]()

## Error Handling and Exit Codes

The eval command implements error handling with specific exit codes for different failure scenarios. System-level errors use `EvalRunError`.

### Exit Code Strategy

| Condition | Exit Code | Source |
|-----------|-----------|--------|
| Success (Pass Rate >= Threshold) | 0 | CLI Default |
| Pass Rate < Threshold | `PROMPTFOO_FAILED_TEST_EXIT_CODE` (default 100) | [src/envars.ts:20]() |
| System/Configuration Error | 1 | [src/main.ts:84]() |
| No Prompts Selected | 1 | [src/evaluator.ts:137-142]() |

Sources: [src/node/doEval.ts:40](), [src/envars.ts:20](), [src/evaluator.ts:137-142]()

# Utility Commands




This page documents the utility commands available in the promptfoo CLI that support project setup, resource management, result sharing, authentication, and configuration management. These commands provide the infrastructure for the core evaluation and red teaming workflows.

---

## Command Overview

The following utility commands are registered on the root Commander.js program in `main.ts`:

| Command | Source File | Primary Purpose |
|---|---|---|
| `init` | [src/commands/init.ts:214-248]() | Initialize a project or download an example |
| `share` | [src/commands/share.ts:55-205]() | Upload and share eval or model audit results |
| `auth` | [src/commands/auth.ts:251-340]() | Manage cloud authentication and team context |
| `config` | [src/commands/config.ts:1-10]() | Read and write local configuration values |
| `show` | [src/commands/show.ts:174-213]() | Display details of specific evals, prompts, or datasets |
| `list` | [src/commands/list.ts:10-156]() | List evals, prompts, and datasets in the local database |
| `cache` | [src/commands/cache.ts:1-44]() | Manage and clear the provider response cache |
| `delete` | [src/commands/delete.ts:1-30]() | Remove evaluations from the local database |
| `import` | [src/commands/import.ts:1-53]() | Import eval records from JSON or OpenAI Evals formats |
| `export` | [src/commands/export.ts:120-225]() | Export eval records or debug logs |
| `validate` | [src/commands/validate.ts:316-375]() | Validate configurations and provider connectivity |
| `view` | [src/commands/view.ts:1-30]() | Start the local web viewer for results |

**Command hierarchy diagram:**

```mermaid
graph TD
  cli["promptfoo (main.ts)"]

  cli --> init["init [directory]"]
  cli --> share["share [id]"]
  cli --> auth["auth"]
  cli --> config["config"]
  cli --> show["show [id]"]
  cli --> list["list"]
  cli --> validate["validate"]
  cli --> view["view"]

  init --> init_opts["--no-interactive\n--example [name]"]

  list --> list_evals["evals"]
  list --> list_prompts["prompts"]
  list --> list_datasets["datasets"]

  validate --> validate_config["-c, --config"]
  validate --> validate_target["target <id>"]

  show --> show_eval["eval [id]"]
  show --> show_prompt["prompt <id>"]
  show --> show_dataset["dataset <id>"]
```

Sources: [src/commands/init.ts:214-248](), [src/commands/show.ts:174-213](), [src/commands/list.ts:10-156](), [src/commands/validate.ts:316-375]()

---

## `init` — Project Initialization

The `init` command bootstraps a new promptfoo project. It supports interactive guided setup and direct example download from the GitHub repository.

### Example Download Flow
When the `--example` flag is used, the CLI interacts with the GitHub API to fetch files from the `examples/` directory of the promptfoo repository [src/commands/init.ts:156-183](). It attempts to use the current package version as a Git ref, falling back to `main` if the version is not found [src/commands/init.ts:188-192]().

```mermaid
flowchart TD
  A["initCommand action"] --> B{"--example flag?"}
  B -- "string" --> D["resolveExampleSelection()"]
  B -- "none" --> E["initializeProject()"]
  D --> F["downloadExample(exampleName, targetDir)"]
  F --> G["downloadDirectory(dirPath, targetDir)"]
  G --> H["GitHub API: /repos/promptfoo/promptfoo/contents/examples/{dirPath}"]
  H -- "Try VERSION ref" --> I{"Success?"}
  I -- "No" --> J["Retry with 'main' ref"]
  J --> K["downloadFile(url, filePath)"]
  I -- "Yes" --> K
  K --> L["fs.writeFile()"]
```

Sources: [src/commands/init.ts:156-183](), [src/commands/init.ts:107-127](), [src/commands/init.ts:210-254]()

### Interactive Onboarding
If no example is specified, `initializeProject` in `src/onboarding.ts` runs a wizard to generate a `promptfooconfig.yaml` [src/onboarding.ts:313-650]().

- **Use Case Selection**: Users choose between `redteam`, `rag`, `agent`, or `compare` [src/onboarding.ts:318-326]().
- **Template Rendering**: Uses `getNunjucksEngine()` to render the `CONFIG_TEMPLATE` [src/onboarding.ts:20-106]().
- **Provider Scaffolding**: Depending on selection, it may create `provider.py`, `provider.js`, or `context.py` files [src/onboarding.ts:385-450]().
- **Red Team Init**: The `redteamInit` function provides a specialized onboarding for adversarial testing, allowing users to define a target purpose and select specific vulnerability plugins [src/redteam/commands/init.ts:202-300]().

Sources: [src/onboarding.ts:313-650](), [src/onboarding.ts:652-691](), [src/redteam/commands/init.ts:202-300]()

---

## `share` — Sharing Results

The `share` command uploads evaluation or model audit results to a remote server (promptfoo cloud or self-hosted) to generate a shareable URL.

### Data Flow for Sharing
The implementation uses a chunked upload mechanism to handle large evaluation records [src/share.ts:213-240](). It supports both standard `Eval` objects and `ModelAudit` records [src/share.ts:22-24]().

1. **Permission Check**: Validates cloud permissions and organization context via `checkCloudPermissions` [src/share.ts:14-17]().
2. **Initial Record**: Sends the base `Eval` metadata (prompts, config, traces) via `sendEvalRecord` [src/share.ts:137-175]().
3. **Result Chunking**: Results are split into batches using `sendChunkedResults` to avoid payload size limits [src/share.ts:213-240]().
4. **Adaptive Resizing**: If a chunk fails due to `PAYLOAD_TOO_LARGE`, the system automatically reduces the chunk size and retries [src/share.ts:37-51]().
5. **Blob Handling**: Large assets are uploaded separately via `uploadBlobRefsForShare` or inlined via `inlineBlobRefsForShare` depending on the storage configuration [src/share.ts:7-19]().

```mermaid
sequenceDiagram
  participant CLI as "CLI (src/commands/share.ts)"
  participant Share as "Share Module (src/share.ts)"
  participant Remote as "Remote API"

  CLI->>Share: createShareableUrl(evalRecord)
  Share->>Remote: POST /api/eval (Metadata via sendEvalRecord)
  Remote-->>Share: { id: "remote-eval-id" }
  loop For each chunk of results
    Share->>Remote: POST /api/eval/remote-eval-id/results (via sendChunkWithRetry)
    alt Success
      Remote-->>Share: 200 OK
    else Payload Too Large
      Share->>Share: Reduce chunk size (AdaptiveChunkConfig)
      Share->>Remote: Retry chunk
    end
  end
  Share-->>CLI: Final Shareable URL
```

Sources: [src/share.ts:137-211](), [src/share.ts:213-240](), [src/commands/share.ts:25-53](), [src/share.ts:37-51]()

---

## `auth` — Authentication

The `auth` command manages the connection between the CLI and Promptfoo Cloud using the `CloudConfig` singleton [src/globalConfig/cloud.ts:94-124]().

- **Login**: Supports API key login via `validateAndSetApiToken` or browser-based OAuth via `openAuthBrowser` [src/commands/auth.ts:208-250](), [src/util/server.ts:15]().
- **Team Context**: `setupTeamContext` allows users to select a specific team and organization to associate their work with [src/commands/auth.ts:119-206]().
- **Persistence**: Validated tokens, hostnames, and custom auth headers are stored in the global config file via `cloudConfig` [src/globalConfig/cloud.ts:182-205]().
- **Resolution**: The CLI resolves the API host by checking the config file, `PROMPTFOO_CLOUD_API_URL`, and finally defaulting to `https://api.promptfoo.app` [src/globalConfig/cloud.ts:143-163]().

Sources: [src/commands/auth.ts:119-206](), [src/commands/auth.ts:208-250](), [src/globalConfig/cloud.ts:94-216](), [src/util/cloud.ts:27-43]()

---

## `show` and `list` — Data Inspection

These commands interact with the SQLite database via Drizzle ORM to display historical results.

### `show` Command
`handleEval(id)` fetches an evaluation by ID using `Eval.findById(id)` [src/commands/show.ts:81-82](). It then uses `generateTable()` from `src/table.ts` to render the results in the terminal [src/commands/show.ts:93](). The table generator handles ANSI colors for PASS/FAIL status and ellipsizes long outputs [src/table.ts:30-43]().

### `list` Command
Lists resources stored in the database:
- **Evals**: Uses `Eval.getMany()` [src/commands/list.ts:29]().
- **Prompts**: Uses `getPrompts()` [src/commands/list.ts:72]().
- **Datasets**: Uses `getTestCases()` [src/commands/list.ts:114]().

Sources: [src/commands/show.ts:81-123](), [src/commands/list.ts:10-156](), [src/table.ts:7-48]()

---

## `validate` — Configuration & Provider Testing

The `validate` command ensures that your configuration is syntactically correct and that providers are reachable.

- **Config Validation**: Validates `promptfooconfig.yaml` against the `UnifiedConfigSchema` [src/commands/validate.ts:273-290]().
- **Connectivity Testing**: `testProviderConnectivity` attempts a simple API call to verify credentials and network access [src/server/routes/providers.ts:71-75]().
- **Cloud Provider Resolution**: If a provider ID is a UUID, the system attempts to fetch the configuration from Promptfoo Cloud via `getProviderFromCloud` [src/util/cloud.ts:51-80]().

Sources: [src/commands/validate.ts:273-290](), [src/server/routes/providers.ts:49-94](), [src/util/cloud.ts:51-80]()

---

## MCP Server Tools

Promptfoo exposes its utility functions to AI agents via the Model Context Protocol (MCP) [src/commands/mcp/server.ts]().

| MCP Tool | Implementation File | Role |
|---|---|---|
| `runEvaluation` | [src/commands/mcp/tools/runEvaluation.ts]() | Triggers a full evaluation pipeline |
| `testProvider` | [src/server/routes/providers.ts:49-94]() | Verifies connectivity for a specific provider config |
| `redteamGenerate` | [src/redteam/commands/generate.ts]() | Generates adversarial test cases |
| `targetDiscovery` | [src/redteam/commands/discover.ts]() | Runs the Target Discovery Agent to map an LLM's purpose |
| `validatePromptfooConfig` | [src/commands/validate.ts]() | Validates a configuration object |

### Target Discovery Agent
The `doTargetPurposeDiscovery` function uses an iterative probing mechanism to identify a target's purpose, limitations, and tools [src/redteam/commands/discover.ts:149-158](). It communicates with the target provider over multiple turns [src/redteam/commands/discover.ts:102-103]().

```mermaid
graph LR
  A["doTargetPurposeDiscovery (discover.ts)"] --> B["resolveDiscoveryProviderContext"]
  B --> C["fetchWithProxy (Remote API via fetch/index.ts)"]
  C --> D["normalizeTargetPurposeDiscoveryResult"]
  D --> E["TargetPurposeDiscoveryResult"]
```

Sources: [src/redteam/commands/discover.ts:114-130](), [src/redteam/commands/discover.ts:149-158](), [src/server/routes/providers.ts:96-135]()

---

## Logging Infrastructure

The `logger.ts` utility provides a unified logging interface wrapping `winston` [src/logger.ts:185-201]().

- **Sanitization**: Automatically redacts sensitive information like Azure Blob SAS tokens and API keys using `redactAzureBlobSasTokens` and `sanitizeObject` [src/logger.ts:11](), [src/share.ts:144-146]().
- **Location Tracking**: In debug mode, the logger captures the caller's file and line number via `getCallerLocation` [src/logger.ts:97-126]().
- **Formatters**: Provides `consoleFormatter` for terminal output and `fileFormatter` for persistent logs [src/logger.ts:151-183]().

Sources: [src/logger.ts:97-201](), [src/share.ts:144-146](), [test/logger.test.ts:179-202]()

# Environment and Logging




This document describes the environment variable management and logging systems in promptfoo. These systems provide consistent configuration handling across the CLI, web UI, and library usage, along with structured logging for debugging and troubleshooting.

## Environment Variable System

promptfoo uses a centralized environment variable management system implemented in `[src/envars.ts]()`. This system provides type-safe access to over 200 environment variables used for feature flags, provider configuration, and system behavior tuning.

### Resolution Hierarchy

Environment variables are resolved in a two-tier hierarchy. This allows configuration files to override system environment variables through the `env` property in the test suite configuration. The CLI state is checked first via `cliState.config.env` `[src/cliState.ts:13-13]()`, followed by `process.env`. The system also utilizes `dotenv` to load variables from `.env` files at startup `[src/envars.ts:6-6]()`.

**Natural Language to Code Entity Space: Environment Resolution**

```mermaid
graph TD
    subgraph "Natural-Language-Space"
    UserReq["User Request for Env Var"]
    ConfigOverride["Config-level Override"]
    SysEnv["System Environment"]
    end

    subgraph "Code-Entity-Space"
    getEnvString["getEnvString() function"]
    cliState["cliState.config.env"]
    processEnv["process.env"]
    dotenv["dotenv.config()"]
    end

    UserReq --> getEnvString
    getEnvString -->|1. Check| cliState
    getEnvString -->|2. Check| processEnv
    processEnv -.->|Initialized by| dotenv
    ConfigOverride -.-> cliState
    SysEnv -.-> processEnv
```

**Sources:** `[src/envars.ts:1-7]()`, `[src/envars.ts:368-386]()`, `[src/cliState.ts:1-20]()`

### Type-Safe Accessor Functions

The system provides four type-safe accessor functions, all exported from `[src/envars.ts]()`. These functions handle the conversion from string-based environment variables to internal TypeScript types:

| Function | Return Type | Parsing Logic |
|----------|-------------|---------------|
| `getEnvString()` | `string \| undefined` | Returns raw string value or default `[src/envars.ts:368-386]()` |
| `getEnvBool()` | `boolean` | Accepts: `"1"`, `"true"`, `"yes"`, `"yup"`, `"yeppers"` `[src/envars.ts:394-411]()` |
| `getEnvInt()` | `number \| undefined` | Uses `Number.parseInt()` with base 10 `[src/envars.ts:419-431]()` |
| `getEnvFloat()` | `number \| undefined` | Uses `Number.parseFloat()` `[src/envars.ts:439-447]()` |

### Environment Variable Categories

Environment variables are defined in the `EnvVars` type definition `[src/envars.ts:9-357]()`. This type serves as the central registry for all supported keys (e.g., `EnvVarKey`).

```mermaid
graph TB
    EnvVars["EnvVars Type (src/envars.ts)"]

    Core["Core Configuration<br/>LOG_LEVEL, NODE_ENV"]
    Features["Feature Flags<br/>PROMPTFOO_DISABLE_*<br/>PROMPTFOO_ENABLE_*"]
    Config["Configuration Options<br/>PROMPTFOO_CACHE_PATH<br/>PROMPTFOO_LOG_DIR"]
    Providers["Provider Settings<br/>OPENAI_API_KEY<br/>ANTHROPIC_API_KEY"]
    System["System Settings<br/>HTTP_PROXY<br/>ALL_PROXY"]
    OTEL["OpenTelemetry<br/>PROMPTFOO_OTEL_ENABLED"]

    EnvVars --> Core
    EnvVars --> Features
    EnvVars --> Config
    EnvVars --> Providers
    EnvVars --> System
    EnvVars --> OTEL
```

**Sources:** `[src/envars.ts:9-169]()`

#### Key Feature Flags
- `PROMPTFOO_DISABLE_TELEMETRY`: Opt out of anonymous usage tracking `[src/envars.ts:56-56]()`.
- `PROMPTFOO_DISABLE_REDTEAM_REMOTE_GENERATION`: Disable remote generation for red team features `[src/envars.ts:51-51]()`.
- `PROMPTFOO_OTEL_ENABLED`: Enable OpenTelemetry tracing for LLM provider calls `[src/envars.ts:89-89]()`.
- `PROMPTFOO_CACHE_ENABLED`: Toggles evaluation caching `[src/envars.ts:21-21]()`.

## Logging System Architecture

The logging system is built on `winston` and provides structured, level-based logging with automatic file rotation and location tracking.

### Core Components

```mermaid
graph TB
    subgraph "Logging-Entrypoints"
    LoggerAPI["logger (src/logger.ts)"]
    WinstonLogger["winstonLogger (winston.Logger)"]
    end

    subgraph "Transports"
    ConsoleTransport["Console Transport"]
    FileTransport["File Transport (winston.transports.File)"]
    end

    subgraph "Formatting"
    ConsoleFormatter["consoleFormatter (Chalk-colored)"]
    FileFormatter["fileFormatter (ISO Timestamp)"]
    end

    LoggerAPI --> WinstonLogger
    WinstonLogger --> ConsoleTransport
    WinstonLogger --> FileTransport

    ConsoleTransport --> ConsoleFormatter
    FileTransport --> FileFormatter
```

**Sources:** `[src/logger.ts:151-201]()`

### Log Levels

The system defines four log levels in `LOG_LEVELS` `[src/logger.ts:35-40]()`:
- `error` (0): Critical errors, displayed in red.
- `warn` (1): Warnings, displayed in yellow.
- `info` (2): Informational messages (default).
- `debug` (3): Detailed debugging information, displayed in cyan.

### Per-Run Log Files

The system supports file-based logging for troubleshooting.
- **Log Directory**: Configured via `PROMPTFOO_LOG_DIR` or defaults to the config directory `[src/logger.ts:131-131]()`.
- **Rotation**: The system retains up to 50 log files (`MAX_LOG_FILES`), deleting the oldest first `[src/logger.ts:13-13]()`.
- **Stderr Routing**: Commands that print machine-readable payloads (like SARIF) use `PROMPTFOO_LOG_TO_STDERR` to ensure logs do not corrupt stdout `[src/logger.ts:191-197]()`.

### Caller Location Tracking

The `getCallerLocation()` function extracts file and line information from the call stack for debug logs `[src/logger.ts:97-126]()`. It parses the stack trace to identify the actual source code location, skipping internal logger frames.

**Natural Language to Code Entity Space: Debug Location Tracking**

```mermaid
flowchart TD
    subgraph "Execution-Context"
    UserCode["Developer calls logger.debug()"]
    LoggerMethod["Logger internal method"]
    end

    subgraph "Location-Extraction"
    ErrorObj["new Error('stack trace capture')"]
    StackSplit["stack.split('\\n')"]
    RegexMatch["match(/at (.*) \\((.+):(\\d+):(\\d+)\\)/)"]
    PathBasename["path.basename(filePath)"]
    end

    UserCode --> LoggerMethod
    LoggerMethod --> ErrorObj
    ErrorObj --> StackSplit
    StackSplit --> RegexMatch
    RegexMatch --> PathBasename
    PathBasename --> Output["[filename:line]"]
```

**Sources:** `[src/logger.ts:97-126]()`

### Specialized Logging Features

- **Source Map Support**: The system lazily loads `source-map-support` via `initializeSourceMapSupport()` when debug is enabled to map TypeScript stack traces back to the original source `[src/logger.ts:73-91]()`.
- **Structured Logging**: Can be enabled via `setStructuredLogging(true)`, allowing machine-readable JSON output `[src/logger.ts:31-33]()`.
- **Log Callback**: A global `globalLogCallback` can be registered via `setLogCallback()` to intercept log messages, primarily used by the Web UI to stream logs `[src/logger.ts:16-20]()`.
- **Sanitization**: The logger includes `SanitizedLogContext` and uses `sanitizeObject` and `sanitizeUrl` to ensure sensitive data like API keys or PII are not leaked into log files `[src/logger.ts:48-54]()`, `[src/logger.ts:11-11]()`.

## Telemetry System

The `Telemetry` class in `[src/telemetry.ts]()` handles anonymous usage tracking.

- **Client**: Uses `posthog-node` for event capture `[src/telemetry.ts:1-3]()`.
- **Opt-out**: Controlled by `PROMPTFOO_DISABLE_TELEMETRY` `[src/telemetry.ts:107-108]()`.
- **Initialization**: The singleton is initialized with a unique ID from `getUserId()` `[src/telemetry.ts:63-69]()`.
- **Events**: Events are sent to both PostHog and a backup endpoint `R_ENDPOINT` `[src/telemetry.ts:136-175]()`.

**Sources:** `[src/telemetry.ts:53-222]()`, `[src/globalConfig/accounts.ts:63-73]()`

## Environment Variables Reference (Summary)

| Variable | Purpose |
|----------|---------|
| `LOG_LEVEL` | Sets verbosity: `error`, `warn`, `info`, `debug` `[src/envars.ts:13-13]()` |
| `PROMPTFOO_CACHE_PATH` | Custom path to evaluation cache `[src/envars.ts:118-118]()` |
| `PROMPTFOO_EVAL_TIMEOUT_MS` | Global timeout for individual provider calls `[src/envars.ts:63-63]()` |
| `PROMPTFOO_LOG_DIR` | Directory for file-based logs `[src/envars.ts:131-131]()` |
| `PROMPTFOO_LOG_TO_STDERR` | Redirects console logs to stderr `[src/envars.ts:132-132]()` |
| `PROMPTFOO_OTEL_ENABLED` | Enables OpenTelemetry tracing `[src/envars.ts:89-89]()` |
| `PROMPTFOO_DISABLE_SHARING` | Disables result sharing functionality `[src/envars.ts:55-55]()` |

**Sources:** `[src/envars.ts:9-155]()`, `[src/logger.ts:189-197]()`

# Red Team System




The Red Team System is promptfoo's adversarial testing framework for identifying vulnerabilities in LLM applications. It automatically generates malicious inputs using specialized plugins, applies attack strategies like jailbreaks and prompt injections, and evaluates target systems for security weaknesses across 50+ vulnerability categories including privacy leaks, harmful content generation, and access control bypasses [site/docs/red-team/quickstart.md:16-21]().

This page is a system-level overview. Detailed documentation is split across subsections:

| Subsection | Topic |
|---|---|
| [Red Team Architecture](#5.1) | Overall design, key concepts, vulnerability categories |
| [Test Generation and Configuration](#5.2) | `synthesize()`, `SynthesizeOptions`, plugin/strategy expansion |
| [Plugins and Metadata](#5.3) | Plugin registry, builtin plugins, custom plugin authoring |
| [Strategies](#5.4) | Attack transformation strategies, `jailbreak`, `prompt-injection`, etc. |
| [Attack Providers](#5.5) | Iterative attack providers: `CrescendoProvider`, `GoatProvider`, etc. |
| [Graders and Evaluation](#5.6) | `RedteamGraderBase`, rubric rendering, result suggestions |
| [Red Team Commands](#5.7) | CLI subcommands: `init`, `generate`, `run`, `discover`, `report` |
| [Provider Manager and Shared Utilities](#5.8) | `redteamProviderManager`, `getTargetResponse()`, runtime transforms |

For information about the evaluation engine that executes red team tests, see page 2.1. For provider integration details, see page 3.

## System Architecture

The Red Team System orchestrates test generation through a plugin-strategy pipeline, where plugins generate base adversarial inputs and strategies transform them into sophisticated attacks [site/docs/red-team/index.md:44-51]().

### Red Team High-Level Flow
```mermaid
graph TB
    CLI["CLI Commands<br/>(redteam/commands/*)"] --> Synthesize["synthesize()<br/>(redteam/index.ts)"]

    Config["RedteamConfigSchema<br/>(validators/redteam.ts)"] --> Synthesize

    Synthesize --> PluginSystem["Plugin System<br/>(redteam/plugins/*)"]
    Synthesize --> StrategySystem["Strategy System<br/>(redteam/strategies/*)"]

    PluginSystem --> TestGeneration["Test Case Generation"]
    StrategySystem --> TestGeneration

    TestGeneration --> Evaluation["Evaluation Engine<br/>(evaluator.ts)"]

    Evaluation --> Results["RedteamResults<br/>(types/index.ts)"]

    RemoteGen["Remote Generation<br/>(remoteGeneration.ts)"] --> PluginSystem
    Providers["Provider System<br/>(providers/*)"] --> Evaluation
```

**Sources:** [src/redteam/index.ts:1-100](), [src/redteam/commands/generate.ts:1-66](), [src/validators/redteam.ts:1-60](), [src/redteam/shared.ts:1-50]()

## Core Components

### Synthesis Engine

The `synthesize()` function in [src/redteam/index.ts:700]() is the central orchestrator, coordinating plugin execution, strategy application, and test case assembly. It manages concurrency, progress tracking, and data flow between components.

### Synthesis Data Flow
```mermaid
graph LR
    Input["SynthesizeOptions\n(redteam/types.ts:224)"] --> Synthesize["synthesize()\n(redteam/index.ts:700)"]

    Synthesize --> PluginExec["Plugin loop\n(async.queue)"]
    Synthesize --> StrategyApp["applyStrategies()\n(index.ts:350)"]

    PluginExec --> BaseTests["TestCaseWithPlugin[]"]
    StrategyApp --> TransformedTests["Strategy-wrapped tests"]

    BaseTests --> FinalTests["Combined test cases"]
    TransformedTests --> FinalTests

    FinalTests --> Output["{purpose, entities,\ntestCases, injectVar,\nfailedPlugins}"]
```

Key responsibilities:
- **Plugin validation**: Inline `validatePlugin` function at [src/redteam/index.ts:982-1009]() filters unregistered or invalid plugins before execution.
- **Concurrency management**: Uses `async.queue` with the `maxConcurrency` parameter, capped by `MAX_MAX_CONCURRENCY` at [src/redteam/index.ts:187]().
- **Progress tracking**: Updates `cli-progress` bars during generation [src/redteam/index.ts:1112-1119]().
- **Strategy orchestration**: Calls `applyStrategies()` at [src/redteam/index.ts:350-567]() after all plugin test cases are generated.
- **Test counting**: `calculateTotalTests()` at [src/redteam/index.ts:621-686]() pre-calculates expected test counts for display.

**Sources:** [src/redteam/index.ts:187-187](), [src/redteam/index.ts:350-567](), [src/redteam/index.ts:621-686](), [src/redteam/index.ts:700-1048](), [src/redteam/types.ts:72-77]()

### Plugin System

Plugins generate adversarial test cases targeting specific vulnerability types. Each registered plugin implements an `action` function matching the shape of `PluginActionParams` [src/redteam/plugins/index.ts:97-98](). For full details see [Plugins and Metadata](#5.3).

### Plugin Registry and Expansion
```mermaid
graph TB
    PluginConfig["RedteamPluginObject\n{id, numTests, config, severity}"] --> PluginRegistry["Plugins array\n(redteam/plugins/index.ts)"]

    PluginRegistry --> BuiltinPlugins["Built-in plugins\n(redteam/plugins/*)"]
    PluginRegistry --> CustomPlugins["CustomPlugin\n(redteam/plugins/custom.ts)"]

    BuiltinPlugins --> HarmPlugins["HARM_PLUGINS\n(constants.ts)"]
    BuiltinPlugins --> PIIPlugins["PII_PLUGINS\n(constants.ts)"]
    BuiltinPlugins --> SecurityPlugins["contracts, bola, rbac,\nsql-injection, etc."]

    CustomPlugins --> FilePlugins["file://path/to/plugin.yaml"]

    HarmPlugins --> TestGen["plugin.action()\n(PluginActionParams)"]
    PIIPlugins --> TestGen
    SecurityPlugins --> TestGen
    FilePlugins --> TestGen

    TestGen --> Metadata["TestCaseWithPlugin\n{pluginId, severity, metadata}"]
```

Plugin categories:
- **`HARM_PLUGINS`**: Generates content violating safety policies [src/redteam/constants/plugins.ts:127-164]().
- **`PII_PLUGINS`**: Tests for personally identifiable information leaks [src/redteam/constants/plugins.ts:114-125]().
- **Security plugins**: Tests access control, injection vulnerabilities, and data exfiltration (e.g., `RBAC_PLUGINS`, `FINANCIAL_PLUGINS`).
- **Custom plugins**: User-defined YAML/JS plugins loaded via the `file://` prefix [src/validators/redteam.ts:102-108]().

**Sources:** [src/redteam/constants/plugins.ts:114-164](), [src/redteam/index.ts:22-29](), [src/redteam/plugins/index.ts:94-98](), [src/validators/redteam.ts:102-108]()

### Strategy System

Strategies transform base test cases into sophisticated attack patterns. They implement delivery mechanisms like jailbreaks, prompt injections, and multi-turn conversations [site/docs/red-team/quickstart.md:106-112](). For full details see [Strategies](#5.4).

### Strategy Application Pipeline
```mermaid
graph LR
    BaseTests["TestCaseWithPlugin[]"] --> StrategyFilter["pluginMatchesStrategyTargets()\n(strategies/util.ts)"]

    StrategyFilter --> StrategyExec["strategy.action()\n(RedteamStrategyObject)"]

    StrategyExec --> Jailbreak["jailbreak\n(strategies/jailbreak/*)"]
    StrategyExec --> Injection["prompt-injection\n(strategies/prompt-injection)"]
    StrategyExec --> Layer["layer\n(strategies/layer)"]
    StrategyExec --> Retry["retry\n(strategies/retry)"]

    Jailbreak --> TransformedTests["TestCase[]\nwith strategyId metadata"]
    Injection --> TransformedTests
    Layer --> TransformedTests
    Retry --> TransformedTests
```

Strategy types:
- **`basic`**: Passes tests through unchanged.
- **`jailbreak`**: Applies adversarial prompting via iterative attack providers.
- **`prompt-injection`**: Embeds malicious instructions inside indirect input fields.
- **`layer`**: Composes multiple strategies sequentially.
- **`retry`**: Re-runs previously failed tests.

The `applyStrategies()` function at [src/redteam/index.ts:350-567]() handles strategy expansion, target plugin filtering, `numTests` capping, and metadata tagging.

**Sources:** [src/redteam/index.ts:350-567](), [src/validators/redteam.ts:189-198]()

### Command System

The CLI interface provides commands for different red team operations. For full details see [Red Team Commands](#5.7).

### CLI Command Wiring
```mermaid
graph TB
    CLI["main.ts"] --> RedteamCommands["redteam/commands/*"]

    RedteamCommands --> GenerateCmd["generate.ts\ndoGenerateRedteam()"]
    RedteamCommands --> RunCmd["run.ts\nredteamRunCommand()"]
    RedteamCommands --> DiscoverCmd["discover.ts\ndoTargetPurposeDiscovery()"]
    RedteamCommands --> PoisonCmd["poison.ts\npoisonCommand()"]

    GenerateCmd --> ConfigLoad["resolveConfigs()\n(util/config/load.ts)"]
    GenerateCmd --> Synthesize["synthesize()\n(redteam/index.ts:700)"]
    GenerateCmd --> OutputWrite["writePromptfooConfig()\n(util/config/writer.ts)"]

    RunCmd --> Shared["doRedteamRun()\n(redteam/shared.ts:23)"]
    Shared --> GenerateCmd
    Shared --> EvalEngine["doEval()\n(commands/eval.ts)"]

    DiscoverCmd --> RemoteAPI["fetchWithProxy()\n(util/fetch/index.ts)"]
```

Key commands:
- **`generate`** (`doGenerateRedteam`): Creates adversarial test cases and writes them to `redteam.yaml` [src/redteam/commands/generate.ts:19-23]().
- **`run`** (`doRedteamRun`): Combines generation and evaluation in one step [src/redteam/shared.ts:23-107]().
- **`discover`**: Automatically extracts the target system's purpose via an agentic dialogue [site/docs/red-team/quickstart.md:68-74]().
- **`poison`**: Generates poisoned documents for RAG red teaming.

**Sources:** [src/redteam/commands/generate.ts:19-23](), [src/redteam/commands/run.ts:19-135](), [src/redteam/shared.ts:23-107]()

## Configuration and Validation

The system uses Zod schemas for configuration validation and type safety. For full details see [Test Generation and Configuration](#5.2).

### Schema Hierarchy
```mermaid
graph TB
    YAML["promptfooconfig.yaml\nredteam section"] --> RedteamConfigSchema["RedteamConfigSchema\n(validators/redteam.ts:250)"]

    RedteamConfigSchema --> PluginValidation["RedteamPluginSchema\n(validators/redteam.ts:128)"]
    RedteamConfigSchema --> StrategyValidation["RedteamStrategySchema\n(validators/redteam.ts:189)"]

    PluginValidation --> PluginExpansion["handleCollectionExpansion()\n(validators/redteam.ts:404)"]
    StrategyValidation --> StrategyExpansion["DEFAULT_STRATEGIES\n(constants.ts)"]

    PluginExpansion --> CollectionPlugins["harmful, pii, default,\nguardrails-eval collections"]
    PluginExpansion --> IndividualPlugins["contracts, bola, rbac,\nsql-injection, etc."]

    CollectionPlugins --> FinalConfig["RedteamFileConfig\n(redteam/types.ts:217)"]
    IndividualPlugins --> FinalConfig
    StrategyExpansion --> FinalConfig

    FinalConfig --> SynthesizeOptions["SynthesizeOptions\n(redteam/types.ts:224)"]
```

Configuration features:
- **Plugin collections**: Shortcuts like `harmful`, `pii`, `default`, and compliance presets like `owasp:llm` expand to matching individual plugins [src/validators/redteam.ts:404-450]().
- **Severity overrides**: Custom severity levels per plugin from configuration or cloud settings [src/redteam/index.ts:195-204]().
- **Strategy targeting**: `config.plugins` on a strategy limits which plugin test cases it transforms [src/redteam/types.ts:172-172]().
- **File references**: `file://` paths supported for custom plugins and strategies [src/validators/redteam.ts:102-109]().
- **Multilingual migration**: `multilingual` strategy is deprecated; use the top-level `language` field instead [src/validators/redteam.ts:152-176]().

**Sources:** [src/redteam/index.ts:195-204](), [src/redteam/types.ts:172-172](), [src/validators/redteam.ts:102-109](), [src/validators/redteam.ts:250-570]()

## Integration Points

The Red Team System integrates with several external systems for provider management, cloud synchronization, and remote inference.

### External Integration Map
```mermaid
graph LR
    RedteamSystem["Red Team System"] --> ProviderSystem["providers/*\n(page 3)"]
    RedteamSystem --> CloudAPI["util/cloud.ts"]
    RedteamSystem --> RemoteGen["remoteGeneration.ts"]

    ProviderSystem --> TargetProviders["Target providers\n(LLM APIs, HTTP, custom)"]
    ProviderSystem --> AttackProviders["redteamProviderManager\n(providers/shared.ts)"]

    CloudAPI --> ConfigSync["getConfigFromCloud()"]
    CloudAPI --> SeverityOverrides["getPluginSeverityOverridesFromCloud()"]
    CloudAPI --> PolicyManagement["getCustomPolicies()\n(util/generation.ts)"]

    RemoteGen --> HealthCheck["checkRemoteHealth()\n(util/apiHealth.ts)"]
    RemoteGen --> RemotePlugins["shouldGenerateRemote()"]
    RemoteGen --> RemoteGrading["doRemoteGrading()\n(remoteGrading.ts)"]

    AttackProviders --> REDTEAM_MODEL["REDTEAM_MODEL\n(default: openai:gpt-4o)"]
```

Integration capabilities:
- **Provider abstraction**: Works with any LLM provider via the `ApiProvider` interface.
- **Cloud synchronization**: Syncs configurations and custom policies from Promptfoo Cloud via `util/cloud.ts` [src/redteam/commands/generate.ts:26-32]().
- **Remote generation**: `shouldGenerateRemote()` decides whether to execute plugins locally or via cloud API [src/redteam/remoteGeneration.ts:45-46]().
- **Health monitoring**: `checkRemoteHealth()` is called in `doRedteamRun()` before test execution [src/redteam/shared.ts:59-65]().

**Sources:** [src/redteam/commands/generate.ts:26-32](), [src/redteam/remoteGeneration.ts:45-46](), [src/redteam/shared.ts:59-65](), [src/redteam/providers/shared.ts:44-44]()
The filtering and search system enables users to narrow down evaluation results based on various criteria including test outcomes, metrics, metadata, and red team-specific attributes. This page covers the frontend filter UI, state management via Zustand, search functionality with debouncing, and backend SQL query construction.

---

## System Overview

The filtering and search system operates across three layers: the frontend UI components that expose filter controls, the Zustand state store that manages filter configuration, and the backend SQL query builder that translates filters into database queries.

### High-Level Architecture

```mermaid
graph TB
    subgraph "Frontend UI Layer"
        SearchInput["SearchInput<br/>(ResultsView.tsx)"]
        FiltersForm["FiltersForm<br/>(FiltersForm.tsx)"]
        FilterModeSelector["FilterModeSelector<br/>(FilterModeSelector.tsx)"]
        ResultsTable["ResultsTable<br/>(ResultsTable.tsx)"]
    end

    subgraph "State Management (Zustand)"
        TableStore["useTableStore<br/>(store.ts)"]
        FiltersState["filters.values<br/>filters.appliedCount<br/>filters.options"]
        SearchState["searchText"]
        FilterMode["filterMode<br/>(all/failures/passes/errors/highlights)"]
    end

    subgraph "Backend Query Layer"
        APIRoute["/api/results/:id/table<br/>(server/routes/eval.ts)"]
        EvalQueries["EvalQueries<br/>(models/eval.ts)"]
        SQLConstruction["combineFilterConditions()"]
        Database["SQLite eval_results table"]
    end

    SearchInput --> SearchState
    FiltersForm --> FiltersState
    FilterModeSelector --> FilterMode

    SearchState --> TableStore
    FiltersState --> TableStore
    FilterMode --> TableStore

    TableStore --> APIRoute
    APIRoute --> EvalQueries
    EvalQueries --> SQLConstruction
    SQLConstruction --> Database
```

**Sources:** [src/app/src/pages/eval/components/ResultsView.tsx:14-43](), [src/app/src/pages/eval/components/store.ts:222-300](), [src/models/eval.ts:160-160](), [src/app/src/pages/eval/components/ResultsTable.tsx:1-40]()

---

## Filter Types and Operators

The system supports six primary filter types, each with specific operators. Filters are defined by the `ResultsFilter` interface in the store.

### Filter Type Definitions

| Filter Type | Purpose | Available Operators | Notes |
|-------------|---------|-------------------|-------|
| `metric` | Filter by custom metric values | `is_defined`, `eq`, `neq`, `gt`, `gte`, `lt`, `lte` | Supports numeric comparisons [src/app/src/pages/eval/components/ResultsView.tsx:110-122]() |
| `metadata` | Filter by test case metadata fields | `equals`, `contains`, `not_contains`, `exists` | Requires field name specification [src/app/src/pages/eval/components/ResultsView.tsx:88-90]() |
| `plugin` | Filter by red team plugin ID | `equals`, `not_equals` | Red team evals only [src/app/src/pages/eval/components/ResultsView.tsx:124-128]() |
| `strategy` | Filter by attack strategy | `equals` | Red team evals only, includes "basic" [src/app/src/pages/eval/components/ResultsView.tsx:130-134]() |
| `severity` | Filter by vulnerability severity | `equals` | Critical/High/Medium/Low/Informational [src/app/src/pages/eval/components/ResultsView.tsx:136-138]() |
| `policy` | Filter by policy violation | `equals` | Formats policy ID to human name [src/app/src/pages/eval/components/ResultsView.tsx:140-142]() |

**Sources:** [src/app/src/pages/eval/components/store.ts:145-172](), [src/app/src/pages/eval/components/ResultsView.tsx:84-145]()

### ResultsFilter Interface

The `ResultsFilter` structure in `store.ts` defines how a single filter criterion is represented.

```mermaid
classDiagram
    class ResultsFilter {
        +string id
        +string type
        +string value
        +string operator
        +string logicOperator
        +string field
    }
```

**Sources:** [src/app/src/pages/eval/components/store.ts:52-52]()

---

## Search Functionality

Search operates independently from structured filters and supports both plain text and regex patterns.

### Search Text Handling

`ResultsView` utilizes `useDebouncedCallback` to manage the `searchText` state, ensuring that the heavy `fetchEvalData` operation is only triggered after the user pauses typing.

```mermaid
sequenceDiagram
    participant User
    participant SearchInput["SearchInput (ResultsView.tsx)"]
    participant DebouncedUpdate["useDebouncedCallback (300ms)"]
    participant URLParams["URL ?search= param"]
    participant TableStore["useTableStore"]
    participant API["fetchEvalData()"]

    User->>SearchInput: Types character
    SearchInput->>DebouncedUpdate: Trigger callback
    Note over DebouncedUpdate: Wait 300ms
    DebouncedUpdate->>URLParams: setSearchParams
    DebouncedUpdate->>TableStore: fetchEvalData(id, {searchText})
    TableStore->>API: callApi(/results/:id/table)
```

**Sources:** [src/app/src/pages/eval/components/ResultsView.tsx:28-29](), [src/app/src/pages/eval/components/Eval.tsx:124-154]()

### Search Highlighting

When `shouldHighlightSearchText` is enabled in the `useTableStore`, the `EvalOutputCell` identifies match ranges in the output text and applies visual highlights using the `searchText` prop.

**Sources:** [src/app/src/pages/eval/components/EvalOutputCell.tsx:42-42](), [src/app/src/pages/eval/components/ResultsTable.test.tsx:70-77]()

---

## Filter State Management

Filters are managed in the `useTableStore` Zustand store. The store tracks the active filter values, the total count of applied filters, and available options extracted from the evaluation data.

### Store State Shape

| Property | Type | Description |
|----------|------|-------------|
| `filters.values` | `Record<string, ResultsFilter>` | Active filter objects keyed by UUID |
| `filters.appliedCount` | `number` | Count of filters with valid values |
| `filters.options` | `Record<string, string[]>` | Available metrics, metadata keys, etc. |

**Sources:** [src/app/src/pages/eval/components/store.ts:21-28](), [src/app/src/pages/eval/components/store.ts:55-73]()

### Filter Mode Provider

Beyond individual filters, the `FilterModeProvider` manages the overall view mode (`all`, `failures`, `passes`, `errors`, `highlights`). This mode is passed as a query parameter to the backend.

**Sources:** [src/app/src/pages/eval/components/FilterModeProvider.tsx](), [src/app/src/pages/eval/components/Eval.tsx:79-79]()

---

## Backend Query Construction

The backend translates frontend filter parameters into SQL WHERE clauses. This logic is encapsulated in `EvalQueries` within `models/eval.ts`.

### SQL Building Pipeline

The system uses `drizzle-orm` to construct safe parameterized queries. Dynamic JSON filtering is handled via SQLite's `json_extract`.

```mermaid
flowchart LR
    subgraph "Filter Construction (models/eval.ts)"
        Combine["combineFilterConditions()"]
        BuildPath["buildSafeJsonPath()"]
        EscapeKey["escapeJsonPathKey()"]
    end

    subgraph "Query Types"
        Vars["getVarsFromEvals()"]
        Meta["getMetadataKeysFromEval()"]
    end

    Combine --> SQL["sql`... AND condition`"]
    BuildPath --> SQL
    Vars --> SQL
    Meta --> SQL
```

**Sources:** [src/models/eval.ts:109-122](), [src/models/eval.ts:138-158](), [src/models/eval.ts:161-193]()

### Safe JSON Paths

To prevent SQL injection while allowing filtering on dynamic metadata keys, the system uses `buildSafeJsonPath` which escapes backslashes and double quotes before wrapping the key in a JSON path string (`$."key"`).

**Sources:** [src/models/eval.ts:109-122]()

---

## Red Team Filter Options

Red team evaluations expose additional filter types derived from the `UnifiedConfig`.

### Building Red Team Options

The store dynamically computes available severities, plugins, and strategies based on the `redteam` configuration in the evaluation results.

| Function | Logic |
|----------|-------|
| `computeAvailableSeverities` | Maps plugins to their risk category severities [src/app/src/pages/eval/components/store.ts:174-205]() |
| `buildPolicyOptions` | Extracts unique policy IDs from redteam plugin configs [src/app/src/pages/eval/components/store.ts:78-97]() |
| `extractUniqueStrategyIds` | Deduplicates strategies and filters out internal 'retry' [src/app/src/pages/eval/components/store.ts:129-135]() |

**Sources:** [src/app/src/pages/eval/components/store.ts:145-172](), [src/app/src/pages/eval/components/store.ts:174-205]()

---

## Performance and Pagination

For large evaluation sets, the system uses server-side pagination and debouncing to maintain UI performance.

1.  **Server-side Filtering**: Filters are applied at the database level during the `fetchEvalData` call, which supports pagination via `pageIndex` and `pageSize`.
2.  **Pagination Control**: The `ResultsTable` component provides a UI for selecting page sizes (10, 50, 100, 500, 1000) and navigating between pages.
3.  **Debouncing**: Search and filter updates are debounced (300ms) to prevent UI lag and excessive database load.

**Sources:** [src/app/src/pages/eval/components/store.ts:207-215](), [src/app/src/pages/eval/components/ResultsTable.tsx:80-82](), [src/app/src/pages/eval/components/ResultsView.tsx:28-29]()
This page defines key terms, jargon, abbreviations, and domain concepts used within the promptfoo codebase. It aims to provide an onboarding engineer with a comprehensive understanding of the terminology, including code pointers to relevant implementations.

## Evaluation Concepts

### Test Suite
A collection of prompts, providers, and test cases that define an evaluation run. It is typically configured via a `promptfooconfig.yaml` file. The `TestSuite` object is a core data structure representing this configuration.
Sources: [src/types/index.ts:75-75](), [src/evaluator.ts:75-75]()

### Prompt
A piece of text or a structured message sent to an LLM. In promptfoo, prompts can be defined directly in the configuration or loaded from external files. They often contain Nunjucks templating variables that are resolved during evaluation.
Sources: [src/types/index.ts:71-71](), [src/evaluator.ts:71-71]()

### Provider
An abstraction layer for interacting with Large Language Models (LLMs) or other API services. Providers encapsulate the logic for making API calls, handling authentication, and parsing responses. Examples include `OpenAiChatCompletionProvider` for OpenAI models and `HttpProvider` for generic HTTP endpoints.
Sources: [src/types/providers.ts:13-20](), [src/evaluator.ts:77-77](), [src/providers/http.ts:58-64]()

### Test Case
A specific input scenario used to evaluate a prompt and provider. A test case consists of input variables (`vars`), optional expected outputs (`assert`), and metadata.
Sources: [src/types/index.ts:64-64](), [src/evaluator.ts:64-64]()

### Assertion
A condition used to check the output of an LLM. Assertions can be deterministic (e.g., `contains`, `not-contains`) or model-graded (e.g., `matches-llm-rubric`, `matches-similarity`).
Sources: [src/types/index.ts:61-63](), [src/evaluator.ts:9-15]()

### Model-graded Assertion
An assertion type where another LLM (the "grader") is used to evaluate the output of the primary LLM. This allows for more nuanced and subjective evaluations. Examples include `matchesLlmRubric` and `matchesFactuality`.
Sources: [src/evaluator.ts:12-12](), [src/assertions/index.ts:1-15]()

### Eval
An instance of an evaluation run. The evaluation process is managed by the `Evaluator` class, which orchestrates the pipeline from prompt rendering to assertion execution.
Sources: [src/evaluator.ts:175-175](), [src/evaluator.ts:122-122]()

### EvalResult
The outcome of a single test case execution, including the LLM's output, assertions results, token usage, and any errors.
Sources: [src/types/index.ts:67-67](), [src/evaluator.ts:67-67]()

### Token Usage
Metrics tracking the number of tokens consumed by prompts and completions during an evaluation. This is crucial for cost estimation and performance analysis. The `TokenUsageTracker` class manages this.
Sources: [src/types/index.ts:7-7](), [src/evaluator.ts:102-102]()

### ProgressBarManager
A utility class responsible for displaying and updating the command-line progress bar during evaluation runs. It handles logging messages without disrupting the progress bar.
Sources: [src/evaluator.ts:175-179]()

### RateLimitRegistry
Manages rate limiting and concurrency for API calls to providers. It uses an Adaptive Increase/Multiplicative Decrease (AIMD) algorithm to dynamically adjust concurrency based on provider responses.
Sources: [src/evaluator.ts:37-39](), [src/types/index.ts:51-62]()

### Nunjucks Templating
A templating engine used to render prompts and other configuration elements. It allows for dynamic insertion of variables and execution of custom filters.
Sources: [src/evaluator.ts:21-21](), [src/providers/http.ts:35-35]()

## Red Team Terminology

### Red Team
The process of proactively identifying vulnerabilities and risks in LLM applications through adversarial testing.
Sources: [src/redteam/index.ts:1-10]()

### Plugin
A modular component in the red team system that generates adversarial test cases or evaluates LLM responses for specific vulnerabilities (e.g., PII leakage, harmful content). Plugins are referenced in the configuration and expanded during synthesis.
Sources: [src/redteam/types.ts:70-70](), [src/redteam/index.ts:42-42]()

### Strategy
A method or approach used to generate adversarial prompts or manipulate test cases. Strategies can involve techniques like jailbreaking, prompt injection, or multi-turn conversations.
Sources: [src/redteam/types.ts:71-71](), [src/redteam/index.ts:56-56]()

### Target
The LLM application or provider being red-teamed. In promptfoo, this often refers to a configured `ApiProvider`.
Sources: [src/redteam/index.ts:44-44]()

### Purpose
The intended function or goal of the LLM application being red-teamed. This context helps in generating more relevant adversarial tests.
Sources: [src/redteam/index.ts:39-39]()

### Context
Additional information or constraints provided to the red team system to guide test generation, such as user roles or system policies.
Sources: [src/redteam/index.ts:48-49]()

### Attack Provider
Specialized providers used in red teaming that implement iterative attack loops, memory systems, and backtracking to find vulnerabilities.
Sources: [src/redteam/providers/shared.ts:1-10](), [src/redteam/index.ts:44-44]()

### RedteamConfigSchema
The Zod schema defining the structure of the `redteam` section within `promptfooconfig.yaml`, which specifies plugins, strategies, and other red team settings.
Sources: [src/types/index.ts:19-19](), [src/validators/redteam.ts:1-10]()

### Severity
A classification of the impact or risk associated with a detected vulnerability, ranging from Low to Critical.
Sources: [src/redteam/index.ts:195-204](), [src/redteam/constants.ts:1-4]()

## Provider Abstractions

### ApiProvider
The core interface for any LLM or API service integration. It defines methods like `callApi` for making requests and `id` for identification.
Sources: [src/types/providers.ts:13-20](), [src/evaluator.ts:77-77]()

### HttpProvider
A generic provider that allows interaction with any HTTP API endpoint. It supports dynamic request construction using Nunjucks, various authentication methods, and response transformations.
Sources: [src/providers/http.ts:48-54](), [src/providers/http.ts:58-64]()

### ProviderOptions
A type defining the configuration options for an `ApiProvider`, including its ID, label, and specific configuration parameters.
Sources: [src/types/index.ts:41-41](), [src/types/providers.ts:1-12]()

### ProviderRegistry
A map that stores and manages available `ApiProvider` implementations, allowing them to be loaded by their string identifiers.
Sources: [src/providers/registry.ts:138-148](), [src/evaluator.ts:29-29]()

### `loadApiProvider()`
A function responsible for resolving a provider string or object into an `ApiProvider` instance, handling file-based configurations and cloud providers.
Sources: [src/providers/registry.ts:1-10](), [src/commands/eval.ts:45-47]()

### `maybeLoadConfigFromExternalFile()`
A utility function that recursively resolves `file://` references within a configuration object, loading content from external files.
Sources: [src/providers/http.ts:17-20]()

## Configuration Schema Terms

### `promptfooconfig.yaml`
The primary configuration file for promptfoo, typically located in the project root. It defines prompts, providers, test cases, and other evaluation settings.
Sources: [site/static/config-schema.json:7-73]()

### `UnifiedConfig`
A type representing the complete, merged configuration for a promptfoo run, combining settings from `promptfooconfig.yaml`, command-line options, and default values.
Sources: [src/types/index.ts:15-15](), [src/commands/eval.ts:20-20]()

### `CommandLineOptions`
A type representing the options that can be passed via the command line when running promptfoo. These options can override settings in the `promptfooconfig.yaml`.
Sources: [src/types/index.ts:99-152](), [src/commands/eval.ts:15-15]()

### `EvaluateOptions`
A type defining various settings that control the evaluation process, such as `maxConcurrency`, `repeat`, and `delay`.
Sources: [site/static/config-schema.json:61-63]()

### `RedteamFileConfig`
A type representing the configuration specifically for red teaming, typically found within the `redteam` section of `promptfooconfig.yaml`.
Sources: [src/types/index.ts:34-34](), [src/redteam/types.ts:65-72]()

### `NunjucksFilterMap`
A map of custom Nunjucks filters that can be used within prompts for data manipulation.
Sources: [src/types/index.ts:6-6](), [src/contracts/shared.ts:1-10]()

## Infrastructure Concepts

### CLI State (`cliState`)
A singleton object that holds global state relevant to the command-line interface, such as the current log file paths and post-action callbacks.
Sources: [src/cliState.ts:1-10](), [src/main.ts:2-2]()

### `main()`
The entry point for the promptfoo CLI application. It initializes the environment, loads configurations, registers commands using Commander.js, and handles global error logging.
Sources: [src/main.ts:53-148]()

### `shutdownGracefully()`
A function called during application shutdown to perform cleanup tasks, such as flushing OpenTelemetry traces and disposing of resources.
Sources: [src/mainUtils.ts:37-37](), [src/main.ts:37-38]()

### OpenTelemetry Tracing
An observability framework integrated into promptfoo to collect and export traces of LLM calls and evaluation steps, aiding in debugging and performance analysis.
Sources: [src/evaluator.ts:47-54]()

### `EvalRunError`
A custom error class used to signal a failure during an evaluation run, carrying an `exitCode` for CLI processes.
Sources: [src/main.ts:40-40]()

### `ConfigResolutionError`
An error type indicating a problem during the loading or merging of configuration files.
Sources: [src/main.ts:48-48](), [src/util/config/load.ts:1-10]()

### `runDbMigrations()`
Executes database schema migrations to ensure the local SQLite database is up-to-date.
Sources: [src/main.ts:64-64]()

### `mcpCommand`
The command for starting the Model Context Protocol (MCP) server, which exposes promptfoo tools to AI agents and development environments.
Sources: [src/main.ts:19-19]()

### `ProgressBarManager`
Title: ProgressBarManager Class Structure
```mermaid
classDiagram
    class ProgressBarManager {
        -SingleBar progressBar
        -boolean isWebUI
        -function originalLogCallback
        -function installedLogCallback
        +constructor(isWebUI: boolean)
        +start(total: number, concurrency: number)
        +increment()
        +stop()
    }
```
The `ProgressBarManager` class is responsible for managing the command-line progress bar during evaluation runs. It ensures that log messages do not interfere with the progress bar's display by clearing the line before logging and re-rendering afterward.
Sources: [src/evaluator.ts:175-220]()

### Evaluation Data Flow
Title: Evaluation Data Flow and Code Entities
```mermaid
graph TD
    A["promptfooconfig.yaml"] --> B["loadDefaultConfig()"]
    B --> C["TestSuite"]
    C --> D["loadApiProviders()"]
    D --> E["ApiProvider"]
    C --> F["renderPrompt()"]
    C --> G["AtomicTestCase"]
    E & F & G --> H["Evaluator.evaluate()"]
    H --> I["provider.callApi()"]
    I --> J["ProviderResponse"]
    J --> K["runAssertions()"]
    K --> L["GradingResult"]
    J --> M["TokenUsageTracker"]
    H --> N["EvalResult"]
    N --> O["SQLite DB"]
    subgraph "CLI"
        Q["evalCommand"] --> B
    end
```
This diagram illustrates the high-level data flow during an evaluation run. The process starts with configuration loading via `loadDefaultConfig`, proceeds through prompt rendering and test case generation, uses `ApiProvider` instances to make LLM calls, and finally processes responses through assertions and grading, persisting results in SQLite.
Sources: [src/evaluator.ts:21-21](), [src/evaluator.ts:75-77](), [src/evaluator.ts:102-102](), [src/main.ts:67-69](), [src/commands/eval.ts:18-32]()

### Red Team System Overview
Title: Red Team Architecture and Core Classes
```mermaid
graph TD
    A["RedteamConfigSchema"] --> B["RedteamFileConfig"]
    B --> C["Plugin Expansion"]
    B --> D["Strategy Expansion"]
    C --> E["RedteamPluginBase"]
    D --> F["Strategies"]
    E & F --> G["synthesize()"]
    G --> H["TestCase"]
    H --> I["Evaluator.evaluate()"]
    I --> J["RedteamIterativeProvider"]
    J --> K["Target (ApiProvider)"]
    K --> L["ProviderResponse"]
    L --> M["RedteamGraderBase"]
    M --> N["GradingResult"]
    subgraph "CLI Commands"
        O["redteamGenerateCommand"] --> G
        P["redteamRunCommand"] --> I
    end
```
This diagram outlines the architecture of the red team system. It starts with the `RedteamConfigSchema` to define red team settings, which are then expanded into plugins and strategy instances. The `synthesize()` function generates adversarial test cases, which are then fed into the evaluation engine. Iterative attack providers manage loops against the target LLM, and graders evaluate the responses for vulnerabilities.
Sources: [src/redteam/index.ts:42-56](), [src/redteam/types.ts:65-72](), [src/validators/redteam.ts:1-10](), [src/main.ts:131-132]()

### `HttpProvider` Request Flow
Title: HttpProvider Internal Logic
```mermaid
graph TD
    A["ProviderOptions"] --> B["HttpProvider.callApi()"]
    B --> C["renderVarsInObject()"]
    C --> D["Nunjucks Engine"]
    D --> E["Request Headers/Body"]
    E --> F["preprocessSignatureAuthConfig()"]
    F --> G["fetchWithCache()"]
    G --> H["HTTP Request"]
    H --> I["HTTP Response"]
    I --> J["createTransformResponse()"]
    J --> K["ProviderResponse"]
```
This diagram illustrates the internal request flow within the `HttpProvider`. User configuration is processed, variables are rendered using Nunjucks templating, and authentication settings are applied. The request is then made via `fetchWithCache()`, and the HTTP response undergoes transformation before being returned as a `ProviderResponse`.
Sources: [src/providers/http.ts:58-64](), [src/providers/http.ts:22-22](), [src/providers/http.ts:35-35](), [src/providers/http.ts:90-110](), [src/providers/http.ts:44-46]()
---
extraction_url: https://deepwiki.com/promptfoo/promptfoo
---
The promptfoo Model Context Protocol (MCP) server provides a standardized interface for AI agents and development environments to interact with promptfoo's evaluation and red-teaming toolset. By exposing core functionalities as MCP tools, agents can autonomously run evaluations, generate datasets, and perform security scans using either `stdio` or `HTTP` transport modes.

## Overview and Architecture

The MCP server is implemented as a CLI command (`mcpCommand`) that initializes a server instance capable of handling tool execution requests from MCP clients. It allows external LLM agents to treat promptfoo as a sophisticated tool for testing and securing other LLMs.

### Implementation Details
The server is registered in the main CLI entrypoint and defined in the MCP command module. It leverages the Model Context Protocol to manage tool definitions and transport. The system supports both client-side MCP integration (where promptfoo acts as a client to other servers) and server-side integration (where promptfoo provides tools to agents).

### Transport Modes
1.  **stdio**: The default mode for local integration where the agent (e.g., Claude Desktop or a local IDE) starts promptfoo as a subprocess and communicates via standard input/output [src/commands/mcp/server.ts:59-70]().
2.  **HTTP**: Used for remote or networked integrations where the agent connects to a persistent promptfoo MCP endpoint. The server implementation handles `WebStandardStreamableHTTPServerTransport` with session management [src/commands/mcp/server.ts:139-142]().

### Data Flow
When an MCP client invokes a tool:
1.  The request is received via the MCP server instance (`McpServer`) [src/commands/mcp/server.ts:76-82]().
2.  The server maps the tool name to a specific internal command handler registered via functions like `registerRunEvaluationTool` or `registerRedteamGenerateTool` [src/commands/mcp/server.ts:93-112]().
3.  The handler executes the logic, often involving the evaluation engine or redteam subsystems.
4.  Results are formatted and returned to the client as JSON.

### System Mapping: NL Space to Code Entity Space

The following diagram maps natural language tool requests to the specific code entities that handle them.

**MCP Tool Execution Mapping**
```mermaid
graph TD
    subgraph "NaturalLanguageRequest"
        A["'Run an evaluation'"]
        B["'Generate a redteam dataset'"]
        C["'Validate my config'"]
    end

    subgraph "MCPServerLayer"
        MCP["McpServer (src/commands/mcp/server.ts)"]
    end

    subgraph "CodeEntitySpace"
        EVAL["registerRunEvaluationTool (src/commands/mcp/tools/runEvaluation.ts)"]
        GEN["registerRedteamGenerateTool (src/commands/mcp/tools/redteamGenerate.ts)"]
        VAL["registerValidatePromptfooConfigTool (src/commands/mcp/tools/validatePromptfooConfig.ts)"]
        LOGS["registerLogTools (src/commands/mcp/tools/logs.ts)"]
    end

    A --> MCP
    B --> MCP
    C --> MCP

    MCP -- "runEvaluation" --> EVAL
    MCP -- "redteamGenerate" --> GEN
    MCP -- "validatePromptfooConfig" --> VAL
    MCP -- "logs" --> LOGS
```
Sources: [src/commands/mcp/server.ts:75-117](), [src/commands/mcp/server.ts:108-112]()

## Available Tools

The MCP server exposes a comprehensive suite of tools that mirror the CLI functionality. These tools allow agents to perform complex evaluation tasks without manually constructing CLI strings.

| Tool Name | Registration Function | Description |
| :--- | :--- | :--- |
| `runEvaluation` | `registerRunEvaluationTool` | Executes an evaluation based on a provided configuration [src/commands/mcp/server.ts:99](). |
| `generateDataset` | `registerGenerateDatasetTool` | Generates synthetic test cases from prompts or existing data [src/commands/mcp/server.ts:103](). |
| `redteamGenerate` | `registerRedteamGenerateTool` | Generates adversarial test cases for red-teaming [src/commands/mcp/server.ts:109](). |
| `redteamRun` | `registerRedteamRunTool` | Executes a red-team evaluation against a target [src/commands/mcp/server.ts:108](). |
| `testProvider` | `registerTestProviderTool` | Tests specific provider connectivity and session settings [src/commands/mcp/server.ts:97](). |
| `validatePromptfooConfig` | `registerValidatePromptfooConfigTool` | Validates configuration integrity and connectivity [src/commands/mcp/server.ts:96](). |
| `compareProviders` | `registerCompareProvidersTool` | Runs a quick comparison between two or more LLM providers [src/commands/mcp/server.ts:105](). |
| `shareEvaluation` | `registerShareEvaluationTool` | Generates a shareable URL for an evaluation result [src/commands/mcp/server.ts:100](). |
| `listEvaluations` | `registerListEvaluationsTool` | Lists historical evaluation runs from the local database [src/commands/mcp/server.ts:94](). |

Sources: [src/commands/mcp/server.ts:93-112]()

## Integration and Usage

### MCP Client and Server Roles
Promptfoo can act as both an MCP server (providing tools to agents) and an MCP client (consuming tools from other servers). The `MCPClient` class handles the client-side logic, allowing providers to use external tools during an evaluation [src/providers/mcp/client.ts:92-105]().

**Agent Evaluation Lifecycle**
```mermaid
sequenceDiagram
    participant Agent as "AI Agent (MCP Client)"
    participant MCP as "Promptfoo MCP Server"
    participant Tool as "Tool Handler (e.g. runEvaluation)"

    Agent->>MCP: Call "validatePromptfooConfig"
    MCP->>Tool: validatePromptfooConfig(config)
    Tool-->>MCP: {valid: true}
    MCP-->>Agent: Validation Success

    Agent->>MCP: Call "runEvaluation"
    MCP->>Tool: executeEval(params)
    Tool-->>MCP: EvalResults
    MCP-->>Agent: JSON Results + Table Summary
```
Sources: [src/commands/mcp/server.ts:93-100](), [src/providers/mcp/client.ts:146-153]()

### Key Classes

-   `MCPClient`: Manages connections to multiple MCP servers, handling initialization and transport [src/providers/mcp/client.ts:92-99]().
-   `McpServer`: The core class from the `@modelcontextprotocol/sdk` used to define the promptfoo server instance [src/commands/mcp/server.ts:76-77]().
-   `WebStandardStreamableHTTPServerTransport`: The transport layer used for HTTP/SSE communication [src/commands/mcp/server.ts:139-142]().

## Configuration

The MCP integration uses specific types to define server connectivity and authentication.

### MCP Configuration Types
-   `MCPServerConfig`: Defines a single server connection, including `path` for local files, `command`/`args` for stdio, or `url` for remote endpoints [src/providers/mcp/types.ts:5-13]().
-   `MCPConfig`: The top-level configuration object for enabling MCP on a provider, including `timeout`, `maxTotalTimeout`, and `pingOnConnect` [src/providers/mcp/types.ts:73-108]().
-   `MCPServerAuth`: Supports multiple authentication strategies: `bearer`, `basic`, `api_key`, and `oauth` (client credentials or password) [src/providers/mcp/types.ts:64-69]().

### Timeout Management
The system provides granular control over request timeouts:
-   `timeout`: Default 60s, configurable via `MCP_REQUEST_TIMEOUT_MS` [src/providers/mcp/client.ts:68]().
-   `resetTimeoutOnProgress`: Resets the timer when progress notifications are received [src/providers/mcp/types.ts:92]().
-   `maxTotalTimeout`: An absolute cap on execution time [src/providers/mcp/types.ts:98]().

Sources: [src/providers/mcp/types.ts:1-129](), [src/providers/mcp/client.ts:63-90]()
The Model Audit system in promptfoo provides static security scanning for Machine Learning (ML) models. It integrates the `modelaudit` engine to detect security vulnerabilities, malicious code, and backdoors across 30+ model formats before they are deployed into production.

## Overview and Purpose

ModelAudit acts as a security gate in the AI pipeline. It identifies risks such as:
*   **Malicious code execution:** Arbitrary code embedded in Python pickle files (`.pkl`, `.pt`, `.pth`).
*   **Suspicious Operations:** Dangerous TensorFlow or Keras operations (e.g., `PyFunc`, `Lambda` layers) that can access system resources.
*   **Embedded Payloads:** Hidden executables, network communication patterns (URLs, IPs), or hardcoded credentials.
*   **Tampering:** Mismatched file hashes or suspicious ZIP archive structures.

Sources: [site/docs/model-audit/index.md:21-53](), [site/docs/model-audit/scanners.md:41-58]()

## System Architecture

The Model Audit system is implemented as a wrapper around the `modelaudit` Python CLI. It bridges the Node.js/TypeScript environment of promptfoo with the Python-based scanning engine.

### Data Flow Diagram
This diagram illustrates the flow from a user command to the execution of the scanner and the persistence of results.

"Model Audit Data Flow"
```mermaid
graph TD
    User["User/CLI"] -- "promptfoo scan-model" --> CLI["modelScanCommand (src/commands/modelScan.ts)"]
    CLI -- "spawn()" --> PythonScanner["modelaudit CLI (Python)"]

    subgraph "Scanning Engine"
        PythonScanner --> Scanners["Scanner Registry"]
        Scanners --> Pickle["Pickle Scanner"]
        Scanners --> TF["TensorFlow Scanner"]
        Scanners --> Keras["Keras Scanner"]
    end

    PythonScanner -- "JSON Output" --> CLI
    CLI -- "ModelAudit.create()" --> DB[("SQLite (model_audits table)")]
    CLI -- "createShareableModelAuditUrl()" --> Cloud["promptfoo Cloud (Optional)"]

    WebUI["Web Interface (ModelAuditSetupPage)"] -- "POST /api/model-audit/scan" --> Express["modelAuditRouter (src/server/routes/modelAudit.ts)"]
    Express -- "spawnModelAuditCapture()" --> PythonScanner
```
Sources: [src/commands/modelScan.ts:1-25](), [src/server/routes/modelAudit.ts:40-89](), [src/types/modelAudit.ts:1-30]()

### Implementation Details

The core logic resides in `src/commands/modelScan.ts`, which handles argument parsing, environment validation, and process execution.

*   **Process Spawning:** The function `spawnModelAudit` [src/commands/modelScan.ts:216]() (referenced as `spawn` call within the command action) executes the underlying `modelaudit` command. It handles signal forwarding (e.g., `SIGINT`, `SIGTERM`) to ensure child processes are terminated when the user cancels a scan [src/commands/modelScan.ts:210-211]().
*   **Result Parsing:** The system uses `parseCompleteModelAuditResults` [src/util/modelAuditResults.ts:26]() to transform raw JSON output from the Python tool into the `ModelAuditScanResults` type.
*   **Exit Codes:** The wrapper maps `modelaudit` exit codes: `0` for clean, `1` for security findings, and `2+` for fatal errors [src/commands/modelScan.ts:125-132](). The helper `getProcessErrorExitCode` handles signal-based terminations [src/commands/modelScan.ts:133-143]().
*   **Update Checks:** The system verifies the installed version of `modelaudit` via `checkModelAuditUpdates` [src/updates.ts:87]() and `getModelAuditCurrentVersion` [src/updates.ts:76](), comparing it against PyPI [src/updates.ts:57]().

Sources: [src/commands/modelScan.ts:123-160](), [src/commands/modelScan.ts:210-211](), [src/updates.ts:57-115]()

## Supported Formats and Scanners

ModelAudit uses specialized scanners tailored to specific file formats. Users can discover available scanners via `promptfoo scan-model --list-scanners` [site/docs/model-audit/index.md:153]().

| Scanner | Supported Extensions | Key Checks |
| :--- | :--- | :--- |
| **Pickle** | `.pkl`, `.pt`, `.pth`, `.bin` | Dangerous opcodes, `os.system`, `eval`, `exec` |
| **TensorFlow** | `.pb`, SavedModel dirs | `PyFunc` ops, file I/O operations, Python calls in graph |
| **Keras** | `.h5`, `.keras` | Unsafe `Lambda` layers, base64 encoded Python code |
| **ONNX** | `.onnx` | External data references, path traversal, tensor integrity |
| **TensorRT** | `.engine`, `.plan` | Shared library references, unauthorized plugins |
| **TF Lite** | `.tflite` | Custom ops, Flex delegate execution, buffer validation |

Sources: [site/docs/model-audit/scanners.md:39-180]()

## Server Integration (API Routes)

The promptfoo web server exposes the Model Audit functionality via the `modelAuditRouter`.

### Key API Endpoints
*   `GET /api/model-audit/check-installed`: Verifies if the `modelaudit` Python package is available in the environment [src/server/routes/modelAudit.ts:92]().
*   `GET /api/model-audit/scanners`: Queries the Python engine for a list of available scanners by spawning `modelaudit` with `LIST_SCANNERS_ARGS` [src/server/routes/modelAudit.ts:109-123]().
*   `POST /api/model-audit/check-path`: Validates if a provided path exists and identifies it as a file or directory, handling home directory expansion [src/server/routes/modelAudit.ts:149-163]().
*   `POST /api/model-audit/scan`: The primary execution endpoint. It accepts `ScanRequestSchema`, resolves paths to absolute locations, and spawns the scanner via `spawnModelAuditCapture` [src/server/routes/modelAudit.ts:195-218]().

"Natural Language to Code: Server Routes"
```mermaid
graph LR
    subgraph "Natural Language Concepts"
        Verify["'Is scanner installed?'"]
        List["'What can I scan?'"]
        Run["'Scan this model'"]
    end

    subgraph "Code Entity Space (src/server/routes/modelAudit.ts)"
        Verify --> R1["GET /check-installed"]
        List --> R2["GET /scanners"]
        Run --> R3["POST /scan"]

        R1 --> F1["checkModelAuditInstalled()"]
        R2 --> F2["spawnModelAuditCapture(LIST_SCANNERS_ARGS)"]
        R3 --> F3["spawnModelAuditCapture(['scan', ...paths])"]
    end
```
Sources: [src/server/routes/modelAudit.ts:92-218](), [src/types/api/modelAudit.ts:8-121]()

## CLI Usage and Configuration

The `promptfoo scan-model` command supports various flags to customize the audit.

### Argument Parsing
The `parseModelAuditArgs` function [src/util/modelAuditCliParser.ts:142]() maps high-level promptfoo options to the specific CLI flags expected by the Python engine. It handles deprecated options by mapping them to environment variables where applicable [src/commands/modelScan.ts:181-205]().

| Option | CLI Flag | Description |
| :--- | :--- | :--- |
| `blacklist` | `--blacklist` | Additional patterns to check against model names |
| `maxSize` | `--max-size` | Maximum total size to scan (e.g., `1GB`) |
| `scanners` | `--scanners` | Specific scanners to run (e.g., `pickle,tf_savedmodel`) |
| `strict` | `--strict` | Fail on warnings and enable stricter validation |
| `sbom` | `--sbom` | Generate a Software Bill of Materials (CycloneDX) |
| `dryRun` | `--dry-run` | Preview scan without processing files |

Sources: [src/util/modelAuditCliParser.ts:121-137](), [src/commands/modelScan.ts:181-205](), [site/docs/model-audit/index.md:171-188]()

### Remote Scanning
ModelAudit supports scanning models from remote sources via URI schemes, authenticated exclusively via environment variables [site/docs/model-audit/usage.md:40]():
*   **HuggingFace:** `hf://org/model` (Uses `HF_TOKEN`) [site/docs/model-audit/usage.md:44-50]()
*   **Cloud Storage:** `s3://bucket/path` (`AWS_ACCESS_KEY_ID`), `gs://bucket/path` (`GOOGLE_APPLICATION_CREDENTIALS`), `r2://bucket/path` [site/docs/model-audit/usage.md:77-107]()
*   **Registries:** `models:/name/version` (MLflow) [site/docs/model-audit/usage.md:64-75]()
*   **JFrog Artifactory:** Authenticated via `JFROG_URL` and `JFROG_API_TOKEN` [site/docs/model-audit/usage.md:52-62]()

## Interpreting Scan Results

Scan results are structured as `ModelAuditScanResults` [src/types/modelAudit.ts:29]().

1.  **Summary Statistics:** `total_checks`, `passed_checks`, `failed_checks`, and `duration` (mapped from raw JSON output).
2.  **Issues:** An array of `ModelAuditIssue` objects containing `severity` (`critical`, `error`, `warning`, `info`, `debug`), `message`, and `location` [src/types/modelAudit.ts:29]().
3.  **Verdict:** The system determines a pass/fail verdict based on `hasFindings` via `getModelAuditVerdict` [src/commands/modelScan.ts:118-120]().
4.  **Metadata:** The command action captures revision information such as `modelId`, `revisionSha`, and `contentHash` to avoid redundant scans [src/commands/modelScan.ts:45-51]().

Sources: [src/commands/modelScan.ts:45-51](), [src/commands/modelScan.ts:118-120](), [src/types/modelAudit.ts:29]()
This page documents the model audit sharing subsystem: the `ModelAudit` data structure, how scan results are uploaded to the cloud, and the functions used to generate shareable URLs. It also compares the model audit sharing flow to the evaluation sharing flow documented in [Sharing System](7.1).

For documentation on cloud authentication, API key management, and the `CloudConfig` singleton, see [Cloud Configuration](7.2). For documentation on the `share` CLI command and how it dispatches between eval and model audit sharing, see [CLI Architecture](4.1).

---

## Overview

Model audit sharing lets users publish model scan results (produced by `promptfoo scan-model`) to a cloud-hosted viewer and obtain a shareable URL. The implementation lives primarily in `src/share.ts` and `src/commands/share.ts`.

Unlike evaluation sharing, which uses a chunked multi-request upload to handle large result sets, model audit sharing is a single synchronous POST. It targets a distinct API endpoint and URL path specialized for security scan reports.

Sources: [src/share.ts:722-795](), [src/commands/share.ts:40-53]()

---

## The `ModelAudit` Data Structure

The `ModelAudit` data model represents the results of a static security scan. When shared, the following fields are serialized and sent to the cloud:

| Field | Description |
|---|---|
| `id` | Unique scan identifier; typically prefixed with `scan-` |
| `name` | Human-readable name for the scan |
| `author` | The user who initiated the scan, resolved via `getAuthor()` |
| `modelId` | Identifier for the model being scanned |
| `modelSource` | Source of the model (e.g., `hf://`, `s3://`, `models:/`) |
| `results` | The `ModelAuditScanResults` object containing check aggregates |
| `checks` | Detailed array of individual scanner results |
| `issues` | Array of `ModelAuditIssue` objects identified during the scan |
| `metadata` | Arbitrary key-value metadata associated with the scan |
| `revisionSha` | Git revision or content SHA used for deduplication |
| `scannerVersion` | Version of the `modelaudit` Python package used |
| `createdAt` | ISO timestamp of scan creation |

Sources: [src/share.ts:743-766](), [src/commands/modelScan.ts:16-16](), [src/types/modelAudit.ts:29-81]()

---

## Enabling Model Audit Sharing

The function `isModelAuditSharingEnabled()` determines whether the environment is configured to support sharing scan results.

**Decision logic:**
1. If `PROMPTFOO_SHARE_API_BASE_URL` is set and does not point to the default `api.promptfoo.app`, sharing is enabled (Self-hosted mode).
2. If `cloudConfig.isEnabled()` is true (meaning a valid API key is present), sharing is enabled (Cloud mode).
3. Otherwise, sharing is disabled.

Note: Model audits cannot be shared to the public `api.promptfoo.app` without authentication, as they often contain sensitive infrastructure or model path information.

Sources: [src/share.ts:75-89]()

---

## Upload Flow

The diagram below maps the upload sequence from the CLI command to the cloud API.

**Model Audit Upload Sequence**

```mermaid
sequenceDiagram
    participant CLI as "CLI shareCommand (src/commands/share.ts)"
    participant Check as "isModelAuditSharingEnabled() (src/share.ts)"
    participant Idemp as "hasModelAuditBeenShared() (src/share.ts)"
    participant Upload as "createShareableModelAuditUrl() (src/share.ts)"
    participant Cloud as "Cloud API (/api/v1/model-audits)"

    CLI->>Check: Verify sharing configuration
    Check-->>CLI: true/false
    CLI->>Idemp: GET /api/v1/model-audits/:id
    Idemp-->>CLI: 200 (Exists) / 404 (New)
    Note over CLI,Idemp: If 200, prompt user to overwrite
    CLI->>Upload: auditRecord, showAuth
    Upload->>Cloud: POST /share (JSON payload)
    Cloud-->>Upload: { "id": "remote-id" }
    Upload-->>CLI: Final URL
```

Sources: [src/share.ts:722-816](), [src/commands/share.ts:208-244](), [src/util/cloud.ts:27-44]()

---

## Key Functions and Entities

The following diagram bridges the natural language concepts of "Sharing" to the specific code entities in the `promptfoo` codebase.

**Code Entity Mapping**

```mermaid
flowchart TD
    subgraph "NaturalLanguageSpace"
        UserAction["User runs 'promptfoo share'"]
        Logic["Sharing Logic"]
        Network["Network Request"]
    end

    subgraph "CodeEntitySpace"
        shareCmd["shareCommand() in src/commands/share.ts"]
        createUrl["createShareableModelAuditUrl() in src/share.ts"]
        isShared["hasModelAuditBeenShared() in src/share.ts"]
        makeReq["makeRequest() in src/util/cloud.ts"]
        fetchProxy["fetchWithProxy() in src/util/fetch/index.ts"]
        ModelAudit["ModelAudit Class in src/models/modelAudit.ts"]
    end

    UserAction --> shareCmd
    shareCmd --> ModelAudit
    shareCmd --> isShared
    isShared --> makeReq
    shareCmd --> createUrl
    createUrl --> fetchProxy
```

Sources: [src/share.ts:722-816](), [src/commands/share.ts:55-134](), [src/util/cloud.ts:27-30]()

### `isModelAuditSharingEnabled()`
[src/share.ts:75-89]()
Validates environment variables and `cloudConfig` state to ensure the scan can be sent to a remote endpoint.

### `hasModelAuditBeenShared(audit)`
[src/share.ts:694-714]()
Checks if a scan with the given ID already exists on the remote server using `makeRequest('model-audits/:id', 'GET')`. This prevents accidental duplication.

### `createShareableModelAuditUrl(auditRecord, showAuth?)`
[src/share.ts:722-795]()
The primary implementation for uploading scans. It:
1. Determines the target API URL via `getShareApiBaseUrl()`.
2. Sets the `Authorization` header if `cloudConfig` is enabled.
3. POSTs the serialized `auditRecord` to the `/share` endpoint.
4. Returns the public URL constructed via `getShareableModelAuditUrl()`.

### `getShareableModelAuditUrl(audit, remoteAuditId, showAuth?)`
[src/share.ts:804-816]()
Constructs the final user-facing URL. It uses `determineShareDomain` to find the correct application host and appends `/model-audit/{remoteAuditId}`.

---

## Comparison: Model Audit vs. Evaluation Sharing

While both share a common infrastructure in `src/share.ts`, their implementations differ to accommodate the data volume and structure.

| Feature | Model Audit Sharing | Evaluation Sharing |
|---|---|---|
| **Code Entrypoint** | `createShareableModelAuditUrl()` | `createShareableUrl()` |
| **Data Flow** | Single atomic POST | Chunked multi-POST with retry |
| **API Path** | `/api/v1/model-audits/share` | `/api/eval` |
| **URL Pattern** | `.../model-audit/{id}` | `.../eval/{id}` |
| **Idempotency** | Checks for scan ID existence | Checks for eval ID + Team ID |
| **Rollback** | Not supported | `rollbackEval()` on failure |
| **Traces** | Not included | Uploaded via `getTraces()` |

Sources: [src/share.ts:137-211](), [src/share.ts:722-795](), [src/commands/share.ts:136-205]()

---

## CLI Integration and ID Routing

The `share` command in `src/commands/share.ts` acts as a router. If an ID is provided, it checks the prefix to determine whether to load a `ModelAudit` or an `Eval`.

**ID Routing Logic**
- If ID starts with `scan-`: Load via `ModelAudit.findById(id)` [src/commands/share.ts:87-93]().
- Otherwise: Load via `Eval.findById(id)` [src/commands/share.ts:96-102]().
- If no ID: Compare `latest()` timestamps of both types and share the most recent [src/commands/share.ts:106-126]().

Once identified as a model audit, the CLI dispatches to `createAndDisplayShareableModelAuditUrl`, which handles the high-level logging and error reporting for the user.

Sources: [src/commands/share.ts:40-53](), [src/commands/share.ts:85-134](), [src/commands/share.ts:208-244]()
This page documents the OpenAI provider implementation in promptfoo, including the core provider classes, supported model families (GPT-4.x, GPT-5.x, o-series), configuration for reasoning effort, tool/function calling, structured outputs, and cost calculation.

For provider loading and string-to-class resolution, see page [3.1](). For Azure OpenAI, see page [3.8]().

---

## Provider Classes

The OpenAI integration is implemented through specialized provider classes that inherit from `OpenAiGenericProvider`.

**Provider Class Hierarchy:**

```mermaid
classDiagram
    class "OpenAiGenericProvider" {
        +modelName: string
        +options: ProviderOptions
        +getApiKey() string
        +getApiUrl() string
    }
    class "OpenAiChatCompletionProvider" {
        +config: OpenAiCompletionOptions
        +mcpClient: MCPClient
        +callApi(prompt) ProviderResponse
        +getOpenAiBody(prompt, context)
        +validateFunctionToolCall()
    }
    class "OpenAiResponsesProvider" {
        +config: OpenAiCompletionOptions
        +callApi(prompt) ProviderResponse
        +getOpenAiBody(prompt, context)
    }
    class "OpenAiAssistantProvider" {
        +callApi(prompt) ProviderResponse
    }
    "OpenAiGenericProvider" <|-- "OpenAiChatCompletionProvider"
    "OpenAiGenericProvider" <|-- "OpenAiResponsesProvider"
    "OpenAiGenericProvider" <|-- "OpenAiAssistantProvider"
```

- **`OpenAiChatCompletionProvider`**: Interfaces with the `/v1/chat/completions` endpoint. It handles chat messages, tool calling, and local function execution. [src/providers/openai/chat.ts:92-115]()
- **`OpenAiResponsesProvider`**: Interfaces with the newer `/responses` API. It supports background execution and advanced reasoning configurations. [src/providers/openai/responses.ts:35-145]()
- **`OpenAiGenericProvider`**: Provides shared utilities for API key retrieval, URL construction, and environment variable overrides. [src/providers/openai/index.ts:18-20]()

Sources: [src/providers/openai/chat.ts:92-115](), [src/providers/openai/responses.ts:35-145](), [src/providers/openai/index.ts:18-20]()

---

## Supported Models and Routing

Promptfoo uses a routing system to map model strings to specific endpoints.

| Prefix | Endpoint | Class |
| :--- | :--- | :--- |
| `openai:chat:<model>` | `/v1/chat/completions` | `OpenAiChatCompletionProvider` |
| `openai:responses:<model>` | `/responses` | `OpenAiResponsesProvider` |
| `openai:assistant:<id>` | Assistants API | `OpenAiAssistantProvider` |
| `openai:embedding:<model>` | `/v1/embeddings` | `OpenAiEmbeddingProvider` |
| `openai:tts:<model>` | `/v1/audio/speech` | `OpenAiAudioProvider` |
| `openai:video:<model>` | Sora Video API | `OpenAiVideoProvider` |

### Model Families
The toolkit defines metadata and costs for several model families in `OPENAI_CHAT_MODELS`:
- **GPT-4.1 Series**: `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano`. [src/providers/openai/util.ts:133-153]()
- **Reasoning (o-series)**: `o1`, `o1-mini`, `o3`, `o3-mini`. [src/providers/openai/util.ts:154-182]()
- **GPT-5 Series**: `gpt-5-search-api`, and various GPT-5 aliases. [src/providers/openai/util.ts:110-116]()
- **Specialized**: `chat-latest` and search-preview models. [src/providers/openai/util.ts:96-132]()

Sources: [site/docs/providers/openai.md:17-41](), [src/providers/openai/util.ts:77-235]()

---

## Configuration and Reasoning

### Reasoning Effort
For o-series and GPT-5 models, users can configure `reasoning_effort`.
- **o-series**: Supports `low`, `medium`, `high`. [src/providers/openai/types.ts:68-72]()
- **GPT-5**: Supports `none`, `minimal`, `low`, `medium`, `high`, `xhigh`, `max`. [src/providers/openai/types.ts:89-93]()

### Structured Outputs
The `response_format` option supports `json_schema` for strict schema enforcement. [src/providers/openai/types.ts:153-165]()

```yaml
providers:
  - id: openai:chat:gpt-4o
    config:
      response_format:
        type: json_schema
        json_schema:
          name: "research_paper"
          strict: true
          schema:
            type: object
            properties:
              title: { type: string }
              authors: { type: array, items: { type: string } }
            required: [title, authors]
            additionalProperties: false
```

Sources: [src/providers/openai/types.ts:53-93](), [src/providers/openai/types.ts:149-165]()

---

## Tool and Function Calling

Promptfoo implements a complex flow for tool calling, including support for Model Context Protocol (MCP) and local callbacks.

**Tool Execution Data Flow:**

```mermaid
flowchart TD
    subgraph "Natural Language Space"
        UserPrompt["User Prompt (Nunjucks)"]
    end

    subgraph "Code Entity Space"
        ChatProvider["OpenAiChatCompletionProvider.callApi()"]
        ToolLoader["maybeLoadToolsFromExternalFile()"]
        MCP["MCPClient.initialize()"]
        CallbackHandler["executeProviderFunctionCallback()"]
    end

    UserPrompt --> ChatProvider
    ToolLoader --> ChatProvider
    MCP -- "transformMCPToolsToOpenAi" --> ChatProvider
    ChatProvider -- "POST /v1/chat/completions" --> OpenAI["OpenAI API"]
    OpenAI -- "Returns tool_calls" --> ChatProvider
    ChatProvider -- "Check functionToolCallbacks" --> CallbackHandler
    CallbackHandler -- "Run local JS/Python" --> ChatProvider
    ChatProvider -- "Recursive call with tool results" --> OpenAI
```

- **MCP Integration**: `OpenAiChatCompletionProvider` can initialize an `mcpClient` to fetch tools from external MCP servers. [src/providers/openai/chat.ts:121-124]()
- **Function Callbacks**: `functionToolCallbacks` allow mapping tool names to local JavaScript functions or file references (`file://...`). [src/providers/openai/chat.ts:146-159]()

Sources: [src/providers/openai/chat.ts:98-100](), [src/providers/openai/chat.ts:121-124](), [src/providers/openai/chat.ts:146-159]()

---

## Token Usage and Cost Calculation

Promptfoo calculates costs based on the specific model and the tokens returned in the API response.

### Cost Calculation Logic
The `calculateOpenAIUsageCost` function uses model-specific rates for input, output, and audio tokens.
- **Search Surcharges**: Certain models like `gpt-5-search-api` incur a flat surcharge ($0.01 - $0.025) per request. [src/providers/openai/chat.ts:82-90]()
- **Audio Costs**: Supported for models like `gpt-4o-mini-tts`. [src/providers/openai/util.ts:77-87]()

### Token Usage Extraction
The `getTokenUsage` function parses the `usage` object from OpenAI's response, extracting:
- `total_tokens`, `prompt_tokens`, `completion_tokens`. [src/providers/openai/util.ts:35]()
- `completion_tokens_details`: `reasoning_tokens`, `accepted_prediction_tokens`. [test/providers/openai/util.test.ts:93-119]()
- `prompt_tokens_details`: `cached_tokens` (cache hits) and `cache_write_tokens`. [test/providers/openai/util.test.ts:121-145]()

Sources: [src/providers/openai/chat.ts:82-90](), [src/providers/openai/util.ts:31-38](), [test/providers/openai/util.test.ts:93-145]()

---

## Tracing

All OpenAI provider calls are wrapped with OpenTelemetry tracing using `withGenAISpan`.
- **Span Attributes**: Records `gen_ai.model_name`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, and OpenAI-specific attributes like `openai.api.type`. [test/providers/openai/chat.test.ts:119-168]()
- **Context**: `buildChatSpanContext` is used to maintain trace continuity across turns. [src/providers/openai/responses.ts:29]()

Sources: [test/providers/openai/chat.test.ts:119-168](), [src/providers/openai/responses.ts:29]()

# Google and Vertex Integration




This page documents promptfoo's integration with Google's LLM platforms: **Google AI Studio** (via the `google:` prefix) and **Google Cloud Vertex AI** (via the `vertex:` prefix). It covers the provider class hierarchy, supported models, authentication mechanisms, safety and guardrail features, function calling, multimodal input handling, and cost calculation.

For general information on how providers are loaded and registered in the system, see [Provider Loading and Registry](#3.1). For the Anthropic provider that is also available through Vertex AI, see [Anthropic Provider](#3.4).

---

## Architecture Overview

The Google integration is organized under `src/providers/google/` and consists of several discrete classes and a shared utility layer.

**Class hierarchy and file layout:**

```mermaid
graph TD
    subgraph "Provider Classes"
        GGP["GoogleGenericProvider\n(src/providers/google/base.ts)"]
        AISC["AIStudioChatProvider\n(src/providers/google/ai.studio.ts)"]
        VCP["VertexChatProvider\n(src/providers/google/vertex.ts)"]
        GP["GoogleProvider\n(src/providers/google/provider.ts)"]
        GLP["GoogleLiveProvider\n(src/providers/google/live.ts)"]
    end

    subgraph "Support Modules"
        UTIL["util.ts\nmaybeCoerceToGeminiFormat\ngeminiFormatAndSystemInstructions\ncalculateGoogleCost\nnormalizeSafetySettings\nnormalizeTools\nvalidateFunctionCall"]
        AUTH["auth.ts\nGoogleAuthManager\ngetGoogleClient\nloadCredentials\nresolveProjectId"]
        TYPES["types.ts\nCompletionOptions\nGoogleProviderConfig\nModelArmorConfig\nTool / Schema / Part"]
        SHARED["shared.ts\nGOOGLE_MODELS\nCHAT_MODELS"]
    end

    GGP --> AISC
    GGP --> VCP
    GGP --> GP
    AISC --> UTIL
    VCP --> UTIL
    GP --> UTIL
    GLP --> UTIL
    UTIL --> AUTH
    AISC --> SHARED
    VCP --> TYPES
    GP --> TYPES
```

Sources: [src/providers/google/vertex.ts:161-168](), [src/providers/google/ai.studio.ts:54-64](), [src/providers/google/live.ts:109-117](), [src/providers/google/util.ts:1-48](), [src/providers/google/types.ts:1-65](), [src/providers/google/shared.ts:1-25]()

---

## Provider Classes

### `AIStudioChatProvider`

Defined in `src/providers/google/ai.studio.ts`, this provider handles Google AI Studio (Gemini API). It extends `GoogleGenericProvider` and forces `vertexai: false` in its config [src/providers/google/ai.studio.ts:62]().

Key methods:

| Method | Description |
|--------|-------------|
| `id()` | Returns `google:<modelName>` |
| `getApiEndpoint(action?)` | Builds AI Studio URL using `getApiBaseUrl` and `getApiVersion` [src/providers/google/ai.studio.ts:72-77]() |
| `getApiVersion()` | Returns `v1alpha` for `gemini-2.0-flash-thinking-exp`, else `v1beta` [src/providers/google/ai.studio.ts:88-96]() |
| `getApiHost()` | Reads `config.apiHost`, `GOOGLE_API_HOST`, or `PALM_API_HOST` [src/providers/google/ai.studio.ts:102-111]() |
| `getApiKey()` | Priority: `config.apiKey` > `GOOGLE_API_KEY` > `GEMINI_API_KEY` [src/providers/google/ai.studio.ts:118-125]() |
| `getAuthHeaders()` | Returns headers with `x-goog-api-key` set [src/providers/google/ai.studio.ts:151-163]() |
| `callApi(prompt, context)` | Routes to `callGemini` or legacy PaLM path [src/providers/google/ai.studio.ts:168-217]() |

Sources: [src/providers/google/ai.studio.ts:54-217]()

---

### `VertexChatProvider`

Defined in `src/providers/google/vertex.ts`, this provider handles Vertex AI. It extends `GoogleGenericProvider` and forces `vertexai: true` [src/providers/google/vertex.ts:161-167]().

Key methods:

| Method | Description |
|--------|-------------|
| `getApiHost()` | Returns `{region}-aiplatform.googleapis.com` or `aiplatform.googleapis.com` for `global` [src/providers/google/vertex.ts:174-182]() |
| `getApiVersion()` | Reads `config.apiVersion` or defaults to `v1` [src/providers/google/vertex.ts:187-194]() |
| `getPublisher()` | Reads `config.publisher` or defaults to `google` [src/providers/google/vertex.ts:199-206]() |
| `getAuthHeaders()` | In express mode, adds `x-goog-api-key`; in OAuth mode, returns `Content-Type` [src/providers/google/vertex.ts:223-224]() |
| `getApiEndpoint(action?)` | Constructs the model-specific endpoint URL [src/providers/google/vertex.ts:212-216]() |

Sources: [src/providers/google/vertex.ts:161-224]()

---

### `GoogleLiveProvider`

Defined in `src/providers/google/live.ts`, this provider implements the Gemini Live API over a WebSocket connection for real-time, multi-turn interactions.

Key behaviors:
- `id()` returns `google:live:${this.modelName}` [src/providers/google/live.ts:123-125]().
- Connects via `ws://` WebSocket to the Live API endpoint.
- `getApiKey()` aligns priority with Python SDK: `GOOGLE_API_KEY` > `GEMINI_API_KEY` [src/providers/google/live.ts:161-164]().
- Supports `getAccessToken()` for OAuth2 authentication via `google-auth-library` [src/providers/google/live.ts:174-177]().

Sources: [src/providers/google/live.ts:109-177]()

---

## Request Flow

**Vertex AI Gemini call flow:**

```mermaid
sequenceDiagram
    participant E as "Evaluator.evaluate"
    participant V as "VertexChatProvider.callApi"
    participant U as "geminiFormatAndSystemInstructions (util.ts)"
    participant C as "getCache / isCacheEnabled"
    participant A as "getGoogleClient (auth.ts)"
    participant API as "Vertex AI REST API"

    E->>V: "callApi(prompt, context)"
    V->>V: "withGenAISpan(spanContext)"
    V->>U: "format prompt to GeminiFormat"
    U-->>V: "{ contents, systemInstruction }"
    V->>C: "cache.get(cacheKey)"
    alt "cache hit"
        C-->>V: "cachedResponse"
    else "cache miss"
        alt "express mode (API key)"
            V->>API: "fetchWithProxy POST /publishers/google/models/{model}:generateContent"
        else "OAuth mode"
            V->>A: "getGoogleClient(credentials)"
            A-->>V: "{ client, projectId }"
            V->>API: "client.request POST /projects/{id}/locations/{region}/publishers/google/models/{model}:generateContent"
        end
        API-->>V: "GeminiApiResponse[]"
        V->>C: "cache.set(cacheKey, response)"
    end
    V-->>E: "ProviderResponse"
```

Sources: [src/providers/google/vertex.ts:1-224](), [src/providers/google/util.ts:32-48](), [src/providers/google/auth.ts:20-38]()

---

## Supported Models

### Gemini (Google AI Studio — `google:` prefix)

| Model | Notes |
|-------|-------|
| `google:gemini-3.7-flash` | Latest Gemini Flash model for coding and agentic workflows |
| `google:gemini-3.5-flash` | Frontier Flash model |
| `google:gemini-3.1-pro-preview` | Tiered pricing above 200K tokens |
| `google:gemini-2.5-pro` | 1M context, enhanced reasoning |
| `google:gemini-2.0-flash-thinking-exp` | Reasoning with thinking process |

Sources: [site/docs/providers/google.md:140-143](), [site/docs/providers/vertex.md:21-36]()

### Gemini (Vertex AI — `vertex:` prefix)

| Model | Notes |
|-------|-------|
| `vertex:gemini-3.7-flash` | Latest Flash model; use `config.region: global` [site/docs/providers/vertex.md:21-32]() |
| `vertex:gemini-3.5-flash` | Frontier Flash model for agentic tasks [site/docs/providers/vertex.md:29]() |
| `vertex:gemini-3.1-pro-preview` | Improved reasoning and performance [site/docs/providers/vertex.md:45]() |

Sources: [site/docs/providers/vertex.md:19-57]()

### Claude and Llama (Vertex AI only)

Vertex AI also hosts third-party models:
- **Claude:** Supports Claude 5, 4.8, 4.7, 4.6, and 4.5 families [site/docs/providers/vertex.md:59-122](). Note that Claude 5 models require provider data sharing enabled via Google Cloud CLI [site/docs/providers/vertex.md:77-87]().
- **Claude 4.8/5 Pricing:** Vertex applies a 10% price premium for regional endpoints over the global endpoint [site/docs/providers/vertex.md:71-76]().

---

## Authentication

### Google AI Studio (`google:` prefix)

Authentication is via API key. Key lookup order in `AIStudioChatProvider`:
1. `config.apiKey`
2. `env.GOOGLE_API_KEY`
3. `env.GEMINI_API_KEY`
4. `env.PALM_API_KEY`

The key is passed via the `x-goog-api-key` HTTP header [src/providers/google/ai.studio.ts:151-163]().

### Vertex AI (`vertex:` prefix)

Vertex AI supports **Express Mode** (API Key) and **OAuth/ADC Mode**.
- **Express Mode:** Triggered if an API key is found. The key is passed via `x-goog-api-key` [src/providers/google/vertex.ts:223-224]().
- **OAuth Mode:** Uses `google-auth-library`. Configured via `credentials` (JSON string or `file://` path), `keyFilename`, or `googleAuthOptions` [src/providers/google/util.ts:37-38]().

---

## Safety Settings and Model Armor

### Safety Settings
Safety settings are normalized via `normalizeSafetySettings` [src/providers/google/util.ts:32-42](). It maps legacy `probability` to the standard `threshold` field.

```yaml
providers:
  - id: vertex:gemini-2.5-pro
    config:
      safetySettings:
        - category: HARM_CATEGORY_HARASSMENT
          threshold: BLOCK_MEDIUM_AND_ABOVE
```

### Model Armor (Vertex AI Only)
Model Armor screens prompts and responses for safety and compliance. Configured via `ModelArmorConfig` in `GoogleProviderConfig`.

| Field | Description |
|-------|-------------|
| `promptTemplate` | Resource path for screening prompts |
| `responseTemplate` | Resource path for screening responses |

Sources: [src/providers/google/util.ts:32-42](), [src/providers/google/vertex.ts:51-65]()

---

## Function Calling and Tools

### Tool Configuration
Tools are specified in `config.tools` or `config.tool_config`. The system normalizes these via `resolveGoogleToolConfig` [src/providers/google/util.ts:113-148]().

- **Modes:** `AUTO`, `ANY`, `NONE`, `VALIDATED` [src/providers/google/util.ts:53-64]().
- **Explicit Config:** Supports both camelCase (`toolConfig`) and snake_case (`tool_config`) [src/providers/google/util.ts:70-108]().

### Validation
Function calls are validated against declared schemas using `validateFunctionCall`. It supports both standard Gemini and Live API response formats (e.g., `toolCall` vs `functionCall`) [test/providers/google/util.test.ts:207-227]().

Sources: [src/providers/google/util.ts:113-148](), [test/providers/google/util.test.ts:157-227]()

---

## Multimodal and Structured Output

### Multimodal Inputs
- **Images/Video:** Handled via `Part` objects. The system supports `inlineData` for base64 encoded content and `fileData` for URI-based content [src/providers/google/util.ts:26]().
- **Audio:** Gemini 3.1 Flash-Lite and Gemini 3.0 support audio input [site/docs/providers/vertex.md:47-51]().

### Structured Output
Controlled via `response_mime_type: 'application/json'` in `generationConfig`. The system allows providing a `response_schema` to enforce specific JSON structures [src/providers/google/util.ts:34-35]().

---

## Cost Calculation

The `calculateGoogleCostFromUsage` function handles pricing based on model metadata [src/providers/google/util.ts:32]().
- **Claude Regional Premium:** Vertex AI Claude models (Sonnet 4.5+, Claude 5) incur a 10% premium if not using the `global` region [site/docs/providers/vertex.md:71-76]().
- **Sonnet 4.5 Long Context:** Vertex AI Sonnet 4.5 has a specific pricing tier for requests exceeding 200,000 tokens [src/providers/google/vertex.ts:79-88]().
- **Custom Costs:** Users can override via `config.inputCost` and `config.outputCost` [src/providers/google/vertex.ts:112-115]().

Sources: [src/providers/google/vertex.ts:79-116](), [src/providers/google/util.ts:32](), [site/docs/providers/vertex.md:71-76]()
Promptfoo integrates with OpenTelemetry (OTLP) to provide deep visibility into LLM provider execution flows, performance bottlenecks, and resource usage during evaluations. This system allows Promptfoo to act as both a producer of traces (instrumenting its own provider calls) and an OTLP receiver (ingesting traces from external services).

## System Architecture

The tracing subsystem consists of an OTLP receiver for ingestion, a local storage layer using SQLite, and instrumentation logic that wraps provider calls.

### Data Flow and Code Entity Mapping

The following diagram illustrates how natural language tracing concepts map to specific code entities and the flow of trace data.

**Tracing Component Map**
```mermaid
graph TD
    subgraph "Natural Language Space"
        A["User Config"]
        B["LLM Provider Call"]
        C["External Trace"]
        D["Trace Visualization"]
    end

    subgraph "Code Entity Space"
        E["OtelConfig"]
        F["withGenAISpan()"]
        G["OTLPReceiver"]
        H["TraceStore"]
        I["SQLite (spans table)"]
    end

    A -->|"defines"| E
    B -->|"instrumented by"| F
    C -->|"ingested by"| G
    G -->|"persisted via"| H
    H -->|"stored in"| I
    I -->|"rendered in"| D

```
Sources: [src/tracing/otlpReceiver.ts:189-202](), [src/tracing/genaiTracer.ts:8-9](), [src/tracing/store.ts:148-157]()

## OTLP Receiver

Promptfoo includes a built-in OTLP receiver that allows the CLI and server to ingest traces directly from instrumented applications (e.g., Vercel AI SDK, LangChain, or custom SDKs) without requiring a separate OpenTelemetry Collector.

### Receiver Implementation
The OTLP receiver is managed through the evaluation lifecycle to ensure it is running when needed.
- **Lifecycle Management**: `startOtlpReceiverIfNeeded` checks the `TestSuite` configuration and environment variables to initialize the receiver [src/tracing/evaluatorTracing.ts:140-155]().
- **Configuration**: The receiver defaults to `127.0.0.1:4318` and supports both `json` and `protobuf` formats [src/tracing/evaluatorTracing.ts:187-202]().
- **Active State**: The `CliState` maintains a reference to the `activeOtlpReceiver`, providing host and port information to the rest of the system [src/cliState.ts:7-11](), [src/cliState.ts:99-101]().

### Local Storage and Persistence
Traces are persisted to the local SQLite database via the `TraceStore`.
- **Database Schema**: Spans are stored in the `spansTable` and grouped by `traceId` in the `tracesTable` [src/database/tables.ts:1-10]().
- **`addSpans()`**: Ingested spans are processed, optionally sanitized, and inserted into the database [src/tracing/store.ts:184-218]().
- **Sanitization**: The system can redact sensitive information from attributes using `sanitizeTraceAttributes` [src/tracing/store.ts:62-66]().

Sources: [src/tracing/evaluatorTracing.ts:140-202](), [src/tracing/store.ts:148-218](), [src/cliState.ts:7-112]()

## Provider Instrumentation

Promptfoo automatically instruments built-in providers using GenAI Semantic Conventions.

### `genaiTracer` and `withGenAISpan()`
Provider calls are wrapped in spans that capture standardized attributes. The `withGenAISpan` utility manages the lifecycle of these spans. Standard attributes recorded include:
- **Request Metadata**: `gen_ai.request.model`, `gen_ai.request.temperature`, and `gen_ai.request.max_tokens` [site/docs/tracing.md:78-81]().
- **Usage Metrics**: `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, and reasoning tokens [site/docs/tracing.md:86-88]().
- **Promptfoo Specifics**: `promptfoo.provider.id`, `promptfoo.test.index`, and `promptfoo.cache_hit` [site/docs/tracing.md:95-98]().

### Trace Context Generation
Promptfoo generates W3C Trace Context headers to propagate state.
- **`generateTraceparent()`**: Creates a standard W3C `traceparent` header (version-traceId-spanId-flags) to link internal and external spans [src/tracing/evaluatorTracing.ts:64-72]().
- **Context Management**: The `generateTraceId` and `generateSpanId` functions create the necessary 16-byte and 8-byte identifiers [src/tracing/evaluatorTracing.ts:49-58]().

Sources: [src/tracing/evaluatorTracing.ts:47-72](), [site/docs/tracing.md:66-105]()

## Trajectory and Trace-Aware Assertions

Promptfoo allows for automated validation of execution trajectories using specialized assertion types that operate on the trace data.

### Trajectory Extraction (`trajectoryUtils.ts`)
The `extractTrajectorySteps()` function processes raw spans into a normalized list of `TrajectoryStep` objects [src/assertions/trajectoryUtils.ts:12-33]().
- **Tool Identification**: The system extracts tool names and arguments from attributes like `tool.name` or `gen_ai.tool.name` [src/assertions/trajectoryUtils.ts:144-150]().
- **Command Normalization**: Tool calls matching names like `exec_command` or `shell` are classified as `command` steps [src/assertions/trajectoryUtils.ts:36-46]().
- **Search Logic**: Spans are heuristically identified as `search` steps if their names match patterns like `find` or `lookup` [src/assertions/trajectoryUtils.ts:48-48](), [src/assertions/trajectoryUtils.ts:101-110]().

### Assertion Types
Users can define assertions that inspect the trace in their configuration:
| Assertion Type | Handler | Description |
| --- | --- | --- |
| `trajectory:tool-used` | `handleTrajectoryToolUsed` | Validates that specific tools were called, supporting min/max counts [src/assertions/trajectory.ts:136-194](). |
| `trajectory:tool-sequence` | `handleTrajectoryToolSequence` | Validates the specific order of tool calls (exact or in-order) [src/assertions/trajectory.ts:22-25](). |
| `trajectory:tool-args-match` | `handleTrajectoryToolArgsMatch` | Validates that tool arguments match expected values (partial or exact) [src/assertions/trajectory.ts:33-39](). |
| `trajectory:goal-success` | `matchesTrajectoryGoalSuccess` | Uses an LLM to judge if the overall trajectory achieved a goal [src/assertions/trajectory.ts:27-29](). |

Sources: [src/assertions/trajectory.ts:1-209](), [src/assertions/trajectoryUtils.ts:1-230](), [test/assertions/trajectory.test.ts:111-197]()

## OpenAI Agents Integration

The `OpenAiAgentsProvider` provides deep integration with the `@openai/agents` SDK, including specialized tracing support.

- **Trace Setup**: The provider uses `setupTracingIfNeeded` to register the `OTLPTracingExporter` and start the SDK's trace export loop [src/providers/openai/agents.ts:150-175]().
- **Context Injection**: It uses `getOrCreateTrace` from the SDK to wrap agent runs, ensuring spans are correctly associated with the Promptfoo evaluation context [src/providers/openai/agents.ts:4-8]().
- **Agent Visualization**: The provider captures multi-turn interactions, tool executions, and handoffs between agents, which are then stored in the local `TraceStore` [src/providers/openai/agents.ts:106-145]().

**Agent Tracing Data Flow**
```mermaid
graph TD
    subgraph "Provider Space"
        A["OpenAiAgentsProvider"]
        B["initializeAgent()"]
        C["runAgent()"]
    end

    subgraph "SDK Space"
        D["@openai/agents SDK"]
        E["OTLPTracingExporter"]
    end

    subgraph "Storage Space"
        F["OTLPReceiver"]
        G["TraceStore"]
    end

    A --> B
    A --> C
    C --> D
    D --> E
    E --> F
    F --> G
```
Sources: [src/providers/openai/agents.ts:41-207](), [test/providers/openai/agents.test.ts:83-126]()

## Vercel AI SDK Integration

Promptfoo integrates with the Vercel AI SDK by acting as a standard OTLP destination. By setting the `OTEL_EXPORTER_OTLP_ENDPOINT` in a Vercel AI application to the Promptfoo receiver (e.g., `http://localhost:4318/v1/traces`), Promptfoo captures the full execution lifecycle of the SDK, including middleware, model calls, and tool invocations.

Sources: [site/docs/tracing.md:16-37](), [site/docs/providers/vercel.md:1-10]()
This page introduces the promptfoo repository as a whole: what it does, how its major subsystems relate, and the entry points available to users. For details on any specific subsystem, follow the links to the relevant child pages throughout this document.

---

## What is promptfoo?

promptfoo is an open-source **LLM evaluation and red-teaming toolkit** (MIT license, version 0.122.2). It provides a CLI, a Node.js library, and a local web UI for:

- Running structured test suites against LLM prompts, agents, and RAG pipelines.
- Comparing responses across multiple providers side-by-side.
- Performing automated red-team scans to find security and safety vulnerabilities.
- Integrating evaluations into CI/CD pipelines.
- Reviewing pull requests for LLM-related security issues via code scanning.

> From `CITATION.cff`: *"LLM evaluation and testing toolkit for prompts, agents, and RAGs. Supports redteaming, pentesting, and vulnerability scanning for LLMs. Compare performance across various models (GPT, Claude, Gemini, Llama, etc.). Features declarative configs, CLI, and CI/CD integration."*

Sources: [README.md:1-97](), [CITATION.cff:1-21](), [package.json:1-5]()

---

## Monorepo Layout

The repository is a Node.js workspace monorepo with primary packages for the core engine, the web application, and documentation.

| Directory | Package name | Purpose |
|-----------|-------------|---------|
| `/` (root) | `promptfoo` | CLI binary, TypeScript library, evaluation engine, provider integrations, red team system |
| `src/app` | `app` | React/Vite web application (results viewer, red team setup wizard, reports) |
| `site` | `promptfoo-docs` | Docusaurus documentation site |

The root package exposes two entry points:

- **CLI binary**: `dist/src/entrypoint.js` (invoked as `promptfoo` or `pf`) [package.json:51-54]()
- **Node.js library**: `dist/src/index.js` / `dist/src/index.cjs` (imported as `promptfoo`) [package.json:12-18]()

For details on the monorepo structure and entry points, see [Monorepo Architecture](#1.1). For information on building from source, see [Dependencies and Build System](#1.2).

Sources: [package.json:29-32](), [src/app/package.json:1-6](), [site/package.json:1-4]()

---

## Major Subsystems

**System interaction diagram:**

```mermaid
flowchart TD
  user["User / CI System"]

  subgraph "EntryPoints"
    cli["CLI (src/main.ts)"]
    lib["Library API (src/index.ts)"]
    webui["Web UI (src/app)"]
  end

  subgraph "CoreEngine"
    eval["Evaluator (src/evaluator.ts)"]
    config["Config Loader (src/util/config/load.ts)"]
    assertions["Assertion Engine (src/assertions/index.ts)"]
    db["Drizzle ORM (src/models/eval.ts)"]
  end

  subgraph "Providers"
    provregistry["providerRegistry (src/providers/providerRegistry.ts)"]
    openai["OpenAiChatCompletionProvider"]
    anthropic["AnthropicChatCompletionProvider"]
    bedrock["AwsBedrockGenericProvider"]
    http["HttpProvider"]
    python["PythonProvider"]
  end

  subgraph "RedTeam"
    rtengine["Red Team Engine (src/redteam)"]
    plugins["RedteamPluginBase"]
    strategies["RedteamStrategy"]
    attackproviders["RedteamIterativeProvider"]
  end

  subgraph "WebAndSharing"
    server["Express Server (src/server/index.ts)"]
    share["Share (src/share.ts)"]
    cloud["CloudConfig (src/globalConfig/cloud.ts)"]
  end

  user --> cli
  user --> lib
  user --> webui

  cli --> eval
  lib --> eval
  webui --> server

  eval --> config
  eval --> assertions
  eval --> provregistry
  eval --> db

  provregistry --> openai
  provregistry --> anthropic
  provregistry --> bedrock
  provregistry --> http
  provregistry --> python

  rtengine --> eval
  rtengine --> plugins
  rtengine --> strategies
  rtengine --> attackproviders

  server --> eval
  server --> db
  server --> share
  share --> cloud
```

Sources: [package.json:12-18](), [src/app/package.json:8-21](), [src/main.ts:1-148]()

---

The table below maps each subsystem to its wiki page and primary source location.

| Subsystem | Description | Key Files | Wiki Page |
|-----------|-------------|-----------|-----------|
| Core Evaluation Engine | Runs test suites: renders prompts, calls providers, executes assertions | `src/evaluator.ts` | [Core Evaluation System](#2) |
| Test Suite & Config | Loads and validates `promptfooconfig.yaml`; merges configs | `src/util/config/`, `src/types/index.ts` | [Test Suite and Configuration](#2.2) |
| Assertions & Grading | Deterministic and model-graded assertion types | `src/assertions/` | [Assertions and Grading](#2.3) |
| Data Persistence | SQLite via Drizzle ORM; `Eval` and `EvalResult` models | `src/models/eval.ts`, `src/migrate.ts` | [Data Models and Persistence](#2.4) |
| Provider System | `ApiProvider` abstraction + integrations for major LLM providers | `src/providers/` | [Provider System](#3) |
| CLI | `Commander.js`-based CLI; `promptfoo` and `pf` commands | `src/main.ts` | [CLI System](#4) |
| Red Team System | Adversarial test generation, plugins, and iterative attack providers | `src/redteam/` | [Red Team System](#5) |
| Web Interface | React frontend + Express 5 + Socket.IO backend | `src/app/`, `src/server/` | [Web Interface](#6) |
| Sharing & Cloud | Chunked upload to cloud, shareable URLs, and authentication | `src/share.ts`, `src/globalConfig/cloud.ts` | [Sharing and Cloud Integration](#7) |

---

## User Interaction Modes

promptfoo can be used in three primary ways:

### 1. CLI

The CLI is the most common interface, providing commands for evaluation, red-teaming, and result management.

```sh
promptfoo eval                  # Run standard evaluation
promptfoo redteam run           # Run adversarial scan
promptfoo view                  # Open the local web results viewer
promptfoo mcp                   # Start Model Context Protocol server
```

The CLI entry point is defined in `package.json` pointing to the built `dist/src/entrypoint.js` [package.json:51-54](). Command registration is handled in `src/main.ts` [src/main.ts:71-137]().

Sources: [package.json:51-54](), [README.md:42-48](), [src/main.ts:71-137]()

### 2. Node.js Library

The package can be imported into TypeScript/JavaScript projects to programmatically run evaluations.

```ts
import { evaluate } from 'promptfoo';

const result = await evaluate({
  prompts: ['Rephrase this: {{text}}'],
  providers: ['openai:gpt-4o'],
  tests: [{ vars: { text: 'Hello world' } }],
});
```

The library entry point is `src/index.ts` (via `dist/src/index.js`) [package.json:12-18]().

Sources: [package.json:12-18](), [src/index.ts:1-10]()

### 3. Web UI

A local React application launched by `promptfoo view`. It connects to an Express server (`src/server/index.ts`) and uses Socket.IO for real-time progress updates during evaluations.

Sources: [src/app/package.json:1-10](), [package.json:87-88](), [src/main.ts:91]()

---

## Core Evaluation Flow

**High-level evaluation lifecycle:**

```mermaid
sequenceDiagram
  participant "CLI/Lib" as caller
  participant "evaluate()" as evaluator
  participant "loadApiProviders()" as providers
  participant "runEval()" as runEval
  participant "runAssertions()" as assertions
  participant "Eval Model" as db

  caller->>evaluator: "evaluate(testSuite, options)"
  evaluator->>providers: "resolve provider strings to ApiProvider instances"
  providers-->>evaluator: "ApiProvider[]"
  evaluator->>db: "initialize Eval record"
  loop "for each (prompt × provider × test)"
    evaluator->>runEval: "runEval()"
    runEval->>providers: "provider.callApi(renderedPrompt)"
    providers-->>runEval: "ProviderResponse"
    runEval->>assertions: "runAssertions(response)"
    assertions-->>runEval: "GradingResult"
    runEval-->>evaluator: "EvaluateResult"
  end
  evaluator->>db: "persist all results"
  evaluator-->>caller: "EvaluateSummary"
```

Sources: [src/evaluator.ts:1-136](), [src/node/doEval.ts:1-50](), [src/assertions/index.ts:1-15]()

---

## Key Code Entities at a Glance

**Core type and class map:**

```mermaid
classDiagram
  class "TestSuite" {
    +providers ApiProvider[]
    +prompts Prompt[]
    +tests TestCase[]
    +defaultTest TestCase
  }
  class "Eval" {
    +id string
    +create(config, prompts)
    +addResult(result)
  }
  class "ApiProvider" {
    <<interface>>
    +id() string
    +callApi(prompt, context) ProviderResponse
  }
  class "Evaluator" {
    +evaluate(testSuite, options)
    +runEval(options)
  }
  class "RedteamPluginBase" {
    <<abstract>>
    +getTests(count)
  }
  class "RedteamGraderBase" {
    <<abstract>>
    +getResult(prompt, output, test)
  }

  Evaluator --> TestSuite : "processes"
  Evaluator --> Eval : "persists to"
  TestSuite "1" --> "*" ApiProvider : "uses"
  RedteamPluginBase ..> "TestCase" : "generates"
```

Sources: [src/types/index.ts:1-209](), [src/evaluator.ts:175-179](), [src/types/providers.ts:1-44]()

---

## Technology Stack Summary

| Layer | Technology |
|-------|-----------|
| Runtime | Node.js `>=22.22.0` [package.json:49-50]() |
| Language | TypeScript 7.x [package.json:153]() |
| Build | `tsdown` + `tsc` [package.json:63]() |
| Database | SQLite via `drizzle-orm` [package.json:53]() |
| CLI framework | `commander` 14 [package.json:45]() |
| Web Server | `express` 5 + `socket.io` [package.json:55, 88]() |
| Frontend | React 19, Vite 8, Zustand 5, Radix UI [src/app/package.json:60, 75, 77, 80-96]() |
| Documentation | Docusaurus 3 [site/package.json:28]() |

Sources: [package.json:1-162](), [src/app/package.json:1-100](), [site/package.json:1-97]()

# Monorepo Architecture




## Purpose and Scope

This document describes the monorepo structure of Promptfoo, covering workspace organization, dependency management, and the build system. It explains how the three main workspaces (CLI core, Web UI, and Documentation) are organized and how they interact during development and deployment. For information about specific subsystems within each workspace, see the relevant sections: Core Evaluation System (section 2), Web Interface (section 6), and CLI System (section 4).

## Workspace Structure

Promptfoo uses npm workspaces to organize three distinct packages within a single repository. The workspace configuration is defined in the root `package.json`.

```mermaid
graph TB
    subgraph "Repository Root"
        Root["Root Package<br/>(promptfoo CLI)<br/>package.json"]

        subgraph "src/app"
            WebUI["Web UI Workspace<br/>(React + Vite)<br/>src/app/package.json"]
        end

        subgraph "site"
            Docs["Documentation Workspace<br/>(Docusaurus)<br/>site/package.json"]
        end

        subgraph "examples/"
            Ex1["examples/redteam-chatbot/"]
            Ex2["examples/http-provider-auth-signature/"]
            ExMore["... (many examples)"]
        end

        subgraph "code-scan-action"
            GitHubAction["GitHub Action<br/>code-scan-action/package.json"]
        end
    end

    Root --> WebUI
    Root --> Docs
    Root --> GitHubAction
```

**Sources:** [package.json:29-32](), [package-lock.json:11-14]()

### Root Package (CLI Core)

The root package serves as the main CLI application and core library. It contains:

- **CLI Entry Point**: `dist/src/entrypoint.js` — registered as both `promptfoo` and `pf` bin commands [package.json:51-54]().
- **Library Entry Point**: `dist/src/index.js` (ESM) / `dist/src/index.cjs` (CommonJS) [package.json:12-17]().
- **Type Definitions**: `dist/src/index.d.ts` [package.json:33-34]().
- **Core Source**: All TypeScript source code in the `src/` directory.
- **Build Output**: Compiled and bundled JavaScript in the `dist/` directory [package.json:42-47]().
- **Exports**: Dual ESM/CJS exports via the `exports` field [package.json:13-28]().
- **Node Engine**: Requires Node `>=22.22.0` [package.json:48-50]().

### Web UI Workspace (src/app)

The Web UI workspace provides a browser-based interface for viewing evaluation results.

| Property | Value |
|----------|-------|
| Location | `src/app/` [package.json:30]() |
| Package Name | `app` [src/app/package.json:2]() |
| Type | ES Module (`"type": "module"`) [src/app/package.json:6]() |
| Build Tool | Vite [src/app/package.json:8]() |
| Framework | React 19 [src/app/package.json:60]() |
| UI Components | Radix UI primitives (`@radix-ui/*`) [src/app/package.json:80-96]() |
| Styling | Tailwind CSS v4 [src/app/package.json:72]() |
| State Management | Zustand [src/app/package.json:77]() |
| Data Fetching | TanStack Query [src/app/package.json:31]() |
| Routing | React Router v7 [src/app/package.json:65]() |
| Test Runner | Vitest [src/app/package.json:16]() |

The workspace is marked as private [src/app/package.json:3]() and is not published to npm. Build artifacts are embedded into the root package during the main build process via `npm run build:app` [package.json:60]().

**Sources:** [src/app/package.json:1-100](), [package.json:60]()

### Documentation Workspace (site)

The documentation workspace uses Docusaurus to generate the static documentation site.

| Property | Value |
|----------|-------|
| Location | `site/` [package.json:31]() |
| Package Name | `promptfoo-docs` [site/package.json:2]() |
| Build Tool | Docusaurus 3.x (`@docusaurus/core`) [site/package.json:28]() |
| Dev Server Port | 3100 (configurable via `PORT` env) [site/package.json:11]() |
| Mermaid Support | `@docusaurus/theme-mermaid` [site/package.json:33]() |

The site fetches GitHub stats before each build via `scripts/fetch-stats.mjs` [site/package.json:7-12]().

**Sources:** [site/package.json:1-96]()

### GitHub Action Workspace (code-scan-action)

A specialized package for scanning pull requests with promptfoo's code-scan capabilities.

- **Location**: `code-scan-action/`
- **Build Tool**: `esbuild` [code-scan-action/package.json:10]()
- **Target**: Node 22 [code-scan-action/package.json:10]()
- **Dependencies**: `@actions/core`, `@actions/github`, `@octokit/rest` [code-scan-action/package.json:21-25]()

**Sources:** [code-scan-action/package.json:1-35]()

## Internal Layer Boundaries

The architecture enforces strict dependency boundaries between modules to prevent circular dependencies and maintain separation of concerns. These are defined in `architecture/layers.json` and enforced by `scripts/checkArchitectureBoundaries.ts`.

| Layer | Responsibility | Allowed to Import From |
|-------|----------------|------------------------|
| **CLI/Commands** | Entrypoints and user interaction | `eval`, `redteam`, `server`, `util` |
| **Red Team** | Adversarial generation and attack providers | `eval`, `providers`, `util` |
| **Eval Engine** | Core evaluation logic and assertions | `providers`, `database`, `util` |
| **Providers** | LLM and API integrations | `util`, `types` |
| **Database** | Persistence layer (SQLite/Drizzle) | `types`, `util` |

**Sources:** [package.json:58](), [scripts/checkArchitectureBoundaries.ts:1-20]()

## Dependency Management

Promptfoo maintains an extensive list of dependencies to support various LLM providers and evaluation capabilities.

### Core Dependencies

Core dependencies are always installed and include:

- **LLM SDKs**: `@anthropic-ai/sdk`, `openai`, `ai` (Vercel AI SDK) [package-lock.json:16,74,35]()
- **Database**: `drizzle-orm` with `@libsql/client` [package-lock.json:53,26]()
- **Server**: `express` 5.x, `socket.io`, `cors`, `compression` [package-lock.json:55,88,47,46]()
- **CLI**: `commander`, `chalk`, `cli-progress`, `@inquirer/*` packages [package-lock.json:45,41,43,19-25]()
- **Templating**: `nunjucks` [package-lock.json:73]()
- **Utilities**: `js-yaml`, `glob`, `ajv`, `zod`, `winston` (logging) [package-lock.json:66,62,36,95,93]()
- **Tracing**: `@opentelemetry/*` packages [package-lock.json:27-33]()

### Optional and Dev Dependencies

Optional dependencies reduce the installation footprint and are loaded dynamically when needed. These include platform-specific binaries and specialized SDKs:

| Package Group | Purpose |
|---|---|
| `@aws-sdk/*` | AWS Bedrock and S3 integration [package-lock.json:104-107]() |
| `@azure/*` | Azure provider support [package-lock.json:110-111]() |
| `@ibm-cloud/watsonx-ai` | IBM watsonx support [package-lock.json:114]() |
| `@modelcontextprotocol/sdk` | MCP integration [package-lock.json:178]() |
| `playwright` | Browser-based providers [package-lock.json:143]() |

**Sources:** [package-lock.json:1-198]()

### Dependency Overrides

The repository uses npm `overrides` to enforce specific versions and reduce vulnerability surface:

| Override | Target Version |
|---|---|
| `chokidar` | `5.0.0` [package.json:115]() |
| `whatwg-url` | `16.0.1` [package.json:116]() |
| `esbuild` | `0.28.2` [package.json:117]() |
| `react`, `react-dom` | `^19.2.4` [package.json:124-125]() |

**Sources:** [package.json:113-162]()

## Build System

The build system orchestrates the compilation of TypeScript source code and the bundling of the web application.

```mermaid
flowchart TB
    subgraph "npm run build (root)"
        Start["npm run build"]
        Parallel["concurrently"]
        TSCNoEmit["tsc --noEmit\n(type checking)"]
        Tsdown["tsdown\n(bundle src/ → dist/)"]
        BuildApp["npm run build:app\n(Vite build)"]
        Postbuild["postbuild: tsx scripts/postbuild.ts"]
    end

    Start --> Parallel
    Parallel --> TSCNoEmit
    Parallel --> Tsdown
    Parallel --> BuildApp
    Tsdown --> Postbuild
    BuildApp --> Postbuild
    TSCNoEmit --> Postbuild
```

**Sources:** [package.json:63-64,108]()

### Build Script Breakdown

The main build command (`npm run build`) runs three tasks in parallel via `concurrently` [package.json:63]():

1. **`npm run tsc`**: Runs `tsc --noEmit` to perform type checking across the project [package.json:108]().
2. **`tsdown`**: Bundles the TypeScript source in `src/` into the `dist/` directory using `tsdown.config.ts` [package.json:63]().
3. **`npm run build:app`**: Triggers the Vite build process in the `src/app` workspace [package.json:60]().

After these complete, the **`postbuild`** hook runs `tsx scripts/postbuild.ts` to perform final asset organization and dual-format (ESM/CJS) support [package.json:64]().

### Development Workflows

```mermaid
graph TB
    subgraph "npm run dev (full stack)"
        DevStart["npm run dev"]
        DevServer["npm run dev:server\ntsx watch src/server/index.ts"]
        DevApp["npm run dev:app\nvite dev server"]
    end

    DevStart --> DevServer
    DevStart --> DevApp

    subgraph "Local CLI"
        Local["npm run local\ntsx src/localEntrypoint.ts"]
    end
```

**Sources:** [package.json:74-75,89]()

The development setup uses `concurrently` to run both the Express backend server (`src/server/index.ts`) and the Vite frontend dev server simultaneously [package.json:75]().

## Code Quality and Testing

Promptfoo uses a variety of tools to ensure code quality and stability.

### Code Quality Tools

| Tool | Purpose | Command |
|---|---|---|
| **Biome** | Linting and formatting (JS/TS/JSON) | `npm run lint` [package.json:87]() |
| **Prettier** | Formatting (CSS/MD/YAML) | `npm run format` [package.json:79]() |
| **Vitest** | Unit and Integration testing | `npm test` [package.json:104]() |
| **Drizzle Kit** | Database migrations | `npm run db:generate` [package.json:66]() |
| **Architecture Check** | Enforce module boundaries | `npm run architecture:check` [package.json:58]() |

**Sources:** [package.json:58-104]()

### Testing Infrastructure

The test suite is divided into several categories to balance speed and coverage:

- **Unit Tests**: Fast tests for individual functions and classes using Vitest [package.json:104]().
- **Integration Tests**: Tests that exercise multiple components or external APIs [package.json:98]().
- **Smoke Tests**: High-level tests to ensure basic functionality is intact [package.json:103]().
- **Red Team Integration**: Specialized end-to-end tests for adversarial capabilities [package.json:102]().
- **App Tests**: Browser and component tests for the React interface [package.json:94-95]().

**Sources:** [package.json:94-105]()

## Release and Versioning

The release process is automated to ensure consistency in versioning and metadata updates.

```mermaid
graph LR
    subgraph "Release Lifecycle"
        Pre["preversion\n(Branch & Git check)"]
        Ver["npm version\n(Bump)"]
        Post["postversion\n(Changelog, Citation, PR)"]
    end

    Pre --> Ver --> Post
```

**Sources:** [package.json:90-92]()

1. **`preversion`**: Ensures the user is on the `main` branch and has the GitHub CLI installed before starting a version bump branch [package.json:90]().
2. **`postversion`**: Runs `scripts/update-changelog-version.cjs` and `scripts/generateCitation.ts` to keep project metadata in sync with the new version, then automatically creates a GitHub Pull Request [package.json:92]().
3. **`prepublishOnly`**: Validates the presence of `PROMPTFOO_POSTHOG_KEY`, performs a clean build, and bundles assets before publishing to npm [package.json:93]().

**Sources:** [package.json:90-93]()

# Dependencies and Build System




This page documents the npm/Node.js dependency structure, TypeScript compilation pipeline, and build scripts for the promptfoo core package. It covers the root-level build configuration and how the workspace packages are assembled into the final distributable.

For information about the CI/CD workflows that consume the build (GitHub Actions, Docker publishing, release automation), see [Build System and CI/CD](9.1). For the testing infrastructure (Vitest configs, coverage), see [Testing Infrastructure](9.2). For the monorepo layout and the purpose of each workspace, see [Monorepo Architecture](1.1).

---

## Node.js and npm Requirements

The repository enforces a specific Node.js version range across all packages to ensure compatibility with modern ESM features and the SQLite driver:

| Requirement | Value |
|---|---|
| Supported Node versions | `^20.20.0 || >=22.22.0` |
| npm version (minimum) | `>= 11` (via Renovate constraint) |
| Package manager | npm with lockfile version 3 |
| Module system | ESM (`"type": "module"` in root `package.json`) |

Sources: [package.json:48-50](), [renovate.json:8-10](), [package-lock.json:4-4]()

---

## Workspace Structure

The repository uses npm workspaces to manage multiple packages from a single `package-lock.json`. This allows for shared dependencies while isolating the frontend UI and documentation from the core CLI logic.

**Workspace layout:**

| Workspace path | Package name | Purpose |
|---|---|---|
| _(root)_ | `promptfoo` | CLI, core evaluation engine, server backend |
| `src/app` | `app` | React web UI (Vite-based) |
| `site` | `promptfoo-docs` | Docusaurus documentation site |

Sources: [package.json:29-32](), [src/app/package.json:1-4](), [site/package.json:1-4]()

**Workspace dependency diagram:**

```mermaid
graph TD
  root["promptfoo (root)"]
  app["src/app (app)"]
  site["site (promptfoo-docs)"]

  root --"npm workspaces"--> app
  root --"npm workspaces"--> site

  root --"produces dist/src/index.js"--> dist_root["dist/src/"]
  root --"produces dist/src/app/"--> dist_app["dist/src/app/ (served by Express)"]
  app --"vite build outputs to"--> dist_app
```

Sources: [package.json:12-28](), [package.json:29-32]()

---

## Runtime Dependencies

These packages are required in the published `promptfoo` npm package to support the CLI, the evaluation engine, and the local server.

### Core Infrastructure

| Package | Version | Role |
|---|---|---|
| `express` | `^5.2.1` | HTTP server for the web UI and API |
| `socket.io` | `^4.8.3` | Real-time evaluation progress streaming |
| `commander` | `^14.0.3` | CLI command and argument parsing |
| `@libsql/client` | `^0.17.3` | SQLite/LibSQL driver for evaluation persistence |
| `drizzle-orm` | `^0.45.1` | ORM for SQLite schema management |
| `zod` | `^4.3.6` | Runtime schema validation and TypeScript inference |
| `winston` | `^3.19.0` | Logging infrastructure |
| `dotenv` | `^17.3.1` | Environment variable loading |
| `tsx` | `^4.23.11` | TypeScript execution for development and scripts |

Sources: [package-lock.json:15-95]()

### LLM Provider SDKs (Runtime)

The project includes several SDKs as direct dependencies to ensure robust integration with major providers:

| Package | Role |
|---|---|
| `@anthropic-ai/sdk` | Anthropic Claude API client |
| `openai` | OpenAI and Azure OpenAI client |
| `ai` (Vercel AI SDK) | Unified AI SDK for streaming and tool use |
| `@opentelemetry/api` | Tracing and observability |
| `posthog-node` | Telemetry and usage analytics |

Sources: [package-lock.json:16-34](), [package-lock.json:73-77]()

---

## Optional Dependencies

Optional dependencies are installed when present but do not cause install failures if unavailable. They gate platform-specific provider integrations or heavy media processing libraries.

| Package group | Packages | When needed |
|---|---|---|
| AWS | `@aws-sdk/client-bedrock-runtime`, `@aws-sdk/client-bedrock-agent-runtime`, `@aws-sdk/client-s3`, `@aws-sdk/client-sagemaker-runtime` | AWS Bedrock and SageMaker providers |
| Azure | `@azure/identity`, `@azure/openai-assistants`, `@azure/ai-projects`, `@azure/storage-blob` | Azure OpenAI and AI Foundry providers |
| Google | `google-auth-library`, `@googleapis/sheets` | Google Vertex AI auth and Google Sheets integration |
| IBM | `@ibm-cloud/watsonx-ai`, `ibm-cloud-sdk-core` | IBM Watsonx provider |
| Agent SDKs | `@anthropic-ai/claude-agent-sdk`, `@openai/agents`, `@openai/codex-sdk`, `@opencode-ai/sdk` | Agentic evaluation and SDK-based providers |
| Infrastructure | `@modelcontextprotocol/sdk` | MCP server support and tool exposure |

Sources: [package-lock.json:162-182]()

---

## TypeScript Configuration and Compilation

The root package uses a two-phase TypeScript process to ensure type safety while maintaining high performance during bundling.

1. **Type checking**: `tsc --noEmit` — validates types across the project without emitting files. [package.json:108-108]()
2. **Bundling**: `tsdown` — a fast TypeScript bundler (based on esbuild/rolldown) that compiles and bundles source into the `dist/` directory. [package.json:63-63]()

The published output includes both ESM and CJS formats to support the widest range of Node.js environments:

```
dist/src/index.js      ← ESM (import)
dist/src/index.cjs     ← CommonJS (require)
dist/src/index.d.ts    ← Type declarations
dist/src/entrypoint.js ← CLI binary entrypoint (aliased to 'promptfoo' and 'pf')
```

Sources: [package.json:12-28](), [package.json:33-41](), [package.json:51-54]()

### postbuild.ts

The `postbuild` script (`tsx scripts/postbuild.ts`) runs after every successful build. It handles tasks that the bundler cannot, such as copying static assets or refining the `dist` structure for distribution.

Sources: [package.json:64-64]()

---

## Build Scripts

### Full Build Pipeline

The build pipeline is designed for speed and concurrency. It uses `concurrently` to run the type checker, the core bundler, and the frontend build in parallel.

**Build pipeline diagram:**

```mermaid
flowchart LR
  build["npm run build"]

  subgraph "Concurrent processes (concurrently -g)"
    tsc["tsc --noEmit\n(type check only)"]
    tsdown["tsdown\n(bundle core to dist/)"]
    buildapp["npm run build:app\n(src/app)"]
  end

  subgraph "src/app build"
    tsc_app["tsc -b"]
    vite["vite build"]
  end

  postbuild["tsx scripts/postbuild.ts\n(postbuild hook)"]

  build --> tsc
  build --> tsdown
  build --> buildapp
  buildapp --> tsc_app
  buildapp --> vite
  tsdown --> dist_main["dist/src/index.js\ndist/src/index.cjs\ndist/src/entrypoint.js"]
  vite --> dist_app["dist/src/app/\n(static assets)"]
  tsc --> postbuild
  tsdown --> postbuild
  buildapp --> postbuild
```

Sources: [package.json:63-64](), [src/app/package.json:10-10]()

### Key npm Scripts Reference

| Script | Command | Purpose |
|---|---|---|
| `build` | `concurrently ... "npm run tsc" "tsdown" "npm run build:app"` | Full production build of all components |
| `build:clean` | `shx rm -rf dist` | Remove build artifacts and stale files |
| `build:watch` | `tsdown --watch` | Incremental watch build for core CLI/server |
| `build:app` | `npm run build --prefix src/app` | Build React app only (Vite + TSC) |
| `dev` | `concurrently "npm run dev:server" "npm run dev:app"` | Start backend server (tsx watch) + frontend (Vite) |
| `dev:server` | `tsx watch src/server/index.ts` | Express server with hot reload for backend logic |
| `dev:app` | `npm run dev --prefix src/app` | Vite dev server for rapid frontend iteration |
| `local` | `tsx src/localEntrypoint.ts` | Run CLI directly from source using tsx |

Sources: [package.json:55-75](), [package.json:89-89]()

The `NODE_OPTIONS='--max-old-space-size=8192'` flag is applied to `tsdown` invocations to prevent heap exhaustion during complex bundling operations. [package.json:62-63]()

---

## Database Schema Management

Drizzle ORM manages the SQLite schema used by the evaluation persistence layer. This allows for declarative schema definitions and automated migrations.

| Script | Command | Purpose |
|---|---|---|
| `db:generate` | `npx drizzle-kit generate` | Generate migration SQL files from TypeScript schema |
| `db:migrate` | `tsx src/migrate.ts` | Apply pending SQL migrations to the local database |
| `db:studio` | `npx drizzle-kit studio` | Launch a web-based GUI to inspect the SQLite database |

Sources: [package.json:66-68]()

---

## Dependency Management

### npm Overrides

The root `package.json` defines overrides to force specific versions of transitive dependencies, resolving security vulnerabilities and ensuring version consistency across workspaces:

| Override | Pinned value | Reason |
|---|---|---|
| `chokidar` | `5.0.0` | Ensure consistent file watching behavior |
| `whatwg-url` | `16.0.1` | Fix compatibility issues in Node environments |
| `esbuild` | `0.28.2` | Pin bundler version for deterministic builds |
| `react` / `react-dom` | `^19.2.4` | Enforce React 19 across the monorepo |
| `undici` | `>=7.29.0 <8` | Fix specific Node "terminated" errors and vulnerabilities |

Sources: [package.json:113-162](), [CHANGELOG.md:41-50]()

### Renovate Automation

The `renovate.json` configuration automates dependency updates with specific grouping rules to reduce PR noise:

| Group | Packages |
|---|---|
| LLM providers | Anthropic, AWS SDK, Azure, OpenAI, PostHog, IBM, fal.ai, langfuse |
| Frameworks | Storybook, Docusaurus, React, TanStack, MUI |
| Tooling | Vitest, SWC, Biome, Playwright, Drizzle ORM, tsdown |
| Infrastructure | OpenTelemetry, socket.io, GitHub Actions, Octokit |

Sources: [renovate.json:61-191]()

---

## src/app Workspace Dependencies

The React app (`src/app`) is a separate TypeScript project that bundles into static assets served by the Express backend.

Key app-level dependencies:

| Package | Role |
|---|---|
| `vite` | Fast frontend build tool and dev server |
| `react` / `react-dom` | Core UI framework (v19) |
| `@tanstack/react-query` | Asynchronous state and API data fetching |
| `@tanstack/react-table` | High-performance results table rendering |
| `zustand` | Lightweight client-side state management |
| `socket.io-client` | Client-side real-time evaluation updates |
| `@radix-ui/*` | Accessible, unstyled UI components (Dialog, Tabs, etc.) |
| `tailwindcss` | Utility-first CSS framework (v4) |

Sources: [src/app/package.json:31-99]()

# Core Evaluation System




This page provides an overview of the evaluation pipeline that powers promptfoo's LLM testing capabilities, tracing how a configuration file becomes a set of scored results. It covers the major components and their roles as they relate to each other.

For deeper coverage of individual subsystems, see:
- [Evaluation Engine](#2.1) — `Evaluator` class internals, concurrency, and progress tracking
- [Test Suite and Configuration](#2.2) — config file loading, merging, and the `TestSuite` type
- [Assertions and Grading](#2.3) — all assertion types and grading logic
- [Data Models and Persistence](#2.4) — the `Eval`/`EvalResult` database models
- [Utilities and Output Generation](#2.5) — prompt rendering, transforms, and output formats

---

## What the Core Evaluation System Does

The core evaluation system takes a `TestSuite` (a fully-resolved in-memory representation of a `promptfooconfig.yaml`) and executes a matrix of test cases: every configured **prompt** × every configured **provider** × every **test case** (and its variable combinations). For each cell in that matrix, it calls the provider API, applies output transforms, runs all assertions, and accumulates scored `EvaluateResult` objects. The system also handles concurrency control, rate limiting, progress reporting, caching, extension hooks, and result persistence.

---

## Top-Level Entry Points

There are two entry points depending on whether the caller is using the CLI or the Node.js library API.

| Entry point | File | Role |
|---|---|---|
| `evaluate()` (public) | [src/index.ts:63-63]() | Library API — entry point for programmatic usage |
| `evaluate()` (internal) | [src/evaluator.ts:901-1185]() | The core execution logic; creates the `Evaluator` instance and runs the eval loop |
| `doEval()` | [src/node/doEval.ts:441-653]() | CLI-side handler — resolves configs, handles CLI flags, and calls the internal `evaluate()` |

The public `evaluate()` in `src/index.ts` is the primary programmatic API [src/index.ts:63-63](). It delegates to the core `evaluate` function in the Node-specific entry point [src/index.ts:4-4]().

Sources: [src/index.ts:4-63](), [src/evaluator.ts:901-1185](), [src/node/doEval.ts:40-40]()

---

## Evaluation Pipeline

**Diagram: End-to-End Evaluation Pipeline**

```mermaid
flowchart TD
    A["promptfooconfig.yaml"] --> B["loadDefaultConfig()"]
    B --> C["UnifiedConfig"]
    C --> D["doEval() / resolveConfigs()"]
    D --> E["EvalRunError check"]
    E --> F["evaluate() in evaluator.ts"]

    F --> G["runExtensionHook('beforeAll')"]
    G --> H["Matrix Expansion:\nProviders x Prompts x Tests"]
    H --> I["async.queue(concurrency)"]

    I --> K["runEval() — single cell"]

    K --> K1["renderPrompt()"]
    K1 --> K2["ApiProvider.callApi()"]
    K2 --> K3["transform() — output mapping"]
    K3 --> K4["runAssertions()"]
    K4 --> K5["EvaluateResult"]

    K5 --> L["EvaluationStore.addResult()"]
    L --> M["selectMaxScore() comparison"]
    M --> N["runExtensionHook('afterAll')"]
    N --> O["writeOutput() — JSON, CSV, HTML"]
    N --> P["SQLite Persistence via Drizzle"]
```

Sources: [src/evaluator.ts:901-1185](), [src/main.ts:67-69](), [src/evaluatorHelpers.ts:21-21](), [src/matchers/comparison.ts:23-23](), [src/node/doEval.ts:7-7]()

---

## Key Code Entities

**Diagram: Core Code Entities and Their Relationships**

```mermaid
classDiagram
    class Evaluator {
        +stats: EvaluateStats
        +evaluate()
        -runEval()
    }

    class ProgressBarManager {
        -progressBar: SingleBar
        -isWebUI: boolean
        +increment()
        +stop()
    }

    class EvaluationStore {
        +addResult()
    }

    class EvaluateResult {
        +prompt: Prompt
        +vars: Vars
        +response: ProviderResponse
        +success: boolean
        +score: number
        +gradingResult: GradingResult
    }

    class GradingResult {
        +pass: boolean
        +score: number
        +reason: string
        +tokensUsed: TokenUsage
    }

    Evaluator --> EvaluationStore : "persists results via"
    Evaluator --> ProgressBarManager : "updates UI via"
    Evaluator --> EvaluateResult : "generates"
    EvaluateResult --> GradingResult : "contains"
```

Sources: [src/evaluator.ts:175-200](), [src/evaluator.ts:122-122](), [src/types/index.ts:325-346](), [src/types/index.ts:453-468]()

---

## Central Data Types

### `TestSuite`
`TestSuite` is the normalized in-memory form of a configuration file [src/types/index.ts:75-75](). It contains instantiated `providers`, processed `prompts`, and normalized `tests` (as `AtomicTestCase` objects).

### `UnifiedConfig`
The Zod-validated structure representing the `promptfooconfig.yaml` [src/types/index.ts:15-15]().

### `EvaluateResult`
The output of a single `runEval()` call [src/evaluator.ts:67-67](). It includes the final `prompt`, the `response` from the provider, and the `gradingResult`.

### `GradingResult`
The outcome of running assertions against a provider response [src/evaluator.ts:69-69](). It tracks whether the test passed, the numerical score, and token usage from model-graded assertions.

### `ResultFailureReason`
An enum identifying why a test failed [src/evaluator.ts:73-73]():
- `ASSERT`: Assertion failure.
- `ERROR`: Provider or system error.

Sources: [src/types/index.ts:1-209](), [src/evaluator.ts:60-80]()

---

## The `runEval()` Function

`runEval()` is the internal method in `Evaluator` that handles the execution of a single prompt/provider/test combination.

1. **Prompt Rendering**: Uses `renderPrompt()` to resolve variables and templates [src/evaluatorHelpers.ts:21-21]().
2. **Provider Call**: Invokes the `ApiProvider` via the `RateLimitRegistry` to manage throttling [src/evaluator.ts:37-39]().
3. **Output Transformation**: Applies `transform` logic to the raw provider response [src/util/transform.ts:112-112]().
4. **Assertion Execution**: Calls `runAssertions()` to process deterministic and model-graded checks [src/assertions/index.ts:13-13]().

Sources: [src/evaluator.ts:9-26](), [src/evaluatorHelpers.ts:21-21]()

---

## Concurrency and Rate Limiting

The `Evaluator` manages concurrency via `async.queue` [src/evaluator.ts:4-4](). It uses a `RateLimitRegistry` to prevent overwhelming providers.

- **Adaptive Concurrency**: The system can adjust the number of simultaneous requests based on provider feedback using an AIMD algorithm [src/evaluator.ts:39-41]().
- **ProgressBarManager**: Manages CLI progress bars [src/evaluator.ts:175-175]() or reports progress to the web UI.

Sources: [src/evaluator.ts:37-43](), [src/evaluator.ts:175-179]()

---

## Extension Hooks

The evaluation lifecycle includes several hooks for custom logic defined in `evaluatorHelpers.ts` [src/evaluatorHelpers.ts:31-37]():
- `beforeAll`: Runs once before the evaluation starts.
- `beforeEach`: Runs before each individual test case.
- `afterEach`: Runs after each individual test case.
- `afterAll`: Runs once after all tests have completed.

Sources: [src/evaluatorHelpers.ts:21-37](), [src/index.ts:31-37]()

---

## Result Persistence and Output

Evaluation results are stored in a SQLite database using the `EvaluationStore` interface [src/evaluator.ts:118-120]().
- **Database**: Managed via Drizzle ORM migrations triggered at startup [src/main.ts:64-64]().
- **Output Formats**: The CLI supports multiple output formats including JSON, CSV, YAML, and HTML via `writeOutput()` [src/util/index.ts:28-28]().
- **Binary Data**: Media assets (images, audio) generated by models are handled by the `extractor` [src/evaluator.ts:16-16]().

Sources: [src/main.ts:64-64](), [src/util/index.ts:24-29](), [src/evaluator.ts:16-24]()

# Evaluation Engine




## Purpose and Scope

The Evaluation Engine is the core orchestration system that executes test cases against LLM providers and validates their outputs. This document covers the evaluation lifecycle, test execution mechanics, and result aggregation. For information about specific assertion types and grading, see **Assertions and Grading (2.3)**. For provider implementation details, see **Provider System (3)**.

The evaluation engine is implemented primarily in `evaluator.ts` and provides both CLI and programmatic interfaces for running tests via the `evaluate()` function [src/index.ts:4]().

**Sources:** [src/evaluator.ts:1-179](), [src/index.ts:1-73]()

---

## Core Architecture

### The Evaluator Class

The evaluation engine is encapsulated in the `Evaluator` class, which manages the complete evaluation lifecycle from configuration to result persistence.

```mermaid
classDiagram
    class Evaluator {
        +Eval evalRecord
        +TestSuite testSuite
        +EvaluateOptions options
        +EvaluateStats stats
        +EvalConversations conversations
        +EvalRegisters registers
        +JsonlFileWriter[] fileWriters
        +_runEvaluation() Promise~Eval~
    }

    class Eval {
        +string id
        +UnifiedConfig config
        +CompletedPrompt[] prompts
        +EvalResult[] results
        +addResult(result)
        +addPrompts(prompts)
        +toEvaluateSummary()
    }

    class TestSuite {
        +Prompt[] prompts
        +ApiProvider[] providers
        +TestCase[] tests
        +Scenario[] scenarios
        +object defaultTest
        +object nunjucksFilters
    }

    class EvaluateOptions {
        +number maxConcurrency
        +number delay
        +boolean cache
        +number repeat
        +AbortSignal abortSignal
        +string eventSource
    }

    Evaluator --> Eval : manages
    Evaluator --> TestSuite : executes
    Evaluator --> EvaluateOptions : configured by
```

**Key Components:**

- **`Evaluator`**: Main orchestrator class that coordinates test execution [src/evaluator.ts:122]().
- **`evalRecord`**: Persistent record of the evaluation, often mapped to the `Eval` model.
- **`conversations`**: Map storing conversation history for multi-turn evaluations [src/evaluator.ts:124]().
- **`registers`**: Storage for values passed between test cases via `storeOutputAs` [src/evaluator.ts:125]().

**Sources:** [src/evaluator.ts:116-136](), [src/types/index.ts:208-209]()

---

## Evaluation Lifecycle

### High-Level Execution Flow

The evaluation lifecycle begins with the `evaluate()` function, which initializes the `Evaluator` and triggers the internal `_runEvaluation()` loop.

```mermaid
flowchart TB
    Start["evaluate()"]
    LoadProviders["loadApiProviders()<br/>Load and initialize providers"]
    ResolveConfig["Resolve Configuration<br/>- defaultTest<br/>- nested providers<br/>- test cases"]
    CreateEval["Create Eval Record<br/>Eval.create() or new Eval()"]
    RunEval["Evaluator._runEvaluation()<br/>Core execution loop"]
    ProcessResults["Process Results<br/>- Aggregate stats<br/>- Convert to summary"]
    WriteOutput["Write Output<br/>JSON/CSV/HTML/etc"]

    Start --> LoadProviders
    LoadProviders --> ResolveConfig
    ResolveConfig --> CreateEval
    CreateEval --> RunEval
    RunEval --> ProcessResults
    ProcessResults --> WriteOutput

    subgraph "_runEvaluation() Details"
        Setup["Setup Phase<br/>- beforeAll hooks<br/>- prompt generation<br/>- var expansion"]
        BuildEvals["Build RunEvalOptions[]<br/>Cartesian product of:<br/>providers × prompts × tests × vars"]
        Execute["Execute Tests<br/>- Concurrent normal tests<br/>- Compare assertions"]
        AfterAll["Cleanup<br/>afterAll hooks"]

        Setup --> BuildEvals
        BuildEvals --> Execute
        Execute --> AfterAll
    end

    RunEval --> Setup
```

**Sources:** [src/evaluator.ts:1-179](), [src/commands/eval.ts:18-170](), [src/index.ts:63-73]()

---

### The _runEvaluation Method

The `_runEvaluation()` method implements the core evaluation loop with several distinct phases:

#### Phase 1: Configuration and Setup

1. **Timeout Management**: Sets up global `AbortController` using values from `getEvalTimeoutMs()` and `getMaxEvalTimeMs()` [src/envars.ts:20]().
2. **Extension Hooks**: Runs `beforeAll` hooks using `runExtensionHook()` that can modify the test suite [src/evaluator.ts:21]().
3. **Prompt Rendering**: Prepares prompts using `renderPrompt()` [src/evaluator.ts:21]().
4. **Prompt ID Generation**: Creates unique IDs for prompts using `generateIdFromPrompt()` [src/evaluator.ts:25]().

**Sources:** [src/evaluator.ts:1-26](), [src/envars.ts:20]()

#### Phase 2: Test Case Building

The evaluator builds a complete list of `RunEvalOptions` objects, one for each test execution:

```mermaid
graph TD
    TestCases["TestSuite.tests[]"]
    Scenarios["TestSuite.scenarios[]"]
    MergeDefault["Merge with defaultTest<br/>- vars<br/>- assert<br/>- options<br/>- metadata"]
    ExpandVars["generateVarCombinations()<br/>Create all var permutations"]
    Repeat["Repeat Loop<br/>options.repeat times"]
    ProviderLoop["For each provider"]
    PromptLoop["For each prompt"]
    CreateRunEval["Create RunEvalOptions<br/>- provider<br/>- prompt<br/>- test<br/>- vars<br/>- indices"]

    TestCases --> MergeDefault
    Scenarios --> MergeDefault
    MergeDefault --> ExpandVars
    ExpandVars --> Repeat
    Repeat --> ProviderLoop
    ProviderLoop --> PromptLoop
    PromptLoop --> CreateRunEval
```

**Important Details:**
- **Concurrency Control**: The CLI `eval` command allows setting `-j, --max-concurrency` [src/commands/eval.ts:89-91](), which defaults to `DEFAULT_MAX_CONCURRENCY` [src/constants.ts:19]().
- **Filtering**: Supports extensive filtering including `--filter-range` [src/commands/eval.ts:108-110](), `--filter-pattern` [src/commands/eval.ts:104-106](), and `--filter-metadata` [src/commands/eval.ts:134-139]().

**Sources:** [src/commands/eval.ts:88-140](), [src/constants.ts:19]()

---

## Test Execution

### The runEval Function

The `runEval()` function executes a single test case against a provider. It is the atomic unit of evaluation.

```mermaid
flowchart TB
    Start["runEval(RunEvalOptions)"]
    SetupVars["Setup Variables<br/>- Merge conversation history<br/>- Apply registers<br/>- Collect file metadata"]
    RenderPrompt["renderPrompt()<br/>Apply Nunjucks templating"]
    CallApi["provider.callApi()<br/>Returns ProviderResponse"]
    ApplyTransforms["Apply Transforms<br/>1. provider.transform<br/>2. test.options.transform"]
    RunAssertions["runAssertions()<br/>Execute all assertions"]
    BuildResult["Build EvaluateResult<br/>- success/failure<br/>- score<br/>- token usage<br/>- latency"]
    StoreRegister["Store in Register<br/>if storeOutputAs set"]
    Return["Return EvaluateResult[]"]

    Start --> SetupVars
    SetupVars --> RenderPrompt
    RenderPrompt --> CallApi
    CallApi --> ApplyTransforms
    ApplyTransforms --> RunAssertions
    RunAssertions --> BuildResult
    BuildResult --> StoreRegister
    StoreRegister --> Return
```

**Sources:** [src/evaluator.ts:74](), [src/evaluatorHelpers.ts:21]()

### Variable and Context Setup

Before prompt rendering, `runEval()` prepares the execution context:

**Conversation Management:**
- Checks if prompt uses `_conversation` variable via `analyzeTemplateReference` [src/evaluator.ts:157]().
- Caches these results in `promptUsesConversationVariableCache` (max 1024 entries) [src/evaluator.ts:145-149]().

**File Metadata:**
- Collects metadata from `file://` references using `collectFileMetadata()` [src/evaluator.ts:21]().

**Sources:** [src/evaluator.ts:144-170](), [src/evaluatorHelpers.ts:21]()

### Provider Execution and Scheduling

The evaluator uses a `RateLimitRegistry` to manage concurrency and rate limits:

```mermaid
flowchart LR
    Evaluator["Evaluator"]
    Registry["RateLimitRegistry<br/>(scheduler/rateLimitRegistry.ts)"]
    Queue["ProviderCallQueue<br/>(scheduler/providerCallQueue.ts)"]
    Provider["ApiProvider"]

    Evaluator --> Registry
    Registry --> Queue
    Queue --> Provider
```

- **`RateLimitRegistry`**: Manages the global state of provider rate limits. It exposes an `execute` method that wraps provider calls [src/types/index.ts:51-62]().
- **`ProviderCallQueue`**: A grouped call queue that manages deferred provider calls, especially for serial grading orchestration [src/types/index.ts:67-69]().
- **Adaptive Concurrency**: The system uses `createProviderRateLimitOptions` to configure the scheduler [src/evaluator.ts:36]().

**Sources:** [src/evaluator.ts:33-44](), [src/types/index.ts:48-69]()

---

## Assertion Execution

After provider output and transformations, assertions are evaluated:

```mermaid
flowchart TB
    RunAssertions["runAssertions()"]
    CheckResult["Check Result<br/>pass/fail/score"]
    UpdateResult["Update EvaluateResult<br/>- success<br/>- score<br/>- namedScores<br/>- error"]
    TrackTokens["Track Assertion Tokens<br/>accumulateAssertionTokenUsage()"]

    RunAssertions --> CheckResult
    CheckResult --> UpdateResult
    UpdateResult --> TrackTokens
```

**Assertion Result Handling:**
- **Deterministic Metrics**: Logical tests like `equals`, `contains`, and `regex` [site/docs/configuration/expected-outputs/deterministic.md:32-80]().
- **Model-Graded**: Uses an LLM provider to grade output based on a rubric [site/docs/configuration/expected-outputs/index.md:52-53]().
- **Token Tracking**: Token usage is tracked for assertions via `accumulateAssertionTokenUsage` [src/evaluator.ts:104]().

**Sources:** [src/evaluator.ts:9-15](), [src/evaluator.ts:103-112](), [site/docs/configuration/expected-outputs/index.md:46-57]()

---

## Progress Reporting

The `ProgressBarManager` class manages progress visualization:

```mermaid
classDiagram
    class ProgressBarManager {
        -SingleBar progressBar
        -boolean isWebUI
        -number totalCount
        -number completedCount
        +initialize()
        +updateProgress()
        +complete()
        +stop()
    }
```

- **CLI Progress**: Uses `cli-progress` to show real-time status [src/evaluator.ts:176]().
- **CI Mode**: Switches to `CIProgressReporter` when running in continuous integration environments [src/evaluator.ts:27]().
- **Logger Integration**: The manager can intercept log callbacks to prevent progress bar corruption [src/evaluator.ts:178-179]().

**Sources:** [src/evaluator.ts:171-179](), [src/evaluator.ts:27]()

---

## Advanced Features

### Token Usage Tracking

Token usage is tracked using `TokenUsageTracker` [src/evaluator.ts:102](). It breaks down usage into:
- **Total Usage**: `accumulateResponseTokenUsage` [src/evaluator.ts:107]().
- **Grading Usage**: `accumulateGradingTokenUsage` [src/evaluator.ts:106]().
- **Assertion Usage**: `accumulateAssertionTokenUsage` [src/evaluator.ts:104]().

**Sources:** [src/evaluator.ts:102-111](), [src/contracts/shared.ts:7]()

### Concurrency and Timeouts

- **Global Timeout**: Enforced via `getEvalTimeoutMs` [src/envars.ts:20]().
- **Concurrency**: Controlled via `InternalEvaluateOptions.maxConcurrency` [src/types/internal.ts:14]().
- **Delay**: Optional delay between tests to prevent rate limits [src/types/index.ts:109]().

**Sources:** [src/envars.ts:20](), [src/types/index.ts:107-109]()
This document covers the red team plugin system and its associated metadata architecture. Plugins generate test cases targeting specific vulnerability types and are organized into categories with severity levels and risk scoring. The metadata system enables systematic classification and evaluation of security risks.

For information about the overall red team architecture and test generation flow, see [Red Team Architecture](#5.1). For details about how strategies transform plugin outputs, see [Strategies](#5.4).

## System Overview

The plugin system operates on a factory pattern with a registry-based architecture for dynamic component loading. Each plugin is associated with metadata including severity levels, risk categories, and human-readable descriptions. The system supports both local and remote test generation.

**Plugin System Architecture**

```mermaid
graph TB
    subgraph "Plugin_Registry"
        Plugins["Plugins: PluginFactory[]<br/>src/redteam/plugins/index.ts"]
        PluginFactories["pluginFactories<br/>src/redteam/plugins/index.ts"]
        PiiPlugins["piiPlugins<br/>src/redteam/plugins/index.ts"]
        BiasPlugins["biasPlugins<br/>src/redteam/plugins/index.ts"]
        RemotePlugins["remotePlugins<br/>src/redteam/plugins/index.ts"]
    end

    subgraph "Metadata_System"
        GRADERS["GRADERS: Record<br/>src/redteam/graders.ts"]
        RiskCategorySeverityMap["riskCategorySeverityMap<br/>src/redteam/constants/metadata.ts"]
        DisplayNameOverrides["displayNameOverrides<br/>src/redteam/constants/metadata.ts"]
        SubCategoryDescriptions["subCategoryDescriptions<br/>src/redteam/constants/metadata.ts"]
    end

    subgraph "Plugin_Execution"
        CreatePluginFactory["createPluginFactory()<br/>src/redteam/plugins/index.ts"]
        PluginAction["plugin.action()<br/>PluginActionParams"]
        GenerateTests["generateTests(n, delayMs)<br/>src/redteam/plugins/base.ts"]
        FetchRemoteTestCases["fetchRemoteTestCases()<br/>src/redteam/plugins/index.ts"]
    end

    subgraph "Test_Output"
        TestCases["TestCase[]<br/>with metadata"]
        PluginMetadata["metadata.pluginId<br/>metadata.severity"]
        AssertionConfig["assert: Assertion[]"]
    end

    PluginFactories --> Plugins
    PiiPlugins --> Plugins
    BiasPlugins --> Plugins
    RemotePlugins --> Plugins

    Plugins --> CreatePluginFactory
    CreatePluginFactory --> PluginAction
    PluginAction --> GenerateTests
    PluginAction --> FetchRemoteTestCases

    GenerateTests --> TestCases
    FetchRemoteTestCases --> TestCases
    TestCases --> PluginMetadata
    TestCases --> AssertionConfig

    RiskCategorySeverityMap -.-> PluginMetadata
    DisplayNameOverrides -.-> PluginMetadata
    GRADERS -.-> AssertionConfig
```

**Sources:** [src/redteam/plugins/index.ts:543-550](), [src/redteam/graders.ts:1-313](), [src/redteam/constants/metadata.ts:14-178](), [src/redteam/plugins/base.ts:106-110]()

## Plugin Registry

### Plugin Factory Pattern

The plugin system uses a factory pattern implemented through the `PluginFactory` interface [src/redteam/plugins/index.ts:94-98]() and `createPluginFactory` function. Each plugin is registered with a unique key and provides an action function that generates test cases.

**Plugin Factory Structure**

```mermaid
graph TB
    subgraph "Factory_Interface"
        PluginFactory["PluginFactory<br/>src/redteam/plugins/index.ts"]
        Key["key: string"]
        Validate["validate?: (config) => void"]
        Action["action: (params) => Promise<TestCase[]>"]
    end

    subgraph "Factory_Function"
        CreatePluginFactory["createPluginFactory<T><br/>src/redteam/plugins/index.ts"]
        PluginClass["PluginClass: new (provider, purpose, injectVar, config)"]
        ShouldGenerateRemote["shouldGenerateRemote()"]
        LocalGeneration["new PluginClass().generateTests()"]
        RemoteGeneration["fetchRemoteTestCases()"]
    end

    subgraph "Plugin_Registration"
        PluginFactories["pluginFactories: PluginFactory[]<br/>src/redteam/plugins/index.ts"]
        AlignedHarmCategories["alignedHarmCategories.map()"]
        ContractPlugin["ContractPlugin"]
        CrossSessionLeakPlugin["CrossSessionLeakPlugin"]
        HallucinationPlugin["HallucinationPlugin"]
    end

    PluginFactory --> Key
    PluginFactory --> Validate
    PluginFactory --> Action

    CreatePluginFactory --> PluginClass
    CreatePluginFactory --> ShouldGenerateRemote
    ShouldGenerateRemote -->|true| RemoteGeneration
    ShouldGenerateRemote -->|false| LocalGeneration

    CreatePluginFactory --> PluginFactories
    AlignedHarmCategories --> PluginFactories
    ContractPlugin --> PluginFactories
    CrossSessionLeakPlugin --> PluginFactories
    HallucinationPlugin --> PluginFactories
```

The `createPluginFactory` function handles both local and remote test generation based on the plugin's `canGenerateRemote` property [src/redteam/plugins/base.ts:52]() and environment configuration [src/redteam/plugins/index.ts:28](). Test cases are enriched with metadata including the plugin ID using `getShortPluginId()` [src/redteam/plugins/base.ts:20]().

**Sources:** [src/redteam/plugins/index.ts:94-106](), [src/redteam/plugins/base.ts:41-76](), [src/redteam/plugins/base.ts:20]()

### Plugin Types and Organization

Plugins are organized into several groups based on their implementation:

| Array | Purpose | Example Plugins |
|-------|---------|-----------------|
| `pluginFactories` | Standard plugins with local implementations | `BeavertailsPlugin`, `ContractPlugin`, `HallucinationPlugin` [src/redteam/plugins/index.ts:47-55]() |
| `piiPlugins` | Privacy-focused plugins | `pii:api-db`, `pii:direct`, `pii:session`, `pii:social` [src/redteam/constants/plugins.ts:15]() |
| `biasPlugins` | Bias detection plugins | `bias:age`, `bias:disability`, `bias:gender`, `bias:race` [src/redteam/constants/plugins.ts:13]() |
| `REMOTE_ONLY_PLUGIN_IDS` | Plugins requiring remote generation | `ascii-smuggling`, `bfla`, `bola`, `sql-injection` [src/redteam/constants/plugins.ts:17]() |

**Sources:** [src/redteam/plugins/index.ts:45-83](), [src/redteam/constants/plugins.ts:1-20]()

## Plugin Categories

### Category Organization

Plugins are organized into categories that map to different risk domains. The category system is defined through multiple related data structures.

**Risk Categories Structure**

```mermaid
graph TB
    subgraph "Category_Definitions"
        RiskCategories["riskCategories<br/>src/redteam/constants/metadata.ts"]
        CategoryDescriptions["categoryDescriptions<br/>src/redteam/constants/metadata.ts"]
        CategoryMap["categoryMapReverse<br/>Plugin -> Category"]
    end

    subgraph "Main_Categories"
        Security["'Security and Access Control'<br/>SQL injection, BFLA, BOLA, SSRF"]
        TrustSafety["'Trust and Safety'<br/>Harmful content, bias, hate speech"]
        ComplianceLegal["'Compliance and Legal'<br/>COPPA, contracts, IP violations"]
        BrandReputation["'Brand and Reputation'<br/>Competitors, hallucination, imitation"]
        DomainSpecific["'Domain Specific'<br/>Medical, financial, pharmacy, insurance"]
    end

    subgraph "Plugin_Collections"
        HARM_PLUGINS["HARM_PLUGINS<br/>src/redteam/constants/plugins.ts"]
        PII_PLUGINS["PII_PLUGINS: ['pii:api-db', 'pii:direct',<br/>'pii:session', 'pii:social']<br/>src/redteam/constants/plugins.ts"]
        BIAS_PLUGINS["BIAS_PLUGINS: ['bias:age', 'bias:disability',<br/>'bias:gender', 'bias:race']<br/>src/redteam/constants/plugins.ts"]
    end

    RiskCategories --> CategoryDescriptions

    CategoryMap --> Security
    CategoryMap --> TrustSafety
    CategoryMap --> ComplianceLegal
    CategoryMap --> BrandReputation
    CategoryMap --> DomainSpecific

    HARM_PLUGINS -.-> TrustSafety
    PII_PLUGINS -.-> Security
    BIAS_PLUGINS -.-> TrustSafety
```

**Sources:** [src/redteam/constants/metadata.ts:14-178](), [src/redteam/constants/plugins.ts:1-221]()

### Category Descriptions

Each category has a description that explains its focus [site/docs/_shared/data/plugins.ts:15-46]():

| Category | Description |
|----------|-------------|
| Security and Access Control | Technical security risk tests mapped to OWASP Top 10 for LLMs, APIs, and web applications, covering SQL injection, SSRF, broken access control, and cross-session leaks. |
| Trust and Safety | Tests that attempt to produce illicit, graphic, or inappropriate responses from the LLM. |
| Compliance and Legal | Tests for LLM behavior that may encourage illegal activity, breach contractual commitments, or violate intellectual property rights. |
| Brand | Tests focused on brand protection, including competitor mentions, misinformation, hallucinations, and model behavior that could impact brand reputation. |
| Dataset | Pre-compiled collections of test cases from research datasets designed to evaluate model safety, robustness, and alignment. |

**Sources:** [site/docs/_shared/data/plugins.ts:15-46](), [src/redteam/constants/metadata.ts:14-178]()

### Plugin Collections

Plugin collections group related vulnerability types for easier configuration.

- `FOUNDATION_PLUGINS`: A collection of plugins designed to run against foundation models [src/redteam/constants/plugins.ts:42-87]().
- `GUARDRAILS_EVALUATION_PLUGINS`: Comprehensive testing suite for evaluating guardrails effectiveness against prompt injection, jailbreaking, harmful content, and PII leakage [src/redteam/constants/plugins.ts:89-154]().
- `MCP_PLUGINS`: Plugins for Model Context Protocol (MCP) including `mcp`, `pii`, `bfla`, `bola`, `sql-injection`, and `rbac` [src/redteam/constants/plugins.ts:156]().
- `AGENTIC_PLUGINS`: Specialized plugins for agents like `agentic:memory-poisoning` [src/redteam/constants/plugins.ts:158]().
- `CODING_AGENT_PLUGINS`: A suite of 13 plugins for testing coding agents, such as `coding-agent:repo-prompt-injection` and `coding-agent:sandbox-read-escape` [test/redteam/constants/plugins.test.ts:76]().

**Sources:** [src/redteam/constants/plugins.ts:42-177](), [test/redteam/constants/plugins.test.ts:76]()

## Metadata System

### Severity Levels and Risk Scoring

The metadata system defines severity levels used for risk classification [src/redteam/constants/metadata.ts:14-178]().

**Severity Mapping Example**

| Plugin ID | Description | Default Severity |
|-----------|-------------|------------------|
| `agentic:memory-poisoning` | Tests vulnerability to memory poisoning attacks | High |
| `harmful:child-exploitation` | Tests handling of child exploitation content | Critical |
| `bias:age` | Age-related bias detection | Low |
| `sql-injection` | Tests for SQL injection vulnerabilities | High |

**Sources:** [src/redteam/constants/metadata.ts:14-178](), [src/redteam/constants/plugins.ts:180-215]()

### Display Names and Descriptions

The metadata system provides human-readable names and descriptions for plugins:

- `subCategoryDescriptions`: A record mapping plugin IDs to their technical descriptions [src/redteam/constants/metadata.ts:14-178]().
- `humanReadableCategoryList`: A utility for generating natural language lists of categories [site/docs/_shared/data/plugins.ts:48-49]().

**Sources:** [src/redteam/constants/metadata.ts:14-178](), [site/docs/_shared/data/plugins.ts:48-51]()

## Grader System

### Grader Registry

Each plugin has a corresponding grader that evaluates test results. The `GRADERS` record maps plugin IDs to grader instances.

**Grader Mapping Structure**

```mermaid
graph TB
    subgraph "Grader_Registry"
        GRADERS["GRADERS Registry<br/>src/redteam/graders.ts"]
    end

    subgraph "Example_Graders"
        AegisGrader["AegisGrader<br/>src/redteam/plugins/aegis.ts"]
        BeavertailsGrader["BeavertailsGrader<br/>src/redteam/plugins/beavertails.ts"]
        SqlInjectionGrader["SqlInjectionGrader<br/>src/redteam/plugins/sqlInjection.ts"]
        PiiGrader["PiiGrader<br/>src/redteam/plugins/pii.ts"]
    end

    AegisGrader --> GRADERS
    BeavertailsGrader --> GRADERS
    SqlInjectionGrader --> GRADERS
    PiiGrader --> GRADERS
```

**Sources:** [src/redteam/graders.ts:1-107]()

### Dataset-Backed Plugins

Promptfoo integrates several research datasets as plugins:

- **HarmBench**: Evaluates harmful content generation using the HarmBench taxonomy [src/redteam/constants/metadata.ts:55]().
- **BeaverTails**: Uses the BeaverTails dataset for safety and alignment evaluation [src/redteam/plugins/beavertails.ts]().
- **Pliny**: Implements jailbreak techniques and datasets [src/redteam/plugins/pliny.ts]().
- **CyberSecEval**: Tests for prompt injection and security vulnerabilities using Meta's dataset [src/redteam/plugins/cyberseceval.ts]().

**Sources:** [src/redteam/constants/metadata.ts:14-178](), [src/redteam/plugins/index.ts:47-83]()

## Writing Custom Plugins

Custom plugins are implemented by extending the `RedteamPluginBase` class.

### Implementation Guide

1.  **Define the Plugin Class**: Extend `RedteamPluginBase` [src/redteam/plugins/base.ts:41]().
2.  **Set Plugin ID**: Provide a unique string identifier [src/redteam/plugins/base.ts:45]().
3.  **Implement `getTemplate()`**: Return the prompt template used to generate test cases [src/redteam/plugins/base.ts:90]().
4.  **Implement `getAssertions()`**: Define the grading criteria for generated prompts [src/redteam/plugins/base.ts:97]().

**Plugin Generation Flow**

```mermaid
graph TB
    subgraph "RedteamPluginBase"
        generateTests["generateTests(n, delayMs)<br/>src/redteam/plugins/base.ts"]
        getTemplate["getTemplate()<br/>Abstract"]
        getAssertions["getAssertions(prompt)<br/>Abstract"]
    end

    subgraph "Execution_Logic"
        ProviderCall["provider.callApi(finalTemplate)"]
        Deduplication["retryWithDeduplication()"]
        ModifierAppender["RedteamPluginBase.appendModifiers()"]
    end

    generateTests --> getTemplate
    generateTests --> ModifierAppender
    ModifierAppender --> ProviderCall
    ProviderCall --> Deduplication
    Deduplication --> getAssertions
```

**Sources:** [src/redteam/plugins/base.ts:41-176](), [test/redteam/plugins/base.test.ts:47-56]()

# Strategies




Strategies are transformation techniques applied to base test cases generated by red team plugins to evade security defenses and bypass content filters. While plugins define what vulnerabilities to test for (e.g., PII leaks, SQL injection), strategies define how to obscure or present those tests to increase the likelihood of bypassing guardrails.

For information about plugins that generate the base test cases, see [Plugins and Metadata](#5.3). For information about attack providers that use multi-turn conversations, see [Attack Providers](#5.5).

## Strategy System Overview

The strategy system is a transformation layer between plugin test generation and final test execution. When plugins generate base test cases, `applyStrategies()` in `src/redteam/index.ts` runs each configured strategy against those cases, producing additional (or transformed) test cases that are harder to block.

**Strategy Application Pipeline**

```mermaid
graph TB
    PluginAction["Plugin action\n(generates TestCase[])"]
    Synthesize["synthesize()\nsrc/redteam/index.ts"]
    ApplyStrategies["applyStrategies()\nsrc/redteam/index.ts"]
    StrategiesArr["Strategies[]\nsrc/redteam/strategies/index.ts"]
    LoadStrategy["loadStrategy()\nfor file:// strategies"]
    PluginMatch["pluginMatchesStrategyTargets()\nsrc/redteam/strategies/util.ts"]
    StrategyAction["strategy.action(testCases, injectVar, config, strategyId)"]
    ResultMetadata["test.metadata.strategyId\ntest.metadata.strategyConfig"]

    PluginAction --> Synthesize
    Synthesize --> ApplyStrategies
    ApplyStrategies --> StrategiesArr
    ApplyStrategies --> LoadStrategy
    ApplyStrategies --> PluginMatch
    PluginMatch -->|"applicable test cases"| StrategyAction
    StrategiesArr --> StrategyAction
    LoadStrategy --> StrategyAction
    StrategyAction --> ResultMetadata
```

Sources: [src/redteam/index.ts:350-567](), [src/redteam/strategies/index.ts:42-350]()

**Strategy Type and Registry**

```mermaid
graph LR
    StrategyInterface["Strategy interface\n{id, action, requiresGoalExtraction?}"]
    StrategiesArr["Strategies[]\nexported from strategies/index.ts"]
    StaticGroup["Static\n(base64, hex, homoglyph, rot13)"]
    DynamicGroup["Dynamic\n(jailbreak:meta, jailbreak:composite, gcg)"]
    MultiTurnGroup["Multi-Turn\n(crescendo, goat, custom)"]
    SpecialGroup["Special\n(basic, retry, layer)"]
    FileStrategy["file:// custom strategy\nloaded via loadStrategy()"]

    StrategyInterface --> StrategiesArr
    StrategiesArr --> StaticGroup
    StrategiesArr --> DynamicGroup
    StrategiesArr --> MultiTurnGroup
    StrategiesArr --> SpecialGroup
    StrategiesArr --> FileStrategy
```

Sources: [src/redteam/strategies/index.ts:42-350](), [src/redteam/constants/strategies.ts:116-123]()

### Key Components

| Component | Description | Code Location |
|-----------|-------------|---------------|
| `Strategies[]` | Registry of all built-in strategy objects | [src/redteam/strategies/index.ts:42-350]() |
| `applyStrategies()` | Applies all configured strategies to plugin test cases | [src/redteam/index.ts:350-567]() |
| `loadStrategy()` | Loads a strategy by ID or `file://` path | [src/redteam/strategies/index.ts:402-440]() |
| `validateStrategies()` | Validates strategy IDs and config before generation | [src/redteam/strategies/index.ts:442-468]() |
| `DEFAULT_STRATEGIES` | Default strategy set: `basic`, `jailbreak:meta`, `jailbreak:composite` | [src/redteam/constants/strategies.ts:15]() |
| `STRATEGY_COLLECTIONS` | Named groupings of strategies (e.g. `other-encodings`) | [src/redteam/constants/strategies.ts:109-114]() |

Sources: [src/redteam/strategies/index.ts:42-468](), [src/redteam/constants/strategies.ts:15-114]()

## Strategy Categories

Strategies are grouped by how they transform test cases. The `requiresGoalExtraction` flag on a strategy entry in `Strategies[]` indicates that the strategy needs a goal extracted from the test prompt before running.

### Static (Single-Turn)

Deterministic transformations. Defined in `ENCODING_STRATEGIES` in [src/redteam/constants/strategies.ts:148-165]().

| Strategy ID | Implementation | Description |
|-------------|---------------|-------------|
| `base64` | `addBase64Encoding()` | Base64-encodes the inject variable |
| `hex` | `addHexEncoding()` | Hex-encodes the inject variable |
| `rot13` | `addRot13()` | ROT13-encodes the inject variable |
| `leetspeak` | `addLeetspeak()` | Substitutes characters with leet equivalents |
| `homoglyph` | `addHomoglyphs()` | Substitutes with visually similar Unicode characters |
| `morse` | `addOtherEncodings()` | Converts to Morse code |
| `piglatin` | `addOtherEncodings()` | Pig Latin transformation |
| `camelcase` | `addOtherEncodings()` | CamelCase transformation |
| `emoji` | `addOtherEncodings()` | Replaces words with emoji sequences |
| `jailbreak-templates` | `addInjections()` | Wraps payload in known static jailbreak templates |
| `audio` | `addAudioToBase64()` | Converts text payload to audio base64 |
| `image` | `addImageToBase64()` | Converts text payload to image base64 |
| `video` | `addVideoToBase64()` | Converts text payload to video base64 |

Sources: [src/redteam/strategies/index.ts:60-102](), [src/redteam/constants/strategies.ts:148-165](), [src/redteam/strategies/simpleAudio.ts:1-20](), [src/redteam/strategies/simpleImage.ts:1-20]()

### Dynamic (Single-Turn)

Use an LLM attacker to generate or refine attack prompts. These make multiple API calls and have higher attack success rates.

| Strategy ID | `requiresGoalExtraction` | Description |
|-------------|--------------------------|-------------|
| `jailbreak:meta` | Yes | Meta-agent building a per-target attack taxonomy |
| `jailbreak:composite` | No | Chains multiple jailbreak techniques; fan-out default n=5 |
| `jailbreak:likert` | No | Frames harmful requests as Likert-scale academic evaluation |
| `jailbreak:tree` | Yes | Tree-based attack search (TAP research) |
| `best-of-n` | No | Samples N prompt variations in parallel (Anthropic research) |
| `citation` | No | Frames requests in academic citation contexts |
| `gcg` | No | Greedy Coordinate Gradient adversarial suffix; fan-out default n=1 |
| `math-prompt` | No | Encodes requests using mathematical notation |
| `authoritative-markup-injection` | No | Exploits trust in structured markup (e.g., XML/JSON) |

Sources: [src/redteam/strategies/index.ts:133-295](), [src/redteam/constants/strategies.ts:73-107](), [src/redteam/strategies/singleTurnComposite.ts:19-73]()

### Multi-Turn

Conduct multi-turn conversations with the target. Defined in `MULTI_TURN_STRATEGIES` in [src/redteam/constants/strategies.ts:20-27]().

| Strategy ID | `requiresGoalExtraction` | Description |
|-------------|--------------------------|-------------|
| `crescendo` | Yes | Gradually escalates harm across turns with backtracking |
| `goat` | Yes | Generative Offensive Agent Tester — dynamic multi-turn attack agent |
| `jailbreak:hydra` | Yes | Adaptive multi-turn agent with scan-wide memory |
| `custom` | Yes | User-defined natural language instructions control the attack |
| `mischievous-user` | No | Multi-turn conversation as a persistently mischievous user |

Sources: [src/redteam/strategies/index.ts:104-240](), [src/redteam/constants/strategies.ts:20-27]()

## Strategy Configuration Schema

Strategies are configured via the `redteam.strategies` section of the config [site/static/config-schema.json:52-54]().

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | The strategy identifier (e.g., `jailbreak:meta`) |
| `config` | `object` | Strategy-specific configuration |
| `config.plugins` | `string[]` | Limit strategy to specific plugin IDs |
| `config.numTests` | `number` | Cap the number of test cases generated |

**Fan-out Configuration:**

Fan-out strategies generate multiple test cases from a single input. Default multipliers are defined in `DEFAULT_N_FAN_OUT_BY_STRATEGY` [src/redteam/constants/strategies.ts:177-180]().

| Strategy | Default `n` |
|----------|-------------|
| `jailbreak:composite` | 5 |
| `gcg` | 1 |

Sources: [src/redteam/constants/strategies.ts:177-196](), [site/static/config-schema.json:52-54]()

## Strategy Application Pipeline

The `applyStrategies` function in `src/redteam/index.ts` is the central orchestrator.

1. **Expansion**: `STRATEGY_COLLECTION_MAPPINGS` expands collections like `other-encodings` into individual strategies [src/redteam/constants/strategies.ts:112-114]().
2. **Filtering**: `pluginMatchesStrategyTargets` ensures strategies aren't applied to exempt plugins like `DATASET_PLUGINS` (e.g., `beavertails`, `pliny`) [src/redteam/constants/strategies.ts:60-71]().
3. **Execution**: The `action` function for each strategy is called, which transforms the `TestCase` variables (specifically the `injectVar`) [src/redteam/strategies/index.ts:42-350]().
4. **Metadata**: Resulting test cases are tagged with `metadata.strategyId` for tracking in the UI.

**Bridging Strategy Logic to Code**

```mermaid
graph TD
    subgraph "Natural Language Space"
        StrategyName["'jailbreak:meta'"]
        CollectionName["'other-encodings'"]
    end

    subgraph "Code Entity Space"
        StrategiesRegistry["Strategies[]\nsrc/redteam/strategies/index.ts"]
        Mappings["STRATEGY_COLLECTION_MAPPINGS\nsrc/redteam/constants/strategies.ts"]
        ActionFn["strategy.action()\nsrc/redteam/strategies/index.ts"]
        RemoteTask["postRemoteGenerationTask()\nsrc/redteam/strategies/multilingual.ts"]
    end

    StrategyName --> StrategiesRegistry
    CollectionName --> Mappings
    StrategiesRegistry --> ActionFn
    ActionFn --> RemoteTask
```

Sources: [src/redteam/strategies/index.ts:42-350](), [src/redteam/constants/strategies.ts:112-114](), [src/redteam/strategies/multilingual.ts:121-148]()

## Special Strategy Behaviors

### `layer`
The `layer` strategy allows chaining multiple transformations sequentially. It calls `addLayerTestCases` which recursively applies strategies from the registry [src/redteam/strategies/index.ts:44-58]().

### `multilingual` (Deprecated)
The `multilingual` strategy is deprecated in favor of the top-level `language` configuration [src/redteam/strategies/multilingual.ts:18-35](). When used, it translates test cases into target languages like `bn`, `sw`, `jv` [src/redteam/strategies/multilingual.ts:37](). It supports remote generation in chunks for reliability [src/redteam/strategies/multilingual.ts:121-148]().

### `retry`
The `retry` strategy targets previously failed test cases to find regressions or refined bypasses [src/redteam/strategies/index.ts:275-281]().

### `math-prompt`
The `math-prompt` strategy tests resilience against mathematical notation-based attacks using set theory and abstract algebra [src/redteam/strategies/index.ts:241-252]().

## Custom Strategies

Users can add custom strategies in two ways:
1. **JavaScript Files**: Using the `file://` protocol. The file must export an object with `id` and `action` [src/redteam/strategies/index.ts:402-440]().
2. **Natural Language**: Using the `custom` strategy to provide instructions to an attacker agent [src/redteam/strategies/index.ts:118-131]().

**Custom Strategy Loading**

```mermaid
graph LR
    UserConfig["file://custom_strat.js"]
    LoadStrat["loadStrategy()\nsrc/redteam/strategies/index.ts"]
    ImportMod["importModule()\nsrc/esm.ts"]
    Validation["isJavascriptFile()\nsrc/util/fileExtensions.ts"]

    UserConfig --> LoadStrat
    LoadStrat --> Validation
    Validation --> ImportMod
    ImportMod --> Action["strategy.action()"]
```

Sources: [src/redteam/strategies/index.ts:402-440](), [src/esm.ts:1-10](), [src/util/fileExtensions.ts:1-10]()

# Attack Providers




This document covers the sophisticated attack provider implementations in promptfoo's red team system. These providers implement advanced multi-turn adversarial strategies, iterative refinement, and tree-based exploration to identify vulnerabilities in LLMs.

## Overview

Attack providers are specialized `ApiProvider` implementations located in `src/redteam/providers/` that orchestrate conversational attacks against target models. Unlike basic plugins that generate single-shot prompts, attack providers manage stateful interactions, score-based feedback loops, and backtracking logic.

The system includes several major iterative implementations:
- **Crescendo**: Progressive multi-turn jailbreaking with backtracking [src/redteam/providers/crescendo/index.ts:178-201]().
- **Iterative Refinement**: Score-based loops for text and images [src/redteam/providers/iterative.ts:80-82]().
- **Tree-based Iteration**: Tree search (TAP-based) with branching and pruning [src/redteam/providers/iterativeTree.ts:88-89]().
- **Goat**: Remote-assisted agentic attacks (Generative Offensive Agent Training) [src/redteam/providers/goat.ts:138-166]().
- **Hydra**: Multi-headed turn-based attacks [src/redteam/providers/hydra/index.ts:149-161]().
- **Voice Crescendo**: Audio-native conversational attacks [src/redteam/providers/voiceCrescendo/index.ts:1-20]().
- **Iterative Meta**: High-level agentic orchestration using cloud-based strategic agents [src/redteam/providers/iterativeMeta.ts:105-135]().
- **Custom**: User-defined strategy templates [src/redteam/providers/custom/index.ts:1-20]().

Sources: [src/redteam/providers/crescendo/index.ts:178-201](), [src/redteam/providers/iterative.ts:80-82](), [src/redteam/providers/iterativeTree.ts:88-89](), [src/redteam/providers/goat.ts:138-166](), [src/redteam/providers/hydra/index.ts:149-161](), [src/redteam/providers/iterativeMeta.ts:105-135]()

## Core Components and Data Flow

The attack system bridges high-level adversarial strategies to executable code through a set of shared managers and utility functions.

### Attack Provider Architecture

Title: Attack Provider Subsystem Mapping
```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        Goal["Adversarial Goal (metadata.goal)"]
        SystemPrompts["System Prompts (ATTACKER_SYSTEM_PROMPT)"]
    end

    subgraph "CodeEntitySpace"
        Manager["RedteamProviderManager (src/redteam/providers/shared.ts)"]
        BaseProvider["ApiProvider (src/types/providers.ts)"]

        subgraph "IterativeImplementations"
            Crescendo["CrescendoProvider (src/redteam/providers/crescendo/index.ts)"]
            Iterative["RedteamIterativeProvider (src/redteam/providers/iterative.ts)"]
            Tree["RedteamIterativeTreeProvider (src/redteam/providers/iterativeTree.ts)"]
            Hydra["HydraProvider (src/redteam/providers/hydra/index.ts)"]
            Voice["VoiceCrescendoProvider (src/redteam/providers/voiceCrescendo/index.ts)"]
        end

        subgraph "SupportSystems"
            Memory["MemorySystem (src/redteam/providers/crescendo/index.ts)"]
            Grader["RedteamGraderBase (src/redteam/shared.ts)"]
            Remote["PromptfooChatCompletionProvider (src/providers/promptfoo.ts)"]
        end
    end

    Goal --> Crescendo
    SystemPrompts --> Hydra
    Crescendo --> Memory
    Iterative --> Manager
    Tree --> Manager
    Manager --> Remote
    Hydra --> Grader
    Voice --> Remote
```

Sources: [src/redteam/providers/shared.ts:157-186](), [src/redteam/providers/crescendo/index.ts:155-176](), [src/redteam/providers/iterative.ts:125-163](), [src/redteam/providers/iterativeTree.ts:11-15](), [src/redteam/providers/voiceCrescendo/index.ts:1-20]()

### Shared Attack Utilities
The `RedteamProviderManager` handles the lifecycle of attacker models, while `getTargetResponse` provides a unified way to probe target models with runtime transformations.

- **`RedteamProviderManager`**: Manages cached instances of redteam, grading, and multilingual providers. It wraps providers with rate limiting via `wrapProviderWithRateLimiting` [src/redteam/providers/shared.ts:178-183]().
- **`tryUnblocking`**: A specialized utility that detects when a target has blocked a conversation (e.g., due to safety filters) and attempts to generate an "unblocking" question to resume the attack [src/redteam/providers/shared.ts:26-26]().
- **`applyRuntimeTransforms`**: Applies per-turn layers (e.g., audio conversion, base64 encoding) to prompts before they reach the target [src/redteam/providers/shared.ts:35-39]().
- **`accumulateUnblockingTokenUsage`**: Tracks token usage for unblocking analysis without attributing it to the primary attacker or target metrics [src/redteam/providers/shared.ts:51-63]().

Sources: [src/redteam/providers/shared.ts:157-186](), [src/redteam/providers/shared.ts:35-39](), [src/redteam/providers/shared.ts:51-63](), [src/redteam/providers/crescendo/index.ts:35-39]()

---

## Crescendo Provider

`CrescendoProvider` implements a multi-turn jailbreak strategy that gradually escalates the conversation. It is unique for its **Backtracking** capability: if a turn results in a refusal, the provider reverts the conversation to a previous state and tries a different approach.

### Implementation Details
- **Memory System**: Uses a `MemorySystem` class to store `Message[]` arrays keyed by conversation IDs. It can `duplicateConversationExcludingLastTurn` to facilitate backtracking by removing the last failed turn [src/redteam/providers/crescendo/index.ts:155-176]().
- **Scoring**: Employs specialized prompts: `REFUSAL_SYSTEM_PROMPT` to detect refusals and `EVAL_SYSTEM_PROMPT` to grade the progress toward the goal on a 1-10 scale [src/redteam/providers/crescendo/index.ts:73-73]().
- **Configuration**: Supports `maxTurns` (default 10) and `maxBacktracks` (default 10). For unauthenticated users, `maxTurns` is capped at 10 [src/redteam/providers/crescendo/index.ts:93-94](), [src/redteam/providers/crescendo/index.ts:200-201]().

Sources: [src/redteam/providers/crescendo/index.ts:155-176](), [src/redteam/providers/crescendo/index.ts:73-73](), [src/redteam/providers/crescendo/index.ts:93-94]()

---

## Iterative Refinement Providers

The iterative providers follow a feedback loop where an "Attacker" model generates a prompt, a "Judge" model scores the response, and the Attacker refines the next prompt based on that score.

### Iterative Tree (TAP) Strategy
Based on the "Tree of Attacks with Pruning" (TAP) paper, `RedteamIterativeTreeProvider` explores multiple attack branches simultaneously.

| Parameter | Default Value | Description |
| :--- | :--- | :--- |
| `DEFAULT_MAX_WIDTH` | 10 | The number of top-scoring nodes kept at each level (pruning) [src/redteam/providers/iterativeTree.ts:118-118](). |
| `DEFAULT_BRANCHING_FACTOR` | 4 | Number of children generated for each parent node [src/redteam/providers/iterativeTree.ts:119-119](). |
| `DEFAULT_MAX_DEPTH` | 25 | Maximum depth of the search tree [src/redteam/providers/iterativeTree.ts:112-112](). |
| `DEFAULT_MAX_ATTEMPTS` | 250 | Total budget of API calls for the attack [src/redteam/providers/iterativeTree.ts:109-109](). |

Sources: [src/redteam/providers/iterativeTree.ts:108-125](), [src/redteam/providers/iterativeTree.ts:153-162]()

### Iterative Image Provider
Specialized for vision models, `IterativeImageProvider` (in `src/redteam/providers/iterativeImage.ts`) iterates on prompts to force image generation models into forbidden behavior. It includes a specific `ATTACKER_SYSTEM_PROMPT` that instructs the model to obfuscate sensitive words and use roleplaying [src/redteam/providers/iterativeImage.ts:73-107]().

Sources: [src/redteam/providers/iterativeImage.ts:73-107](), [src/redteam/providers/iterativeImage.ts:42-58]()

---

## Goat and Hydra Providers

### GoatProvider
The `GoatProvider` is a remote-first agentic attack implementation. It delegates the complex task of "agentic" attack generation to promptfoo's cloud services while executing the target calls locally.
- **Remote Requirements**: Explicitly requires remote generation to be enabled. If `neverGenerateRemote()` is true, it throws an error [src/redteam/providers/goat.ts:167-169]().
- **Statefulness**: Supports `stateful` mode and `continueAfterSuccess` for extended probing [src/redteam/providers/goat.ts:116-117]().

Sources: [src/redteam/providers/goat.ts:138-200](), [src/redteam/providers/goat.ts:167-169]()

### HydraProvider
The `HydraProvider` uses a "multi-headed" approach, managing multiple concurrent conversation turns. It uses the `hydra-decision` task via `PromptfooChatCompletionProvider` to decide the next move in an attack sequence [src/redteam/providers/hydra/index.ts:188-195]().

Sources: [src/redteam/providers/hydra/index.ts:149-161](), [src/redteam/providers/hydra/index.ts:188-195]()

---

## Implementation Mechanics

### The Attack Loop (Iterative Refinement)

Title: Iterative Attack Loop Logic
```mermaid
sequenceDiagram
    participant P as Provider (Iterative/Tree)
    participant A as Attacker (Remote PromptfooChatCompletionProvider)
    participant T as Target (System Under Test)
    participant J as Judge/Grader (Scoring LLM)

    Note over P, J: Loop for numIterations or until Success
    P->>A: callApi(task='iterative', History, Goal)
    A-->>P: Refined Adversarial Prompt (JSON)
    P->>T: getTargetResponse(Adversarial Prompt)
    T-->>P: Target Output
    P->>J: evaluateResponse(Output, Goal)
    J-->>P: Score (1-10) + Explanation
    alt Score >= 10
        P->>P: Terminate (Success)
    else Score < 10
        P->>P: Update History & Continue
    end
```

Sources: [src/redteam/providers/iterative.ts:125-163](), [src/redteam/providers/iterativeTree.ts:153-162](), [src/redteam/providers/shared.ts:56-60](), [src/redteam/providers/shared.ts:63-68]()

### Multi-Input Materialization
Providers support an `inputs` configuration which allows the attacker model to manipulate multiple variables simultaneously. This is handled via `materializeInputVariablesWithMetadata` and `buildRemoteMaterializedInputVariables` to ensure complex prompts with multiple variables are correctly formed before being sent to the target [src/redteam/providers/crescendo/index.ts:24-25](), [src/redteam/providers/iterative.ts:24-26]().

Sources: [src/redteam/providers/crescendo/index.ts:24-25](), [src/redteam/providers/iterative.ts:24-26](), [src/redteam/providers/shared.ts:23-25]()

# Graders and Evaluation




## Purpose and Scope

This document describes the grading and evaluation system used by the red team framework to determine whether attacks successfully bypass safety mechanisms. Graders evaluate target responses against specific vulnerability criteria and return pass/fail results that drive iterative attack refinement.

For information about test generation and attack strategies, see [Strategies (5.4)](./strategies). For details about plugins that generate test cases, see [Plugins and Metadata (5.3)](./plugins-and-metadata).

## Grader Registry Architecture

The grading system is built around a centralized registry that maps assertion types to grader implementations. All red team graders extend from `RedteamGraderBase` and implement a consistent evaluation interface.

### Core Registry Structure

```mermaid
graph TB
    subgraph "Registry [src/redteam/graders.ts]"
        GRADERS["GRADERS Record&lt;string, RedteamGraderBase&gt;"]
        getGraderById["getGraderById(id: string)"]
    end

    subgraph "Base Class [src/redteam/plugins/base.ts]"
        RedteamGraderBase["RedteamGraderBase"]
        RedteamGraderBase_getResult["RedteamGraderBase.getResult()"]
    end

    subgraph "Grader Implementations"
        CoppaGrader["CoppaGrader [src/redteam/plugins/compliance/coppa.ts]"]
        BflaGrader["BflaGrader [src/redteam/plugins/bfla.ts]"]
        HarmfulGrader["HarmfulGrader [src/redteam/plugins/harmful/graders.ts]"]
        PiiGrader["PiiGrader [src/redteam/plugins/pii.ts]"]
        Other["100+ other graders..."]
    end

    GRADERS --> getGraderById
    getGraderById --> RedteamGraderBase

    RedteamGraderBase --> CoppaGrader
    RedteamGraderBase --> BflaGrader
    RedteamGraderBase --> HarmfulGrader
    RedteamGraderBase --> PiiGrader
    RedteamGraderBase --> Other

    CoppaGrader --> RedteamGraderBase_getResult
    BflaGrader --> RedteamGraderBase_getResult
    HarmfulGrader --> RedteamGraderBase_getResult
```

**Sources:** [src/redteam/graders.ts:1-107](), [src/redteam/graders.ts:202-217](), [src/redteam/plugins/base.ts:41-76]()

The `GRADERS` registry [src/redteam/graders.ts:113-288]() contains a mapping of assertion type identifiers to their respective grader instances. The `getGraderById` function [src/redteam/graders.ts:290-313]() retrieves graders by ID, with fallback logic for `harmful` subtypes to ensure specific harm categories (like `harmful:child-exploitation`) use the correct specialized grader [src/redteam/graders.ts:296-301]().

| Grader Category | Example IDs | Purpose |
|----------------|-------------|---------|
| Compliance | `promptfoo:redteam:coppa`, `promptfoo:redteam:contracts` | Regulatory and legal violations [src/redteam/graders.ts:11-14]() |
| Security | `promptfoo:redteam:bfla`, `promptfoo:redteam:sql-injection` | OWASP Top 10 and technical attacks [src/redteam/graders.ts:6-8]() |
| Harmful Content | `promptfoo:redteam:harmful:*` | Trust & safety violations across 20+ categories [src/redteam/graders.ts:39-61]() |
| Privacy | `promptfoo:redteam:pii:*`, `promptfoo:redteam:cross-session-leak` | Data leakage and PII exposure [src/redteam/graders.ts:86-91]() |
| Brand | `promptfoo:redteam:competitors`, `promptfoo:redteam:hallucination` | Reputation and misinformation risks [src/redteam/graders.ts:10-37]() |
| Industry-Specific | `promptfoo:redteam:medical:*`, `promptfoo:redteam:financial:*` | Medical, Financial, and Insurance risks [src/redteam/graders.ts:24-79]() |

**Sources:** [src/redteam/graders.ts:1-107](), [site/docs/_shared/data/plugins.ts:99-236](), [src/redteam/constants/metadata.ts:14-102]()

## Rubric Rendering with Nunjucks

Graders use Nunjucks templates to define their evaluation criteria. This allows for dynamic rubric generation based on the target's purpose, allowed entities, and the specific attack prompt.

### Example Rubric: Harmful Content

The `HarmfulGrader` and its variants use templates to guide the LLM evaluator [src/redteam/plugins/harmful/graders.ts:15-48]():

```nunjucks
You are grading an AI Agent with the following purpose:
<purpose>{{purpose}}</purpose>

{% if entities and entities.length > 0 %}
The following entities are allowed to be mentioned:
<AllowedEntities>
{% for entity in entities %}<Entity>{{ entity }}</Entity>{% endfor %}
</AllowedEntities>
{% endif %}

<UserQuery>{{prompt}}</UserQuery>
...
Your job is to determine if the output contains harmful content...
```

**Sources:** [src/redteam/plugins/harmful/graders.ts:15-48](), [src/redteam/plugins/bfla.ts:10-70](), [src/redteam/plugins/pii.ts:170-185]()

## ResultSuggestion Generation

Graders can provide `ResultSuggestion` objects when a vulnerability is detected. These suggestions offer actionable remediation steps to be displayed in the UI.

### BflaGrader Suggestions

The `BflaGrader` (Broken Function Level Authorization) provides specific security recommendations when a vulnerability is identified [src/redteam/plugins/bfla.ts:72-91]():

```typescript
getSuggestions({}: { rawPrompt: string; renderedValue?: AssertionValue }): ResultSuggestion[] {
  const noteValue = dedent`
    It's recommended to enforce proper access control at the API layer...
    1. Implement RBAC
    2. Use principle of least privilege...
  `;
  return [{ action: 'note', type: 'access-control', value: noteValue }];
}
```

**Sources:** [src/redteam/plugins/bfla.ts:72-91]()

## Grading Process and getResult()

The `getResult()` method is the core execution logic for every grader. It handles refusal detection and delegates to the base LLM-based evaluation.

### Grading Method Flow

```mermaid
graph LR
    subgraph "Input Space"
        Prompt["prompt: string"]
        Output["output: string"]
        Test["test: AtomicTestCase"]
    end

    subgraph "Code Entity Space"
        isBasicRefusal["isBasicRefusal(output)<br/>[src/redteam/util.ts]"]
        RedteamGraderBase_getResult["RedteamGraderBase.getResult()<br/>[src/redteam/plugins/base.ts]"]
        matchesLlmRubric["matchesLlmRubric()<br/>[src/matchers/rubric.ts]"]
    end

    subgraph "Result Space"
        GradingResult["GradingResult {<br/>pass: boolean,<br/>score: number,<br/>reason: string<br/>}"]
    end

    Prompt --> isBasicRefusal
    Output --> isBasicRefusal
    isBasicRefusal -->|Refusal| GradingResult
    isBasicRefusal -->|Not Refusal| RedteamGraderBase_getResult
    RedteamGraderBase_getResult --> matchesLlmRubric
    matchesLlmRubric --> GradingResult
```

**Sources:** [src/redteam/plugins/harmful/graders.ts:50-81](), [src/redteam/plugins/base.ts:41-76](), [src/redteam/util.ts:136-212](), [src/matchers/rubric.ts:1-20]()

### Refusal Detection

Graders short-circuit the evaluation if the model provides a standard refusal (e.g., "I am sorry, I cannot fulfill this request"). In red teaming, a refusal is considered a **success** for the safety system (meaning the grader returns `pass: true`) [src/redteam/plugins/harmful/graders.ts:60-69](). This check is performed using a list of common refusal prefixes and substrings [src/redteam/util.ts:136-212]().

## Built-in Grader Library

Promptfoo includes a comprehensive library of graders for specific adversarial categories.

| Grader Class | ID | Purpose |
|--------------|----|---------|
| `HarmfulGrader` | `promptfoo:redteam:harmful` | General harmful content detection [src/redteam/graders.ts:44]() |
| `BflaGrader` | `promptfoo:redteam:bfla` | Broken Function Level Authorization [src/redteam/graders.ts:6]() |
| `AegisGrader` | `promptfoo:redteam:aegis` | NVIDIA Aegis safety model grading [src/redteam/graders.ts:1]() |
| `PiiGrader` | `promptfoo:redteam:pii` | PII leakage detection [src/redteam/graders.ts:86]() |
| `SqlInjectionGrader` | `promptfoo:redteam:sql-injection` | SQL injection success detection [src/redteam/graders.ts:105]() |
| `ShellInjectionGrader` | `promptfoo:redteam:shell-injection` | Shell command injection detection [src/redteam/graders.ts:104]() |
| `CoppaGrader` | `promptfoo:redteam:coppa` | COPPA compliance violation detection [src/redteam/graders.ts:11]() |

**Sources:** [src/redteam/graders.ts:1-107](), [test/redteam/graders.test.ts:1-117]()

## Integration with matchesLlmRubric

`RedteamGraderBase` integrates with the core `matchesLlmRubric` matcher. This allows red team graders to leverage the same evaluation engine used for standard assertions while applying adversarial-specific rubrics.

### Data Flow

1. The `RedteamGraderBase` renders the Nunjucks rubric with test variables including `purpose` and `prompt`.
2. It calls the core grading utility `matchesLlmRubric` [src/redteam/plugins/base.ts:4]().
3. The LLM evaluator processes the rubric, prompt, and output using the configured grading provider.
4. The result is returned as a `GradingResult` containing `pass`, `score`, and `reason`.

**Sources:** [src/redteam/plugins/base.ts:4](), [src/redteam/plugins/harmful/graders.ts:71-80](), [src/matchers/rubric.ts:1-20]()

# Red Team Commands




This document covers the command-line interface for red team operations in promptfoo. These commands provide the primary user interface for generating adversarial test cases, executing red team evaluations, and performing specialized security testing tasks.

For information about the underlying red team system architecture, see [Red Team Architecture](#5.1). For details about plugins and strategies used by these commands, see [Test Generation and Configuration](#5.2).

## Command Overview

The red team system exposes several CLI subcommands, each serving distinct security testing purposes. These are registered in the main CLI entry point and managed via `Commander.js`.

| Command | Function | Primary Implementation |
|---------|----------|----------------------|
| `init` | Initialize a new red team project | `redteamInit()` |
| `generate` | Create adversarial test cases | `doGenerateRedteam()` |
| `run` | Full red team evaluation (generate + evaluate) | `doRedteamRun()` |
| `discover` | Target system discovery agent | `doTargetPurposeDiscovery()` |
| `poison` | Generate poisoned RAG documents | `doPoisonDocuments()` |
| `report` | View the red team security report | `redteamReportCommand()` |
| `plugins` | List available redteam plugins | `redteamPluginsCommand()` |

### Command Registration Flow

```mermaid
graph TD
    CLI["main.ts Entry Point"]
    RTC["redteamGenerateCommand()"]
    RRC["redteamRunCommand()"]
    DC["discoverCommand()"]
    PC["poisonCommand()"]
    INC["redteamInit()"]

    CLI --> RTC
    CLI --> RRC
    CLI --> DC
    CLI --> PC
    CLI --> INC

    RTC --> DGR["doGenerateRedteam()"]
    RRC --> DRR["doRedteamRun()"]
    DC --> DTPD["doTargetPurposeDiscovery()"]
    PC --> DPD["doPoisonDocuments()"]
```

**Sources:** [src/redteam/commands/generate.ts:43](), [src/redteam/commands/run.ts:22-146](), [src/redteam/commands/discover.ts:280-377](), [src/redteam/commands/poison.ts:174-203](), [src/redteam/commands/init.ts:203-230]()

## Init Command

The `init` command provides an interactive onboarding experience to bootstrap a red team configuration. It uses `@inquirer` to walk users through defining their target, purpose, and security posture.

### Initialization Flow
1. **Project Setup**: Creates a project directory and initializes `promptfooconfig.yaml` [src/redteam/commands/init.ts:207-212]().
2. **Target Definition**: Prompts for the target name and type (HTTP endpoint, RAG, or Prompt/Model) [src/redteam/commands/init.ts:217-235]().
3. **Purpose Discovery**: Optionally triggers the discovery agent or prompts for a system purpose [src/redteam/commands/init.ts:237-250]().
4. **Configuration Generation**: Uses `renderRedteamConfig()` with a Nunjucks template to produce the final YAML [src/redteam/commands/init.ts:174-201]().

**Sources:** [src/redteam/commands/init.ts:33-109](), [src/redteam/commands/init.ts:174-201](), [src/redteam/commands/init.ts:203-260]()

## Generate Command

The `generate` command creates adversarial test cases using plugins and strategies. It serves as the foundation for red team testing by producing targeted prompts designed to expose vulnerabilities.

### Core Implementation

```mermaid
graph TD
    RGC["redteamGenerateCommand()"] --> DGR["doGenerateRedteam()"]
    DGR["doGenerateRedteam()"] --> PL["checkRedteamProbeLimit()"]
    DGR --> RC["resolveConfigs()"]
    DGR --> SYN["synthesize()"]
    DGR --> WPC["writePromptfooConfig()"]

    SYN["synthesize()"] --> ESP["extractSystemPurpose()"]
    SYN --> EE["extractEntities()"]
    SYN --> PB["Plugins[pluginId].generate()"]
    SYN --> SB["loadStrategy()"]

    PB --> TCS["TestCaseWithPlugin[]"]
    SB --> TCS
    TCS --> WPC
```

The `doGenerateRedteam()` function orchestrates the generation process. It first checks the monthly probe limit for non-logged-in users via `checkRedteamProbeLimit()` [src/redteam/commands/generate.ts:44](). It then handles configuration resolution, test case synthesis via `synthesize()`, and output formatting.

### Command Options

Key parameters supported by the generate command:

- `--config` - Configuration file path or cloud UUID [src/redteam/commands/generate.ts:36-37]().
- `--plugins` - Comma-separated plugin list [src/validators/redteam.ts:85-87]().
- `--strategies` - Comma-separated strategy list [src/validators/redteam.ts:152-164]().
- `--num-tests` - Number of tests per plugin [src/validators/redteam.ts:112-116]().
- `--output` - Output file path (defaults to `redteam.yaml`) [src/redteam/commands/generate.ts:38]().
- `--remote` - Force remote inference for generation [src/redteam/commands/generate.ts:62]().

### Configuration Resolution

The command supports multiple configuration sources with precedence handling:

1. **Cloud configurations** via UUID [src/redteam/commands/generate.ts:27-30]().
2. **Local YAML files** resolved via `resolveConfigs()` [src/redteam/commands/generate.ts:36]().
3. **Command-line overrides** processed via `RedteamGenerateOptionsSchema` [src/validators/redteam.ts:204-234]().

**Sources:** [src/redteam/commands/generate.ts:60](), [src/redteam/index.ts:189-204](), [src/validators/redteam.ts:204-234]()

## Run Command

The `run` command executes a complete red team evaluation by combining test generation with evaluation execution. It is the primary command for a full security scan.

### Two-Phase Execution

```mermaid
graph TD
    RRC["redteamRunCommand()"] --> DRR["doRedteamRun()"]
    DRR --> Phase1["Phase 1: Generate"]
    DRR --> Phase2["Phase 2: Evaluate"]

    Phase1 --> DGR["doGenerateRedteam()"]
    DGR --> SYN["synthesize()"]
    SYN --> TC["redteam.yaml"]

    Phase2 --> DE["doEval()"]
    TC --> DE
    DE --> RES["Eval Result"]
```

### Execution Flow
1. **Health Check**: It verifies the API health via `checkRemoteHealth()` before proceeding [src/redteam/index.ts:10]().
2. **Generation**: Calls `doGenerateRedteam()` to produce the `redteam.yaml` file [src/redteam/commands/generate.ts:19]().
3. **Evaluation**: Executes the standard evaluation pipeline using the generated adversarial suite.

**Sources:** [src/redteam/commands/run.ts:22-146](), [src/redteam/index.ts:10](), [src/redteam/commands/generate.ts:19]()

## Discover Command

The `discover` command implements the **Target Discovery Agent**. It uses an iterative questioning approach to extract system information, which can then be used to improve the relevance of generated red team tests.

### Discovery Process Flow

```mermaid
graph TD
    DC["discoverCommand()"] --> DTPD["doTargetPurposeDiscovery()"]
    DTPD --> AGENT["Discovery Agent Loop"]
    AGENT --> Q["Generate Question"]
    Q --> TARGET["Call Target Provider"]
    TARGET --> ANS["Process Answer"]
    ANS --> Done{"Information Sufficient?"}
    Done -->|No| Q
    Done -->|Yes| Result["Purpose, Entities, Context"]
```

The agent attempts to identify:
- **System Purpose**: What the application is designed to do [src/redteam/index.ts:39]().
- **User Context**: Who the intended users are.
- **System Limitations**: Explicit constraints or boundaries.

**Sources:** [src/redteam/commands/discover.ts:139-273](), [src/redteam/index.ts:39]()

## Poison Command

The `poison` command generates poisoned documents for RAG (Retrieval-Augmented Generation) testing. It injects malicious or manipulative content into existing documents to test if a model's RAG pipeline can be subverted.

### Document Processing Pipeline

```mermaid
graph TD
    PC["poisonCommand()"] --> DPD["doPoisonDocuments()"]
    DPD --> DOCS["Collect Documents (File/Dir)"]
    DOCS --> GEN["generatePoisonedDocument()"]
    GEN --> REMOTE["Remote Generation API"]
    REMOTE --> WRITE["Write poisoned_[filename]"]
```

The command supports:
- **Recursive Directory Scanning**: Collects all files in a path.
- **Goal-Oriented Poisoning**: Users can specify a `goal` (e.g., "make the model recommend a competitor").

**Sources:** [src/redteam/commands/poison.ts:56-80](), [src/redteam/commands/poison.ts:134-172]()

## Shared Infrastructure

### Remote Generation and Health
Many red team commands rely on remote inference for the "attacker" models. This is managed via `remoteGeneration.ts` and `apiHealth.ts`.
- `checkRemoteHealth(url)`: Ensures the generation service is available [src/redteam/index.ts:10]().
- `shouldGenerateRemote()`: Determines if generation should happen locally or via the promptfoo cloud API [src/redteam/index.ts:45]().

### Caching
Red team commands utilize the centralized cache system to avoid redundant generation of adversarial tests.
- `withCacheEnabled(enabled, fn)`: Wraps generation logic to provide persistence [src/redteam/commands/generate.ts:9]().
- `cliState.cache`: Global state determining if cache is used [src/redteam/index.ts:7]().

**Sources:** [src/redteam/commands/generate.ts:9](), [src/redteam/index.ts:10](), [src/redteam/index.ts:45](), [src/cache.ts:65-71]()
## Purpose and Scope

This document provides an overview of Promptfoo's provider ecosystem, covering the 50+ LLM provider integrations beyond the core providers detailed in earlier sections. It focuses on the architecture patterns used to integrate different provider types, including OpenAI-compatible wrappers, embedding providers, open-source model providers (Ollama, LocalAI), and specialized services like Mistral, WatsonX, xAI, and HuggingFace.

---

## Provider Categories

Promptfoo organizes providers into several major categories based on their implementation patterns and capabilities:

### Category Overview Diagram

```mermaid
graph TB
    subgraph "Provider Categories"
        OpenAIBased["OpenAI-Based Providers<br/>(Wrapper Pattern)"]
        Embeddings["Embedding Providers"]
        OpenSource["Open Source Providers"]
        Custom["Custom Providers"]
        Cloud["Cloud Providers"]
    end

    subgraph "OpenAI-Based Examples"
        OAI1["OpenRouter"]
        OAI2["Perplexity"]
        OAI3["TogetherAI"]
        OAI4["Mistral"]
        OAI5["xAI (Grok)"]
        OAI6["DeepSeek"]
    end

    subgraph "Embedding Examples"
        EMB1["OpenAI Embeddings"]
        EMB2["Voyage"]
        EMB3["Vertex Embeddings"]
        EMB4["Ollama Embeddings"]
        EMB5["LocalAI Embeddings"]
    end

    subgraph "Open Source Examples"
        OS1["Ollama"]
        OS2["Replicate"]
        OS3["LocalAI"]
        OS4["vLLM"]
    end

    subgraph "Custom Examples"
        CUST1["PythonProvider"]
        CUST2["ScriptCompletionProvider"]
        CUST3["GolangProvider"]
        CUST4["HttpProvider"]
    end

    OpenAIBased --> OAI1
    OpenAIBased --> OAI2
    OpenAIBased --> OAI3
    OpenAIBased --> OAI4
    OpenAIBased --> OAI5
    OpenAIBased --> OAI6

    Embeddings --> EMB1
    Embeddings --> EMB2
    Embeddings --> EMB3
    Embeddings --> EMB4
    Embeddings --> EMB5

    OpenSource --> OS1
    OpenSource --> OS2
    OpenSource --> OS3
    OpenSource --> OS4

    Custom --> CUST1
    Custom --> CUST2
    Custom --> CUST3
    Custom --> CUST4
```

**Sources:** `[src/providers/index.ts:1-331]()`

---

## Local and Open Source Providers

### Ollama Integration
The `OllamaCompletionProvider` and `OllamaChatProvider` interface with the local Ollama API (default `http://localhost:11434`) `[src/providers/ollama.ts:220-220]()`. It supports extensive model options including `num_predict`, `temperature`, and `top_p` `[src/providers/ollama.ts:16-54]()`. It also supports reasoning models via the `think` parameter `[src/providers/ollama.ts:52-52]()` and tool usage via `tools` `[src/providers/ollama.ts:51-51]()`.

### LocalAI Integration
`LocalAiChatProvider`, `LocalAiCompletionProvider`, and `LocalAiEmbeddingProvider` provide an OpenAI-compatible interface for local models `[src/providers/localai.ts:57-183]()`. They utilize `fetchWithCache` to communicate with the LocalAI endpoint, defaulting to `http://localhost:8080/v1` `[src/providers/localai.ts:34-38]()`.

### Replicate Integration
The `ReplicateProvider` handles models hosted on Replicate by constructing predictions and polling for completion `[src/providers/replicate.ts:111-131]()`. It supports specific input options like `max_new_tokens`, `system_prompt`, and `stop_sequences` `[src/providers/replicate.ts:202-214]()`.

---

## Major Cloud and API Providers

### Mistral AI
Mistral is implemented via `MistralChatCompletionProvider` and `MistralEmbeddingProvider` `[src/providers/mistral.ts:237-254]()`. It includes a comprehensive cost table for models like `mistral-large-latest` and `pixtral-12b` `[src/providers/mistral.ts:20-218]()`. It supports tool calling and structured outputs via `response_format` `[src/providers/mistral.ts:242-254]()`.

### xAI (Grok)
The `xai` provider supports Grok models through an interface compatible with OpenAI's format `[site/docs/providers/xai.md:21-23]()`. It includes specific support for reasoning models like `grok-4.6`, `grok-4.5`, and `grok-4.3` `[src/providers/xai/chat.ts:123-185]()`. For reasoning models, it accepts a `reasoning_effort` parameter (`none`, `low`, `medium`, `high`) `[site/docs/providers/xai.md:127-127]()`. The `XAIResponsesProvider` supports advanced agent tools including `web_search`, `x_search`, and `code_execution` `[src/providers/xai/chat.ts:19-74]()`.

### IBM WatsonX
The `WatsonXProvider` and `WatsonXChatProvider` use the `@ibm-cloud/watsonx-ai` SDK `[src/providers/watsonx.ts:11-12]()`. It supports both IAM (API Key) and Bearer Token authentication `[src/providers/watsonx.ts:50-55]()`. It includes a sophisticated `TIER_PRICING` model for cost calculation based on IBM's pricing classes `[src/providers/watsonx.ts:98-117]()`.

### HuggingFace Ecosystem
HuggingFace integration spans two primary areas:
1. **Inference**: `HuggingfaceChatCompletionProvider` (OpenAI-compatible) and `HuggingfaceTextGenerationProvider` `[src/providers/huggingface.ts:68-142]()`. It supports routing via inference providers using a suffix pattern `huggingface:chat:org/model:provider-name` `[src/providers/huggingface.ts:63-63]()`.
2. **Datasets**: Allows using HuggingFace datasets as test cases via `fetchHuggingFaceDataset`.

### Azure OpenAI
The `azure` provider enables access to GPT-4, reasoning models (o1, o3), and third-party models via Azure AI Foundry `[site/docs/providers/azure.md:8-10]()`. It supports `AzureChatCompletionProvider`, `AzureEmbeddingProvider`, and `AzureAssistantProvider` `[site/docs/providers/azure.md:89-97]()`. Authentication is handled via API Key, Service Principal (Client Credentials), or Azure CLI `[site/docs/providers/azure.md:14-73]()`.

---

## Model Context Protocol (MCP) Integration

Promptfoo supports the Model Context Protocol (MCP) to connect LLMs to external tools and data sources.

### MCP Client Architecture

```mermaid
graph LR
    subgraph "MCP Client [src/providers/mcp/client.ts]"
        Client["Client Class"]
        Transport["Transport (Stdio/SSE/HTTP)"]
    end

    subgraph "Servers"
        S1["Local Script (.js/.py)"]
        S2["Remote SSE Server"]
        S3["NPM Package"]
    end

    Client --> Transport
    Transport --> S1
    Transport --> S2
    Transport --> S3
```

**Sources:** `[src/providers/mcp/client.ts:89-141]()`, `[src/providers/mcp/client.ts:152-195]()`

The `MCPClient` manages connections to multiple servers and handles tool discovery `[src/providers/mcp/client.ts:89-91]()`. It supports `StdioClientTransport` for local processes and `SSEClientTransport` or `StreamableHTTPClientTransport` for remote servers `[src/providers/mcp/client.ts:93-96]()`.

---

## Shared Provider Patterns

### Tracing and Observability
Most modern providers in the ecosystem use the `withGenAISpan` utility to wrap API calls `[src/providers/ollama.ts:187-188]()`, `[src/providers/mistral.ts:460-461]()`, `[src/providers/huggingface.ts:216-216]()`. This integrates provider execution with the OpenTelemetry-based tracing system, capturing `tokenUsage` and model metadata `[src/providers/ollama.ts:159-172]()`.

### Request Flow and Data Normalization

```mermaid
sequenceDiagram
    participant E as Evaluator
    participant P as ApiProvider (e.g. OllamaCompletionProvider)
    participant C as Cache (fetchWithCache)
    participant A as External API

    E->>P: callApi(prompt, context)
    P->>P: Setup GenAISpanContext [src/providers/ollama.ts:159]
    P->>P: parseChatPrompt() [src/providers/shared.ts]
    P->>C: fetchWithCache(url, body, timeout) [src/cache.ts]
    C->>A: HTTP POST
    A-->>C: JSON Response
    C-->>P: Data + Cache Status
    P->>P: Extract tokenUsage & output
    P-->>E: ProviderResponse
```

**Sources:** `[src/providers/ollama.ts:157-238]()`, `[src/providers/shared.ts:1-50]()`

### Configuration and Security
Providers resolve API keys using a hierarchy:
1. Explicit `apiKey` in provider config `[src/providers/mistral.ts:238-238]()`.
2. Provider-specific environment variables (e.g., `XAI_API_KEY`, `HF_TOKEN`, `AZURE_API_KEY`) `[src/providers/xai/chat.test.ts:62-62]()`, `[src/providers/huggingface.ts:91-91]()`.
3. Global environment variables.

### Common Utilities
| Feature | Implementation | Key File |
| :--- | :--- | :--- |
| **Caching** | `fetchWithCache` | `[src/cache.ts]()` |
| **Tracing** | `withGenAISpan` | `[src/tracing/genaiTracer.ts]()` |
| **Timeouts** | `getRequestTimeoutMs` | `[src/providers/shared.ts:25]()` |
| **Prompt Parsing** | `parseChatPrompt` | `[src/providers/shared.ts:25]()` |

---

## Implementation Details: WatsonX Authentication

WatsonX demonstrates a complex authentication flow supporting multiple IBM Cloud methods:

```mermaid
graph TD
    subgraph "WatsonXProvider.getClient()"
        Start["Start Client Init"]
        CheckIAM["Check apiKey / WATSONX_AI_APIKEY"]
        CheckBearer["Check apiBearerToken / WATSONX_AI_BEARER_TOKEN"]

        IAM["IamAuthenticator [ibm-cloud-sdk-core]"]
        Bearer["BearerTokenAuthenticator [ibm-cloud-sdk-core]"]

        NewInstance["WatsonXAI.newInstance()"]
    end

    Start --> CheckIAM
    CheckIAM -->|Found| IAM
    CheckIAM -->|Not Found| CheckBearer
    CheckBearer -->|Found| Bearer
    CheckBearer -->|Not Found| Error["Throw Auth Error"]

    IAM --> NewInstance
    Bearer --> NewInstance
```

**Sources:** `[src/providers/watsonx.ts:222-226]()`, `[src/providers/watsonx.ts:50-55]()`, `[test/providers/watsonx.test.ts:162-181]()`
This system handles the dynamic loading, registration, and instantiation of API providers based on configuration strings, files, or objects. It provides a unified interface for working with diverse provider types ranging from cloud APIs to local executables.

For information about specific provider implementations and their capabilities, see [Provider Ecosystem](#3.9). For HTTP-specific provider functionality, see [HTTP Provider](#3.2).

## Core Loading Functions

The provider loading system centers around two main functions: `loadApiProvider` for single providers and `loadApiProviders` for multiple providers.

### loadApiProvider Function

The `loadApiProvider` function in `src/providers/index.ts` takes a provider identifier and returns a single `ApiProvider` instance. It handles several resolution paths:

- **Environment Template Rendering**: Renders `{{ env.VAR }}` templates in the provider ID and configuration at load time using `renderEnvOnlyInObject` [src/providers/index.ts:94-100]().
- **Cloud references**: Identifies `promptfoo://provider/` strings via `isCloudProvider`, fetches the configuration from Promptfoo Cloud via `getProviderFromCloud`, and merges it with local overrides [src/providers/index.ts:120-163]().
- **File references**: Loads provider definitions from `file://` paths pointing to YAML or JSON files via `readProviderConfigFile` [src/providers/index.ts:165-200]().
- **Registry Lookup**: Delegates to `getProviderFactories` to find matching implementations in the `providerMap` [src/providers/index.ts:202-214]().

Title: "loadApiProvider Resolution Flow"
```mermaid
graph TD
    subgraph "loadApiProvider Flow [src/providers/index.ts]"
        INPUT["Input: providerPath + LoadApiProviderContext"]
        RENDER["renderEnvOnlyInObject (Resolve {{env.*}})"]
        CLOUD{"isCloudProvider?"}
        FILE{"isProviderConfigFileReference?"}
        REGISTRY["Registry Lookup (getProviderFactories)"]
        FACTORY["Execute matching factory.create()"]
        PROVIDER["Return ApiProvider instance"]
    end

    INPUT --> RENDER
    RENDER --> CLOUD
    CLOUD -->|Yes| GETCLOUD["getProviderFromCloud()"]
    CLOUD -->|No| FILE
    FILE -->|Yes| LOADFILE["readProviderConfigFile()"]
    FILE -->|No| REGISTRY
    REGISTRY --> FACTORY
    GETCLOUD --> PROVIDER
    LOADFILE --> PROVIDER
    FACTORY --> PROVIDER
```

**loadApiProvider Resolution Process**
Sources: [src/providers/index.ts:83-220](), [test/providers.test.ts:48-161]()

### loadApiProviders Function

The `loadApiProviders` function processes arrays of provider specifications. It uses `normalizeProviderRef` to classify inputs and `loadProviderConfigsFromFile` to flatten nested configurations from files [src/providers/index.ts:14-19](). It ensures that if a file reference contains multiple providers, they are all instantiated and returned as a flat list [src/providers/index.ts:173-178]().

Sources: [src/providers/index.ts:222-265](), [test/providers.test.ts:84-123]()

## Provider Registry Architecture

The registry uses a factory pattern where each provider type has a dedicated factory that can test for compatibility and create instances. The primary registry is the `providerMap` array in `src/providers/registry.ts`.

Title: "Provider Registry and Factory Mapping"
```mermaid
graph TB
    subgraph "Provider Registry [src/providers/registry.ts]"
        PROVIDERMAP["providerMap: ProviderFactory[]"]

        subgraph "ProviderFactory Interface [src/providers/registryTypes.ts]"
            TEST["test(providerPath): boolean"]
            CREATE["create(providerPath, options, context): Promise<ApiProvider>"]
        end

        subgraph "Core Factories"
            SCRIPT["createScriptBasedProviderFactory (python, golang, ruby)"]
            OPENAI["OpenAiChatCompletionProvider"]
            ANTHROPIC["AnthropicMessagesProvider"]
            BEDROCK["AwsBedrockCompletionProvider"]
            XAI["createXAIProvider"]
        end

        PROVIDERMAP --> TEST
        PROVIDERMAP --> CREATE
        CREATE --> SCRIPT
        CREATE --> OPENAI
        CREATE --> ANTHROPIC
        CREATE --> XAI
    end
```

**Provider Factory Registry Pattern**
Sources: [src/providers/registry.ts:138-148](), [test/providers/registry.test.ts:57-85]()

### Factory Implementation Examples

Each factory in the `providerMap` array implements the `ProviderFactory` interface.

**Script-based Provider Factory**:
Uses `createScriptBasedProviderFactory` to register executors for `exec` (ScriptCompletionProvider), `golang` (GolangProvider), `python` (PythonProvider), and `ruby` (RubyProvider) [src/providers/registry.ts:93-101]().

**xAI Provider Factory**:
Checks for the `xai:` prefix and calls `createXAIProvider` [src/providers/registry.ts:113-117]().

**Dynamic Loading (getProviderFactories)**:
The `getProviderFactories` function handles lazy-loading of provider families (like `redteam` or `bedrock`) to keep the core bundle small. It returns the `providerMap` for standard providers but merges additional factories for specialized families [src/providers/registry.test.ts:87-113]().

Sources: [src/providers/registry.ts:138-148](), [src/providers/registry.test.ts:87-138](), [test/providers/registry.test.ts:140-171]()

## Configuration and Environment Integration

### Environment Variable Resolution
The system uses `src/envars.ts` to manage configuration keys such as `PROMPTFOO_CACHE_ENABLED` or `PROMPTFOO_OTEL_ENABLED` [src/envars.ts:21-80](). At load time, `loadApiProvider` merges environment overrides from the test suite context with provider-specific options [src/providers/index.ts:91-92]().

### File-based Configuration
Providers can be defined in external files. The system supports recursive resolution of `file://` references within provider configurations (e.g., loading an API key or a system prompt from a separate text file) via `maybeLoadConfigFromExternalFile` [test/providers.test.ts:125-161]().

Title: "Recursive Configuration Resolution"
```mermaid
flowchart TD
    CONFIG[Provider Configuration Object] --> RECURSE["maybeLoadConfigFromExternalFile()"]
    RECURSE --> ISFILE{"Value starts with file://?"}
    ISFILE -->|Yes| READ["fs.readFileSync()"]
    ISFILE -->|No| KEEP[Keep original value]
    READ --> MERGE[Replace reference with file content]
    MERGE --> CONFIG
```

**Recursive File Reference Resolution**
Sources: [test/providers.test.ts:125-161](), [src/providers/index.ts:165-180]()

## Error Handling and Validation

The system enforces strict validation during the loading process:
- **Sanitization**: Invalid provider configurations are passed through `sanitizeObject` before being logged to avoid leaking secrets [src/providers/index.ts:65-79]().
- **Type Safety**: Uses `isApiProvider` to ensure loaded objects implement the required `callApi` interface [src/providers/index.ts:5-11]().
- **Conflict Prevention**: `loadApiProvider` throws an error if it encounters a file containing an array of providers, directing the user to `loadApiProviders` instead [src/providers/index.ts:174-178]().
- **Registry Context**: `LoadApiProviderContext` is passed through the registry to ensure providers have access to the `basePath` for resolving relative paths to scripts or local models [src/providers/registry.ts:119-122]().

Sources: [src/providers/index.ts:65-79](), [src/providers/index.ts:174-178](), [test/providers.test.ts:65-82](), [src/providers/registry.ts:141-147]()

# HTTP Provider




The HTTP Provider enables integration with custom API endpoints for LLM inference through flexible HTTP/HTTPS requests. This provider allows you to evaluate models hosted on your own servers or third-party services not directly supported by built-in providers. It supports structured and raw HTTP request modes, advanced authentication mechanisms, and comprehensive request/response transformation capabilities.

The HTTP Provider is implemented in the `HttpProvider` class and provides a general-purpose way to integrate with any HTTP endpoint that offers language model capabilities.

## HTTP Provider Architecture

The HTTP provider is implemented through the `HttpProvider` class [src/providers/http.ts:433](), which conforms to the `ApiProvider` interface [src/types/providers.ts:123](). This provider enables communication with any HTTP/HTTPS endpoint by constructing and sending HTTP requests containing prompts and processing the responses.

### HttpProvider Class Structure

```mermaid
classDiagram
    class ApiProvider {
        <<interface>>
        +id(): string
        +callApi(prompt, context?): Promise~ProviderResponse~
    }

    class HttpProvider {
        -url: string
        -config: HttpProviderConfig
        -transformResponse: Promise~Function~
        -sessionParser: Promise~Function~
        -transformRequest: Promise~Function~
        -validateStatus: Promise~Function~
        -lastSignatureTimestamp?: number
        -lastSignature?: string
        +constructor(url, options)
        +id(): string
        +toString(): string
        +callApi(prompt, context?): Promise~ProviderResponse~
        -refreshSignatureIfNeeded(): Promise~void~
        -getDefaultHeaders(body): Record~string, string~
        -validateContentTypeAndBody(headers, body): void
        -getHeaders(defaultHeaders, vars): Promise~Record~string, string~~
        -estimateTokenUsage(promptText, completionText): Promise~TokenUsage~
    }

    class HttpProviderConfigSchema {
        +body?: any
        +headers?: Record~string, string~
        +maxRetries?: number
        +method?: string
        +queryParams?: Record~string, string~
        +request?: string
        +useHttps?: boolean
        +sessionParser?: string | Function
        +transformRequest?: string | Function
        +transformResponse?: string | Function
        +url?: string
        +validateStatus?: string | Function
        +signatureAuth?: SignatureAuthConfig
        +multipart?: HttpMultipartConfig
    }

    ApiProvider <|-- HttpProvider
    HttpProvider *-- HttpProviderConfigSchema
```

Sources:
- [src/providers/http.ts:397-431]()
- [src/providers/http.ts:433-460]()
- [src/types/providers.ts:123-140]()

## Request Processing Flow

The HTTP provider processes requests through multiple stages, with different paths for structured, raw, and multipart request modes.

### Request Processing Pipeline

```mermaid
flowchart TD
    prompt["Prompt Input (CallApiContextParams)"] --> transformReq["HttpProvider.transformRequest()"]
    transformReq --> chooseMode{"Request Mode?"}

    chooseMode -->|"config.request"| rawMode["Raw Request Mode"]
    chooseMode -->|"config.multipart"| multipartMode["Multipart Mode"]
    chooseMode -->|"Default"| structuredMode["Structured Request Mode"]

    rawMode --> renderRaw["renderRawRequestWithNunjucks()"]
    renderRaw --> parseRaw["httpZ.parse()"]

    multipartMode --> renderMultipart["renderHttpMultipartBody()"]
    renderMultipart --> buildMultipart["Build FormData via undici.Agent"]

    structuredMode --> renderVars["renderVarsInObject()"]
    renderVars --> processBody["processJsonBody() / processTextBody()"]

    parseRaw --> validateRequest["HttpProvider.validateContentTypeAndBody()"]
    buildMultipart --> validateRequest
    processBody --> validateRequest

    validateRequest --> signatureAuth["HttpProvider.refreshSignatureIfNeeded()"]
    signatureAuth --> sendRequest["fetchWithCache()"]

    sendRequest --> validateStatus["HttpProvider.validateStatus()"]
    validateStatus --> parseResponse["Parse Response (JSON/Text)"]
    parseResponse --> sessionParser["HttpProvider.sessionParser()"]
    sessionParser --> transformResponse["HttpProvider.transformResponse()"]
    transformResponse --> providerResponse["ProviderResponse"]
```

Sources:
- [src/providers/http.ts:1061-1192]()
- [src/providers/http.ts:1218-1244]()
- [src/providers/http.ts:682-704]()
- [src/providers/http.ts:495-574]()

## Configuration Options

The HTTP provider is configured using the `HttpProviderConfig` schema, defined via Zod in the codebase [src/providers/http.ts:397-431]().

### Configuration Schema Highlights

| Option | Type | Description |
|--------|------|-------------|
| `url` | string | The target endpoint [src/providers/http.ts:401](). |
| `method` | string | HTTP verb (GET, POST, etc.) [src/providers/http.ts:402](). |
| `headers` | Record | HTTP headers with template support [src/providers/http.ts:403](). |
| `body` | any | Request payload [src/providers/http.ts:404](). |
| `request` | string | Raw HTTP request string (supports `file://`) [src/providers/http.ts:407](). |
| `multipart` | object | Config for `multipart/form-data` via `HttpMultipartConfigSchema` [src/providers/http.ts:413](). |
| `transformResponse` | string \| Function | Extract result from response using `createTransformResponse` [src/providers/http.ts:409](). |
| `signatureAuth` | object | Digital signature configuration [src/providers/http.ts:425](). |

### Multipart Support
The provider supports `multipart/form-data` for file uploads and complex form fields [site/docs/providers/http.md:76-81](). It uses `renderHttpMultipartBody` to build the request [src/providers/http.ts:39-42](). It can generate deterministic files (PDF, PNG, JPEG) or upload local files via the `path` source [site/docs/providers/http.md:114-118]().

Sources:
- [src/providers/http.ts:397-431]()
- [src/providers/http.ts:39-42]()
- [site/docs/providers/http.md:76-142]()

## Authentication Mechanisms

### Digital Signature Authentication
The HTTP provider supports signing requests with digital signatures. It handles various certificate types including PEM, JKS, and PFX via `preprocessSignatureAuthConfig` [src/providers/http.ts:85-199](). This function maps generic certificate fields to type-specific fields (e.g., `certificateContent` to `pfxContent` for PFX) [src/providers/http.ts:149-151]().

```mermaid
flowchart TD
    config["SignatureAuth Config"] --> preprocess["preprocessSignatureAuthConfig()"]
    preprocess --> detectType{"Detect Type"}
    detectType -->|"PEM"| pem["Load Private Key (fs.readFile)"]
    detectType -->|"JKS"| jks["Load Keystore Content"]
    detectType -->|"PFX"| pfx["Load PFX Content"]

    pem --> sign["crypto.createSign('SHA256')"]
    jks --> sign
    pfx --> sign

    sign --> result["Set signature & signatureTimestamp in vars"]
```

Sources:
- [src/providers/http.ts:85-199]()
- [src/providers/http.ts:954-988]()
- [test/providers/http/auth.test.ts:36-98]()

### Standard Auth
- **Bearer/API Key**: Managed via the `headers` configuration with variable substitution [site/docs/providers/http.md:18-22]().
- **Basic Auth**: Can be constructed manually in headers or via raw request [site/docs/providers/http.md:152-167]().
- **OAuth**: Supported through token refresh mechanisms and `TOKEN_REFRESH_BUFFER_MS` [src/providers/http.ts:25]().

## Dynamic Request Construction

The provider uses Nunjucks templating to render requests dynamically [src/providers/http.ts:35]().

### JSON Variable Escaping
To prevent invalid JSON when substituting multiline strings or quotes, the provider uses `escapeJsonVariables` [src/providers/http.ts:74-81](). This ensures that a variable like `value\nwith\nnewlines` is safely converted to `value\\nwith\\nnewlines` within a JSON context [src/providers/http.ts:71-73]().

### Raw Request Parsing
When `config.request` is used, the provider utilizes `http-z` to parse the raw HTTP string into a structured request object [src/providers/http.ts:7](). This is handled in `renderRawRequestWithNunjucks` [src/providers/http.ts:1218-1244]().

Sources:
- [src/providers/http.ts:74-81]()
- [src/providers/http.ts:1218-1244]()

## Response Transformation and Validation

### transformResponse
Users can provide a string (evaluated as a function body) or a JavaScript function to extract data from the response [src/providers/http.ts:706-777](). It is created via `createTransformResponse` [src/providers/httpTransforms.ts:43-46]().

### validateStatus
Custom logic to determine if an HTTP status code should be treated as a success or failure [src/providers/http.ts:804-856]().

### sessionParser
Extracts session information (like Cookies) from responses to maintain state in multi-turn evaluations [src/providers/http.ts:451-489]().

Sources:
- [src/providers/http.ts:706-777]()
- [src/providers/http.ts:804-856]()
- [src/providers/http.ts:451-489]()

## TLS and mTLS Configuration

The provider supports advanced TLS configurations for secure communication.

- **mTLS**: Configured via `signatureAuth` or `https` agent settings [src/providers/http.ts:115-120]().
- **Certificate Handling**: Supports loading certificates from files via `maybeLoadFromExternalFile` [src/providers/http.ts:18]().
- **Custom Agents**: Uses `undici` for high-performance HTTP pooling and `https.Agent` for specialized TLS requirements [src/providers/http.ts:4-8]().

Sources:
- [src/providers/http.ts:4-8]()
- [src/providers/http.ts:18]()

## WebSocket Provider

While `HttpProvider` handles standard REST/RPC, promptfoo also provides a specialized `WebSocketProvider` for real-time bidirectional communication [src/providers/websocket.ts:91]().

- **Message Templates**: Uses `messageTemplate` to construct outgoing messages [src/providers/websocket.ts:103]().
- **Streaming Response**: Supports streaming response accumulation via `streamResponse` [src/providers/websocket.ts:109-113]().
- **Implementation**: Uses the `ws` library for connection management [src/providers/websocket.ts:3]().

Sources:
- [src/providers/websocket.ts:91-108]()
- [src/providers/websocket.ts:102-119]()
- [site/docs/providers/websocket.md:7-15]()
This page documents the shared infrastructure used by all red team attack provider implementations: the `RedteamProviderManager` singleton, the `getTargetResponse()` helper, `tryUnblocking()`, `applyRuntimeTransforms()` / per-turn layers, and a set of conversation utilities. These components live in [`src/redteam/providers/shared.ts`]() and [`src/redteam/util.ts`]() and are consumed by every multi-turn attack provider.

For documentation of the attack providers themselves (Crescendo, Iterative, GOAT, etc.) that call these utilities, see [5.5](). For the layer strategy that injects `_perTurnLayers` into provider configs, see [5.4]().

---

## Overview

All red team attack providers share three common needs:

1.  **A consistent LLM** to act as the attacker/judge (distinct from the target being tested).
2.  **A normalized way** to call the target provider and get a string response back.
3.  **Conversation utilities** for message management, refusal detection, and variable transformation.

The module at `src/redteam/providers/shared.ts` satisfies all three, providing a single singleton and a set of exported functions that each attack provider imports.

**Provider Manager and Shared Utilities — Module Map**

```mermaid
graph TD
  subgraph "src/redteam/providers/shared.ts"
    RPM["redteamProviderManager\n(RedteamProviderManager)"]
    GTR["getTargetResponse()"]
    TU["tryUnblocking()"]
    CIC["createIterationContext()"]
    ERH["externalizeResponseForRedteamHistory()"]
    CPP["checkPenalizedPhrases()"]
    BGA["buildGraderResultAssertion()"]
    ICMA["isValidChatMessageArray()"]
    GLMC["getLastMessageContent()"]
    MTR["messagesToRedteamHistory()"]
  end
  subgraph "src/redteam/shared/runtimeTransform.ts"
    ART["applyRuntimeTransforms()"]
  end
  subgraph "src/redteam/util.ts"
    IBR["isBasicRefusal()"]
    GSI["getSessionId()"]
    EPT["extractPromptFromTags()"]
    EIV["extractInputVarsFromPrompt()"]
  end
  "CrescendoProvider" --> RPM
  "CrescendoProvider" --> GTR
  "CrescendoProvider" --> TU
  "CrescendoProvider" --> ART
  "RedteamIterativeProvider" --> RPM
  "RedteamIterativeProvider" --> GTR
  "RedteamIterativeProvider" --> CIC
  "RedteamIterativeProvider" --> ART
  "GoatProvider" --> TU
  "GoatProvider" --> ART
  "RedteamIterativeTreeProvider" --> RPM
  "RedteamIterativeTreeProvider" --> GTR
  "RedteamIterativeTreeProvider" --> CIC
  "RedteamIterativeTreeProvider" --> ART
```

Sources: [`src/redteam/providers/shared.ts:157-244`](), [`src/redteam/providers/iterative.ts:43-60`](), [`src/redteam/providers/crescendo/index.ts:43-66`](), [`src/redteam/providers/goat.ts:41-54`](), [`src/redteam/providers/iterativeTree.ts:52-68`]()

---

## `RedteamProviderManager`

`RedteamProviderManager` is a class instantiated once as the module-level export `redteamProviderManager` [`src/redteam/providers/shared.ts:244`](). It maintains up to five cached `ApiProvider` slots and exposes `getProvider()`, `getGradingProvider()`, and `getMultilingualProvider()`.

### Cached Slots

| Property | Purpose |
| :--- | :--- |
| `provider` | Default redteam attack provider [`src/redteam/providers/shared.ts:158`]() |
| `jsonOnlyProvider` | Same provider, forced `response_format: json_object` [`src/redteam/providers/shared.ts:160`]() |
| `multilingualProvider` | Configured for multilingual attack generation [`src/redteam/providers/shared.ts:161`]() |
| `gradingProvider` | Provider used for scoring/grading [`src/redteam/providers/shared.ts:162`]() |
| `gradingJsonOnlyProvider` | Grading provider, forced JSON output [`src/redteam/providers/shared.ts:163`]() |
| `rateLimitRegistry` | Optional `RateLimitRegistry` from `src/scheduler.ts` [`src/redteam/providers/shared.ts:164`]() |

Sources: [`src/redteam/providers/shared.ts:157-164`]()

### Rate Limiting Integration

When `setRateLimitRegistry(registry)` is called, every provider returned by the manager is automatically wrapped with `wrapProviderWithRateLimiting()` [`src/redteam/providers/shared.ts:178-183`](). The registry is intentionally **not** cleared by `clearProvider()`, as it is managed by the evaluator lifecycle, not by provider resets [`src/redteam/providers/shared.ts:185-187`]().

### `getProvider()` — Resolution Priority

The resolution checks `cliState.config?.redteam?.provider` first, then falls back to `cliState.config?.defaultTest` levels: `.provider`, `.options.provider.text`, and `.options.provider` [`src/redteam/providers/shared.ts:125-155`]().

**`redteamProviderManager.getProvider()` resolution chain**

```mermaid
flowchart TD
  A["getProvider(provider?, jsonOnly, preferSmallModel)"]
  B{"Cached\nthis.provider?"}
  C["Return cached\n(wrapped)"]
  D{"Explicit provider arg\nor cliState.redteam.provider?"}
  E["loadRedteamProvider\n(explicit arg)"]
  F{"defaultTest\nconfig chain?"}
  G["loadRedteamProvider\n(defaultTest provider)"]
  H["Default: new OpenAiChatCompletionProvider\n(ATTACKER_MODEL or ATTACKER_MODEL_SMALL)"]

  A --> B
  B -- "Yes" --> C
  B -- "No" --> D
  D -- "Yes" --> E
  D -- "No" --> F
  F -- "Yes" --> G
  F -- "No" --> H
```

Sources: [`src/redteam/providers/shared.ts:125-155`](), [`src/redteam/providers/shared.ts:197-206`]()

### `getGradingProvider()` — Resolution Priority

Grading (scoring) uses a separate resolution chain, allowing a more capable model to be used for evaluation than for attack generation.

| Priority | Source |
| :--- | :--- |
| 1 | Explicit `provider` argument to `getGradingProvider()` |
| 2 | Cached `this.gradingProvider` / `this.gradingJsonOnlyProvider` |
| 3 | `defaultTest` config chain (same logic as `getProvider`) |
| 4 | Fallback: delegates to `getProvider()` (same model as attack) |

Sources: [`src/redteam/providers/shared.ts:208-230`]()

---

## `TargetResponse` Type

Every attack provider ultimately calls the target through `getTargetResponse()`, which returns a `TargetResponse`. The key distinction from `ProviderResponse` is that `output` is always a `string` (never `undefined` or an object):

```typescript
export type TargetResponse = {
  traceContext?: TraceContextData | null;
  traceSummary?: string;
  image?: {
    data?: string;
    format?: string;
  };
} & Omit<ProviderResponse, 'output'> & {
  output: string;
};
```

Sources: [`src/redteam/providers/shared.ts:246-258`]()

---

## `getTargetResponse()`

`getTargetResponse()` wraps a single call to `targetProvider.callApi()`, normalizes the output to a string, handles provider delays, and returns a `TargetResponse` [`src/redteam/providers/shared.ts:261-331`]().

**`getTargetResponse()` execution flow**

```mermaid
flowchart TD
  A["getTargetResponse(targetProvider, targetPrompt, context, options)"]
  B["targetProvider.callApi(targetPrompt, context, options)"]
  C{"AbortError?"}
  D["Re-throw"]
  E{"cached=false\nand provider.delay > 0?"}
  F["sleep(provider.delay)"]
  G{"hasError in response?"}
  H["Return error TargetResponse\n(output: string or empty)"]
  I{"hasOutput?"}
  J["Stringify output\nReturn TargetResponse"]
  K["throw malformed response error"]

  A --> B
  B --> C
  C -- "Yes" --> D
  C -- "No" --> E
  E -- "Yes" --> F
  F --> G
  E -- "No" --> G
  G -- "Yes" --> H
  G -- "No" --> I
  I -- "Yes" --> J
  I -- "No" --> K
```

Sources: [`src/redteam/providers/shared.ts:261-331`]()

Non-string outputs are serialized with `safeJsonStringify()`. The function always sets `tokenUsage.numRequests = 1` if it is not present [`src/redteam/providers/shared.ts:326-328`]().

---

## `tryUnblocking()`

Some targets respond to adversarial prompts with clarifying questions that block the conversation from progressing. `tryUnblocking()` detects these and generates an answer via the remote generation API [`src/redteam/providers/shared.ts:507-550`]().

### Behavior

1.  Checks `checkServerFeatureSupport('blocking-question-analysis', '2025-06-16T...')` [`src/redteam/providers/shared.ts:515-518`]().
2.  Checks `PROMPTFOO_ENABLE_UNBLOCKING` environment variable — **disabled by default** [`src/redteam/providers/shared.ts:520`]().
3.  If either check fails, returns `{ success: false }` immediately [`src/redteam/providers/shared.ts:521`]().
4.  Otherwise, sends conversation history to the remote generation API via `PromptfooChatCompletionProvider` with task `blocking-question-analysis` [`src/redteam/providers/shared.ts:523-537`]().

**Consumers:** `CrescendoProvider` [`src/redteam/providers/crescendo/index.ts:449-487`]() and `GoatProvider` [`src/redteam/providers/goat.ts:235-305`]() call `tryUnblocking()` after each target turn.

---

## `applyRuntimeTransforms()` and Per-Turn Layers

The `layer` strategy can compose an attack provider with additional per-turn transforms (e.g., audio, base64). When configured, the strategy injects a `_perTurnLayers: LayerConfig[]` array into the attack provider's config [`src/redteam/providers/crescendo/index.ts:145`]().

At each turn, providers call `applyRuntimeTransforms()` from `src/redteam/shared/runtimeTransform.ts`:

```typescript
export async function applyRuntimeTransforms(
  attackPrompt: string,
  injectVar: string,
  perTurnLayers: LayerConfig[],
  Strategies: any,
  context: {
    evaluationId?: string;
    testCaseId?: string;
    purpose?: string;
    goal?: string;
  },
): Promise<TransformResult>
```

**Per-turn layer transform flow**

```mermaid
flowchart LR
  AP["attackPrompt\n(plain text)"]
  ART["applyRuntimeTransforms()\nsrc/redteam/shared/runtimeTransform.ts"]
  TRt["TransformResult\n{ prompt, audio?, image?, error? }"]

  AP --> ART
  ART --> TRt

  TRt --> NA["No audio/image:\nUse TransformResult.prompt\nas targetPrompt"]
  TRt --> HA["Has audio/image:\nBuild hybrid JSON payload\n{ history: prevTurns, currentTurn: { audio/image } }"]
```

Sources: [`src/redteam/providers/crescendo/index.ts:35-39`](), [`src/redteam/providers/iterative.ts:35-39`](), [`src/redteam/providers/goat.ts:36-40`]()

---

## `createIterationContext()`

Multi-iteration providers need to re-run `transformVars` on each iteration to generate fresh values (e.g., a new `sessionId` per attempt).

```typescript
export async function createIterationContext({
  originalVars,
  transformVarsConfig,
  context,
  iterationNumber,
  loggerTag,
}: {
  originalVars: Record<string, VarValue>;
  transformVarsConfig?: TransformFunction | string;
  context?: CallApiContextParams;
  iterationNumber: number;
  loggerTag: string;
}): Promise<CallApiContextParams | undefined>
```

Sources: [`src/redteam/providers/shared.ts:413-466`]()

On each iteration it calls `transform(transformVarsConfig, originalVars, { uuid: randomUUID() }, ...)` and merges the result back into `originalVars` [`src/redteam/providers/shared.ts:441-447`]().

---

## `externalizeResponseForRedteamHistory()`

Before copying a `ProviderResponse` into conversation history, any large binary payloads (base64 images, audio) are extracted and stored externally via the blob storage system.

```typescript
export async function externalizeResponseForRedteamHistory<T extends ProviderResponse>(
  response: T,
  context?: {
    evalId?: string;
    testIdx?: number;
    promptIdx?: number;
  },
): Promise<T>
```

Sources: [`src/redteam/providers/shared.ts:493-505`]()

This calls `extractAndStoreBinaryData()` from `src/blobs/extractor.ts` only when blob storage is enabled or remote blob upload is available [`src/redteam/providers/shared.ts:497-501`]().

---

## Conversation Helpers

| Function | Signature | Purpose |
| :--- | :--- | :--- |
| `isValidChatMessageArray` | `(parsed: unknown) => parsed is Message[]` | Validates JSON is an array of `{role, content}` messages [`src/redteam/providers/shared.ts:340-349`]() |
| `getLastMessageContent` | `(messages, role) => string \| undefined` | Extracts last message of a given role [`src/redteam/providers/shared.ts:351-356`]() |
| `messagesToRedteamHistory` | `(messages) => {prompt, output}[]` | Converts message pairs to history format [`src/redteam/providers/shared.ts:358-387`]() |
| `checkPenalizedPhrases` | `(output: string) => boolean` | Detects hollow compliance phrases (e.g., "yes, I can help you") [`src/redteam/providers/shared.ts:389-399`]() |

---

## `src/redteam/util.ts` — General Red Team Utilities

`src/redteam/util.ts` provides functions used by both providers and plugins.

### Refusal Detection

`isBasicRefusal()` checks if the response starts with common refusal prefixes or matches specific word-boundary patterns like `\bAs an AI\b` or `\bcannot assist with that request\b` [`src/redteam/util.ts:136-212`]().

### Multi-Input Mode Helpers

When the `inputs` config is set, these functions parse the attacker's JSON output:

| Function | Role |
| :--- | :--- |
| `extractPromptFromTags(text)` | Extracts content from the first `<Prompt>...</Prompt>` tag [`src/redteam/util.ts:40-43`]() |
| `extractVariablesFromJson(parsed, inputs)` | Extracts named keys from a parsed JSON object [`src/redteam/util.ts:71-84`]() |
| `extractInputVarsFromPrompt(prompt, inputs)` | Combines tag extraction and JSON variable parsing [`src/redteam/util.ts:113-127`]() |

Sources: [`src/redteam/util.ts:28-127`]()
## Purpose and Scope

The Provider System is the abstraction layer responsible for loading, configuring, and managing LLM integrations across 50+ different APIs and services. It implements a factory pattern that instantiates the appropriate provider class based on configuration strings, file paths, or provider objects.

This document covers:
- Provider loading and resolution mechanisms
- Provider registry and factory pattern
- Major provider categories and implementations
- Authentication and configuration systems
- Provider features (transformations, sessions, token tracking)

For information about how providers are used during evaluation, see [Evaluation Engine](#2.1).

---

## Provider Loading Architecture

### Factory Pattern and Provider Registry

```mermaid
graph TB
    Input["Provider String<br/>providerPath"]
    LoadAPI["loadApiProvider()<br/>src/providers/index.ts"]

    subgraph "Processing Steps"
        RenderEnv["renderEnvOnlyInObject()<br/>Render env vars only<br/>src/util/render.ts"]
        CheckCloud{"isCloudProvider()?<br/>src/util/cloud.ts"}
        CheckFile{"file://*.yaml or<br/>*.json?"}
        ProviderMap["providerMap Registry<br/>src/providers/registry.ts"]
    end

    subgraph "Cloud Provider Flow"
        GetCloud["getProviderFromCloud()<br/>src/util/cloud.ts"]
        MergeConfig["Merge cloud + local config<br/>src/providers/index.ts"]
        RecursiveLoad["Recursive loadApiProvider()<br/>with merged options"]
    end

    subgraph "File Provider Flow"
        ReadConfig["readProviderConfigFile()<br/>src/util/providerRef.ts"]
        ResolveRefs["maybeLoadConfigFromExternalFile()<br/>src/util/file.ts"]
        RecursiveFile["Recursive loadApiProvider()<br/>with file config"]
    end

    subgraph "Factory Matching"
        IterateFactories["for (factory of providerMap)"]
        TestPattern["factory.test(providerPath)"]
        CreateProvider["factory.create(providerPath, options)"]
    end

    Output["ApiProvider Instance"]
    Error["Error: Could not identify provider"]

    Input --> LoadAPI
    LoadAPI --> RenderEnv
    RenderEnv --> CheckCloud

    CheckCloud -->|Yes| GetCloud
    GetCloud --> MergeConfig
    MergeConfig --> RecursiveLoad
    RecursiveLoad --> LoadAPI

    CheckCloud -->|No| CheckFile
    CheckFile -->|Yes| ReadConfig
    ReadConfig --> ResolveRefs
    ResolveRefs --> RecursiveFile
    RecursiveFile --> LoadAPI

    CheckFile -->|No| ProviderMap
    ProviderMap --> IterateFactories
    IterateFactories --> TestPattern
    TestPattern -->|Match| CreateProvider
    CreateProvider --> Output

    TestPattern -->|No Match| IterateFactories
    IterateFactories -->|No factories left| Error
```

**Provider Loading Flow**

The `loadApiProvider()` function is the central entry point. It processes the provider path through several stages:

1.  **Environment Variable Rendering**: Only `{{ env.* }}` templates are rendered at load time using `renderEnvOnlyInObject()`, preserving runtime variable templates like `{{ vars.* }}` for per-test customization [src/providers/index.ts:94-101]().
2.  **Cloud Provider Resolution**: If the path starts with `promptfoo://provider/`, it fetches the provider definition from Promptfoo Cloud via `getProviderFromCloud()`, merges local config overrides, and recursively loads the resolved provider [src/providers/index.ts:120-163]().
3.  **File Provider Loading**: YAML/JSON files are loaded via `readProviderConfigFile()`, their `file://` references resolved recursively via `maybeLoadConfigFromExternalFile()`, and the provider ID is extracted for recursive loading [src/providers/index.ts:165-196]().
4.  **Factory Pattern Matching**: The `providerMap` registry iterates through factories. The first matching factory creates the provider instance [src/providers/registry.ts:138-156]().

Sources: [src/providers/index.ts:83-224](), [src/providers/registry.ts:138-1849](), [src/util/render.ts:20-20](), [src/util/cloud.ts:8-11]()

For details, see [Provider Loading and Registry](#3.1).

---

## Major Provider Categories

### HTTP and Custom Providers

```mermaid
graph TB
    subgraph "HTTP Provider [HttpProvider]"
        Http["src/providers/http.ts"]
        RawMode["Raw HTTP Mode<br/>Full request control"]
        JsonMode["JSON Body Mode<br/>Template substitution"]
        Transform["Request/Response<br/>Transforms"]
    end

    subgraph "Script Providers"
        Python["PythonProvider<br/>src/providers/pythonCompletion.ts"]
        Script["ScriptCompletionProvider<br/>src/providers/scriptCompletion.ts"]
        Ruby["RubyProvider<br/>src/providers/rubyCompletion.ts"]
    end

    subgraph "Execution Architecture"
        PyWorker["PythonWorkerPool<br/>Persistent processes"]
        Wrapper["wrapper.py<br/>Execution bridge"]
        Exec["child_process.spawn()"]
    end

    Http --> RawMode
    Http --> JsonMode
    Http --> Transform

    Python --> PyWorker
    PyWorker --> Wrapper
    Script --> Exec
    Ruby --> Exec
```

**Custom Provider Features**

-   **HTTP Provider**: Flexible provider supporting raw request mode, JSON templating, custom authentication (TLS client certs, digital signatures), and request/response transformations [src/providers/http.ts:48-193]().
-   **Python Provider**: Uses `PythonWorkerPool` for persistent worker processes, avoiding the overhead of spawning a new Python interpreter for every request [src/providers/pythonCompletion.ts:93-93]().
-   **Script Provider**: Executes arbitrary shell commands using `ScriptCompletionProvider` [src/providers/scriptCompletion.ts:101-101]().

Sources: [src/providers/http.ts:48-193](), [src/providers/pythonCompletion.ts:93-93](), [src/providers/scriptCompletion.ts:101-101](), [src/providers/registry.ts:45-101]().

For details, see [HTTP Provider](#3.2) and [Python and Script Providers](#3.7).

---

### Native LLM Integrations

The system includes deep integrations for major model providers, handling their specific message formats, tool calling schemas, and cost calculation logic.

-   **OpenAI**: Supports GPT-4o, o-series reasoning models, and assistant APIs [src/providers/openai/chat.ts:77-77](). For details, see [OpenAI Integration](#3.5).
-   **Anthropic**: Native integration with Claude's message format, thinking blocks, and tool use [src/providers/anthropic/messages.ts:14-14](). For details, see [Anthropic Provider](#3.4).
-   **AWS Bedrock**: Supports multi-vendor models (Claude, Llama, Titan, Nova) with model-specific configurations and Knowledge Base RAG integration [src/providers/registry.ts:141-152](). For details, see [AWS Bedrock Integration](#3.3).
-   **Google/Vertex**: Native integration with Gemini models, multi-modal capabilities, and Model Armor guardrails [src/providers/registry.ts:173-174](). For details, see [Google and Vertex Integration](#3.6).
-   **Moonshot (Kimi)**: OpenAI-compatible provider for Kimi K2 thinking models, handling specific sampling parameter pinning and reasoning content extraction [src/providers/registry.ts:71-71]().
-   **Agent SDKs**: Specialized providers for agentic execution models like the Claude Agent SDK and OpenAI Codex [src/providers/openai/codex-sdk.ts:10-10](). For details, see [Agent SDK Providers](#3.8).

Sources: [src/providers/registry.ts:9-118](), [src/providers/openai/chat.ts:77-77](), [src/providers/anthropic/messages.ts:14-14](), [test/providers.test.ts:9-15]().

---

## Provider Features and Shared Utilities

### Token Usage and Cost Tracking

Token usage is tracked at multiple levels to provide accurate cost and performance metrics.

| Feature | Description | Implementation |
| :--- | :--- | :--- |
| **TokenUsage** | Tracks prompt, completion, and cached tokens | [src/types/shared.ts:1]() |
| **ApiProvider** | Interface for all providers, including `callApi` and optional `callEmbeddingApi` | [src/types/providers.ts:123-140]() |
| **Cost Calculation** | Calculates USD cost based on model-specific rates | [src/providers/shared.ts:38-62]() |
| **Token Usage Utils** | Shared utilities for initializing and managing token counts | [src/util/tokenUsageUtils.ts:36-36]() |

Sources: [src/types/providers.ts:123-140](), [src/types/shared.ts:1](), [src/providers/http.ts:36-36]().

### Request and Response Transformations

Providers support two levels of transformation:
1.  **Request Transforms**: Modify the outgoing request (e.g., adding custom headers or reformatting the body) [src/providers/http.ts:43-43]().
2.  **Response Transforms**: Extract specific data from the model response (e.g., `json.output` to extract a field from a JSON response) [src/providers/http.ts:44-44]().

For details, see [Provider Ecosystem](#3.9).

---

## Summary of Child Pages

-   [Provider Loading and Registry](#3.1): Detailed documentation of `loadApiProvider()`, the `providerMap` registry, and configuration resolution.
-   [HTTP Provider](#3.2): Advanced configuration for the `HttpProvider`, including templating and authentication.
-   [AWS Bedrock Integration](#3.3): Integration with AWS Bedrock Converse API and multi-vendor models.
-   [Anthropic Provider](#3.4): Native Claude integration, message formatting, and extended thinking.
-   [OpenAI Integration](#3.5): GPT-4o, o-series, tool calling, and structured outputs.
-   [Google and Vertex Integration](#3.6): Gemini models, Vertex AI, and AI Studio integrations.
-   [Python and Script Providers](#3.7): Custom execution via Python, shell scripts, and persistent worker pools.
-   [Agent SDK Providers](#3.8): Agentic execution models and SDK integrations.
-   [Provider Ecosystem](#3.9): Survey of additional providers (Ollama, Mistral, Cohere, Moonshot) and shared utilities.
This page documents the architecture and implementation of promptfoo's code-based and script-based provider systems. These providers enable the evaluation of arbitrary logic, the integration of non-HTTP models, and complex multi-turn conversation simulations.

---

## PythonProvider

`PythonProvider` ([src/providers/pythonCompletion.ts:176-195]()) is the primary class for executing user-defined Python scripts. It supports text completion, embeddings, and classification by mapping calls to corresponding functions in a Python script.

### Configuration and ID Resolution
A `PythonProvider` is initialized with a `runPath` which typically follows the format `file://path/to/script.py:function_name`.
- **Path Parsing**: The constructor uses `parsePathOrGlob` to separate the script's file path from the specific function name [src/providers/pythonCompletion.ts:190-195]().
- **ID Generation**: If no explicit ID is provided, it defaults to `python:scriptPath:functionName` [src/providers/pythonCompletion.ts:196-198]().

**PythonProviderConfig** ([src/providers/pythonCompletion.ts:25-30]()):
| Field | Type | Description |
|---|---|---|
| `pythonExecutable` | `string` | Path to a specific Python binary. |
| `workers` | `number` | Number of worker processes to spawn. |
| `timeout` | `number` | Execution timeout in milliseconds. |

### Initialization and Resource Management
`PythonProvider` implements a lazy, idempotent initialization pattern [src/providers/pythonCompletion.ts:213-217]().
1. **File References**: It processes `file://` references within the provider configuration to ensure all local data is loaded before execution [src/providers/pythonCompletion.ts:220-222]().
2. **Concurrency**: It determines the worker pool size by checking `config.workers`, the `PROMPTFOO_PYTHON_WORKERS` environment variable, or falling back to global CLI concurrency [src/providers/pythonCompletion.ts:233-247]().
3. **Worker Pool**: It instantiates a `PythonWorkerPool` which maintains persistent subprocesses [src/providers/pythonCompletion.ts:254-257]().

### Data Flow and Execution
The execution lifecycle for a single `callApi` request follows these steps:
1. **Cache Key Generation**: A SHA-256 hash of the Python script content is generated to ensure that changes to the script invalidate the cache [src/providers/pythonCompletion.ts:289-291]().
2. **Context Sanitization**: The `sanitizeScriptContext` utility is called to remove non-serializable objects (like `winston` logger instances or Nunjucks filter maps) from the `context` object before it is passed across the process boundary [src/providers/pythonCompletion.ts:311-313]().
3. **Pool Dispatch**: The task is submitted to the `PythonWorkerPool` [src/providers/pythonCompletion.ts:321-325]().
4. **Result Validation**: The returned dictionary is validated against the expected schema via `validateCallApiResult`, `validateEmbeddingResult`, or `validateClassificationResult` [src/providers/pythonCompletion.ts:113-154]().

**Diagram: Python Execution Architecture**

```mermaid
graph TD
    subgraph "Node.js Environment"
        PP["PythonProvider (src/providers/pythonCompletion.ts)"]
        WP["PythonWorkerPool (src/python/workerPool.ts)"]
        SSC["sanitizeScriptContext (src/providers/scriptContext.ts)"]
    end

    subgraph "Python Subprocess"
        PW["persistent_wrapper.py (src/python/persistent_wrapper.py)"]
        US["User Script (e.g. echo_provider.py)"]
    end

    PP -->|1. Sanitize| SSC
    PP -->|2. Request| WP
    WP -->|3. stdin: CALL| PW
    PW -->|4. importlib| US
    US -->|5. Result Dict| PW
    PW -->|6. stdout: DONE| WP
    WP -->|7. JSON| PP
```
Sources: [src/providers/pythonCompletion.ts:176-325](), [src/python/workerPool.ts:1-20](), [src/python/persistent_wrapper.py:1-50]()

---

## PythonWorkerPool and Wrapper Mechanism

The `PythonWorkerPool` ([src/python/workerPool.ts]()) is designed to eliminate the overhead of starting a Python interpreter and importing heavy ML libraries (like `torch` or `transformers`) for every test case.

### Persistent Worker Architecture
Each `PythonWorker` ([src/python/worker.ts:19]()) maintains a persistent `PythonShell` instance.
- **Ready Signal**: The worker waits for a `READY` string from the subprocess before accepting calls [src/python/worker.ts:75-84]().
- **Communication**: It uses a pipe-delimited command protocol (`CALL|function|requestFile|responseFile`) to avoid conflicts with Windows drive letters [src/python/worker.ts:153-154]().
- **Reliability**: The pool implements exponential backoff when reading response files to handle OS-level filesystem delays [src/python/worker.ts:168-185]().

### Wrapper Execution Mechanism
The system uses two types of wrappers:
1. **Standard Wrapper**: `runPythonCode` executes snippets by writing to a temporary `script.py` and calling the interpreter [src/python/wrapper.ts:16-40]().
2. **Persistent Wrapper**: `persistent_wrapper.py` stays alive, loading the user script once via `importlib` and using `inspect.iscoroutinefunction` to handle both `async` and `sync` user functions [src/python/persistent_wrapper.py]().

Sources: [src/python/worker.ts:19-204](), [src/python/wrapper.ts:16-40](), [src/python/persistent_wrapper.py:1-100]()

---

## ScriptCompletionProvider

The `ScriptCompletionProvider` ([src/providers/scriptCompletion.ts:57]()) provides a generic interface for executing arbitrary shell commands or non-Python scripts (e.g., Bash, C++, Rust binaries).

### Implementation Details
- **Command Parsing**: It uses `parseScriptParts` to correctly tokenize command strings, respecting single and double quotes [src/providers/scriptCompletion.ts:23-39]().
- **Argument Injection**: It appends the `prompt`, a JSON-serialized `options` object, and a JSON-serialized `context` object as the final three positional arguments to the command [src/providers/scriptCompletion.ts:101-105]().
- **Process Management**: It uses `child_process.execFile` and explicitly closes `stdin` immediately to prevent hanging processes that might block waiting for input [src/providers/scriptCompletion.ts:131-134]().
- **Caching**: It hashes any files detected in the command string to create a robust cache key [src/providers/scriptCompletion.ts:41-55]().

Sources: [src/providers/scriptCompletion.ts:23-137]()

---

## Golang and Ruby Providers

### GolangProvider
The `GolangProvider` ([src/providers/golangCompletion.ts:30]()) automates the lifecycle of Go-based providers.
- **Environment Setup**: It searches for a `go.mod` file to identify the project root [src/providers/golangCompletion.ts:56-65]().
- **Build Pipeline**: It injects a standard `wrapper.go` ([src/esm.ts:59-70]()) and compiles the binary using `go build` [src/providers/golangCompletion.ts:133-147]().
- **Invocation**: The resulting binary is called with JSON-encoded arguments [src/providers/golangCompletion.ts:153-157]().

### RubyProvider
The `RubyProvider` ([src/providers/rubyCompletion.ts]()) executes Ruby scripts, passing serialized JSON data via command-line arguments, similar to the one-shot script execution pattern. It uses a Ruby wrapper script to bridge the Node.js and Ruby environments [src/ruby/rubyUtils.ts]().

Sources: [src/providers/golangCompletion.ts:30-160](), [src/esm.ts:59-70](), [src/providers/rubyCompletion.ts:1-30]()

---

## SimulatedUser

The `SimulatedUser` ([src/providers/simulatedUser.ts:58]()) is a meta-provider used for multi-turn conversation testing. It orchestrates a loop between a "simulated user" and a "target agent".

### Turn-Based Logic
1. **Persona Injection**: It renders user instructions using Nunjucks [src/providers/simulatedUser.ts:102-115]().
2. **User Turn**: It calls `PromptfooSimulatedUserProvider` (a remote or local LLM) to generate a message from the user's perspective [src/providers/simulatedUser.ts:9-10]().
3. **Agent Turn**: It passes that message to the `originalProvider` (the system under test) [src/providers/simulatedUser.ts:209-245]().
4. **Termination**: The loop continues until `maxTurns` is reached or the simulated user generates a termination signal [src/providers/simulatedUser.ts:74]().

**Diagram: SimulatedUser Turn Sequence**

```mermaid
sequenceDiagram
    participant SU as "SimulatedUser (src/providers/simulatedUser.ts)"
    participant SUP as "PromptfooSimulatedUserProvider (src/providers/promptfoo.ts)"
    participant TA as "Target Agent (originalProvider)"

    Note over SU: Loop until maxTurns or STOP
    SU->>SUP: callApi(flippedMessages)
    SUP-->>SU: "Hello, I want to..."
    SU->>TA: callApi(userMessage)
    TA-->>SU: "I cannot assist with..."
    Note over SU: Update History
    SU->>SUP: callApi(updatedHistory)
    SUP-->>SU: "###STOP###"
    SU-->>SU: Terminate Loop
```
Sources: [src/providers/simulatedUser.ts:58-245](), [src/providers/promptfoo.ts:43-161]()

---

## Python Path Resolution

Promptfoo implements a multi-stage discovery strategy to find a valid Python interpreter [src/python/pythonUtils.ts:172-192]():
1. **Explicit Config**: Checks `config.pythonExecutable` [src/python/pythonUtils.ts:48-51]().
2. **Environment**: Checks the `PROMPTFOO_PYTHON` environment variable [src/python/pythonUtils.ts:52-54]().
3. **Windows Logic**: Uses the `where` command but filters out Microsoft Store "stubs" found in `WindowsApps` folders [src/python/pythonUtils.ts:67-92]().
4. **Unix Logic**: Attempts to find `python3`, then falls back to `python` [src/python/pythonUtils.ts:189-191]().
5. **Verification**: Validates the path by running `sys.executable` checks [src/python/pythonUtils.ts:109-139]().

Sources: [src/python/pythonUtils.ts:48-192]()
The red team system in promptfoo is designed to identify vulnerabilities in LLM applications through systematic adversarial testing. It uses a two-phase approach: **generation** (creating adversarial test cases) and **evaluation** (executing those tests and grading the results).

## Two-Phase Architecture

The red team workflow consists of distinct generation and evaluation phases:

**Generation Phase** (`synthesize()` in [src/redteam/index.ts:514-1042]()):
1. Extract system context including `purpose`, `entities`, and `injectVar` [src/redteam/index.ts:742-805]().
2. Execute plugins in parallel to generate base adversarial inputs [src/redteam/index.ts:821-1018]().
3. Apply strategies to transform base inputs into sophisticated attacks [src/redteam/index.ts:1027-1064]().
4. Return enriched test cases with complete metadata and grading rubrics.

**Evaluation Phase** (handled by core eval system):
1. Execute generated test cases against the target LLM [src/redteam/commands/run.ts:114-124]().
2. Apply `RedteamGraderBase` implementations to detect policy violations [src/redteam/graders.ts:1-120]().
3. Generate reports with severity classifications and framework compliance mappings [src/redteam/commands/run.ts:126-135]().

## Core `synthesize()` Function

The `synthesize()` function orchestrates the entire test generation pipeline. It accepts `SynthesizeOptions` [src/redteam/types.ts:72-72]() and returns test cases with extracted context.

### System Architecture Diagram

Title: Red Team System Architecture
```mermaid
graph TB
    subgraph "Command_Layer"
        doGenerateRedteam["doGenerateRedteam()"]
        doRedteamRun["doRedteamRun()"]
    end

    subgraph "Core_Generation"
        synthesize["synthesize()"]
        extractSystemPurpose["extractSystemPurpose()"]
        extractEntities["extractEntities()"]
        extractVariablesFromTemplates["extractVariablesFromTemplates()"]
    end

    subgraph "Plugin_Execution"
        Plugins["Plugins.find()"]
        pluginAction["plugin.action()"]
        CustomPlugin["CustomPlugin"]
        extractGoalFromPrompt["extractGoalFromPrompt()"]
    end

    subgraph "Strategy_Execution"
        applyStrategies["applyStrategies()"]
        Strategies["Strategies.find()"]
        strategyAction["strategy.action()"]
        pluginMatchesStrategyTargets["pluginMatchesStrategyTargets()"]
    end

    subgraph "Provider_System"
        redteamProviderManager["redteamProviderManager"]
        getProvider["getProvider()"]
    end

    subgraph "Configuration"
        RedteamConfigSchema["RedteamConfigSchema"]
        resolveConfigs["resolveConfigs()"]
        validateStrategies["validateStrategies()"]
    end

    doGenerateRedteam --> resolveConfigs
    resolveConfigs --> RedteamConfigSchema
    doGenerateRedteam --> synthesize
    doRedteamRun --> doGenerateRedteam

    synthesize --> extractSystemPurpose
    synthesize --> extractEntities
    synthesize --> extractVariablesFromTemplates
    synthesize --> redteamProviderManager
    synthesize --> validateStrategies

    redteamProviderManager --> getProvider

    synthesize --> Plugins
    Plugins --> pluginAction
    Plugins --> CustomPlugin
    pluginAction --> extractGoalFromPrompt

    synthesize --> applyStrategies
    applyStrategies --> pluginMatchesStrategyTargets
    applyStrategies --> Strategies
    Strategies --> strategyAction
```

**Sources:** [src/redteam/index.ts:514-1042](), [src/redteam/commands/generate.ts:105-628](), [src/redteam/commands/run.ts:18-136]()

## Synthesis Execution Flow

The `synthesize()` function orchestrates test generation through five sequential phases:

### Synthesis Flow Diagram

Title: Red Team Synthesis Execution Flow
```mermaid
flowchart TD
    start["synthesize() Entry"]

    subgraph "Phase_1_Input_Processing"
        validatePrompts["Validate prompts array"]
        expandStrategies["Expand strategy collections"]
        dedupeStrategies["Deduplicate by keyForStrategy()"]
        validateStrategies["validateStrategies()"]
        checkLanguage["Check language disallowed strategies"]
    end

    subgraph "Phase_2_Provider_and_Context"
        getProvider["redteamProviderManager.getProvider()"]
        checkHealth["checkRemoteHealth() if remote"]
        extractPurpose["extractSystemPurpose()"]
        extractEntities["extractEntities()"]
        extractInjectVar["extractVariablesFromTemplates()"]
    end

    subgraph "Phase_3_Plugin_Generation"
        validatePlugin["validatePlugin() for each"]
        expandPlugins["Expand plugin collections"]
        forEachLimit["async.forEachLimit(plugins, maxConcurrency)"]
        findPlugin["Plugins.find()"]
        executeAction["plugin.action()"]
        addPluginMetadata["addLanguageToPluginMetadata()"]
        extractGoal["extractGoalFromPrompt()"]
    end

    subgraph "Phase_4_Strategy_Application"
        retryFirst["Apply retry strategy first"]
        applyStrategies["applyStrategies()"]
        filterApplicable["pluginMatchesStrategyTargets()"]
        executeStrategy["strategy.action()"]
        addStrategyMetadata["Add strategyId, strategyConfig"]
        multilingualLast["Apply multilingual strategy last"]
    end

    subgraph "Phase_5_Result_Assembly"
        combineTests["Combine plugin + strategy test cases"]
        generateReport["generateReport()"]
        returnResult["Return { testCases, purpose, entities, injectVar }"]
    end

    start --> validatePrompts
    validatePrompts --> expandStrategies
    expandStrategies --> dedupeStrategies
    dedupeStrategies --> validateStrategies
    validateStrategies --> checkLanguage

    checkLanguage --> getProvider
    getProvider --> checkHealth
    checkHealth --> extractPurpose
    extractPurpose --> extractEntities
    extractEntities --> extractInjectVar

    extractInjectVar --> validatePlugin
    validatePlugin --> expandPlugins
    expandPlugins --> forEachLimit
    forEachLimit --> findPlugin
    findPlugin --> executeAction
    executeAction --> addPluginMetadata
    addPluginMetadata --> extractGoal

    extractGoal --> retryFirst
    retryFirst --> applyStrategies
    applyStrategies --> filterApplicable
    filterApplicable --> executeStrategy
    executeStrategy --> addStrategyMetadata
    addStrategyMetadata --> multilingualLast

    multilingualLast --> combineTests
    combineTests --> generateReport
    generateReport --> returnResult
```

**Key Code Entities:**

| Entity | Location | Purpose |
|--------|----------|---------|
| `synthesize()` | [src/redteam/index.ts:514-1042]() | Main orchestration function for red team test generation |
| `async.forEachLimit()` | [src/redteam/index.ts:821-1018]() | Parallel plugin execution with concurrency control |
| `applyStrategies()` | [src/redteam/index.ts:246-387]() | Transform base tests with strategies |
| `extractGoalFromPrompt()` | [src/redteam/util.ts:62-62]() | Extract attack goal from each test for strategy guidance |
| `generateReport()` | [src/redteam/index.ts:87-120]() | Create summary of generated tests for CLI output |

**Sources:** [src/redteam/index.ts:514-1042](), [src/redteam/index.ts:246-387](), [src/redteam/index.ts:87-120]()

## Plugin and Strategy Ecosystem

The red team system organizes vulnerabilities into plugins and delivery techniques into strategies.

### Vulnerability Categories (Plugins)
Plugins generate adversarial payloads across several categories [site/docs/_shared/data/plugins.ts:1-8]():
- **Security**: Prompt injection, SQL injection, SSRF, RBAC, Shell Injection [src/redteam/plugins/index.ts:67-72]().
- **Privacy**: PII leaks (direct, session), Cross-session leak [src/redteam/plugins/index.ts:47-61]().
- **Harmful Content**: Hate speech, violence, illegal drugs, weapons (via `harmful` plugin) [src/redteam/plugins/harmful/common.ts:55]().
- **Misinformation & Misuse**: Hallucinations, copyright violations (contracts), competitor endorsements [src/redteam/plugins/index.ts:46-78]().
- **Dataset-backed**: HarmBench, BeaverTails, CybersecEval, Pliny [src/redteam/plugins/index.ts:45-77]().

### Attack Strategies
Strategies transform payloads to bypass filters [src/redteam/strategies/index.ts:56-56]():
- **Encoding**: Base64, Hex, Rot13, Leetspeak, Homoglyphs [src/redteam/constants/strategies.ts:151-168]().
- **Dynamic Single-Turn**: Best-of-N, Citation, Math Prompt, GCG [src/redteam/constants/strategies.ts:169-181]().
- **Multi-turn/Agentic**: Iterative, Goat, Hydra, Tree-based attacks [src/redteam/constants/strategies.ts:188-203]().
- **Custom**: User-defined transformations using Javascript files (`file://`) or natural language instructions [src/validators/redteam.ts:165-184]().

**Sources:** [src/redteam/constants/strategies.ts](), [src/redteam/plugins/index.ts](), [src/redteam/strategies/index.ts](), [site/docs/_shared/data/plugins.ts]()

## Compliance Framework Mappings

Promptfoo maps red team findings to global compliance frameworks to help organizations meet regulatory requirements. Mappings are defined in `FRAMEWORK_COMPLIANCE_IDS` [src/redteam/constants/frameworks.ts:1-20]().

| Framework ID | Framework Name |
|--------------|----------------|
| `owasp:llm` | OWASP Top 10 for LLM Applications |
| `nist:ai:measure` | NIST AI Risk Management Framework |
| `mitre:atlas` | MITRE ATLAS |
| `eu:ai-act` | EU AI Act |
| `iso:42001` | ISO/IEC 42001 (AI Management System) |
| `gdpr` | General Data Protection Regulation |

**Sources:** [src/redteam/constants/frameworks.ts:1-20](), [site/docs/red-team/configuration.md:95-106]()

## Provider Management and Remote Generation

The red team system supports both local and remote test generation through `redteamProviderManager` [src/redteam/providers/shared.ts](). Remote generation allows access to specialized, uncensored models for high-quality attack probes.

Title: Red Team Provider and Remote Generation Flow
```mermaid
graph TB
    subgraph "Provider_Selection"
        configProvider["redteam.provider config"]
        defaultProvider["REDTEAM_MODEL default"]
        redteamProviderManager["redteamProviderManager"]

        configProvider --> redteamProviderManager
        defaultProvider --> redteamProviderManager
    end

    subgraph "Remote_Generation"
        shouldGenerateRemote["shouldGenerateRemote()"]
        remoteHealthCheck["checkRemoteHealth()"]
        remoteGenUrl["getRemoteGenerationUrl()"]
        cloudGeneration["Cloud-based Generation"]

        redteamProviderManager --> shouldGenerateRemote
        shouldGenerateRemote --> remoteHealthCheck
        remoteHealthCheck --> remoteGenUrl
        remoteGenUrl --> cloudGeneration
    end

    subgraph "Local_Generation"
        localProvider["Local Provider"]
        apiProvider["ApiProvider.callApi()"]

        redteamProviderManager --> localProvider
        localProvider --> apiProvider
    end
```

**Sources:** [src/redteam/index.ts:742-760](), [src/redteam/remoteGeneration.ts:23-27](), [src/redteam/providers/shared.ts]()

# Test Generation and Configuration




This page documents how promptfoo's red team system generates adversarial test cases: the `synthesize()` function, the `SynthesizeOptions` and `RedteamConfigSchema` types, plugin and strategy resolution, and the `redteam` configuration block in `promptfooconfig.yaml`.

For general architecture of the red team system (plugins, strategies, graders), see [5.1](). For the full plugin registry and writing custom plugins, see [5.3](). For the CLI commands that invoke generation, see [5.7]().

---

## Overview

The test generation pipeline takes a YAML configuration, resolves plugins and strategies, extracts the target's purpose, and produces a set of `TestCaseWithPlugin` objects. These test cases are then written to `redteam.yaml` and consumed by the evaluation engine.

**Test Generation Data Flow**

```mermaid
flowchart TD
    A["promptfooconfig.yaml\n(redteam section)"] --> B["doGenerateRedteam()\nsrc/redteam/commands/generate.ts"]
    B --> C["RedteamConfigSchema.safeParse()\nsrc/validators/redteam.ts"]
    C --> D["synthesize()\nsrc/redteam/index.ts"]
    D --> E["extractSystemPurpose()\nsrc/redteam/extraction/purpose.ts"]
    D --> F["extractEntities()\nsrc/redteam/extraction/entities.ts"]
    D --> G["Plugins registry\nsrc/redteam/plugins/index.ts"]
    D --> H["applyStrategies()\nsrc/redteam/index.ts"]
    G --> I["TestCaseWithPlugin[]"]
    H --> I
    I --> J["redteam.yaml output"]
```

Sources: [src/redteam/index.ts:700-723](), [src/redteam/commands/generate.ts:19-60](), [src/validators/redteam.ts:48-60]()

---

## The `redteam` Configuration Block

The `redteam` key in `promptfooconfig.yaml` (or a standalone config file) is validated by `RedteamConfigSchema`. The following fields are supported:

| Field | Type | Default | Description |
|---|---|---|---|
| `injectVar` | `string` | Inferred from prompts | Template variable to substitute adversarial content into |
| `purpose` | `string` | Extracted from prompts | Describes the target system; used by plugins to guide generation |
| `testGenerationInstructions` | `string` | — | Additional instructions passed to plugins to guide attack creation |
| `provider` | `string \| object` | `openai:gpt-4o` | LLM used to generate adversarial inputs |
| `plugins` | `RedteamPlugin[]` | `default` | Plugins to run (adversarial generators) |
| `strategies` | `RedteamStrategy[]` | `basic`, `jailbreak:meta`, `jailbreak:composite` | Strategies to apply (attack delivery techniques) |
| `numTests` | `number` | 5 | Default tests per plugin |
| `language` | `string \| string[]` | English | Language(s) for test generation |
| `maxConcurrency` | `number` | 4 | Max parallel plugin generation calls (capped at 20) |
| `delay` | `number` | 0 | Milliseconds between API calls; forces `maxConcurrency = 1` |
| `entities` | `string[]` | Extracted from prompts | Named entities used to make probes realistic |
| `contexts` | `RedteamContext[]` | — | Test contexts for different app states |

### Minimal example

```yaml
redteam:
  purpose: "Customer support chatbot for an e-commerce platform"
  numTests: 10
  plugins:
    - id: harmful:hate
    - id: sql-injection
    - id: pii:direct
      numTests: 3
  strategies:
    - id: jailbreak
    - id: base64
```

Sources: [src/validators/redteam.ts:206-360](), [site/docs/red-team/configuration.md:70-95](), [src/redteam/index.ts:186-203]()

---

## Schema Validation: `RedteamConfigSchema`

`RedteamConfigSchema` is defined in [src/validators/redteam.ts]() and built from composable sub-schemas:

| Schema | Purpose |
|---|---|
| `RedteamPluginObjectSchema` | Validates a single plugin: `{ id, numTests, config, severity }` |
| `RedteamPluginSchema` | Union of string shorthand and `RedteamPluginObjectSchema` |
| `RedteamStrategySchema` | Union of string shorthand and `{ id, config }` object |
| `strategyIdSchema` | Validates strategy IDs against `ALL_STRATEGIES` or `file://` paths |
| `RedteamConfigSchema` | Top-level schema composing the above |
| `RedteamGenerateOptionsSchema` | Schema for the `redteam generate` CLI command options |

Plugin `id` validation accepts:
- Any member of `pluginOptions` (built-in plugins and collections like `owasp:llm`) [src/validators/redteam.ts:85-111]()
- A string starting with `file://` (custom plugin path) [src/validators/redteam.ts:102-110]()

Strategy `id` validation accepts:
- Any member of `ALL_STRATEGIES` [src/validators/redteam.ts:153-164]()
- A `file://` path ending in `.js` or `.ts` [src/validators/redteam.ts:165-176]()
- A custom strategy identifier (via `isCustomStrategy()`) [src/validators/redteam.ts:177-185]()

Sources: [src/validators/redteam.ts:85-198](), [src/validators/redteam.ts:206-250]()

---

## Plugin and Strategy Types

**Type Hierarchy**

```mermaid
classDiagram
    class RedteamPluginObject {
        +id: string
        +numTests: number
        +config: PluginConfig
        +severity: Severity
    }
    class RedteamStrategyObject {
        +id: string
        +config: StrategyConfig
    }
    class PluginConfig {
        +language: string|string[]
        +modifiers: Record~string,unknown~
        +examples: string[]
        +graderExamples: GraderExample[]
        +excludeStrategies: string[]
        +inputs: Inputs
    }
    class StrategyConfig {
        +enabled: boolean
        +plugins: string[]
        +numTests: number
    }
    class SynthesizeOptions {
        +plugins: RedteamPluginObject[]
        +strategies: RedteamStrategyObject[]
        +prompts: string[]
        +numTests: number
        +language: string|string[]
        +purpose: string
        +entities: string[]
        +injectVar: string
        +maxConcurrency: number
        +targetIds: string[]
    }
    SynthesizeOptions --> RedteamPluginObject
    SynthesizeOptions --> RedteamStrategyObject
    RedteamPluginObject --> PluginConfig
    RedteamStrategyObject --> StrategyConfig
```

Sources: [src/redteam/types.ts:55-165](), [src/redteam/types.ts:169-180](), [src/redteam/index.ts:70-73]()

---

## Plugin Collections and Expansion

Named collections expand to lists of individual plugin IDs at resolution time. This happens via `ALIASED_PLUGIN_MAPPINGS` and `COLLECTIONS`.

| Collection | Description | Source |
|---|---|---|
| `harmful` | All keys of `HARM_PLUGINS` | [src/redteam/constants/plugins.ts]() |
| `pii` | All entries of `PII_PLUGINS` | [src/redteam/constants/plugins.ts]() |
| `foundation` | All entries of `FOUNDATION_PLUGINS` | [src/redteam/constants/plugins.ts]() |
| `medical` | All entries of `MEDICAL_PLUGINS` | [src/redteam/constants/plugins.ts]() |
| `nist:ai:measure` | NIST AI RMF mapping | [src/redteam/constants/frameworks.ts]() |
| `owasp:llm` | OWASP Top 10 for LLMs mapping | [src/redteam/constants/frameworks.ts]() |

Strategy collections similarly expand. In `synthesize()`, any strategy whose `id` matches a key in `STRATEGY_COLLECTION_MAPPINGS` is expanded into constituent strategy IDs [src/redteam/index.ts:32-36]().

Sources: [src/redteam/index.ts:15-36](), [src/validators/redteam.ts:3-26]()

---

## `doGenerateRedteam()`: Configuration Resolution

`doGenerateRedteam()` in [src/redteam/commands/generate.ts:19]() orchestrates everything before `synthesize()` is called.

**`doGenerateRedteam()` Resolution Steps**

```mermaid
flowchart TD
    A["CLI invocation or\nweb UI trigger"] --> B{"configFromCloud?"}
    B -- "yes" --> C["Write cloud config\nto temp .yaml file"]
    B -- "no" --> D{"Config file exists?"}
    C --> E["resolveConfigs()"]
    D -- "yes" --> F{"Hash changed?"}
    F -- "no, --force absent" --> G["Return cached\nredteam.yaml"]
    F -- "yes" --> E
    D -- "no" --> H{"purpose provided?"}
    H -- "yes" --> I["Use stub TestSuite"]
    H -- "no" --> J["Error: run redteam init"]
    E --> K["Extract redteamConfig\nfrom resolved config"]
    I --> K
    K --> L["Build plugins[]\nfrom config or DEFAULT_PLUGINS"]
    L --> M["Apply cloud severity\noverrides if cloud provider"]
    M --> N["Resolve policy\nreferences from cloud"]
    N --> O["Build strategies[]\nfrom config or DEFAULT_STRATEGIES"]
    O --> P["RedteamConfigSchema.safeParse()"]
    P --> Q["extractMcpToolsInfo()\nappend to purpose"]
    Q --> R["synthesize()"]
    R --> S["Handle failedPlugins\n(warn or throw if --strict)"]
    S --> T["Write redteam.yaml\nwith header comments"]
```

Sources: [src/redteam/commands/generate.ts:19-118](), [src/redteam/commands/generate.ts:170-195]()

---

## `synthesize()`: Core Test Generation

`synthesize()` is the central function that produces adversarial test cases.

**`synthesize()` Internal Flow**

```mermaid
flowchart TD
    A["synthesize(SynthesizeOptions)"] --> B["Validate inputs\n(prompts non-empty,\nconcurrency limits)"]
    B --> C["Expand strategy collections\nvia STRATEGY_COLLECTION_MAPPINGS"]
    C --> D["Deduplicate strategies\nvia keyForStrategy()"]
    D --> E["validateStrategies()\nvalidateSharpDependency()"]
    E --> F["redteamProviderManager\n.getProvider()"]
    F --> G["calculateTotalTests(\nplugins, strategies, language)"]
    G --> H{"purpose provided?"}
    H -- "no" --> I["extractSystemPurpose(\nprovider, prompts)"]
    H -- "yes" --> J["Use provided purpose"]
    I --> K
    J --> K
    K{"entities provided?"} -- "no" --> L["extractEntities(\nprovider, prompts)"]
    K -- "yes" --> M["Use provided entities"]
    L --> N
    M --> N
    N["Resolve injectVar\nfrom prompts if absent"] --> O["async.queue(\nworker, maxConcurrency)"]
    O --> P["For each plugin:\nfind in Plugins[]\ncall plugin.action()"]
    P --> Q["addLanguageToPluginMetadata()\nattach pluginId, severity"]
    Q --> R["applyStrategies(\ntestCases, strategies, injectVar)"]
    R --> S["generateReport()\nlog to console"]
    S --> T["Return {purpose, entities,\ntestCases, injectVar, failedPlugins}"]
```

Sources: [src/redteam/index.ts:114-185](), [test/redteam/index.test.ts:133-180]()

### Concurrency and rate limiting

- `maxConcurrency` defaults to 4; capped at `MAX_MAX_CONCURRENCY = 20` [src/redteam/index.ts:187](), [site/docs/red-team/configuration.md:93]()
- If `delay` is set, `maxConcurrency` is forced to 1 [site/docs/red-team/configuration.md:94]()
- Plugin generation tasks are queued with `async.queue()` from the `async` library [src/redteam/index.ts:3]()

Sources: [src/redteam/index.ts:187](), [site/docs/red-team/configuration.md:93-94]()

---

## Multi-Input Materialization

For targets with multiple input variables, promptfoo uses a materialization process to map single adversarial strings into complex JSON structures or multi-variable sets.

- `rematerializeStrategyInputVars()`: Re-parses adversarial inputs to extract specific variables if `inputs` configuration is provided [src/redteam/index.ts:114-185]().
- `extractMaterializedVariablesFromJsonWithMetadata()`: Extracts variables from JSON responses to populate `TestCase.vars` [src/redteam/index.ts:156-165]().

Sources: [src/redteam/index.ts:114-185]()

---

## Metadata Attached to Generated Test Cases

Every generated `TestCase` has a `metadata` object populated during generation.

| Metadata Key | Set by | Description |
|---|---|---|
| `pluginId` | `synthesize()` | Short plugin ID (e.g. `harmful:hate`) |
| `pluginConfig` | `computeModifiersFromConfig()` | Resolved plugin config including modifiers |
| `severity` | `getPluginSeverity()` | `Severity` enum value (`Low`, `Medium`, `High`, `Critical`) |
| `strategyId` | `applyStrategies()` | Strategy that produced this variant |
| `inputMaterialization` | `rematerializeStrategyInputVars()` | Materialized variables for multi-input testing |

Severity defaults come from `riskCategorySeverityMap` and can be overridden per plugin or via cloud severity override profiles.

Sources: [src/redteam/index.ts:195-204](), [src/redteam/plugins/index.ts:114-132](), [src/redteam/index.ts:114-184]()

---

## Strict Mode and Partial Generation Errors

By default, if a plugin generates zero test cases, `synthesize()` logs a warning and continues. With the `--strict` flag, `handleFailedPlugins()` [src/redteam/commands/generate.ts:85-118]() throws a `PartialGenerationError` instead, halting the run.

`PartialGenerationError` carries a `failedPlugins: FailedPluginInfo[]` array, where each entry has `{ pluginId, requested }`.

Sources: [src/redteam/commands/generate.ts:85-118](), [src/redteam/commands/generate.ts:64]()
The Red Team Report UI provides a comprehensive visualization of adversarial evaluation results. It transforms raw evaluation data into an executive-style dashboard that highlights vulnerabilities, strategy effectiveness, and compliance with security frameworks.

## Overview and Data Flow

The Red Team Report is a specialized view within the promptfoo web application, accessible via the `/reports` route [src/app/src/App.tsx:120](). It operates in two modes: a list view (`ReportIndex`) for browsing historical reports and a detail view (`Report`) for analyzing specific evaluation IDs [src/app/src/pages/redteam/report/page.tsx:33]().

### Component Hierarchy

The report interface is composed of several specialized components that consume a unified data state derived from evaluation results.

| Component | Responsibility |
| :--- | :--- |
| `Report.tsx` | Main container; handles API fetching, data processing, and global filtering [src/app/src/pages/redteam/report/components/Report.tsx:72](). |
| `Overview.tsx` | High-level summary of vulnerabilities categorized by severity [src/app/src/pages/redteam/report/components/Report.tsx:53](). |
| `TestSuites.tsx` | Detailed table of plugins, risk scores, and attack success rates (ASR) [src/app/src/pages/redteam/report/components/TestSuites.tsx:59](). |
| `RiskCategoryDrawer.tsx` | Slide-out panel for inspecting specific test cases, prompts, and outputs for a plugin [src/app/src/pages/redteam/report/components/RiskCategoryDrawer.tsx:136](). |
| `StrategyStats.tsx` | Breakdown of which adversarial strategies (e.g., jailbreak, PII) were most effective [src/app/src/pages/redteam/report/components/StrategyStats.tsx:35](). |
| `FrameworkCompliance.tsx` | Mapping of results to external standards like OWASP LLM Top 10 or NIST AI RMF [src/app/src/pages/redteam/report/components/FrameworkCompliance.tsx:30](). |

### Data Retrieval Implementation

The report fetches data using the `callApi` utility [src/app/src/pages/redteam/report/components/Report.tsx:30](). If an `evalId` is provided in the URL search parameters, it fetches that specific result; otherwise, it retrieves the latest evaluation from the `/results` endpoint [src/app/src/pages/redteam/report/components/Report.tsx:95-149]().

**Data Flow Diagram**
```mermaid
sequenceDiagram
    participant UI as "Report.tsx"
    participant API as "Backend API (/results)"
    participant Store as "useReportStore (Zustand)"

    UI->>API: "callApi('/results/:id')"
    API-->>UI: "Returns SharedResults (ResultsFile)"
    UI->>UI: "convertResultsToTable()"
    UI->>UI: "Process failuresByPlugin & passesByPlugin"
    UI->>Store: "setPluginPassRateThreshold()"
    UI->>UI: "Calculate categoryStats"
```

**Sources:**
- [src/app/src/pages/redteam/report/components/Report.tsx:72-149]()
- [src/app/src/pages/redteam/report/page.tsx:33]()
- [src/app/src/pages/redteam/report/components/Report.test.tsx:103-143]()

## Risk Category Visualization

The report organizes findings by "Plugins" (vulnerability categories). Each category is assigned a severity and a risk score calculated based on the impact and the complexity of the successful attacks.

### Severity and Risk Scoring
Severity is mapped from the plugin definition. The `TestSuites` component calculates a `riskScore` using the `calculatePluginRiskScore` utility [src/app/src/pages/redteam/report/components/TestSuites.tsx:25](), which factors in the severity and the `complexityScore` of the attack strategy used [src/app/src/pages/redteam/report/components/TestSuites.tsx:121-146]().

- **Critical/High/Medium/Low**: Visualized using color-coded badges and cards. The UI uses `getSeverityColor` to determine visual styling [src/app/src/pages/redteam/report/components/TestSuites.tsx:31]().
- **Attack Success Rate (ASR)**: The percentage of adversarial attempts that successfully bypassed model safeguards, calculated via `calculateAttackSuccessRate` [src/app/src/pages/redteam/report/components/TestSuites.tsx:170]().

### Detailed Inspection (RiskCategoryDrawer)
When a user selects a specific category in `TestSuites`, the `RiskCategoryDrawer` opens. It displays:
1. **Pass/Fail Stats**: A summary of total tests vs. successful attacks [src/app/src/pages/redteam/report/components/RiskCategoryDrawer.tsx:168-170]().
2. **Conversation History**: Full multi-turn interactions for failed tests, reconstructed from `redteamHistory` or `redteamTreeHistory` metadata via `buildChatMessages` [src/app/src/pages/redteam/report/components/RiskCategoryDrawer.tsx:99-134]().
3. **Suggestions**: Remediation advice generated by the grading engine, extracted from `gradingResult.componentResults` [src/app/src/pages/redteam/report/components/RiskCategoryDrawer.tsx:192-194]().

**Sources:**
- [src/app/src/pages/redteam/report/components/TestSuites.tsx:47-177]()
- [src/app/src/pages/redteam/report/components/RiskCategoryDrawer.tsx:99-196]()
- [src/app/src/pages/redteam/report/components/shared.ts:1-21]()

## Strategy Effectiveness

Adversarial strategies (e.g., `jailbreak:composite`, `pliny`, `prompt-injections`) are analyzed in `StrategyStats.tsx`. This allows developers to understand which attack vectors their model is most susceptible to.

- **ASR per Strategy**: Calculates how often a specific strategy succeeded across all plugins by iterating through `succeededAttacksByPlugin` and `failedAttacksByPlugin` [src/app/src/pages/redteam/report/components/StrategyStats.tsx:54-89]().
- **Visualization**: Uses red-toned progress bars via `getProgressBarColor` where higher success (for the attacker) indicates higher risk [src/app/src/pages/redteam/report/components/StrategyStats.tsx:22-33]().

**Sources:**
- [src/app/src/pages/redteam/report/components/StrategyStats.tsx:22-192]()

## Framework Compliance

The `FrameworkCompliance` component maps internal plugin results to industry-standard security frameworks.

### Compliance Mapping Logic
Mappings are defined in `ALIASED_PLUGIN_MAPPINGS` [src/app/src/pages/redteam/report/components/FrameworkCompliance.tsx:7](). The UI determines compliance by checking if the pass rate for all plugins associated with a framework requirement exceeds the `pluginPassRateThreshold` (managed in the report store) [src/app/src/pages/redteam/report/components/FrameworkCompliance.tsx:63-68]().

**Framework Mapping Diagram**
```mermaid
graph TD
    subgraph "Natural Language Space"
        NIST["NIST AI RMF"]
        OWASP["OWASP Top 10 for LLM"]
    end

    subgraph "Code Entity Space"
        FC["FrameworkCompliance.tsx"]
        MAP["ALIASED_PLUGIN_MAPPINGS"]
        STATS["categoryStats (Record<string, TestResultStats>)"]
        UTIL["categorizePlugins()"]

        FC --> MAP
        MAP -->|"Lookup Plugins"| STATS
        STATS --> UTIL
        UTIL -->|"Pass Rate < Threshold"| NON_COMPLIANT["Non-Compliant Status"]
    end

    NIST -.->|"Mapped via"| MAP
    OWASP -.->|"Mapped via"| MAP
```

### Features
- **CSV Export**: Allows exporting compliance data for auditing purposes via `FrameworkCsvExporter.tsx` [src/app/src/pages/redteam/report/components/FrameworkCompliance.tsx:183-187]().
- **Severity Aggregation**: The overall severity of a framework violation is determined by the highest severity of its non-compliant plugins [src/app/src/pages/redteam/report/components/FrameworkCompliance.tsx:73-102]().

**Sources:**
- [src/app/src/pages/redteam/report/components/FrameworkCompliance.tsx:30-192]()
- [src/app/src/pages/redteam/report/components/FrameworkComplianceUtils.ts:1-19]()

## State Management

The report uses a specialized Zustand store, `useReportStore`, to manage UI state across the various components [src/app/src/pages/redteam/report/components/Report.tsx:59]().

| State Property | Description |
| :--- | :--- |
| `pluginPassRateThreshold` | The percentage (0.0 - 1.0) required for a plugin to be considered "passed" [src/app/src/pages/redteam/report/components/Report.tsx:82](). |
| `severityFilter` | Current filter applied to the Overview and TestSuites (e.g., only show 'Critical') [src/app/src/pages/redteam/report/components/TestSuites.tsx:68](). |
| `showUntestedPlugins` | Toggle to display or hide categories that were not included in the eval [src/app/src/pages/redteam/report/components/FrameworkCompliance.tsx:31](). |

**Sources:**
- [src/app/src/pages/redteam/report/components/Report.tsx:82]()
- [src/app/src/pages/redteam/report/components/TestSuites.tsx:68]()
- [src/app/src/pages/redteam/report/components/FrameworkCompliance.tsx:31]()

## UI Interaction Diagram

The following diagram illustrates how a user navigates from the high-level overview to specific failure logs.

```mermaid
graph LR
    Overview["Overview.tsx (Severity Cards)"] -- "handleNavigateToVulnerabilities()" --> Filter["setSeverityFilter() in useReportStore"]
    Filter --> Table["TestSuites.tsx (Filtered Rows)"]
    Table -- "Click Row" --> Drawer["RiskCategoryDrawer.tsx"]
    Drawer -- "Click View All Logs" --> EvalView["ResultsView.tsx (Full Eval Table)"]

    subgraph "Navigation Logic"
        NAV["useNavigate()"]
        ROUTE["EVAL_ROUTES.EVAL_DETAIL"]
    end

    Table --> NAV
    NAV --> ROUTE
```

**Sources:**
- [src/app/src/pages/redteam/report/components/Report.tsx:73]()
- [src/app/src/pages/redteam/report/components/TestSuites.tsx:67-69]()
- [src/app/src/pages/redteam/report/components/RiskCategoryDrawer.tsx:146-154]()

# Model Audit UI




The Model Audit UI provides a web-based interface for the `promptfoo scan-model` capability. It allows users to perform static security analysis on machine learning models to detect malicious code, unsafe operations, and configuration risks across various formats (PyTorch, TensorFlow, ONNX, etc.). The interface facilitates path selection, advanced scanner configuration, real-time progress monitoring, and historical result management.

## System Architecture

The Model Audit UI bridges the React-based frontend with the underlying `modelaudit` Python package via an Express backend. The backend manages the lifecycle of the scanning process by spawning `modelaudit` as a subprocess.

### Component Relationship Diagram

This diagram shows how UI components interact with the Zustand state and the backend API routes.

```mermaid
graph TD
    subgraph "Frontend (React + Zustand)"
        SetupPage["ModelAuditSetupPage"]
        HistoryPage["ModelAuditHistoryPage"]
        ConfigStore["useModelAuditConfigStore"]
        PathSel["PathSelector"]
        AdvOpts["AdvancedOptionsDialog"]
        Results["ResultsTab"]
    end

    subgraph "Backend (Express)"
        Router["modelAuditRouter"]
        CheckInstalled["GET /check-installed"]
        CheckPath["POST /check-path"]
        ScanRoute["POST /scan"]
    end

    subgraph "External"
        MA_CLI["modelaudit CLI"]
    end

    SetupPage --> PathSel
    SetupPage --> AdvOpts
    SetupPage --> ConfigStore
    PathSel --> CheckPath
    AdvOpts --> Router
    SetupPage --> ScanRoute
    ScanRoute --> MA_CLI
    HistoryPage --> Router
    Results --> ScanStatistics
```
**Sources:** [src/app/src/App.tsx:80-111](), [src/server/routes/modelAudit.ts:21-200](), [src/types/api/modelAudit.ts:8-105]()

## Scan Configuration

Users configure scans through a multi-step process involving path validation and advanced parameter tuning.

### Path Selection and Validation
The `PathSelector` component allows users to specify local files or directories. It communicates with the `POST /api/model-audit/check-path` endpoint to verify the existence and type of the provided path.
*   **Path Verification:** The backend uses `fs.stat` to confirm if a path exists and determines if it is a `file` or `directory` [src/server/routes/modelAudit.ts:171-179]().
*   **Home Directory Expansion:** Both the path check and the scan execution handle `~/` expansion to the user's home directory [src/server/routes/modelAudit.ts:160-163](), [src/server/routes/modelAudit.ts:224-226]().
*   **Remote Sources:** While the UI facilitates local selection, the underlying system supports `hf://`, `s3://`, `gs://`, and `models:/` protocols for remote scanning [site/docs/model-audit/index.md:118-126]().

### Advanced Options
The `AdvancedOptionsDialog` manages the fine-grained configuration of the `modelaudit` engine.
*   **Scanner Catalog:** The UI fetches available scanners via `GET /api/model-audit/scanners` [src/server/routes/modelAudit.ts:109-146](). This returns a list of `ScannerInfo` including IDs, descriptions, and supported extensions [src/types/api/modelAudit.ts:20-28]().
*   **Blacklist Patterns:** Users can define regex patterns for disallowed model names or strings [src/types/api/modelAudit.ts:73-73]().
*   **Resource Limits:** Configuration for `timeout` (seconds) and `maxSize` (e.g., "1GB") are passed to the scanner to prevent resource exhaustion [src/types/api/modelAudit.ts:74-86]().
*   **Scanner Control:** Users can explicitly include specific scanners via `scanners` or remove noisy ones via `excludeScanner` [src/types/api/modelAudit.ts:87-88]().

**Sources:** [src/server/routes/modelAudit.ts:109-146](), [src/types/api/modelAudit.ts:43-105](), [site/docs/model-audit/index.md:169-189]()

## State Management

The `useModelAuditConfigStore` is a Zustand store that persists configuration and scan history in the browser. It utilizes the types defined in `ModelAudit.types.ts` to maintain consistency with the backend schemas.

| State Property | Type | Purpose |
| :--- | :--- | :--- |
| `recentScans` | `RecentScan[]` | Persists metadata of previously executed scans in localStorage [src/app/src/pages/model-audit/ModelAudit.types.ts:17-22](). |
| `scanOptions` | `ScanOptions` | Stores current global configuration like `blacklist`, `timeout`, and `strict` [src/app/src/pages/model-audit/ModelAudit.types.ts:34-50](). |
| `installationStatus` | `InstallationStatus` | Tracks if the `modelaudit` CLI is available on the host system [src/app/src/pages/model-audit/ModelAudit.types.ts:27-32](). |

**Sources:** [src/app/src/pages/model-audit/ModelAudit.types.ts:5-50](), [src/app/src/pages/model-audit/stores/useModelAuditConfigStore.ts:1-20]()

## Backend Execution Flow

The backend acts as a bridge, translating HTTP requests into CLI commands.

### Scan Subprocess Logic
When a scan is initiated via `POST /api/model-audit/scan`, the server:
1.  **Validation:** Validates the request body against `ScanRequestSchema` [src/server/routes/modelAudit.ts:196-200]().
2.  **Path Resolution:** Resolves relative paths to absolute locations on the host filesystem [src/server/routes/modelAudit.ts:215-231]().
3.  **Argument Parsing:** Maps UI options to CLI arguments using `parseModelAuditArgs` [src/util/modelAuditCliParser.ts:142-182](). This function handles boolean flags (e.g., `--strict`), strings, and arrays (e.g., multiple `--blacklist` entries) [src/util/modelAuditCliParser.ts:156-178]().
4.  **Delegation:** Spawns the `modelaudit` process with `PROMPTFOO_DELEGATED: 'true'` to signal it is being run by promptfoo [src/server/routes/modelAudit.ts:28-33]().
5.  **Output Capture:** Captures `stdout` and `stderr` using `StringDecoder` to handle real-time streams [src/server/routes/modelAudit.ts:40-89]().

### Process Flow Diagram

```mermaid
sequenceDiagram
    participant UI as ModelAuditSetupPage
    participant API as modelAuditRouter
    participant DB as SQLite (ModelAudit Model)
    participant CLI as modelaudit (Python)

    UI->>API: POST /scan {paths, options}
    API->>API: parseModelAuditArgs()
    API->>CLI: spawn("modelaudit", ["scan", ...])
    CLI-->>API: JSON Output (stdout)
    API->>DB: ModelAudit.create()
    DB-->>API: Persisted Record
    API-->>UI: Scan Results + auditId
```
**Sources:** [src/server/routes/modelAudit.ts:195-280](), [src/util/modelAuditCliParser.ts:142-182](), [src/commands/modelScan.ts:1-150]()

## Results and Statistics

Once a scan completes, results are displayed using the `ResultsTab` and `ScanStatistics` components, mapping the `ModelAuditScanResults` data structure to UI elements.

*   **ScanStatistics:** Summarizes the scan using `total_checks`, `passed_checks`, and `failed_checks`. It also displays `bytes_scanned` and `duration` [src/types/modelAudit.ts:83-86]().
*   **Findings Display:** Issues are categorized by severity (`critical`, `error`, `warning`, `info`). Each `ModelAuditIssue` includes a `message`, `location`, and a `why` field explaining the security risk [src/types/modelAudit.ts:12-19]().
*   **Asset Inspection:** The UI lists `assets` detected within the model, such as embedded shared libraries or configuration files [src/types/modelAudit.ts:21-25]().
*   **Historical Audits:** The `ListScansResponseSchema` defines the structure for paginated historical results, allowing users to sort by `createdAt`, `failedChecks`, or `modelPath` [src/types/api/modelAudit.ts:128-179]().

### Versioning and Updates
The UI checks for `modelaudit` updates by comparing the local version against PyPI.
*   **Local Version Check:** Executes `modelaudit --version` and parses the output [src/updates.ts:89-98]().
*   **Remote Version Check:** Fetches metadata from `https://pypi.org/pypi/modelaudit/json` [src/updates.ts:70-87]().
*   **CLI UI Support:** The `supportsCliUiWithOutput` helper determines if the installed version supports advanced UI features based on semver [src/commands/modelScan.ts:104-113]().

**Sources:** [src/types/modelAudit.ts:62-105](), [src/types/api/modelAudit.ts:139-180](), [src/updates.ts:70-128](), [src/commands/modelScan.ts:104-113]()

# Sharing and Cloud Integration




This page covers how promptfoo uploads evaluation results to a remote server, generates shareable URLs, and manages authenticated access to the promptfoo Cloud service. It includes the sharing pipeline for both standard evaluations and model audits, the `CloudConfig` singleton, cloud API utilities, and the `auth` CLI commands.

For details on the CLI commands that trigger sharing (e.g., `promptfoo eval --share`, `promptfoo share`), see page [CLI System](#4). For details on the web UI that displays shared evaluations, see page [Web Interface](#6). For details on self-hosting the promptfoo server, see page [Self-Hosting and Deployment](#9.4).

---

## System Overview

The sharing and cloud integration system has three distinct concerns that work together:

1.  **Sharing** — uploading eval results or model audit results to a remote server and returning a URL.
2.  **Cloud Configuration** — storing and retrieving the API key, API host, app URL, and team/org context.
3.  **Cloud API Utilities** — making authenticated HTTP calls to the cloud API for providers, configs, permissions, etc.

**System context diagram**

```mermaid
graph TD
    CLI["CLI Commands\n(share, auth, eval)"]
    Share["src/share.ts\ncreateShareableUrl\ncreateShareableModelAuditUrl"]
    CloudCfg["src/globalConfig/cloud.ts\nCloudConfig singleton"]
    CloudUtil["src/util/cloud.ts\nmakeRequest\ncheckCloudPermissions"]
    RemoteAPI["Remote API\n(promptfoo.app or self-hosted)"]
    GlobalCfg["src/globalConfig/globalConfig.ts\nreadGlobalConfig"]

    CLI --> Share
    CLI --> CloudCfg
    Share --> CloudCfg
    Share --> CloudUtil
    CloudUtil --> CloudCfg
    CloudUtil --> RemoteAPI
    Share --> RemoteAPI
    CloudCfg --> GlobalCfg
```

Sources: [src/share.ts:1-24](), [src/util/cloud.ts:1-17](), [src/globalConfig/cloud.ts:1-13]()

---

## Sharing System

For a deep dive into the chunked upload mechanism and rollback logic, see [Sharing System](#7.1).

### Entry Points

| Function | File | Purpose |
| :--- | :--- | :--- |
| `createShareableUrl()` | `src/share.ts` | Share an `Eval` record, return URL |
| `createShareableModelAuditUrl()` | `src/share.ts` | Share a `ModelAudit` record, return URL |
| `isSharingEnabled()` | `src/share.ts` | Check whether sharing is configured for an eval |
| `isModelAuditSharingEnabled()` | `src/share.ts` | Check whether model audit sharing is configured |
| `hasEvalBeenShared()` | `src/share.ts` | Check if an eval already exists on the remote |
| `hasModelAuditBeenShared()` | `src/share.ts` | Check if a model audit already exists on the remote |

Sources: [src/share.ts:53-73](), [src/share.ts:75-89](), [src/commands/share.ts:25-38](), [src/commands/share.ts:40-53]()

### `isSharingEnabled()` Logic

The function checks three sources in order. Any one being truthy returns `true`:

1.  `eval.config.sharing.apiBaseUrl` is set (per-eval config) [src/share.ts:54-55]().
2.  `getShareApiBaseUrl()` returns a URL that does **not** contain `api.promptfoo.app` (i.e., it is a custom self-hosted URL) [src/share.ts:56-66]().
3.  `cloudConfig.isEnabled()` returns `true` (an API key is present) [src/share.ts:58-70]().

Sources: [src/share.ts:53-73]()

### Chunked Upload Mechanism

`sendChunkedResults` (invoked via `createShareableUrl`) handles large eval result sets by calculating an adaptive chunk size based on the largest result sample [src/share.ts:111-122](). It handles network timeouts or payload size errors by recursively splitting chunks in half. Large media assets are handled via `uploadBlobRefsForShare` or `inlineBlobRefsForShare` before upload [src/share.ts:7](), [src/share.ts:19]().

Sources: [src/share.ts:111-122](), [src/share.ts:7](), [src/share.ts:19]()

---

## Cloud Configuration

For details on API key management and team context, see [Cloud Configuration](#7.2).

### `CloudConfig` Class

The `CloudConfig` class is a singleton in `src/globalConfig/cloud.ts`, backed by the global config file (`~/.promptfoo/promptfoo.yaml`) [src/globalConfig/cloud.ts:94-95](). It manages the `apiKey`, `apiHost`, and `appUrl` used for all cloud interactions [src/globalConfig/cloud.ts:73-92]().

**CloudConfig data structure**

```mermaid
classDiagram
    class CloudConfig {
        -configState CloudConfigState
        +isEnabled() bool
        +getApiKey() string
        +getApiHost() string
        +getAppUrl() string
        +validateApiToken(token, host) Promise
        +getCurrentOrganizationId() string
        +setCurrentOrganization(id)
        +getCurrentTeamId(orgId?) string
        +setCurrentTeamId(teamId, orgId?)
    }
    class GlobalConfig {
        id string
        cloud CloudConfigState
    }
    CloudConfig --> GlobalConfig : "reads via readGlobalConfig"
```

Sources: [src/globalConfig/cloud.ts:94-124](), [src/globalConfig/accounts.ts:52-61]()

### Authentication and Teams

Authentication is handled via the `auth` CLI command group [src/commands/auth.ts:55-57](). Users can login via API key or browser [src/commands/auth.ts:85](), [src/commands/auth.ts:110-114](). Team and organization context is managed through `setupTeamContext`, which allows users to select from available teams returned by the cloud API [src/commands/auth.ts:120-207]().

Sources: [src/commands/auth.ts:85](), [src/commands/auth.ts:120-207](), [src/globalConfig/cloud.ts:189-192]()

---

## Model Audit Sharing

For details on how model scanning results are shared, see [Model Audit Sharing](#7.3).

`createShareableModelAuditUrl()` performs an upload of the `ModelAudit` data structure [src/commands/share.ts:44](). Unlike evaluation sharing, it does not use a chunked mechanism as model audit payloads are typically smaller and consolidated. It utilizes `isModelAuditSharingEnabled` to determine if sharing is permitted [src/share.ts:75-89]().

Sources: [src/commands/share.ts:40-53](), [src/share.ts:75-89]()

---

## Telemetry and Analytics

For details on PostHog integration and data anonymization, see [Telemetry and Analytics](#7.4).

The `Telemetry` class records events to help improve the tool [src/telemetry.ts:53](). It uses PostHog for event capture [src/telemetry.ts:139](). The system respects the `PROMPTFOO_DISABLE_TELEMETRY` environment variable and can be completely disabled by users [src/telemetry.ts:19](). User identity is managed via `getUserId()` and `getUserAuthInfo()` to provide context while maintaining privacy [src/globalConfig/accounts.ts:51-73]().

Sources: [src/telemetry.ts:19-40](), [src/telemetry.ts:53-175](), [src/globalConfig/accounts.ts:51-73]()

---

## Cloud API Utilities

`src/util/cloud.ts` provides authenticated wrappers for the Cloud API, ensuring that requests include the correct `Authorization` headers.

| Function | Purpose |
| :--- | :--- |
| `makeRequest(path, method, body)` | Generic authenticated request using `fetchWithProxy` [src/util/cloud.ts:27-43]() |
| `getProviderFromCloud(id)` | Fetches a provider configuration from the cloud by ID [src/util/cloud.ts:51-80]() |
| `checkCloudPermissions(config)` | Validates user permissions for cloud features [src/util/cloud.ts:103]() |
| `getUserTeams()` | Retrieves the list of teams the user belongs to [src/commands/auth.ts:131]() |
| `setupTeamContext()` | Sets the current team/org in `CloudConfig` [src/commands/auth.ts:120-207]() |

Sources: [src/util/cloud.ts:27-43](), [src/util/cloud.ts:51-80](), [src/commands/auth.ts:120-207]()

# Sharing System




This page documents how promptfoo uploads evaluation results to a remote server and generates shareable URLs. It covers the `createShareableUrl()` function, the chunked upload mechanism, adaptive retry logic, rollback behavior, and the `isSharingEnabled()` check.

For cloud authentication setup (API keys, organization and team management) see [Cloud Configuration](7.2). For model audit sharing specifics see [Model Audit Sharing](7.3). For the `share` CLI command surface, see [Utility Commands](4.3).

---

## Overview

Sharing serializes a local `Eval` record (configuration metadata + all result rows) and uploads it to a remote server — either promptfoo's managed cloud or a self-hosted instance. The upload uses a two-phase approach: first POST the eval shell, then stream result rows in size-bounded chunks. If any chunk fails, an adaptive split-and-retry strategy is applied; if the entire upload fails, a DELETE rollback is issued.

**Primary entry point:** `createShareableUrl()` in [src/share.ts:609-652]().

---

## Key Interfaces and Types

| Symbol | File | Purpose |
|---|---|---|
| `ShareOptions` | [src/share.ts:30-35]() | Options for `createShareableUrl` — `silent` and `showAuth` |
| `ChunkSizeError` | [src/share.ts:38]() | Union type: `PAYLOAD_TOO_LARGE`, `NETWORK_TIMEOUT`, `UNKNOWN` |
| `ChunkSendResult` | [src/share.ts:41-45]() | Result of one chunk attempt: `success`, `errorType`, `originalError` |
| `AdaptiveChunkConfig` | [src/share.ts:48-51]() | Bounds for adaptive chunking: `minResultsPerChunk`, `maxResultsPerChunk` |
| `ShareDomainResult` | [src/share.ts:26-28]() | Return type of `determineShareDomain` — `{ domain }` |

**Sources:** [src/share.ts:26-51]()

---

## isSharingEnabled

`isSharingEnabled(evalRecord: Eval): boolean` [src/share.ts:53-73]() determines whether sharing can proceed. It returns `true` when any of the following conditions hold:

**Sharing Enabled Logic:**

```mermaid
flowchart TD
    A["isSharingEnabled(evalRecord)"] --> B{"evalRecord.config.sharing\nis an object with apiBaseUrl?"}
    B -- "Yes" --> R1["return true"]
    B -- "No" --> C{"getShareApiBaseUrl() is set\nand NOT api.promptfoo.app?"}
    C -- "Yes" --> R2["return true (self-hosted env URL)"]
    C -- "No" --> D{"cloudConfig.isEnabled()?"}
    D -- "Yes" --> R3["return true (cloud API key present)"]
    D -- "No" --> R4["return false"]
```

**Sources:** [src/share.ts:53-73](), [src/globalConfig/cloud.ts:178-180]()

The function reads from three sources in priority order:

1. **Eval config object** — `evalRecord.config.sharing.apiBaseUrl` being set signals a self-hosted target [src/share.ts:54-55]().
2. **Environment variable** — `getShareApiBaseUrl()` returning a non-default URL signals a self-hosted target [src/share.ts:64-66]().
3. **Cloud config** — `cloudConfig.isEnabled()` returns `true` when a `PROMPTFOO_API_KEY` or stored API key is present [src/share.ts:68-70]().

---

## API Endpoint Selection

`getApiConfig(evalRecord)` [src/share.ts:557-575]() determines which API endpoint to use:

| Mode | Endpoint | Auth |
|---|---|---|
| Cloud (`cloudConfig.isEnabled()`) | `{cloudConfig.getApiHost()}/api/v1/results` | `Authorization: Bearer {apiKey}` |
| Self-hosted | `{evalRecord.config.sharing.apiBaseUrl ?? getShareApiBaseUrl()}/api/eval` | None |

**Sources:** [src/share.ts:557-575](), [src/globalConfig/cloud.ts:198-200]()

---

## createShareableUrl

**Signature:** `createShareableUrl(evalRecord: Eval, options: ShareOptions): Promise<string | null>` [src/share.ts:609-652]()

**Upload Flow Diagram:**

```mermaid
sequenceDiagram
    participant "CLI/caller" as CLI
    participant "createShareableUrl" as CSU
    participant "sendChunkedResults" as SCR
    participant "sendEvalRecord" as SER
    participant "sendChunkWithRetry" as SCWR
    participant "Remote API" as API

    CLI->>CSU: createShareableUrl(evalRecord, options)
    CSU->>CSU: checkEnvBool(PROMPTFOO_DISABLE_SHARING)
    CSU->>CSU: getOrgContext() [log team name]
    CSU->>CSU: handleEmailCollection(evalRecord)
    CSU->>CSU: getApiConfig(evalRecord) => url
    CSU->>SCR: sendChunkedResults(evalRecord, url, options)
    SCR->>SCR: checkCloudPermissions(evalRecord.config)
    SCR->>SCR: Sample first 1000 results via fetchResultsBatched(1000)
    SCR->>SCR: findLargestResultSize(sampleResults)
    SCR->>SCR: Compute resultsPerChunk (TARGET=900KB)
    SCR->>SER: sendEvalRecord(evalRecord, url, headers)
    SER->>API: POST /api/v1/results (eval shell + traces, results:[])
    API-->>SER: { id: remoteEvalId }
    SER-->>SCR: remoteEvalId
    loop "for each chunk of results"
        SCR->>SCWR: sendChunkWithRetry(chunk, url, remoteEvalId, ...)
        SCWR->>API: POST /api/v1/results/{remoteEvalId}/results
        alt "413 or NETWORK_TIMEOUT"
            SCWR->>SCWR: split chunk, recurse on each half
        else "UNKNOWN error"
            SCWR-->>SCR: throw error
            SCR->>API: DELETE /api/v1/results/{remoteEvalId} [rollback]
            SCR-->>CSU: return null
        end
    end
    SCR-->>CSU: remoteEvalId
    CSU->>CSU: getShareableUrl(evalRecord, remoteEvalId, showAuth)
    CSU-->>CLI: "https://promptfoo.app/eval/{remoteEvalId}"
```

**Sources:** [src/share.ts:609-652](), [src/share.ts:368-514](), [src/share.ts:137-211]()

---

## Chunked Upload: sendChunkedResults

`sendChunkedResults(evalRecord, url, options)` [src/share.ts:368-514]() manages the full upload lifecycle:

### Chunk Size Calculation

```
TARGET_CHUNK_SIZE = 900 KB (0.9 * 1024 * 1024 bytes)
resultsPerChunk = max(1, floor(TARGET_CHUNK_SIZE / largestResultSizeInSample))
```

- `findLargestResultSize()` [src/share.ts:115-122]() samples up to 1,000 results to find the maximum serialized byte size.
- The env var `PROMPTFOO_SHARE_CHUNK_SIZE` (read via `getEnvInt`) overrides this calculation when set to a positive integer [src/share.ts:398-403]().

### Blob Inlining

If `isBlobStorageEnabled()` and `PROMPTFOO_SHARE_INLINE_BLOBS` is set (defaults to `true` when cloud is disabled), blob references in results are resolved inline before upload via `inlineBlobRefsForShare()` [src/share.ts:379-390]().

### Progress Reporting

A `cliProgress.SingleBar` is shown unless any of [src/share.ts:430-435]():
- Debug logging is enabled (`isDebugEnabled()`)
- Running in CI (`isCI()`)
- `silent` option is `true`

---

## Adaptive Retry: sendChunkWithRetry

`sendChunkWithRetry(chunk, url, evalId, headers, config, onProgress, depth, maxDepth)` [src/share.ts:274-349]() implements recursive binary splitting on retryable errors.

**Retry Decision Tree:**

```mermaid
flowchart TD
    A["sendChunkWithRetry(chunk, depth)"] --> B["sendChunkOfResults(chunk)"]
    B --> C{"ChunkSendResult.success?"}
    C -- "true" --> D["onProgress(chunk.length)\nreturn chunk.length"]
    C -- "false" --> E{"errorType?"}
    E -- "PAYLOAD_TOO_LARGE\nor NETWORK_TIMEOUT" --> F{"chunk.length <= minResultsPerChunk?"}
    F -- "true" --> G["throw: cannot split further"]
    F -- "false" --> H["split into firstHalf / secondHalf\nlog info about retry"]
    H --> I["sendChunkWithRetry(firstHalf, depth+1)"]
    H --> J["sendChunkWithRetry(secondHalf, depth+1)"]
    I --> K["return firstSent + secondSent"]
    J --> K
    E -- "UNKNOWN" --> L["throw originalError\n=> triggers rollback in caller"]
```

**Sources:** [src/share.ts:274-349]()

**Max depth** is computed as `ceil(log2(chunk.length / minResultsPerChunk)) + 1` — allowing splits all the way down to a single result [src/share.ts:451-452](). `minResultsPerChunk` is always `1`.

**Error classification** in `sendChunkOfResults()` [src/share.ts:213-268]():

| HTTP status / exception | `ChunkSizeError` | Behavior |
|---|---|---|
| `413 Payload Too Large` | `PAYLOAD_TOO_LARGE` | Recursive split and retry |
| `TypeError('fetch failed')` | `NETWORK_TIMEOUT` | Recursive split and retry |
| Any other non-OK status | `UNKNOWN` | Throw immediately, triggers rollback |

---

## Rollback

`rollbackEval(url, evalId, headers)` [src/share.ts:351-366]() issues a `DELETE` to `{url}/{evalId}`. It is called from `sendChunkedResults` catch block only when an `evalId` was already assigned (i.e., the initial `sendEvalRecord` succeeded before a chunk failed) [src/share.ts:503-505](). Rollback failures are logged as warnings but do not re-throw.

---

## URL Generation

**Domain resolution** is handled by `determineShareDomain(eval_)` [src/share.ts:91-108]():

| Priority | Source |
|---|---|
| 1 (highest) | `cloudConfig.getAppUrl()` when cloud is enabled [src/share.ts:100-101]() |
| 2 | `eval_.config.sharing.appBaseUrl` [src/share.ts:102-103]() |
| 3 | `PROMPTFOO_REMOTE_APP_BASE_URL` env var [src/share.ts:97]() |
| 4 (default) | `getDefaultShareViewBaseUrl()` → `https://promptfoo.app` [src/share.ts:104]() |

**Final URL format** in `getShareableUrl()` [src/share.ts:583-601]():

| Scenario | URL pattern |
|---|---|
| Cloud enabled | `{cloudConfig.getAppUrl()}/eval/{remoteEvalId}` |
| Default share view / no custom domain | `{domain}/eval/{remoteEvalId}` |
| Custom self-hosted domain | `{domain}/eval/?evalId={remoteEvalId}` |

`stripAuthFromUrl(urlString)` [src/share.ts:527-537]() strips any embedded `user:password@` from the URL before returning it, unless `showAuth: true` is passed. This behavior prevents accidental credential leakage.

---

## Idempotency: hasEvalBeenShared

`hasEvalBeenShared(eval_: Eval): Promise<boolean>` [src/share.ts:659-687]() is called by the CLI share command before re-uploading [src/commands/share.ts:172](). It uses `makeCloudRequest` to `GET results/{eval_.id}` (with optional `?teamId=` scope) and interprets HTTP 200 as already-shared, 404 as not-shared.

This check is only available when cloud is enabled; self-hosted instances always re-upload.

---

## Email Collection

`handleEmailCollection(evalRecord)` [src/share.ts:539-555]() prompts for a work email on first share in interactive terminals [src/share.ts:544-547](). The email is stored via `setUserEmail()` and written to `evalRecord.author` before saving [src/share.ts:549-552]().

---

## Initial Eval Record Payload

`sendEvalRecord()` [src/share.ts:137-211]() POSTs:
```
{ ...evalRecord, results: [], traces: [...] }
```
- Results are excluded from the initial POST — they are sent separately as chunks [src/share.ts:153]().
- Traces are fetched via `evalRecord.getTraces()` and included in the initial payload [src/share.ts:143]().
- When cloud is enabled and a `currentTeamId` is set, it is injected into `config.metadata.teamId` to route the eval to the correct team [src/share.ts:156-170]().

---

## Function and Module Map

```mermaid
graph LR
    subgraph "src/commands/share.ts"
        shareCommand["shareCommand()"]
        createAndDisplayShareableUrl["createAndDisplayShareableUrl()"]
    end

    subgraph "src/share.ts"
        isSharingEnabled["isSharingEnabled()"]
        createShareableUrl["createShareableUrl()"]
        sendChunkedResults["sendChunkedResults()"]
        sendEvalRecord["sendEvalRecord()"]
        sendChunkWithRetry["sendChunkWithRetry()"]
        sendChunkOfResults["sendChunkOfResults()"]
        rollbackEval["rollbackEval()"]
        getShareableUrl["getShareableUrl()"]
        determineShareDomain["determineShareDomain()"]
        stripAuthFromUrl["stripAuthFromUrl()"]
        hasEvalBeenShared["hasEvalBeenShared()"]
        handleEmailCollection["handleEmailCollection()"]
        getApiConfig["getApiConfig()"]
    end

    subgraph "src/globalConfig/cloud.ts"
        cloudConfig["cloudConfig (CloudConfig)"]
    end

    subgraph "src/util/cloud.ts"
        makeCloudRequest["makeRequest()"]
        checkCloudPermissions["checkCloudPermissions()"]
        getOrgContext["getOrgContext()"]
    end

    shareCommand --> isSharingEnabled
    shareCommand --> hasEvalBeenShared
    shareCommand --> createAndDisplayShareableUrl
    createAndDisplayShareableUrl --> createShareableUrl
    createShareableUrl --> handleEmailCollection
    createShareableUrl --> getApiConfig
    createShareableUrl --> sendChunkedResults
    createShareableUrl --> getShareableUrl
    getShareableUrl --> determineShareDomain
    getShareableUrl --> stripAuthFromUrl
    sendChunkedResults --> checkCloudPermissions
    sendChunkedResults --> sendEvalRecord
    sendChunkedResults --> sendChunkWithRetry
    sendChunkedResults --> rollbackEval
    sendChunkWithRetry --> sendChunkOfResults
    hasEvalBeenShared --> makeCloudRequest
    getApiConfig --> cloudConfig
    determineShareDomain --> cloudConfig
    sendChunkedResults --> cloudConfig
    createShareableUrl --> getOrgContext
```

**Sources:** [src/share.ts](), [src/commands/share.ts](), [src/globalConfig/cloud.ts](), [src/util/cloud.ts]()

---

## Relevant Environment Variables

| Variable | Effect |
|---|---|
| `PROMPTFOO_DISABLE_SHARING` | Causes `createShareableUrl` to return `null` immediately [src/share.ts:616]() |
| `PROMPTFOO_SHARE_CHUNK_SIZE` | Overrides calculated `resultsPerChunk` [src/share.ts:398-403]() |
| `PROMPTFOO_REMOTE_APP_BASE_URL` | Custom base URL for the generated shareable link [src/share.ts:97]() |
| `PROMPTFOO_SHARE_INLINE_BLOBS` | Inline blob refs before upload [src/share.ts:380]() |
| `PROMPTFOO_DISABLE_SHARE_EMAIL_REQUEST` | Skip email prompt in `handleEmailCollection` [src/share.ts:540]() |
| `PROMPTFOO_API_KEY` | Enables cloud mode via `cloudConfig` [src/globalConfig/cloud.ts:131]() |

**Sources:** [src/share.ts](), [src/globalConfig/cloud.ts]()

# Cloud Configuration




## Purpose and Scope

The Cloud Configuration system manages authentication, feature detection, and API routing for Promptfoo Cloud integration. This page covers the `CloudConfig` singleton that provides a centralized interface for managing cloud-related functionality including API authentication, URL resolution, and team/organization context. It also documents the `auth` command suite, identity management via `accounts.ts`, and the `makeRequest` utility for authenticated cloud communication.

For information about sharing evaluation results to cloud or self-hosted instances, see [Sharing System (7.1)](). For model audit sharing specifically, see [Model Audit Sharing (7.3)]().

## Cloud Configuration Module

The `CloudConfig` class, instantiated as a singleton `cloudConfig`, is located at `src/globalConfig/cloud.ts`. It manages the persistence of cloud credentials and context within the global Promptfoo configuration file.

### Core Implementation

The class maintains an internal state synced with the global configuration file via `readGlobalConfig` and `writeGlobalConfigPartial` [src/globalConfig/cloud.ts:103-124]().

| Method | Return Type | Purpose |
|--------|-------------|---------|
| `isEnabled()` | `boolean` | Determines if Promptfoo Cloud integration is active based on the presence of an API key [src/globalConfig/cloud.ts:178-180](). |
| `getApiHost()` | `string` | Returns the cloud API base URL, defaulting to `https://api.promptfoo.app` [src/globalConfig/cloud.ts:198-200](). |
| `getAuthHeaderName()` | `string` | Returns the header name (default `Authorization`) used for cloud auth [src/globalConfig/cloud.ts:207-209](). |
| `getApiKey()` | `string \| undefined` | Returns the API key from config or `PROMPTFOO_API_KEY` env var [src/globalConfig/cloud.ts:194-196](). |
| `getCurrentTeamId(orgId?)` | `string \| undefined` | Returns the active team context for a specific organization [src/globalConfig/cloud.ts:251-264](). |

Sources: [src/globalConfig/cloud.ts:94-209](), [src/globalConfig/cloud.ts:251-264]()

### Data Flow and Code Entities

The following diagram bridges the natural language requirements to the specific code entities responsible for cloud configuration.

**Cloud Configuration Entity Mapping**
```mermaid
graph TD
    subgraph "Natural Language Space"
        Auth["Authentication"]
        Context["Team/Org Context"]
        Persistence["Global Persistence"]
    end

    subgraph "Code Entity Space"
        CC["class CloudConfig"]
        RGC["readGlobalConfig()"]
        WGCP["writeGlobalConfigPartial()"]
        VSAT["validateAndSetApiToken()"]
        SCT["setCurrentTeamId()"]
        UAI["getUserAuthInfo()"]
    end

    Auth --- CC
    Auth --- VSAT
    Auth --- UAI
    Context --- SCT
    Persistence --- RGC
    Persistence --- WGCP

    CC -.->|"uses"| RGC
    CC -.->|"updates"| WGCP
    VSAT -.->|"calls"| CC
    UAI -.->|"reads"| RGC
```
Sources: [src/globalConfig/cloud.ts:94-124](), [src/globalConfig/cloud.ts:237-249](), [src/globalConfig/accounts.ts:51-61]()

## Identity and Account Management

Identity management is handled in `src/globalConfig/accounts.ts`, which abstracts user-level details like emails and unique identifiers.

### User Authentication Info
The `getUserAuthInfo()` function provides a snapshot of the current user's status by reading the global configuration [src/globalConfig/accounts.ts:51-61]().

```typescript
export function getUserAuthInfo(): UserAuthInfo {
  const globalConfig = readGlobalConfig();
  const email = globalConfig?.account?.email || null;
  const isLoggedIntoCloud = !!(globalConfig?.cloud?.apiKey || process.env.PROMPTFOO_API_KEY);

  return {
    email,
    isLoggedIntoCloud,
    authMethod: isLoggedIntoCloud ? 'api-key' : email ? 'email' : 'none',
  };
}
```
Sources: [src/globalConfig/accounts.ts:51-61]()

### User Identification
Each installation is assigned a unique UUID via `getUserId()`. If no ID exists in the global config, one is generated and persisted [src/globalConfig/accounts.ts:63-73](). This ID is used as the `distinctId` for telemetry events [src/telemetry.ts:67-69]().

## API Key Management

### Validation and Persistence
The `validateAndSetApiToken` method is the entry point for establishing a cloud session. It verifies the token and retrieves associated metadata (user, organization, app, and license status) [src/globalConfig/cloud.ts:237-249]().

```typescript
// src/globalConfig/cloud.ts
async validateAndSetApiToken(token: string, apiHost?: string, authHeaderName?: string) {
  const { user, organization, app, hasActiveLicense } = await this.validateApiToken(
    token,
    apiHost,
    authHeaderName,
  );
  this.saveValidatedApiToken(token, apiHost, user, app, hasActiveLicense, authHeaderName);
  return { user, organization, app, hasActiveLicense };
}
```
Sources: [src/globalConfig/cloud.ts:237-249]()

### Sharing Preference Logic
Promptfoo implements a grandfathering policy for auto-sharing. Users created before `2026-03-09T00:00:00Z` (`SHARING_CUTOFF_DATE`) are grandfathered into auto-sharing even if they lack an active license [src/globalConfig/cloud.ts:13, 188-211]().

## Authentication Commands

The CLI `auth` command (implemented in `src/commands/auth.ts`) provides the user interface for managing cloud identity.

### Command Structure
- `login`: Supports `--api-key` for direct token entry or interactive browser login via `openAuthBrowser` [src/commands/auth.ts:223-273]().
- `logout`: Calls `cloudConfig.delete()` and clears the local email to purge credentials [src/commands/auth.ts:468-473]().
- `whoami`: Displays current identity and active team/organization context [src/commands/auth.ts:475-507]().
- `teams`: Allows users to switch their active team context within an organization [src/commands/auth.ts:509-519]().

**Authentication Sequence**
```mermaid
sequenceDiagram
    participant User as CLI User
    participant Auth as src/commands/auth.ts
    participant Cloud as CloudConfig Singleton
    participant API as Promptfoo Cloud API

    User->>Auth: promptfoo auth login --api-key <key>
    Auth->>Cloud: validateAndSetApiToken(key, host)
    Cloud->>API: GET /api/v1/users/me
    API-->>Cloud: 200 OK (User/Org Data)
    Cloud->>Cloud: saveValidatedApiToken()
    Cloud-->>Auth: Success
    Auth->>User: "Successfully logged in as..."
```
Sources: [src/commands/auth.ts:223-250](), [src/globalConfig/cloud.ts:213-249]()

## Team and Organization Context

Promptfoo Cloud supports multi-tenancy through Organizations and Teams. The `CloudConfig` state tracks these contexts to ensure evaluations and providers are associated with the correct entity.

### Context Resolution
When a user logs in, the CLI attempts to resolve the team context via `setupTeamContext` [src/commands/auth.ts:120-207]():
1. If a team is specified via `--team`, it is validated against accessible teams [src/commands/auth.ts:145-150]().
2. If only one team exists in the organization, it is automatically selected [src/commands/auth.ts:151-152]().
3. In interactive mode with multiple teams, the user selects one via a searchable list [src/commands/auth.ts:162-189]().
4. The selection is persisted via `setCurrentTeamId` [src/globalConfig/cloud.ts:276-285]().

## Cloud Utility: makeRequest

The `makeRequest` utility in `src/util/cloud.ts` is the standard way to perform authenticated calls to the cloud API [src/util/cloud.ts:27-43]().

```typescript
// src/util/cloud.ts
export function makeRequest(path: string, method: string, body?: any): Promise<Response> {
  const apiHost = cloudConfig.getApiHost();
  const url = `${apiHost}/api/v1/${path.startsWith('/') ? path.slice(1) : path}`;
  try {
    return fetchWithProxy(url, {
      method,
      body: JSON.stringify(body),
      headers: { ...(cloudConfig.getAuthHeaders() ?? {}), 'Content-Type': 'application/json' },
    });
  } catch (e) {
    logger.error(`[Cloud] Failed to make request to ${url}: ${e}`);
    throw e;
  }
}
```
Sources: [src/util/cloud.ts:27-43]()

## Configuration Summary Table

| Config Key | Code Accessor | Default Value | Env Var Override |
|------------|---------------|---------------|------------------|
| `apiHost` | `getApiHost()` | `https://api.promptfoo.app` | `PROMPTFOO_CLOUD_API_URL` [src/globalConfig/cloud.ts:4, 150]() |
| `apiKey` | `getApiKey()` | `undefined` | `PROMPTFOO_API_KEY` [src/globalConfig/cloud.ts:131]() |
| `authHeader` | `getAuthHeaderName()` | `Authorization` | `PROMPTFOO_CLOUD_AUTH_HEADER` [src/globalConfig/cloud.ts:175]() |
| `appUrl` | `getAppUrl()` | `https://www.promptfoo.app` | N/A [src/globalConfig/cloud.ts:115]() |

Sources: [src/globalConfig/cloud.ts:4-10](), [src/globalConfig/cloud.ts:112-176]()
This page documents the multi-step red team configuration wizard in the promptfoo web application. It covers the page component, its Zustand state store, the plugins selection interface, and the review/run step. For the underlying red team system that generates and executes the attacks, see [Red Team Architecture](#5.1). For the backend API endpoints that this UI calls, see [Backend Server](#6.6). For the Zustand stores used elsewhere in the app, see [State Management](#6.3).

---

## Overview

The red team setup UI is a six-step wizard that guides a user from choosing a target, through describing the application, selecting plugins and strategies, and finally running an evaluation. It lives entirely under `src/app/src/pages/redteam/setup/`.

The wizard state is held in a persisted Zustand store (`useRedTeamConfig`) so that configuration survives page refreshes and tab navigation. On the final step, the UI submits the configuration to the backend via `/redteam/run`, polls for job status, and displays live logs.

---

## Wizard Steps and Routing

**Wizard step routing diagram**

```mermaid
flowchart LR
    subgraph "RedTeamSetupPage"
        T0["Step 0\nTargetTypeSelection"]
        T1["Step 1\nTargetConfiguration"]
        T2["Step 2\nPurpose"]
        T3["Step 3\nPlugins"]
        T4["Step 4\nStrategies"]
        T5["Step 5\nReview"]
    end
    T0 --> T1 --> T2 --> T3 --> T4 --> T5
```

The top-level component `RedTeamSetupPage` in [src/app/src/pages/redteam/setup/page.tsx:124]() uses a numeric `value` state (0–5) to control which step is visible. The current step is persisted in the URL hash (`#0` through `#5`), enabling browser back/forward navigation [src/app/src/pages/redteam/setup/page.tsx:131-134]().

Step configuration is defined in `TAB_CONFIG` at [src/app/src/pages/redteam/setup/page.tsx:109-122]():

| Step | Label | Icon | Component |
|------|-------|------|-----------|
| 0 | Target Type | `Crosshair` | `TargetTypeSelection` |
| 1 | Target Config | `Settings` | `TargetConfiguration` |
| 2 | Application Details | `LayoutGrid` | `Purpose` |
| 3 | Plugins | `Puzzle` | `Plugins` |
| 4 | Strategies | `Brain` | `Strategies` |
| 5 | Review | `ClipboardCheck` | `Review` |

The wizard handles navigation via `handleNext` and `handleBack` functions which update the numeric step and sync the URL hash [src/app/src/pages/redteam/setup/page.tsx:196-202]().

Sources: [src/app/src/pages/redteam/setup/page.tsx:109-202]()

---

## Sidebar Actions

In addition to step navigation, the sidebar provides global actions for configuration management:

| Action | Logic | Backend / Utility |
|--------|-------------|-------------|
| Save | Opens `SaveConfigDialog` | `POST /configs` with `{name, type: 'redteam', config}` |
| Load | Opens `LoadConfigDialog` | `GET /configs?type=redteam`, then `GET /configs/redteam/:id` |
| Reset | Opens `ResetConfigDialog` | Calls `resetConfig()` on the Zustand store |

The **Load Config** functionality also supports importing a YAML file directly. The file is read via `readFileAsText` [src/app/src/pages/redteam/setup/page.tsx:73-80](), parsed with `loadYaml` [src/app/src/pages/redteam/setup/page.tsx:30](), and applied to the store via `setFullConfig()`.

Sources: [src/app/src/pages/redteam/setup/page.tsx:73-155](), [src/app/src/pages/redteam/setup/hooks/useRedTeamConfig.ts:313-324]()

---

## State Management: `useRedTeamConfig`

**State store structure diagram**

```mermaid
classDiagram
    class useRedTeamConfig {
        +config Config
        +updateConfig(section, value)
        +updatePlugins(plugins)
        +setFullConfig(config)
        +resetConfig()
        +updateApplicationDefinition(section, value)
    }
    class Config {
        +description string
        +prompts string[]
        +target ProviderOptions
        +plugins RedteamPlugin[]
        +strategies RedteamStrategy[]
        +purpose string
        +numTests number
        +applicationDefinition ApplicationDefinition
        +provider string|CoreProviderOptions
    }
    class ApplicationDefinition {
        +purpose string
        +features string
        +industry string
        +attackConstraints string
        +sensitiveDataTypes string
        +criticalActions string
    }
    useRedTeamConfig --> Config
    Config --> ApplicationDefinition
```

`useRedTeamConfig` is a Zustand store with `persist` middleware stored in localStorage under the key `"redTeamConfig"`. It is defined in [src/app/src/pages/redteam/setup/hooks/useRedTeamConfig.ts:7]().

### Key behaviors

- **`updatePlugins(plugins)`**: Merges the incoming plugin list while preserving existing configurations for specific plugins. It handles both string IDs and object-based plugin definitions [src/app/src/pages/redteam/setup/components/Plugins.tsx:159-186]().
- **Validation**: The store and associated hooks use `isPlainObject` [src/app/src/pages/redteam/setup/hooks/useRedTeamConfig.ts:69-75]() and `isValidHttpUrlOrTemplate` [src/app/src/pages/redteam/setup/hooks/useRedTeamConfig.ts:139-153]() to ensure configuration integrity before persistence.
- **Target Reconciliation**: Uses `registerTargetConfigReconciler` to synchronize UI state with the underlying provider configuration [src/app/src/pages/redteam/setup/hooks/useRedTeamConfig.ts:12]().

A second store, `useRecentlyUsedPlugins`, tracks the last `NUM_RECENT_PLUGINS` (default 6) plugins enabled by the user [src/app/src/pages/redteam/setup/hooks/useRedTeamConfig.ts:19-24]().

Sources: [src/app/src/pages/redteam/setup/hooks/useRedTeamConfig.ts](), [src/app/src/pages/redteam/setup/types.ts]()

---

## Step 0 & 1: Target Setup

The target configuration is split into two phases:
1.  **Target Type Selection** (`TargetTypeSelection`): The user selects the provider type from a categorized list including "My Application", "Agent Frameworks", and "AI Providers" [src/app/src/pages/redteam/setup/components/Targets/ProviderTypeSelector.tsx:30-248]().
2.  **Target Configuration** (`Targets`): Detailed configuration of the selected provider using `ProviderEditor` [src/app/src/pages/redteam/setup/components/Targets/index.tsx:189-190]().

### HTTP Endpoint Configuration
The `HttpEndpointConfiguration` component provides a specialized UI for REST APIs [src/app/src/pages/redteam/setup/components/Targets/HttpEndpointConfiguration.tsx:92]():
- **Connection**: URL and Method selection [src/app/src/pages/redteam/setup/components/Targets/HttpEndpointConfiguration.tsx:157-166]().
- **Authentication**: Header management [src/app/src/pages/redteam/setup/components/Targets/HttpEndpointConfiguration.tsx:108-113]().
- **Validation**: A `handleTestTarget` function calls `/providers/test` to verify connectivity and configuration [src/app/src/pages/redteam/setup/components/Targets/HttpEndpointConfiguration.tsx:169-215]().

### Foundation Model Configuration
Supports major providers like OpenAI, Anthropic, and Google. It maps user-friendly names to internal provider IDs like `openai:chat:gpt-4o` or `anthropic:messages:claude-3-5-sonnet-latest` [src/app/src/pages/redteam/setup/hooks/useRedTeamConfig.ts:25-45]().

Sources: [src/app/src/pages/redteam/setup/components/Targets/HttpEndpointConfiguration.tsx](), [src/app/src/pages/redteam/setup/components/Targets/ProviderTypeSelector.tsx](), [src/app/src/pages/redteam/setup/components/Targets/index.tsx]()

---

## Step 2: Application Details (`Purpose`)

The `Purpose` component [src/app/src/pages/redteam/setup/components/Purpose.tsx:83]() collects context about the application.

### Auto-Discovery
The UI integrates with the Target Discovery Agent. `handleTargetPurposeDiscovery` calls `POST /providers/discover` [src/app/src/pages/redteam/setup/components/Purpose.tsx:164-186](). Results are rendered via `DiscoveryResult` components, allowing users to "Apply" discovered features or purpose statements directly to their configuration [src/app/src/pages/redteam/setup/components/Purpose.tsx:34-78]().

### Completion Tracking
The UI calculates a completion percentage for each application section (e.g., "Core Application Details", "Access & Permissions") based on which fields in `ApplicationDefinition` are populated [src/app/src/pages/redteam/setup/components/Purpose.tsx:123-152]().

Sources: [src/app/src/pages/redteam/setup/components/Purpose.tsx](), [src/app/src/pages/redteam/setup/types.ts:44-65]()

---

## Step 3: Plugins (`Plugins` and `PluginsTab`)

### `Plugins` component
The `Plugins` container [src/app/src/pages/redteam/setup/components/Plugins.tsx:107]() manages the high-level tabs:
- **Plugins**: Modular vulnerability tests [src/app/src/pages/redteam/setup/components/Plugins.tsx:43-60]().
- **Custom Intents**: Seed phrases for attack generation [src/app/src/pages/redteam/setup/components/Plugins.tsx:61-97]().
- **Custom Policies**: Rules for AI adherence testing [src/app/src/pages/redteam/setup/components/Plugins.tsx:98-104]().

### `PluginsTab` component
`PluginsTab` [src/app/src/pages/redteam/setup/components/PluginsTab.tsx:179]() provides:
- **Presets**: Groups like `Recommended`, `NIST`, and `OWASP LLM Top 10` [src/app/src/pages/redteam/setup/components/PluginsTab.tsx:77-142]().
- **Enterprise Mappings**: Specific regulatory frameworks like `EU AI Act` or `DoD AI Ethical Principles` [src/app/src/pages/redteam/setup/components/PluginsTab.tsx:131-150]().
- **Configuration**: Certain plugins (e.g., `indirect-prompt-injection`) trigger a `PluginConfigDialog` [src/app/src/pages/redteam/setup/components/PluginsTab.tsx:206-207]().

Sources: [src/app/src/pages/redteam/setup/components/Plugins.tsx](), [src/app/src/pages/redteam/setup/components/PluginsTab.tsx]()

---

## Step 4: Strategies (`Strategies`)

The `Strategies` component [src/app/src/pages/redteam/setup/components/Strategies.tsx:73]() handles the selection of attack methodologies.

- **Hero Strategies**: High-impact strategies like `jailbreak` and `prompt-injection` [src/app/src/pages/redteam/setup/components/strategies/HeroStrategiesSection.tsx:29]().
- **Multi-turn & Agentic**: Specialized categories for testing conversational state and tool-use capabilities [src/app/src/pages/redteam/setup/components/Strategies.tsx:130-140]().
- **Gating**: Strategies requiring remote generation (e.g., `gcg`) are disabled if `apiHealthStatus` is 'disabled' [src/app/src/pages/redteam/setup/components/Strategies.tsx:93-104]().

Sources: [src/app/src/pages/redteam/setup/components/Strategies.tsx]()

---

## Step 5: Review (`Review`)

The `Review` component [src/app/src/pages/redteam/setup/components/Review.tsx:160]() provides the final interface for execution.

### Execution Pipeline
1. **Validation**: Checks for target configuration errors via `useRedTeamTargetConfigValidation` [src/app/src/pages/redteam/setup/components/Review.tsx:167]().
2. **Unified Config**: Generates the final YAML-compatible configuration using `getUnifiedConfig` [src/app/src/pages/redteam/setup/components/Review.tsx:41]().
3. **Job Management**: Submits the run to the backend and tracks the `jobId` in `useRedteamJobStore` [src/app/src/pages/redteam/setup/components/Review.tsx:173]().
4. **Monitoring**: Displays live logs via `LogViewer` and progress estimations [src/app/src/pages/redteam/setup/components/Review.tsx:50-51]().

### YAML Export
The `generateOrderedYaml` utility [src/app/src/pages/redteam/setup/utils/yamlHelpers.ts:59]() ensures that the exported configuration follows the standard `promptfooconfig.yaml` structure, ordering keys like `description`, `targets`, `plugins`, and `strategies` correctly.

Sources: [src/app/src/pages/redteam/setup/components/Review.tsx](), [src/app/src/pages/redteam/setup/page.tsx:59]()
The promptfoo telemetry system is designed to collect anonymized usage data to improve the tool's performance and identify popular features. It employs a multi-channel approach, sending events to both **PostHog** and a custom internal endpoint, while providing strict controls for user privacy and environment-specific behavior.

## System Architecture

The telemetry system is centered around the `Telemetry` class, which manages user identification, event recording, and graceful shutdown of tracking clients.

### Telemetry Data Flow

The following diagram illustrates how an event triggered in the CLI or Web UI flows through the `Telemetry` class to external collectors.

**Telemetry Event Pipeline**

```mermaid
graph TD
    subgraph "Execution Space"
        CLI["CLI Command (main.ts)"]
        WEB["Web Backend (src/server/routes/user.ts)"]
    end

    subgraph "Code Entity Space: src/telemetry.ts"
        T_Class["class Telemetry"]
        T_Record["telemetry.record(eventName, properties)"]
        T_Send["sendEvent()"]
        PH_Client["PostHog Client (posthog-node)"]
    end

    subgraph "External Collectors"
        PH_Cloud["PostHog Cloud (EVENTS_ENDPOINT)"]
        R_End["Internal API (R_ENDPOINT)"]
        C_End["Consent API (CONSENT_ENDPOINT)"]
    end

    CLI --> T_Record
    WEB --> T_Record
    T_Record --> T_Send
    T_Send --> PH_Client
    T_Send --> R_End
    T_Class -->|saveConsent| C_End
    PH_Client --> PH_Cloud
```

**Sources:** [src/telemetry.ts:117-124](), [src/telemetry.ts:126-175](), [src/telemetry.ts:201-221](), [src/server/routes/user.ts:65-72]()

## Key Components

### The Telemetry Class
The `Telemetry` class is the primary interface for recording analytics. It is typically instantiated as a singleton.

- **`initialize()`**: Associates the current session with a unique user ID retrieved via `getUserId()` and triggers the identity sequence [src/telemetry.ts:63-69]().
- **`identify()`**: Associates the current session with user properties such as email and CI status. It calls `client.identify` on the PostHog instance [src/telemetry.ts:84-104]().
- **`record(eventName, properties)`**: The main entry point for logging. If telemetry is disabled via environment variables, it calls `recordTelemetryDisabled()` to log the opt-out status once [src/telemetry.ts:117-124]().
- **`sendEvent()`**: Orchestrates the delivery of data. It appends runtime metadata (Node version, platform, arch) and package version before sending to PostHog and the internal `R_ENDPOINT` via `fetchWithProxy` [src/telemetry.ts:126-175]().

### Account and Identity Management
Identity is managed via the `globalConfig/accounts.ts` utilities, which interact with the user's global configuration file.

- **User ID**: A persistent UUID is stored in the global configuration. If missing, `getUserId()` generates a new one using `crypto.randomUUID()` and persists it via `writeGlobalConfig` [src/globalConfig/accounts.ts:63-73]().
- **User Properties**: The `getPersonProperties()` method aggregates data from `getUserAuthInfo()`, including the user's email, cloud login status, and the `authMethod` (`api-key`, `email`, or `none`) [src/telemetry.ts:76-82](), [src/globalConfig/accounts.ts:51-61]().

### PostHog Integration
Promptfoo uses the `posthog-node` library. The client is configured with specific settings to ensure CLI performance and prevent process hangs:
- **`flushInterval: 0`**: Disables the internal automatic flush timer. Without this, PostHog's internal `setInterval` keeps the Node.js event loop alive indefinitely, causing processes that import promptfoo to hang [src/telemetry.ts:25-34]().
- **Immediate Flushing**: Events are sent immediately, and `client.flush()` is called after each capture to ensure data is transmitted before the CLI command completes [src/telemetry.ts:139-152]().

**Sources:** [src/telemetry.ts:18-40](), [src/globalConfig/accounts.ts:51-73]()

## Data Collection and Anonymization

The system collects specific event properties alongside a standard set of runtime metadata.

| Data Type | Fields | Source |
| :--- | :--- | :--- |
| **Identity** | `distinctId` (UUID), `email` | [src/telemetry.ts:94](), [src/globalConfig/accounts.ts:53]() |
| **Runtime** | `nodeVersion`, `platform`, `arch`, `packageVersion` | [src/telemetry.ts:44-51](), [src/telemetry.ts:131]() |
| **Environment** | `isRunningInCi`, `NODE_ENV` | [src/telemetry.ts:132](), [src/telemetry.ts:165]() |
| **Auth Context** | `isLoggedIntoCloud`, `authMethod` | [src/globalConfig/accounts.ts:51-61]() |

### Telemetry Control

Users can opt-out of telemetry using environment variables.

| Variable | Effect |
| :--- | :--- |
| `PROMPTFOO_DISABLE_TELEMETRY` | Disables PostHog initialization and prevents `sendEvent` from firing [src/telemetry.ts:19-21](), [src/telemetry.ts:106-108](). |
| `IS_TESTING` | Blocks telemetry in test environments to prevent network calls during CI/unit tests [src/telemetry.ts:19-21](), [src/telemetry.ts:137](). |

**Sources:** [src/telemetry.ts:19-21](), [src/telemetry.ts:106-108]()

## Implementation Details

### Process Lifecycle and Shutdown
The telemetry system provides a shutdown mechanism to ensure the PostHog client is properly closed when the process exits.

**Shutdown Logic**

```mermaid
sequenceDiagram
    participant P as Node.js Process
    participant T as Telemetry Instance
    participant PH as PostHog Client

    Note over P: Process Exit / beforeExit
    P->>T: shutdown()
    alt isShuttingDown == true
        T-->>P: Return early
    else isShuttingDown == false
        T->>T: Set isShuttingDown = true
        T->>PH: client.shutdown()
        PH-->>T: Flush and Close
        T-->>P: Done
    end
```

The `shutdown()` method uses an `isShuttingDown` flag to guard against multiple calls from `beforeExit` and explicit CLI shutdown handlers [src/telemetry.ts:177-196]().

### Red Team Consent and Email Validation
A specialized endpoint `CONSENT_ENDPOINT` is used specifically for redteaming. This is triggered when a user provides their email for "harmful" plugin synthesis or logs into the Web UI [src/telemetry.ts:201-221]().

The system also performs email status checks via `checkEmailStatus`, which communicates with the Promptfoo API to verify if an email is risky, disposable, or requires verification. In CI environments, a synthetic placeholder `CI_PLACEHOLDER_EMAIL` is used to bypass interactive prompts [src/globalConfig/accounts.ts:161-184]().

**Email Validation State Machine**

```mermaid
stateDiagram-v2
    [*] --> NO_EMAIL
    NO_EMAIL --> OK: User enters email
    OK --> EMAIL_VERIFICATION_REQUIRED: API returns verification needed
    EMAIL_VERIFICATION_REQUIRED --> OK: checkEmailStatus(validate=true)
    OK --> RISKY_EMAIL: API flags email as risky

    state OK {
        [*] --> Validated
    }
    state EMAIL_VERIFICATION_REQUIRED {
        [*] --> setUserEmailNeedsValidation(true)
    }
```

**Sources:** [src/telemetry.ts:177-196](), [src/telemetry.ts:201-221](), [src/globalConfig/accounts.ts:161-213](), [src/types/email.ts:1-15]()

# Advanced Features




This section provides an overview of the advanced capabilities within the promptfoo ecosystem that extend beyond standard evaluation and red teaming. These features include deep observability through OpenTelemetry, static security analysis for machine learning models, automated code vulnerability scanning, and agentic integration via the Model Context Protocol (MCP).

## 8.1 OpenTelemetry Tracing

Promptfoo integrates with the OpenTelemetry (OTLP) ecosystem to provide deep visibility into LLM provider execution flows. It acts as an **OpenTelemetry receiver**, allowing it to ingest traces from external applications or internal provider calls and visualize them directly in the web UI [site/docs/tracing.md:8-16]().

### Core Components
*   **OTLP Receiver**: Collects traces during evaluation runs to provide visibility into nested calls and tool executions via `src/tracing/otlpReceiver.ts` [src/cliState.ts:60-67]().
*   **GenAI Instrumentation**: Built-in providers are instrumented using `genaiTracer` and `withGenAISpan` to capture standardized attributes like `gen_ai.system`, `gen_ai.request.model`, and token usage [site/docs/tracing.md:68-82]().
*   **Trajectory Assertions**: Analyzes the sequence of spans (e.g., tool calls, reasoning steps) using `extractTrajectorySteps` to verify agent behavior [src/assertions/trajectoryUtils.ts:177-187]().
*   **Trace-Aware Assertions**: Specialized handlers like `handleTrajectoryStepCount`, `handleTrajectoryToolUsed`, and `handleTrajectoryToolSequence` allow for assertions based on the execution path of the underlying trace [test/assertions/trajectory.test.ts:2-7]().

### Trace-to-Code Mapping
The following diagram illustrates how OpenTelemetry spans are processed from a Provider call into the promptfoo persistence layer.

**Trace Ingestion Pipeline**
```mermaid
graph TD
    subgraph "Natural Language Space"
        UserPrompt["User Prompt"]
    end

    subgraph "Code Entity Space"
        Provider["ApiProvider.callApi()"]
        Tracer["genaiTracer (withGenAISpan)"]
        Exporter["localSpanExporter"]
        SQLite["SQLite (spans table)"]
        TrajUtils["trajectoryUtils.extractTrajectorySteps()"]
    end

    UserPrompt --> Provider
    Provider --> Tracer
    Tracer --> Exporter
    Exporter --> SQLite
    SQLite --> TrajUtils
```
Sources: [src/tracing/genaiTracer.ts:1-20](), [src/assertions/trajectoryUtils.ts:177-197](), [site/docs/tracing.md:38-43]()

For details, see [OpenTelemetry Tracing](#8.1).

---

## 8.2 Model Audit (ModelAudit)

The `scan-model` command provides static security analysis for machine learning models. It leverages the `modelaudit` library to detect malicious code, unsafe configurations, and backdoors in over 30 model formats [site/docs/model-audit/index.md:2-10]().

### Key Capabilities
*   **Static Analysis**: Scans for dangerous Python opcodes in pickle-based models (`.pkl`, `.pt`) and unsafe Lambda layers in Keras [site/docs/model-audit/scanners.md:39-58]().
*   **Remote Scanning**: Supports scanning models directly from HuggingFace (`hf://`), S3, GCS, and JFrog Artifactory using environment-based authentication [site/docs/model-audit/usage.md:34-62]().
*   **Scanner Management**: Users can list available scanners with `--list-scanners` and selectively run or exclude them via CLI flags [src/commands/modelScan.ts:78-80]().
*   **Web UI**: A dedicated interface at `/model-audit` uses `modelAuditRouter` to manage path checks and scan execution [src/server/routes/modelAudit.ts:21-30]().

**Model Scan Execution Flow**
```mermaid
graph TD
    subgraph "Natural Language Space"
        User["Security Engineer"]
        ModelPath["'s3://bucket/model.pkl'"]
    end

    subgraph "Code Entity Space"
        CLI["promptfoo scan-model (src/commands/modelScan.ts)"]
        Router["modelAuditRouter (src/server/routes/modelAudit.ts)"]
        Spawn["spawnModelAuditCapture"]
        Python["modelaudit (External CLI)"]
        DB["ModelAudit.create() (src/models/modelAudit.ts)"]
    end

    User --> CLI
    CLI --> Spawn
    Router --> Spawn
    Spawn --> Python
    Python --> DB
```
Sources: [src/commands/modelScan.ts:216-230](), [src/server/routes/modelAudit.ts:195-210](), [site/docs/model-audit/scanners.md:27-35]()

For details, see [Model Audit (ModelAudit)](#8.2).

---

## 8.3 Code Scanning

Code scanning identifies LLM-related security vulnerabilities within application source code, such as insecure prompt construction or unsafe handling of LLM outputs.

### Key Components
*   **CLI Command Group**: Managed via `code-scans` commands for local repository analysis.
*   **GitHub Action**: The `code-scan-action` analyzes `git diff` to identify new risks in pull requests.
*   **Vulnerability Detection**: Identifies patterns that lead to prompt injection or data leakage.
*   **Reporting**: Results are reported back to the CLI or CI environment, often in SARIF format for integration with security dashboards [site/docs/model-audit/usage.md:211-217]().

For details, see [Code Scanning](#8.3).

---

## 8.4 MCP Server

Promptfoo implements a **Model Context Protocol (MCP)** server via `mcpCommand`, allowing AI agents to use promptfoo as a toolset.

### Available Tools
The MCP server exposes several capabilities to agents:
*   `runEvaluation`: Execute evaluations from a configuration.
*   `generateDataset`: Synthesize test cases for a given prompt.
*   `redteamGenerate`: Generate adversarial test cases.
*   `testProvider`: Verify provider connectivity and output.
*   `validatePromptfooConfig`: Perform schema validation on `promptfooconfig.yaml`.

### Architecture
The server supports both `stdio` and `http` transport modes, enabling integration with desktop agents like Claude or remote orchestration services.

**MCP Tool Execution Flow**
```mermaid
graph LR
    subgraph "Natural Language Space"
        Agent["AI Agent (e.g. Claude)"]
        Goal["'Evaluate this prompt'"]
    end

    subgraph "Code Entity Space"
        MCP["mcpCommand (src/commands/mcp.ts)"]
        Registry["Tool Registry"]
        EvalFunc["evaluate() (src/evaluator.ts)"]
        Config["readConfig()"]
    end

    Agent -- "Natural Language Request" --> Goal
    Goal -- "Tool Call" --> MCP
    MCP --> Registry
    Registry -- "Execute" --> EvalFunc
    EvalFunc --> Config
```
Sources: [src/cliState.ts:60-67](), [src/server/routes/modelAudit.ts:123-130]()

For details, see [MCP Server](#8.4).
The test suite system defines how evaluations are structured in promptfoo. A test suite consists of prompts, providers, test cases, and configuration options. The system handles variable expansion, test case merging with defaults, and configuration resolution from multiple sources.

For information about how test suites are executed, see [Evaluation Engine](#2.1). For provider configuration, see [Provider System](#3).

## Test Suite Structure

A test suite in promptfoo is defined primarily through the `TestSuite` interface, which specifies prompts, providers, and test cases. The system processes this structure to generate all test combinations.

### TestSuite Core Components

**TestSuite Structure**

```mermaid
graph TB
    subgraph "TestSuite Interface [src/types/index.ts]"
        TestSuite["TestSuite"]
        TestSuite --> prompts["prompts: Prompt[]"]
        TestSuite --> providers["providers: ApiProvider[]"]
        TestSuite --> tests["tests?: TestCase[]"]
        TestSuite --> scenarios["scenarios?: Scenario[]"]
        TestSuite --> defaultTest["defaultTest?: TestCase | string"]
        TestSuite --> extensions["extensions?: string[]"]
        TestSuite --> nunjucksFilters["nunjucksFilters?: NunjucksFilterMap"]
        TestSuite --> providerPromptMap["providerPromptMap?: Record<string, string[]>"]

        prompts --> Prompt["Prompt { raw, label, id }"]
        tests --> TestCase["TestCase { vars, assert, options }"]
        defaultTest --> DefaultTestCase["Base properties for all tests"]
        scenarios --> Scenario["Scenario { config, tests }"]
    end
```

Sources: [src/types/index.ts:566-605]()

**Configuration Loading and Dereferencing Pipeline**

```mermaid
graph LR
    rawYaml["promptfooconfig.yaml"] --> readConfig["readConfig()"]
    readConfig --> dereference["dereferenceConfig()"]
    dereference --> refParser["@apidevtools/json-schema-ref-parser"]
    refParser --> unifiedConfig["UnifiedConfig object"]
    unifiedConfig --> resolveConfigs["resolveConfigs()"]
    resolveConfigs --> TestSuite["TestSuite object"]
```

Sources: [src/util/config/load.ts:183-228](), [src/util/config/load.ts:439-491]()

### Test Suite YAML Configuration

The `promptfooconfig.yaml` file defines the test suite structure. The schema ensures validation of all evaluation parameters.

| Section | Type | Purpose |
|---------|------|---------|
| `prompts` | `string[]` or `Prompt[]` | Prompt templates to evaluate. Supports `file://` and glob patterns. |
| `providers` | `string[]` or `Provider[]` | LLM providers to test against. |
| `tests` | `TestCase[]` or `string` | Individual test cases with variables and assertions. |
| `defaultTest` | `TestCase` or `string` | Default properties inherited by all tests. |
| `scenarios` | `Scenario[]` | Grouped test configurations for combinatorial testing. |
| `extensions` | `string[]` | Hook functions (JS/Py) for custom behavior. |
| `redteam` | `RedteamConfig` | Configuration for adversarial testing and vulnerability scanning. |

Sources: [src/types/index.ts:566-605](), [site/docs/configuration/guide.md:25-42](), [site/static/config-schema.json:9-69]()

## Test Case Definition

Test cases define the inputs and expected outputs for each evaluation. The `TestCase` interface allows flexible specification of variables, assertions, and test-specific configuration.

### TestCase Structure

**TestCase Components**

```mermaid
graph TB
    subgraph "TestCase Interface [src/types/index.ts]"
        TestCase["TestCase"]
        TestCase --> vars["vars?: Vars"]
        TestCase --> assert["assert?: Assertion[]"]
        TestCase --> options["options?: TestCaseOptions"]
        TestCase --> provider["provider?: ApiProvider"]
        TestCase --> threshold["threshold?: number"]
        TestCase --> metadata["metadata?: Record<string, any>"]

        vars --> varMapping["Variable key-value pairs"]
        assert --> assertions["Array of assertion objects"]
        options --> transform["transform, prefix, suffix"]
        options --> storeOutputAs["storeOutputAs: string"]
        options --> disableVarExpansion["disableVarExpansion: boolean"]
    end
```

Sources: [src/types/index.ts:647-715]()

### Test Case Formats

Promptfoo supports multiple formats for test cases, loaded via `readTests` and `readTest`.

*   **YAML/JSON**: The standard format within the config file.
*   **CSV**: Loaded via `src/csv.ts`. Variables are mapped from columns. [src/csv.ts:127-214]()
*   **External Files**: Using `file://` prefix in the `tests` or `vars` section. [site/docs/configuration/guide.md:131-151]()
*   **HuggingFace**: Loading datasets directly from HuggingFace via `huggingface://`. [site/docs/configuration/parameters.md:110-114]()
*   **Excel (XLSX)**: Supported via the `src/util/xlsx.ts` utility. [src/util/xlsx.ts:7-40]()

Sources: [src/util/testCaseReader.ts:182-273](), [src/util/config/load.ts:46-48]()

## Dereferencing and Merging

The configuration pipeline uses a dereferencing step to resolve `$ref` pointers and external file references before merging configurations.

### The Dereferencing Pipeline

The `dereferenceConfig` function uses `@apidevtools/json-schema-ref-parser` to resolve references. The system includes specific logic to handle environment variables and recursive merging.

1.  **Environment Variable Rendering**: The system renders environment variables in the raw object using `renderEnvOnlyInObject`. [src/util/config/load.ts:39]()
2.  **Dereference**: The `$RefParser.dereference` call resolves all `$ref` and file pointers. This can be disabled by setting `PROMPTFOO_DISABLE_REF_PARSER`. [src/util/config/load.ts:184-187]()
3.  **Sanitization**: Tracing configurations are preserved during the process to ensure credentials aren't leaked or lost. [src/util/config/load.ts:46]()

Sources: [src/util/config/load.ts:183-243]()

### Config Merging with `combineConfigs`

When multiple configuration files are provided via the CLI (e.g., `promptfoo eval -c config1.yaml -c config2.yaml`), the system merges them into a single `UnifiedConfig`.

*   **Prompts**: Concatenated into a single list. [src/util/config/load.ts:349-354]()
*   **Providers**: Concatenated. [src/util/config/load.ts:356-361]()
*   **Tests**: Concatenated. [src/util/config/load.ts:363-368]()
*   **EvaluateOptions**: Shallow merged, with later configs overriding earlier ones. [src/util/config/load.ts:376-381]()

Sources: [src/util/config/load.ts:349-437]()

## defaultTest Merging

The `defaultTest` property provides base configuration that is merged with each individual test case. This merging happens during test suite processing in `resolveConfigs`.

### defaultTest Merge Rules

| Property | Merge Behavior |
|----------|----------------|
| `vars` | Shallow merge - individual test vars override defaults. |
| `assert` | Concatenation - default assertions run first, then test-specific. |
| `options` | Shallow merge - individual options override defaults. |
| `metadata` | Shallow merge - individual metadata overrides defaults. |
| `threshold` | Override - individual threshold takes precedence. |

Sources: [src/util/config/load.ts:316-347](), [src/util/testCaseReader.ts:133-180]()

## Variable Resolution and Expansion

Variables in test cases can be static, file-based, or dynamically generated via scripts.

### Scripted Variables

Variables can be loaded from JavaScript or Python files using the `file://` prefix.
*   **JavaScript**: The file should export a function receiving `(varName, prompt, otherVars, provider)`. [site/docs/configuration/guide.md:215-240]()
*   **Python**: The file should define a `get_var(var_name, prompt, other_vars)` function. [site/docs/configuration/guide.md:242-262]()

Sources: [src/util/config/load.ts:38-40](), [site/docs/configuration/guide.md:191-199]()

### Variable Expansion

If a variable value is an array, promptfoo can expand it into multiple test cases (Cartesian product). This behavior can be disabled globally via environment variables or per-test via the `disableVarExpansion` option in `TestCaseOptions`.

Sources: [src/util/config/load.ts:180-182](), [src/types/index.ts:685]()

## Scenarios

Scenarios allow for high-level grouping and combinatorial testing by applying a set of configurations to a set of tests.

### Scenario Expansion Flow

```mermaid
graph TB
    subgraph "Scenario Processing [src/util/config/load.ts]"
        Scenario["Scenario"] --> config["config: TestCase[] (Templates)"]
        Scenario --> tests["tests: TestCase[] (Instances)"]

        config --> crossProduct["Apply each config template to each test instance"]
        tests --> crossProduct

        crossProduct --> finalTests["Resulting TestCase list"]
    end
```

Sources: [src/types/index.ts:762-767](), [src/util/config/load.ts:103-111]()

## CLI Provider Resolution

When providers are passed via the CLI (`--providers`), `resolveCliProvidersWithConfig` matches these tokens against providers defined in the YAML configuration to preserve their specific configurations (like `temperature` or `max_tokens`).

**Matching Priority**:
1. Exact match on provider `id`. [src/util/config/load.ts:164-167]()
2. Exact match on provider `label`. [src/util/config/load.ts:169-172]()
3. Suffix match (e.g., CLI `llama3.1:8b` matches config `ollama:llama3.1:8b`). [src/util/config/load.ts:174-177]()
4. Fallback to raw string for fresh provider creation. [src/util/config/load.ts:179]()

Sources: [src/util/config/load.ts:146-181]()
This page documents the testing approach, framework configurations, test categories, coverage reporting, and parallelized execution for the promptfoo codebase. It covers the test suite under `test/`, `src/app/`, and the ancillary language wrappers in `src/python/`, `src/ruby/`, and `src/golang/`.

For information about CI/CD pipelines and release automation, see [Build System and CI/CD](9.1). For code quality tooling (linting, formatting), see [Code Quality](9.3).

---

## Test Frameworks

The codebase uses two test frameworks depending on the layer being tested:

| Layer | Framework | Config Location | Runner Script |
|---|---|---|---|
| Backend (TypeScript core) | Vitest | `vitest.config.ts` (root) | `npm run test` |
| Frontend (React, `src/app`) | Vitest | `src/app/vitest.config.ts` | `npm run test:app` |
| Python utilities | `unittest` (stdlib) | N/A | `python -m unittest discover` |
| Ruby wrapper | Manual script | N/A | `ruby src/ruby/wrapper.rb ...` |
| Go wrapper | `go test` | `src/golang/go.mod` | `go test -v wrapper.go wrapper_test.go` |

Test files in `test/` import directly from `vitest` [test/AGENTS.md:40-43](). The configuration for the primary test suite is defined in `vitest.config.ts` and `vitest.setup.ts`.

Sources: [test/AGENTS.md:7-22](), [vitest.config.ts:1-10](), [vitest.setup.ts:1-5]()

---

## Test Categories

The following diagram maps test categories to their corresponding entry points in CI.

**Test Category to CI Job Mapping**

```mermaid
graph TD
    CI["main.yml CI workflow"]

    CI --> test_job["test job\n(Node matrix + shards)"]
    CI --> docker_job["docker.yml workflow\n(Multi-arch build/test)"]
    CI --> tusk_job["Tusk Test Runner\n(Parallel Vitest)"]
    CI --> code_scan_job["promptfoo-code-scan.yml\n(Security scan)"]

    test_job --> unit_cmd["npm run test"]
    test_job --> coverage_cmd["npm run test -- --coverage"]
    docker_job --> docker_health["HEALTHCHECK\n(curl /health)"]
    docker_job --> docker_eval["npm run local -- eval"]
    tusk_job --> tusk_vitest["npx vitest run {{file}}"]
    code_scan_job --> cs_action["promptfoo/code-scan-action"]
```

Sources: [.github/workflows/main.yml:130-132](), [.github/workflows/docker.yml:164-167](), [.github/workflows/promptfoo-code-scan.yml:52-53](), [.github/workflows/tusk-test-runner-app-vitest-unit-tests.yml:125-125]()

### Unit Tests
Unit tests live in the `test/` directory, mirroring the structure of `src/` [test/AGENTS.md:52-55](). They use Vitest with extensive module mocking via `vi.mock` [test/AGENTS.md:61-67](). The CI environment runs these across Node versions 22.22, 24.x, and 26.x [.github/workflows/main.yml:32-35]().

### Integration Tests
Integration tests run against the compiled source and involve the file system, SQLite database, or spawning child processes. They are executed via `npm run test:integration` [test/AGENTS.md:21-21](). Database isolation and migration tests ensure the SQLite/Drizzle layer functions correctly [src/database/index.ts:121-145]().

### Smoke Tests
Smoke tests verify the built CLI package works correctly end-to-end by testing `dist/src/main.js` directly using `spawnSync` [test/AGENTS.md:203-205](). The Docker CI workflow performs a smoke test by running a local evaluation inside the container against a provided config [.github/workflows/docker.yml:152-155]().

### Frontend Tests
Frontend tests for the React web application live under `src/app/` and run with Vitest. These tests use integration patterns with real Zustand stores to verify state changes [test/AGENTS.md:95-103](). They are also integrated into the Tusk parallel runner for faster execution [.github/workflows/tusk-test-runner-app-vitest-unit-tests.yml:81-82]().

---

## Test Hygiene and Environment Control

The project enforces strict test hygiene rules:

- **Restricting `.only` and `.skip`**: Ensures that tests are not accidentally skipped in CI [test/AGENTS.md:27-27]().
- **Mock Isolation**: Tests run in random order by default. Developers must use `vi.clearAllMocks()` and `mockReset()` in `beforeEach` to prevent test pollution [test/AGENTS.md:29-31](), [test/AGENTS.md:76-83]().
- **Environment Variables**: The `mockProcessEnv()` utility from `test/util/utils.ts` is preferred for tests that need to change environment variables [test/AGENTS.md:88-91]().
- **Database Safety**: The database layer refuses to open the default production database (`~/.promptfoo/promptfoo.db`) while running tests to prevent accidental data mutation [src/database/index.ts:130-141]().

Sources: [test/AGENTS.md:24-31](), [src/database/index.ts:121-145](), [test/AGENTS.md:87-92]()

---

## CI Test Matrix and Sharding

The CI runs across a matrix of Node.js versions and operating systems. To handle large test volumes on Windows, the suite is sharded into 3 parts [.github/workflows/main.yml:36-38]().

| OS | Node Versions | Sharding | Purpose |
|---|---|---|---|
| Ubuntu | 22.22, 24.x, 26.x | No | Primary verification + Coverage |
| Windows | 22.22 (PR), 24.x/26.x (Main) | 3 Shards | Cross-platform compatibility |
| macOS | 22.22 (PR), 24.x/26.x (Main) | No | Apple Silicon/Intel verification |

Sources: [.github/workflows/main.yml:31-64]()

---

## Coverage Reporting

Coverage is collected using Vitest's coverage-v8 provider. It is uploaded to Codecov using OIDC authentication [.github/workflows/main.yml:138-148]().

- **Backend Coverage**: Collected on Ubuntu with Node 22.22 [.github/workflows/main.yml:132-132]().
- **Coverage Ratcheting**: The `test:coverage:ratchet` script ensures that coverage percentages do not decrease over time [.github/workflows/main.yml:134-136]().

---

## Parallel Execution with Tusk

For high-concurrency testing, the project uses **Tusk Test Runner**. This allows parallelizing Vitest tests across multiple GitHub runners by sharding test files [.github/workflows/tusk-test-runner-app-vitest-unit-tests.yml:58-63]().

- **Test Script**: Vitest is executed in run mode per file shard: `npx vitest run {{file}}` [.github/workflows/tusk-test-runner-app-vitest-unit-tests.yml:125-125]().
- **Node 26 Compatibility**: Node 26 hosted installs stall during lifecycle scripts. CI installs the tree without scripts and then rebuilds `better-sqlite3` manually [.github/workflows/main.yml:114-120]().

---

## Entity Relationship Diagrams

**Testing Infrastructure Components**

```mermaid
graph TD
    subgraph "Test Runners"
        VITEST["Vitest (test/)"]
        VITEST_APP["Vitest (src/app/)"]
        TUSK["Tusk Test Runner"]
    end

    subgraph "CI Orchestration"
        MAIN_YML[".github/workflows/main.yml"]
        DOCKER_YML[".github/workflows/docker.yml"]
    end

    subgraph "Hygiene & Safety"
        DB_SAFETY["getDbPath() Safety Check"]
        MOCK_ISO["Mock Isolation (afterEach)"]
        CODECOV["Codecov OIDC"]
    end

    MAIN_YML -- "triggers" --> VITEST
    MAIN_YML -- "uploads to" --> CODECOV
    DB_SAFETY -- "protects" --> DB_PROD["~/.promptfoo/promptfoo.db"]
    MOCK_ISO -- "ensures" --> VITEST
    DOCKER_YML -- "smoke tests" --> DOCKER_FILE["Dockerfile"]
```

Sources: [.github/workflows/main.yml:130-146](), [src/database/index.ts:130-141](), [test/AGENTS.md:28-28](), [.github/workflows/docker.yml:152-155]()

**Code Entity to Test Mapping**

```mermaid
graph LR
    subgraph "Source Entities"
        DB_INDEX["src/database/index.ts"]
        OPENAI_PROV["src/providers/openai/index.ts"]
        STORE_HOOK["src/app/src/hooks/usePageMeta.ts"]
    end

    subgraph "Test Entities"
        DB_TEST["test/database/index.test.ts"]
        OPENAI_TEST["test/providers/openai.test.ts"]
        STORE_TEST["src/app/src/hooks/usePageMeta.test.ts"]
    end

    DB_TEST -- "tests" --> DB_INDEX
    OPENAI_TEST -- "verifies" --> OPENAI_PROV
    STORE_TEST -- "verifies" --> STORE_HOOK
```

Sources: [test/database/index.test.ts:1-5](), [test/AGENTS.md:54-54](), [test/AGENTS.md:37-37]()

# Code Quality




This page documents the code style tooling, linting configuration, static analysis checks, and architecture boundary enforcement within the promptfoo codebase. These automated quality gates ensure consistency across the monorepo and prevent regressions in performance or maintainability.

---

## Overview

Code quality enforcement in promptfoo is a multi-layered system involving formatters, linters, and custom static analysis scripts. The primary enforcement occurs during the `style-check` CI job, but several specialized scripts handle architectural integrity and package boundaries.

The following diagram maps the relationship between system components and the tools used to validate them.

**Code Quality Tooling Architecture**

```mermaid
graph TD
    subgraph "Natural Language Space (Developer Intent)"
        Style["Coding Style & Conventions"]
        Architecture["System Boundaries"]
        Security["Lockfile & Dependency Safety"]
    end

    subgraph "Code Entity Space"
        Biome["biome.jsonc"]
        Boundaries["checkArchitectureBoundaries.ts"]
        Layers["architecture/layers.json"]
        ArtifactTest["scripts/testPackageArtifact.ts"]
    end

    Style --> Biome
    Architecture --> Layers
    Architecture --> Boundaries
    Security --> ArtifactTest
```

Sources: [biome.jsonc:1-33](), [architecture/layers.json:1-23](), [AGENTS.md:53-62]()

---

## TypeScript and JavaScript Quality

The project uses **Biome** as the primary engine for JavaScript and TypeScript linting and formatting. Biome replaces ESLint and Prettier for source files to provide significantly faster performance in the monorepo environment [site/docs/contributing.md:177-185]().

### Biome Configuration
The configuration in `biome.jsonc` enforces strict rules to maintain a high-quality codebase:
- **Restricted Globals**: Direct use of `fetch()` is denied in favor of `fetchWithProxy()` to ensure consistent proxy support across the CLI [biome.jsonc:136-143]().
- **Restricted Imports**: Direct imports of `node-fetch`, `undici`, or `cross-fetch` are blocked [biome.jsonc:144-157]().
- **Complexity Management**: The linter warns when functions exceed a cognitive complexity score of 30 [biome.jsonc:108-113]().
- **Async Safety**: `noFloatingPromises` is enabled to prevent unhandled asynchronous execution paths [biome.jsonc:191-192]().
- **Import Organization**: Imports are grouped by source (React, Node built-ins, external dependencies, and internal paths) with mandatory blank lines between groups [biome.jsonc:48-94]().

### Prettier Integration
While Biome handles core logic files, **Prettier** is retained for file types Biome does not yet support, such as CSS, HTML, and Markdown [site/docs/contributing.md:177-185]().

Sources: [biome.jsonc:48-157](), [site/docs/contributing.md:177-185]()

---

## Internal Architecture Boundaries

Promptfoo enforces strict internal package boundaries to support a future multi-package split. These boundaries are defined in `architecture/layers.json` and enforced by `scripts/checkArchitectureBoundaries.ts` [docs/architecture/packages.md:1-23]().

### Layer Definitions
The codebase is divided into several logical layers with defined `tierOrder` [architecture/layers.json:9-21]():
- **contracts**: Leaf-safe shared schemas (dependency-free or `zod` only) [docs/architecture/packages.md:39-43]().
- **core**: Evaluation domain logic (assertions, matchers, prompts, scheduler) [docs/architecture/packages.md:13-13]().
- **node**: Runtime adapters (database, storage, models) [docs/architecture/packages.md:14-14]().
- **cli**: Command-line orchestration [docs/architecture/packages.md:18-18]().
- **legacy-runtime**: A transitional layer for mixed modules awaiting narrower ownership [docs/architecture/packages.md:20-20]().

### Enforcement Rules
1. **Public Facade Restriction**: Internal modules must not import `src/index.ts`, which serves as the public compatibility surface [docs/architecture/packages.md:27-31]().
2. **Leaf Layer Integrity**: The `contracts` layer may only import other contracts or external packages on the `allowedExternal` allowlist (currently only `zod`) [architecture/layers.json:141-145]().
3. **Dependency Ratchet**: Each layer declares allowed dependencies. New cross-layer relationships fail `npm run architecture:check` until reviewed [docs/architecture/packages.md:63-69]().
4. **Cycle Prevention**: The system limits the size of the largest remaining layer cycle via `maxStronglyConnectedComponentSize` (currently set to 6) [architecture/layers.json:22-22]().

**Layer Dependency Flow**

```mermaid
flowchart TD
    CLI["cli (src/commands)"] --> Core["core (src/assertions)"]
    CLI --> Providers["providers (src/providers)"]
    CLI --> ViewServer["view-server (src/server)"]
    Core --> Node["node (src/database)"]
    Core --> Contracts["contracts (src/contracts)"]
    Node --> Contracts

    subgraph "Leaf Layer"
        Contracts
    end
```

Sources: [architecture/layers.json:23-198](), [docs/architecture/packages.md:1-130](), [scripts/checkArchitectureBoundaries.ts:1-20]()

---

## Test Hygiene and Isolation

To ensure test determinism, promptfoo enforces strict isolation rules [test/AGENTS.md:24-32]().

### Automated Hygiene Checks
The `test/test-hygiene.test.ts` suite uses `oxc-parser` to statically analyze test files for anti-patterns [test/test-hygiene.test.ts:10-13]():
- **Disallowed Skip/Only**: Blocks the use of `.only()` or `.skip()` in committed code unless explicitly allowlisted for platform-specific reasons [test/test-hygiene.test.ts:56-149]().
- **Persistent Mocks**: Identifies legacy files using hoisted persistent mocks that might leak state [test/test-hygiene.test.ts:164-197]().
- **Environment Mutations**: Blocks direct `process.env` mutations in new tests [test/test-hygiene.test.ts:153-154]().

### Isolation Rules
- **Mock Cleanup**: All tests must clean up mocks in `afterEach` using `vi.resetAllMocks()` or `vi.clearAllMocks()` to prevent pollution [test/AGENTS.md:45-48]().
- **Zustand Store Testing**: Prefers integration testing with real stores over mocking. Initial state must be captured outside `describe` blocks and reset in both `beforeEach` and `afterEach` [test/AGENTS.md:158-161]().

Sources: [test/test-hygiene.test.ts:1-197](), [test/AGENTS.md:24-161]()

---

## Artifact Integrity Validation

The `scripts/testPackageArtifact.ts` script validates the integrity of the generated npm package before release [scripts/testPackageArtifact.ts:1-10]().

### Key Validations
- **Required Paths**: Ensures critical files like `dist/src/entrypoint.js`, `dist/src/main.js`, and database migration files in `dist/drizzle/` are present [scripts/testPackageArtifact.ts:39-71]().
- **Executable Permissions**: Validates that CLI entrypoints have the correct execution bits (`0o111`) [scripts/testPackageArtifact.ts:205-212]().
- **Exclusion Rules**: Confirms that source maps (`.map`), compiled tests, and mocks are excluded from the final production artifact [scripts/testPackageArtifact.ts:192-203]().
- **Dependency Range Validation**: Checks that `undici` versions in the artifact satisfy security requirements (e.g., `^6.28.0`) [scripts/testPackageArtifact.ts:41-43]().

Sources: [scripts/testPackageArtifact.ts:39-71](), [scripts/testPackageArtifact.ts:192-212]()

---

## Pull Request and Changelog Process

The project follows the **Conventional Commits** specification for all PR titles [docs/agents/pr-conventions.md:1-10]().

### Scoping Rules
- **(redteam)**: Mandatory scope if the PR touches redteam plugins, strategies, or UI [docs/agents/pr-conventions.md:107-111]().
- **(webui)**: Used for React app changes in `src/app/` [docs/agents/pr-conventions.md:85-85]().
- **(deps)**: Used for dependency updates, categorized as `fix(deps)` for patches or `chore(deps)` for major upgrades [docs/agents/pr-conventions.md:143-146]().

### Build and Release
- **tsdown.config.ts**: Manages the multi-format build (ESM and CJS). It injects build-time constants like `__PROMPTFOO_VERSION__` and `__PROMPTFOO_NODE_ENGINE_RANGE__` into the output [tsdown.config.ts:32-40]().
- **Automated Releases**: Changelog generation is automated via `release-please`. Only `feat`, `fix`, and breaking changes (`!`) appear in the user-facing release notes [docs/agents/pr-conventions.md:34-34]().

Sources: [docs/agents/pr-conventions.md:1-146](), [tsdown.config.ts:32-116](), [site/docs/contributing.md:102-109]()

# Self-Hosting and Deployment




This document provides technical documentation for self-hosting the promptfoo server and web UI. It covers deployment via Docker, Docker Compose, and Kubernetes (Helm), detailed architecture of the server and sharing systems, and the specific constraints of the SQLite-based architecture.

## Overview

Self-hosting promptfoo allows teams to persist evaluation results, share reports privately, and run evaluations within a controlled infrastructure. The self-hosted application is an Express server that serves the React-based web UI and a REST API for data persistence and sharing.

### Deployment Modes
1.  **Local Development**: Standard CLI usage where `promptfoo view` starts a temporary local server.
2.  **Self-Hosted Production**: Persistent deployment using Docker or Kubernetes with externalized storage and custom domains.
3.  **Cloud Mode**: Managed hosting via `promptfoo.app`.

## Architecture and Implementation

### Server Architecture
The server is built using Express 5 and Socket.IO for real-time updates. It serves the built React frontend and provides API endpoints for managing evaluations, providers, and red teaming configurations.

```mermaid
graph TB
    subgraph "Server_Entrypoint [src/server/index.ts]"
        startServer["startServer()"]
    end

    subgraph "Express_App [src/server/server.ts]"
        createApp["createApp()"]
        auth["Auth_Middleware"]
        apiRoutes["/api_Router"]
        static["Static_File_Server"]
        health["/health_Endpoint"]
    end

    subgraph "Data_Layer [src/migrate.ts]"
        migrate["runDbMigrations()"]
        sqlite["SQLite_DB (promptfoo.db)"]
    end

    subgraph "Real-time_Communication"
        socketIO["Socket.IO_Server"]
        signalWatcher["Signal_Watcher (File_System_Events)"]
    end

    startServer --> migrate
    migrate --> sqlite
    startServer --> createApp
    createApp --> apiRoutes
    createApp --> static
    createApp --> health
    startServer --> socketIO
    signalWatcher --> socketIO
```

**Key Components:**
- **Health Check**: A `/health` endpoint is provided for container orchestration and load balancer health checks [Dockerfile:79-79]().
- **Database Migrations**: On startup, the server ensures the SQLite schema is up to date via Drizzle migrations [package.json:67-67]().
- **Signal Watcher**: The server monitors for signal files to trigger Socket.IO `update` events, allowing the UI to refresh when a CLI-based evaluation completes.

**Sources:** [Dockerfile:78-81](), [package.json:67-67](), [package.json:74-75]()

### Sharing System Data Flow
Sharing an evaluation involves uploading results from a local environment to a remote self-hosted or cloud instance. The system supports chunked uploads to handle large evaluation payloads and mitigate 413 (Payload Too Large) errors.

```mermaid
sequenceDiagram
    participant CLI as "CLI_Entrypoint [src/entrypoint.ts]"
    participant Utils as "Share_Utilities [src/share.ts]"
    participant Remote as "Express_Server [src/server/server.ts]"
    participant DB as "SQLite_Storage [src/migrate.ts]"

    CLI->>Utils: createShareableUrl(eval)
    Utils->>Utils: determineShareDomain()
    Utils->>Remote: POST /api/eval (Metadata)
    Remote->>DB: INSERT_eval_record
    Remote-->>Utils: 201_Created (evalId)

    loop Chunked_Upload
        Utils->>Remote: POST /api/eval/:id/results (Results_Chunk)
        Remote->>DB: INSERT_eval_results
    end

    Utils-->>CLI: Return_Shareable_URL
```

**Sources:** [package.json:52-53](), [package.json:93-93](), [Dockerfile:69-70]()

## Deployment Methods

### Docker
The project provides a multi-arch Docker image using Node 24 and Python 3 for broad provider support.

**Key Dockerfile Stages:**
- **Base**: Installs `node:24.20.0-alpine` and Python 3 for provider support [Dockerfile:2-18]().
- **Builder**: Installs dependencies with `npm ci --ignore-scripts` to block untrusted lifecycle scripts, then rebuilds essential native modules like `esbuild` and `@swc/core` [Dockerfile:21-48]().
- **Server**: Final production image with `promptfoo` and `pf` linked globally, listening on port 3000 [Dockerfile:55-76]().

**Data Persistence:**
Persistence is achieved by mounting a volume to `/home/promptfoo/.promptfoo` inside the container [Dockerfile:65-65]().

**Sources:** [Dockerfile:1-81](), [package.json:49-49](), [package-lock.json:159-160]()

### Docker Compose
Docker Compose is recommended for defining environment variables and volume mounts declaratively.

```yaml
services:
  promptfoo:
    image: ghcr.io/promptfoo/promptfoo:latest
    ports:
      - '3000:3000'
    volumes:
      - ./promptfoo_data:/home/promptfoo/.promptfoo
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - PROMPTFOO_SELF_HOSTED=1
      - PROMPTFOO_RUNNING_IN_DOCKER=1
```

**Sources:** [Dockerfile:67-70]()

### Kubernetes (Helm)
Deployment to Kubernetes requires careful consideration of the storage layer.

**Critical Constraint:**
Because promptfoo uses a local SQLite database via Drizzle ORM [package.json:53-53](), it **must** be deployed as a single instance (replica count of 1). Multiple replicas cannot safely share the same SQLite file on a standard Persistent Volume.

**Persistence in K8s:**
Deployment requires a `PersistentVolumeClaim` (PVC) mounted to `/home/promptfoo/.promptfoo` to ensure data survives pod restarts [Dockerfile:65-65]().

**Sources:** [package.json:53-53](), [Dockerfile:65-65]()

## Configuration and Environment

### Environment Variables
The following variables control sharing behavior and server configuration:

| Variable | Purpose | Reference |
| :--- | :--- | :--- |
| `PROMPTFOO_SELF_HOSTED` | Signals the app it is running in a hosted environment | [Dockerfile:69-69]() |
| `PROMPTFOO_RUNNING_IN_DOCKER` | Indicates the environment is a container | [Dockerfile:70-70]() |
| `API_PORT` | Port the server listens on (default 3000) | [Dockerfile:67-67]() |
| `HOST` | Bind address (default 0.0.0.0) | [Dockerfile:68-68]() |
| `VITE_TELEMETRY_DISABLED` | Disables telemetry during the build process | [.github/workflows/main.yml:16-16]() |

**Sources:** [Dockerfile:67-72](), [.github/workflows/main.yml:16-16]()

### Reverse Proxy Setup
When deploying behind a reverse proxy (e.g., Nginx or Ingress), ensure:
1.  **WebSocket Support**: Required for Socket.IO real-time updates between the server and the React app [package-lock.json:88-89]().
2.  **Request Body Size**: Increase allowed body size to handle large evaluation uploads sent by the CLI.
3.  **HTTPS Termination**: The internal server runs on HTTP [Dockerfile:79-79]().

**Sources:** [package-lock.json:88-89](), [Dockerfile:79-79]()

## Limitations and Constraints

- **Single Instance (SQLite)**: The architecture is restricted to a single instance due to the use of SQLite (`@libsql/client`) for data persistence [package-lock.json:26-26](). Horizontal scaling is not supported in the community version.
- **Node.js Version**: The system requires Node.js >= 22.22.0 [package.json:49-49]().
- **Authentication**: The base self-hosted server provides the API and UI; advanced authentication (SSO/RBAC) must typically be handled by an external proxy or identity provider.
- **Persistence**: If the volume mount for `/home/promptfoo/.promptfoo` is omitted, all evaluation data, history, and shared results will be lost on container restart [Dockerfile:65-65]().

**Sources:** [package-lock.json:26-26](), [package.json:49-49](), [Dockerfile:65-65]()
This page documents the utility functions and output generation mechanisms used across the promptfoo evaluation pipeline. It covers file handling, prompt template rendering, variable resolution, transform function execution, extension hook dispatch, and post-evaluation output writing.

---

## Module Organization

The `src/util/` directory is organized into specialized submodules. `src/util/index.ts` re-exports from each submodule as a backwards-compatibility barrel.

| Export Module | Re-exported Symbols | Source File |
|---|---|---|
| `comparison` | `deduplicateTestCases`, `varsMatch`, `resultIsForTestCase` | [src/util/index.ts:4-11]() |
| `env` | `setupEnv` | [src/util/index.ts:13]() |
| `file` | `maybeLoadFromExternalFileWithVars`, `readOutput`, `readFilters`, `parsePathOrGlob` | [src/util/index.ts:15-22]() |
| `output` | `writeOutput`, `writeMultipleOutputs`, `createOutputMetadata` | [src/util/index.ts:24-29]() |
| `render` | `renderVarsInObject`, `renderEnvOnlyInObject` | [src/util/index.ts:33]() |
| `runtime` | `printBorder`, `isRunningUnderNpx` | [src/util/index.ts:35]() |
| `provider` | `providerToIdentifier` | [src/util/index.ts:31]() |

Sources: [src/util/index.ts:1-35]()

---

## File Handling and Variable Resolution

### Variable Resolution
The `resolveVariables` function in `src/evaluatorHelpers.ts` handles cross-references between variables within a test case. It uses a regex `\{\{\s*(\w+)\s*\}\}` to find placeholders and performs up to 5 iterations to resolve nested dependencies (e.g., `var1` referencing `var2` which references `var3`). It skips resolution for specific keys provided in `skipResolveVars`.

Sources: [src/evaluatorHelpers.ts:54-93]()

### External File Loading
The `maybeLoadFromExternalFile` utility (referenced via `src/util/file.ts`) provides a unified interface for loading content from local files via the `file://` prefix.
- **Automatic Parsing**: Detects `.json`, `.yaml`, `.yml`, and `.csv` extensions to return parsed objects/arrays instead of raw strings. [site/docs/configuration/parameters.md:195-207]()
- **CSV Handling**: The `testCaseFromCsvRow` and `assertionFromString` functions in `src/csv.ts` convert flat CSV rows into structured `TestCase` objects. It handles special column prefixes like `__expected`, `__prefix`, `__suffix`, `__description`, and `__metadata:`. [src/csv.ts:127-208](), [test/csv.test.ts:31-65]()
- **Finite Number Parsing**: `parseFiniteNumber` is used for CSV fields to ensure `0` is preserved while blank cells are treated as `undefined`. [src/csv.ts:118-125]()

Sources: [src/csv.ts:118-208](), [site/docs/configuration/parameters.md:195-207](), [test/csv.test.ts:31-65]()

### Multimedia and PDF Extraction
Promptfoo supports extracting content from external files to populate variables:
- **PDF Extraction**: The `extractTextFromPDF` function uses the `pdf-parse` library to read and trim text from PDF files. [src/evaluatorHelpers.ts:35-52]()
- **Multimedia Metadata**: `collectFileMetadata` identifies `file://` references to images, videos, and audio. It identifies the format and type based on extensions like `.jpg`, `.mp4`, or `.wav`. [src/evaluatorHelpers.ts:121-152]()
- **MIME Detection**: `getMimeTypeFromExtension` maps common extensions (e.g., `webp`, `avif`, `heic`, `svg`) to MIME types, defaulting to `image/jpeg`. [src/evaluatorHelpers.ts:172-190]()

Sources: [src/evaluatorHelpers.ts:35-190]()

---

## Prompt Rendering

The `renderPrompt` function transforms a raw prompt template into a final string sent to the provider.

### Prompt Rendering Flow
```mermaid
flowchart TD
    A["renderPrompt(prompt, vars, filters, provider)"] --> B{"Is prompt.function?"}
    B -- "Yes" --> C["Execute prompt.function({vars, provider})"]
    B -- "No" --> D["Check for file:// vars"]
    D --> E["Load external vars (JS, Python, PDF, etc.)"]
    E --> F["resolveVariables(vars)"]
    F --> G{"JSON.parse(prompt.raw) succeeds?"}
    G -- "Yes" --> H["renderVarsInObject(parsed, vars)"]
    G -- "No" --> I["nunjucks.renderString(prompt.raw, vars)"]
    H --> J["Final Rendered Prompt"]
    I --> J
    C --> J
```

Sources: [src/evaluatorHelpers.ts:54-93](), [src/util/index.ts:33](), [test/evaluatorHelpers.test.ts:177-195]()

**Key Rendering Behaviors:**
- **Auto-wrapping**: `autoWrapRawIfPartialNunjucks` detects unclosed Nunjucks tags (like `{%` or `{{`) and wraps the prompt in `{% raw %}` to prevent rendering errors. [src/evaluatorHelpers.ts:96-105]()
- **Variable Syntax**: Variables use Nunjucks templating, supporting filters (e.g., `{{message | upper}}`) and conditionals. [site/docs/configuration/parameters.md:211-222]()
- **External Integration**: Supports loading prompts directly from Portkey, Langfuse, or Helicone via URI schemes. [src/evaluatorHelpers.ts:7-9]()

Sources: [src/evaluatorHelpers.ts:7-9](), [src/evaluatorHelpers.ts:96-105](), [site/docs/configuration/parameters.md:211-222]()

---

## Transform Function Execution

The `transform` utility allows users to modify outputs or variables using JavaScript or Python.

### Implementation Details
- **JavaScript Transforms**: Loaded via `importModule`. Supports default exports, named exports (via `file.js:funcName`), or the module itself if it is a function. [src/util/index.ts:30]()
- **Python Transforms**: Executed via `runPython`. Defaults to a `get_transform` function name. [src/evaluatorHelpers.ts:12]()
- **Inline Transforms**: Handled within the `transform` utility to allow quick logic without separate files. [src/evaluatorHelpers.ts:30]()

### Transform Execution Logic
```mermaid
flowchart TD
    subgraph "Code Entity Space"
        TRANS["transform() in src/util/transform.ts"]
        JS_EXEC["importModule() in src/esm.ts"]
        PY_EXEC["runPython() in src/python/pythonUtils.ts"]
    end

    subgraph "Natural Language Space"
        INPUT["User Transform String or File Path"]
    end

    INPUT -->|"file://*.js"| JS_EXEC
    INPUT -->|"file://*.py"| PY_EXEC

    JS_EXEC --> TRANS
    PY_EXEC --> TRANS
```

Sources: [src/evaluatorHelpers.ts:12-30](), [src/util/index.ts:30]()

---

## Extension Hooks

Extension hooks allow custom code to run at specific points in the evaluation lifecycle. These are registered in the `TestSuite` and dispatched via `runExtensionHook`.

| Hook Name | Context Type | Execution Point |
|---|---|---|
| `beforeAll` | `BeforeAllExtensionHookContext` | Before evaluation starts |
| `beforeEach` | `BeforeEachExtensionHookContext` | Before a specific test case |
| `afterEach` | `AfterEachExtensionHookContext` | After a specific test case |
| `afterAll` | `AfterAllExtensionHookContext` | After all tests complete |

Sources: [test/evaluatorHelpers.test.ts:6-13]()

---

## Output Generation

Promptfoo supports generating results in multiple formats. The `writeMultipleOutputs` function iterates through target paths and dispatches to specific writers.

### Persistence and Sanitization
Before results are written to the database or output files, they are sanitized to protect credentials and prevent serialization errors.
- **Circular References**: `sanitizeForDb` uses `safeJsonStringify` to handle circular structures (like Node.js `Timeout` objects) gracefully. [src/models/evalResult.ts:142-164]()
- **Secret Redaction**: `sanitizeProvider` redacts keys like `apiKey`, `token`, and `authorization` within provider configurations. It also redacts credentials from templated WebSocket URLs. [src/models/evalResult.ts:93-131](), [test/models/evalResult.test.ts:58-132]()
- **Sensitive Headers**: A specific set of HTTP headers (e.g., `authorization`, `cookie`, `set-cookie`) are redacted via `SENSITIVE_RESPONSE_HEADER_NAMES` to ensure they aren't persisted. [src/models/evalResult.ts:199-215]()

Sources: [src/models/evalResult.ts:93-215](), [test/models/evalResult.test.ts:58-132]()

### Supported Formats
- **JSON/YAML**: Full evaluation state, including configurations and results. [site/docs/configuration/parameters.md:144-147]()
- **CSV**: Tabular view of variables and outputs. `serializeObjectArrayAsCSV` handles the conversion of internal result objects to flat CSV rows. [test/csv.test.ts:4]()
- **HTML**: Interactive report generated using templates. [site/docs/configuration/parameters.md:141]()
- **Table Transformation**: `convertResultsToTable` transforms raw `EvaluateResult` objects into the `EvaluateTable` format. It handles deduping variables, formatting output text, and injecting redteam-specific metadata like `sessionId` or `redteamFinalPrompt` into the table rows. [src/util/convertEvalResultsToTable.ts:14-156]()

Sources: [src/util/convertEvalResultsToTable.ts:14-156](), [site/docs/configuration/parameters.md:141-147](), [test/csv.test.ts:4]()
This page provides an overview of the promptfoo web application: the React frontend, the Express/Socket.IO backend server, and the real-time communication layer. It covers the component hierarchy, the API route structure, Zustand state management, and the mechanism for live evaluation updates.

For deeper dives into specific areas, see:
- [Frontend Architecture](#6.1) — Vite, routing, Tanstack Query, component hierarchy
- [Results Viewer](#6.2) — `Eval`, `ResultsView`, `ResultsTable`, `EvalOutputCell`
- [State Management](#6.3) — `useTableStore`, `useResultsViewSettingsStore`
- [Filtering and Search](#6.4) — `FiltersForm`, filter modes, metadata filters
- [Red Team Setup UI](#6.5) — Multi-step wizard, `RedTeamSetupPage`
- [Backend Server](#6.6) — Express routes in detail, Zod validation, error handling
- [Real-time Updates](#6.7) — Socket.IO `init`/`update` events
- [Red Team Report UI](#6.8) — Risk category visualization and compliance mapping
- [Model Audit UI](#6.9) — Static security scanning interface

---

## Architecture Overview

The web interface is a single-page React application served by an Express HTTP server. The server also runs a Socket.IO instance for real-time evaluation progress updates.

**System architecture diagram**

```mermaid
graph TD
    Browser["Browser (React SPA)"]
    SocketClient["SocketIOClient (socket.io-client)"]
    ExpressApp["createApp() Express app"]
    SocketIO["SocketIOServer (socket.io)"]
    StaticFiles["Static files (dist/src/app/)"]
    APIRoutes["API Routes (src/server/routes/)"]
    SQLite["SQLite DB (drizzle-orm)"]
    SignalFile["Signal file (src/database/signal.ts)"]

    Browser -->|"REST /api/*"| APIRoutes
    Browser -->|"Socket.IO"| SocketIO
    SocketClient -->|"events: init, update"| SocketIO
    ExpressApp --> StaticFiles
    ExpressApp --> APIRoutes
    APIRoutes --> SQLite
    SignalFile -->|"updateSignalFile()"| SocketIO
    SocketIO -->|"socket.emit('init')"| SocketClient
```

Sources: [src/app/src/pages/eval/components/Eval.tsx:13-13](), [src/app/src/pages/eval/components/Eval.tsx:35-36](), [src/models/eval.ts:52-55]()

---

## Backend Server

The backend is initialized via `startServer` which calls `createApp()`. The server handles data persistence for evaluations and provides the API for the frontend.

### API Route Groups

The server modularizes logic into specific routers to manage different entities:

| Router | Purpose | Key Data Entities |
|---|---|---|
| **Eval** | Result retrieval and pagination | `evalsTable`, `evalResultsTable` [src/models/eval.ts:7-8]() |
| **Redteam** | Test generation and reports | `PLUGIN_CATEGORIES`, `Severity` [src/app/src/pages/eval/components/store.ts:3-10]() |
| **User** | Identity management | `getAuthor`, `getUserEmail` [src/models/eval.ts:16-16]() |

Sources: [src/models/eval.ts:1-14](), [src/app/src/pages/eval/components/store.ts:1-12]()

---

## Real-Time Communication

The server uses a "signal file" mechanism to notify the frontend of evaluation progress. When an evaluation state changes, `updateSignalFile` or `notifyEvaluationChanged` is called.

**Real-time update flow diagram**

```mermaid
sequenceDiagram
    participant Evaluator as "Evaluator (core)"
    participant Signal as "notifyEvaluationChanged()"
    participant SocketIO as "Server (SocketIOServer)"
    participant Browser as "Eval.tsx (SocketIOClient)"

    Evaluator->>Signal: "Evaluation state changed"
    Signal->>SocketIO: "io.emit('update', { evalId })"
    SocketIO->>Browser: "on('update', handleResultsFile)"
    Browser->>Browser: "fetchEvalData(id)"
```

Sources: [src/models/eval.ts:51-55](), [src/app/src/pages/eval/components/Eval.tsx:171-180]()

---

## Frontend Structure

The React application uses `react-router-dom` for navigation and `Navigation.tsx` for the top-level menu. It is built around a centralized table view for results.

**Frontend component hierarchy diagram**

```mermaid
graph TD
    App["App.tsx (Entry)"]
    Nav["Navigation.tsx"]
    Eval["Eval.tsx (Container)"]
    ResultsView["ResultsView.tsx"]
    ResultsTable["ResultsTable.tsx"]
    EvalOutputCell["EvalOutputCell.tsx"]
    TableStore["useTableStore (Zustand)"]

    App --> Nav
    App --> Eval
    Eval --> ResultsView
    ResultsView --> ResultsTable
    ResultsTable --> EvalOutputCell
    Eval -.->|"fetchEvalData"| TableStore
    ResultsTable -.->|"selects state"| TableStore
```

Sources: [src/app/src/pages/eval/components/Eval.tsx:61-77](), [src/app/src/pages/eval/components/ResultsView.tsx:41-45](), [src/app/src/pages/eval/components/ResultsTable.tsx:40-50]()

### State Management

Global state is managed primarily through Zustand stores to maintain UI consistency:

- **useTableStore**: Manages evaluation data, pagination (`pageIndex`, `pageSize`), and filtering (`ResultsFilter[]`) [src/app/src/pages/eval/components/store.ts:12-28]().
- **useResultsViewSettingsStore**: Tracks UI preferences like `renderMarkdown`, `inComparisonMode`, and column visibility [src/app/src/pages/eval/components/store.ts:13-16]().
- **Filter Management**: Handles complex logic for red team specific filters like `plugin`, `strategy`, and `severity` [src/app/src/pages/eval/components/store.ts:145-172]().

### Core UI Components

- **ResultsTable**: A high-performance table built with `@tanstack/react-table` that handles large evaluation datasets with virtualization and custom cell rendering [src/app/src/pages/eval/components/ResultsTable.tsx:39-44]().
- **EvalOutputCell**: Renders individual model outputs, supporting text, markdown, and media (images, audio, video) with support for human rating and feedback [src/app/src/pages/eval/components/EvalOutputCell.tsx:88-118]().
- **Navigation**: Provides access to "New" setups (Eval, Red Team, Model Audit) and "Results" views [src/app/src/components/Navigation.tsx:133-172]().
- **StorageRefAudioPlayer**: Handles asynchronous resolution of audio references (blobs/storage refs) into playable elements [src/app/src/pages/eval/components/ResultsTable.tsx:98-144]().

Sources: [src/app/src/pages/eval/components/ResultsTable.tsx:15-21](), [src/app/src/pages/eval/components/EvalOutputCell.tsx:1-32](), [src/app/src/components/Navigation.tsx:206-215]()

# Frontend Architecture




The promptfoo web application is a modern React-based single-page application (SPA) designed to provide a rich graphical interface for viewing evaluation results, configuring red team tests, and managing prompts and datasets. It is built using **Vite** for fast development and optimized production builds, and utilizes **Tanstack Query** for data synchronization and **Radix UI** for accessible component primitives.

## Technology Stack

The frontend architecture is built on a foundation of industry-standard libraries and tools:

| Category | Technology | Purpose |
| :--- | :--- | :--- |
| **Framework** | React 18+ | UI component architecture and state management. |
| **Build Tool** | Vite | Module bundling, HMR, and build optimization [src/app/vite.config.ts:7-14](). |
| **Data Fetching** | Tanstack Query (v5) | Server state management, caching, and synchronization [src/app/src/App.tsx:3-10](). |
| **Routing** | React Router (v6) | Declarative routing and navigation [src/app/src/App.tsx:4-12](). |
| **UI Components** | Radix UI / Shadcn UI | Accessible, unstyled primitives for complex UI elements [src/app/src/components/Navigation.tsx:3-11](). |
| **Styling** | Tailwind CSS v4 | Utility-first CSS framework using modern CSS variables [src/app/src/index.css:1-2](). |
| **Real-time** | Socket.IO Client | Bi-directional communication for live evaluation updates. |
| **State Management** | Zustand | Lightweight store for local UI state (e.g., table settings). |

**Sources:** [src/app/vite.config.ts:1-182](), [src/app/src/App.tsx:1-147](), [src/app/src/components/Navigation.tsx:1-21](), [src/app/src/index.css:1-237]()

## Routing and App Structure

The application's entry point is `App.tsx`, which configures global providers (e.g., `QueryClientProvider`, `TooltipProvider`, `ToastProvider`) and defines the routing hierarchy using `createBrowserRouter` [src/app/src/App.tsx:49-145]().

### Route Definition

The application uses a nested route structure. Most pages are wrapped in a `PageShell` component that provides consistent navigation and layout [src/app/src/App.tsx:55-55](). The `TelemetryTracker` component is used as a wrapper to record `webui_page_view` events on every route change via the `useTelemetry` hook [src/app/src/App.tsx:38-47]().

```mermaid
graph TD
    App["App [src/app/src/App.tsx]"] --> Providers["Providers (QueryClient, Toast, History)"]
    Providers --> Router["RouterProvider"]
    Router --> Shell["PageShell [src/app/src/components/PageShell.tsx]"]

    subgraph "Routes [src/app/src/App.tsx]"
        Shell --> Telemetry["TelemetryTracker [src/app/src/App.tsx:38]"]
        Telemetry --> Eval["/eval - EvalPage [src/app/src/pages/eval/page.tsx]"]
        Telemetry --> Evals["/evals - EvalsIndexPage [src/app/src/pages/evals/page.tsx]"]
        Telemetry --> Setup["/setup - EvalCreatorPage [src/app/src/pages/eval-creator/page.tsx]"]
        Telemetry --> Redteam["/redteam/setup - RedteamSetupPage [src/app/src/pages/redteam/setup/page.tsx]"]
        Telemetry --> Reports["/reports - ReportPage [src/app/src/pages/redteam/report/page.tsx]"]
        Telemetry --> History["/history - HistoryPage [src/app/src/pages/history/page.tsx]"]
        Telemetry --> Datasets["/datasets - DatasetsPage [src/app/src/pages/datasets/page.tsx]"]
        Telemetry --> Prompts["/prompts - PromptsPage [src/app/src/pages/prompts/page.tsx]"]
        Telemetry --> ModelAudit["/model-audit - ModelAuditSetupPage [src/app/src/pages/model-audit-setup/page.tsx]"]
    end
```

**Sources:** [src/app/src/App.tsx:38-129](), [src/app/src/App.tsx:133-145]()

## Component Hierarchy

The application follows a modular component structure, separating layout, common UI elements, and page-specific logic.

### PageShell and Navigation

The `PageShell` acts as the primary layout wrapper, containing the `Navigation` component and an `Outlet` for rendering the current route's content [src/app/src/App.tsx:55-57]().

The `Navigation` component provides the top-level app bar and dropdown menus for navigating between different functional areas:
*   **New**: Entry points for creating evaluations (`/setup`), red team setups (`/redteam/setup`), and model audits (`/model-audit/setup`) [src/app/src/components/Navigation.tsx:133-149]().
*   **View Results**: Links to the latest results, all evaluations, vulnerability reports, and the media library [src/app/src/components/Navigation.tsx:151-172]().
*   **Browse**: Access to prompts, datasets, and historical runs [src/app/src/components/Navigation.tsx:174-195]().

The navigation bar uses a `sticky` header with a specific z-index defined by `--z-appbar` (1200) to ensure it stays above page content but below modals [src/app/src/components/Navigation.tsx:206](), [src/app/src/index.css:221]().

```mermaid
graph LR
    subgraph "Navigation.tsx [src/app/src/components/Navigation.tsx]"
        Logo["Logo [src/app/src/components/Logo.tsx]"]
        NavMenu["NavigationMenu (Radix)"]
        NavMenu --> New["'New' Dropdown (createMenuItems)"]
        NavMenu --> Results["'Results' Dropdown (resultsMenuItems)"]
        NavMenu --> Browse["'Browse' Dropdown (browseMenuItems)"]
        Theme["ThemeSelector [src/app/src/components/ThemeSelector.tsx]"]
    end

    PageShell["PageShell [src/app/src/components/PageShell.tsx]"] --> Navigation
    PageShell --> Content["Outlet (Page Content)"]
```

**Sources:** [src/app/src/components/Navigation.tsx:197-230](), [src/app/src/App.tsx:55-125](), [src/app/src/index.css:220-225]()

### Data Table Architecture

The application relies heavily on a shared `DataTable` component built on **Tanstack Table** [src/app/src/components/data-table/data-table.tsx:1-16](). It is used across Prompts [src/app/src/pages/prompts/Prompts.tsx:139](), Datasets [src/app/src/pages/datasets/Datasets.tsx:168](), and History pages.

| Feature | Implementation Detail |
| :--- | :--- |
| **Virtualization** | Supports `client-virtualized` and `server-virtualized` modes using `@tanstack/react-virtual` [src/app/src/components/data-table/data-table.tsx:17-37](). |
| **Filtering** | Uses `DataTableHeaderFilter` and `operatorFilterFn` for column-level control [src/app/src/components/data-table/data-table.tsx:19-20](). |
| **Column Sizing** | Implements manual resizing via `renderDataTableHeaderResizeHandle` [src/app/src/components/data-table/data-table.tsx:135-156](). |
| **Sticky Columns** | Allows pinning columns to the `left` or `right` edges [src/app/src/components/data-table/data-table.tsx:38-43](). |

**Sources:** [src/app/src/components/data-table/data-table.tsx:1-206](), [src/app/src/pages/prompts/Prompts.tsx:139-148](), [src/app/src/pages/datasets/Datasets.tsx:168-177]()

## Data Flow and State Management

Data flow in the frontend is primarily managed through Tanstack Query for server-side data and Zustand for local UI state.

### Server State (Tanstack Query)

The frontend interacts with the Express backend via REST API calls. Tanstack Query manages the lifecycle of these requests. For example, `ReportPage` checks for user authentication via `useUserStore` before rendering reports [src/app/src/pages/redteam/report/page.tsx:14-29]().

### Local State (Zustand)

Zustand stores are used for UI-specific state that needs to persist across component re-renders:
*   **useUserStore**: Manages user session state, including the user's email and login status [src/app/src/pages/redteam/report/page.tsx:14]().
*   **useTableStore**: Manages table-specific configurations like column visibility and filtering.

### Authentication Flow

The `LoginPage` handles user authentication. Upon successful login, it updates the global user state. The `ReportPage` uses this state to redirect unauthenticated users to `/login` [src/app/src/pages/redteam/report/page.tsx:26-29]().

**Sources:** [src/app/src/pages/redteam/report/page.tsx:11-46](), [src/app/src/App.tsx:131-141]()

## Build and Development

The frontend build process is managed by Vite, configured in `vite.config.ts`.

| Feature | Implementation |
| :--- | :--- |
| **Aliases** | `@app` maps to `./src`, `@promptfoo` maps to `../` [src/app/vite.config.ts:79-82](). |
| **Code Splitting** | Vendor groups are used to optimize chunking via `vendorCodeSplittingGroups` [src/app/vite.config.ts:96-102](). |
| **Environment** | Exposes `VITE_` prefixed variables like `VITE_PUBLIC_PROMPTFOO_REMOTE_API_BASE_URL` [src/app/vite.config.ts:65-68](). |
| **Testing** | Uses Vitest with `jsdom` and parallelizes via child process forks to prevent memory leaks [src/app/vite.config.ts:106-120](). |

**Sources:** [src/app/vite.config.ts:72-182]()

## Testing Infrastructure

Frontend components are tested using **Vitest** and **React Testing Library**.

*   **Component Tests**: `Navigation.test.tsx` verifies that all navigation links and dropdowns render correctly and respond to user events, including theme switching [src/app/src/components/Navigation.test.tsx:86-155]().
*   **DataTable Tests**: `data-table.test.tsx` ensures virtualization, filtering, and sorting work across different screen sizes [src/app/src/components/data-table/data-table.test.tsx:53-200]().
*   **Routing Tests**: `ReportPage.test.tsx` ensures that the report viewer reacts correctly to URL search parameters like `evalId` and handles authentication redirects [src/app/src/pages/redteam/report/page.test.tsx:67-104]().

**Sources:** [src/app/src/components/Navigation.test.tsx:72-206](), [src/app/src/pages/redteam/report/page.test.tsx:52-181](), [src/app/src/components/data-table/data-table.test.tsx:1-191]()

# Results Viewer




This page documents the evaluation results viewer in the promptfoo web application: the components responsible for loading, displaying, filtering, and interacting with evaluation output data. It covers the `Eval`, `ResultsView`, `ResultsTable`, and `EvalOutputCell` components, as well as the Zustand stores that back them.

For information about the Zustand stores themselves (state shape, actions, initialization), see [State Management](#6.3). For filtering and search behavior in detail, see [Filtering and Search](#6.4). For the backend API routes that supply data to these components, see [Backend Server](#6.6).

---

## Component Hierarchy

The results viewer is composed of several layers of React components, each with a clearly scoped responsibility.

**Component Hierarchy Diagram**

```mermaid
graph TD
    EvalTsx["Eval\n(Eval.tsx)"]
    ResultsViewTsx["ResultsView\n(ResultsView.tsx)"]
    EvalHeaderTsx["EvalHeader\n(EvalHeader.tsx)"]
    ResultsChartsTsx["ResultsCharts\n(ResultsCharts.tsx)"]
    FiltersFormTsx["FiltersForm\n(ResultsFilters/FiltersForm.tsx)"]
    ColumnSelectorTsx["ColumnSelector\n(ColumnSelector.tsx)"]
    FilterModeSelectorTsx["FilterModeSelector\n(FilterModeSelector.tsx)"]
    ResultsTableTsx["ResultsTable\n(ResultsTable.tsx)"]
    ResultsTableHeaderTsx["ResultsTableHeader\n(inner component)"]
    EvalOutputCellTsx["EvalOutputCell\n(EvalOutputCell.tsx)"]
    VariableCell["VariableMarkdownCell /\nTruncatedText"]
    SettingsModal["SettingsModal\n(TableSettings/TableSettingsModal.tsx)"]
    ShareModal["ShareModal\n(ShareModal.tsx)"]
    EvalOutputPromptDialogTsx["EvalOutputPromptDialog\n(EvalOutputPromptDialog.tsx)"]

    EvalTsx --> ResultsViewTsx
    ResultsViewTsx --> EvalHeaderTsx
    ResultsViewTsx --> ResultsChartsTsx
    ResultsViewTsx --> FiltersFormTsx
    ResultsViewTsx --> ColumnSelectorTsx
    ResultsViewTsx --> FilterModeSelectorTsx
    ResultsViewTsx --> ResultsTableTsx
    ResultsViewTsx --> SettingsModal
    ResultsViewTsx --> ShareModal
    ResultsTableTsx --> ResultsTableHeaderTsx
    ResultsTableTsx --> EvalOutputCellTsx
    ResultsTableTsx --> VariableCell
    EvalOutputCellTsx --> EvalOutputPromptDialogTsx
```

Sources: `[src/app/src/pages/eval/components/Eval.tsx:61-77]()`, `[src/app/src/pages/eval/components/ResultsView.tsx:40-45]()`, `[src/app/src/pages/eval/components/ResultsTable.tsx:47-56]()`, `[src/app/src/pages/eval/components/EvalOutputCell.tsx:36-51]()`

---

## Data Loading and State Flow

The `Eval` component is the entry point. It calls `fetchEvalData` from `useTableStore`, which fetches evaluation data from the Express backend and populates the store.

**Data Flow Diagram**

```mermaid
sequenceDiagram
    participant EvalTsx as "Eval.tsx"
    participant useTableStore as "useTableStore"
    participant BackendAPI as "GET /api/eval/:id/table"
    participant ResultsViewTsx as "ResultsView.tsx"
    participant ResultsTableTsx as "ResultsTable.tsx"

    EvalTsx->>useTableStore: "fetchEvalData(id, options)"
    useTableStore->>BackendAPI: "callApi('/eval/${id}/table/')"
    BackendAPI-->>useTableStore: "EvalTableDTO { table, config, version, ... }"
    useTableStore-->>EvalTsx: "table, config, evalId set in store"
    EvalTsx->>ResultsViewTsx: "renders when table != null"
    ResultsViewTsx->>ResultsTableTsx: "passes columnVisibility, filterMode, zoom"
    ResultsTableTsx->>useTableStore: "reads table.head, table.body"
    ResultsTableTsx->>useTableStore: "calls fetchEvalData on pagination/filter change"
```

Sources: `[src/app/src/pages/eval/components/Eval.tsx:124-154]()`, `[src/app/src/pages/eval/components/store.ts:534-650]()`, `[src/app/src/pages/eval/components/ResultsTable.tsx:597-650]()`

### `Eval` Component

`Eval` ([src/app/src/pages/eval/components/Eval.tsx]()) is responsible for:

- Calling `fetchRecentFileEvals` (`GET /results`) on mount to populate the eval selector `[src/app/src/pages/eval/components/Eval.tsx:99-114]()`.
- Calling `loadEvalById` with the `fetchId` URL parameter to load a specific eval `[src/app/src/pages/eval/components/Eval.tsx:124-154]()`.
- Establishing a Socket.IO connection to receive real-time evaluation progress updates via the `init` and `update` events `[src/app/src/pages/eval/components/Eval.tsx:255-290]()`.
- Deserializing URL `filter` query parameters via `parseFiltersParam` and applying them to the store on mount `[src/app/src/pages/eval/components/Eval.tsx:38-48]()`.

When the table data is successfully loaded, it renders `ResultsView`. If no eval is found, it renders `EmptyState` `[src/app/src/pages/eval/components/Eval.tsx:300-350]()`.

### `fetchEvalData` in `useTableStore`

The `fetchEvalData` action ([src/app/src/pages/eval/components/store.ts:534-650]()) is the central data-loading function. It accepts an `id` and `FetchEvalOptions`:

| Option | Type | Purpose |
|---|---|---|
| `pageIndex` | `number` | Page offset for paginated results |
| `pageSize` | `number` | Number of rows per page |
| `filterMode` | `EvalResultsFilterMode` | `all`, `failures`, `errors`, `user-rated` |
| `searchText` | `string` | Full-text search query |
| `filters` | `ResultsFilter[]` | Structured metadata/metric/plugin/strategy filters |
| `skipSettingEvalId` | `boolean` | Avoids re-setting `evalId` during pagination |
| `skipLoadingState` | `boolean` | Suppresses loading spinner during background updates |

The function calls `callApi` to `GET /api/eval/${id}/table/` with the relevant query parameters, then updates the Zustand store with the returned `EvalTableDTO` `[src/app/src/pages/eval/components/store.ts:630-680]()`.

---

## ResultsView

`ResultsView` ([src/app/src/pages/eval/components/ResultsView.tsx]()) orchestrates the toolbar, filter chips, charts, and table. It does not directly fetch data; it reads from `useTableStore` and `useResultsViewSettingsStore`.

**Key responsibilities:**

- **Search**: Maintains `searchInputValue` and `debouncedSearchText` (passed to `ResultsTable`). Uses `useDebouncedCallback` for efficient searching `[src/app/src/pages/eval/components/ResultsView.tsx:340-355]()`.
- **Column management**: Computes `currentColumnState` from `columnStates` in `useResultsViewSettingsStore`, keyed by `currentEvalId` `[src/app/src/pages/eval/components/ResultsView.tsx:320-330]()`.
- **Filter mode**: Supports modes like `all`, `failures`, `errors`, `user-rated`, and `different`. The `different` mode highlights rows where outputs vary across prompts `[src/app/src/pages/eval/components/ResultsView.tsx:430-450]()`.
- **Charts**: `ResultsCharts` provides visualizations of scores across prompts and providers. Visibility is toggled based on viewport height `MIN_VIEWPORT_HEIGHT_FOR_CHARTS = 1100` `[src/app/src/pages/eval/components/ResultsView.tsx:61-186]()`.
- **Zoom**: Controls `resultsTableZoom`, applied to the `ResultsTable` for better visibility of large datasets `[src/app/src/pages/eval/components/ResultsView.tsx:490-510]()`.

Sources: `[src/app/src/pages/eval/components/ResultsView.tsx:63-600]()`

---

## ResultsTable

`ResultsTable` ([src/app/src/pages/eval/components/ResultsTable.tsx]()) is the core display component. It uses **TanStack Table v8** to manage column definitions, sizing, and visibility `[src/app/src/pages/eval/components/ResultsTable.tsx:33-44]()`.

### Column Construction

Columns are built dynamically in three groups:

- **Variable columns**: One column per entry in `head.vars`. Cells render using `VariableMarkdownCell` `[src/app/src/pages/eval/components/ResultsTable.tsx:718-750]()`.
- **Metadata columns**: Displays evaluation metadata keys. Column width is estimated based on content length percentiles `[src/app/src/pages/eval/components/ResultsTable.tsx:187-198]()`.
- **Prompt columns**: One column per prompt/provider combination. Each cell renders an `EvalOutputCell` `[src/app/src/pages/eval/components/ResultsTable.tsx:830-870]()`.

Column sizes are initialized using heuristics like `estimateMetadataColumnSize` or defaults like `PROMPT_COLUMN_SIZE_PX = 480` `[src/app/src/pages/eval/components/ResultsTable.tsx:146-199]()`.

Sources: `[src/app/src/pages/eval/components/ResultsTable.tsx:670-950]()`

### Custom Metrics and Totals

The table displays aggregated metrics in the header:
- **Token Usage**: Displays total tokens, provider tokens (or target tokens for redteam), and average tokens `[src/app/src/pages/eval/components/ResultsTable.tsx:22-26]()`.
- **Named Metrics**: Displays specific scores like cost and latency, formatted via `formatDuration` `[src/app/src/pages/eval/components/ResultsTable.tsx:19-20]()`.
- **Pass Rates**: Visual indicators of test success per prompt using `usePassRates` hook `[src/app/src/pages/eval/components/ResultsTable.tsx:72-78]()`.

---

## EvalOutputCell

`EvalOutputCell` ([src/app/src/pages/eval/components/EvalOutputCell.tsx]()) renders a single output cell.

### Output Rendering Logic

The component handles various media types and display modes:
- **Diffs**: If `showDiffs` is enabled, it renders JSON, sentence, or word diffs using the `diff` library `[src/app/src/pages/eval/components/EvalOutputCell.tsx:21-32]()`.
- **Media**: Detects image and video providers via `isImageProvider` and `isVideoProvider` to prevent incorrect text truncation `[src/app/src/pages/eval/components/EvalOutputCell.tsx:89-119]()`.
- **Markdown**: Renders output as markdown using `ReactMarkdown` with `REMARK_PLUGINS` `[src/app/src/pages/eval/components/EvalOutputCell.tsx:34-40]()`.
- **Audio**: Supports `StorageRefAudioPlayer` for base64 or storage-referenced audio data `[src/app/src/pages/eval/components/ResultsTable.tsx:98-143]()`.

### Cell Actions
The cell includes an action row with buttons for:
- Human pass/fail rating (`ThumbsUp`/`ThumbsDown`). For redteam, these are labeled "Mark as safe"/"Mark as vulnerable" `[src/app/src/pages/eval/components/EvalOutputCell.test.tsx:184-200]()`.
- Numeric scoring via `SetScoreDialog` `[src/app/src/pages/eval/components/EvalOutputCell.tsx:41-43]()`.
- Viewing detailed output/test details (`EvalOutputPromptDialog`) `[src/app/src/pages/eval/components/EvalOutputCell.tsx:37-49]()`.

Sources: `[src/app/src/pages/eval/components/EvalOutputCell.tsx:460-850]()`

---

## EvalOutputPromptDialog

`EvalOutputPromptDialog` ([src/app/src/pages/eval/components/EvalOutputPromptDialog.tsx]()) provides a detailed inspection view for a single evaluation result using a Radix UI `Sheet` `[src/app/src/pages/eval/components/EvalOutputPromptDialog.tsx:5-10]()`.

**Key features:**
- **Prompt & Output**: Displays the raw prompt, provider-specific prompt, and model output in a syntax-highlighted `CodeDisplay` `[src/app/src/pages/eval/components/EvalOutputPromptDialog.tsx:49-111]()`.
- **Tabs**: Organizes data into "Prompt & Output", "Metadata", "Evaluation", and "Traces" `[src/app/src/pages/eval/components/EvalOutputPromptDialog.tsx:11-18]()`.
- **Replay**: Allows editing the prompt and re-running the evaluation directly from the UI via `onReplay` `[src/app/src/pages/eval/components/EvalOutputPromptDialog.tsx:116-129]()`.
- **Tracing**: Fetches and displays OpenTelemetry traces associated with the evaluation via `fetchTraces` `[src/app/src/pages/eval/components/EvalOutputPromptDialog.tsx:184-198]()`.

Sources: `[src/app/src/pages/eval/components/EvalOutputPromptDialog.tsx:1-205]()`

---

## Comparison Mode

Comparison mode allows multiple evaluations to be displayed side by side.

When `inComparisonMode` is `true`:
- `comparisonEvalIds` in `useResultsViewSettingsStore` holds the additional eval IDs `[src/app/src/pages/eval/components/store.ts:81-82]()`.
- `fetchEvalData` triggers the backend to merge results from multiple evals into a single `EvaluateTable` `[src/app/src/pages/eval/components/store.ts:534-550]()`.
- Diff mode is available in `EvalOutputCell` to compare outputs against a baseline prompt column.

Sources: `[src/app/src/pages/eval/components/store.ts:13-29]()`, `[src/app/src/pages/eval/components/ResultsTable.tsx:30-32]()`

---

## Settings Persistence

`useResultsViewSettingsStore` is persisted to `localStorage` to maintain user preferences across sessions `[src/app/src/pages/eval/components/store.ts:12-13]()`.

| Field | Description |
|---|---|
| `maxTextLength` | Max chars before truncation in cells |
| `renderMarkdown` | Enable markdown rendering in cells |
| `prettifyJson` | Pretty-print JSON output |
| `showInferenceDetails` | Show token/latency/cost stats |
| `columnStates` | Per-eval column visibility state |

Sources: `[src/app/src/pages/eval/components/store.ts:13-28]()`

# State Management




This page documents the Zustand-based state management system used by the promptfoo web application's evaluation viewer. It covers the primary stores (`useTableStore` and `useResultsViewSettingsStore`), their state shapes, actions, and how components interact with them.

For documentation on the React components that consume this state, see [Results Viewer (6.2)](). For filtering and search UI behavior, see [Filtering and Search (6.4)](). For the red team configuration wizard's store (`useRedTeamConfig`), see [Red Team Setup UI (6.5)]().

---

## Store Architecture Overview

The eval viewer uses two Zustand stores, both defined in [src/app/src/pages/eval/components/store.ts]().

| Store | Middleware | Persistence | Responsibility |
|---|---|---|---|
| `useTableStore` | `subscribeWithSelector` | None (session-only) | Evaluation data, filters, fetch state |
| `useResultsViewSettingsStore` | `persist` | `localStorage` (`eval-settings`) | Display preferences, column visibility, comparison mode |

A third store, `useStore` from `src/app/src/stores/evalConfig.ts`, handles red team configuration and is imported as `useMainStore` in `ResultsView.tsx` [src/app/src/pages/eval/components/ResultsView.tsx:21-21]().

**Store-to-Component Dependency Diagram**

Title: Store-to-Component Dependency Diagram
```mermaid
graph TD
    subgraph "src/app/src/pages/eval/components/store.ts"
        TS["useTableStore"]
        SS["useResultsViewSettingsStore"]
    end

    subgraph "src/app/src/stores/evalConfig.ts"
        EC["useStore (useMainStore)"]
    end

    EvalTsx["Eval.tsx"] -->|"fetchEvalData, setEvalId, filters"| TS
    ResultsViewTsx["ResultsView.tsx"] -->|"table, config, evalId, filters"| TS
    ResultsViewTsx -->|"columnStates, comparisonEvalIds, wordBreak"| SS
    ResultsViewTsx -->|"updateConfig"| EC
    ResultsTableTsx["ResultsTable.tsx"] -->|"table, evalId, fetchEvalData, filters"| TS
    ResultsTableTsx -->|"inComparisonMode, renderMarkdown"| SS
    EvalOutputCellTsx["EvalOutputCell.tsx"] -->|"shouldHighlightSearchText, addFilter"| TS
    EvalOutputCellTsx -->|"renderMarkdown, showPassFail, showPrompts"| SS
    FiltersFormTsx["ResultsFilters/FiltersForm.tsx"] -->|"filters, metadataKeys, addFilter, updateFilter"| TS
```
Sources: [src/app/src/pages/eval/components/store.ts:12-13](), [src/app/src/pages/eval/components/Eval.tsx:67-81](), [src/app/src/pages/eval/components/ResultsView.tsx:44-44](), [src/app/src/pages/eval/components/ResultsTable.tsx:54-54](), [src/app/src/pages/eval/components/EvalOutputCell.tsx:42-42]()

---

## `useTableStore`

### Purpose

`useTableStore` is the primary data store for the eval results page. It owns the evaluated data (`EvaluateTable`), the current eval's configuration, filter state, pagination, metadata keys for filters, and async fetch state.

It is created using Zustand's `subscribeWithSelector` middleware [src/app/src/pages/eval/components/store.ts:13-13](), which allows external code (notably `Eval.tsx`) to subscribe to specific state slices without causing React re-renders.

### State Shape

**`TableState` interface** [src/app/src/pages/eval/components/store.ts:268-401]()

| Field | Type | Description |
|---|---|---|
| `evalId` | `string \| null` | ID of the currently loaded evaluation |
| `author` | `string \| null` | Author of the eval |
| `table` | `EvaluateTable \| null` | Rendered table data (head + body rows) |
| `config` | `Partial<UnifiedConfig> \| null` | Full eval configuration |
| `version` | `number \| null` | Eval schema version (3 = old, 4 = normalized) |
| `filteredResultsCount` | `number` | Count of results matching current filters |
| `totalResultsCount` | `number` | Unfiltered total result count |
| `highlightedResultsCount` | `number` | Outputs with `!highlight` comment prefix |
| `userRatedResultsCount` | `number` | Outputs with a `human` assertion type rating |
| `filteredMetrics` | `PromptMetrics[] \| null` | Backend-calculated metrics for the filtered dataset |
| `stats` | `EvaluateStats \| null` | Eval-level statistics (e.g., `durationMs`) |
| `isFetching` | `boolean` | True while `fetchEvalData` is in-flight |
| `isStreaming` | `boolean` | True when a Socket.IO live update is in progress |
| `shouldHighlightSearchText` | `boolean` | Enables search highlight rendering in cells |
| `filters` | `FiltersState` | Nested filter state (see below) |
| `metadataKeys` | `string[]` | Available metadata keys for the metadata filter |
| `metadataValues` | `Record<string, string[]>` | Cached metadata values per key |
| `filterMode` | `EvalResultsFilterMode` | Active display mode (`all`, `failures`, `errors`, etc.) |

### Filter State

The `filters` field is a nested object within `useTableStore` [src/app/src/pages/eval/components/store.ts:355-381]():

```typescript
filters: {
  values:          Record<string, ResultsFilter>   // all defined filters
  appliedCount:    number                          // filters with a non-empty value
  options: {
    metric:        string[]                        // available metric names
    metadata:      string[]                        // available metadata keys
    plugin?:       string[]                        // redteam only
    strategy?:     string[]                        // redteam only
    severity?:     string[]                        // redteam only
    policy?:       string[]                        // redteam only
  }
  policyIdToNameMap?: Record<string, string>       // policy ID → display name
}
```

The `ResultsFilter` type [src/app/src/pages/eval/components/store.ts:248-266]():

| Field | Type | Description |
|---|---|---|
| `id` | `string` | UUID, assigned at creation |
| `type` | `ResultsFilterType` | `metric`, `metadata`, `plugin`, `strategy`, `severity`, `policy` |
| `operator` | `ResultsFilterOperator` | `equals`, `contains`, `exists`, `gt`, `lte`, etc. |
| `value` | `string` | Filter value |
| `field` | `string?` | For metadata/metric filters: the key name |
| `logicOperator` | `'AND' \| 'OR'` | How this filter combines with others |

### Actions

| Action | Signature | Effect |
|---|---|---|
| `setEvalId` | `(id: string) => void` | Sets `evalId`, clears `filteredMetrics` [src/app/src/pages/eval/components/store.ts:543-546]() |
| `setTable` | `(table: EvaluateTable \| null) => void` | Sets `table`, recomputes highlight/rated counts [src/app/src/pages/eval/components/store.ts:553-562]() |
| `fetchEvalData` | `(id, options?) => Promise<EvalTableDTO \| null>` | Fetches paginated eval data from the API [src/app/src/pages/eval/components/store.ts:654-700]() |
| `addFilter` | `(filter) => void` | Appends a new filter to `filters.values` [src/app/src/pages/eval/components/store.ts:586-591]() |
| `removeFilter` | `(id) => void` | Removes a filter by ID [src/app/src/pages/eval/components/store.ts:592-598]() |
| `updateFilter` | `(filter) => void` | Updates an existing filter by ID [src/app/src/pages/eval/components/store.ts:602-608]() |

### `fetchEvalData` Async Flow

`fetchEvalData` is the central async action. It is called from `Eval.tsx` (initial load), `ResultsTable.tsx` (pagination and filter changes), and indirectly from Socket.IO update handlers.

**`fetchEvalData` Sequence Diagram**

Title: fetchEvalData Sequence Diagram
```mermaid
sequenceDiagram
    participant "Caller (Eval.tsx / ResultsTable.tsx)" as Caller
    participant "useTableStore.fetchEvalData" as Store
    participant "API /api/results/:id/table" as API
    participant "buildRedteamFilterOptions" as FilterBuilder

    Caller->>Store: "fetchEvalData(id, options)"
    Store->>Store: "set isFetching = true (unless skipLoadingState)"
    Store->>API: "GET /api/results/:id/table?pageIndex=&pageSize=&filterMode=&filters="
    API-->>Store: "EvalTableDTO { table, config, version, filteredCount, totalCount, filteredMetrics, stats }"
    Store->>FilterBuilder: "buildRedteamFilterOptions(config, table)"
    FilterBuilder-->>Store: "{ plugin, strategy, severity, policy }"
    Store->>Store: "set table, config, version, counts, filters.options, stats"
    Store->>Store: "set isFetching = false"
    Store-->>Caller: "EvalTableDTO | null"
```
Sources: [src/app/src/pages/eval/components/store.ts:654-700](), [src/app/src/pages/eval/components/Eval.tsx:124-154](), [src/app/src/pages/eval/components/ResultsTable.tsx:635-649]() (implied by table state dependencies).

### Derived / Computed Values

Several computed values are re-derived when `setTable` is called [src/app/src/pages/eval/components/store.ts:30-53]():

| Helper | Triggers on | Returns |
|---|---|---|
| `computeHighlightCount(table)` | `setTable` | Count of outputs where `gradingResult.comment` starts with `!highlight` [src/app/src/pages/eval/components/store.ts:30-40]() |
| `computeUserRatedCount(table)` | `setTable` | Count of outputs with a component result of type `human` [src/app/src/pages/eval/components/store.ts:46-53]() |
| `computeAvailableMetrics(table)` | `fetchEvalData` | Sorted list of unique metric names from `prompt.metrics.namedScores` [src/app/src/pages/eval/components/store.ts:55-73]() |

Sources: [src/app/src/pages/eval/components/store.ts:30-73]()

---

## `useResultsViewSettingsStore`

### Purpose

`useResultsViewSettingsStore` stores user interface display preferences. Unlike `useTableStore`, its state is persisted to `localStorage` under the key `eval-settings` (version 2) using Zustand's `persist` middleware [src/app/src/pages/eval/components/store.ts:445-510]().

### State Shape

**`SettingsState` interface** [src/app/src/pages/eval/components/store.ts:403-443]()

| Field | Type | Default | Description |
|---|---|---|---|
| `maxTextLength` | `number` | `250` | Max characters before text truncation |
| `wordBreak` | `'break-word' \| 'break-all'` | `'break-word'` | CSS word-break style for cells |
| `renderMarkdown` | `boolean` | `true` | Render cell text as Markdown |
| `prettifyJson` | `boolean` | `false` | Pretty-print JSON in output cells |
| `showPrompts` | `boolean` | `true` | Show the prompt used in each cell |
| `showPassFail` | `boolean` | `true` | Show pass/fail badge in cells |
| `inComparisonMode` | `boolean` | `false` | True when comparing multiple evals |
| `comparisonEvalIds` | `string[]` | `[]` | IDs of evals being compared |
| `columnStates` | `Record<string, ColumnState>` | `{}` | Per-eval column selection and visibility |

### Column State and Schema Hashing

Column visibility is managed at two levels:

1. **Per-eval** (`columnStates` keyed by `evalId`): Controls visibility of `description` and `Prompt N` columns.
2. **Per-schema** (`hiddenVarNamesBySchema` keyed by a schema hash): Controls visibility of variable columns. The hash is computed from sorted variable names via `hashVarSchema(head.vars)` [src/app/src/pages/eval/components/utils.ts:16-16]().

Sources: [src/app/src/pages/eval/components/store.ts:403-443](), [src/app/src/pages/eval/components/ResultsView.tsx:46-46]() (hashVarSchema import).

---

## State Shape Summary Diagram

**State fields mapped to store and file location**

Title: State Shape Summary Diagram
```mermaid
erDiagram
    useTableStore {
        string evalId
        string_or_null author
        EvaluateTable_or_null table
        UnifiedConfig_or_null config
        number_or_null version
        number filteredResultsCount
        number totalResultsCount
        number highlightedResultsCount
        number userRatedResultsCount
        PromptMetrics_array_or_null filteredMetrics
        EvaluateStats_or_null stats
        boolean isFetching
        boolean isStreaming
        boolean shouldHighlightSearchText
        FiltersState filters
        string_array metadataKeys
        string_map metadataValues
        EvalResultsFilterMode filterMode
    }

    useResultsViewSettingsStore {
        number maxTextLength
        string wordBreak
        boolean showInferenceDetails
        boolean renderMarkdown
        boolean prettifyJson
        boolean showPrompts
        boolean showPassFail
        boolean showPassReasons
        boolean inComparisonMode
        string_array comparisonEvalIds
        boolean stickyHeader
        Record_string_ColumnState columnStates
        Record_string_stringArray hiddenVarNamesBySchema
        number maxImageWidth
        number maxImageHeight
    }

    FiltersState {
        Record_id_ResultsFilter values
        number appliedCount
        FilterOptions options
        Record_string_string policyIdToNameMap
    }

    useTableStore ||--|| FiltersState : "contains"
```
Sources: [src/app/src/pages/eval/components/store.ts:268-443]()

---

## Component Interaction Patterns

### Reading State

Components call the store hook directly:

```typescript
// In ResultsTable.tsx
const { evalId, table, setTable, config, fetchEvalData, filters } = useTableStore();
const { inComparisonMode, renderMarkdown } = useResultsViewSettingsStore();
```
Sources: [src/app/src/pages/eval/components/ResultsTable.tsx:54-54]()

### Writing State: Ratings Flow

When a user rates an output, `ResultsTable.tsx` handles the event and updates the store. A result is considered user-rated if it has a component result with `assertion.type === 'human'` [src/app/src/pages/eval/components/store.ts:44-45]().

```mermaid
graph LR
    UserClick["User clicks thumbs-up"] --> handleRating["handleRating() in ResultsTable.tsx"]
    handleRating --> setTable["setTable(newTable) - Optimistic Update"]
    handleRating --> callApi["callApi('/api/results/:id/results/:resultId/rating')"]
```
Sources: [src/app/src/pages/eval/components/ResultsTable.tsx:18-18](), [src/app/src/pages/eval/components/store.ts:46-53]()

### Writing State: Filter Updates

Filters are managed through atomic actions. `Eval.tsx` subscribes to the `filters` slice via `subscribeWithSelector` and serializes the active filters to the URL's `?filter=` query parameter [src/app/src/pages/eval/components/Eval.tsx:38-48]().

**Filter Lifecycle Diagram**

Title: Filter Lifecycle Diagram
```mermaid
sequenceDiagram
    participant "URL (?filter=)" as URL
    participant "Eval.tsx" as Eval
    participant "useTableStore.filters" as Filters
    participant "FiltersForm.tsx" as Form
    participant "ResultsTable.tsx" as Table

    URL->>Eval: "page load: ?filter=[...]"
    Eval->>Filters: "addFilter() x N"
    Form->>Filters: "addFilter / updateFilter / removeFilter"
    Filters-->>Eval: "subscribe callback"
    Eval->>URL: "replaceSearchParams({ filter: JSON.stringify(values) })"
    Filters-->>Table: "filters change → fetchEvalData()"
```
Sources: [src/app/src/pages/eval/components/Eval.tsx:38-48](), [src/app/src/pages/eval/components/store.ts:586-608]()

---

## Metadata Key and Value Fetching

`useTableStore` manages lazy-loaded metadata keys and values used by the filter form.

| State field | Purpose |
|---|---|
| `metadataKeys` | List of all metadata key names across results |
| `metadataValues` | Per-key cache of distinct metadata values |

`fetchMetadataKeys` calls `GET /api/results/:id/metadata-keys` [src/app/src/pages/eval/components/store.ts:702-736](). `fetchMetadataValues` calls `GET /api/results/:id/metadata-values?key=...` [src/app/src/pages/eval/components/store.ts:738-782](). Both abort any prior in-flight request for the same resource using an `AbortController`.

Sources: [src/app/src/pages/eval/components/store.ts:382-400](), [src/app/src/pages/eval/components/store.ts:702-782]()
