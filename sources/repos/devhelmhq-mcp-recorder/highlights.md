# Highlights

- [`Architecture.md` L5-L35](deepwiki-snapshot/devhelmhq/mcp-recorder/Architecture.md) Recording routes MCP JSON-RPC traffic through a proxy and transport, captures each exchange, and persists it as a cassette.
- [`Proxy_Recording_Engine.md` L46-L91](deepwiki-snapshot/devhelmhq/mcp-recorder/Proxy_Recording_Engine.md) The proxy classifies lifecycle events, notifications, and requests while handling both transport-backed forwarding and HTTP/SSE stream capture.
- [`Replay_Engine_and_Matcher.md` L39-L65](deepwiki-snapshot/devhelmhq/mcp-recorder/Replay_Engine_and_Matcher.md) Replay offers method-and-parameters, sequential, and strict matching, then rewrites current request IDs and restores SSE framing.
- [`Verifier_and_Scrubber.md` L3-L20](deepwiki-snapshot/devhelmhq/mcp-recorder/Verifier_and_Scrubber.md) Verification re-executes recorded interactions and compares normalized expected and actual responses structurally.
- [`Verifier_and_Scrubber.md` L54-L73](deepwiki-snapshot/devhelmhq/mcp-recorder/Verifier_and_Scrubber.md) Scrubbing redacts configured secrets from metadata and responses but preserves request bodies to avoid breaking deterministic replay.
- [`Transport_Layer.md` L3-L67](deepwiki-snapshot/devhelmhq/mcp-recorder/Transport_Layer.md) A shared asynchronous transport contract hides HTTP session/SSE handling and stdio subprocess routing from higher-level components.
- [`Scenario_Execution_Pipeline.md` L3-L103](deepwiki-snapshot/devhelmhq/mcp-recorder/Scenario_Execution_Pipeline.md) Declarative scenarios resolve a target, start a proxy, dispatch MCP actions, scrub the captured cassette, and save it.
- [`pytest_Integration.md` L19-L46](deepwiki-snapshot/devhelmhq/mcp-recorder/pytest_Integration.md) A cassette marker connects tests to replay and verification fixtures for client-side mocking and server-side regression checks.
