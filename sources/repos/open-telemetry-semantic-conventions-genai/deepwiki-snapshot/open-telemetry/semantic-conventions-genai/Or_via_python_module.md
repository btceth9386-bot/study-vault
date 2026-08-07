python -m semconv_genai.report
```
Sources: [reference/src/semconv_genai/report.py:5-6]()

This command:
1.  Loads all `data.json` files from `reference/scenarios/` [reference/src/semconv_genai/report.py:218]().
2.  Loads the semantic convention model via `semconv_model.py` [reference/src/semconv_genai/report.py:31-34]().
3.  Generates the markdown content for each signal type [reference/src/semconv_genai/report.py:220-227]().
4.  Updates the `reference/README.md` file [reference/src/semconv_genai/report.py:230-240]().

# CI/CD & GitHub Automation




This page provides a high-level overview of the automation infrastructure supporting the Semantic Conventions for Generative AI. The repository utilizes GitHub Actions to orchestrate model validation, documentation generation, reference scenario testing, and release management.

## Automation Overview

The automation strategy ensures that the YAML-based semantic convention model remains consistent with its generated documentation and that the conventions are practically verifiable against real-world LLM client libraries.

### System Orchestration Diagram

The following diagram illustrates how GitHub Actions (`CI.yml`) interacts with the repository's toolchain (Weaver, Makefile, and Python Reference Framework) to validate changes.

**CI Validation Flow**
```mermaid
graph TD
    subgraph "GitHub Actions Space"
        [".github/workflows/ci.yml"] -- "triggers" --> ["links"]
        [".github/workflows/ci.yml"] -- "triggers" --> ["policies"]
        [".github/workflows/ci.yml"] -- "triggers" --> ["generated-docs"]
        [".github/workflows/ci.yml"] -- "triggers" --> ["reference-scenarios"]
    end

    subgraph "Code Entity Space"
        ["policies"] -- "executes" --> ["make check-policies"]
        ["generated-docs"] -- "executes" --> ["make generate-all"]
        ["reference-scenarios"] -- "invokes" --> ["uv run run-scenario"]

        ["make check-policies"] -- "calls" --> ["weaver registry check"]
        ["make generate-all"] -- "calls" --> ["weaver registry generate"]
        ["uv run run-scenario"] -- "executes" --> ["reference/src/semconv_genai/pipeline.py"]
    end

    subgraph "Filesystem"
        ["weaver registry check"] -- "reads" --> ["model/"]
        ["weaver registry generate"] -- "updates" --> ["docs/registry/"]
        ["weaver registry generate"] -- "updates" --> ["schema-snapshot/"]
    end
```
Sources: [.github/workflows/ci.yml:1-192](), [Makefile:112-156](), [reference/src/semconv_genai/pipeline.py:1-50]()

---

## CI Pipeline

The primary CI pipeline is defined in `.github/workflows/ci.yml`. It acts as a gatekeeper for all Pull Requests, ensuring that no breaking changes are introduced to the model or the reference implementations.

### Key Workflows
*   **Link Checking**: Uses `lychee` via the `flint` wrapper to verify all internal and external documentation links [.github/workflows/ci.yml:20-45]().
*   **Model Validation**: Executes `make check-policies` which runs the `weaver registry check` command against the `model/` directory using OPA policies [.github/workflows/ci.yml:47-64]().
*   **Sync Checks**: Runs `make generate-all` and verifies that the resulting files in `docs/registry/` and `schema-snapshot/` match the committed versions [.github/workflows/ci.yml:65-95]().
*   **Scenario Testing**: A matrix-based job that runs reference scenarios for libraries like OpenAI and Anthropic, ensuring the conventions can be correctly implemented [.github/workflows/ci.yml:136-163]().

For details, see [CI Workflows](#7.1).

---

## Release & Versioning

The repository follows a structured release process for the "dev-channel" of GenAI semantic conventions. Versions are managed via the `schema_url` in the model manifest.

### Release Automation Diagram

This diagram maps the release process from the YAML configuration to the GitHub Release assets.

**Release Asset Generation**
```mermaid
graph LR
    subgraph "Natural Language Space"
        ["Version Bump"]
        ["Changelog Update"]
    end

    subgraph "Code Entity Space"
        ["Version Bump"] --> ["model/manifest.yaml"]
        ["model/manifest.yaml"] -- "parsed by" --> [".github/workflows/release-dev.yml"]
        [".github/workflows/release-dev.yml"] -- "calls" --> ["make package-dev"]
        ["make package-dev"] -- "produces" --> [".build/package/resolved.yaml"]
        [".build/package/resolved.yaml"] -- "uploaded to" --> ["GitHub Release Asset"]
    end
```
Sources: [RELEASING.md:1-23](), [.github/workflows/release-dev.yml:16-75](), [Makefile:68-70]()

### Release Process Summary
1.  **Preparation**: The `schema_url` in `model/manifest.yaml` is updated [RELEASING.md:8-10]().
2.  **Drafting**: A GitHub Release draft is created manually with the corresponding `vX.Y.Z-dev` tag [RELEASING.md:16-19]().
3.  **Execution**: The `release-dev.yml` workflow is triggered. It computes the tag from the manifest, runs `make package-dev` to generate a resolved schema, and attaches `resolved.yaml` and `manifest.yaml` to the release [.github/workflows/release-dev.yml:16-64]().

---

## PR Dashboard & Notifications

To manage the high volume of contributions and track the status of various provider-specific conventions, the repository utilizes a custom PR dashboard and Slack notification system.

*   **Dashboard**: A Netlify-hosted interface that aggregates PR status, labels, and CI results.
*   **State Management**: Python scripts under `.github/scripts/pull-request-dashboard/` manage the lifecycle of PR data, using `state.py` to track individual PR entities.
*   **Notifications**: Automated Slack alerts notify maintainers of new PRs or status changes, classified by the logic in `classification.py`.

For details, see [PR Dashboard & Notifications](#7.2).

---

## Tooling and Environment

The automation relies on a consistent environment defined by several configuration files:
*   **Makefile**: The central entry point for all automation tasks, abstracting `weaver` calls via Docker [Makefile:1-22]().
*   **versions.env**: Contains pinned versions for `WEAVER_VERSION` and `SEMCONV_VERSION` to ensure reproducible builds [Makefile:8-10]().
*   **mise.toml**: Configures local development tools like `lychee` and `flint` [mise.toml:1-14]().

Sources: [Makefile:1-160](), [RELEASING.md:1-23](), [.github/workflows/ci.yml:1-200](), [.github/workflows/release-dev.yml:1-75]()

# CI Workflows




The `semantic-conventions-genai` repository utilizes GitHub Actions to ensure the integrity of the semantic convention model, the consistency of generated documentation, and the validity of reference implementations. The primary CI pipeline is defined in `.github/workflows/ci.yml` and is supplemented by security scanning and issue management workflows.

## CI Pipeline Overview

The main CI workflow ([.github/workflows/ci.yml:1-11]()) triggers on every push to the `main` branch, pull requests targeting `main`, and within GitHub Merge Groups. It is designed with high concurrency to cancel in-progress runs when new commits are pushed to the same branch or PR ([.github/workflows/ci.yml:11-13]()).

### Workflow Execution Flow

The following diagram illustrates the dependency graph and data flow of the CI pipeline.

**CI Job Dependencies and Data Flow**
```mermaid
graph TD
    subgraph "Validation Phase"
        [links] --> [required-status-check]
        [policies] --> [required-status-check]
        [generated-docs] --> [required-status-check]
        [reference-python-lint] --> [required-status-check]
    end

    subgraph "Reference Testing Phase"
        [reference-scenario-matrix] --> [reference-scenarios]
        [reference-scenarios] --> [required-status-check]
        [reference-status-report] --> [required-status-check]
    end

    [required-status-check] -- "Gatekeeper" --> SUCCESS["Branch Protection Pass"]

    style [required-status-check] stroke-dasharray: 5 5
```
**Sources:** [.github/workflows/ci.yml:183-200]()

---

## Static Analysis and Model Validation

### Link Checking (lychee)
The `links` job uses the `lychee` tool via the `flint` wrapper to validate all hyperlinks within the repository ([.github/workflows/ci.yml:20-45]()).
- **Configuration**: Managed via `.github/config/lychee.toml` and `.github/config/flint.toml`.
- **Behavior**: It checks all local links in every file and all remote links in changed files ([.github/config/flint.toml:1-4]()).
- **Exclusions**: Specific domains that block automated crawlers (e.g., OpenAI, DeepSeek) or future schema URLs not yet published are excluded ([.github/config/lychee.toml:15-26]()).

### Policy Validation
The `policies` job ensures the YAML model adheres to OpenTelemetry semantic convention rules ([.github/workflows/ci.yml:47-64]()).
- **Tooling**: It installs a specific version of `weaver` as defined in the repository's version pins ([.github/workflows/ci.yml:57-61]()).
- **Execution**: Runs `make check-policies` ([.github/workflows/ci.yml:63]()), which invokes Weaver's policy engine against the `model/` directory.

### Generated Documentation Sync
The `generated-docs` job verifies that the human-readable markdown in `docs/` and the `schema-snapshot/` are perfectly in sync with the YAML model ([.github/workflows/ci.yml:65-95]()).
- **Process**:
    1. Executes `make generate-all` to refresh all artifacts ([.github/workflows/ci.yml:82]()).
    2. Runs `git diff --exit-code` to detect if any generated files were modified but not committed ([.github/workflows/ci.yml:83]()).
    3. Checks for untracked files that should have been included in the PR ([.github/workflows/ci.yml:88-93]()).

**Sources:** [.github/workflows/ci.yml:20-95](), [mise.toml:11-14](), [.github/config/lychee.toml:1-27]()

---

## Reference Implementation Testing

The CI validates the conventions against real-world scenarios using a Python-based testing framework located in the `reference/` directory.

### Matrix Discovery and Parallel Execution
To optimize execution time, the CI dynamically discovers available scenarios.
1. **Discovery**: The `reference-scenario-matrix` job runs `uv run run-scenario --print-ci-matrix` ([.github/workflows/ci.yml:133]()). This outputs a JSON matrix of all subdirectories in `reference/scenarios/`.
2. **Execution**: The `reference-scenarios` job consumes this matrix to run tests in parallel ([.github/workflows/ci.yml:143-145]()).

### Scenario Validation Logic
Each parallel runner performs the following:
- **Environment Setup**: Uses the `setup-reference-tooling` composite action ([.github/workflows/ci.yml:149]()).
- **Dependency Materialization**: Runs `make filter-upstream` to prepare the base OpenTelemetry semantic conventions required for Weaver live-checks ([.github/workflows/ci.yml:151-153]()).
- **Test Run**: Executes the specific library scenario (e.g., `openai`, `anthropic`) which generates a `data.json` file ([.github/workflows/ci.yml:156]()).
- **Data Integrity**: Ensures the `data.json` produced by the code matches the version committed in the repository ([.github/workflows/ci.yml:158-163]()).

### Status Report Verification
The `reference-status-report` job runs `uv run update-reports` ([.github/workflows/ci.yml:177]()). This script aggregates results from all `data.json` files to update the coverage tables in `reference/README.md` and the detailed reports in `reference/reports/`. The CI fails if these reports are not up to date with the latest scenario outputs ([.github/workflows/ci.yml:179-180]()).

**Sources:** [.github/workflows/ci.yml:118-181]()

---

## Security and Maintenance

### CodeQL Analysis
The `CodeQL` workflow ([.github/workflows/codeql.yml]()) performs static analysis security testing (SAST) for GitHub Actions and Python code.
- **Schedules**: Runs weekly and on every PR ([.github/workflows/codeql.yml:3-9]()).
- **Exclusions**: The `mock_server` infrastructure used for local testing is excluded from analysis to reduce noise ([.github/codeql/codeql-config.yml:3-6]()).

### Issue Management
Automated workflows handle the lifecycle of issues and PRs:
- **Stale Action**: Automatically labels and eventually closes issues/PRs that have been inactive for 14 days while awaiting author feedback ([.github/workflows/issue-management-stale-action.yml:28-40]()).
- **Label Cleanup**: Automatically removes `needs author feedback` and `stale` labels when the original author posts a comment ([.github/workflows/issue-management-feedback-label.yml:11-28]()).

**Sources:** [.github/workflows/codeql.yml:1-50](), [.github/codeql/codeql-config.yml:1-7](), [.github/workflows/issue-management-stale-action.yml:1-42]()

---

## Branch Protection: The Required Gate

The `required-status-check` job acts as the final gatekeeper for branch protection rules ([.github/workflows/ci.yml:183-200]()). It depends on every other functional job in the CI pipeline.

**Required Check Logic**
| Job | Responsibility |
| :--- | :--- |
| `links` | No broken URLs in documentation. |
| `policies` | Model complies with Weaver semantic rules. |
| `generated-docs` | `docs/` and `schema-snapshot/` match the YAML model. |
| `reference-python-lint` | `ruff` check and format pass for reference code. |
| `reference-scenarios` | All provider scenarios produce expected telemetry. |
| `reference-status-report` | Coverage reports are synchronized with scenario data. |

The job is configured to fail if any of its dependencies fail, are cancelled, or are skipped ([.github/workflows/ci.yml:197]()), ensuring that no PR can be merged unless the entire suite passes.

**Sources:** [.github/workflows/ci.yml:183-200]()