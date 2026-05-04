publish:
    needs: [build, release-notes, test-pypi-publish, pre-release-checks, test-dependents]
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # For trusted publishing to PyPI
    steps:
      # ... publish with pypa/gh-action-pypi-publish@release/v1
```

This follows the PyPI trusted publishing recommendation to separate build artifacts from credentials ([.github/workflows/_release.yml:64-74]()).

**Sources**: [.github/workflows/_release.yml:45-50](), [.github/workflows/_release.yml:547-553](), [.github/workflows/_release.yml:64-74]()

### Backwards Compatibility Testing

The `test-prior-published-packages-against-new-core` job ([.github/workflows/_release.yml:386-473]()) validates that new `langchain-core` releases don't break existing partner packages:

```bash
# From .github/workflows/_release.yml:test-prior-published-packages-against-new-core
# Only runs if: startsWith(inputs.working-directory, 'libs/core')

# Identify latest published partner package tag (excluding pre-releases)
LATEST_PACKAGE_TAG="$(
  git ls-remote --tags origin "langchain-${{ matrix.partner }}*" \
  | awk '{print $2}' \
  | sed 's|refs/tags/||' \
  | grep -E '[0-9]+\.[0-9]+\.[0-9]+$' \
  | sort -Vr \
  | head -n 1
)"

# Shallow-fetch just that single tag
git fetch --depth=1 origin tag "$LATEST_PACKAGE_TAG"

# Checkout the latest published package files
rm -rf $GITHUB_WORKSPACE/libs/partners/${{ matrix.partner }}/*
rm -rf $GITHUB_WORKSPACE/libs/standard-tests/*
cd $GITHUB_WORKSPACE/libs/
git checkout "$LATEST_PACKAGE_TAG" -- standard-tests/
git checkout "$LATEST_PACKAGE_TAG" -- partners/${{ matrix.partner }}/

# Install dependencies and new core
cd partners/${{ matrix.partner }}
uv sync --group test --group test_integration
uv pip install ../../core/dist/*.whl

# Run integration tests (old partner code + new core)
make integration_tests
```

The job runs for both OpenAI and Anthropic partners in a matrix strategy ([.github/workflows/_release.yml:398-400]()).

**Sources**: [.github/workflows/_release.yml:386-473]()

## Test Organization and Conventions

### Directory Structure

```
libs/{package}/
├── tests/
│   ├── unit_tests/
│   │   ├── test_chat_models.py
│   │   ├── test_embeddings.py
│   │   └── test_tools.py
│   ├── integration_tests/
│   │   ├── test_chat_models.py
│   │   ├── test_standard.py
│   │   └── cassettes/           # VCR cassettes
│   │       └── TestClass_test.yaml.gz
│   └── conftest.py              # pytest configuration
├── pyproject.toml
├── uv.lock
└── extended_testing_deps.txt    # Optional extended dependencies
```

**Sources**: [libs/standard-tests/langchain_tests/integration_tests/chat_models.py:594-738](), [.github/workflows/check_diffs.yml:153-160]()

### Makefile Targets

Each package provides standardized Makefile targets:

| Target | Purpose | Invoked By |
|--------|---------|------------|
| `lint_package` | Lint package code with ruff + mypy | [.github/workflows/_lint.yml:62-64]() |
| `lint_tests` | Lint test code with ruff + mypy | [.github/workflows/_lint.yml:78-81]() |
| `test` | Run unit tests with pytest | [.github/workflows/_test.yml:51-53]() |
| `tests` | Alias for `test` | [.github/workflows/_test.yml:71-72]() |
| `integration_tests` | Run integration tests | [.github/workflows/_release.yml:381]() |
| `extended_tests` | Run tests with extended deps | [.github/workflows/check_diffs.yml:160]() |

**Sources**: [.github/workflows/_lint.yml:1-82](), [.github/workflows/_test.yml:1-86](), [.github/workflows/check_diffs.yml:153-160]()

### Pytest Configuration

The `pyproject.toml` for `langchain-tests` ([libs/standard-tests/pyproject.toml:104-113]()) defines standard pytest markers:

```toml
[tool.pytest.ini_options]
addopts = "--strict-markers --strict-config --durations=5 -vv"
markers = [
    "requires: mark tests as requiring a specific library",
    "scheduled: mark tests to run in scheduled testing",
    "compile: mark placeholder test used to compile integration tests without running them",
]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
```

**Sources**: [libs/standard-tests/pyproject.toml:104-113]()

## Environment Variables and Secrets

Test workflows have access to provider API keys stored as GitHub secrets:

| Secret | Used By | Example Tests |
|--------|---------|---------------|
| `OPENAI_API_KEY` | OpenAI integration tests | Chat model invoke/stream tests |
| `ANTHROPIC_API_KEY` | Anthropic integration tests | Chat model invoke/stream tests |
| `MISTRAL_API_KEY` | Mistral integration tests | Chat model invoke/stream tests |
| `GROQ_API_KEY` | Groq integration tests | Chat model invoke/stream tests |
| `LANGCHAIN_TESTS_USER_AGENT` | HTTP tests | Audio/video multimodal tests |

**Sources**: [.github/workflows/_release.yml:346-380](), [.github/workflows/check_diffs.yml:203-223](), [libs/standard-tests/langchain_tests/integration_tests/chat_models.py:143-156]()

## Performance Testing with CodSpeed

The CI pipeline includes performance benchmarking using CodSpeed ([.github/workflows/check_diffs.yml:175-233]()):

```yaml
- name: "⚡ Run Benchmarks"
  uses: CodSpeedHQ/action@v4
  with:
    token: ${{ secrets.CODSPEED_TOKEN }}
    run: |
      cd ${{ matrix.job-configs.working-directory }}
      if [ "${{ matrix.job-configs.working-directory }}" = "libs/core" ]; then
        uv run --no-sync pytest ./tests/benchmarks --codspeed
      else:
        uv run --no-sync pytest ./tests/ --codspeed
      fi
    mode: ${{ matrix.job-configs.working-directory == 'libs/core' && 'walltime' || 'instrumentation' }}
```

Tests can be marked with `@pytest.mark.benchmark` or use the `pytest-codspeed` plugin. The `mode` parameter differs between `libs/core` (walltime) and other packages (instrumentation).

**Sources**: [.github/workflows/check_diffs.yml:175-233](), [libs/standard-tests/pyproject.toml:21-22]()