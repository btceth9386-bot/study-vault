class TestChatParrotLinkUnit(ChatModelUnitTests):
    @property
    def chat_model_class(self) -> type[ChatParrotLink]:
        return ChatParrotLink
    
    @property
    def chat_model_params(self) -> dict:
        return {"model": "bird-brain-001", "temperature": 0}
    
    # Inherits test methods from ChatModelUnitTests:
    # - test_init() - validates model initialization
    # - test_serialize() - validates model serialization with dumpd/load
    # - test_standard_params() - validates temperature, max_tokens, etc.
    # - test_bind_tool_pydantic() - validates tool binding
    # - test_anthropic_inputs_with_tools() - validates Anthropic content blocks

class TestChatParrotLinkIntegration(ChatModelIntegrationTests):
    @property
    def chat_model_class(self) -> type[ChatParrotLink]:
        return ChatParrotLink
    
    # Inherits integration test methods:
    # - test_invoke() - validates model.invoke("Hello") returns AIMessage
    # - test_stream() - validates streaming with AIMessageChunk
    # - test_invoke_with_tool_calling() - validates tool call generation
    # - test_structured_output() - validates with_structured_output()
```

**Sources**: [libs/standard-tests/tests/unit_tests/test_custom_chat_model.py:17-45](), [libs/standard-tests/tests/unit_tests/custom_chat_model.py:18-149](), [libs/standard-tests/langchain_tests/unit_tests/chat_models.py:276-1033](), [libs/standard-tests/langchain_tests/integration_tests/chat_models.py:746-1059]()

## CI/CD Pipeline Architecture

The CI/CD pipeline uses intelligent change detection via the `check_diffs.yml` workflow ([.github/workflows/check_diffs.yml:15]()) and `check_diff.py` script ([.github/scripts/check_diff.py:1-341]()) to minimize test execution time while maintaining comprehensive coverage.

### Change Detection and Test Matrix Generation

Title: CI Workflow Orchestration from check_diffs.yml

```mermaid
graph TB
    subgraph "Trigger Events"
        PR["pull_request event"]
        PUSH["push to master"]
        MERGE["merge_group event"]
    end
    
    subgraph "check_diffs.yml Jobs"
        BUILD["build job:<br/>Ana06/get-changed-files@v2.3.0<br/>check_diff.py $files<br/>Output: JSON matrices"]
        LINT["lint job:<br/>uses: ./.github/workflows/_lint.yml<br/>matrix: fromJson(needs.build.outputs.lint)"]
        TEST["test job:<br/>uses: ./.github/workflows/_test.yml<br/>matrix: fromJson(needs.build.outputs.test)"]
        PYDANTIC["test-pydantic job:<br/>uses: ./.github/workflows/_test_pydantic.yml<br/>matrix: fromJson(needs.build.outputs.test-pydantic)"]
        COMPILE["compile-integration-tests job:<br/>uses: ./.github/workflows/_compile_integration_test.yml"]
        EXTENDED["extended-tests job:<br/>uv sync --group test<br/>uv pip install -r extended_testing_deps.txt"]
        CODSPEED["codspeed job:<br/>CodSpeedHQ/action@v4<br/>pytest --codspeed"]
        SUCCESS["ci_success job:<br/>needs: [build, lint, test,...]<br/>Exit code based on all results"]
    end
    
    PR --> BUILD
    PUSH --> BUILD
    MERGE --> BUILD
    
    BUILD -->|"outputs.lint != '[]'"| LINT
    BUILD -->|"outputs.test != '[]'"| TEST
    BUILD -->|"outputs.test-pydantic != '[]'"| PYDANTIC
    BUILD -->|"outputs.compile-integration-tests != '[]'"| COMPILE
    BUILD -->|"outputs.extended-tests != '[]'"| EXTENDED
    BUILD -->|"outputs.codspeed != '[]' && !codspeed-ignore"| CODSPEED
    
    LINT --> SUCCESS
    TEST --> SUCCESS
    PYDANTIC --> SUCCESS
    COMPILE --> SUCCESS
    EXTENDED --> SUCCESS
    CODSPEED --> SUCCESS
```

**Sources**: [.github/workflows/check_diffs.yml:15-262](), [.github/scripts/check_diff.py:1-341]()

### Dependency Graph Construction

The `dependents_graph()` function ([.github/scripts/check_diff.py:63-113]()) parses `pyproject.toml` and `extended_testing_deps.txt` to build a dependency map. The `add_dependents()` function ([.github/scripts/check_diff.py:116-126]()) then expands the test matrix to include all dependent packages.

Title: Dependency Graph Construction in check_diff.py

```mermaid
graph LR
    subgraph "dependents_graph() Function"
        GLOB["glob.glob('./libs/**/pyproject.toml')"]
        PARSE_TOML["tomllib.load(f)<br/>pyproject['project']['dependencies']<br/>pyproject['dependency-groups']['test']"]
        PARSE_EXT["Read extended_testing_deps.txt<br/>Extract -e ../partners/* deps"]
        BUILD_GRAPH["defaultdict(set)<br/>dependents['langchain-core'] = {'libs/core', ...}"]
    end
    
    subgraph "Changed Files Processing"
        FILES["sys.argv[1:] file list<br/>from Ana06/get-changed-files"]
        MAP_DIRS["Map files to dirs:<br/>libs/core, libs/partners/openai, etc."]
    end
    
    subgraph "add_dependents() Function"
        EXPAND["For each dir in dirs_to_eval:<br/>pkg = 'langchain-' + dir.split('/')[-1]<br/>updated.update(dependents[pkg])"]
        SKIP_CORE["if 'core' in dir and IGNORE_CORE_DEPENDENTS:<br/>skip expansion"]
    end
    
    subgraph "_get_configs_for_multi_dirs()"
        GEN_CONFIGS["For each dir:<br/>_get_configs_for_single_dir(job, dir)<br/>Returns list of dicts with<br/>working-directory, python-version"]
    end
    
    GLOB --> PARSE_TOML
    PARSE_TOML --> BUILD_GRAPH
    PARSE_EXT --> BUILD_GRAPH
    
    FILES --> MAP_DIRS
    MAP_DIRS --> EXPAND
    BUILD_GRAPH --> EXPAND
    EXPAND --> SKIP_CORE
    SKIP_CORE --> GEN_CONFIGS
```

**Sources**: [.github/scripts/check_diff.py:63-113](), [.github/scripts/check_diff.py:116-126](), [.github/scripts/check_diff.py:201-223]()

### Test Matrix Dimensions

The CI pipeline tests across multiple dimensions:

| Dimension | Configuration | Source |
|-----------|--------------|--------|
| **Python versions** | `libs/core`: 3.10, 3.11, 3.12, 3.13, 3.14<br/>Other packages: 3.10, 3.14 | [.github/scripts/check_diff.py:135-143]() |
| **Pydantic versions** | Range determined from `uv.lock` min/max versions | [.github/scripts/check_diff.py:146-199]() |
| **Dependency versions** | Current from `uv.lock` + minimum from constraints | [.github/scripts/get_min_versions.py:1-200]() |
| **Extended deps** | Optional dependencies in `extended_testing_deps.txt` | [.github/workflows/check_diffs.yml:153-160]() |

**Sources**: [.github/scripts/check_diff.py:129-199](), [.github/scripts/get_min_versions.py:20-35]()

## Test Execution Workflows

### Unit Testing with Minimum Dependencies

The `_test.yml` workflow ([.github/workflows/_test.yml:4]()) runs `make test` twice: once with current dependencies from `uv.lock`, then again with minimum supported versions calculated by `get_min_versions.py`.

Title: Unit Test Workflow with Minimum Version Testing

```mermaid
graph TB
    subgraph "Setup Phase"
        CHECKOUT["actions/checkout@v6"]
        UV_SETUP["./.github/actions/uv_setup<br/>inputs: python-version, cache-suffix"]
        INSTALL["uv sync --group test --dev"]
    end
    
    subgraph "Test with Current Dependencies"
        TEST_CURR["make test<br/>(runs: uv run pytest tests/unit_tests)"]
    end
    
    subgraph "Calculate Minimum Versions"
        MIN_CALC["get_min_versions.py<br/>pyproject.toml pull_request $python_version"]
        MIN_LIBS["MIN_VERSION_LIBS = [<br/>'langchain-core',<br/>'langchain',<br/>'langchain-text-splitters',<br/>'numpy',<br/>'SQLAlchemy']"]
        GET_PYPI["get_pypi_versions(package_name)<br/>requests.get(f'https://pypi.org/pypi/{package_name}/json')"]
        FIND_MIN["get_minimum_version(pkg, spec_string)<br/>SpecifierSet.contains(version)"]
        OUTPUT["echo 'min-versions=langchain-core==1.2.2 ...'"]
    end
    
    subgraph "Test with Minimum Dependencies"
        INSTALL_MIN["VIRTUAL_ENV=.venv uv pip install<br/>--force-reinstall $MIN_VERSIONS"]
        TEST_MIN["make tests"]
    end
    
    VERIFY["git status check:<br/>grep 'nothing to commit, working tree clean'"]
    
    CHECKOUT --> UV_SETUP
    UV_SETUP --> INSTALL
    INSTALL --> TEST_CURR
    TEST_CURR --> MIN_CALC
    MIN_CALC --> MIN_LIBS
    MIN_LIBS --> GET_PYPI
    GET_PYPI --> FIND_MIN
    FIND_MIN --> OUTPUT
    OUTPUT --> INSTALL_MIN
    INSTALL_MIN --> TEST_MIN
    TEST_MIN --> VERIFY
```

**Sources**: [.github/workflows/_test.yml:1-86](), [.github/scripts/get_min_versions.py:20-92](), [.github/scripts/get_min_versions.py:111-152]()

### Pydantic Version Compatibility Testing

The `_test_pydantic.yml` workflow ([.github/workflows/_test_pydantic.yml:3]()) runs tests against multiple Pydantic 2.x versions. The `_get_pydantic_test_configs()` function ([.github/scripts/check_diff.py:146-198]()) computes the version range:

```python