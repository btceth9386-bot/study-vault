from typing import Type
from langchain_tests.integration_tests import ChatModelIntegrationTests
from langchain_yourprovider import ChatYourProvider

class TestChatYourProviderIntegration(ChatModelIntegrationTests):
    @property
    def chat_model_class(self) -> Type[ChatYourProvider]:
        return ChatYourProvider
    
    @property
    def chat_model_params(self) -> dict:
        return {
            "model": "your-model-001",
            "temperature": 0,
        }
    
    # Set feature flags based on your model's capabilities
    @property
    def has_tool_calling(self) -> bool:
        return True  # Your model supports tool calling
    
    @property
    def supports_image_inputs(self) -> bool:
        return True  # Your model supports images
    
    @property
    def structured_output_kwargs(self) -> dict:
        # Customize how structured output is tested
        return {"method": "function_calling"}
```

**Step 3: Run tests**

```bash
# Run unit tests (no API calls)
pytest tests/unit_tests/

# Run integration tests (requires API key)
export YOUR_PROVIDER_API_KEY=...
pytest tests/integration_tests/
```

### Feature Flags Reference

Configure these properties to match your model's capabilities:

| Property | Type | Default | Purpose |
|----------|------|---------|---------|
| `has_tool_calling` | `bool` | Auto-detect | Enable tool calling tests |
| `has_tool_choice` | `bool` | Auto-detect | Test `tool_choice` parameter |
| `has_structured_output` | `bool` | Auto-detect | Test `with_structured_output()` |
| `supports_json_mode` | `bool` | `False` | Test JSON mode structured output |
| `supports_image_inputs` | `bool` | `False` | Test image content blocks |
| `supports_audio_inputs` | `bool` | `False` | Test audio content blocks |
| `returns_usage_metadata` | `bool` | `True` | Test usage metadata in responses |

**Auto-detection:**
- `has_tool_calling`: Checks if `bind_tools()` is overridden
- `has_tool_choice`: Checks if `tool_choice` param in `bind_tools()` signature
- `has_structured_output`: Checks if `with_structured_output()` is overridden

**VCR recording for deterministic tests:**

```python