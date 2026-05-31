if __name__ == "__main__":
    mcp.run(
        transport='sse',
        host='0.0.0.0',
        port=8000
    )
```

**TypeScript HTTP Transport:**

```typescript
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";

const transport = new SSEServerTransport("/mcp", (message) => {
  // Send SSE message to client
  response.write(`data: ${JSON.stringify(message)}\n\n`);
});

await server.connect(transport);
```

### Authorization for HTTP Servers

HTTP servers should implement OAuth 2.1 for secure authentication:

```python