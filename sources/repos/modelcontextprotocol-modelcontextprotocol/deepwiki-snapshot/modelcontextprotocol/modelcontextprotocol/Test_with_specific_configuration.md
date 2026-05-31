npx @modelcontextprotocol/inspector npx -y @modelcontextprotocol/server-filesystem /tmp
```

The Inspector provides:
- **Tool testing:** Execute tools and see results
- **Resource browsing:** List and read resources
- **Prompt testing:** Invoke prompts with parameters
- **Notification monitoring:** Observe real-time notifications
- **Error debugging:** View detailed error messages

### Debugging Reference Servers

**TypeScript server debugging:**

```bash
# Add debugging output to server code
console.error("Debug message");  // Writes to stderr, visible in logs

# Run with Node.js inspector
node --inspect build/index.js
```

**Python server debugging:**

```bash