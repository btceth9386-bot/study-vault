# devhelmhq/mcp-recorder

## Summary

`mcp-recorder` is a testing utility that captures Model Context Protocol traffic into portable, versioned JSON cassettes. It sits between an MCP client and server as a proxy, records JSON-RPC requests, responses, notifications, lifecycle events, latency, and transport details, then reuses that evidence in two ways: replay serves recorded responses without contacting the real server, while verification sends recorded requests to a live server and reports structural differences. This record-replay-verify cycle turns otherwise stateful and asynchronous MCP behavior into deterministic regression tests.

The architecture separates protocol behavior from communication details. A common transport interface supports remote HTTP/SSE servers and local stdio subprocesses, while the proxy and verifier operate on the same interaction model. Replay uses selectable matching strategies: method-and-parameters matching tolerates changing request IDs and metadata, sequential matching enforces call order, and strict matching compares the complete request. Recorded response IDs are rewritten to match current client requests, and SSE responses are reconstructed when needed.

Reliability depends on controlling nondeterminism without hiding meaningful changes. The verifier removes volatile fields and performs recursive structural comparison, including JSON serialized inside strings. The scrubber removes explicitly configured secrets from metadata and responses but deliberately leaves request bodies unchanged so replay keys remain valid; sensitive request data produces a warning for manual review. Declarative YAML scenarios automate repeatable recordings, including environment interpolation, redaction rules, and tool, prompt, or resource actions. A pytest plugin then exposes replay URLs and verification results as fixtures, making cassettes usable in ordinary client-side and server-side tests. The durable lesson is that wire-level contracts become practical test assets when capture, normalization, matching, sanitization, and lifecycle management are designed together.

## Knowledge Map

- Versioned cassettes model complete MCP interaction sessions.
- Recording captures live traffic; replay isolates clients; verification detects server regressions.
- Matching strategies trade flexibility for ordering and exactness.
- Transport adapters keep HTTP/SSE and stdio behind one testing workflow.
- Scrubbing and volatility handling balance safety, determinism, and useful diffs.
- YAML scenarios and pytest fixtures turn the core engine into repeatable automation.

## Key Takeaways

- Record the wire contract when tool schemas and responses must not drift silently.
- Choose the least strict matcher that still protects the behavior under test.
- Normalize only known volatile data; broad ignores can conceal real regressions.
- Never mutate recorded requests during redaction because replay depends on their identity.
- Keep cassettes versioned, reviewable, and runnable through standard test tooling.
