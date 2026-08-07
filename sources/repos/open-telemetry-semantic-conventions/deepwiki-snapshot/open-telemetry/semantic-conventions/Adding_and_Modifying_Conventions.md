This document explains the process and best practices for adding new semantic conventions or modifying existing ones in the OpenTelemetry semantic-conventions repository. It covers the workflow for defining conventions in YAML models, generating documentation, and ensuring backward compatibility.

For working with specific schema syntax details, see [Working with YAML Models](#4.2). For managing version changes, see [Changelog Management](#4.3).

## Process Overview

Adding or modifying semantic conventions involves several steps that ensure quality, consistency, and backward compatibility. The following diagram illustrates the overall process:

```mermaid
flowchart TD
    A["Identify Need for Convention"] --> B["Create/Modify YAML Model Files"]
    B --> C["Update Markdown Documentation"]
    C --> D["Check New Conventions (Policy Validation)"]
    D --> E["Verify Changes Before Committing"]
    E --> F["Add Changelog Entry"]
    F --> G["Create Pull Request"]
    G --> H["Review Process"]
    H --> I["Merge"]

    style A stroke-width:2px
    style I stroke-width:2px
```

Sources: [CONTRIBUTING.md:111-130](), [CONTRIBUTING.md:183-196](), [CONTRIBUTING.md:225-237]()

## File Organization

Before adding or modifying conventions, it's important to understand how files are organized in the repository:

```mermaid
flowchart TD
    subgraph "Repository Structure"
        model["model/ Directory"]
        docs["docs/ Directory"]
        schemas["schemas/ Directory"]
    end

    subgraph "Model Directory Structure"
        model --> namespaces["Namespace Directories\n(http, db, process, etc.)"]
        namespaces --> regYaml["registry.yaml\n(attribute definitions)"]
        namespaces --> signalYaml["spans.yaml, metrics.yaml, events.yaml\n(telemetry signal definitions)"]
        namespaces --> deprecated["deprecated/\n(deprecated conventions)"]
    end

    subgraph "Documentation Structure"
        docs --> docsNamespaces["Namespace Directories"]
        docs --> attrRegistry["attribute_registry/\n(auto-generated attribute docs)"]
        docsNamespaces --> README["README.md"]
        docsNamespaces --> otherDocs["Other .md files"]
    end
```

Sources: [CONTRIBUTING.md:131-166](), [README.md:10-13]()

## 1. Modifying the YAML Model

The first step in adding or modifying semantic conventions is updating the YAML model files in the `model/` directory.

### Where to Define New Attributes

All attributes must be defined in a registry file matching their root namespace:

- Common attributes: `/model/{root-namespace}/registry.yaml`
- Telemetry signals (spans, metrics, events): `/model/{root-namespace}/{signal}.yaml`
- Deprecated conventions: `/model/{root-namespace}/deprecated/registry-deprecated.yaml`

### Example of Attribute Definition

Here's an example showing how attributes are defined in YAML files:

```yaml