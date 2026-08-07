# Highlights

- `docs/gen-ai/gen-ai-spans.md:27-45` GenAI inference spans use a consistent operation-and-model naming pattern and distinguish remote client calls from in-process execution.
- `docs/gen-ai/gen-ai-spans.md:120-300` Separate spans model embeddings, retrieval, memory access, and tool execution instead of collapsing an entire AI workflow into one model-call span.
- `docs/gen-ai/gen-ai-agent-spans.md:13-28` Agent creation, agent invocation, workflow orchestration, and planning form a trace hierarchy for multi-step agent behavior.
- `model/gen-ai/spans.yaml:50-61` Prompt and response content attributes are opt-in because they may expose sensitive or high-volume data.
- `docs/gen-ai/gen-ai-spans.md:352-376` Instrumentation can record content inline or upload it externally and retain only a URL and upload status.
- `docs/gen-ai/gen-ai-spans.md:383-400` Streaming spans stay open until the stream ends, associating chunk events and final-only usage attributes with one operation.
- `docs/gen-ai/gen-ai-input-messages.json:52-225` Messages are structured as roles plus typed parts for text, blobs, reasoning, tool requests, and tool responses.
- `docs/gen-ai/gen-ai-tool-definitions.json:3-51` Tool definitions use a shared name, description, and JSON Schema contract rather than provider-specific payload shapes.
- `docs/gen-ai/anthropic.md:45-70` Provider conventions refine common requirements and add provider-only measurements such as prompt-cache token usage.
- `docs/gen-ai/mcp.md:58-153` MCP client and server spans map JSON-RPC methods to traceable operations and propagate context through protocol metadata.
- `reference/README.md:7-44` Deterministic reference scenarios compare emitted telemetry with the semantic model and publish per-library coverage.
- `.github/instructions/reference-scenarios.instructions.md:8-52` Reference scenarios must derive attributes from public API inputs and outputs, proving that proposed fields are genuinely capturable.
