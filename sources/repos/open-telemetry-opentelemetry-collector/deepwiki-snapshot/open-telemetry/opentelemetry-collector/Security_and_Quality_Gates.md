This document describes the automated security scanning, quality checks, and validation gates that run on every pull request to the OpenTelemetry Collector. These gates ensure code security, maintain API compatibility, enforce code quality standards, and validate that generated code is up-to-date. For information about the broader CI/CD system and multi-platform testing, see [CI/CD and Automation](#10). For the release preparation workflow, see [Release Management](#11).

---

## Security Scanning Infrastructure

The collector implements multiple layers of security scanning to detect vulnerabilities, analyze code for security issues, and assess supply chain security posture.

### CodeQL Static Analysis

The `codeql-analysis.yml` workflow performs static security analysis on every push to `main` and on all pull requests. CodeQL identifies security vulnerabilities, coding errors, and other potential issues in the Go codebase.

**CodeQL Analysis Logic**
```mermaid
graph TB
    ["workflow: CodeQL Analysis"] -- "on: push/pull_request" --> [Init]

    subgraph "CodeQL_Analysis_Pipeline"
        [Init] -- "uses: github/codeql-action/init" --> [Lang_Go]
        [Lang_Go] -- "languages: go" --> [Autobuild]
        [Autobuild] -- "uses: github/codeql-action/autobuild" --> [Analyze]
        [Analyze] -- "uses: github/codeql-action/analyze" --> [Upload_SARIF]
    end

    [Upload_SARIF] -- "permissions: security-events: write" --> [Security_Dashboard]
```

**CodeQL Analysis Workflow**

The workflow uses GitHub's CodeQL action to scan the entire codebase:

1. **Initialization**: The `github/codeql-action/init` action initializes CodeQL with Go language support [.github/workflows/codeql-analysis.yml:43-46]().
2. **Build**: The `autobuild` action attempts to compile the project automatically to enable deeper analysis [.github/workflows/codeql-analysis.yml:48-49]().
3. **Analysis**: CodeQL scans the compiled code for security vulnerabilities and code quality issues [.github/workflows/codeql-analysis.yml:51-52]().
4. **Upload**: Results are uploaded to GitHub's security dashboard with `security-events: write` permission [.github/workflows/codeql-analysis.yml:18]().

The workflow runs concurrently with other checks and can be canceled if a newer commit is pushed to the same branch [.github/workflows/codeql-analysis.yml:7-9]().

**Sources**: [.github/workflows/codeql-analysis.yml:1-53]()

---

### Vulnerability Scanning with govulncheck

The `govulncheck` job in the `build-and-test.yml` workflow scans all Go module dependencies for known security vulnerabilities using the official Go vulnerability database.

**Vulnerability Scan Flow**
```mermaid
graph LR
    ["job: setup-environment"] --> ["job: govulncheck"]

    subgraph "Vulnerability_Scan_Process"
        ["job: govulncheck"] --> [Restore_Go_Cache]
        [Restore_Go_Cache] --> ["run: make govulncheck"]
        ["run: make govulncheck"] --> [Scan_Against_Vuln_DB]
    end

    [Scan_Against_Vuln_DB] --> [Report_Vulnerabilities]
```

**Vulnerability Scanning Process**

The `govulncheck` job runs on every pull request and push to main:

| Step | Action | Details |
|------|--------|---------|
| Setup | Checkout repository and setup Go | Uses specific Go version (e.g., `oldstable`) [.github/workflows/build-and-test.yml:79-82]() |
| Cache | Restore Go modules and binaries from cache | Path: `~/go/bin` and `~/go/pkg/mod` [.github/workflows/build-and-test.yml:84-91]() |
| Scan | Execute `make govulncheck` | 30-minute timeout [.github/workflows/build-and-test.yml:70-94]() |

The job leverages the `setup-environment` job to ensure dependencies are pre-downloaded and cached [.github/workflows/build-and-test.yml:73]().

**Sources**: [.github/workflows/build-and-test.yml:70-94]()

---

### Supply Chain Security with OpenSSF Scorecard

The `scorecard.yml` workflow runs the OpenSSF Scorecard to assess the project's supply chain security practices against industry standards.

**Scorecard Pipeline**
```mermaid
graph TB
    [Triggers] --> [Checkout_Code]

    subgraph "Scorecard_Evaluation"
        [Checkout_Code] -- "persist-credentials: false" --> [Run_Analysis]
        [Run_Analysis] -- "uses: ossf/scorecard-action" --> [Checks]
        [Checks] --> [Generate_SARIF]
    end

    [Generate_SARIF] --> [Upload_Artifact]
    [Generate_SARIF] -- "uses: github/codeql-action/upload-sarif" --> [Upload_to_Code_Scanning]
    [Upload_to_Code_Scanning] --> [Publish_to_OpenSSF_API]
```

**OpenSSF Scorecard Evaluation**

The workflow evaluates supply chain security on three types of triggers:

1. **Weekly Schedule**: Runs every Wednesday at 1:39 AM UTC to ensure the "Maintained" check stays current [.github/workflows/scorecard.yml:9-10]().
2. **Push to main**: Evaluates security posture on every merge to the default branch [.github/workflows/scorecard.yml:11-12]().
3. **Branch Protection Rule Changes**: Re-evaluates when branch protection settings change [.github/workflows/scorecard.yml:6]().

The workflow uses `persist-credentials: false` for enhanced security during analysis [.github/workflows/scorecard.yml:34](). Results are:
- Uploaded as a SARIF artifact with 5-day retention [.github/workflows/scorecard.yml:58-63]().
- Sent to GitHub's code scanning dashboard [.github/workflows/scorecard.yml:66-69]().
- Published to the OpenSSF REST API for public visibility and badge generation [.github/workflows/scorecard.yml:54]().

**Sources**: [.github/workflows/scorecard.yml:1-70]()

---

## API Compatibility Validation

The `api-compatibility.yml` workflow prevents breaking changes to stable APIs by comparing the API surface between the PR branch and the main branch using `apidiff`.

**API Compatibility Logic**
```mermaid
graph TB
    ["on: pull_request"] --> [Checkout-Main]
    ["on: pull_request"] --> [Checkout-HEAD]

    subgraph "API_Compatibility_Logic"
        [Checkout-Main] -- "env: BASE_REF" --> ["run: make apidiff-build"]
        [Checkout-HEAD] -- "env: HEAD_REF" --> ["run: make apidiff-compare"]
        ["run: make apidiff-build"] -- "Snapshot in internal/data/apidiff" --> ["run: make apidiff-compare"]
    end

    ["run: make apidiff-compare"] --> [Check-States]
    [Check-States] -- "Exit Code" --> [Pass_Fail]
```

**API Compatibility Check Process**

The workflow performs a multi-step validation process:

1. **Generate Baseline**: Checks out the base branch (main) and runs `make apidiff-build` to create snapshots of the current API state [.github/workflows/api-compatibility.yml:51-54]().
2. **Compare Differences**: Checks out the PR branch and runs `make apidiff-compare` to display all changes [.github/workflows/api-compatibility.yml:57-63]().
3. **Enforce Compatibility**: Runs `make apidiff-compare` with the `-c` flag. This step fails the build if any incompatible changes (e.g., removing a public method or changing a function signature) are detected [.github/workflows/api-compatibility.yml:66-72]().

The workflow sets `COMPARE_OPTS` to point to the snapshots generated in the base reference directory (e.g., `../${{ github.base_ref }}/internal/data/apidiff`) [.github/workflows/api-compatibility.yml:69]().

**Sources**: [.github/workflows/api-compatibility.yml:1-73]()

---

## Code Quality Gates

Multiple code quality checks run in the `lint` and `checks` jobs of the `build-and-test.yml` workflow, enforcing consistency, license compliance, and documentation standards.

### Linting and Formatting

The `lint` job focuses on Go-specific static analysis [.github/workflows/build-and-test.yml:43-69]():
- `make golint`: Runs `golangci-lint` with a comprehensive set of linters [.github/workflows/build-and-test.yml:65-66]().
- `make goimpi`: Validates Go import organization [.github/workflows/build-and-test.yml:67-68]().

### Documentation and Standards

The `checks` job enforces broader project standards [.github/workflows/build-and-test.yml:96-168]():

| Gate | Command | Purpose |
|------|---------|---------|
| License | `make checklicense` | Ensures Apache 2.0 headers are present in all files [.github/workflows/build-and-test.yml:122-123](). |
| Spelling | `make misspell` | Detects common misspellings in documentation [.github/workflows/build-and-test.yml:124-125](). |
| Docs Structure | `make checkdoc` | Validates documentation standards [.github/workflows/build-and-test.yml:126-127](). |
| Markdown | `make markdownlint` | Enforces markdown style rules using Node.js [.github/workflows/build-and-test.yml:128-129](). |
| API Check | `make checkapi` | General API validation [.github/workflows/build-and-test.yml:130-131](). |
| Porto | `make goporto` | Validates internal documentation links and module names [.github/workflows/build-and-test.yml:136-139](). |
| Tidy | `make gotidy` | Ensures `go.mod` and `go.sum` are synchronized [.github/workflows/build-and-test.yml:132-135](). |

**Sources**: [.github/workflows/build-and-test.yml:43-168]()

---

## Code Generation Validation

The collector uses extensive code generation. The `checks` job verifies that all generated code is up-to-date and matches what is committed in the repository.

**Code Generation Validation Matrix**

If any of the following commands result in a diff, the CI fails, instructing the developer to run the generation locally and commit the changes:

- **General Go Generate**: `make gogenerate` [.github/workflows/build-and-test.yml:140-143]().
- **Protobuf**: `make genproto` [.github/workflows/build-and-test.yml:144-147]().
- **Pdata**: `make genpdata` [.github/workflows/build-and-test.yml:148-151]().
- **Otelcorecol**: `make genotelcorecol` [.github/workflows/build-and-test.yml:152-155]().
- **Module Crosslinks**: `make crosslink` ensures replace directives in `go.mod` files are correct [.github/workflows/build-and-test.yml:158-161]().
- **Chloggen Components**: `make generate-chloggen-components` updates the component list for changelog generation [.github/workflows/build-and-test.yml:162-165]().

**Sources**: [.github/workflows/build-and-test.yml:140-165]()

---

## Changelog Enforcement

The `changelog.yml` workflow ensures every PR targeting the `main` branch includes a changelog entry in the `.chloggen/` directory.

**Changelog Validation Rules**

1. **No Direct Edits**: Developers must not modify `CHANGELOG.md` or `CHANGELOG-API.md` directly [.github/workflows/changelog.yml:49-60]().
2. **YAML Entry Required**: A new `.yaml` file must be added to the `./.chloggen/` directory [.github/workflows/changelog.yml:62-73]().
3. **Validation**: The entry must pass schema validation via `make chlog-validate` [.github/workflows/changelog.yml:75-78]().
4. **Link Integrity**: The workflow renders a preview and uses `lycheeverse/lychee-action` to ensure all links in the changelog entry are valid [.github/workflows/changelog.yml:81-88]().

The workflow can be skipped by adding the "Skip Changelog" label, the "dependencies" label, or adding `[chore]` to the PR title [.github/workflows/changelog.yml:24]().

**Sources**: [.github/workflows/changelog.yml:1-89]()

---

## Cross-Repository Testing (Contrib)

The `contrib-tests.yml` workflow validates that changes to the core collector do not break the `opentelemetry-collector-contrib` repository.

**Process**:
1. **Prepare**: Clones the contrib repository and runs `make prepare-contrib`, which points contrib modules to the local core collector code [.github/workflows/contrib-tests.yml:28-32]().
2. **Matrix Test**: Runs tests for all contrib components in parallel groups (e.g., `receiver-0`, `processor`, `exporter-1`, `connector`, `pkg`) [.github/workflows/contrib-tests.yml:43-59]().
3. **Verification**: Uses `make check-contrib` within the matrix to execute tests against the modified dependencies [.github/workflows/contrib-tests.yml:87-88]().

This gate is critical for ensuring that core API changes are backward compatible with the vast ecosystem of contrib components.

**Sources**: [.github/workflows/contrib-tests.yml:1-110]()