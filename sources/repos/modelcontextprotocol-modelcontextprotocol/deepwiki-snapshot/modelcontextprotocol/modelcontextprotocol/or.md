pip install mcp-server-name
python -m mcp_server_name
```

**Sources:** [docs/examples.mdx:38-55]()

## Testing and Debugging

### MCP Inspector

Interactive testing tool for server development:

**Location:** `github.com/modelcontextprotocol/inspector`

**Features:**
- Browse available tools, resources, and prompts
- Execute tools with custom inputs
- View real-time notifications
- Monitor request/response logs

**Usage:**

```bash
npx @modelcontextprotocol/inspector path/to/server
```

**Sources:** [docs/docs/learn/architecture.mdx:19]()

### Testing with Claude Desktop

1. Add server to `claude_desktop_config.json`
2. Restart Claude Desktop completely
3. Verify hammer icon appears in chat input
4. Click to see available tools
5. Test tool execution with approval dialogs

**Debugging Logs:**

- **macOS:** `~/Library/Logs/Claude/mcp*.log`
- **Windows:** `%APPDATA%\Claude\logs\mcp*.log`

View recent logs:

```bash