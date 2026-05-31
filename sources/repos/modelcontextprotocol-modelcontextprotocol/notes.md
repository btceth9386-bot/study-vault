# modelcontextprotocol/modelcontextprotocol

## Summary

The `modelcontextprotocol/modelcontextprotocol` repository is the canonical specification source for MCP. It does more than describe a wire protocol: it defines the versioned schema, the generated JSON and MDX artifacts, the governance process for evolving the protocol, and the ecosystem-facing documentation that helps clients and servers implement the same contract. The core design is a bidirectional JSON-RPC 2.0 protocol where clients and servers negotiate optional features during initialization instead of assuming one fixed capability set.

Three ideas stand out. First, MCP separates the transport from the protocol. The same request, response, and notification model can run over local stdio or remote Streamable HTTP, which lets the ecosystem cover both desktop-style local integrations and hosted multi-tenant services. Second, capability negotiation is central rather than decorative. Features such as tools, resources, prompts, roots, sampling, elicitation, tasks, and extensions are declared explicitly, so each side can degrade gracefully instead of guessing what the other party supports. Third, the repository treats schema maintenance as an engineering system: TypeScript definitions act as the single source of truth, while JSON Schema and docs are generated and checked in CI to keep implementations aligned.

The security model is similarly pragmatic. MCP does not force OAuth everywhere; stdio servers are expected to rely on environment-based credentials, while HTTP servers adopt OAuth 2.1-style discovery and protected resource metadata when access control matters. The repository also frames filesystem roots as advisory boundaries that good servers should respect, which is useful because many real MCP servers expose powerful local capabilities without the protocol itself acting as a hard sandbox.

## Knowledge Map

- MCP as a bidirectional JSON-RPC protocol rather than a one-way tool API
- Initialization-time capability negotiation as the contract for optional features
- Transport split between local stdio and remote Streamable HTTP
- Roots, elicitation, and tasks as client-exposed capabilities that shape agent workflows
- Schema-driven protocol evolution with generated artifacts and CI validation
- OAuth-based discovery and token validation for HTTP deployments
- Extension negotiation for evolving beyond the core protocol

## Key Takeaways

- MCP standardizes how AI clients and servers exchange tools, resources, prompts, and workflow requests without hard-coding one host application.
- The protocol is intentionally modular: transports, capabilities, authorization, and extensions can evolve independently.
- The spec repo is not just documentation; it is the operational source of truth for schema generation, versioning, and governance.
