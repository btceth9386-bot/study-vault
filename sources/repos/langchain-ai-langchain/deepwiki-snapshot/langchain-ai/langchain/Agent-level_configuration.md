from langchain.agents import create_agent
from langchain.agents.structured_output import ResponseFormat

response_format = ResponseFormat(
    schema=Response,
    strategy=AutoStrategy(),  # Automatically selects best method
)

agent = create_agent(
    model=model,
    tools=tools,
    response_format=response_format,
)
```

Sources: [libs/langchain_v1/tests/unit_tests/agents/test_response_format.py:1-100]()

### Middleware-Based Dynamic Configuration

```python
# Dynamic response format in middleware
from langchain.agents.middleware.types import before_model

@before_model
def set_response_format(request):
    if should_use_structured_output(request.state):
        request.response_format = ResponseFormat(
            schema=MySchema,
            strategy=ProviderStrategy(),
        )
    return request
```

Sources: [libs/langchain_v1/langchain/agents/middleware/types.py:200-300]()

## Provider Compatibility Matrix

| Provider | Native JSON Schema | Tool-Based | JSON Mode | Validation |
|----------|-------------------|------------|-----------|------------|
| OpenAI (GPT-4o+) | ✅ `json_schema` | ✅ | ✅ | Strict |
| OpenAI (GPT-4, 3.5) | ❌ | ✅ | ✅ | Standard |
| Anthropic (Claude) | ❌ | ✅ | ❌ | Standard |
| Mistral (Large+) | ❌ | ✅ | ✅ | Standard |
| Groq | ❌ | ✅ | ✅ | Standard |

Sources: [libs/partners/openai/langchain_openai/chat_models/base.py:1200-1500](), [libs/partners/anthropic/langchain_anthropic/chat_models.py:1100-1300](), [libs/partners/mistralai/langchain_mistralai/chat_models.py:600-800]()

## Best Practices

### Strategy Selection

1. **Use AutoStrategy by default**: Let the system choose the optimal method
2. **Prefer ProviderStrategy when available**: Native support is most reliable
3. **Use ToolStrategy for compatibility**: Works across all tool-capable models

### Schema Design

1. **Keep schemas simple**: Complex nested structures may fail validation
2. **Provide descriptions**: Help the model understand expected output
3. **Use strict mode when available**: Ensures exact schema compliance

### Error Handling

1. **Implement retry logic**: Validation failures can often be corrected
2. **Provide clear error messages**: Include validation details in retry prompts
3. **Monitor validation rates**: Track success/failure for model evaluation

Sources: [libs/langchain_v1/langchain/agents/structured_output.py](), [libs/langchain_v1/langchain/agents/factory.py:107-108]()