| Function | Location | Purpose |
| :--- | :--- | :--- |
| `call_llm()` | `agent/auxiliary_client.py` | Main entry point for all auxiliary LLM tasks. |
| `_resolve_auto()` | `agent/auxiliary_client.py` | Logic for the priority fallback chain. |
| `_normalize_aux_provider()` | `agent/auxiliary_client.py` | Resolves aliases and "main" provider keywords. |
| `_get_anthropic_max_output()` | `agent/anthropic_adapter.py` | Model-specific token limit lookup. |
| `_load_openai_cls()` | `agent/auxiliary_client.py` | Lazy loader for the OpenAI SDK. |

**Sources:** [agent/auxiliary_client.py:72-183](), [agent/anthropic_adapter.py:119-137]()