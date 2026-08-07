# Highlights

- `Overview.md:L18-L25` Semantic conventions standardize the meaning of spans, metrics, logs, events, and resource attributes across producers and consumers.
- `Core_Architecture.md:L51-L105` YAML models are the source of truth, with central attribute definitions referenced by span, metric, and event models and checked by schemas and policies.
- `from_modelprocessdeprecatedregistry-deprecated.yaml.md:L107-L156` References and inheritance enable reuse, while requirement levels express required, recommended, opt-in, and conditionally required attributes.
- `Core_Architecture.md:L138-L199` The build system validates models and generates documentation, changelogs, tables, and registries from the same definitions.
- `Schema_Evolution_System.md:L36-L86` Versioned change operations explicitly map renamed attributes and metrics and scope changes to signals or resources.
- `Schema_Evolution_System.md:L178-L207` Schema mappings allow older telemetry to be translated and give implementers a concrete migration plan.
- `Domain-Specific_Conventions.md:L269-L310` Registry metadata, stability states, changelogs, and domain approval jointly control how conventions evolve.
- `Governance_Model.md:L106-L177` CI checks and CODEOWNERS route proposed changes through domain-specific and global review before merge.
