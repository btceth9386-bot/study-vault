python -m pdb -m mcp_server_git
```

**Claude Desktop logs:**
- **macOS:** `~/Library/Logs/Claude/mcp*.log`
- **Windows:** `%APPDATA%\Claude\logs\mcp*.log`

Log files contain:
- `mcp.log` - General MCP connection logging
- `mcp-server-{name}.log` - Server-specific stderr output

### Common Development Patterns

**Adding a new tool to a reference server:**

```typescript
// TypeScript pattern
server.registerTool(
  "new_tool_name",
  {
    description: "Tool description",
    inputSchema: {
      type: "object",
      properties: {
        param: { type: "string" }
      },
      required: ["param"]
    }
  },
  async ({ param }) => {
    // Tool implementation
    return {
      content: [{ type: "text", text: `Result: ${param}` }]
    };
  }
);
```

```python