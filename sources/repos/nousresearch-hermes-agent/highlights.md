# Highlights

- `README.md L15-L17`: Hermes is presented as a self-improving agent with a built-in learning loop, persistent knowledge, provider flexibility, and no model lock-in.
- `README.md L20-L26`: The feature table defines the main product pillars: terminal UI, messaging gateway, memory and skills, cron automation, subagent delegation, multiple execution backends, and RL-oriented research support.
- `README.md L82-L98`: The CLI vs messaging section shows Hermes as a shared runtime with different front doors rather than separate products.
- `Section: ACP Server and IDE Integration` in `notes.md`: Hermes implements ACP so the agent can act as a backend for AI-native editors like VS Code and Zed.
- `Section: Session Management` in `notes.md`: ACP sessions are persisted in a shared session database and can be restored across process restarts.
- `Section: Context Compression` in `notes.md`: Conversation history is surgically compacted when token usage crosses a threshold instead of simply truncating old context.
- `Section: Tool System` in `notes.md`: Built-in tools and MCP server tools are unified under a tool registry and grouped into configurable toolsets.
- `Section: Cron and Scheduled Tasks` in `notes.md`: Hermes can run natural-language jobs unattended, store outputs, and deliver results back to configured platforms.
- `Section: TUI Terminal User Interface` in `notes.md`: The TUI uses a Node.js frontend and Python JSON-RPC gateway, showing a split frontend/backend architecture even for terminal UX.
- `Section: Toolset Distributions` in `notes.md`: Evaluation runs can sample toolsets probabilistically, which decouples benchmark scenarios from a fixed always-on tool surface.
