npx -y @modelcontextprotocol/server-filesystem C:\Users\username\Documents
```

**Sources:** [docs/examples.mdx:16](), [docs/docs/develop/connect-local-servers.mdx:90-147](), [docs/docs/learn/client-concepts.mdx:106-138]()

## Git Server

### Purpose

The Git server provides comprehensive tools for reading, searching, and manipulating Git repositories. It enables LLMs to inspect repository structure, search commit history, analyze code changes, and understand repository evolution without requiring direct filesystem access.

### Package Information

- **Package:** `mcp-server-git`
- **Repository:** [modelcontextprotocol/servers/tree/main/src/git](https://github.com/modelcontextprotocol/servers/tree/main/src/git)
- **Language:** Python
- **Execution:** `uvx mcp-server-git` or `pip install mcp-server-git && python -m mcp_server_git`

### Capabilities

| Tool Category | Specific Operations |
|--------------|---------------------|
| **Repository Reading** | Clone repository, read file contents at specific commits |
| **Commit Analysis** | View commit history, show commit details, generate diffs |
| **Branch Operations** | List branches, compare branches, show branch history |
| **Search Functions** | Search commits by message, author, or file changes |
| **Status Inspection** | Show repository status, list modified files |

### Tool Examples

**Commit History:**
```python
# Lists commits with author, date, and message
# Supports filtering by author, date range, file path
# Returns structured commit objects
```

**Diff Generation:**
```python