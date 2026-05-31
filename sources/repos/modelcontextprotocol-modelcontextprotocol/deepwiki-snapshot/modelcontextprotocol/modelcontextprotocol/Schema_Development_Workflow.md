This document covers the technical workflow for developing and maintaining the MCP protocol schemas. It explains how to edit TypeScript schema definitions, generate derived artifacts (JSON Schema and MDX documentation), and validate changes through CI/CD.

For information about the protocol specification content itself, see [Schema System and Message Types](#2.2). For build system details beyond schema generation, see [Build System and CI/CD](#6.4).

## Purpose and Scope

The schema development workflow manages the transformation of canonical TypeScript schemas into multiple generated artifacts:

- **TypeScript schemas** (`schema/*/schema.ts`) are the single source of truth
- **JSON schemas** (`schema/*/schema.json`) are generated for machine consumption and tooling
- **MDX documentation** (`docs/specification/*/schema.mdx`) is generated for human-readable API reference

This document covers editing TypeScript schemas, running generation tools, understanding version-specific transformations, and validating that generated artifacts remain synchronized with the source.

## Schema System Architecture

```mermaid
graph TB
    subgraph "Source of Truth"
        DraftTS["schema/draft/schema.ts<br/>TypeScript Definitions"]
        V20251125TS["schema/2025-11-25/schema.ts"]
        V20250618TS["schema/2025-06-18/schema.ts"]
    end
    
    subgraph "Generation Tools"
        GenScript["scripts/generate-schemas.ts<br/>JSON Schema Generator"]
        TypeDocTool["TypeDoc + Plugin<br/>MDX Generator"]
    end
    
    subgraph "Generated Artifacts"
        DraftJSON["schema/draft/schema.json<br/>JSON Schema 2020-12"]
        V20251125JSON["schema/2025-11-25/schema.json<br/>JSON Schema 2020-12"]
        V20250618JSON["schema/2025-06-18/schema.json<br/>JSON Schema draft-07"]
        
        DraftMDX["docs/specification/draft/schema.mdx"]
        V20251125MDX["docs/specification/2025-11-25/schema.mdx"]
        V20250618MDX["docs/specification/2025-06-18/schema.mdx"]
    end
    
    DraftTS -->|typescript-json-schema| GenScript
    V20251125TS -->|typescript-json-schema| GenScript
    V20250618TS -->|typescript-json-schema| GenScript
    
    GenScript -->|writes| DraftJSON
    GenScript -->|writes| V20251125JSON
    GenScript -->|writes| V20250618JSON
    
    DraftTS -->|typedoc --schemaPageTemplate| TypeDocTool
    V20251125TS -->|typedoc --schemaPageTemplate| TypeDocTool
    V20250618TS -->|typedoc --schemaPageTemplate| TypeDocTool
    
    TypeDocTool -->|writes| DraftMDX
    TypeDocTool -->|writes| V20251125MDX
    TypeDocTool -->|writes| V20250618MDX
```

**Title: Schema Generation Pipeline Architecture**

The schema system consists of versioned TypeScript source files that are transformed through two parallel generation pipelines. The `typescript-json-schema` tool extracts JSON Schema definitions for validation and tooling, while TypeDoc with a custom plugin generates human-readable MDX documentation for the website.

Sources: [scripts/generate-schemas.ts:1-149](), [package.json:33-35]()

## Editing TypeScript Schemas

### Source Files Location

TypeScript schemas are located in version-specific directories:

```
schema/
├── draft/schema.ts           # Active development version
├── 2025-11-25/schema.ts      # Current stable (modern)
├── 2025-06-18/schema.ts      # Previous version (legacy)
├── 2025-03-26/schema.ts      # Earlier version (legacy)
└── 2024-11-05/schema.ts      # Earlier version (legacy)
```

**Active development occurs in `schema/draft/schema.ts`**. When a new protocol version is released, the draft schema is copied to a dated directory and frozen.

Sources: [scripts/generate-schemas.ts:10-17]()

### TypeScript Schema Structure

The TypeScript schema defines the protocol using standard TypeScript interfaces and type aliases:

```typescript
// Example from schema/draft/schema.ts
export interface JSONRPCRequest extends Request {
  jsonrpc: typeof JSONRPC_VERSION;
  id: RequestId;
}

export interface InitializeRequest extends JSONRPCRequest {
  method: "initialize";
  params: InitializeRequestParams;
}
```

Key patterns used in the schema:

| Pattern | Purpose | Example |
|---------|---------|---------|
| `interface` | Define protocol message structures | `InitializeRequest`, `InitializeResult` |
| `type` unions | Define discriminated unions | `JSONRPCMessage`, `ContentBlock` |
| `const` types | Define literal values | `method: "initialize"` |
| TSDoc comments | Document types for generation | `/** Description */` |
| `@category` tags | Organize generated docs | `@category "initialize"` |

Sources: [schema/draft/schema.ts:1-150](), [schema/draft/schema.ts:242-270]()

### Validation During Editing

To validate TypeScript syntax and type correctness while editing:

```bash
npm run check:schema:ts
```

This command runs three checks:

1. **TypeScript compilation** (`tsc --noEmit`) - Validates type correctness without generating output
2. **ESLint** - Enforces code quality rules
3. **Prettier** - Validates code formatting

Sources: [package.json:29]()

## Generation Pipeline

### JSON Schema Generation

```mermaid
graph LR
    TSSource["schema/VERSION/schema.ts"]
    TJS["typescript-json-schema<br/>--defaultNumberType integer<br/>--required<br/>--skipLibCheck"]
    RawJSON["Raw JSON Schema<br/>draft-07 format"]
    Transform["applyJsonSchema202012Transformations()"]
    FinalJSON["schema/VERSION/schema.json"]
    
    TSSource --> TJS
    TJS --> RawJSON
    RawJSON --> Transform
    Transform --> FinalJSON
    
    Note1["Modern versions only<br/>(2025-11-25, draft)"]
    
    Transform -.-> Note1
```

**Title: JSON Schema Generation Process**

The `typescript-json-schema` tool extracts JSON Schema definitions from TypeScript interfaces. For modern schema versions, the output is transformed from JSON Schema draft-07 to 2020-12 format.

#### Transformation Details

For modern schemas (`2025-11-25` and `draft`), three transformations are applied:

| Transformation | Draft-07 Format | 2020-12 Format |
|----------------|-----------------|----------------|
| Schema URI | `http://json-schema.org/draft-07/schema#` | `https://json-schema.org/draft/2020-12/schema` |
| Definitions key | `"definitions":` | `"$defs":` |
| Definition references | `#/definitions/` | `#/$defs/` |

Legacy schemas (`2024-11-05`, `2025-03-26`, `2025-06-18`) maintain draft-07 format for backward compatibility.

Sources: [scripts/generate-schemas.ts:10-14](), [scripts/generate-schemas.ts:23-47]()

### MDX Documentation Generation

```mermaid
graph LR
    TSSource["schema/VERSION/schema.ts"]
    Template["schema/VERSION/schema.mdx<br/>Template with frontmatter"]
    TypeDoc["typedoc<br/>--entryPoints schema.ts<br/>--schemaPageTemplate schema.mdx"]
    MDXOutput["docs/specification/VERSION/schema.mdx<br/>Mintlify-compatible"]
    
    TSSource --> TypeDoc
    Template --> TypeDoc
    TypeDoc --> MDXOutput
```

**Title: MDX Documentation Generation Process**

TypeDoc processes TypeScript source files and uses a custom template (`schema.mdx`) to generate Mintlify-compatible MDX documentation. The template includes frontmatter and structure, while TypeDoc populates it with type information and descriptions.

#### Template Structure

Each version directory contains a `schema.mdx` template:

```
schema/draft/schema.mdx       # Template for draft version
schema/2025-11-25/schema.mdx  # Template for 2025-11-25 version
```

The generated output is written to:

```
docs/specification/draft/schema.mdx
docs/specification/2025-11-25/schema.mdx
```

Sources: [package.json:35]()

### Running Generation Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `npm run generate:schema` | Generate both JSON and MDX | After editing TypeScript schemas |
| `npm run generate:schema:json` | Generate JSON schemas only | Testing JSON transformations |
| `npm run generate:schema:md` | Generate MDX documentation only | Testing documentation output |
| `npm run check:schema` | Validate without generating | Pre-commit validation |

The `generate:schema` command runs both JSON and MDX generation in parallel using shell background jobs (`&` and `wait`).

Sources: [package.json:33-35]()

## Version Management

### Legacy vs Modern Schemas

```mermaid
graph TB
    subgraph "Legacy Versions (JSON Schema draft-07)"
        L1["2024-11-05<br/>First public release"]
        L2["2025-03-26<br/>Added features"]
        L3["2025-06-18<br/>Last legacy version"]
    end
    
    subgraph "Modern Versions (JSON Schema 2020-12)"
        M1["2025-11-25<br/>First modern version<br/>Tasks, simplified auth"]
        M2["draft<br/>Active development"]
    end
    
    L1 --> L2
    L2 --> L3
    L3 --> M1
    M1 --> M2
    
    Note1["Maintain draft-07<br/>for compatibility"]
    Note2["Adopt 2020-12<br/>$defs terminology"]
    
    L3 -.-> Note1
    M1 -.-> Note2
```

**Title: Schema Version Evolution and JSON Schema Dialect Split**

The schema version split occurred at `2025-11-25` when the protocol adopted JSON Schema 2020-12. Earlier versions remain frozen in draft-07 format to preserve backward compatibility for existing implementations.

### Version-Specific Constants

The `generate-schemas.ts` script maintains two arrays defining which transformation pipeline to use:

```typescript
// Legacy schemas remain as JSON Schema draft-07
const LEGACY_SCHEMAS = ['2024-11-05', '2025-03-26', '2025-06-18'];

// Modern schemas use JSON Schema 2020-12
const MODERN_SCHEMAS = ['2025-11-25', 'draft'];
```

Sources: [scripts/generate-schemas.ts:10-14]()

### Adding a New Version

When releasing a new protocol version:

1. **Copy draft schema to dated directory**:
   ```bash
   cp -r schema/draft schema/YYYY-MM-DD
   ```

2. **Update version constants** in `scripts/generate-schemas.ts`:
   ```typescript
   const MODERN_SCHEMAS = ['2025-11-25', 'YYYY-MM-DD', 'draft'];
   ```

3. **Generate artifacts for new version**:
   ```bash
   npm run generate:schema
   ```

4. **Update documentation navigation** in `docs.json` to include the new version

Sources: [scripts/generate-schemas.ts:10-17]()

## Development Workflow

### Complete Development Cycle

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant TS as schema/draft/schema.ts
    participant Gen as Generation Scripts
    participant JSON as schema/draft/schema.json
    participant MDX as docs/specification/draft/schema.mdx
    participant CI as GitHub Actions
    
    Dev->>TS: Edit TypeScript schema
    Dev->>Dev: npm run check:schema:ts
    Note over Dev: Validate TypeScript
    
    Dev->>Gen: npm run generate:schema
    Gen->>JSON: typescript-json-schema
    Gen->>JSON: applyJsonSchema202012Transformations()
    Gen->>MDX: typedoc --schemaPageTemplate
    Gen-->>Dev: Generation complete
    
    Dev->>Dev: npm run check:docs
    Note over Dev: Validate docs formatting
    
    Dev->>CI: git push
    CI->>CI: npm run check:schema:json
    CI->>CI: npm run check:schema:md
    Note over CI: Validate generated<br/>artifacts match source
    
    alt Artifacts out of sync
        CI-->>Dev: ✗ Check failed
        Dev->>Gen: npm run generate:schema
        Dev->>CI: git push (with updated artifacts)
    else Artifacts in sync
        CI-->>Dev: ✓ Check passed
    end
```

**Title: Complete Schema Development and Validation Workflow**

The workflow ensures that all generated artifacts remain synchronized with the TypeScript source. CI validation catches any cases where generated files were not committed after source changes.

### Recommended Development Steps

1. **Make changes to TypeScript schema**:
   ```bash
   # Edit schema/draft/schema.ts
   vim schema/draft/schema.ts
   ```

2. **Validate TypeScript**:
   ```bash
   npm run check:schema:ts
   ```

3. **Generate artifacts**:
   ```bash
   npm run generate:schema
   ```

4. **Validate all changes**:
   ```bash
   npm run check:docs
   npm run format
   ```

5. **Or run everything at once**:
   ```bash
   npm run prep:changes
   ```

The `prep:changes` command is a convenience script that runs the complete validation and generation pipeline.

Sources: [package.json:36]()

## CI/CD Validation

### GitHub Actions Workflow

The CI pipeline validates schema consistency through three checks:

```yaml