This page documents the pytest setup used across the LangChain monorepo: custom markers, command-line options, `conftest.py` patterns, dependency enforcement tests, and the minimum-version compatibility testing script. This information is relevant to anyone writing, running, or debugging tests in any package under `libs/`.

For information on the standard test suites (`ChatModelUnitTests`, `VectorStoreIntegrationTests`, etc.) see page [5.1](). For how tests are triggered in CI, see page [5.3]().

---

## Overview of pytest Configuration Locations

Each package in the monorepo has its own `pyproject.toml` containing a `[tool.pytest.ini_options]` section. These are not inherited; each package configures pytest independently. The `conftest.py` files provide shared fixtures and hook implementations.

**Pytest configuration diagram:**

```mermaid
graph TD
    subgraph "libs/core"
        core_pyproject["pyproject.toml\n[tool.pytest.ini_options]"]
    end
    subgraph "libs/langchain_v1"
        v1_pyproject["pyproject.toml\n[tool.pytest.ini_options]"]
        v1_conftest["tests/unit_tests/conftest.py"]
    end
    subgraph "libs/langchain"
        lc_pyproject["pyproject.toml\n[tool.pytest.ini_options]"]
        lc_conftest["tests/unit_tests/conftest.py"]
    end
    core_pyproject -->|"declares markers\nrequires, compile"| M1["Marker Registry"]
    v1_pyproject -->|"declares markers\nrequires, compile, scheduled"| M1
    lc_pyproject -->|"declares markers\nrequires, compile, scheduled"| M1
    lc_conftest -->|"pytest_addoption\npytest_collection_modifyitems"| Hooks["Pytest Hook Implementations"]
    v1_conftest -->|"same hooks"| Hooks
```

Sources: [libs/core/pyproject.toml:141-149](), [libs/langchain/pyproject.toml:225-237](), [libs/langchain_v1/pyproject.toml:185-197](), [libs/langchain/tests/unit_tests/conftest.py:1-99]()

---

## `[tool.pytest.ini_options]` Across Packages

The table below summarizes the key differences in pytest configuration per package.

| Setting | `langchain-core` | `langchain` | `langchain_v1` |
|---|---|---|---|
| `addopts` | `--snapshot-warn-unused --strict-markers --strict-config --durations=5` | same + `-vv` | same + `-vv` |
| `asyncio_mode` | `auto` | `auto` | `auto` |
| `asyncio_default_fixture_loop_scope` | `function` | _(not set)_ | _(not set)_ |
| Markers | `requires`, `compile` | `requires`, `compile`, `scheduled` | `requires`, `compile`, `scheduled` |
| Filtered warnings | `LangChainBetaWarning` | `LangChainBetaWarning`, `LangChainDeprecationWarning`, `LangChainPendingDeprecationWarning` | same as `langchain` |

Sources: [libs/core/pyproject.toml:141-149](), [libs/langchain/pyproject.toml:225-237](), [libs/langchain_v1/pyproject.toml:185-197]()

### `--strict-markers`

All packages use `--strict-markers`, meaning any test decorated with an unregistered marker will cause pytest to error at collection time. Every marker must be explicitly declared in `[tool.pytest.ini_options]` under `markers`.

### `--strict-config`

Causes pytest to error if unknown `[tool.pytest.ini_options]` keys are found in the config. This prevents silent misconfigurations.

### `asyncio_mode = "auto"`

All packages use `pytest-asyncio` in `auto` mode — async test functions do not require explicit `@pytest.mark.asyncio` decoration.

---

## Registered Pytest Markers

**Marker-to-purpose diagram:**

```mermaid
graph LR
    requires["@pytest.mark.requires(\"pkg\")"]
    compile_m["@pytest.mark.compile"]
    scheduled["@pytest.mark.scheduled"]

    requires -->|"skip if pkg not importable"| pytest_collection_modifyitems
    compile_m -->|"used by _compile_integration_test.yml\npytest -m compile"| CI["CI Compile Check"]
    scheduled -->|"filtered in scheduled CI runs"| ScheduledCI["Scheduled Testing Jobs"]
```

Sources: [libs/langchain/pyproject.toml:227-231](), [libs/langchain_v1/pyproject.toml:187-191](), [libs/core/pyproject.toml:143-146](), [.github/workflows/_compile_integration_test.yml:52-53]()

| Marker | Packages | Purpose |
|---|---|---|
| `requires` | core, langchain, langchain_v1, partners | Skip a test if a named Python package is not installed |
| `compile` | core, langchain, langchain_v1, partners | Placeholder marker for integration tests; used to verify tests can be imported without running them |
| `scheduled` | langchain, langchain_v1 | Marks tests that should only run during scheduled (nightly) CI |

---

## `conftest.py` Patterns

### Location

Each test subdirectory can have its own `conftest.py`. The primary one for custom hook implementations lives at:

- [libs/langchain/tests/unit_tests/conftest.py]()

An equivalent is present in `langchain_v1`.

### `pytest_addoption`

[libs/langchain/tests/unit_tests/conftest.py:9-28]()

Adds three command-line flags to pytest:

| Flag | Type | Default | Effect |
|---|---|---|---|
| `--only-extended` | `store_true` | `False` | Only run tests that have a `requires` marker |
| `--only-core` | `store_true` | `False` | Only run tests with no `requires` marker |
| `--community` | `store_true` | `False` | Enable tests marked with `community` keyword |

These flags are mutually exclusive: passing both `--only-extended` and `--only-core` raises a `ValueError`.

### `pytest_collection_modifyitems`

[libs/langchain/tests/unit_tests/conftest.py:31-99]()

This hook runs after test collection and handles three behaviors:

**1. `requires` marker — package availability check**

```
@pytest.mark.requires("some_package")
def test_something(): ...
```

For each test with this marker, the hook calls `importlib.util.find_spec(pkg)` for each named package. If any package is not installed:
- Default behavior: the test is skipped with reason `Requires pkg: \`{pkg}\``
- With `--only-extended`: `pytest.fail()` is called (the package should be present)
- With `--only-core`: the test is skipped regardless

Results of `find_spec` are cached in `required_pkgs_info: dict[str, bool]` to avoid repeated lookups.

**2. `community` keyword — opt-in community tests**

Tests tagged with `community` in their keywords are skipped unless `--community` is passed.

**3. `--only-extended` / `--only-core` filter**

- `--only-core`: Any test that has a `requires` marker is skipped.
- `--only-extended`: Any test without a `requires` marker is skipped.

**Flow diagram for `pytest_collection_modifyitems`:**

```mermaid
flowchart TD
    Start["For each collected test item"]
    CheckCommunity{"has 'community' keyword\nand --community not set?"}
    SkipCommunity["add skip marker"]
    CheckRequires{"has 'requires' marker?"}
    CheckOnlyCore{"--only-core set?"}
    SkipCore["skip: not a core test"]
    CheckPkgInstalled{"all required\npackages installed?"}
    CheckOnlyExt{"--only-extended set?"}
    FailExt["pytest.fail()"]
    SkipMissing["skip: Requires pkg"]
    CheckOnlyExtNoReq{"--only-extended set\nand no requires marker?"}
    SkipNotExt["skip: not an extended test"]
    Pass["test runs normally"]

    Start --> CheckCommunity
    CheckCommunity -->|yes| SkipCommunity
    CheckCommunity -->|no| CheckRequires
    CheckRequires -->|yes| CheckOnlyCore
    CheckOnlyCore -->|yes| SkipCore
    CheckOnlyCore -->|no| CheckPkgInstalled
    CheckPkgInstalled -->|yes| Pass
    CheckPkgInstalled -->|no| CheckOnlyExt
    CheckOnlyExt -->|yes| FailExt
    CheckOnlyExt -->|no| SkipMissing
    CheckRequires -->|no| CheckOnlyExtNoReq
    CheckOnlyExtNoReq -->|yes| SkipNotExt
    CheckOnlyExtNoReq -->|no| Pass
```

Sources: [libs/langchain/tests/unit_tests/conftest.py:31-99]()

---

## Dependency Enforcement Tests

[libs/langchain/tests/unit_tests/test_dependencies.py]()

These unit tests act as a guard against accidentally adding new required or test dependencies to `libs/langchain/pyproject.toml`.

### `test_required_dependencies`

Reads `pyproject.toml` via the `uv_conf` fixture, parses `project.dependencies`, and asserts the exact set of required package names matches a hardcoded allowlist:

```
PyYAML, SQLAlchemy, async-timeout, langchain-core,
langchain-text-splitters, langsmith, pydantic, requests
```

### `test_test_group_dependencies`

Reads `dependency-groups.test` from `pyproject.toml` and asserts the exact set of test-group package names. This prevents contributors from adding non-infrastructure packages (e.g. `boto3`, `azure`) to the test group.

### `uv_conf` fixture

[libs/langchain/tests/unit_tests/test_dependencies.py:16-20]()

A session-scoped pytest fixture that reads and returns the parsed `pyproject.toml` as a dict. The fixture is parameterless and loads the file relative to the test file's location via `pathlib.Path`.

---

## Minimum-Version Testing

The CI system tests each package against both the current and the minimum allowed versions of key dependencies. This catches regressions where code works with the latest dependencies but breaks with versions at the lower bound of the declared specifier.

### `get_min_versions.py`

[.github/scripts/get_min_versions.py]()

This script accepts a `pyproject.toml` path, a context (`pull_request` or `release`), and a Python version string. It returns a space-separated string of `package==version` pinned to the minimum compatible version.

**Key functions:**

| Function | Purpose |
|---|---|
| `get_pypi_versions(package_name)` | Fetches all published versions from PyPI JSON API |
| `get_minimum_version(package_name, spec_string)` | Returns the lowest published version satisfying the specifier |
| `get_min_version_from_toml(toml_path, versions_for, python_version)` | Orchestrates the above for all packages in `MIN_VERSION_LIBS` |

**`MIN_VERSION_LIBS`** — the packages for which minimum versions are always checked:

```
langchain-core, langchain, langchain-text-splitters, numpy, SQLAlchemy
```

**`SKIP_IF_PULL_REQUEST`** — packages skipped during PR checks (only tested on release), because simultaneous development across packages would otherwise cause false failures:

```
langchain-core, langchain-text-splitters, langchain
```

### How the Script Is Invoked in CI

**In `_test.yml`** [.github/workflows/_test.yml:56-72]():

```
python .github/scripts/get_min_versions.py pyproject.toml pull_request {python_version}
```

The output is captured as `min-versions`. If non-empty, `uv pip install --force-reinstall $MIN_VERSIONS` is run and then `make tests` is executed again.

**In `_release.yml`** [.github/workflows/_release.yml:317-336]():

Same logic but uses `release` context — so `langchain-core` and friends are also tested at their minimum versions.

**Minimum-version testing flow:**

```mermaid
sequenceDiagram
    participant CI as "_test.yml"
    participant Script as "get_min_versions.py"
    participant PyPI as "PyPI JSON API"
    participant Make as "make tests"

    CI->>Script: "pyproject.toml pull_request 3.11"
    Script->>PyPI: "GET /pypi/{package}/json"
    PyPI-->>Script: "list of versions"
    Script-->>CI: "numpy==1.26.4 SQLAlchemy==1.4.0 ..."
    CI->>Make: "uv pip install --force-reinstall {min_versions}"
    CI->>Make: "make tests"
    Make-->>CI: "pass or fail"
```

Sources: [.github/scripts/get_min_versions.py](), [.github/workflows/_test.yml:56-72](), [.github/workflows/_release.yml:317-336]()

---

## Test Plugin Dependencies

The `test` dependency group in each package specifies which pytest plugins are used. The table below lists the plugins consistently used across core packages.

| Plugin | Purpose |
|---|---|
| `pytest-asyncio` | `asyncio_mode = "auto"` — runs async tests without explicit markers |
| `pytest-mock` | `mocker` fixture for mocking |
| `pytest-socket` | Network socket blocking in unit tests |
| `pytest-xdist` | Parallel test execution with `-n` flag |
| `syrupy` | Snapshot testing (`--snapshot-warn-unused`) |
| `pytest-watcher` | File-watching re-runner for development |
| `freezegun` | Time mocking in tests |
| `blockbuster` | Detects blocking calls in async code (used in `langchain_v1`) |
| `pytest-benchmark` / `pytest-codspeed` | Performance benchmarking (used in `langchain-core`) |

Sources: [libs/core/pyproject.toml:60-77](), [libs/langchain/pyproject.toml:66-91](), [libs/langchain_v1/pyproject.toml:62-75]()

---

## Summary: Marker and Option Flow

```mermaid
graph TD
    subgraph "pyproject.toml"
        MarkerDecl["markers = [requires, compile, scheduled]"]
        AddOpts["addopts = --strict-markers --strict-config ..."]
    end

    subgraph "conftest.py"
        AddOption["pytest_addoption()\n--only-extended\n--only-core\n--community"]
        ModifyItems["pytest_collection_modifyitems()\nskip / fail logic"]
    end

    subgraph "Test Files"
        RequiresMark["@pytest.mark.requires(\"pkg\")"]
        CompileMark["@pytest.mark.compile"]
        ScheduledMark["@pytest.mark.scheduled"]
    end

    subgraph "CI Workflows"
        TestYml["_test.yml: make test"]
        CompileYml["_compile_integration_test.yml: pytest -m compile"]
        ScheduledJob["scheduled jobs"]
    end

    MarkerDecl --> ModifyItems
    AddOption --> ModifyItems
    RequiresMark --> ModifyItems
    CompileMark --> CompileYml
    ScheduledMark --> ScheduledJob
    ModifyItems --> TestYml
```

Sources: [libs/langchain/tests/unit_tests/conftest.py](), [libs/core/pyproject.toml:141-149](), [libs/langchain/pyproject.toml:225-237](), [.github/workflows/_compile_integration_test.yml:52-53]()

# CI/CD and Testing Infrastructure




This page documents the CI/CD workflow architecture for the LangChain monorepo, focusing on how `check_diffs.yml` orchestrates test execution, how `check_diff.py` performs dependency analysis and generates dynamic test matrices, and how reusable workflows (`_lint.yml`, `_test.yml`, `_test_pydantic.yml`, `_compile_integration_test.yml`) execute tests efficiently.

For information about the specific test suites and testing patterns (e.g., `ChatModelIntegrationTests`, VCR caching), see page 5.1 (Standard Testing Framework). This page focuses on the CI orchestration layer.

---

## Overview

The CI/CD system optimizes test execution in a monorepo environment where changes to core packages affect multiple dependent packages. The architecture consists of:

1. **`check_diffs.yml`**: Main workflow that detects changes and orchestrates all CI jobs
2. **`check_diff.py`**: Python script that analyzes dependencies and generates test matrices
3. **Reusable workflows**: Modular workflow files for linting, testing, and compilation
4. **`get_min_versions.py`**: Resolves minimum compatible dependency versions
5. **Dependency groups**: Organized via `[dependency-groups]` in `pyproject.toml`

**Key optimizations:**
- Tests only affected packages based on file changes
- Includes dependent packages automatically when core components change
- Validates against minimum supported dependency versions
- Tests across Python 3.10-3.14 and Pydantic 2.x versions
- Caches dependencies per package and Python version

**Sources:** [.github/workflows/check_diffs.yml:1-262](), [.github/scripts/check_diff.py:1-341]()

---

## Smart Test Selection System

### Architecture Overview

The smart test selection system analyzes git diffs to determine which directories need testing, linting, or building. This optimization is critical for CI performance in a monorepo with 15+ packages.

**Diagram: Smart Test Selection Pipeline - Function Call Flow**

```mermaid
graph TB
    subgraph "Triggering Events"
        PR["Pull Request"]
        Push["Push to master"]
        MergeGroup["Merge Group"]
    end
    
    subgraph "Change Detection (check_diffs.yml)"
        GetFiles["Ana06/get-changed-files@v2.3.0<br/>outputs.all → files list"]
        CheckDiffScript["check_diff.py script<br/>sys.argv[1:] = files"]
    end
    
    subgraph "Dependency Analysis (check_diff.py)"
        DependentsGraph["dependents_graph()<br/>→ dict[str, set[str]]"]
        AllPackageDirs["all_package_dirs()<br/>→ Set[str]"]
        AddDependents["add_dependents(dirs_to_eval, dependents)<br/>→ List[str]"]
    end
    
    subgraph "dirs_to_run Dict Construction"
        DirsToRun["dirs_to_run: Dict[str, set]<br/>keys: 'lint', 'test',<br/>'extended-test', 'codspeed'"]
    end
    
    subgraph "Matrix Generation Functions"
        GetConfigsMulti["_get_configs_for_multi_dirs(<br/>job: str,<br/>dirs_to_run: Dict[str, Set[str]],<br/>dependents: dict)<br/>→ List[Dict[str, str]]"]
        GetConfigsSingle["_get_configs_for_single_dir(<br/>job: str, dir_: str)<br/>→ List[Dict[str, str]]"]
        GetPydanticConfigs["_get_pydantic_test_configs(<br/>dir_: str, python_version: str)<br/>→ List[Dict[str, str]]"]
    end
    
    subgraph "GitHub Actions Output"
        MatrixOutput["map_job_to_configs dict<br/>printed as: job=JSON<br/>to GITHUB_OUTPUT"]
    end
    
    PR --> GetFiles
    Push --> GetFiles
    MergeGroup --> GetFiles
    
    GetFiles --> CheckDiffScript
    CheckDiffScript --> DependentsGraph
    CheckDiffScript --> AllPackageDirs
    CheckDiffScript --> DirsToRun
    
    DependentsGraph --> AddDependents
    DirsToRun --> AddDependents
    AddDependents --> GetConfigsMulti
    GetConfigsMulti --> GetConfigsSingle
    GetConfigsMulti --> GetPydanticConfigs
    
    GetConfigsMulti --> MatrixOutput
```

**Sources:** [.github/workflows/check_diffs.yml:44-70](), [.github/scripts/check_diff.py:225-341]()

### Dependency Graph Construction

The `dependents_graph()` function at [.github/scripts/check_diff.py:63-113]() constructs a mapping of package → dependents by parsing all `pyproject.toml` files and `extended_testing_deps.txt` files.

**Diagram: `dependents_graph()` Function Implementation**

```mermaid
graph TB
    GlobPattern["glob.glob('./libs/**/pyproject.toml',<br/>recursive=True)<br/>Skip: 'template' in path"]
    
    LoadToml["with open(path, 'rb') as f:<br/>pyproject = tomllib.load(f)"]
    ExtractPkgDir["pkg_dir = 'libs' +<br/>/libs[1].split('/')[:-1]"]
    ParseProjectDeps["pyproject['project']['dependencies']<br/>→ List[str]"]
    ParseDepGroups["pyproject['dependency-groups']['test']<br/>→ List[str]"]
    ParseExtDeps["extended_testing_deps.txt<br/>Parse: '-e ../partners/{name}'<br/>→ 'langchain-{partner}'"]
    
    ReqParsing["for dep in dependencies:<br/>requirement = Requirement(dep)<br/>package_name = requirement.name"]
    
    BuildGraph["if 'langchain' in dep:<br/>dependents[package_name].add(pkg_dir)"]
    
    Filter["for partner in IGNORED_PARTNERS:<br/>dependents[k].remove(<br/>f'libs/partners/{partner}')"]
    
    Output["return dependents<br/>Type: defaultdict[str, set[str]]<br/>Example: {'langchain-core':<br/>{'libs/langchain', 'libs/text-splitters'}}"]
    
    GlobPattern --> LoadToml
    LoadToml --> ExtractPkgDir
    ExtractPkgDir --> ParseProjectDeps
    ExtractPkgDir --> ParseDepGroups
    ExtractPkgDir --> ParseExtDeps
    
    ParseProjectDeps --> ReqParsing
    ParseDepGroups --> ReqParsing
    ParseExtDeps --> ReqParsing
    
    ReqParsing --> BuildGraph
    BuildGraph --> Filter
    Filter --> Output
```

**Implementation details:**

- **Package discovery**: `glob.glob("./libs/**/pyproject.toml", recursive=True)` at [.github/scripts/check_diff.py:70]() with exclusions at line 59: `if "libs/cli" not in path and "libs/standard-tests" not in path`
- **Template filtering**: `if "template" in path: continue` at [.github/scripts/check_diff.py:72]()
- **Package directory extraction**: `pkg_dir = "libs" + "/".join(path.split("libs")[1].split("/")[:-1])` at [.github/scripts/check_diff.py:78]()
- **Dependency parsing**: `requirement = Requirement(dep)` from `packaging.requirements` at [.github/scripts/check_diff.py:83-84]()
- **Langchain filtering**: `if "langchain" in dep:` at [.github/scripts/check_diff.py:85]() - only tracks LangChain packages as dependencies
- **Editable dependencies**: Parses `-e ../partners/{partner}` format at [.github/scripts/check_diff.py:96-102](), converts to `langchain-{partner}`
- **Partner filtering**: `IGNORED_PARTNERS = ["huggingface", "prompty"]` at [.github/scripts/check_diff.py:44-52](), removed via loop at lines 109-112
- **Return type**: `defaultdict(set)` initialized at [.github/scripts/check_diff.py:68]()

**Sources:** [.github/scripts/check_diff.py:63-113]()

### File-to-Package Mapping

The script maps changed files to affected packages using path-based rules:

| File Pattern | Action | Packages Affected |
|-------------|--------|------------------|
| `.github/workflows/*`, `.github/actions/*`, `.github/scripts/check_diff.py` | `dirs_to_run["extended-test"].update(LANGCHAIN_DIRS)` | `libs/core`, `libs/text-splitters`, `libs/langchain`, `libs/langchain_v1` |
| `libs/core/*` | `dirs_to_run["codspeed"].add("libs/core")` | `libs/core` (+ dependents if not `IGNORE_CORE_DEPENDENTS=False`) |
| `libs/standard-tests/*` | Add to `dirs_to_run["lint"]` and `dirs_to_run["test"]` | `libs/partners/mistralai`, `libs/partners/openai`, `libs/partners/anthropic`, `libs/partners/fireworks`, `libs/partners/groq` |
| `libs/partners/{partner}/*` | `dirs_to_run["test"].add(f"libs/partners/{partner}")` | `libs/partners/{partner}` |
| `libs/cli/*` | `dirs_to_run["lint"].add("libs/cli")` and `dirs_to_run["test"].add("libs/cli")` | `libs/cli` |

**Special handling for `LANGCHAIN_DIRS` list:**

When files change in core packages (`libs/core`, `libs/text-splitters`, `libs/langchain`, `libs/langchain_v1`), the script adds that directory and all subsequent directories in the list to extended tests. This ensures cascading dependency testing.

**Sources:** [.github/scripts/check_diff.py:242-314]()

### Matrix Configuration Generation

For each job type, the `_get_configs_for_single_dir(job: str, dir_: str)` function at [.github/scripts/check_diff.py:129-143]() generates a matrix of configurations specifying `working-directory` and `python-version`:

```python
# From _get_configs_for_single_dir() at line 129
if job == "test-pydantic":
    return _get_pydantic_test_configs(dir_)

if job == "codspeed":
    py_versions = ["3.13"]
elif dir_ == "libs/core":
    py_versions = ["3.10", "3.11", "3.12", "3.13", "3.14"]
elif dir_ in {"libs/partners/chroma"}:
    py_versions = ["3.10", "3.13"]
else:
    py_versions = ["3.10", "3.14"]

return [{"working-directory": dir_, "python-version": py_v} for py_v in py_versions]
```

**Pydantic version testing** via `_get_pydantic_test_configs()` at [.github/scripts/check_diff.py:146-198]() generates a more complex matrix:

1. Parse `uv.lock` files to extract `package["version"]` for package with `package["name"] == "pydantic"`
2. Call `get_min_version_from_toml(pyproject_path, "release", python_version, include=["pydantic"])` to get minimum Pydantic version
3. Calculate `min_pydantic_minor = max(int(dir_min_pydantic_minor), int(core_min_pydantic_minor))`
4. Calculate `max_pydantic_minor = min(int(dir_max_pydantic_minor), int(core_max_pydantic_minor))`
5. Generate configs: `[{"working-directory": dir_, "pydantic-version": f"2.{v}.0", "python-version": python_version} for v in range(min_pydantic_minor, max_pydantic_minor + 1)]`

**Sources:** [.github/scripts/check_diff.py:129-198]()

---

## Test Execution Workflows

### Workflow Orchestration in `check_diffs.yml`

The `check_diffs.yml` workflow at [.github/workflows/check_diffs.yml:1-262]() orchestrates all CI jobs:

**Diagram: `check_diffs.yml` Job Orchestration and Dependencies**

```mermaid
graph TB
    build["build job (lines 44-70)<br/>step: Ana06/get-changed-files@v2.3.0<br/>step: python check_diff.py<br/>outputs.lint, outputs.test,<br/>outputs.extended-tests,<br/>outputs.compile-integration-tests,<br/>outputs.test-pydantic,<br/>outputs.codspeed"]
    
    lint["lint job (lines 72-83)<br/>needs: [build]<br/>if: needs.build.outputs.lint != '[]'<br/>uses: ./.github/workflows/_lint.yml<br/>strategy.matrix.job-configs:<br/>fromJson(needs.build.outputs.lint)"]
    
    test["test job (lines 86-97)<br/>needs: [build]<br/>if: needs.build.outputs.test != '[]'<br/>uses: ./.github/workflows/_test.yml<br/>strategy.matrix.job-configs:<br/>fromJson(needs.build.outputs.test)"]
    
    test_pydantic["test-pydantic job (lines 100-111)<br/>needs: [build]<br/>if: needs.build.outputs.test-pydantic != '[]'<br/>uses: ./.github/workflows/_test_pydantic.yml<br/>strategy.matrix.job-configs:<br/>fromJson(needs.build.outputs.test-pydantic)"]
    
    compile_integration["compile-integration-tests job (lines 114-126)<br/>needs: [build]<br/>uses: ./.github/workflows/_compile_integration_test.yml"]
    
    extended["extended-tests job (lines 129-173)<br/>needs: [build]<br/>runs-on: ubuntu-latest<br/>steps:<br/>uv venv<br/>uv sync --group test<br/>uv pip install -r extended_testing_deps.txt<br/>make extended_tests"]
    
    codspeed["codspeed job (lines 175-233)<br/>needs: [build]<br/>if: !contains(labels, 'codspeed-ignore')<br/>uses: CodSpeedHQ/action@v4<br/>run: pytest --codspeed<br/>mode: walltime | instrumentation"]
    
    ci_success["ci_success job (lines 236-261)<br/>needs: [build, lint, test,<br/>compile-integration-tests,<br/>extended-tests, test-pydantic,<br/>codspeed]<br/>if: always()<br/>env.EXIT_CODE:<br/>!contains(needs.*.result, 'failure')"]
    
    build --> lint
    build --> test
    build --> test_pydantic
    build --> compile_integration
    build --> extended
    build --> codspeed
    
    lint --> ci_success
    test --> ci_success
    test_pydantic --> ci_success
    compile_integration --> ci_success
    extended --> ci_success
    codspeed --> ci_success
```

**Concurrency control** at [.github/workflows/check_diffs.yml:30-32]():
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

Cancels in-progress runs when new commits are pushed to the same PR, optimizing CI resource usage.

**Sources:** [.github/workflows/check_diffs.yml:14-262]()

### Lint Workflow (`_lint.yml`)

The `_lint.yml` reusable workflow at [.github/workflows/_lint.yml:1-82]() runs quality checks using `ruff` and `mypy`:

**Diagram: `_lint.yml` Step-by-Step Execution Flow**

```mermaid
graph TB
    checkout["Step: Checkout Code (line 41)<br/>uses: actions/checkout@v6"]
    
    uv_setup["Step: Set up Python + UV (line 43)<br/>uses: ./.github/actions/uv_setup<br/>with.python-version: inputs.python-version<br/>with.cache-suffix: lint-{working-directory}<br/>with.working-directory: inputs.working-directory"]
    
    sync_lint["Step: Install Lint & Typing Dependencies (line 56)<br/>run: uv sync --group lint --group typing<br/>working-directory: inputs.working-directory"]
    
    lint_package["Step: Analyze Package Code with Linters (line 61)<br/>run: make lint_package<br/>Makefile targets:<br/>ruff check, ruff format --check, mypy"]
    
    sync_test["Step: Install Test Dependencies (line 66/72)<br/>if: !startsWith('libs/partners/')<br/>run: uv sync --inexact --group test<br/>elif: startsWith('libs/partners/')<br/>run: uv sync --inexact --group test<br/>--group test_integration"]
    
    lint_tests["Step: Analyze Test Code with Linters (line 78)<br/>run: make lint_tests<br/>Makefile targets: ruff check tests/"]
    
    checkout --> uv_setup
    uv_setup --> sync_lint
    sync_lint --> lint_package
    lint_package --> sync_test
    sync_test --> lint_tests
```

**Environment configuration** at [.github/workflows/_lint.yml:25-31]():
```yaml
env:
  RUFF_OUTPUT_FORMAT: github  # Enables inline PR annotations
  UV_FROZEN: "true"            # Respects uv.lock versions
```

**Dependency groups used:**
- `--group lint`: Contains `ruff>=0.14.11,<0.15.0` (see `pyproject.toml`)
- `--group typing`: Contains `mypy>=1.19.1,<1.20.0`, type stubs
- `--group test`: Required for linting test code (imports test utilities)
- `--group test_integration`: Partner packages only, for linting integration tests

**Makefile targets:**
- `lint_package`: Runs `ruff check` and `ruff format --check` on package source
- `lint_tests`: Runs `ruff check` and `ruff format --check` on test code

**Sources:** [.github/workflows/_lint.yml:1-82]()

### Unit Test Workflow (`_test.yml`)

The `_test.yml` reusable workflow at [.github/workflows/_test.yml:1-86]() runs unit tests with both current and minimum dependency versions:

**Diagram: `_test.yml` Step-by-Step Execution with Min Version Testing**

```mermaid
graph TB
    checkout["Step: Checkout Code (line 35)<br/>uses: actions/checkout@v6"]
    
    uv_setup["Step: Set up Python + UV (line 38)<br/>uses: ./.github/actions/uv_setup<br/>id: setup-python<br/>with.python-version: inputs.python-version<br/>with.cache-suffix: test-{working-directory}"]
    
    sync["Step: Install Test Dependencies (line 46)<br/>run: uv sync --group test --dev<br/>env.UV_FROZEN=true<br/>env.UV_NO_SYNC=true"]
    
    make_test["Step: Run Core Unit Tests (line 50)<br/>run: make test<br/>Makefile target: pytest tests/unit_tests"]
    
    calc_min["Step: Calculate Minimum Dependency Versions (line 55)<br/>id: min-version<br/>run: python get_min_versions.py<br/>pyproject.toml pull_request {python_version}<br/>output: steps.min-version.outputs.min-versions"]
    
    check_empty{"if: steps.min-version.outputs.min-versions != ''<br/>(line 67)"}
    
    install_min["Step: Run Tests with Minimum Dependencies (line 66)<br/>env.MIN_VERSIONS: steps.min-version.outputs.min-versions<br/>run: VIRTUAL_ENV=.venv uv pip install MIN_VERSIONS"]
    
    make_tests_min["run: make tests<br/>Makefile target: pytest"]
    
    git_status["Step: Verify Clean Working Directory (line 75)<br/>run: git status | grep 'nothing to commit'"]
    
    checkout --> uv_setup
    uv_setup --> sync
    sync --> make_test
    make_test --> calc_min
    calc_min --> check_empty
    check_empty -->|Yes| install_min
    check_empty -->|No| git_status
    install_min --> make_tests_min
    make_tests_min --> git_status
```

**Key implementation details:**

- **Dual testing strategy**: Tests with current `uv.lock` versions at [.github/workflows/_test.yml:46-53](), then with minimum versions at [.github/workflows/_test.yml:66-73]()
- **Timeout**: `timeout-minutes: 20` on `ubuntu-latest` runner
- **Environment**: `UV_FROZEN="true"` (respect lockfile), `UV_NO_SYNC="true"` (skip auto-sync) at [.github/workflows/_test.yml:22-23]()
- **Conditional min version testing**: Only runs if `steps.min-version.outputs.min-versions != ''` at [.github/workflows/_test.yml:67]()
- **Dependency group**: `--group test` contains `pytest>=7.0.0,<9.0.0` and other test dependencies

**Sources:** [.github/workflows/_test.yml:1-86]()

### Pydantic Version Testing (`_test_pydantic.yml`)

The `_test_pydantic.yml` reusable workflow at [.github/workflows/_test_pydantic.yml:1-74]() validates compatibility across Pydantic 2.x versions:

**Diagram: `_test_pydantic.yml` Execution Flow**

```mermaid
graph TB
    checkout["actions/checkout@v6"]
    
    uv_setup[".github/actions/uv_setup<br/>python-version: inputs.python-version (default 3.12)<br/>cache-suffix: test-pydantic-{working-directory}"]
    
    sync["uv sync --group test"]
    
    install_pydantic["VIRTUAL_ENV=.venv<br/>uv pip install 'pydantic~=$PYDANTIC_VERSION'<br/>(e.g. pydantic~=2.7.0)"]
    
    make_test["make test"]
    
    git_status["git status<br/>grep 'nothing to commit'"]
    
    checkout --> uv_setup
    uv_setup --> sync
    sync --> install_pydantic
    install_pydantic --> make_test
    make_test --> git_status
```

**Job configuration:**
- **Python version**: Default `3.12` (input `inputs.python-version` at [.github/workflows/_test_pydantic.yml:12-16]())
- **Pydantic version**: Specified by matrix input `inputs.pydantic-version` at [.github/workflows/_test_pydantic.yml:17-20]()

**Installation logic** at [.github/workflows/_test_pydantic.yml:52-56]():
```bash
VIRTUAL_ENV=.venv uv pip install "pydantic~=$PYDANTIC_VERSION"
```

The `~=` operator installs the specified minor version (e.g., `~=2.7.0` allows `>=2.7.0, <2.8.0`).

**Matrix generation:** The matrix is generated by `_get_pydantic_test_configs()` at [.github/scripts/check_diff.py:146-198](), which determines the Pydantic version range from `uv.lock` and `pyproject.toml` minimum versions.

**Sources:** [.github/workflows/_test_pydantic.yml:1-74](), [.github/scripts/check_diff.py:146-198]()

### Integration Test Compilation

The `_compile_integration_test.yml` workflow verifies that integration tests can be imported without syntax errors:

```bash
uv run pytest -m compile tests/integration_tests
```

This catches issues like:
- Import errors
- Syntax errors
- Missing dependencies
- Typos in test files

**Sources:** [.github/workflows/_compile_integration_test.yml:1-66]()

### Extended Tests

Extended tests run for core packages (`libs/core`, `libs/text-splitters`, `libs/langchain`, `libs/langchain_v1`) and install additional dependencies:

```bash
uv venv
uv sync --group test
VIRTUAL_ENV=.venv uv pip install -r extended_testing_deps.txt
VIRTUAL_ENV=.venv make extended_tests
```

**Purpose:** Tests requiring additional dependencies beyond standard test group. Examples:
- Partner package integrations (via `-e ../partners/{name}` in `extended_testing_deps.txt`)
- Specific database drivers or optional backends
- Features requiring heavy external dependencies

**Extended test invocation:**
```bash
VIRTUAL_ENV=.venv make extended_tests
# Typically runs: pytest tests/unit_tests with extended deps available
```

**Sources:** [.github/workflows/check_diffs.yml:129-173]()

### CodSpeed Benchmarks

CodSpeed benchmarks run on packages with changed files (unless labeled `codspeed-ignore`):

```bash