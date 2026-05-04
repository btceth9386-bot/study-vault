This guide covers how to install GEPA and get up and running with its two primary APIs: `gepa.optimize` for prompt optimization and `optimize_anything` for arbitrary text artifacts.

---

## Installation

Install GEPA from PyPI:

```bash
pip install gepa
```

To include all optional dependencies (for DSPy integration, experiment tracking with WandB/MLflow, and specialized adapters):

```bash
pip install "gepa[full]"
```

**Requirements:**
- **Python**: `3.10` to `3.14` [[pyproject.toml:18]()]
- **API Keys**: Set environment variables for your providers (e.g., `OPENAI_API_KEY`). GEPA uses `litellm` to interface with 100+ models [[README.md:86-88]()].

**Sources:** [[pyproject.toml:18-40](), [README.md:52-62]()]

---

## Simple Prompt Optimization (`gepa.optimize`)

The `gepa.optimize` function is the high-level entry point for optimizing system prompts. It uses a `DefaultAdapter` to handle single-turn LLM tasks by wrapping them into a standard evaluation loop [[docs/docs/guides/quickstart.md:29-31]()].

### Example: AIME Math Problems
Optimize a prompt to improve a model's performance on competition-level math:

```python
import gepa