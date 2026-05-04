VIRTUAL_ENV=.venv uv pip install --force-reinstall --editable .
VIRTUAL_ENV=.venv uv pip install --force-reinstall $MIN_VERSIONS
make tests
```

The `--force-reinstall` ensures minimum versions replace the current locked versions. The `--editable` install ensures the package under test remains editable.

**Sources:** [.github/workflows/_release.yml:317-336]()

**5. Integration tests (partners only):**
```bash
make integration_tests
```

**No caching policy:** The `pre-release-checks` job explicitly does not use the `uv_setup` action's caching. Comments at [.github/workflows/_release.yml:241-253]() explain:

> "We explicitly *don't* set up caching here. This ensures our tests are maximally sensitive to catching breakage. For example, here's a way that caching can cause a falsely-passing test: Make the langchain package manifest no longer list a dependency package as a requirement... That dependency used to be required, so it may have been cached. When restoring the venv packages from cache, that dependency gets included. Tests pass, because the dependency is present even though it wasn't specified. The package is published, and it breaks on the missing dependency when used in the real world."

**Sources:** [.github/workflows/_release.yml:230-382]()

### Testing New Core Against Old Partners

When releasing `langchain-core`, the `test-prior-published-packages-against-new-core` stage tests the new core with previously published partner packages:

**Algorithm:**
1. Identify latest partner package tag (excluding pre-releases)
2. Shallow-fetch that specific tag
3. Checkout the partner package files from that tag
4. Install dependencies for that old partner version
5. Install the new core from `dist/*.whl`
6. Run integration tests

**Tested partners:**
```yaml
strategy:
  matrix:
    partner: [openai, anthropic]
  fail-fast: false  # Continue testing other partners if one fails
```

**Environment secrets:** Both partners require API keys passed via GitHub secrets:
- `ANTHROPIC_API_KEY`, `ANTHROPIC_FILES_API_IMAGE_ID`, `ANTHROPIC_FILES_API_PDF_ID`
- `OPENAI_API_KEY`, `AZURE_OPENAI_*` credentials

**Purpose:** Ensures new core changes don't break existing partner packages in the wild.

**Sources:** [.github/workflows/_release.yml:386-472]()

### Trusted Publishing to PyPI

**Test PyPI publication:**
```yaml
- name: Publish to test PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    packages-dir: ${{ inputs.working-directory }}/dist/
    repository-url: https://test.pypi.org/legacy/
    skip-existing: true  # Overwrite for CI testing only
```

**Production PyPI publication:**
```yaml
- name: Publish package distributions to PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    packages-dir: ${{ inputs.working-directory }}/dist/
```

**Authentication:** Uses GitHub's trusted publishing with OIDC (`id-token: write` permission). No API keys stored in secrets.

**Sources:** [.github/workflows/_release.yml:195-228](), [.github/workflows/_release.yml:507-514]()

### GitHub Release Creation

The final stage creates a GitHub release with the version tag:

```yaml
- name: Create Tag
  uses: ncipollo/release-action@v1
  with:
    artifacts: "dist/*"
    tag: ${{needs.build.outputs.pkg-name}}==${{ needs.build.outputs.version }}
    body: ${{ needs.release-notes.outputs.release-body }}
    commit: ${{ github.sha }}
    makeLatest: ${{ needs.build.outputs.pkg-name == 'langchain-core'}}
```

**Tag format:** `{package-name}=={version}` (e.g., `langchain-core==0.3.0`)

**Release body:** Contains commit messages since previous tag

**Sources:** [.github/workflows/_release.yml:547-556]()

---

## Dependency Group Management

### Dependency Groups in `pyproject.toml`

LangChain packages use `[dependency-groups]` in `pyproject.toml` to organize development dependencies. Example from [libs/standard-tests/pyproject.toml:38-46]():

```toml
[dependency-groups]
test = ["langchain-core"]
test_integration = []
lint = ["ruff>=0.14.11,<0.15.0"]
typing = [
    "mypy>=1.19.1,<1.20.0",
    "types-pyyaml>=6.0.12.2,<7.0.0.0",
    "langchain-core",
]
```

**Group purposes:**

| Group | Purpose | Installation Command | Used By |
|-------|---------|---------------------|---------|
| `test` | Unit test dependencies (`pytest`, etc.) | `uv sync --group test` | `_test.yml`, `_lint.yml` (for test linting) |
| `test_integration` | Integration test dependencies | `uv sync --group test_integration` | `_lint.yml` (partners), `_compile_integration_test.yml` |
| `lint` | Linting tools (`ruff`) | `uv sync --group lint` | `_lint.yml` |
| `typing` | Type checking tools (`mypy`, type stubs) | `uv sync --group typing` | `_lint.yml` |

**Installation in workflows:**
- `uv sync --group test`: Installs `test` group dependencies
- `uv sync --group test --group test_integration`: Installs both groups (for partner packages)
- `uv sync --group lint --group typing`: Installs linting and type checking tools

**Sources:** [libs/standard-tests/pyproject.toml:38-46](), [.github/workflows/_lint.yml:56-76](), [.github/workflows/_test.yml:46-48]()

### Extended Testing Dependencies

For packages requiring additional dependencies beyond standard test groups, `extended_testing_deps.txt` specifies extra requirements. Example usage in `check_diffs.yml` at [.github/workflows/check_diffs.yml:153-160]():

```bash
uv venv
uv sync --group test
VIRTUAL_ENV=.venv uv pip install -r extended_testing_deps.txt
VIRTUAL_ENV=.venv make extended_tests
```

**Format:**
- Standard pip requirement format: `package==version`
- Editable installs for partner packages: `-e ../partners/{name}`

This allows testing optional features or partner integrations without adding them to the main test group.

**Sources:** [.github/workflows/check_diffs.yml:153-160]()

## CI Optimization Strategies

### Concurrency Control

**Workflow-level cancellation** at [.github/workflows/check_diffs.yml:30-32]():
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

Cancels outdated workflow runs when new commits are pushed, preventing resource waste on testing obsolete code.

**Sources:** [.github/workflows/check_diffs.yml:30-32]()

### UV Environment Configuration

**Environment variables** at [.github/workflows/check_diffs.yml:37-39]():
```yaml
env:
  UV_FROZEN: "true"     # Use locked versions from uv.lock
  UV_NO_SYNC: "true"    # Skip automatic sync operations
```

**Benefits:**
- **Reproducibility**: Always uses exact versions from `uv.lock`
- **Speed**: Skips unnecessary dependency resolution (saves ~5-10 seconds per job)
- **Reliability**: Prevents unexpected version changes mid-CI

**Sources:** [.github/workflows/check_diffs.yml:37-39]()

### Caching Strategy

The custom `.github/actions/uv_setup` composite action manages caching. Example usage at [.github/workflows/_test.yml:38-44]():

```yaml
- name: "🐍 Set up Python ${{ inputs.python-version }} + UV"
  uses: "./.github/actions/uv_setup"
  with:
    python-version: ${{ inputs.python-version }}
    cache-suffix: test-${{ inputs.working-directory }}
    working-directory: ${{ inputs.working-directory }}
```

**Cache key structure:** Combines `python-version`, `cache-suffix`, and `working-directory` to create unique cache keys per package and job type:
- `3.12-test-libs/core`
- `3.12-lint-libs/partners/openai`
- `3.13-test-pydantic-libs/langchain_v1`

**UV cache benefits:**
- Shares downloaded packages across workflow runs
- Respects `uv.lock` for reproducible installs
- Separate cache per Python version prevents cross-version contamination
- Typical cache hit saves ~30-60 seconds of installation time

**Sources:** [.github/workflows/_test.yml:38-44]()

### Fail-Fast Disabled

At [.github/workflows/check_diffs.yml:89-92]():
```yaml
strategy:
  matrix:
    job-configs: ${{ fromJson(needs.build.outputs.test) }}
  fail-fast: false
```

**Rationale:** Allow all matrix jobs to complete even if one fails, providing comprehensive feedback on which packages/versions have issues.

**Sources:** [.github/workflows/check_diffs.yml:89-92]()

### Timeout Configuration

All jobs use a 20-minute timeout. Example at [.github/workflows/_test.yml:32]():
```yaml
timeout-minutes: 20
```

Prevents stuck jobs from consuming CI resources indefinitely. Most jobs complete in 2-5 minutes.

**Sources:** [.github/workflows/_test.yml:32]()

### Large Diff Handling

At [.github/scripts/check_diff.py:236-241]():
```python
if len(files) >= 300:
    # max diff length is 300 files - there are likely files missing
    dirs_to_run["lint"] = all_package_dirs()
    dirs_to_run["test"] = all_package_dirs()
    dirs_to_run["extended-test"] = set(LANGCHAIN_DIRS)
```

When diffs exceed 300 files, the system defaults to testing all packages as a safety measure. This handles cases where the GitHub API may have truncated results.

**Sources:** [.github/scripts/check_diff.py:236-241]()

---

## Version Consistency Checks

The `check_core_versions.yml` workflow ensures version numbers stay synchronized:

**Validated files:**
- `libs/core/pyproject.toml` vs. `libs/core/langchain_core/version.py`
- `libs/langchain_v1/pyproject.toml` vs. `libs/langchain_v1/langchain/__init__.py`

**Extraction logic:**
```bash