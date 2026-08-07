# open-telemetry/semantic-conventions

## Summary

The OpenTelemetry Semantic Conventions repository defines a shared vocabulary for traces, metrics, logs, events, and resources so telemetry emitted by different languages and products can be interpreted consistently. Its central design choice is to keep machine-readable YAML models as the source of truth. Those models describe attribute names and types, span and metric structures, requirement levels, stability, examples, and explanatory text. Human-readable documentation and language-specific artifacts can then be generated from the same definitions instead of maintained as independent copies.

A central attribute registry prevents domains from inventing incompatible names for the same idea. Domain models for HTTP, databases, messaging, RPC, cloud platforms, runtimes, and other systems reference or extend those shared attributes while defining signal-specific rules. Requirement levels distinguish data that is mandatory, conditionally required, recommended, or opt-in; stability labels tell implementers how much change to expect.

The repository treats evolution as part of the schema contract. Versioned schema URLs identify the vocabulary used by telemetry, while explicit mappings record attribute and metric renames between versions. This lets collectors and backends translate older data and gives instrumentation authors a concrete migration path. Breaking-change policy depends on convention stability and is reinforced by changelog entries.

Quality and governance are automated around the model. Schema checks, semantic policies, linting, generated-table checks, and documentation generation run locally and in CI. CODEOWNERS routes changes to domain experts as well as global approvers, balancing specialized correctness with ecosystem-wide consistency. Together, the declarative model, reusable registry, migration history, validation pipeline, and domain ownership turn naming guidance into a maintainable interoperability standard.

## Knowledge Map

- YAML semantic models as the source of truth for telemetry schemas
- Shared attribute registry, references, and group inheritance
- Attribute requirement levels and convention stability states
- Versioned schema URLs and explicit rename mappings
- Generated documentation, policy validation, and CI checks
- Domain-specific conventions under domain and global governance

## Key Takeaways

- A semantic convention is an enforceable data contract, not just a naming suggestion.
- One machine-readable model should drive validation, documentation, and generated artifacts.
- Requirement and stability metadata communicate different promises: presence versus compatibility.
- Explicit version-to-version mappings make telemetry schema changes operationally migratable.
- Domain ownership preserves technical accuracy while global review protects cross-domain consistency.
