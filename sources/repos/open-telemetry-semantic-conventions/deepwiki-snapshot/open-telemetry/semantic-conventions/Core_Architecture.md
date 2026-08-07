This document describes the fundamental architecture of the OpenTelemetry Semantic Conventions repository, explaining how semantic conventions are defined, structured, maintained, and governed. For specific details about domain-specific semantic conventions like HTTP or Database, see [Domain-Specific Conventions](#3).

## Semantic Convention Repository Overview

The OpenTelemetry Semantic Conventions repository serves as the central definition source for standardized telemetry attributes, metrics, spans, and events across various technology domains. These conventions ensure consistent telemetry data regardless of programming language or implementation.

```mermaid
flowchart TB
    subgraph "Core Architecture"
        Models["YAML Model Files"]
        Schema["Schema Management"]
        Build["Build System"]
        Gov["Governance"]
    end

    Models --> Schema
    Models --> Build
    Models -.-> Gov

    subgraph "Generated Artifacts"
        Doc["Markdown Documentation"]
        Changelog["CHANGELOG.md"]
    end

    Build --> Doc
    Build --> Changelog

    subgraph "Domain Conventions"
        HTTP["HTTP"]
        DB["Database"]
        MSG["Messaging"]
        SYS["System"]
        GenAI["GenAI"]
        K8s["Kubernetes"]
        Resource["Resource"]
        RPC["RPC"]
    end

    Models --> HTTP
    Models --> DB
    Models --> MSG
    Models --> SYS
    Models --> GenAI
    Models --> K8s
    Models --> Resource
    Models --> RPC
```

Sources: [CHANGELOG.md:1-472]()/[docs/http/http-spans.md:1-40]()

## Semantic Convention Structure

Semantic conventions are defined in YAML model files, which serve as the source of truth for all telemetry conventions. These files follow a structured schema that enables validation, versioning, and documentation generation.

```mermaid
flowchart TD
    subgraph "Model Definitions"
        YAML["semantic_conventions/*.yaml"]

        YAML --> Spans["span_definitions"]
        YAML --> Metrics["metric_definitions"]
        YAML --> Events["event_definitions"]
        YAML --> Attributes["attribute_registry"]
    end

    subgraph "Attribute References"
        SpanAttrs["span_attributes"]
        MetricAttrs["metric_attributes"]
        EventAttrs["event_attributes"]

        Attributes --> SpanAttrs
        Attributes --> MetricAttrs
        Attributes --> EventAttrs

        Spans --> SpanAttrs
        Metrics --> MetricAttrs
        Events --> EventAttrs
    end

    subgraph "Documentation"
        MarkdownDocs["docs/*.md"]
    end

    subgraph "Validation"
        Schema["schemas/*.yaml"]
        Policies["policies/*.rego"]
    end

    YAML --> MarkdownDocs
    YAML -.-> Schema
    YAML -.-> Policies
```

Sources: [docs/http/http-spans.md:35-115]()

### Key Components

| Component | Description | File Path Pattern |
|-----------|-------------|-------------------|
| Attribute Registry | Central definitions for all attributes used across spans, metrics, and events | `semantic_conventions/attributes/*.yaml` |
| Span Definitions | Definitions for trace spans across different domains | `semantic_conventions/trace/*.yaml` |
| Metric Definitions | Definitions for metrics across different domains | `semantic_conventions/metrics/*.yaml` |
| Event Definitions | Definitions for events across different domains | `semantic_conventions/events/*.yaml` |
| Schema Files | JSON Schema files for validating YAML model files | `schemas/*.yaml` |
| Policy Files | OPA Rego policies for semantic validation | `policies/*.rego` |

Sources: [docs/http/http-spans.md:35-115]()

### YAML Model Structure

The YAML model files contain structured definitions for spans, metrics, events, and attributes, with metadata that includes stability level, requirement level, and descriptive documentation.

Example snippet of a semantic convention YAML structure:

```
groups:
  - id: http.server
    prefix: http.server
    type: span
    stability: stable
    brief: "HTTP server span conventions"
    attributes:
      - id: request.method
        type: string
        brief: "HTTP request method"
        examples: ["GET", "POST", "HEAD"]
        requirement_level: required
      - id: response.status_code
        type: int
        brief: "HTTP response status code"
        examples: ["200"]
        requirement_level: conditionally_required
        condition: "If and only if one was received/sent"
```

Sources: [docs/http/http-spans.md:120-170]()

## Build and Validation System

The repository includes a comprehensive build and validation system that ensures semantic conventions are consistent, well-documented, and adhere to policies.

```mermaid
flowchart LR
    subgraph "Development Workflow"
        YAML["YAML Model Files"]

        YAML --> Make["Makefile"]
        YAML --> CI["GitHub Actions"]

        subgraph "Validation Checks"
            Schema["Schema Validation"]
            Lint["YAML Lint"]
            Policy["Policy Validation"]
            Links["Link Check"]
            Spell["Spell Check"]
        end

        CI --> Schema
        CI --> Lint
        CI --> Policy
        CI --> Links
        CI --> Spell

        subgraph "Generation Tasks"
            Tables["Table Generation"]
            Registry["Registry Generation"]
            ChangeLog["Changelog Generation"]
            Markdown["Markdown Documentation"]
        end

        Make --> Tables
        Make --> Registry
        Make --> ChangeLog
        Make --> Markdown

        Valid{"Validation\nSuccessful?"}

        Schema --> Valid
        Lint --> Valid
        Policy --> Valid
        Links --> Valid
        Spell --> Valid

        Valid -->|"Yes"| Merge["Merge to Main"]
        Valid -->|"No"| Feedback["Fix Issues"]
        Feedback --> YAML
    end
```

Sources: [CHANGELOG.md:1-20]()

The build process performs several key functions:

1. **Validation** - Ensures YAML files conform to schemas and policies
2. **Documentation Generation** - Creates consistent markdown documentation
3. **Changelog Management** - Tracks changes and maintains versioning
4. **Table Generation** - Creates consistent attribute tables in documentation
5. **Registry Generation** - Ensures attribute consistency across conventions

Sources: [CHANGELOG.md:1-20]()

## Schema Evolution System

The schema evolution system provides a structured way to evolve conventions over time while maintaining backward compatibility.

```mermaid
flowchart TD
    subgraph "Schema Versioning"
        Previous["Previous Schemas"]
        Current["Current Schema (v1.34.0)"]
        Next["Next Schema Version"]

        Previous --> Current
        Current --> Next
    end

    subgraph "Evolution Operations"
        Rename["Rename Operations"]
        Add["Add Operations"]
        Deprecate["Deprecate Operations"]
        Remove["Remove Operations"]

        Rename --> RenameAttr["Rename Attributes"]
        Rename --> RenameMetrics["Rename Metrics"]

        Add --> AddAttr["Add Attributes"]
        Add --> AddMetrics["Add Metrics"]

        Deprecate --> DeprecateAttr["Deprecate Attributes"]
        Deprecate --> DeprecateMetrics["Deprecate Metrics"]
    end

    Current --> Rename
    Current --> Add
    Current --> Deprecate
    Current --> Remove

    subgraph "Change Tracking"
        AttributeMap["attribute_map.yaml"]
        ChangeLog["CHANGELOG.md"]
    end

    RenameAttr --> AttributeMap
    RenameMetrics --> AttributeMap

    Rename --> ChangeLog
    Add --> ChangeLog
    Deprecate --> ChangeLog
    Remove --> ChangeLog
```

Sources: [CHANGELOG.md:6-102]()

### Schema Stability Levels

The semantic conventions define different stability levels:

| Stability Level | Description | Breaking Change Policy |
|-----------------|-------------|------------------------|
| Stable | Mature conventions unlikely to change | Breaking changes require major version bump |
| Release Candidate | Nearly stable, may have minor changes | Breaking changes announced in advance |
| Development | Actively evolving, may change significantly | Breaking changes with minor version bump |

Sources: [docs/http/http-spans.md:7-9]()

### Breaking Changes Process

When breaking changes are necessary, the repository follows a strict process:

1. Document the change in CHANGELOG.md
2. Update attribute maps for renamed attributes
3. Include migration guidance when applicable
4. Version bump according to stability level

For example, in v1.34.0, there was a breaking change to convert deprecated text to structured format:

```
- `all`: Convert deprecated text to structured format. (#2047)
  This is a breaking change from the schema perspective, but does not change anything for instrumentations or the end users. It breaks compatibility with the (old) code generation tooling.
```

Sources: [CHANGELOG.md:10-15]()

## Governance Model

The repository employs a domain-based governance model where experts in specific areas oversee their respective domains.

```mermaid
flowchart TD
    subgraph "Governance Structure"
        Global["Global Maintainers"]

        Global --> SemConvApprovers["Semantic Convention\nApprovers"]

        SemConvApprovers --> Domain["Domain-Specific\nApprovers"]

        Domain --> HTTP["HTTP Approvers"]
        Domain --> DB["Database Approvers"]
        Domain --> MSG["Messaging Approvers"]
        Domain --> K8s["Kubernetes Approvers"]
        Domain --> Tool["Tooling Approvers"]
        Domain --> Other["Other Domain Approvers"]
    end

    subgraph "Contribution Flow"
        Issue["Issues/PRs"]
        Labels["Area Labels"]
        CODEOWNERS["CODEOWNERS File"]
        PR["Pull Request"]
        Review["Review"]
        Merge["Merge"]

        Issue --> Labels
        PR --> Review
        CODEOWNERS --> Review
        Review --> Merge
    end

    Domain -.-> CODEOWNERS
    CODEOWNERS -.-> Domain
```

Sources: [CHANGELOG.md:1-5]()

### Domain-Specific Ownership

The governance model ensures that experts in each domain are responsible for approving changes to their specific areas. This is defined in the CODEOWNERS file, which maps directories and files to specific maintainers.

For example:
- HTTP conventions are maintained by HTTP experts
- Database conventions are maintained by database experts
- Messaging conventions are maintained by messaging experts
- Kubernetes conventions are maintained by Kubernetes experts

This ensures that conventions are accurate and meet the needs of domain specialists.

Sources: [docs/http/http-spans.md:1-40]()

## Code Generation and Tooling

The repository provides tools for generating code and documentation from the semantic convention definitions.

```mermaid
flowchart LR
    subgraph "Source Definitions"
        YAML["YAML Model Files"]
    end

    subgraph "Generator Tools"
        Weaver["weaver CLI Tool"]
    end

    subgraph "Generated Artifacts"
        Markdown["Markdown Docs"]
        Code["Language Code"]
        Tables["Attribute Tables"]
    end

    YAML --> Weaver
    Weaver --> Markdown
    Weaver --> Code
    Weaver --> Tables
```

### Weaver Tool

A tool called "weaver" is used to generate:
- Semantic convention markdown documentation
- Code for various programming languages
- Consistent attribute tables

This replaced the older code generation tooling as mentioned in the CHANGELOG:

```
This is a breaking change from the schema perspective, but does not change anything for instrumentations or the end users. It breaks compatibility with the (old) code generation tooling. Please use [weaver](https://github.com/open-telemetry/weaver) to generate Semantic Conventions markdown or code.
```

Sources: [CHANGELOG.md:14-15]()

## Conclusion

The core architecture of the OpenTelemetry Semantic Conventions repository provides a robust system for defining, validating, evolving, and governing telemetry conventions across multiple domains. The YAML-based model files serve as the source of truth, while the build and validation system ensures quality and consistency. The schema evolution system allows for controlled changes over time, and the governance model ensures domain expertise is applied to convention development.