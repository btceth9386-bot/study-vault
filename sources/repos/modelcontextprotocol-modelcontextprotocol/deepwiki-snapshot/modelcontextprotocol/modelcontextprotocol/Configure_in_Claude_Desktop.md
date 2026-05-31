{
  "mcpServers": {
    "everything": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-everything"]
    }
  }
}
```

**Sources:** [docs/examples.mdx:14]()

## Fetch Server

### Purpose

The Fetch server provides web content retrieval and conversion capabilities optimized for LLM consumption. It fetches web pages and converts HTML content into clean, LLM-friendly formats that maximize information density while minimizing token usage.

### Package Information

- **Package:** `@modelcontextprotocol/server-fetch`
- **Repository:** [modelcontextprotocol/servers/tree/main/src/fetch](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch)
- **Language:** TypeScript
- **Execution:** `npx -y @modelcontextprotocol/server-fetch`

### Capabilities

| Capability | Description |
|------------|-------------|
| **Web Fetching Tool** | Retrieves web page content via HTTP/HTTPS |
| **Content Conversion** | Converts HTML to clean markdown or plain text |
| **Resource Caching** | Caches fetched content as accessible resources |
| **LLM Optimization** | Strips unnecessary HTML/CSS/JS while preserving semantic content |

### Key Features

- User-agent header customization for reliable access
- Automatic handling of redirects and common HTTP patterns
- Content extraction that preserves document structure
- Memory-efficient streaming for large pages
- Error handling for network issues and invalid URLs

### Execution Example

```bash
# Run directly with npx
npx -y @modelcontextprotocol/server-fetch

# Configure in Claude Desktop
{
  "mcpServers": {
    "fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"]
    }
  }
}
```

**Sources:** [docs/examples.mdx:15]()

## Filesystem Server

### Purpose

The Filesystem server provides secure file operations with configurable access controls. It implements filesystem boundaries (roots) to prevent unauthorized access outside specified directories. This server demonstrates the MCP roots concept and secure file handling patterns.

### Package Information

- **Package:** `@modelcontextprotocol/server-filesystem`
- **Repository:** [modelcontextprotocol/servers/tree/main/src/filesystem](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)
- **Language:** TypeScript
- **Execution:** `npx -y @modelcontextprotocol/server-filesystem /path/to/allowed/files`

### Capabilities

| Tool | Purpose | Security Consideration |
|------|---------|----------------------|
| `read_file` | Read file contents | Path must be within allowed directories |
| `write_file` | Write content to file | Creates parent directories if needed |
| `list_directory` | List directory contents | Recursive traversal respects boundaries |
| `move_file` | Move/rename files | Both source and destination must be within allowed paths |
| `search_files` | Search for files by pattern | Searches only within allowed directories |
| `get_file_info` | Get file metadata | Returns size, modified time, type |

### Resources

The server exposes file contents as resources using the `file://` URI scheme:

- URI pattern: `file:///absolute/path/to/file`
- MIME type detection based on file extension
- Automatic text encoding detection for text files

### Security Model

**Path Validation:**
```typescript
// All file operations validate paths against allowed directories
// Symlinks are resolved and validated
// Parent directory traversal (..) is checked
// Operations outside allowed paths are rejected
```

The security model implements defense-in-depth:
1. Command-line arguments define allowed directories
2. All paths are normalized and resolved
3. Symlink targets are validated against boundaries
4. Operations fail-fast with clear error messages

### Configuration Pattern

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/username/Desktop",
        "/Users/username/Documents"
      ]
    }
  }
}
```

**Multiple allowed directories:** Specify multiple paths as separate arguments to grant access to different filesystem locations.

### Execution Examples

```bash