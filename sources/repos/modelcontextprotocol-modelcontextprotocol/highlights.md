# Highlights

- `Section: Overview` The repository acts as the authoritative source for the MCP spec, schema definitions, versioned docs, and governance, not just a reference implementation.
- `Section: Protocol Specification` MCP uses bidirectional JSON-RPC 2.0 messages, so both clients and servers can issue requests and notifications when capabilities allow.
- `Section: Connection Lifecycle and Capabilities` The `initialize` request/response plus `notifications/initialized` handshake is the gate that negotiates protocol version and optional features.
- `Section: Protocol Specification / Transport Layer` MCP intentionally supports both local stdio transport and remote Streamable HTTP transport, keeping the message model stable across deployment styles.
- `Section: Authorization and Security` OAuth-style discovery is meant for HTTP servers, while stdio deployments should retrieve credentials from the environment instead of following the web authorization flow.
- `Section: Request structured user input` Elicitation gives servers a structured way to ask clients for user input instead of abusing plain text prompts for confirmation and forms.
- `Section: Server receives roots list` Roots communicate filesystem boundaries as advisory context that well-behaved servers should respect.
- `Section: Schema Development Workflow` TypeScript schema files are the single source of truth, with JSON Schema and MDX docs generated and validated in CI.
- `Section: Extensions Framework` Extensions are negotiated during initialization and require both parties to declare support before use.
