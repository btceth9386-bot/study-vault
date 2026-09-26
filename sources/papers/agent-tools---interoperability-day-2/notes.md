# Agent Tools & Interoperability — Day 2

## Summary

This paper presents open protocols as the connective tissue of agentic systems. MCP standardizes how models discover and invoke tools, reducing a bespoke N-model-by-M-tool integration matrix to adapters on each side of a shared protocol. Its practical onboarding flow is discovery, configuration, and connection: prefer official or governed servers, scope credentials and permissions, verify schemas through the handshake, and inspect the transport directly when calls fail. The paper repeatedly stresses that protocol convenience does not replace security; public servers require auditing, secrets must stay outside prompts and code, production data should be isolated, and high-impact calls should remain visible to humans.

The architecture then moves from a single overloaded agent toward specialized agents. Internal specialization narrows each agent's prompt, tools, and context, while distributed specialists require a common collaboration protocol. A2A fills that role for multi-turn, stateful delegation. Unlike a bounded tool call, a delegated agent may pause, ask questions, negotiate trade-offs, and resume. Agent Cards describe capabilities, security expectations, and interaction schemas, while registries make those specialists discoverable. Executors and endpoints translate between A2A and the underlying agent framework.

A2UI extends interoperability to human interfaces. Agents emit declarative UI intent rather than executable frontend code or raw JSON. A trusted client-side component catalog constrains what can be rendered. Layout may be generated dynamically by an LLM when user intent determines the interface, or returned by a deterministic tool template when inputs determine a stable layout. Hybrid responses can include both raw data and UI so API and human clients consume the same result appropriately.

Finally, UCP and AP2 divide agentic commerce responsibilities. UCP standardizes merchant discovery, catalog, cart, and order interactions; AP2 provides signed mandates, authorization, and auditable payment intent. Together, the protocols let agents act across tools, specialists, interfaces, and transactions without rebuilding a custom integration at every boundary.

## Knowledge Map

- MCP: tool discovery, configuration, transport, schema validation, and scoped access
- Agent specialization: focused contexts and smaller tool search spaces
- A2A: stateful delegation, Agent Cards, registries, executors, and endpoints
- A2UI: declarative interfaces rendered from trusted component catalogs
- UCP and AP2: commerce orchestration separated from payment authorization

## Key Takeaways

- Use protocols to replace pairwise adapters, but keep security and governance explicit.
- Use MCP for bounded tool operations and A2A when another participant must own an evolving task.
- Prefer specialist agents when narrower tools and context improve reliability or external expertise already exists.
- Render agent-generated UI through trusted catalogs, never arbitrary executable code.
- Separate what an agent buys from how payment is authorized and proven.
