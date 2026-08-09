mcp-recorder verify --cassette cassettes/demo.json --target http://localhost:8000
```

For installation instructions and a walkthrough of your first recording, see [Getting Started](#1.1).

---

### Subsystem Overview

*   **Transport Layer**: Manages the lifecycle of the connection to the MCP server. The `StdioTransport` handles subprocess management and non-blocking I/O, while `HttpTransport` manages SSE streams and session IDs [src/mcp_recorder/transport.py:14-20]().
*   **Proxy (Recording Engine)**: Acts as a Starlette-based reverse proxy that captures `JSON-RPC` requests and responses in real-time [src/mcp_recorder/proxy.py:91-105]().
*   **Replay & Matcher**: The `SequentialMatcher` and `MethodParamsMatcher` determine which recorded response to return based on the incoming request's method and parameters [src/mcp_recorder/matcher.py:18-25]().
*   **Verifier & Scrubber**: The verifier uses `_deep_diff` to compare server responses against the cassette, while the scrubber redacts sensitive information like `API_KEY`s before persistence [src/mcp_recorder/verifier.py:155-160](), [src/mcp_recorder/scrubber.py:28-35]().

Sources: [src/mcp_recorder/transport.py:14-20](), [src/mcp_recorder/proxy.py:91-105](), [src/mcp_recorder/matcher.py:18-25](), [src/mcp_recorder/verifier.py:155-160](), [src/mcp_recorder/scrubber.py:28-35]()

# Getting Started




`mcp-recorder` is a tool for recording, replaying, and verifying Model Context Protocol (MCP) interactions, functioning similarly to VCR.py but tailored for the specific stateful and asynchronous nature of MCP. It supports both HTTP (SSE) and `stdio` (subprocess) transports, capturing wire-level exchanges into portable JSON "cassette" files.

## Installation and Requirements

The project requires **Python 3.11 or higher** [pyproject.toml:10-22](). It leverages `uv` for modern dependency management and `uvicorn`/`starlette` for the proxy and mock server components [pyproject.toml:23-30]().

### Using pip
```bash
pip install mcp-recorder
```

### Using uv (Recommended)
For development or project integration:
```bash
uv add mcp-recorder