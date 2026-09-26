# Highlights

- `p. 7` The interoperability stack assigns distinct roles to MCP, skills, A2A, A2UI, AP2, and UCP instead of treating every external interaction as a custom tool wrapper.
- `pp. 11–12` MCP onboarding follows discovery, configuration, and connection: find a suitable server, define scope and authentication, then verify its tools and schemas through the handshake.
- `pp. 13–14` A shared protocol changes model-to-tool integration effort from pairwise `O(N × M)` adapters to `O(N + M)` protocol endpoints.
- `pp. 15–16` Safe MCP consumption requires server auditing, least-privilege credentials, development data, read-only access where possible, human visibility for tool inputs, and usage logs.
- `pp. 18–20` Specializing agents reduces tool search space, attention dilution, contextual load, and the blast radius of one failing instruction or tool.
- `pp. 23–24` A bounded tool returns a result, while an unbounded delegated agent may clarify, pause, negotiate, and resume; A2A isolates that stateful collaboration from MCP's structured tool layer.
- `pp. 25–28` Agent Cards describe capabilities and interaction requirements, registries enable discovery, and executors translate A2A requests into framework-specific agent calls.
- `pp. 33–35` A2UI communicates declarative UI intent through trusted components, separating agent-selected composition from safe native rendering on the client.
- `pp. 35–42` LLM-generated layouts fit intent-driven interfaces, deterministic tool templates fit stable layouts, and hybrid data-plus-UI output supports both API and human consumers.
- `pp. 45–46` UCP handles merchant interaction and order construction, while AP2 uses signed mandates and verification to constrain and audit payment authorization.
