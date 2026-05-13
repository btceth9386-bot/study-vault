This page covers the model selection and validation system, including the model catalog system, provider-aware normalization, runtime validation against provider APIs, and context length discovery.

---

## Model Catalog System

Hermes maintains a multi-tier model discovery system that combines the community-maintained `models.dev` database, curated static lists, and live API discovery.

### Models.dev Integration
The primary database for providers and models is the `models.dev` registry [agent/models_dev.py:1-19](). This provides rich metadata for over 4,000 models, including context windows, costs, and capabilities like reasoning or tool-calling [agent/models_dev.py:47-81]().
*   **Data Resolution**: It uses a resolution order of: Bundled snapshot → Disk cache (`~/.hermes/models_dev_cache.json`) → Network fetch (`https://models.dev/api.json`) [agent/models_dev.py:11-15]().
*   **Provider Mapping**: Hermes maps internal provider slugs to `models.dev` IDs via `PROVIDER_TO_MODELS_DEV` [agent/models_dev.py:141-175]().

### Curated and Dynamic Catalogs
The `hermes_cli/models.py` module serves as the source of truth for the `hermes setup` wizard and the `/model` command [hermes_cli/models.py:1-6]().
*   **Nous**: Recommended models including `kimi-k2.6`, `mimo-v2.5-pro`, and various Claude/GPT versions [hermes_cli/models.py:157-185]().
*   **OpenAI Codex**: Curated list derived from `hermes_cli/codex_models.py` which prioritizes live API discovery via OAuth tokens before falling back to `DEFAULT_CODEX_MODELS` [hermes_cli/codex_models.py:14-35](), [hermes_cli/codex_models.py:169-174]().
*   **xAI**: Derived from the `models.dev` disk cache via `_xai_curated_models()`, falling back to `_XAI_STATIC_FALLBACK` [hermes_cli/models.py:116-156]().

### Live Discovery and Auto-Detection
*   **Aggregators**: OpenRouter models are fetched from `OPENROUTER_MODELS_URL` [agent/model_metadata.py:21]().
*   **Local Servers**: The `_auto_detect_local_model` function queries local `/v1/models` endpoints to automatically resolve the model ID when a user points to a local base URL [hermes_cli/runtime_provider.py:89-107]().

**Model Resolution Data Flow**

```mermaid
graph TD
    "Input[User Input/Alias]" --> "Direct[DIRECT_ALIASES]"
    "Direct" --> "ModelIdentity[ModelIdentity/MODEL_ALIASES]"
    "ModelIdentity" --> "ModelsDev[agent.models_dev.get_model_info]"
    "ModelsDev" --> "Normalize[hermes_cli.model_normalize.normalize_model_for_provider]"
    "Normalize" --> "Final[Resolved API Model ID]"
```
Sources: [hermes_cli/model_switch.py:99-176](), [agent/models_dev.py:47-81](), [hermes_cli/model_normalize.py:23-28]()

---

## Model Selection and Normalization

### Provider-Aware Normalization
The `hermes_cli/model_normalize.py` module centralizes the translation of user-friendly model names into provider-specific API identifiers [hermes_cli/model_normalize.py:1-28]().
*   **Aggregators**: OpenRouter and Nous require `vendor/model` slugs [hermes_cli/model_normalize.py:67-72]().
*   **Anthropic**: Native API expects bare names with dots replaced by hyphens (e.g., `claude-3-5-sonnet`) [hermes_cli/model_normalize.py:74-77]().
*   **DeepSeek**: Special handling maps various aliases (r1, think, reasoning) to canonical names like `deepseek-reasoner` or `deepseek-chat` [hermes_cli/model_normalize.py:119-181]().
*   **Xiaomi**: Requires strictly lowercase model IDs [hermes_cli/model_normalize.py:114-116]().

### Model Switcher Logic
The `/model` command and setup wizard use `hermes_cli/model_switch.py` to handle the transition pipeline: parse flags → alias resolution → provider resolution → normalize model name → metadata lookup [hermes_cli/model_switch.py:1-19]().
*   **Non-Agentic Warning**: The system checks `is_nous_hermes_non_agentic()` to warn users if they select Nous Hermes 3 or 4 models, which lack the tool-calling capabilities required for the agent [hermes_cli/model_switch.py:53-84]().

**Code Entity Space: Model Switching**

```mermaid
graph LR
    subgraph "hermes_cli/model_switch.py"
        "switch_model" --> "resolve_provider_full"
        "switch_model" --> "normalize_model_for_provider"
        "switch_model" --> "get_model_info"
    end
    subgraph "hermes_cli/model_normalize.py"
        "normalize_model_for_provider" --> "deepseek[_normalize_for_deepseek]"
        "normalize_model_for_provider" --> "dots[_dots_to_hyphens]"
    end
    subgraph "agent/models_dev.py"
        "get_model_info" --> "fetch_models_dev"
    end
```
Sources: [hermes_cli/model_switch.py:1-44](), [hermes_cli/model_normalize.py:148-181](), [agent/models_dev.py:1-19]()

---

## Context Length Discovery

Hermes discovers model context lengths dynamically to handle new models and ensure the `ContextCompressor` operates within limits.

### Resolution Priority
The `get_model_context_length()` function in `agent/model_metadata.py` follows this chain:
1.  **Memory Cache**: `_model_metadata_cache` [agent/model_metadata.py:105]().
2.  **models.dev**: Primary source for provider-specific context lengths [agent/model_metadata.py:136-137]().
3.  **Hardcoded Fallbacks**: `DEFAULT_CONTEXT_LENGTHS` using substring matching for major families (e.g., Claude 4.6 at 1M, Gemini at 1M, GPT-5 at 400k) [agent/model_metadata.py:137-172]().
4.  **Probe Tiers**: If all else fails, the system steps down through `CONTEXT_PROBE_TIERS` (256K, 128K, 64K, 32K, 16K, 8K) [agent/model_metadata.py:112-123]().

### Validation and Errors
*   **Minimum Context**: The system enforces `MINIMUM_CONTEXT_LENGTH = 64_000`. Models with fewer tokens are rejected as they cannot maintain the tool-calling workflow [agent/model_metadata.py:131-132]().
*   **Error Parsing**: If a request fails, `parse_context_limit_from_error()` extracts the actual limit from OpenAI, Ollama, or Anthropic error strings using regex [agent/model_metadata.py:31]().

---

## Auxiliary Model Management

Hermes uses an auxiliary LLM client for secondary tasks like vision analysis, summarization, and web extraction [agent/auxiliary_client.py:1-6]().

### Provider Resolution
The auxiliary system resolves providers in this order:
1.  **Task Override**: Specific provider/model set in `config.yaml` (e.g., `auxiliary.vision.model`) [agent/auxiliary_client.py:32-34]().
2.  **Main Alias**: If set to `main`, it resolves to the primary agent model and provider [agent/auxiliary_client.py:27-36]().
3.  **Auto Discovery**: Tries OpenRouter, then Nous, then native Anthropic or OpenAI based on available credentials [agent/auxiliary_client.py:7-23]().

### Normalization
The `_normalize_vision_provider` and `_normalize_aux_provider` functions map common names (e.g., `google` → `gemini`, `codex` → `openai-codex`) to ensure compatibility with the auxiliary client's internal resolution [agent/auxiliary_client.py:131-162]().

Sources: [agent/auxiliary_client.py:1-162](), [agent/model_metadata.py:105-180](), [hermes_cli/model_switch.py:1-176](), [hermes_cli/model_normalize.py:1-181](), [agent/models_dev.py:1-175]()