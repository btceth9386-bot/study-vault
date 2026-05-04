def _get_pydantic_test_configs(dir_: str, *, python_version: str = "3.12"):
    # Read uv.lock files to get max versions
    with open("./libs/core/uv.lock", "rb") as f:
        core_uv_lock_data = tomllib.load(f)
    for package in core_uv_lock_data["package"]:
        if package["name"] == "pydantic":
            core_max_pydantic_minor = package["version"].split(".")[1]
            break
    
    with open(f"./{dir_}/uv.lock", "rb") as f:
        dir_uv_lock_data = tomllib.load(f)
    for package in dir_uv_lock_data["package"]:
        if package["name"] == "pydantic":
            dir_max_pydantic_minor = package["version"].split(".")[1]
            break
    
    # Get min versions from pyproject.toml constraints
    core_min_pydantic_version = get_min_version_from_toml(
        "./libs/core/pyproject.toml", "release", python_version, include=["pydantic"]
    )["pydantic"]
    dir_min_pydantic_version = get_min_version_from_toml(
        f"./{dir_}/pyproject.toml", "release", python_version, include=["pydantic"]
    ).get("pydantic", "0.0.0")
    
    # Calculate intersection of version ranges
    max_pydantic_minor = min(int(dir_max_pydantic_minor), int(core_max_pydantic_minor))
    min_pydantic_minor = max(int(dir_min_pydantic_minor), int(core_min_pydantic_minor))
    
    # Generate test configs for each minor version
    configs = [
        {"working-directory": dir_, "pydantic-version": f"2.{v}.0", "python-version": python_version}
        for v in range(min_pydantic_minor, max_pydantic_minor + 1)
    ]
    return configs
```

The workflow then installs each Pydantic version with `uv pip install "pydantic~=$PYDANTIC_VERSION"` ([.github/workflows/_test_pydantic.yml:56]()) and runs `make test`.

**Sources**: [.github/scripts/check_diff.py:146-198](), [.github/workflows/_test_pydantic.yml:52-61]()

### Integration Test Compilation

The `_compile_integration_test.yml` workflow ([.github/workflows/_compile_integration_test.yml:9]()) runs `pytest -m compile tests/integration_tests` ([.github/workflows/_compile_integration_test.yml:53]()) to verify tests compile without executing them. The `compile` marker is registered in `pyproject.toml`:

```toml
# From libs/standard-tests/pyproject.toml
[tool.pytest.ini_options]
markers = [
    "requires: mark tests as requiring a specific library",
    "scheduled: mark tests to run in scheduled testing",
    "compile: mark placeholder test used to compile integration tests without running them",
]
```

Integration test files include a placeholder test to enable compilation:

```python