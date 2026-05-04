This page documents the LangChain integration packages for OpenAI and Anthropic chat models. These integrations provide standardized interfaces to the OpenAI Chat Completions API, OpenAI Responses API, Azure OpenAI, and Anthropic Claude models through the `ChatOpenAI` and `ChatAnthropic` classes that implement `BaseChatModel` from langchain-core.

For information about other LLM provider integrations (Groq, Fireworks, Ollama), see [page 3.2](#3.2). For information about embeddings and vector stores, see [page 3.4](#3.4). For information about agent middleware and structured output patterns that work across providers, see [page 4](#4).

## Package Architecture

Both integrations are distributed as separate packages that depend on langchain-core for base abstractions and provider-specific SDKs for API communication.

```mermaid
graph TB
    subgraph "langchain-openai Package"
        OPENAI_CHAT["ChatOpenAI<br/>libs/partners/openai/langchain_openai/chat_models/base.py"]
        OPENAI_CLIENT["_get_default_httpx_client<br/>_get_default_async_httpx_client"]
        OPENAI_COMPAT["_compat.py<br/>v1 to v03 conversion"]
        OPENAI_PROFILES["_profiles.py<br/>model capabilities"]
    end
    
    subgraph "langchain-anthropic Package"
        ANTHROPIC_CHAT["ChatAnthropic<br/>libs/partners/anthropic/langchain_anthropic/chat_models.py"]
        ANTHROPIC_CLIENT["_get_default_httpx_client<br/>_get_default_async_httpx_client"]
        ANTHROPIC_COMPAT["_compat.py<br/>v1 to anthropic conversion"]
        ANTHROPIC_PROFILES["_profiles.py<br/>model capabilities"]
    end
    
    subgraph "External Dependencies"
        OPENAI_SDK["openai>=2.26.0"]
        ANTHROPIC_SDK["anthropic>=0.78.0"]
        LANGCHAIN_CORE["langchain-core>=1.2.18"]
        TIKTOKEN["tiktoken>=0.7.0"]
    end
    
    OPENAI_CHAT --> OPENAI_CLIENT
    OPENAI_CHAT --> OPENAI_COMPAT
    OPENAI_CHAT --> OPENAI_PROFILES
    OPENAI_CHAT --> OPENAI_SDK
    OPENAI_CHAT --> LANGCHAIN_CORE
    OPENAI_CHAT --> TIKTOKEN
    
    ANTHROPIC_CHAT --> ANTHROPIC_CLIENT
    ANTHROPIC_CHAT --> ANTHROPIC_COMPAT
    ANTHROPIC_CHAT --> ANTHROPIC_PROFILES
    ANTHROPIC_CHAT --> ANTHROPIC_SDK
    ANTHROPIC_CHAT --> LANGCHAIN_CORE
```

**Sources**: [libs/partners/openai/pyproject.toml:1-172](), [libs/partners/anthropic/pyproject.toml:1-147]()

| Package | Version | Key Dependencies | Purpose |
|---------|---------|-----------------|---------|
| `langchain-openai` | 1.1.11 | openai>=2.26.0, tiktoken>=0.7.0 | OpenAI and Azure OpenAI integration |
| `langchain-anthropic` | 1.3.5 | anthropic>=0.78.0 | Anthropic Claude models integration |

**Sources**: [libs/partners/openai/pyproject.toml:23-29](), [libs/partners/anthropic/pyproject.toml:23-29]()

## Chat Model Initialization

### ChatOpenAI Initialization

The `ChatOpenAI` class supports multiple initialization patterns with flexible API key resolution.

```mermaid
graph LR
    subgraph "API Key Sources"
        ENV_VAR["OPENAI_API_KEY<br/>environment variable"]
        PARAM_STR["api_key parameter<br/>string or SecretStr"]
        PARAM_SYNC["api_key parameter<br/>sync callable"]
        PARAM_ASYNC["api_key parameter<br/>async callable"]
    end
    
    subgraph "Key Resolution"
        RESOLVE["_resolve_sync_and_async_api_keys"]
    end
    
    subgraph "Client Creation"
        SYNC_CLIENT["OpenAI client<br/>sync operations"]
        ASYNC_CLIENT["AsyncOpenAI client<br/>async operations"]
    end
    
    ENV_VAR --> RESOLVE
    PARAM_STR --> RESOLVE
    PARAM_SYNC --> RESOLVE
    PARAM_ASYNC --> RESOLVE
    
    RESOLVE --> SYNC_CLIENT
    RESOLVE --> ASYNC_CLIENT
```

**Sources**: [libs/partners/openai/langchain_openai/chat_models/base.py:581-633](), [libs/partners/openai/langchain_openai/chat_models/base.py:1012-1059]()

**Initialization Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` / `model_name` | str | "gpt-3.5-turbo" | Model identifier |
| `api_key` / `openai_api_key` | SecretStr \| Callable | OPENAI_API_KEY env | API authentication |
| `base_url` / `openai_api_base` | str \| None | None | Custom API endpoint for Azure/proxies |
| `temperature` | float \| None | None | Sampling temperature (0-2) |
| `max_tokens` | int \| None | None | Maximum tokens to generate |
| `timeout` / `request_timeout` | float \| tuple | None | Request timeout configuration |
| `stream_usage` | bool \| None | True | Include usage in streaming chunks |
| `use_responses_api` | bool \| None | None | Use Responses API instead of Chat API |

**Sources**: [libs/partners/openai/langchain_openai/chat_models/base.py:572-905]()

### ChatAnthropic Initialization

The `ChatAnthropic` class follows a similar pattern with Anthropic-specific features.

```mermaid
graph LR
    subgraph "Configuration Sources"
        ANTHROPIC_ENV["ANTHROPIC_API_KEY<br/>environment variable"]
        API_PARAM["anthropic_api_key parameter"]
        PROXY_ENV["ANTHROPIC_PROXY<br/>environment variable"]
        PROXY_PARAM["anthropic_proxy parameter"]
    end
    
    subgraph "Client Setup"
        CLIENT_PARAMS["_client_params property"]
        SYNC_ANTHROPIC["Anthropic client"]
        ASYNC_ANTHROPIC["AsyncAnthropic client"]
    end
    
    subgraph "Model Defaults"
        PROFILE_LOOKUP["_get_default_model_profile"]
        MAX_TOKENS_CALC["max_tokens fallback logic"]
    end
    
    ANTHROPIC_ENV --> CLIENT_PARAMS
    API_PARAM --> CLIENT_PARAMS
    PROXY_ENV --> CLIENT_PARAMS
    PROXY_PARAM --> CLIENT_PARAMS
    
    CLIENT_PARAMS --> SYNC_ANTHROPIC
    CLIENT_PARAMS --> ASYNC_ANTHROPIC
    
    PROFILE_LOOKUP --> MAX_TOKENS_CALC
```

**Sources**: [libs/partners/anthropic/langchain_anthropic/chat_models.py:800-1016]()

**Initialization Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` / `model_name` | str | Required | Claude model identifier |
| `anthropic_api_key` / `api_key` | SecretStr | ANTHROPIC_API_KEY env | API authentication |
| `base_url` / `anthropic_api_url` | str | https://api.anthropic.com | API endpoint |
| `temperature` | float \| None | None | Sampling temperature |
| `max_tokens` | int \| None | Model-specific | Maximum output tokens (auto-set per model) |
| `timeout` / `default_request_timeout` | float \| None | None | Request timeout |
| `stream_usage` | bool | True | Include usage in streaming |

**Sources**: [libs/partners/anthropic/langchain_anthropic/chat_models.py:804-862]()

## Message Format Conversion

Both integrations convert between LangChain's standardized message types and provider-specific API formats.

### OpenAI Message Conversion

```mermaid
graph TB
    subgraph "LangChain Messages"
        LC_HUMAN["HumanMessage"]
        LC_AI["AIMessage<br/>tool_calls, invalid_tool_calls"]
        LC_SYSTEM["SystemMessage"]
        LC_TOOL["ToolMessage"]
        LC_FUNCTION["FunctionMessage"]
    end
    
    subgraph "Conversion Functions"
        TO_DICT["_convert_message_to_dict"]
        FROM_DICT["_convert_dict_to_message"]
        FORMAT_CONTENT["_format_message_content"]
    end
    
    subgraph "OpenAI API Format"
        OAI_USER["role: user<br/>content: str | list"]
        OAI_ASSISTANT["role: assistant<br/>tool_calls, function_call"]
        OAI_SYSTEM["role: system | developer"]
        OAI_TOOL["role: tool<br/>tool_call_id"]
        OAI_FUNCTION["role: function"]
    end
    
    LC_HUMAN --> TO_DICT
    LC_AI --> TO_DICT
    LC_SYSTEM --> TO_DICT
    LC_TOOL --> TO_DICT
    LC_FUNCTION --> TO_DICT
    
    TO_DICT --> FORMAT_CONTENT
    FORMAT_CONTENT --> OAI_USER
    FORMAT_CONTENT --> OAI_ASSISTANT
    FORMAT_CONTENT --> OAI_SYSTEM
    FORMAT_CONTENT --> OAI_TOOL
    FORMAT_CONTENT --> OAI_FUNCTION
    
    OAI_USER --> FROM_DICT
    OAI_ASSISTANT --> FROM_DICT
    OAI_SYSTEM --> FROM_DICT
    OAI_TOOL --> FROM_DICT
    OAI_FUNCTION --> FROM_DICT
    
    FROM_DICT --> LC_HUMAN
    FROM_DICT --> LC_AI
    FROM_DICT --> LC_SYSTEM
    FROM_DICT --> LC_TOOL
    FROM_DICT --> LC_FUNCTION
```

**Sources**: [libs/partners/openai/langchain_openai/chat_models/base.py:173-238](), [libs/partners/openai/langchain_openai/chat_models/base.py:321-401](), [libs/partners/openai/langchain_openai/chat_models/base.py:260-319]()

### Anthropic Message Conversion

Anthropic uses a different format that requires message merging and special handling of tool results.

```mermaid
graph TB
    subgraph "Input Processing"
        LC_MESSAGES["List[BaseMessage]"]
        MERGE["_merge_messages<br/>Combine consecutive user/tool messages"]
        FORMAT["_format_messages<br/>Convert to Anthropic format"]
    end
    
    subgraph "Anthropic Format Requirements"
        SYSTEM_EXTRACT["Extract SystemMessage → system param"]
        TOOL_RESULT["ToolMessage → tool_result content block"]
        CONTENT_BLOCKS["Content as list of blocks"]
    end
    
    subgraph "Special Handling"
        IMAGE_FORMAT["_format_image<br/>Base64 or URL image sources"]
        DATA_BLOCKS["_format_data_content_block<br/>image, file, text-plain"]
        BUILTIN_TOOLS["_is_builtin_tool<br/>computer_use, web_search, etc."]
    end
    
    LC_MESSAGES --> MERGE
    MERGE --> FORMAT
    FORMAT --> SYSTEM_EXTRACT
    FORMAT --> TOOL_RESULT
    FORMAT --> CONTENT_BLOCKS
    
    CONTENT_BLOCKS --> IMAGE_FORMAT
    CONTENT_BLOCKS --> DATA_BLOCKS
    FORMAT --> BUILTIN_TOOLS
```

**Sources**: [libs/partners/anthropic/langchain_anthropic/chat_models.py:240-302](), [libs/partners/anthropic/langchain_anthropic/chat_models.py:430-689](), [libs/partners/anthropic/langchain_anthropic/chat_models.py:193-238](), [libs/partners/anthropic/langchain_anthropic/chat_models.py:304-428]()

## Tool Calling

Both integrations support tool calling through standardized interfaces, with provider-specific handling.

### OpenAI Tool Calling

```mermaid
graph TB
    subgraph "Tool Binding"
        BIND_TOOLS["bind_tools method"]
        CONVERT_TOOL["convert_to_openai_tool"]
        WELL_KNOWN["WellKnownTools<br/>file_search, code_interpreter, etc."]
    end
    
    subgraph "Request Format"
        TOOLS_PARAM["tools parameter<br/>List of tool definitions"]
        PARALLEL_PARAM["parallel_tool_calls parameter"]
        TOOL_CHOICE["tool_choice parameter<br/>auto, required, none, specific"]
    end
    
    subgraph "Response Parsing"
        RAW_TOOL_CALLS["raw tool_calls from API"]
        PARSE_TOOL["parse_tool_call"]
        TOOL_CALL_OBJ["ToolCall objects"]
        INVALID_TOOL["InvalidToolCall objects<br/>for JSON decode errors"]
    end
    
    BIND_TOOLS --> CONVERT_TOOL
    BIND_TOOLS --> WELL_KNOWN
    CONVERT_TOOL --> TOOLS_PARAM
    WELL_KNOWN --> TOOLS_PARAM
    TOOLS_PARAM --> PARALLEL_PARAM
    TOOLS_PARAM --> TOOL_CHOICE
    
    RAW_TOOL_CALLS --> PARSE_TOOL
    PARSE_TOOL --> TOOL_CALL_OBJ
    PARSE_TOOL --> INVALID_TOOL
```

**Sources**: [libs/partners/openai/langchain_openai/chat_models/base.py:161-171](), [libs/partners/openai/langchain_openai/chat_models/base.py:194-203](), [libs/partners/openai/tests/unit_tests/chat_models/test_base.py:242-317]()

### Anthropic Tool Calling and Built-in Tools

Anthropic supports both custom tools and built-in server-side tools.

```mermaid
graph TB
    subgraph "Tool Definition"
        CUSTOM["Custom Tools<br/>AnthropicTool TypedDict"]
        BUILTIN["Built-in Tools<br/>computer_*, web_*, code_execution_*"]
        CONVERT_ANTHROPIC["convert_to_anthropic_tool"]
    end
    
    subgraph "Built-in Tool Detection"
        IS_BUILTIN["_is_builtin_tool<br/>Check type prefix"]
        BETA_HEADER["_TOOL_TYPE_TO_BETA<br/>Map to beta header"]
        PASS_THROUGH["Pass dict unchanged to API"]
    end
    
    subgraph "Tool Call Processing"
        TOOL_USE_BLOCK["tool_use content block"]
        SERVER_TOOL_USE["server_tool_use, mcp_tool_use"]
        EXTRACT_CALLS["extract_tool_calls<br/>Parse from content blocks"]
    end
    
    CUSTOM --> CONVERT_ANTHROPIC
    BUILTIN --> IS_BUILTIN
    IS_BUILTIN --> BETA_HEADER
    IS_BUILTIN --> PASS_THROUGH
    
    TOOL_USE_BLOCK --> EXTRACT_CALLS
    SERVER_TOOL_USE --> EXTRACT_CALLS
```

**Sources**: [libs/partners/anthropic/langchain_anthropic/chat_models.py:99-123](), [libs/partners/anthropic/langchain_anthropic/chat_models.py:137-173](), [libs/partners/anthropic/langchain_anthropic/chat_models.py:175-191]()

**Built-in Tool Support**:

| Tool Type Prefix | Beta Header | Purpose |
|-----------------|-------------|---------|
| `computer_*` | computer-use-2025-01-24 / 2025-11-24 | Computer control (screen, mouse, keyboard) |
| `web_search_*`, `web_fetch_*` | web-fetch-2025-09-10 | Web search and page fetching |
| `code_execution_*` | code-execution-2025-05-22 / 2025-08-25 | Execute Python code |
| `mcp_toolset` | mcp-client-2025-11-20 | Model Context Protocol toolsets |
| `memory_*` | context-management-2025-06-27 | Context memory management |
| `tool_search_*` | advanced-tool-use-2025-11-20 | Tool search and discovery |

**Sources**: [libs/partners/anthropic/langchain_anthropic/chat_models.py:137-163]()

## Streaming

Both integrations support streaming responses with token-by-token delivery and aggregated usage metadata.

### OpenAI Streaming Implementation

```mermaid
graph TB
    subgraph "Stream Invocation"
        STREAM_METHOD["_stream method"]
        CREATE_STREAM["client.chat.completions.create<br/>stream=True"]
        RESPONSE_STREAM["Stream[ChatCompletionChunk]"]
    end
    
    subgraph "Chunk Processing"
        DELTA["delta from chunk"]
        CONVERT_DELTA["_convert_delta_to_message_chunk"]
        AI_CHUNK["AIMessageChunk"]
    end
    
    subgraph "Usage Tracking"
        STREAM_USAGE_FLAG["stream_usage parameter"]
        USAGE_CHUNK["Final chunk with usage"]
        UPDATE_USAGE["_update_token_usage<br/>Aggregate nested dicts"]
        USAGE_METADATA["UsageMetadata object"]
    end
    
    STREAM_METHOD --> CREATE_STREAM
    CREATE_STREAM --> RESPONSE_STREAM
    RESPONSE_STREAM --> DELTA
    DELTA --> CONVERT_DELTA
    CONVERT_DELTA --> AI_CHUNK
    
    STREAM_USAGE_FLAG --> USAGE_CHUNK
    USAGE_CHUNK --> UPDATE_USAGE
    UPDATE_USAGE --> USAGE_METADATA
```

**Sources**: [libs/partners/openai/langchain_openai/chat_models/base.py:1519-1628](), [libs/partners/openai/langchain_openai/chat_models/base.py:403-457](), [libs/partners/openai/langchain_openai/chat_models/base.py:459-485]()

### Anthropic Streaming Implementation

```mermaid
graph TB
    subgraph "Stream Setup"
        ASTREAM["_stream / _astream method"]
        MESSAGES_CREATE["client.messages.create<br/>stream=True"]
        EVENT_STREAM["MessageStream"]
    end
    
    subgraph "Event Processing"
        MESSAGE_START["message_start event<br/>initial input_tokens"]
        CONTENT_DELTA["content_block_delta<br/>text or tool_use progress"]
        MESSAGE_DELTA["message_delta<br/>usage updates"]
        MESSAGE_STOP["message_stop event"]
    end
    
    subgraph "Chunk Aggregation"
        TEXT_CHUNK["AIMessageChunk with text"]
        TOOL_CHUNK["tool_call_chunk<br/>name, args, id, index"]
        CHUNK_COMBINE["AIMessageChunk + operator<br/>Aggregate tool_call_chunks"]
    end
    
    ASTREAM --> MESSAGES_CREATE
    MESSAGES_CREATE --> EVENT_STREAM
    
    EVENT_STREAM --> MESSAGE_START
    EVENT_STREAM --> CONTENT_DELTA
    EVENT_STREAM --> MESSAGE_DELTA
    EVENT_STREAM --> MESSAGE_STOP
    
    CONTENT_DELTA --> TEXT_CHUNK
    CONTENT_DELTA --> TOOL_CHUNK
    TEXT_CHUNK --> CHUNK_COMBINE
    TOOL_CHUNK --> CHUNK_COMBINE
```

**Sources**: [libs/partners/anthropic/langchain_anthropic/chat_models.py:1594-1732](), [libs/partners/anthropic/tests/integration_tests/test_chat_models.py:41-85]()

## Structured Output

Both integrations provide methods for extracting structured data with schema validation.

### OpenAI Structured Output Strategies

OpenAI supports three strategies for structured output, selected via the `method` parameter.

```mermaid
graph TB
    subgraph "with_structured_output Interface"
        WSO["with_structured_output<br/>schema, method, include_raw"]
        SCHEMA_TYPES["BaseModel | TypedDict | JsonSchema"]
    end
    
    subgraph "Strategy Selection"
        JSON_SCHEMA["method=json_schema<br/>Default for GPT-4o+"]
        FUNCTION_CALLING["method=function_calling"]
        JSON_MODE["method=json_mode"]
    end
    
    subgraph "json_schema Strategy"
        RESPONSE_FORMAT["response_format parameter<br/>type: json_schema"]
        STRICT_MODE["strict=True by default"]
        NATIVE_PARSING["Native API validation"]
    end
    
    subgraph "function_calling Strategy"
        TOOL_BIND["bind_tools with single function"]
        TOOL_PARSER["PydanticToolsParser<br/>JsonOutputKeyToolsParser"]
    end
    
    subgraph "json_mode Strategy"
        JSON_FORMAT["response_format: type=json_object"]
        JSON_PARSER["JsonOutputParser<br/>PydanticOutputParser"]
        MANUAL_VALIDATION["Client-side validation"]
    end
    
    WSO --> SCHEMA_TYPES
    WSO --> JSON_SCHEMA
    WSO --> FUNCTION_CALLING
    WSO --> JSON_MODE
    
    JSON_SCHEMA --> RESPONSE_FORMAT
    RESPONSE_FORMAT --> STRICT_MODE
    STRICT_MODE --> NATIVE_PARSING
    
    FUNCTION_CALLING --> TOOL_BIND
    TOOL_BIND --> TOOL_PARSER
    
    JSON_MODE --> JSON_FORMAT
    JSON_FORMAT --> JSON_PARSER
    JSON_PARSER --> MANUAL_VALIDATION
```

**Sources**: [libs/partners/openai/langchain_openai/chat_models/base.py:1950-2147](), [libs/partners/openai/langchain_openai/chat_models/base.py:2333-2401]()

### Anthropic Structured Output

Anthropic uses tool calling for structured output with automatic strategy selection.

```mermaid
graph TB
    subgraph "with_structured_output"
        ANTHROPIC_WSO["with_structured_output<br/>schema, include_raw"]
        PYDANTIC_SCHEMA["Pydantic BaseModel"]
        JSON_SCHEMA["JSON Schema dict"]
    end
    
    subgraph "Implementation"
        CONVERT_TOOL_SCHEMA["convert_to_json_schema<br/>convert_to_openai_tool"]
        BIND_SINGLE_TOOL["bind_tools with one tool"]
        TOOL_CHOICE_ANY["tool_choice='any'"]
    end
    
    subgraph "Parsing"
        PARSER_SELECT["Select parser based on schema"]
        PYDANTIC_PARSER["PydanticToolsParser"]
        JSON_PARSER["JsonOutputKeyToolsParser"]
    end
    
    ANTHROPIC_WSO --> PYDANTIC_SCHEMA
    ANTHROPIC_WSO --> JSON_SCHEMA
    
    PYDANTIC_SCHEMA --> CONVERT_TOOL_SCHEMA
    JSON_SCHEMA --> CONVERT_TOOL_SCHEMA
    CONVERT_TOOL_SCHEMA --> BIND_SINGLE_TOOL
    BIND_SINGLE_TOOL --> TOOL_CHOICE_ANY
    
    TOOL_CHOICE_ANY --> PARSER_SELECT
    PARSER_SELECT --> PYDANTIC_PARSER
    PARSER_SELECT --> JSON_PARSER
```

**Sources**: [libs/partners/anthropic/langchain_anthropic/chat_models.py:1913-2039]()

## Provider-Specific Features

### OpenAI: Responses API vs Chat Completions API

OpenAI provides two distinct APIs with different capabilities and response formats.

```mermaid
graph TB
    subgraph "API Selection Logic"
        PREFER_RESPONSES["_model_prefers_responses_api<br/>gpt-5-pro*, codex models"]
        USE_RESPONSES_PARAM["use_responses_api parameter"]
        INVOCATION_PARAMS["Check for responses-only params"]
    end
    
    subgraph "Chat Completions API"
        CHAT_CREATE["client.chat.completions.create"]
        CHAT_RESPONSE["ChatCompletion object"]
        CONVERT_V1_CHAT["_convert_from_v1_to_chat_completions"]
    end
    
    subgraph "Responses API"
        RESPONSES_CREATE["client.responses.create"]
        RESPONSE_OBJ["Response object"]
        CONVERT_V1_RESP["_convert_from_v1_to_responses"]
        REASONING_ITEMS["ResponseReasoningItem<br/>thinking, summary"]
        OUTPUT_ITEMS["ResponseOutputText, ResponseOutputRefusal"]
        TOOL_CALLS_RESP["ResponseFunctionToolCall<br/>ResponseFileSearchToolCall"]
    end
    
    PREFER_RESPONSES --> USE_RESPONSES_PARAM
    USE_RESPONSES_PARAM --> INVOCATION_PARAMS
    
    INVOCATION_PARAMS --> CHAT_CREATE
    INVOCATION_PARAMS --> RESPONSES_CREATE
    
    CHAT_CREATE --> CHAT_RESPONSE
    CHAT_RESPONSE --> CONVERT_V1_CHAT
    
    RESPONSES_CREATE --> RESPONSE_OBJ
    RESPONSE_OBJ --> CONVERT_V1_RESP
    CONVERT_V1_RESP --> REASONING_ITEMS
    CONVERT_V1_RESP --> OUTPUT_ITEMS
    CONVERT_V1_RESP --> TOOL_CALLS_RESP
```

**Sources**: [libs/partners/openai/langchain_openai/chat_models/base.py:536-547](), [libs/partners/openai/langchain_openai/chat_models/base.py:1395-1434](), [libs/partners/openai/langchain_openai/chat_models/_compat.py:1-500]()

**Responses API Features**:

| Feature | Parameter | Description |
|---------|-----------|-------------|
| Reasoning mode | `reasoning` | Configure effort level and summary style |
| Verbosity | `verbosity` | Control response detail (low/medium/high) |
| Truncation | `truncation` | Auto-drop middle messages to fit context |
| Previous response | `use_previous_response_id` | Reference prior response for continuity |
| Output version | `output_version` | Format control (v0, responses/v1, v1) |

**Sources**: [libs/partners/openai/langchain_openai/chat_models/base.py:718-924]()

### OpenAI: Azure OpenAI Support

Azure OpenAI uses the same `ChatOpenAI` class with special configuration.

```mermaid
graph TB
    subgraph "Azure Configuration"
        AZURE_ENDPOINT["azure_endpoint parameter<br/>https://*.openai.azure.com"]
        API_VERSION["api_version parameter<br/>Default from environment"]
        DEPLOYMENT["azure_deployment parameter<br/>Deployment name"]
    end
    
    subgraph "Authentication"
        AZURE_KEY["api_key parameter<br/>Azure API key"]
        AZURE_AD["azure_ad_token parameter<br/>Azure AD token"]
        DEFAULT_CRED["DefaultAzureCredential<br/>get_bearer_token_provider"]
    end
    
    subgraph "Client Creation"
        AZURE_CLIENT["AzureOpenAI client"]
        ASYNC_AZURE["AsyncAzureOpenAI client"]
    end
    
    AZURE_ENDPOINT --> AZURE_CLIENT
    API_VERSION --> AZURE_CLIENT
    DEPLOYMENT --> AZURE_CLIENT
    
    AZURE_KEY --> AZURE_CLIENT
    AZURE_AD --> AZURE_CLIENT
    DEFAULT_CRED --> AZURE_CLIENT
    
    AZURE_CLIENT --> ASYNC_AZURE
```

**Sources**: [libs/partners/openai/tests/integration_tests/chat_models/test_azure.py:1-339]()

### Anthropic: Extended Thinking Mode

Anthropic models support explicit thinking/reasoning through content blocks.

```mermaid
graph TB
    subgraph "Thinking Configuration"
        THINKING_PARAM["thinking parameter<br/>enabled, budget, type"]
        BUDGET_TOKENS["budget.tokens value"]
        THINKING_TYPE["type: enabled or disabled"]
    end
    
    subgraph "Response Content"
        THINKING_BLOCK["thinking content block<br/>type: thinking"]
        THINKING_TEXT["thinking: str<br/>model reasoning"]
        SIGNATURE["signature: str<br/>Anthropic signature"]
    end
    
    subgraph "Redacted Thinking"
        REDACTED_BLOCK["redacted_thinking content block"]
        ENCRYPTED_DATA["data: encrypted thinking"]
    end
    
    THINKING_PARAM --> BUDGET_TOKENS
    THINKING_PARAM --> THINKING_TYPE
    
    BUDGET_TOKENS --> THINKING_BLOCK
    THINKING_TYPE --> THINKING_BLOCK
    THINKING_BLOCK --> THINKING_TEXT
    THINKING_BLOCK --> SIGNATURE
    
    THINKING_BLOCK --> REDACTED_BLOCK
    REDACTED_BLOCK --> ENCRYPTED_DATA
```

**Sources**: [libs/partners/anthropic/langchain_anthropic/chat_models.py:853-887](), [libs/partners/anthropic/langchain_anthropic/chat_models.py:570-578]()

## Usage Metadata and Token Tracking

Both integrations track token usage and provide detailed metadata.

### OpenAI Usage Metadata

```mermaid
graph TB
    subgraph "Usage Data Sources"
        COMPLETION_TOKENS["completion_tokens"]
        PROMPT_TOKENS["prompt_tokens"]
        TOTAL_TOKENS["total_tokens"]
        COMPLETION_DETAILS["completion_tokens_details<br/>reasoning_tokens, audio_tokens"]
        PROMPT_DETAILS["prompt_tokens_details<br/>cached_tokens, audio_tokens"]
    end
    
    subgraph "UsageMetadata Construction"
        CREATE_USAGE["_create_usage_metadata"]
        INPUT_TOKENS["input_tokens = prompt_tokens"]
        OUTPUT_TOKENS["output_tokens = completion_tokens"]
        INPUT_DETAILS["input_token_details<br/>cache_read, audio"]
        OUTPUT_DETAILS["output_token_details<br/>reasoning, audio"]
    end
    
    PROMPT_TOKENS --> CREATE_USAGE
    COMPLETION_TOKENS --> CREATE_USAGE
    TOTAL_TOKENS --> CREATE_USAGE
    COMPLETION_DETAILS --> CREATE_USAGE
    PROMPT_DETAILS --> CREATE_USAGE
    
    CREATE_USAGE --> INPUT_TOKENS
    CREATE_USAGE --> OUTPUT_TOKENS
    CREATE_USAGE --> INPUT_DETAILS
    CREATE_USAGE --> OUTPUT_DETAILS
```

**Sources**: [libs/partners/openai/langchain_openai/chat_models/base.py:1211-1261]()

### Anthropic Usage Metadata

```mermaid
graph TB
    subgraph "Anthropic Usage Object"
        ANTHRO_INPUT["input_tokens"]
        ANTHRO_OUTPUT["output_tokens"]
        CACHE_CREATE["cache_creation_input_tokens"]
        CACHE_READ["cache_read_input_tokens"]
    end
    
    subgraph "Metadata Conversion"
        CREATE_ANTHRO_USAGE["_create_usage_metadata"]
        TOTAL_CALC["total = input + cache_create + cache_read + output"]
        INPUT_DETAILS_ANTHRO["input_token_details<br/>cache_creation, cache_read"]
    end
    
    ANTHRO_INPUT --> CREATE_ANTHRO_USAGE
    ANTHRO_OUTPUT --> CREATE_ANTHRO_USAGE
    CACHE_CREATE --> CREATE_ANTHRO_USAGE
    CACHE_READ --> CREATE_ANTHRO_USAGE
    
    CREATE_ANTHRO_USAGE --> TOTAL_CALC
    CREATE_ANTHRO_USAGE --> INPUT_DETAILS_ANTHRO
```

**Sources**: [libs/partners/anthropic/langchain_anthropic/chat_models.py:2242-2281]()

## Error Handling

Both integrations provide specialized error handling for context overflow and API-specific errors.

### Error Type Hierarchy

```mermaid
graph TB
    subgraph "OpenAI Errors"
        OAI_BAD_REQUEST["openai.BadRequestError"]
        OAI_API_ERROR["openai.APIError"]
        OAI_CONTEXT_BAD["OpenAIContextOverflowError<br/>Extends BadRequestError + ContextOverflowError"]
        OAI_CONTEXT_API["OpenAIAPIContextOverflowError<br/>Extends APIError + ContextOverflowError"]
    end
    
    subgraph "Anthropic Errors"
        ANTHRO_BAD_REQUEST["anthropic.BadRequestError"]
        ANTHRO_CONTEXT["AnthropicContextOverflowError<br/>Extends BadRequestError + ContextOverflowError"]
    end
    
    subgraph "Error Handlers"
        HANDLE_OAI_BAD["_handle_openai_bad_request<br/>Check message patterns"]
        HANDLE_OAI_API["_handle_openai_api_error<br/>Check error message"]
        HANDLE_ANTHRO["_handle_anthropic_bad_request<br/>Check prompt too long"]
    end
    
    OAI_BAD_REQUEST --> HANDLE_OAI_BAD
    HANDLE_OAI_BAD --> OAI_CONTEXT_BAD
    
    OAI_API_ERROR --> HANDLE_OAI_API
    HANDLE_OAI_API --> OAI_CONTEXT_API
    
    ANTHRO_BAD_REQUEST --> HANDLE_ANTHRO
    HANDLE_ANTHRO --> ANTHRO_CONTEXT
```

**Sources**: [libs/partners/openai/langchain_openai/chat_models/base.py:487-534](), [libs/partners/anthropic/langchain_anthropic/chat_models.py:750-765]()

**Common Error Patterns**:

| Provider | Error Check | Exception Type | Trigger |
|----------|-------------|----------------|---------|
| OpenAI | "context_length_exceeded" | OpenAIContextOverflowError | Input + output exceeds model limit |
| OpenAI | "Input tokens exceed" | OpenAIContextOverflowError | Input alone exceeds limit |
| OpenAI | "exceeds the context window" | OpenAIAPIContextOverflowError | Server-side context error |
| OpenAI | "json_schema not supported" | Warning + original error | Using structured output on incompatible model |
| Anthropic | "prompt is too long" | AnthropicContextOverflowError | Input exceeds context window |
| Anthropic | "at least one message required" | Warning + original error | Only system messages provided |

**Sources**: [libs/partners/openai/langchain_openai/chat_models/base.py:495-525](), [libs/partners/anthropic/langchain_anthropic/chat_models.py:754-765]()

## Client Caching and Connection Management

Both integrations implement client caching to reuse HTTP connections across instances with identical configurations.

### Client Cache Key Strategy

```mermaid
graph TB
    subgraph "ChatOpenAI Cache Keys"
        OAI_BASE_URL["base_url"]
        OAI_TIMEOUT["timeout"]
        OAI_MAX_RETRIES["max_retries"]
        OAI_ORG["organization"]
        OAI_PROXY["openai_proxy"]
        OAI_HTTP_CLIENT["http_client / http_async_client"]
    end
    
    subgraph "Cache Comparison"
        SAME_CONFIG["Identical parameters"]
        SHARED_CLIENT["Reuse cached client"]
        DIFF_CONFIG["Different parameters"]
        NEW_CLIENT["Create new client"]
    end
    
    subgraph "ChatAnthropic Cache Keys"
        ANTHRO_BASE["anthropic_api_url"]
        ANTHRO_TIMEOUT["default_request_timeout"]
        ANTHRO_MAX_RETRIES["max_retries"]
        ANTHRO_PROXY["anthropic_proxy"]
    end
    
    OAI_BASE_URL --> SAME_CONFIG
    OAI_TIMEOUT --> SAME_CONFIG
    OAI_MAX_RETRIES --> SAME_CONFIG
    OAI_ORG --> SAME_CONFIG
    OAI_PROXY --> SAME_CONFIG
    OAI_HTTP_CLIENT --> DIFF_CONFIG
    
    SAME_CONFIG --> SHARED_CLIENT
    DIFF_CONFIG --> NEW_CLIENT
    
    ANTHRO_BASE --> SAME_CONFIG
    ANTHRO_TIMEOUT --> SAME_CONFIG
    ANTHRO_MAX_RETRIES --> SAME_CONFIG
    ANTHRO_PROXY --> SAME_CONFIG
```

**Sources**: [libs/partners/openai/tests/unit_tests/chat_models/test_base.py:106-128](), [libs/partners/anthropic/tests/unit_tests/test_chat_models.py:72-86]()

## Testing Infrastructure

Both packages use standard integration tests from langchain-tests to ensure API compatibility.

### Test Organization

| Test Type | Location Pattern | Purpose |
|-----------|-----------------|---------|
| Unit Tests | `tests/unit_tests/` | Fast tests without API calls |
| Integration Tests | `tests/integration_tests/` | Real API validation |
| Standard Tests | Inherit from `ChatModelIntegrationTests` | Cross-provider consistency |

**Sources**: [libs/partners/openai/pyproject.toml:142-149](), [libs/partners/anthropic/pyproject.toml:122-129]()

### Key Test Scenarios

```mermaid
graph LR
    subgraph "OpenAI Tests"
        OAI_INVOKE["test_invoke<br/>Basic completion"]
        OAI_STREAM["test_stream<br/>Streaming chunks"]
        OAI_TOOLS["test_tool_use<br/>Function calling"]
        OAI_AZURE["test_azure<br/>Azure-specific"]
        OAI_RESPONSES["test_responses_api<br/>Responses API"]
    end
    
    subgraph "Anthropic Tests"
        ANTHRO_INVOKE["test_invoke<br/>Basic completion"]
        ANTHRO_STREAM["test_stream<br/>Streaming chunks"]
        ANTHRO_TOOLS["test_tool_use<br/>Custom tools"]
        ANTHRO_BUILTIN["test_builtin_tools<br/>Computer use, web search"]
        ANTHRO_THINKING["test_thinking<br/>Extended thinking"]
    end
    
    subgraph "Standard Tests"
        STANDARD_INVOKE["Standard invoke tests"]
        STANDARD_STREAM["Standard stream tests"]
        STANDARD_TOOLS["Standard tool tests"]
    end
    
    OAI_INVOKE --> STANDARD_INVOKE
    ANTHRO_INVOKE --> STANDARD_INVOKE
    OAI_STREAM --> STANDARD_STREAM
    ANTHRO_STREAM --> STANDARD_STREAM
    OAI_TOOLS --> STANDARD_TOOLS
    ANTHRO_TOOLS --> STANDARD_TOOLS
```

**Sources**: [libs/partners/openai/tests/integration_tests/chat_models/test_base.py:1-600](), [libs/partners/anthropic/tests/integration_tests/test_chat_models.py:1-1000]()

# Groq, Fireworks, and OpenRouter Integrations




This document covers the LangChain partner integrations for Groq, Fireworks, and OpenRouter LLM providers. These integrations provide unified access to multiple AI models through standardized interfaces that extend `BaseChatModel` from `langchain-core`.

For information about the OpenAI and Anthropic integrations, see [OpenAI and Anthropic Integrations](#3.1). For broader context on integration patterns, see [Integration Patterns and Best Practices](#3.5).

## Overview

Each integration package implements a chat model class that provides access to provider-specific models and features:

- **`langchain-groq`**: Fast inference API with reasoning modes and flexible service tiers
- **`langchain-fireworks`**: Model hosting platform with structured output support
- **`langchain-openrouter`**: Unified API routing across 100+ models from multiple providers

All three integrations share common patterns for initialization, tool calling, and structured output while exposing provider-specific capabilities.

**Sources:** [libs/partners/groq/langchain_groq/chat_models.py:91-351](), [libs/partners/fireworks/langchain_fireworks/chat_models.py:281-296](), [libs/partners/openrouter/langchain_openrouter/chat_models.py:85-137]()

## Class Hierarchy and Core Architecture

```mermaid
graph TB
    subgraph "langchain-core"
        BaseChatModel["BaseChatModel"]
        Runnable["Runnable"]
        BaseChatModel --> Runnable
    end
    
    subgraph "Partner Integrations"
        ChatGroq["ChatGroq<br/>libs/partners/groq/"]
        ChatFireworks["ChatFireworks<br/>libs/partners/fireworks/"]
        ChatOpenRouter["ChatOpenRouter<br/>libs/partners/openrouter/"]
    end
    
    subgraph "SDK Clients"
        GroqClient["groq.Groq"]
        FireworksClient["fireworks.Fireworks"]
        OpenRouterClient["openrouter.OpenRouter"]
    end
    
    BaseChatModel --> ChatGroq
    BaseChatModel --> ChatFireworks
    BaseChatModel --> ChatOpenRouter
    
    ChatGroq --> GroqClient
    ChatFireworks --> FireworksClient
    ChatOpenRouter --> OpenRouterClient
    
    ChatGroq --> |"invoke/stream/batch"| BaseChatModel
    ChatFireworks --> |"invoke/stream/batch"| BaseChatModel
    ChatOpenRouter --> |"invoke/stream/batch"| BaseChatModel
```

**Sources:** [libs/partners/groq/langchain_groq/chat_models.py:91](), [libs/partners/fireworks/langchain_fireworks/chat_models.py:281](), [libs/partners/openrouter/langchain_openrouter/chat_models.py:85]()

## Common Implementation Patterns

### Initialization and Client Setup

All three integrations follow a consistent pattern for client initialization using Pydantic validators:

| Pattern | Implementation |
|---------|---------------|
| API Key Management | SecretStr with environment variable defaults |
| Client Creation | `@model_validator(mode="after")` for SDK client initialization |
| Configuration | Field aliases for both snake_case and provider-specific names |
| Profile Loading | Default model profiles loaded after validation |

The initialization flow:

```mermaid
sequenceDiagram
    participant User
    participant ChatModel["ChatGroq/ChatFireworks/ChatOpenRouter"]
    participant Validator["model_validator"]
    participant SDK["SDK Client"]
    
    User->>ChatModel: __init__(model, api_key, ...)
    ChatModel->>Validator: build_extra (mode="before")
    Note over Validator: Move extra kwargs to model_kwargs
    Validator->>ChatModel: validate_environment (mode="after")
    ChatModel->>SDK: Initialize client with params
    SDK-->>ChatModel: client instance
    ChatModel->>ChatModel: _set_model_profile
    ChatModel-->>User: ChatModel instance
```

**ChatGroq** client initialization example:

[libs/partners/groq/langchain_groq/chat_models.py:498-544]()

**ChatFireworks** client initialization example:

[libs/partners/fireworks/langchain_fireworks/chat_models.py:399-425]()

**ChatOpenRouter** client initialization example:

[libs/partners/openrouter/langchain_openrouter/chat_models.py:304-351]()

**Sources:** [libs/partners/groq/langchain_groq/chat_models.py:468-544](), [libs/partners/fireworks/langchain_fireworks/chat_models.py:391-432](), [libs/partners/openrouter/langchain_openrouter/chat_models.py:274-358]()

### Message Conversion and Processing

All integrations implement bidirectional message conversion between LangChain message types and provider API formats:

```mermaid
graph LR
    subgraph "LangChain Message Types"
        HumanMessage["HumanMessage"]
        AIMessage["AIMessage"]
        SystemMessage["SystemMessage"]
        ToolMessage["ToolMessage"]
    end
    
    subgraph "Conversion Layer"
        ToDict["_convert_message_to_dict"]
        FromDict["_convert_dict_to_message"]
    end
    
    subgraph "Provider API Format"
        UserDict["{role: 'user', content: ...}"]
        AssistantDict["{role: 'assistant', content: ..., tool_calls: ...}"]
        SystemDict["{role: 'system', content: ...}"]
        ToolDict["{role: 'tool', content: ..., tool_call_id: ...}"]
    end
    
    HumanMessage --> ToDict --> UserDict
    AIMessage --> ToDict --> AssistantDict
    SystemMessage --> ToDict --> SystemDict
    ToolMessage --> ToDict --> ToolDict
    
    UserDict --> FromDict --> HumanMessage
    AssistantDict --> FromDict --> AIMessage
    SystemDict --> FromDict --> SystemMessage
    ToolDict --> FromDict --> ToolMessage
```

**Groq** message conversion handles reasoning content and tool calls:

[libs/partners/groq/langchain_groq/chat_models.py:1389-1494]()

**Fireworks** message conversion includes reasoning_content extraction:

[libs/partners/fireworks/langchain_fireworks/chat_models.py:99-216]()

**OpenRouter** message conversion supports multimodal content:

[libs/partners/openrouter/langchain_openrouter/chat_models.py:847-1005]()

**Sources:** [libs/partners/groq/langchain_groq/chat_models.py:1389-1494](), [libs/partners/fireworks/langchain_fireworks/chat_models.py:99-216](), [libs/partners/openrouter/langchain_openrouter/chat_models.py:847-1005]()

### Tool Calling Implementation

All three integrations support tool calling via the `bind_tools` method, which converts tools to OpenAI-compatible format:

```mermaid
graph TB
    Tools["Tools<br/>(Pydantic, dict, Callable)"]
    
    BindTools["bind_tools(tools, tool_choice)"]
    
    ConvertTools["convert_to_openai_tool"]
    
    FormattedTools["Formatted Tools<br/>{type: 'function', function: {...}}"]
    
    ToolChoice["Tool Choice<br/>('auto', 'none', 'required', dict)"]
    
    BoundModel["Runnable with tools bound"]
    
    Tools --> BindTools
    BindTools --> ConvertTools
    ConvertTools --> FormattedTools
    ToolChoice --> BindTools
    FormattedTools --> BoundModel
    
    Note1["Groq: Converts 'any' to 'required'"]
    Note2["Fireworks: Supports strict parameter"]
    Note3["OpenRouter: Standard OpenAI format"]
    
    BindTools --> Note1
    BindTools --> Note2
    BindTools --> Note3
```

**ChatGroq** `bind_tools` implementation:

[libs/partners/groq/langchain_groq/chat_models.py:859-906]()

**ChatFireworks** `bind_tools` with strict support:

[libs/partners/fireworks/langchain_fireworks/chat_models.py:666-713]()

**ChatOpenRouter** `bind_tools` implementation:

[libs/partners/openrouter/langchain_openrouter/chat_models.py:1221-1272]()

**Sources:** [libs/partners/groq/langchain_groq/chat_models.py:859-906](), [libs/partners/fireworks/langchain_fireworks/chat_models.py:666-713](), [libs/partners/openrouter/langchain_openrouter/chat_models.py:1221-1272]()

## Groq-Specific Features

### Reasoning Format and Effort

**ChatGroq** supports advanced reasoning capabilities through two parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `reasoning_format` | `"parsed"`, `"raw"`, `"hidden"` | Controls how reasoning output is returned |
| `reasoning_effort` | `str` | Controls reasoning token budget (`"low"`, `"medium"`, `"high"`, `"none"`) |

**Reasoning Format Behavior:**

- **`"parsed"`**: Reasoning appears in `additional_kwargs.reasoning_content`
- **`"raw"`**: Reasoning embedded in content within `<think>` tags
- **`"hidden"`**: Reasoning performed but not returned in response

[libs/partners/groq/langchain_groq/chat_models.py:371-394]()

Example test demonstrating reasoning output:

[libs/partners/groq/tests/integration_tests/test_chat_models.py:227-244]()

### Service Tier Configuration

Groq provides three service tier options for request routing:

```mermaid
graph LR
    ServiceTier["service_tier parameter"]
    
    OnDemand["on_demand<br/>(default)<br/>Standard processing"]
    Flex["flex<br/>Best-effort with<br/>rapid timeouts"]
    Auto["auto<br/>on_demand → flex<br/>fallback"]
    
    ServiceTier --> OnDemand
    ServiceTier --> Flex
    ServiceTier --> Auto
    
    OnDemand --> Response["Response with<br/>service_tier in metadata"]
    Flex --> Response
    Auto --> Response
```

Service tier can be set at class level or per-request:

[libs/partners/groq/langchain_groq/chat_models.py:433-446]()

Service tier test examples:

[libs/partners/groq/tests/integration_tests/test_chat_models.py:555-644]()

### Structured Output with JSON Schema

**ChatGroq** supports native structured output via the `json_schema` method for specific models:

[libs/partners/groq/langchain_groq/chat_models.py:78-83]()

The `with_structured_output` method supports three approaches:

| Method | Description | Models |
|--------|-------------|--------|
| `function_calling` | Uses tool calling API | All tool-capable models |
| `json_mode` | JSON object mode | All models |
| `json_schema` | Native structured output with strict mode | `openai/gpt-oss-*`, select models |

Strict mode implementation:

[libs/partners/groq/langchain_groq/chat_models.py:908-1087]()

Test coverage for json_schema:

[libs/partners/groq/tests/integration_tests/test_standard.py:53-72]()

**Sources:** [libs/partners/groq/langchain_groq/chat_models.py:371-446](), [libs/partners/groq/tests/integration_tests/test_chat_models.py:227-360]()

## Fireworks-Specific Features

### Reasoning Content Handling

**ChatFireworks** extracts reasoning content from responses into `additional_kwargs`:

[libs/partners/fireworks/langchain_fireworks/chat_models.py:116-118]()

The reasoning content is preserved during message conversion:

[libs/partners/fireworks/langchain_fireworks/chat_models.py:173-177]()

### Structured Output Methods

**ChatFireworks** supports structured output with three methods:

```mermaid
graph TB
    WithStructuredOutput["with_structured_output(schema, method)"]
    
    FunctionCalling["method='function_calling'<br/>Uses tool calling API"]
    JsonSchema["method='json_schema'<br/>Native structured output"]
    JsonMode["method='json_mode'<br/>JSON object mode"]
    
    WithStructuredOutput --> FunctionCalling
    WithStructuredOutput --> JsonSchema
    WithStructuredOutput --> JsonMode
    
    FunctionCalling --> Parser1["PydanticToolsParser or<br/>JsonOutputKeyToolsParser"]
    JsonSchema --> ResponseFormat["response_format:<br/>{type: 'json_schema', json_schema: {...}}"]
    JsonMode --> ResponseFormat2["response_format:<br/>{type: 'json_object'}"]
    
    Parser1 --> Output["Structured Output"]
    ResponseFormat --> Output
    ResponseFormat2 --> Output
```

Implementation with strict support:

[libs/partners/fireworks/langchain_fireworks/chat_models.py:715-890]()

Test demonstrating json_schema method:

[libs/partners/fireworks/tests/integration_tests/test_chat_models.py:158-173]()

**Sources:** [libs/partners/fireworks/langchain_fireworks/chat_models.py:99-890](), [libs/partners/fireworks/tests/integration_tests/test_chat_models.py:158-173]()

## OpenRouter-Specific Features

### Provider Routing and Preferences

**ChatOpenRouter** enables routing requests across multiple underlying providers with configurable preferences:

| Parameter | Type | Description |
|-----------|------|-------------|
| `openrouter_provider` | `dict` | Provider preferences, e.g., `{"order": ["Anthropic", "OpenAI"]}` |
| `route` | `str` | Route preference, e.g., `"fallback"` |
| `reasoning` | `dict` | Reasoning configuration with `effort` and `summary` |

[libs/partners/openrouter/langchain_openrouter/chat_models.py:236-267]()

Provider routing flow:

```mermaid
graph TB
    Request["User Request"]
    
    OpenRouter["OpenRouter API"]
    
    ProviderPref["openrouter_provider<br/>{order: ['Anthropic', 'OpenAI']}"]
    
    Route["route parameter<br/>(e.g., 'fallback')"]
    
    Provider1["Anthropic API"]
    Provider2["OpenAI API"]
    Provider3["Other Providers"]
    
    Request --> OpenRouter
    ProviderPref --> OpenRouter
    Route --> OpenRouter
    
    OpenRouter --> |"Try first"| Provider1
    OpenRouter --> |"Try second"| Provider2
    OpenRouter --> |"Fallback"| Provider3
    
    Provider1 --> Response["Response"]
    Provider2 --> Response
    Provider3 --> Response
```

### Reasoning Configuration

OpenRouter supports reasoning token control via the `reasoning` parameter:

[libs/partners/openrouter/langchain_openrouter/chat_models.py:236-258]()

Configuration structure:
- `effort`: Controls reasoning token budget (`"xhigh"`, `"high"`, `"medium"`, `"low"`, `"minimal"`, `"none"`)
- `summary`: Controls summary verbosity (`"auto"`, `"concise"`, `"detailed"`)

### Attribution Headers

OpenRouter requires attribution for API usage tracking:

[libs/partners/openrouter/langchain_openrouter/chat_models.py:154-175]()

Default headers:
- `HTTP-Referer`: `https://docs.langchain.com/oss` (from `app_url`)
- `X-Title`: `langchain` (from `app_title`)

Test verifying attribution:

[libs/partners/openrouter/tests/unit_tests/test_chat_models.py:314-338]()

### Retry Configuration

**ChatOpenRouter** uses exponential backoff with configurable retry limits:

[libs/partners/openrouter/langchain_openrouter/chat_models.py:180-186]()

The SDK client configuration with retries:

[libs/partners/openrouter/langchain_openrouter/chat_models.py:339-349]()

**Sources:** [libs/partners/openrouter/langchain_openrouter/chat_models.py:154-349](), [libs/partners/openrouter/tests/unit_tests/test_chat_models.py:314-338]()

## Streaming and Usage Metadata

All three integrations implement streaming with proper usage metadata tracking:

```mermaid
sequenceDiagram
    participant User
    participant ChatModel["ChatGroq/Fireworks/OpenRouter"]
    participant Client["SDK Client"]
    participant Callback["CallbackManager"]
    
    User->>ChatModel: stream(messages)
    ChatModel->>Client: create(messages, stream=True)
    
    loop For each chunk
        Client-->>ChatModel: chunk
        ChatModel->>ChatModel: _convert_chunk_to_message_chunk
        ChatModel->>Callback: on_llm_new_token
        ChatModel-->>User: ChatGenerationChunk
    end
    
    Note over ChatModel: Final chunk includes usage_metadata
    Client-->>ChatModel: final chunk with usage
    ChatModel->>ChatModel: aggregate usage_metadata
    ChatModel-->>User: Final chunk with full metadata
```

### Usage Metadata Structure

All integrations track token usage with detailed breakdowns:

| Field | Description |
|-------|-------------|
| `input_tokens` | Prompt tokens consumed |
| `output_tokens` | Completion tokens generated |
| `total_tokens` | Sum of input and output tokens |
| `input_token_details` | Optional: `cache_read` for cached tokens |
| `output_token_details` | Optional: `reasoning` for reasoning tokens |

**ChatGroq** usage metadata creation:

[libs/partners/groq/langchain_groq/chat_models.py:1327-1388]()

Test verifying usage metadata in streaming:

[libs/partners/groq/tests/integration_tests/test_chat_models.py:100-135]()

**ChatFireworks** streaming with usage:

[libs/partners/fireworks/langchain_fireworks/chat_models.py:488-521]()

**ChatOpenRouter** streaming configuration:

[libs/partners/openrouter/langchain_openrouter/chat_models.py:226-231]()

**Sources:** [libs/partners/groq/langchain_groq/chat_models.py:655-761](), [libs/partners/fireworks/langchain_fireworks/chat_models.py:488-521](), [libs/partners/openrouter/langchain_openrouter/chat_models.py:453-560]()

## Standard Testing Integration

All three integrations implement the `ChatModelIntegrationTests` interface from `langchain-tests`:

```mermaid
graph TB
    subgraph "langchain-tests"
        ChatModelIntegrationTests["ChatModelIntegrationTests<br/>(base test class)"]
    end
    
    subgraph "Groq Tests"
        TestGroq["TestGroq<br/>test_standard.py"]
        TestGroqUnit["TestGroqStandard<br/>test_unit_standard.py"]
    end
    
    subgraph "Fireworks Tests"
        TestFireworks["TestFireworksStandard<br/>test_standard.py"]
        TestFireworksUnit["TestFireworksStandard<br/>test_unit_standard.py"]
    end
    
    subgraph "OpenRouter Tests"
        TestOpenRouterIntegration["Integration tests in<br/>test_chat_models.py"]
        TestOpenRouterUnit["TestChatOpenRouterUnit<br/>test_standard.py"]
    end
    
    ChatModelIntegrationTests --> TestGroq
    ChatModelIntegrationTests --> TestFireworks
    
    TestGroq --> |"chat_model_class = ChatGroq"| Props1["Properties:<br/>chat_model_params<br/>supports_json_mode"]
    TestFireworks --> |"chat_model_class = ChatFireworks"| Props2["Properties:<br/>chat_model_params<br/>supports_json_mode"]
```

### Test Configuration

**ChatGroq** test configuration:

[libs/partners/groq/tests/integration_tests/test_standard.py:17-51]()

Key test properties:
- Uses `llama-3.3-70b-versatile` model
- Rate limiter at 0.2 requests/second
- Marks flaky tool calling tests with `xfail` and retry

**ChatFireworks** test configuration:

[libs/partners/fireworks/tests/integration_tests/test_standard.py:13-33]()

Uses `kimi-k2-instruct-0905` model with temperature 0.

### Structured Output Testing

Special test classes verify `json_schema` method support:

[libs/partners/groq/tests/integration_tests/test_standard.py:53-72]()

This parametrized test validates structured output with:
- Pydantic models
- TypedDict classes
- JSON schema dictionaries

**Sources:** [libs/partners/groq/tests/integration_tests/test_standard.py:1-72](), [libs/partners/fireworks/tests/integration_tests/test_standard.py:1-34]()

## Error Handling and Validation

All integrations implement consistent error handling patterns:

### Parameter Validation

Common validation checks across all integrations:

| Check | Implementation |
|-------|---------------|
| API key presence | Raises `ValueError` if missing |
| Streaming with n>1 | Raises `ValueError` (n must be 1 when streaming) |
| Extra kwargs | Warns and moves to `model_kwargs` |
| Field conflicts | Raises `ValueError` if field specified twice |

**ChatGroq** parameter validation:

[libs/partners/groq/langchain_groq/chat_models.py:468-496]()

**ChatFireworks** parameter validation:

[libs/partners/fireworks/langchain_fireworks/chat_models.py:391-396]()

**ChatOpenRouter** parameter validation:

[libs/partners/openrouter/langchain_openrouter/chat_models.py:274-302]()

### Tool Call Error Handling

Invalid tool calls are captured and returned in `invalid_tool_calls`:

```mermaid
graph TB
    ToolCalls["API Response with tool_calls"]
    
    ParseTools["Parse each tool_call"]
    
    Valid["Valid: parse_tool_call succeeds"]
    Invalid["Invalid: parse_tool_call raises exception"]
    
    ToolCall["ToolCall object"]
    InvalidToolCall["InvalidToolCall object<br/>with error message"]
    
    AIMessage["AIMessage<br/>tool_calls=[...]<br/>invalid_tool_calls=[...]"]
    
    ToolCalls --> ParseTools
    ParseTools --> Valid
    ParseTools --> Invalid
    
    Valid --> ToolCall
    Invalid --> InvalidToolCall
    
    ToolCall --> AIMessage
    InvalidToolCall --> AIMessage
```

Invalid tool call handling in Groq:

[libs/partners/groq/langchain_groq/chat_models.py:1430-1449]()

Test coverage for malformed tool calls:

[libs/partners/groq/tests/unit_tests/test_chat_models.py:100-143]()

**Sources:** [libs/partners/groq/langchain_groq/chat_models.py:468-496](), [libs/partners/groq/tests/unit_tests/test_chat_models.py:100-143]()

## Model Profile Registry

All integrations support model profiles that provide default configuration:

```mermaid
graph LR
    ModelProfileRegistry["_MODEL_PROFILES<br/>(ModelProfileRegistry)"]
    
    GetProfile["_get_default_model_profile(model_name)"]
    
    ModelName["model_name: str"]
    
    Profile["ModelProfile<br/>{...default config...}"]
    
    ChatModel["ChatGroq/Fireworks/OpenRouter"]
    
    ModelProfileRegistry --> GetProfile
    ModelName --> GetProfile
    GetProfile --> Profile
    
    Profile --> ChatModel
    ChatModel --> |"After validation"| SetProfile["self.profile = profile"]
```

**ChatGroq** profile loading:

[libs/partners/groq/langchain_groq/chat_models.py:74-88](), [libs/partners/groq/langchain_groq/chat_models.py:546-551]()

**ChatFireworks** profile loading:

[libs/partners/fireworks/langchain_fireworks/chat_models.py:91-96](), [libs/partners/fireworks/langchain_fireworks/chat_models.py:427-432]()

**ChatOpenRouter** profile loading:

[libs/partners/openrouter/langchain_openrouter/chat_models.py:74-82](), [libs/partners/openrouter/langchain_openrouter/chat_models.py:353-358]()

Profile test in Fireworks:

[libs/partners/fireworks/tests/unit_tests/test_standard.py:40-46]()

**Sources:** [libs/partners/groq/langchain_groq/chat_models.py:74-88](), [libs/partners/fireworks/tests/unit_tests/test_standard.py:40-46]()

## Serialization and LangSmith Integration

All integrations support serialization for persistence and LangSmith tracing:

### Serialization Support

Each integration implements:

| Method | Purpose |
|--------|---------|
| `lc_secrets` | Maps secret fields to environment variables |
| `is_lc_serializable()` | Returns `True` to enable serialization |
| `_get_ls_params()` | Provides LangSmith tracing parameters |

**ChatGroq** serialization:

[libs/partners/groq/langchain_groq/chat_models.py:557-564]()

Test verifying serialization:

[libs/partners/groq/tests/unit_tests/test_chat_models.py:314-341]()

### LangSmith Parameters

Standard LangSmith params returned by all integrations:

```python
LangSmithParams(
    ls_provider="groq" | "fireworks" | "openrouter",
    ls_model_name=model_name,
    ls_model_type="chat",
    ls_temperature=temperature,
    ls_max_tokens=max_tokens,  # optional
    ls_stop=stop_sequences,     # optional
)
```

**ChatGroq** LangSmith params:

[libs/partners/groq/langchain_groq/chat_models.py:574-589]()

**ChatFireworks** LangSmith params:

[libs/partners/fireworks/langchain_fireworks/chat_models.py:450-465]()

**ChatOpenRouter** LangSmith params:

[libs/partners/openrouter/langchain_openrouter/chat_models.py:396-413]()

**Sources:** [libs/partners/groq/langchain_groq/chat_models.py:557-589](), [libs/partners/groq/tests/unit_tests/test_chat_models.py:314-341]()

# Ollama Integration




The Ollama integration provides LangChain components for running language models locally via [Ollama](https://ollama.com/). This package (`langchain-ollama`) enables chat models, text completion LLMs, and embeddings using models served by a local Ollama instance. It implements standardized LangChain interfaces for local model inference with features including tool calling, streaming, multimodal inputs, and reasoning mode for supported models.

For cloud-based provider integrations using remote APIs, see [OpenAI and Anthropic Integrations](#3.1), [Groq, Fireworks, and OpenRouter Integrations](#3.2), or [Embeddings and Vector Stores](#3.4).

## Package Structure

The `langchain-ollama` integration is organized as a standalone partner package with the following structure:

| Component | Purpose | File Path |
|-----------|---------|-----------|
| `ChatOllama` | Chat model implementation | [libs/partners/ollama/langchain_ollama/chat_models.py]() |
| `OllamaLLM` | Text completion LLM implementation | [libs/partners/ollama/langchain_ollama/llms.py]() |
| `OllamaEmbeddings` | Embeddings implementation | [libs/partners/ollama/langchain_ollama/embeddings.py]() |
| Utilities | Model validation, URL parsing | [libs/partners/ollama/langchain_ollama/_utils.py]() |
| Compatibility | v1 message format conversion | [libs/partners/ollama/langchain_ollama/_compat.py]() |

The package depends on `ollama>=0.6.0` for the Ollama Python client and `langchain-core>=1.0.0` for base abstractions [libs/partners/ollama/pyproject.toml:25-28]().

**Sources:** [libs/partners/ollama/pyproject.toml](), [libs/partners/ollama/langchain_ollama/__init__.py]()

## Component Architecture

```mermaid
graph TB
    subgraph "LangChain Core Abstractions"
        BaseChatModel["BaseChatModel"]
        BaseLLM["BaseLLM"]
        Embeddings["Embeddings"]
    end
    
    subgraph "Ollama Integration (langchain_ollama)"
        ChatOllama["ChatOllama"]
        OllamaLLM["OllamaLLM"]
        OllamaEmbeddings["OllamaEmbeddings"]
        
        Utils["_utils.py:<br/>validate_model()<br/>parse_url_with_auth()<br/>merge_auth_headers()"]
        Compat["_compat.py:<br/>_convert_from_v1_to_ollama()"]
    end
    
    subgraph "Ollama Client Library"
        Client["ollama.Client"]
        AsyncClient["ollama.AsyncClient"]
        Message["ollama.Message"]
    end
    
    subgraph "Ollama Server"
        OllamaAPI["Ollama API<br/>http://localhost:11434"]
        Models["Local Models<br/>llama3.1, deepseek-r1, etc."]
    end
    
    ChatOllama -.extends.-> BaseChatModel
    OllamaLLM -.extends.-> BaseLLM
    OllamaEmbeddings -.implements.-> Embeddings
    
    ChatOllama --> Utils
    OllamaLLM --> Utils
    OllamaEmbeddings --> Utils
    ChatOllama --> Compat
    
    ChatOllama --> Client
    ChatOllama --> AsyncClient
    OllamaLLM --> Client
    OllamaLLM --> AsyncClient
    OllamaEmbeddings --> Client
    OllamaEmbeddings --> AsyncClient
    
    Client --> OllamaAPI
    AsyncClient --> OllamaAPI
    OllamaAPI --> Models
```

**ChatOllama Architecture**

The `ChatOllama` class provides chat model functionality with message-based conversation support, tool calling, and multimodal inputs. Key methods include:

- `_convert_messages_to_ollama_messages()`: Transforms LangChain `BaseMessage` objects to `ollama.Message` format [libs/partners/ollama/langchain_ollama/chat_models.py:812-929]()
- `_chat_params()`: Assembles request parameters including model options, tools, and reasoning configuration [libs/partners/ollama/langchain_ollama/chat_models.py:720-788]()
- `_create_chat_stream()` / `_acreate_chat_stream()`: Handle streaming responses from Ollama [libs/partners/ollama/langchain_ollama/chat_models.py:951-969]()
- `_iterate_over_stream()`: Processes stream chunks into `ChatGenerationChunk` objects [libs/partners/ollama/langchain_ollama/chat_models.py:998-1116]()

**Sources:** [libs/partners/ollama/langchain_ollama/chat_models.py:260-1710](), [libs/partners/ollama/langchain_ollama/llms.py:25-542](), [libs/partners/ollama/langchain_ollama/embeddings.py:19-333]()

## Client Initialization and Authentication

All Ollama integration classes use a common initialization pattern with synchronous and asynchronous Ollama clients:

```mermaid
graph LR
    subgraph "Model Initialization"
        Init["ChatOllama()<br/>OllamaLLM()<br/>OllamaEmbeddings()"]
    end
    
    subgraph "Validation (_set_clients)"
        ParseURL["parse_url_with_auth()"]
        MergeHeaders["merge_auth_headers()"]
        CreateClients["Client()<br/>AsyncClient()"]
        ValidateModel["validate_model()"]
    end
    
    subgraph "Clients"
        SyncClient["self._client<br/>(Client)"]
        AsyncClient["self._async_client<br/>(AsyncClient)"]
    end
    
    Init --> ParseURL
    ParseURL --> MergeHeaders
    MergeHeaders --> CreateClients
    CreateClients --> SyncClient
    CreateClients --> AsyncClient
    CreateClients --> ValidateModel
```

The `_set_clients()` model validator method [libs/partners/ollama/langchain_ollama/chat_models.py:790-810]() performs the following steps:

1. **URL Parsing**: Extracts authentication credentials from `base_url` using `parse_url_with_auth()` [libs/partners/ollama/langchain_ollama/_utils.py:50-98]()
2. **Header Merging**: Combines authentication headers with `client_kwargs` via `merge_auth_headers()` [libs/partners/ollama/langchain_ollama/_utils.py:101-114]()
3. **Client Creation**: Instantiates `ollama.Client` and `ollama.AsyncClient` with merged configuration
4. **Model Validation**: If `validate_model_on_init=True`, calls `validate_model()` to verify the model exists locally [libs/partners/ollama/langchain_ollama/_utils.py:12-47]()

**Authentication Support**

The integration supports HTTP Basic Authentication via `userinfo` in the `base_url` parameter:

```python
ChatOllama(
    model="llama3.1",
    base_url="http://username:password@localhost:11434"
)
```

The `parse_url_with_auth()` function extracts credentials, creates a Base64-encoded Authorization header, and returns a cleaned URL without credentials [libs/partners/ollama/langchain_ollama/_utils.py:50-98]().

**Sources:** [libs/partners/ollama/langchain_ollama/chat_models.py:790-810](), [libs/partners/ollama/langchain_ollama/llms.py:322-342](), [libs/partners/ollama/langchain_ollama/embeddings.py:275-295](), [libs/partners/ollama/langchain_ollama/_utils.py:1-115]()

## Message Conversion and Content Handling

The `ChatOllama` class handles conversion between LangChain's message format and Ollama's expected format through `_convert_messages_to_ollama_messages()`:

```mermaid
graph TB
    subgraph "Input: LangChain Messages"
        HumanMsg["HumanMessage"]
        AIMsg["AIMessage<br/>+ tool_calls<br/>+ content_blocks"]
        SystemMsg["SystemMessage"]
        ToolMsg["ToolMessage"]
        ChatMsg["ChatMessage"]
    end
    
    subgraph "Conversion Process"
        V1Check["Check output_version=='v1'"]
        ConvertV1["_convert_from_v1_to_ollama()"]
        ExtractRole["Extract role"]
        ExtractContent["Extract content<br/>(text, images)"]
        ExtractTools["Extract tool_calls"]
        BuildMsg["Build ollama.Message dict"]
    end
    
    subgraph "Output: Ollama Format"
        OllamaMsg["ollama.Message:<br/>{role, content, images,<br/>tool_calls, tool_call_id}"]
    end
    
    AIMsg --> V1Check
    V1Check -->|v1| ConvertV1
    V1Check -->|not v1| ExtractRole
    ConvertV1 --> ExtractRole
    
    HumanMsg --> ExtractRole
    SystemMsg --> ExtractRole
    ToolMsg --> ExtractRole
    ChatMsg --> ExtractRole
    
    ExtractRole --> ExtractContent
    ExtractContent --> ExtractTools
    ExtractTools --> BuildMsg
    BuildMsg --> OllamaMsg
```

**Message Type Mapping**

| LangChain Message | Ollama Role | Special Handling |
|-------------------|-------------|------------------|
| `HumanMessage` | `"user"` | Content extraction (text, images) |
| `AIMessage` | `"assistant"` | Tool calls conversion via `_lc_tool_call_to_openai_tool_call()` |
| `SystemMessage` | `"system"` | Direct conversion |
| `ToolMessage` | `"tool"` | Includes `tool_call_id` |
| `ChatMessage` | Custom role | Uses `message.role` directly |

**Content Block Processing**

The conversion handles multiple content types within messages [libs/partners/ollama/langchain_ollama/chat_models.py:868-916]():

- **Text content**: String content or `{"type": "text", "text": "..."}` blocks
- **Images**: Base64-encoded images from `image_url` blocks or data content blocks via `_get_image_from_data_content_block()` [libs/partners/ollama/langchain_ollama/chat_models.py:240-253]()
- **Tool use**: Skipped during conversion (tool calls handled separately)

**v1 Content Block Support**

When `output_version="v1"` is set in `AIMessage.response_metadata`, the conversion unpacks v1 content blocks back to Ollama format using `_convert_from_v1_to_ollama()` [libs/partners/ollama/langchain_ollama/chat_models.py:824-838]().

**Sources:** [libs/partners/ollama/langchain_ollama/chat_models.py:812-929](), [libs/partners/ollama/langchain_ollama/chat_models.py:240-253](), [libs/partners/ollama/langchain_ollama/chat_models.py:228-237](), [libs/partners/ollama/langchain_ollama/_compat.py]()

## Tool Calling

The integration supports tool calling through LangChain's standardized tool interface with special handling for Ollama's tool call format:

```mermaid
graph TB
    subgraph "Tool Binding"
        BindTools["llm.bind_tools([tools])"]
        ConvertTools["convert_to_openai_tool()"]
        ChatParams["_chat_params(tools=...)"]
    end
    
    subgraph "Ollama Response"
        RawResponse["Ollama response:<br/>{message: {tool_calls: [...]}}"]
        ParseToolCalls["_get_tool_calls_from_response()"]
        ParseArgs["_parse_arguments_from_tool_call()"]
        ParseJSON["_parse_json_string()"]
    end
    
    subgraph "Output"
        ToolCall["ToolCall:<br/>{id, name, args}"]
        AIMessage["AIMessage.tool_calls"]
    end
    
    BindTools --> ConvertTools
    ConvertTools --> ChatParams
    ChatParams --> RawResponse
    
    RawResponse --> ParseToolCalls
    ParseToolCalls --> ParseArgs
    ParseArgs --> ParseJSON
    ParseJSON --> ToolCall
    ToolCall --> AIMessage
```

**Tool Call Parsing**

The `_get_tool_calls_from_response()` function extracts tool calls from Ollama responses and converts them to LangChain's `ToolCall` format [libs/partners/ollama/langchain_ollama/chat_models.py:207-225]():

1. Extracts raw tool calls from `response["message"]["tool_calls"]`
2. Generates UUID for each tool call if not provided
3. Parses arguments via `_parse_arguments_from_tool_call()`

**Argument Parsing with Fallback**

The `_parse_arguments_from_tool_call()` function handles inconsistent argument structures from Ollama models [libs/partners/ollama/langchain_ollama/chat_models.py:170-204]():

- Filters out metadata fields like `functionName` that echo the function name
- Attempts JSON parsing with `json.loads()`
- Falls back to `ast.literal_eval()` for Python-style dictionaries with single quotes
- Recursively parses nested string-encoded JSON values

This provides robustness against Ollama's inconsistent tool call argument structure (see https://github.com/ollama/ollama/issues/6155).

**Tool Streaming**

During streaming, tool calls are accumulated via `_accumulate_tool_call_chunks()` [libs/partners/ollama/langchain_ollama/chat_models.py:1118-1182](). Tool call chunks are emitted as `ToolCallChunk` objects in `AIMessageChunk.tool_call_chunks`, then consolidated into complete tool calls in the final chunk.

**Sources:** [libs/partners/ollama/langchain_ollama/chat_models.py:207-225](), [libs/partners/ollama/langchain_ollama/chat_models.py:170-204](), [libs/partners/ollama/langchain_ollama/chat_models.py:118-168](), [libs/partners/ollama/langchain_ollama/chat_models.py:1118-1182](), [libs/partners/ollama/langchain_ollama/chat_models.py:228-237]()

## Reasoning Mode

The Ollama integration supports reasoning/thinking mode for compatible models (e.g., DeepSeek R1) through the `reasoning` parameter:

```mermaid
graph TB
    subgraph "Configuration"
        ReasoningParam["reasoning parameter:<br/>True/False/None/str"]
        InitParam["ChatOllama(reasoning=...)"]
        InvokeParam["invoke(..., reasoning=...)"]
    end
    
    subgraph "Request Building"
        ChatParams["_chat_params()"]
        ThinkParam["params['think'] = reasoning"]
    end
    
    subgraph "Response Processing"
        OllamaResp["Ollama response:<br/>{thinking: '...', response: '...'}"]
        IterateStream["_iterate_over_stream()"]
        ExtractThinking["Extract 'thinking' field"]
        StoreReasoning["additional_kwargs['reasoning_content']"]
        ContentBlocks["content_blocks[{type: 'reasoning'}]"]
    end
    
    ReasoningParam --> InitParam
    ReasoningParam --> InvokeParam
    InitParam --> ChatParams
    InvokeParam --> ChatParams
    ChatParams --> ThinkParam
    
    ThinkParam --> OllamaResp
    OllamaResp --> IterateStream
    IterateStream --> ExtractThinking
    ExtractThinking --> StoreReasoning
    ExtractThinking --> ContentBlocks
```

**Reasoning Parameter Values**

| Value | Behavior |
|-------|----------|
| `True` | Enables reasoning mode; captures reasoning in `additional_kwargs['reasoning_content']` |
| `False` | Disables reasoning mode; no reasoning content in response |
| `None` (default) | Model uses default behavior; thinking tags may appear in content |
| `str` (e.g., `'low'`, `'medium'`, `'high'`) | Custom intensity level (model-specific, e.g., gpt-oss) |

**Response Handling**

When `reasoning=True`, the integration processes Ollama's `thinking` field [libs/partners/ollama/langchain_ollama/chat_models.py:1050-1064]():

1. Extracts thinking content from stream chunks
2. Stores in `AIMessage.additional_kwargs['reasoning_content']`
3. Creates content blocks with `type='reasoning'` for v1 output format
4. Ensures `` tags are not present in either main content or reasoning content

**Implementation Details**

For `ChatOllama`, reasoning handling occurs in `_iterate_over_stream()` [libs/partners/ollama/langchain_ollama/chat_models.py:1032-1072](). For `OllamaLLM`, it's in `_stream()` and `_stream_with_aggregation()` [libs/partners/ollama/langchain_ollama/llms.py:419-459]().

The `reasoning` parameter can be set at initialization or per-invocation [libs/partners/ollama/langchain_ollama/chat_models.py:527-544]().

**Sources:** [libs/partners/ollama/langchain_ollama/chat_models.py:527-544](), [libs/partners/ollama/langchain_ollama/chat_models.py:1032-1072](), [libs/partners/ollama/langchain_ollama/llms.py:116-128](), [libs/partners/ollama/langchain_ollama/llms.py:419-459](), [libs/partners/ollama/langchain_ollama/chat_models.py:720-788]()

## Streaming Architecture

```mermaid
graph TB
    subgraph "Stream Request"
        InvokeStream["invoke() / stream()"]
        CreateStream["_create_chat_stream()"]
        ClientChat["self._client.chat(stream=True)"]
    end
    
    subgraph "Stream Processing"
        IterateStream["_iterate_over_stream()"]
        ChunkLoop["for chunk in stream"]
        
        CheckDone["done_reason == 'load'<br/>and empty content?"]
        SkipChunk["Log warning, skip chunk"]
        ProcessChunk["Process chunk"]
        
        ExtractContent["Extract 'content'"]
        ExtractTools["Extract 'tool_calls'"]
        ExtractReasoning["Extract 'thinking'"]
        ExtractMetadata["Extract token counts"]
        
        BuildChunk["ChatGenerationChunk"]
        AccumTools["_accumulate_tool_call_chunks()"]
    end
    
    subgraph "Output"
        AIMessageChunk["AIMessageChunk:<br/>content, tool_calls,<br/>tool_call_chunks"]
        UsageMetadata["UsageMetadata:<br/>input_tokens, output_tokens"]
    end
    
    InvokeStream --> CreateStream
    CreateStream --> ClientChat
    ClientChat --> IterateStream
    
    IterateStream --> ChunkLoop
    ChunkLoop --> CheckDone
    CheckDone -->|Yes| SkipChunk
    CheckDone -->|No| ProcessChunk
    
    ProcessChunk --> ExtractContent
    ProcessChunk --> ExtractTools
    ProcessChunk --> ExtractReasoning
    ProcessChunk --> ExtractMetadata
    
    ExtractContent --> BuildChunk
    ExtractTools --> AccumTools
    AccumTools --> BuildChunk
    ExtractReasoning --> BuildChunk
    ExtractMetadata --> BuildChunk
    
    BuildChunk --> AIMessageChunk
    ExtractMetadata --> UsageMetadata
```

**Stream Chunk Processing**

The `_iterate_over_stream()` method processes Ollama stream chunks [libs/partners/ollama/langchain_ollama/chat_models.py:998-1116]():

1. **Load Response Filtering**: Skips chunks with `done_reason='load'` and empty/whitespace content, logging a warning [libs/partners/ollama/langchain_ollama/chat_models.py:1013-1026]()
2. **Content Extraction**: Extracts text from `chunk["message"]["content"]`
3. **Tool Call Accumulation**: Builds complete tool calls from incremental chunks via `_accumulate_tool_call_chunks()` [libs/partners/ollama/langchain_ollama/chat_models.py:1118-1182]()
4. **Reasoning Extraction**: Separates thinking content when `reasoning=True`
5. **Usage Metadata**: Constructs `UsageMetadata` from token counts using `_get_usage_metadata_from_generation_info()` [libs/partners/ollama/langchain_ollama/chat_models.py:101-115]()

**Async Streaming**

Async streaming follows the same pattern using `_acreate_chat_stream()` and async iterators [libs/partners/ollama/langchain_ollama/chat_models.py:931-949]().

**Sources:** [libs/partners/ollama/langchain_ollama/chat_models.py:998-1116](), [libs/partners/ollama/langchain_ollama/chat_models.py:951-969](), [libs/partners/ollama/langchain_ollama/chat_models.py:1118-1182](), [libs/partners/ollama/langchain_ollama/chat_models.py:101-115]()

## OllamaLLM Text Completion

The `OllamaLLM` class provides text completion functionality using Ollama's generate endpoint:

```mermaid
graph LR
    subgraph "LLM Methods"
        Generate["_generate(prompts)"]
        Stream["_stream(prompt)"]
    end
    
    subgraph "Request Building"
        GenerateParams["_generate_params()"]
        Options["Options:<br/>temperature, top_p,<br/>num_predict, etc."]
    end
    
    subgraph "Ollama Client"
        ClientGenerate["self._client.generate()"]
        CreateStream["_create_generate_stream()"]
    end
    
    subgraph "Response Processing"
        StreamAgg["_stream_with_aggregation()"]
        ExtractThinking["Extract 'thinking'"]
        ExtractResponse["Extract 'response'"]
    end
    
    subgraph "Output"
        GenerationChunk["GenerationChunk:<br/>text, generation_info"]
        LLMResult["LLMResult"]
    end
    
    Generate --> GenerateParams
    Stream --> GenerateParams
    GenerateParams --> Options
    
    GenerateParams --> CreateStream
    CreateStream --> ClientGenerate
    
    ClientGenerate --> StreamAgg
    StreamAgg --> ExtractThinking
    StreamAgg --> ExtractResponse
    
    ExtractResponse --> GenerationChunk
    GenerationChunk --> LLMResult
```

**Key Differences from ChatOllama**

- Uses `ollama.Client.generate()` instead of `chat()` [libs/partners/ollama/llms.py:361-375]()
- Accepts string prompts rather than message lists
- Returns `GenerationChunk` and `LLMResult` instead of message objects
- Supports the same model parameters and reasoning mode as `ChatOllama`

**Sources:** [libs/partners/ollama/langchain_ollama/llms.py:25-542](), [libs/partners/ollama/langchain_ollama/llms.py:264-306](), [libs/partners/ollama/langchain_ollama/llms.py:419-459]()

## OllamaEmbeddings

The `OllamaEmbeddings` class provides document and query embedding through Ollama's embed endpoint:

| Method | Purpose | Returns |
|--------|---------|---------|
| `embed_documents(texts)` | Embed multiple texts synchronously | `list[list[float]]` |
| `embed_query(text)` | Embed single query synchronously | `list[float]` |
| `aembed_documents(texts)` | Embed multiple texts asynchronously | `list[list[float]]` |
| `aembed_query(text)` | Embed single query asynchronously | `list[float]` |

**Implementation**

The embedding methods call `ollama.Client.embed()` or `ollama.AsyncClient.embed()` with model parameters [libs/partners/ollama/langchain_ollama/embeddings.py:297-332]():

```python
self._client.embed(
    self.model,
    texts,
    options=self._default_params,  # temperature, num_ctx, etc.
    keep_alive=self.keep_alive
)
```

The `_default_params` property constructs options from model parameters like `temperature`, `num_ctx`, `num_gpu`, etc. [libs/partners/ollama/langchain_ollama/embeddings.py:256-273]().

**Sources:** [libs/partners/ollama/langchain_ollama/embeddings.py:19-333](), [libs/partners/ollama/langchain_ollama/embeddings.py:297-332](), [libs/partners/ollama/langchain_ollama/embeddings.py:256-273]()

## Model Parameters and Configuration

All Ollama integration classes share common model parameters that map to Ollama's model options:

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `model` | `str` | Model name (required) | - |
| `temperature` | `float` | Sampling temperature (0.0-1.0) | `0.8` |
| `num_predict` | `int` | Max tokens to predict | `128` |
| `num_ctx` | `int` | Context window size | `2048` |
| `top_p` | `float` | Nucleus sampling parameter | `0.9` |
| `top_k` | `int` | Top-k sampling parameter | `40` |
| `repeat_penalty` | `float` | Repetition penalty | `1.1` |
| `seed` | `int` | Random seed for reproducibility | - |
| `mirostat` | `int` | Mirostat sampling mode (0/1/2) | `0` |
| `stop` | `list[str]` | Stop sequences | - |

**Chat-Specific Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `reasoning` | `bool \| str \| None` | Reasoning mode control |
| `format` | `Literal["", "json"] \| JsonSchemaValue` | Output format constraint |
| `validate_model_on_init` | `bool` | Validate model exists on initialization |

**Client Configuration**

| Parameter | Type | Description |
|-----------|------|-------------|
| `base_url` | `str` | Ollama server URL (supports `userinfo` auth) |
| `keep_alive` | `int \| str` | How long to keep model loaded |
| `client_kwargs` | `dict` | Additional httpx client kwargs |
| `sync_client_kwargs` | `dict` | Sync client-specific kwargs |
| `async_client_kwargs` | `dict` | Async client-specific kwargs |

**Parameter Handling**

Parameters set to `None` are excluded from the options dict sent to Ollama [libs/partners/ollama/langchain_ollama/chat_models.py:744-767](), preventing unnecessary API parameters. Explicitly provided `options` dicts override this filtering [libs/partners/ollama/langchain_ollama/chat_models.py:744]().

**Sources:** [libs/partners/ollama/langchain_ollama/chat_models.py:524-713](), [libs/partners/ollama/langchain_ollama/llms.py:113-256](), [libs/partners/ollama/langchain_ollama/embeddings.py:124-251](), [libs/partners/ollama/langchain_ollama/chat_models.py:720-788]()

## Testing Infrastructure

The Ollama integration includes comprehensive unit and integration tests following LangChain's standard testing framework:

**Standard Test Implementation**

| Test Class | Base Class | Purpose |
|------------|------------|---------|
| `TestChatOllama` (unit) | `ChatModelUnitTests` | Standard unit tests |
| `TestChatOllama` (integration) | `ChatModelIntegrationTests` | Standard integration tests |

The integration tests extend `ChatModelIntegrationTests` from `langchain-tests` [libs/partners/ollama/tests/integration_tests/chat_models/test_chat_models_standard.py:12-63]() and configure test properties:

```python
@property
def supports_json_mode(self) -> bool:
    return True

@property
def has_tool_choice(self) -> bool:
    return False  # Not yet supported by Ollama

@property
def supports_image_inputs(self) -> bool:
    return True
```

**Integration Test Execution**

Tests are run with configurable model names via environment variables [libs/partners/ollama/Makefile:14-16]():
- `OLLAMA_TEST_MODEL` (default: `llama3.1`)
- `OLLAMA_REASONING_TEST_MODEL` (default: `deepseek-r1:1.5b`)

**Known Issues**

The tests mark expected failures for Ollama's inconsistent tool calling behavior [libs/partners/ollama/tests/integration_tests/chat_models/test_chat_models_standard.py:35-62]():
- Tool responses sometimes return strings instead of expected types (e.g., `'3'` instead of `3`)
- Tool arguments may contain unexpected metadata keys like `'conversations'`

**Sources:** [libs/partners/ollama/tests/unit_tests/test_chat_models.py:41-49](), [libs/partners/ollama/tests/integration_tests/chat_models/test_chat_models_standard.py:12-63](), [libs/partners/ollama/Makefile:14-29](), [libs/partners/ollama/tests/integration_tests/chat_models/test_chat_models_reasoning.py]()

# Vector Stores




This page documents the `VectorStore` base interface defined in `langchain-core` and the `Chroma` integration from `langchain-chroma`. It covers document storage and retrieval operations, the four search methods, embedding function wiring, collection management, and the standard test suite used to validate any vector store implementation.

For information on the broader `Embeddings` interface that feeds into vector stores, see page [3.1](#3.1) (OpenAI embeddings) and [3.3](#3.3) (Ollama embeddings). For the `BaseRetriever` interface that wraps vector stores, see page [2.1](#2.1). For information on how `VectorStoreIntegrationTests` fits into the test framework, see page [5.1](#5.1).

---

## VectorStore Interface

The abstract `VectorStore` class lives in `langchain-core` and is imported from `langchain_core.vectorstores`. All concrete implementations, including `Chroma`, subclass it.

**Diagram: VectorStore class hierarchy and key methods**

```mermaid
classDiagram
    class VectorStore {
        +add_documents(documents, **kwargs) list~str~
        +aadd_documents(documents, **kwargs) list~str~
        +add_texts(texts, metadatas, ids) list~str~
        +delete(ids) bool
        +adelete(ids) bool
        +similarity_search(query, k) list~Document~
        +asimilarity_search(query, k) list~Document~
        +similarity_search_with_score(query, k) list~tuple~
        +similarity_search_by_vector(embedding, k) list~Document~
        +max_marginal_relevance_search(query, k, fetch_k, lambda_mult) list~Document~
        +get_by_ids(ids) list~Document~
        +as_retriever(**kwargs) VectorStoreRetriever
        +from_texts(texts, embedding, **kwargs)$ VectorStore
        +from_documents(documents, embedding, **kwargs)$ VectorStore
    }

    class Chroma {
        -_client chromadb.ClientAPI
        -_chroma_collection chromadb.Collection
        -_embedding_function Embeddings
        -_collection_name str
        -_collection_metadata dict
        -override_relevance_score_fn Callable
        +add_texts(texts, metadatas, ids) list~str~
        +add_images(uris, metadatas, ids) list~str~
        +get_by_ids(ids) list~Document~
        +delete(ids) bool
        +update_documents(ids, documents) void
        +similarity_search(query, k, filter) list~Document~
        +similarity_search_with_score(query, k, filter) list~tuple~
        +similarity_search_with_vectors(query, k) list~tuple~
        +max_marginal_relevance_search(query, k, fetch_k, lambda_mult) list~Document~
        +delete_collection() void
        +reset_collection() void
        +get(ids, where, limit, offset) dict
        +fork(new_name) Chroma
        +from_texts(texts, embedding, **kwargs)$ Chroma
        +from_documents(documents, embedding, **kwargs)$ Chroma
    }

    VectorStore <|-- Chroma
```

Sources: [libs/partners/chroma/langchain_chroma/vectorstores.py:1-30](), [libs/standard-tests/langchain_tests/integration_tests/vectorstores.py:1-20]()

---

## The `Chroma` Class

Located in `libs/partners/chroma/langchain_chroma/vectorstores.py`, the `Chroma` class is the primary integration point between the LangChain ecosystem and the [ChromaDB](https://www.trychroma.com/) vector database. The `langchain-chroma` package depends on both `langchain-core>=1.1.3` and `chromadb>=1.3.5`.

### Constructor Parameters

The `__init__` method accepts three groups of parameters:

**Indexing parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `collection_name` | `str` | `"langchain"` | Name of the ChromaDB collection |
| `embedding_function` | `Embeddings \| None` | `None` | LangChain `Embeddings` object used to embed texts |
| `collection_metadata` | `dict \| None` | `None` | Metadata passed to the collection on creation |
| `collection_configuration` | `CreateCollectionConfiguration \| None` | `None` | Index configuration (e.g. HNSW settings) |
| `relevance_score_fn` | `Callable \| None` | `None` | Override the relevance score normalization function |
| `create_collection_if_not_exists` | `bool` | `True` | Auto-create the collection if absent |

**Client connection parameters (mutually exclusive):**

| Parameter | Description |
|---|---|
| `persist_directory` | Local path for a `PersistentClient` |
| `host` | Hostname for an `HttpClient` (port defaults to `8000`) |
| `chroma_cloud_api_key` | API key for a `CloudClient` (requires `tenant` and `database`) |
| `client` | Pass a pre-existing `chromadb.ClientAPI` directly |

Only one of `persist_directory`, `host`, or `chroma_cloud_api_key` may be provided. Passing more than one raises `ValueError`.

**Additional HTTP client parameters:** `ssl`, `headers`, `tenant`, `database`, `client_settings`.

Sources: [libs/partners/chroma/langchain_chroma/vectorstores.py:302-420](), [libs/partners/chroma/pyproject.toml:23-28]()

### Client Type Selection

**Diagram: Chroma client selection logic in `__init__`**

```mermaid
flowchart TD
    A["Chroma.__init__ called"]
    B{"client != None?"}
    C["Use provided\nchromadb.ClientAPI"]
    D{"persist_directory\n!= None?"}
    E["chromadb.PersistentClient\n(path=persist_directory)"]
    F{"host != None?"}
    G["chromadb.HttpClient\n(host, port, ssl, headers)"]
    H{"chroma_cloud_api_key\n!= None?"}
    I["chromadb.CloudClient\n(tenant, database, api_key)"]
    J["chromadb.Client\n(in-memory, settings only)"]
    K["__ensure_collection()"]

    A --> B
    B -- "yes" --> C
    B -- "no" --> D
    D -- "yes" --> E
    D -- "no" --> F
    F -- "yes" --> G
    F -- "no" --> H
    H -- "yes" --> I
    H -- "no" --> J
    C --> K
    E --> K
    G --> K
    I --> K
    J --> K
```

Sources: [libs/partners/chroma/langchain_chroma/vectorstores.py:349-421]()

---

## Document Operations

### Adding Documents

**`add_texts`** [libs/partners/chroma/langchain_chroma/vectorstores.py:505-570]()

Accepts a list of text strings, optional per-document metadata dicts, and optional explicit IDs. If `ids` is not provided, UUIDs are generated. If an `embedding_function` is set, texts are embedded via `embedding_function.embed_documents(texts)` before insertion.

**`add_images`** [libs/partners/chroma/langchain_chroma/vectorstores.py:573-630]()

Accepts a list of local file URI strings. Each image is base64-encoded via `encode_image`, then passed to a Chroma embedding function that supports image input. Metadata and IDs are handled identically to `add_texts`.

**`from_texts` / `from_documents`** — class methods that create a new `Chroma` instance and call `add_texts` / `add_documents` in one step.

### Retrieving Documents

**`get_by_ids`** — Returns `list[Document]` for a given list of ID strings. Fetches `documents`, `metadatas`, and `ids` from the underlying collection.

**`get`** [libs/partners/chroma/langchain_chroma/vectorstores.py:857-920]()

Lower-level access. Accepts `ids`, `where` (metadata filter dict), `limit`, and `offset`. Returns the raw ChromaDB result dict.

### Updating Documents

**`update_documents`** [libs/partners/chroma/langchain_chroma/vectorstores.py:680-720]()

Takes a list of `ids` and matching `list[Document]`. Re-embeds the new `page_content` and calls `collection.update(...)` with new embeddings, documents, and metadatas.

### Deleting Documents

**`delete`** — Calls `collection.delete(ids=ids)`. If no IDs are passed, raises a `ValueError`.

**`delete_collection`** — Calls `client.delete_collection(name)` and sets `_chroma_collection = None`.

**`reset_collection`** — Deletes and re-creates the collection in one step via `delete_collection()` then `__ensure_collection()`.

---

## Search Methods

The `Chroma` class provides four distinct search strategies. All search methods accept a `filter` parameter (a metadata filter dict matching the ChromaDB `Where` type) and a `where_document` parameter (a document content filter).

**Diagram: Search method call flow**

```mermaid
flowchart LR
    Q["Query string / vector"]

    subgraph "Text-based entry points"
        SS["similarity_search(query, k)"]
        SSS["similarity_search_with_score(query, k)"]
        SSRS["similarity_search_with_relevance_scores(query, k)"]
        SSV["similarity_search_with_vectors(query, k)"]
        MMR["max_marginal_relevance_search(query, k, fetch_k, lambda_mult)"]
    end

    subgraph "Vector-based entry points"
        SSBV["similarity_search_by_vector(embedding, k)"]
        SSBVRS["similarity_search_by_vector_with_relevance_scores(embedding, k)"]
        MMRBV["max_marginal_relevance_search_by_vector(embedding, k)"]
    end

    subgraph "__query_collection"
        QC["collection.query(query_texts / query_embeddings, n_results)"]
    end

    subgraph "Result helpers"
        RTD["_results_to_docs()"]
        RTDS["_results_to_docs_and_scores()"]
        RTDV["_results_to_docs_and_vectors()"]
        MMR_ALGO["maximal_marginal_relevance()"]
    end

    Q --> SS --> QC --> RTD
    Q --> SSS --> QC --> RTDS
    Q --> SSRS --> QC --> RTDS
    Q --> SSV --> QC --> RTDV
    Q --> MMR --> QC --> RTDV --> MMR_ALGO
    Q --> SSBV --> QC --> RTD
    Q --> SSBVRS --> QC --> RTDS
    Q --> MMRBV --> QC --> RTDV --> MMR_ALGO
```

Sources: [libs/partners/chroma/langchain_chroma/vectorstores.py:730-870]()

### `similarity_search`

Returns `list[Document]`. Calls `__query_collection` with `query_texts=[query]` and converts results via `_results_to_docs`.

### `similarity_search_with_score`

Returns `list[tuple[Document, float]]`. The float is the raw **L2 distance** returned by ChromaDB (lower = more similar).

### `similarity_search_with_relevance_scores`

Wraps `similarity_search_with_score` and converts raw distances to normalized relevance scores in `[0, 1]` (higher = more similar) using `_select_relevance_score_fn`. The function selected depends on the collection's distance metric:

| ChromaDB distance metric | Relevance score function |
|---|---|
| `"cosine"` (default) | `_cosine_relevance_score_fn` |
| `"l2"` | `_euclidean_relevance_score_fn` |
| `"ip"` | `_max_inner_product_relevance_score_fn` |

A custom function can be supplied via the `relevance_score_fn` constructor argument.

### `max_marginal_relevance_search` (MMR)

Balances relevance with diversity. Parameters:

| Parameter | Default | Description |
|---|---|---|
| `k` | `4` | Number of documents to return |
| `fetch_k` | `20` | Number of candidates fetched from the store before re-ranking |
| `lambda_mult` | `0.5` | Diversity weight: `0` = maximum diversity, `1` = minimum diversity |

Internally calls `__query_collection` requesting `fetch_k` results with `include=["embeddings"]`, then applies the `maximal_marginal_relevance` function [libs/partners/chroma/langchain_chroma/vectorstores.py:109-152]() which implements the MMR formula using cosine similarity.

---

## Metadata Filtering

All search methods accept a `filter` keyword argument. The value is a ChromaDB `Where` dict.

Simple equality filter:

```python
results = store.similarity_search("query", k=5, filter={"category": "news"})
```

Operator-based filter:

```python
results = store.similarity_search(
    "query",
    k=5,
    filter={"year": {"$gte": 2020}},
)
```

The `where_document` parameter filters by the document's text content:

```python
results = store.similarity_search(
    "query",
    k=5,
    where_document={"$contains": "important phrase"},
)
```

Sources: [libs/partners/chroma/langchain_chroma/vectorstores.py:449-484](), [libs/partners/chroma/tests/integration_tests/test_vectorstores.py:228-279]()

---

## Embedding Functions

The `Chroma` class accepts a LangChain `Embeddings` object (from `langchain_core.embeddings`) via its `embedding_function` constructor parameter. This is stored as `self._embedding_function` and exposed through the read-only `embeddings` property.

**Important:** The embedding function is managed by LangChain, not by ChromaDB. When calling `client.get_or_create_collection`, `embedding_function=None` is always passed [libs/partners/chroma/langchain_chroma/vectorstores.py:424-429](). LangChain calls `embedding_function.embed_documents(texts)` itself before handing pre-computed vectors to ChromaDB's API.

**Diagram: Embedding flow for `add_texts`**

```mermaid
sequenceDiagram
    participant "Caller"
    participant "Chroma.add_texts"
    participant "Embeddings.embed_documents"
    participant "chromadb.Collection.upsert"

    "Caller" ->> "Chroma.add_texts": texts, metadatas, ids
    alt "embedding_function is not None"
        "Chroma.add_texts" ->> "Embeddings.embed_documents": texts
        "Embeddings.embed_documents" -->> "Chroma.add_texts": embeddings (list[list[float]])
        "Chroma.add_texts" ->> "chromadb.Collection.upsert": ids, embeddings, documents, metadatas
    else "no embedding_function"
        "Chroma.add_texts" ->> "chromadb.Collection.upsert": ids, documents, metadatas (ChromaDB embeds)
    end
    "chromadb.Collection.upsert" -->> "Chroma.add_texts": void
    "Chroma.add_texts" -->> "Caller": ids
```

Sources: [libs/partners/chroma/langchain_chroma/vectorstores.py:505-570]()

---

## Collection Management

| Method | Description |
|---|---|
| `__ensure_collection()` | Calls `client.get_or_create_collection(name, ...)`. Called automatically in `__init__` when `create_collection_if_not_exists=True`. |
| `_collection` (property) | Returns `self._chroma_collection`. Raises `ValueError` if `None` (i.e., collection not initialized). |
| `update_collection(collection_metadata)` | Modifies collection metadata on an existing collection. |
| `reset_collection()` | Deletes the collection and re-creates it via `__ensure_collection()`. |
| `delete_collection()` | Calls `client.delete_collection(name)` and sets `_chroma_collection = None`. |
| `fork(new_name)` | Calls `collection.fork(new_name=new_name)` and returns a new `Chroma` instance wrapping the forked collection. |

Sources: [libs/partners/chroma/langchain_chroma/vectorstores.py:422-505]()

---

## Using as a Retriever

`VectorStore.as_retriever()` (inherited from `langchain-core`) wraps the vector store in a `VectorStoreRetriever`, making it compatible with the `BaseRetriever` interface and thus chainable via LCEL.

```python
retriever = store.as_retriever(
    search_type="mmr",  # or "similarity", "similarity_score_threshold"
    search_kwargs={"k": 3, "fetch_k": 10, "lambda_mult": 0.5},
)
```

The `search_type` values map to the underlying search methods:

| `search_type` | Underlying method |
|---|---|
| `"similarity"` | `similarity_search` |
| `"similarity_score_threshold"` | `similarity_search_with_relevance_scores` |
| `"mmr"` | `max_marginal_relevance_search` |

Sources: [libs/partners/chroma/langchain_chroma/vectorstores.py:295-298]()

---

## Standard Test Suite

The `langchain-tests` package provides `VectorStoreIntegrationTests` in `libs/standard-tests/langchain_tests/integration_tests/vectorstores.py`. Any vector store implementation can be validated against it by subclassing and providing a `vectorstore` fixture.

### Subclassing Pattern

```python
# libs/partners/chroma/tests/unit_tests/test_standard.py
class TestChromaStandard(VectorStoreIntegrationTests):
    @pytest.fixture()
    def vectorstore(self) -> Generator[VectorStore, None, None]:
        store = Chroma(embedding_function=self.get_embeddings())
        try:
            yield store
        finally:
            store.delete_collection()
```

The `get_embeddings()` static method returns a `DeterministicFakeEmbedding(size=6)` for test reproducibility [libs/standard-tests/langchain_tests/integration_tests/vectorstores.py:123-136]().

### Test Coverage

| Test Method | What It Checks |
|---|---|
| `test_vectorstore_is_empty` | Fixture yields an empty store |
| `test_add_documents` | `add_documents` adds retrievable docs; originals not mutated |
| `test_vectorstore_still_empty` | Fixture resets between tests |
| `test_deleting_documents` | `delete([id])` removes one document |
| `test_deleting_bulk_documents` | `delete([id1, id2, ...])` removes multiple documents |
| `test_add_documents_with_existing_ids` | Upsert behavior with pre-specified IDs |
| `test_get_by_ids` | `get_by_ids` returns the correct documents |
| `test_get_by_ids_missing` | Returns empty list for unknown IDs |
| `test_similarity_search` | Returns relevant documents for a text query |
| `test_similarity_search_with_relevance_scores` | Scores are in `[0, 1]` range |
| `test_async_*` | Async variants of the above |

Properties that control which tests run:

| Property | Default | Description |
|---|---|---|
| `has_sync` | `True` | Include sync tests |
| `has_async` | `True` | Include async tests |
| `has_get_by_ids` | `True` | Include `get_by_ids` tests |

Sources: [libs/standard-tests/langchain_tests/integration_tests/vectorstores.py:21-500](), [libs/partners/chroma/tests/unit_tests/test_standard.py:1-50]()

---

## Package Structure

```
libs/partners/chroma/
├── langchain_chroma/
│   ├── __init__.py
│   └── vectorstores.py          # Chroma class
├── tests/
│   ├── integration_tests/
│   │   ├── test_vectorstores.py # Full ChromaDB integration tests
│   │   └── fake_embeddings.py
│   └── unit_tests/
│       ├── test_standard.py     # VectorStoreIntegrationTests subclass
│       └── test_vectorstores.py # Unit-level tests
└── pyproject.toml               # langchain-chroma package metadata
```

**Runtime dependencies** ([libs/partners/chroma/pyproject.toml:23-28]()):
- `langchain-core>=1.1.3,<2.0.0`
- `chromadb>=1.3.5,<2.0.0`
- `numpy>=1.26.0` (Python < 3.13), `numpy>=2.1.0` (Python >= 3.13)

Sources: [libs/partners/chroma/pyproject.toml:1-40]()