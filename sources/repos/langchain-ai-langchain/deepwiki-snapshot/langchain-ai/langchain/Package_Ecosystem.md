This page describes every package in the LangChain monorepo: what each one contains, its PyPI distribution name, its version, and how the packages depend on one another. For information about the foundational abstractions that packages are built on top of, see [Core Architecture](#2). For patterns around selecting and swapping providers, see [Integration Patterns and Best Practices](#3.5). For the build system and `pyproject.toml` structure, see [Package Structure and Build System](#6.1).

---

## Monorepo Layout

The repository is a monorepo under `libs/`. Each subdirectory is an independently versioned Python package with its own `pyproject.toml`. The mapping from directory path to PyPI package name is not always obvious.

**Directory → PyPI name mapping:**

| Directory | PyPI Package Name | Current Version |
|---|---|---|
| `libs/core/` | `langchain-core` | 1.2.16 |
| `libs/langchain_v1/` | `langchain` | 1.2.10 |
| `libs/langchain/` | `langchain-classic` | 1.0.1 |
| `libs/text-splitters/` | `langchain-text-splitters` | (independent) |
| `libs/standard-tests/` | `langchain-tests` | (independent) |
| `libs/partners/openai/` | `langchain-openai` | (independent) |
| `libs/partners/anthropic/` | `langchain-anthropic` | (independent) |
| `libs/partners/mistralai/` | `langchain-mistralai` | (independent) |
| `libs/partners/groq/` | `langchain-groq` | (independent) |
| `libs/partners/fireworks/` | `langchain-fireworks` | (independent) |
| `libs/partners/xai/` | `langchain-xai` | (independent) |
| `libs/partners/ollama/` | `langchain-ollama` | (independent) |
| `libs/partners/chroma/` | `langchain-chroma` | (independent) |
| `libs/partners/huggingface/` | `langchain-huggingface` | (independent) |
| `libs/partners/deepseek/` | `langchain-deepseek` | (independent) |
| `libs/partners/perplexity/` | `langchain-perplexity` | (independent) |

> **Note:** The directory `libs/langchain_v1/` contains the current main `langchain` package on PyPI. The directory `libs/langchain/` is a separate legacy package called `langchain-classic`.

Sources: [libs/core/pyproject.toml:1-36](), [libs/langchain_v1/pyproject.toml:1-30](), [libs/langchain/pyproject.toml:1-34](), [libs/text-splitters/README.md:1-5](), [libs/standard-tests/README.md:1-5]()

---

## Dependency Graph

The packages form a layered dependency hierarchy. `langchain-core` sits at the bottom, with no dependencies on other LangChain packages. All other packages depend on it.

**Package dependency graph:**

```mermaid
graph TD
    core["\"langchain-core\n(libs/core/)\""]
    splitters["\"langchain-text-splitters\n(libs/text-splitters/)\""]
    langchain["\"langchain\n(libs/langchain_v1/)\""]
    classic["\"langchain-classic\n(libs/langchain/)\""]
    tests["\"langchain-tests\n(libs/standard-tests/)\""]

    subgraph partners["\"Partner packages (libs/partners/*)\""]
        openai["\"langchain-openai\""]
        anthropic["\"langchain-anthropic\""]
        mistralai["\"langchain-mistralai\""]
        groq["\"langchain-groq\""]
        fireworks["\"langchain-fireworks\""]
        xai["\"langchain-xai\""]
        ollama["\"langchain-ollama\""]
        chroma["\"langchain-chroma\""]
        huggingface["\"langchain-huggingface\""]
        deepseek["\"langchain-deepseek\""]
        perplexity["\"langchain-perplexity\""]
    end

    splitters --> core
    langchain --> core
    classic --> core
    classic --> splitters
    tests --> core
    openai --> core
    anthropic --> core
    mistralai --> core
    groq --> core
    fireworks --> core
    xai --> core
    ollama --> core
    chroma --> core
    huggingface --> core
    deepseek --> core
    perplexity --> core
```

Sources: [libs/core/pyproject.toml:26-35](), [libs/langchain_v1/pyproject.toml:26-30](), [libs/langchain/pyproject.toml:25-34]()

---

## Package Descriptions

### `langchain-core` — `libs/core/`

The foundational package. Contains all abstract base classes and the `Runnable` interface. No third-party LLM provider dependencies are included. The package docstring in [libs/core/langchain_core/__init__.py:1-9]() states: "No third-party integrations are defined here."

**Runtime dependencies** ([libs/core/pyproject.toml:26-35]()):

| Dependency | Version Constraint | Purpose |
|---|---|---|
| `langsmith` | `>=0.3.45,<1.0.0` | Tracing and run tracking |
| `tenacity` | `!=8.4.0,>=8.1.0,<10.0.0` | Retry logic |
| `jsonpatch` | `>=1.33.0,<2.0.0` | JSON patch operations |
| `PyYAML` | `>=5.3.0,<7.0.0` | YAML parsing |
| `typing-extensions` | `>=4.7.0,<5.0.0` | Backported type hints |
| `packaging` | `>=23.2.0` | Version handling |
| `pydantic` | `>=2.7.4,<3.0.0` | Data validation |
| `uuid-utils` | `>=0.12.0,<1.0` | UUID generation |

Python compatibility: `>=3.10.0,<4.0.0`. The version is maintained in [libs/core/langchain_core/version.py:3]() as `VERSION = "1.2.16"` and imported by [libs/core/langchain_core/__init__.py:15-17]().

Sources: [libs/core/pyproject.toml:1-82](), [libs/core/langchain_core/version.py:1-3](), [libs/core/langchain_core/__init__.py:1-20]()

---

### `langchain` — `libs/langchain_v1/`

The primary user-facing package installable via `pip install langchain`. It provides the agent system, middleware pipeline, `init_chat_model`, and higher-level application building blocks. It depends on `langchain-core` and `langgraph`.

**Runtime dependencies** ([libs/langchain_v1/pyproject.toml:26-30]()):

| Dependency | Version Constraint |
|---|---|
| `langchain-core` | `>=1.2.10,<2.0.0` |
| `langgraph` | `>=1.0.8,<1.1.0` |
| `pydantic` | `>=2.7.4,<3.0.0` |

This package does **not** depend on `langchain-text-splitters` as a required dependency; text splitting is opt-in. Partner packages are available as optional extras declared in `[project.optional-dependencies]` ([libs/langchain_v1/pyproject.toml:32-49]()):

```
langchain[openai]      → langchain-openai
langchain[anthropic]   → langchain-anthropic
langchain[mistralai]   → langchain-mistralai
langchain[groq]        → langchain-groq
langchain[fireworks]   → langchain-fireworks
langchain[ollama]      → langchain-ollama
langchain[huggingface] → langchain-huggingface
langchain[deepseek]    → langchain-deepseek
langchain[xai]         → langchain-xai
langchain[perplexity]  → langchain-perplexity
langchain[community]   → langchain-community
```

The package version `__version__ = "1.2.10"` is set in [libs/langchain_v1/langchain/__init__.py:3]() and must match `pyproject.toml`, which is enforced by the test in [libs/langchain_v1/tests/unit_tests/test_version.py:10-27]().

Sources: [libs/langchain_v1/pyproject.toml:1-100](), [libs/langchain_v1/langchain/__init__.py:1-3]()

---

### `langchain-classic` — `libs/langchain/`

A legacy package on PyPI (`pip install langchain-classic`). Contains legacy chains, `langchain-community` re-exports, deprecated functionality, and the indexing API. The README in [libs/langchain/README.md:20-23]() describes it as: "Legacy chains, `langchain-community` re-exports, indexing API, deprecated functionality, and more."

**Runtime dependencies** ([libs/langchain/pyproject.toml:25-34]()):

| Dependency | Version Constraint |
|---|---|
| `langchain-core` | `>=1.2.5,<2.0.0` |
| `langchain-text-splitters` | `>=1.1.0,<2.0.0` |
| `langsmith` | `>=0.1.17,<1.0.0` |
| `pydantic` | `>=2.7.4,<3.0.0` |
| `SQLAlchemy` | `>=1.4.0,<3.0.0` |
| `requests` | `>=2.0.0,<3.0.0` |
| `PyYAML` | `>=5.3.0,<7.0.0` |

The required dependencies are locked in a dependency test at [libs/langchain/tests/unit_tests/test_dependencies.py:23-44]() to prevent accidental new required dependencies.

Sources: [libs/langchain/pyproject.toml:1-55](), [libs/langchain/README.md:1-37](), [libs/langchain/tests/unit_tests/test_dependencies.py:23-44]()

---

### `langchain-text-splitters` — `libs/text-splitters/`

A standalone package for splitting text documents into chunks. Depends only on `langchain-core`. Split out to a separate package so applications that do not need text splitting do not incur the dependency.

Key classes (documented further in [2.6](#2.6)):
- `RecursiveCharacterTextSplitter`
- `CharacterTextSplitter`
- `HTMLHeaderTextSplitter`
- `MarkdownHeaderTextSplitter`
- `TokenTextSplitter`

Sources: [libs/text-splitters/README.md:1-37](), [libs/core/pyproject.toml:52-53]()

---

### `langchain-tests` — `libs/standard-tests/`

A testing utility package providing base test classes that integration developers inherit to validate their implementations against the standard LangChain interface contract.

Key test base classes:
- `ChatModelUnitTests`
- `ChatModelIntegrationTests`
- `VectorStoreIntegrationTests`
- `EmbeddingsIntegrationTests`
- `ToolUnitTests` / `ToolIntegrationTests`
- `BaseStoreIntegrationTests`
- `CacheIntegrationTests`

This package is consumed as a dev/test dependency by `langchain-core`, `langchain`, and all partner packages. It is not intended as a runtime dependency. See [Standard Testing Framework](#5.1) for full documentation.

Sources: [libs/standard-tests/README.md:1-94](), [libs/core/pyproject.toml:73-75](), [libs/langchain_v1/pyproject.toml:73-74]()

---

### Partner Packages — `libs/partners/*/`

Each partner package provides concrete implementations of `langchain-core` abstract base classes for a specific AI provider. All partner packages depend only on `langchain-core` (not on `langchain` or `langchain-classic`), keeping them lightweight.

**Interface implementations by partner package:**

```mermaid
graph LR
    subgraph core_ifaces["\"langchain-core interfaces\""]
        BaseChatModel["\"BaseChatModel\""]
        BaseEmbeddings["\"Embeddings\""]
        VectorStore["\"VectorStore\""]
        BaseLLM["\"BaseLLM\""]
    end

    subgraph openai_p["\"langchain-openai\""]
        ChatOpenAI["\"ChatOpenAI\""]
        AzureChatOpenAI["\"AzureChatOpenAI\""]
        OpenAIEmbeddings["\"OpenAIEmbeddings\""]
        AzureOpenAIEmbeddings["\"AzureOpenAIEmbeddings\""]
        OpenAI_LLM["\"OpenAI (LLM)\""]
    end

    subgraph anthropic_p["\"langchain-anthropic\""]
        ChatAnthropic["\"ChatAnthropic\""]
        ChatAnthropicBedrock["\"ChatAnthropicBedrock\""]
    end

    subgraph other_p["\"Other partner packages\""]
        ChatMistralAI["\"ChatMistralAI\""]
        ChatGroq["\"ChatGroq\""]
        ChatFireworks["\"ChatFireworks\""]
        ChatXAI["\"ChatXAI\""]
        ChatOllama["\"ChatOllama\""]
        ChatDeepSeek["\"ChatDeepSeek\""]
        ChatPerplexity["\"ChatPerplexity\""]
        Chroma["\"Chroma\""]
    end

    ChatOpenAI --> BaseChatModel
    AzureChatOpenAI --> BaseChatModel
    ChatAnthropic --> BaseChatModel
    ChatMistralAI --> BaseChatModel
    ChatGroq --> BaseChatModel
    ChatFireworks --> BaseChatModel
    ChatXAI --> BaseChatModel
    ChatOllama --> BaseChatModel
    ChatDeepSeek --> BaseChatModel
    ChatPerplexity --> BaseChatModel
    OpenAI_LLM --> BaseLLM
    OpenAIEmbeddings --> BaseEmbeddings
    AzureOpenAIEmbeddings --> BaseEmbeddings
    Chroma --> VectorStore
```

Sources: [libs/langchain_v1/pyproject.toml:32-49](), [libs/langchain/pyproject.toml:36-53]()

---

## Versioning Strategy

Each package is versioned independently using [Semantic Versioning](https://semver.org/). The version is declared in `pyproject.toml` under `[project] version` and repeated in a `version.py` or `__init__.py` file within the package source. A test enforces that these two values are kept in sync.

| Package | Version Source File | Test |
|---|---|---|
| `langchain-core` | [libs/core/langchain_core/version.py:3]() | — |
| `langchain` | [libs/langchain_v1/langchain/__init__.py:3]() | [libs/langchain_v1/tests/unit_tests/test_version.py]() |

All packages use `hatchling` as the build backend ([libs/core/pyproject.toml:1-3](), [libs/langchain_v1/pyproject.toml:1-3](), [libs/langchain/pyproject.toml:1-3]()). Dependency management uses `uv` with workspace-local path references for intra-monorepo dependencies, e.g.:

```toml