assert isinstance(full_message, AIMessageChunk)
assert full_message.content  # Aggregated content
assert full_message.usage_metadata  # Aggregated usage
```

**Chunk merging behavior:**
- Content strings are concatenated
- Tool call chunks are aggregated by index
- Usage metadata is summed
- Response metadata is updated with latest values

**Sources:**
- [libs/partners/openai/tests/integration_tests/chat_models/test_base.py:156-174]()
- [libs/partners/anthropic/tests/integration_tests/test_chat_models.py:41-85]()

## Usage Metadata Tracking

All providers track token usage through the `UsageMetadata` structure, which is attached to both complete responses and streaming chunks.

**Diagram: Usage Metadata Extraction in `_create_usage_metadata()`**

```mermaid
graph TB
    APIResponse["OpenAI API Response"]
    CheckUsage["response.usage<br/>present?"]
    
    ExtractBase["input_tokens = usage.prompt_tokens<br/>output_tokens = usage.completion_tokens<br/>total_tokens = usage.total_tokens"]
    
    CheckDetails["usage has<br/>prompt_tokens_details<br/>or completion_tokens_details?"]
    
    ExtractInputDetails["InputTokenDetails(<br/>cache_creation=cached_tokens,<br/>cache_read=cache_read_tokens)"]
    
    ExtractOutputDetails["OutputTokenDetails(<br/>reasoning=reasoning_tokens,<br/>audio=audio_tokens)"]
    
    CreateMetadata["UsageMetadata(<br/>input_tokens=input_tokens,<br/>output_tokens=output_tokens,<br/>total_tokens=total_tokens,<br/>input_token_details=input_details,<br/>output_token_details=output_details)"]
    
    AttachToMessage["AIMessage.usage_metadata =<br/>usage_metadata"]
    
    APIResponse --> CheckUsage
    CheckUsage -->|Yes| ExtractBase
    CheckUsage -->|No| AttachToMessage
    
    ExtractBase --> CheckDetails
    CheckDetails -->|Yes| ExtractInputDetails
    CheckDetails -->|No| CreateMetadata
    
    ExtractInputDetails --> ExtractOutputDetails
    ExtractOutputDetails --> CreateMetadata
    CreateMetadata --> AttachToMessage
```

### Usage Metadata Structure

| Field | Type | Description | Source |
|-------|------|-------------|--------|
| `input_tokens` | `int` | Total input tokens | `usage.prompt_tokens` |
| `output_tokens` | `int` | Total output tokens | `usage.completion_tokens` |
| `total_tokens` | `int` | Sum of input + output | `usage.total_tokens` |
| `input_token_details` | `InputTokenDetails` | Cache hits, audio | `usage.prompt_tokens_details` |
| `output_token_details` | `OutputTokenDetails` | Reasoning, audio | `usage.completion_tokens_details` |

### Streaming Usage Metadata

Providers control usage metadata in streams via the `stream_usage` parameter:

```python