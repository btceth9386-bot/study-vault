for root in roots:
    if file_path.startswith(root.uri):
        # Access allowed
        content = read_file(file_path)
```

Sources: [docs/docs/learn/client-concepts.mdx:105-153]()

## Transport Configuration

MCP servers must configure a transport layer for client communication. The choice between stdio and HTTP depends on deployment requirements.

### Transport Comparison

| Transport | Use Case | Connection Method | Authentication |
|-----------|----------|-------------------|----------------|
| stdio | Local development, Claude Desktop | Process spawn, stdin/stdout | None (local trust) |
| HTTP | Remote servers, web services | HTTP POST + SSE | OAuth 2.1, Bearer tokens |

### stdio Transport Implementation

The stdio transport is the simplest for local servers that run as spawned processes.

**Python stdio Transport:**

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("server-name")

# Register capabilities...

if __name__ == "__main__":
    mcp.run(transport='stdio')
```

**TypeScript stdio Transport:**

```typescript
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Server running on stdio");
}

main();
```

**Critical stdio Logging Rule:** Never write to stdout in stdio servers. Use stderr or file logging only, as stdout is reserved for JSON-RPC messages.

```python
# ❌ Wrong - breaks JSON-RPC protocol
print("Server started")

# ✅ Correct - writes to stderr
import logging
logging.info("Server started")
```

Sources: [docs/docs/develop/build-server.mdx:44-73](), [docs/docs/develop/build-server.mdx:252-262](), [docs/docs/develop/build-server.mdx:732-746]()

### HTTP Transport Implementation

HTTP transport enables remote server access with SSE streaming for real-time updates.

**Python HTTP Transport:**

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("server-name")