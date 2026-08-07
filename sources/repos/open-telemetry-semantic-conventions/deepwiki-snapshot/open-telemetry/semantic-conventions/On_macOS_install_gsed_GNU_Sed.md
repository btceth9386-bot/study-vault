brew bundle
```

Sources: [CONTRIBUTING.md:45-122]()

## Contribution Workflow Overview

The following diagram illustrates the complete workflow for contributing to the semantic conventions repository:

```mermaid
flowchart TD
    A["Start Contribution"] --> B["1. Modify YAML Model"]
    B --> C["2. Update Markdown Files"]
    C --> D["3. Check New Conventions"]
    D --> E["4. Verify Changes"]
    E --> F["5. Add Changelog Entry"]
    F --> G["Create Pull Request"]
    G --> H{"Review Process"}
    H --> |"Approved"| I["Merged"]
    H --> |"Changes Requested"| B

    subgraph "Validation Checks"
      E --> E1["make check"]
      E1 --> E2["Markdown Style"]
      E1 --> E3["Spell Check"]
      E1 --> E4["Link Check"]
      E1 --> E5["YAML Lint"]
      E1 --> E6["Schema Check"]
      E1 --> E7["Policy Check"]
    end
```

Sources: [CONTRIBUTING.md:50-317]()

## Code Structure and Organization

The repository has a specific structure that organizes YAML model files and their corresponding documentation:

```mermaid
flowchart TD
    A["Repository Structure"]
    A --> B["model/"]
    A --> C["docs/"]

    B --> D["model/{root-namespace}/"]
    D --> E["registry.yaml\n(attribute definitions)"]
    D --> F["spans.yaml\n(span conventions)"]
    D --> G["metrics.yaml\n(metric conventions)"]
    D --> H["events.yaml\n(event conventions)"]
    D --> I["deprecated/\n(deprecated conventions)"]

    C --> J["docs/{root-namespace}/"]
    J --> K["README.md"]
    J --> L["Other .md files"]

    C --> M["attribute_registry/"]

    E -- "table generation" --> M
    F -- "table generation" --> J
    G -- "table generation" --> J
    H -- "table generation" --> J
```

Sources: [CONTRIBUTING.md:130-166]()

## 1. Modify the YAML Model

All semantic conventions are formally defined in YAML files under the `model/` directory. When making changes:

- Add new attributes to the appropriate `registry.yaml` file
- Define new semantic conventions in the appropriate signal file (spans, metrics, events)
- Put deprecated conventions in the `deprecated/` folder

### Schema Files

When modifying existing semantic conventions, you must update the `schema-next.yaml` file to ensure backward compatibility. Semantic conventions follow a strict versioning and stability policy.

```bash
# Example: Updating the schema-next.yaml for an attribute rename
attributes:
  changes:
    - rename:
        from: old.attribute.name
        to: new.attribute.name
```

Sources: [CONTRIBUTING.md:124-182]()

## 2. Update the Markdown Files

After modifying the YAML files, you need to regenerate the corresponding markdown documentation:

```bash