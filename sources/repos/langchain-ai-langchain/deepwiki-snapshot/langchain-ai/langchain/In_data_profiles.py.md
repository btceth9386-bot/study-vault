from langchain_core.language_models import ModelProfileRegistry

_PROFILES: ModelProfileRegistry = {
    "gpt-4": {
        "max_input_tokens": 8192,
        "max_output_tokens": 4096,
        "tool_calling": True,
        "structured_output": False,
        "supports_vision": True,
    },
    "claude-sonnet-4-5-20250929": {
        "max_input_tokens": 200000,
        "max_output_tokens": 8192,
        "tool_calling": True,
        "structured_output": True,
        "supports_vision": True,
    },
}