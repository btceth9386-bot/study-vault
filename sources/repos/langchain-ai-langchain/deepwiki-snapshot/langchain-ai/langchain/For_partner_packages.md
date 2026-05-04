uv run --no-sync pytest ./tests/ --codspeed
```

**Modes:**
- `walltime`: For `libs/core` - measures actual execution time
- `instrumentation`: For partner packages - instruments code for detailed performance data

**Sources:** [.github/workflows/check_diffs.yml:175-233]()

---

## Minimum Version Testing

### Purpose and Strategy

The minimum version testing ensures packages work with the oldest supported dependency versions, preventing accidental requirements creep. This is implemented via `get_min_versions.py` at [.github/scripts/get_min_versions.py:1-200]().

**Targeted libraries** defined in `MIN_VERSION_LIBS` list at [.github/scripts/get_min_versions.py:20-26]():
```python
MIN_VERSION_LIBS = [
    "langchain-core",
    "langchain",
    "langchain-text-splitters",
    "numpy",
    "SQLAlchemy",
]
```

**Testing contexts and filtering:**

| Context | `versions_for` Parameter | Skipped Libraries | Rationale |
|---------|-------------------------|-------------------|-----------|
| Pull requests | `"pull_request"` | `SKIP_IF_PULL_REQUEST = ["langchain-core", "langchain-text-splitters", "langchain"]` | Core libraries may have simultaneous changes requiring coordinated releases |
| Releases | `"release"` | None (empty list) | All libraries in `MIN_VERSION_LIBS` are tested |

**Implementation:** The `get_min_version_from_toml()` function at [.github/scripts/get_min_versions.py:111-152]() checks at line 132:
```python
if versions_for == "pull_request" and lib in SKIP_IF_PULL_REQUEST:
    continue
```

**Sources:** [.github/scripts/get_min_versions.py:20-34](), [.github/scripts/get_min_versions.py:130-135]()

### Version Resolution Algorithm

The `get_minimum_version()` function at [.github/scripts/get_min_versions.py:56-92]() resolves the minimum compatible version from PyPI:

**Diagram: `get_minimum_version()` Function Logic Flow**

```mermaid
graph TB
    input["get_minimum_version(<br/>package_name: str,<br/>spec_string: str)<br/>→ str | None<br/>(line 56)"]
    
    rewrite_caret["Rewrite caret syntax (lines 67-77):<br/>re.sub(r'\^0\.0\.(\d+)', r'0.0.\1')<br/>Loop y in range(1, 10):<br/>re.sub(r'\^0\.{y}\.(\d+)', r'>=0.{y}.\1,<0.{y+1}')<br/>Loop x in range(1, 10):<br/>re.sub(r'\^{x}\.(\d+)\.(\d+)', r'>={x}.\1.\2,<{x+1}')"]
    
    specset["spec_set = SpecifierSet(spec_string)<br/>from packaging.specifiers<br/>(line 79)"]
    
    fetch_pypi["all_versions = get_pypi_versions(package_name)<br/>requests.get(<br/>f'https://pypi.org/pypi/{package_name}/json')<br/>return response.json()['releases'].keys()<br/>(lines 37-53, 80)"]
    
    filter_versions["valid_versions = []<br/>for version_str in all_versions:<br/>version = parse(version_str)<br/>if spec_set.contains(version):<br/>valid_versions.append(version)<br/>(lines 82-90)"]
    
    return_min["return str(min(valid_versions))<br/>if valid_versions else None<br/>(line 92)"]
    
    input --> rewrite_caret
    rewrite_caret --> specset
    specset --> fetch_pypi
    fetch_pypi --> filter_versions
    filter_versions --> return_min
```

**Caret syntax handling** at [.github/scripts/get_min_versions.py:66-77]():

| Input | Rewritten Constraint | Explanation |
|-------|---------------------|-------------|
| `^0.0.5` | `0.0.5` | Exact version for 0.0.x |
| `^0.2.1` | `>=0.2.1,<0.3` | Compatible with 0.2.x |
| `^1.2.3` | `>=1.2.3,<2` | Compatible with 1.x |

**Sources:** [.github/scripts/get_min_versions.py:56-92]()

### Python Version Marker Handling

The `_check_python_version_from_requirement()` function respects `python_version` markers in dependencies:

```python
if "python_version" in marker_str or "python_full_version" in marker_str:
    python_version_str = "".join(
        char for char in marker_str
        if char.isdigit() or char in (".", "<", ">", "=", ",")
    )
    return check_python_version(python_version, python_version_str)
```

**Marker extraction:** Strips non-numeric/operator characters from `marker_str` to extract constraints like `>=3.9,<4.0`

**Validation:** Calls `check_python_version(python_version, python_version_str)` which converts to `Version` and checks against `SpecifierSet`

This ensures dependencies with Python version restrictions (e.g., `dependency; python_version >= "3.9"`) are only included in minimum version calculations for compatible Python versions.

**Sources:** [.github/scripts/get_min_versions.py:94-187]()

---

## Release Pipeline

### 7-Stage Release Workflow

The `_release.yml` workflow implements a secure, multi-stage release pipeline:

```mermaid
graph TB
    Trigger["workflow_dispatch<br/>or workflow_call<br/>inputs: working-directory"]
    
    Build["build job<br/>uv build in working-dir<br/>upload-artifact: dist<br/>outputs: pkg-name, version"]
    
    ReleaseNotes["release-notes job<br/>git log PREV_TAG..HEAD<br/>outputs: release-body"]
    
    TestPyPI["test-pypi-publish job<br/>gh-action-pypi-publish<br/>repository-url: test.pypi.org<br/>skip-existing: true"]
    
    PreRelease["pre-release-checks job<br/>uv pip install dist/*.whl<br/>make tests<br/>get_min_versions.py release<br/>make integration_tests"]
    
    TestCore["test-prior-published-<br/>packages-against-new-core job<br/>matrix: [openai, anthropic]<br/>git checkout LATEST_TAG"]
    
    Publish["publish job<br/>gh-action-pypi-publish<br/>packages-dir: dist/<br/>trusted publishing"]
    
    MarkRelease["mark-release job<br/>ncipollo/release-action<br/>tag: pkg-name==version<br/>makeLatest: if langchain-core"]
    
    Trigger --> Build
    Build --> ReleaseNotes
    ReleaseNotes --> TestPyPI
    TestPyPI --> PreRelease
    PreRelease --> TestCore
    TestCore --> Publish
    Publish --> MarkRelease
```

**Sources:** [.github/workflows/_release.yml:1-557]()

### Security Design

**Permission separation:**
```yaml