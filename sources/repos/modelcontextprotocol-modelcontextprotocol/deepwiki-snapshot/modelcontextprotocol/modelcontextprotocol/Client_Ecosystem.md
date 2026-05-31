This page documents the MCP client ecosystem: the applications that integrate with MCP servers to expose tools, resources, prompts, and other capabilities to users and AI models. The ecosystem includes desktop applications, IDE extensions, web platforms, CLI tools, and specialized frameworks. For information about building MCP clients or using the client SDKs, see [Integration Patterns](#4.2). For details about the MCP protocol features themselves, see [Protocol Specification](#2).

## Client Feature Support

The MCP client ecosystem exhibits a power law distribution in feature adoption. The protocol defines twelve capabilities across server-exposed, client-exposed, and lifecycle categories. Actual client implementations range from full-featured platforms supporting all capabilities to minimal integrations that expose only tool invocation.

**Feature Categories**

The feature matrix in [docs/clients.mdx:8-23]() documents twelve distinct capabilities organized by category:

| Category | Feature | Description |
|----------|---------|-------------|
| Server-Exposed | Resources | Attachment of local files and data via URI templates |
| Server-Exposed | Prompts | Prompt template library with arguments |
| Server-Exposed | Tools | Function invocation with input/output schemas |
| Server-Exposed | Instructions | Server-provided usage metadata and guidance |
| Server-Exposed | Discovery | Dynamic tool/resource registration updates |
| Client-Exposed | Sampling | LLM completion requests from servers |
| Client-Exposed | Elicitation | User input collection (form and URL modes) |
| Client-Exposed | Roots | Filesystem boundary declarations |
| Extensions | CIMD | Client ID Metadata Document support (SEP-991) |
| Extensions | DCR | Dynamic Client Registration support (RFC 7591) |
| Extensions | Tasks | Long-running operation tracking |
| Extensions | Apps | Interactive HTML interfaces (MCP Apps) |

**Adoption Patterns**

The `Tools` capability represents the baseline value proposition, with ~95% adoption across all clients. This validates MCP's primary use case: enabling LLMs to invoke executable functions. Secondary features like `Resources` (~40%) and `Prompts` (~40%) see moderate adoption, while advanced capabilities like `Sampling` (~15%), `Tasks` (~10-15%), and `Apps` serve specialized use cases.

Sources: [docs/clients.mdx:8-23]()

## Client Transport and Configuration

Clients choose between two transport mechanisms based on deployment model and server location:

**Transport Mechanisms**

| Transport | Deployment | Authentication | Examples |
|-----------|-----------|-----------------|----------|
| stdio | Local process | Environment variables, embedded credentials | Claude Desktop, Continue, Cline, Amazon Q CLI |
| Streamable HTTP + SSE | Remote servers | OAuth 2.1 (mandatory) | Claude.ai, ChatGPT, Glama, Gemini |

The stdio transport is used by desktop applications and IDE extensions for local server connections, characterized by zero network overhead and process isolation. The Streamable HTTP transport with Server-Sent Events is required for remote, multi-tenant server deployments and mandates OAuth 2.1 authorization (see [Authorization and Security](#3)).

**Configuration Patterns**

Clients employ three primary configuration strategies:

| Strategy | Mechanism | Examples |
|----------|-----------|----------|
| File-Based | JSON configuration files | `claude_desktop_config.json` (Claude Desktop), `mcp.json` (VS Code) |
| UI-Based | Graphical server management | Web platforms (Claude.ai, ChatGPT), desktop apps (BoltAI, Chatbox) |
| Runtime | Environment variables, dynamic discovery | CLI tools, framework integrations |

Desktop clients typically use JSON configuration files to define server connections with command arguments. Web and desktop applications provide graphical interfaces for server connection management, OAuth credential flow initiation, and feature enable/disable per server. Advanced clients support environment variable substitution for credentials and dynamic server registration via discovery protocols.

Sources: [docs/clients.mdx:1-220](), [docs/tutorials/security/authorization.mdx:1-50]()

## Client Directory and Feature Matrix

The complete client directory is maintained in [docs/clients.mdx]() with a searchable, filterable interface. The feature matrix uses color-coded badges to indicate capability support:

**Feature Badge Colors**

| Color | Features |
|-------|----------|
| Blue | Server capabilities (Resources, Prompts, Tools) |
| Green | Client capabilities (Sampling, Roots, Elicitation) |
| Purple | Lifecycle features (Instructions, Discovery) |
| Yellow | Authorization extensions (CIMD, DCR) |
| Orange | Advanced features (Tasks, Apps) |

The `McpClient` component in [docs/clients.mdx:156-278]() renders each client entry with:
- Client name and homepage link
- Supported features with color-coded badges
- Source code link (if available)
- Configuration instructions
- Expandable description with key features

The `ClientFilter` component in [docs/clients.mdx:82-153]() enables filtering by:
- Feature selection (multi-select)
- Text search by client name
- Real-time result count display

This standardized format enables developers to quickly assess client compatibility for their use cases.

Sources: [docs/clients.mdx:1-220]()

## Notable Client Implementations

The client ecosystem spans multiple categories based on feature support and deployment model. Key implementations include:

**Desktop Applications**

- **Claude Desktop App** [docs/clients.mdx:701-720](): Anthropic's flagship client with Resources, Prompts, and Tools support. Uses `claude_desktop_config.json` for local server configuration via stdio transport. Supports both local servers and remote servers via DCR.

- **BoltAI** [docs/clients.mdx:562-582](): Native macOS client supporting multiple AI providers (OpenAI, Anthropic, Google AI, Ollama). Features MCP tool integrations, quick setup via Claude Desktop import, and remote MCP server support in mobile app.

- **AIQL TUUI** [docs/clients.mdx:367-389](): Native cross-platform desktop client supporting multiple AI providers (Anthropic, OpenAI, Deepseek, Qwen). Implements dynamic LLM/agent switching, configurable tools, advanced sampling control, and cross-platform compatibility (macOS, Windows, Linux).

**IDE Extensions**

- **Continue** [docs/clients.mdx:795-811](): Open-source AI code assistant supporting VS Code and JetBrains. Surfaces MCP resources via `@` mentions, prompts as slash commands, and tools directly in chat. Compatible with any LLM provider.

- **Cline** [docs/clients.mdx:740-754](): Autonomous coding agent in VS Code. Unique in its natural language tool creation and sharing of custom MCP servers via `~/Documents/Cline/MCP` directory.

- **Cursor** [docs/clients.mdx:829-846](): AI code editor with support for MCP tools in Cursor Composer, roots, prompts, elicitation, and both STDIO and SSE transports.

**Web Platforms**

- **Claude.ai** [docs/clients.mdx:722-737](): Anthropic's web-based assistant with support for remote MCP servers via integrations UI. Supports Resources, Prompts, Tools, CIMD, and DCR.

- **ChatGPT** [docs/clients.mdx:635-650](): OpenAI's assistant with MCP support for remote servers via connections UI in settings. Enterprise-grade security and compliance features. Supports Tools and DCR.

- **Gemini CLI** [docs/clients.mdx:975-983](): Open-source AI agent bringing Gemini into the terminal. Supports Prompts, Tools, Instructions, and DCR.

**Framework Integrations**

- **fast-agent** [docs/clients.mdx:898-913](): Python Agent framework with full multi-modal support (PDF, Image) based on MCP native types. Includes interactive frontend for development and diagnosis, built-in "Building Effective Agents" workflows, and ability to deploy agents as MCP servers.

- **Genkit** [docs/clients.mdx:1002-1015](): Cross-language SDK for building GenAI features. The `genkitx-mcp` plugin enables consuming MCP servers as a client or creating MCP servers from Genkit tools and prompts.

- **BeeAI Framework** [docs/clients.mdx:541-560](): Open-source framework for building agentic workflows. Includes native MCP Tool feature for seamless integration of MCP servers into workflows.

Sources: [docs/clients.mdx:1-220]()

## Client Implementation Patterns

**SDK Usage**

Clients integrate with MCP servers using language-specific SDKs. The Java SDK provides both synchronous and asynchronous client APIs:

```java
// Sync client example
McpSyncClient client = McpClient.sync(transport)
    .requestTimeout(Duration.ofSeconds(10))
    .capabilities(ClientCapabilities.builder()
        .roots(true)
        .sampling()
        .elicitation()
        .build())
    .build();

client.initialize();
ListToolsResult tools = client.listTools();
CallToolResult result = client.callTool(
    new CallToolRequest("calculator", Map.of("a", 2, "b", 3))
);
```

See [Java MCP Client](/sdk/java/mcp-client) for complete SDK documentation.

**Transport Implementation**

Clients implement transport-specific handlers:

| Transport | Client Implementation | Key Classes |
|-----------|----------------------|-------------|
| stdio | Process spawning + stdin/stdout | `StdioClientTransport` |
| Streamable HTTP | HTTP POST/GET + SSE | `HttpClientStreamableHttpTransport`, `HttpClientSseClientTransport` |
| Spring WebFlux | Reactive HTTP streaming | `WebClientStreamableHttpTransport`, `WebFluxSseClientTransport` |

**Capability Negotiation**

During initialization, clients declare supported capabilities via `ClientCapabilities`:

```java
ClientCapabilities.builder()
    .roots(true)           // Filesystem boundary support
    .sampling()            // LLM completion requests
    .elicitation()         // User input collection
    .build()
```

The server responds with `ServerCapabilities` indicating which features it exposes. This negotiation enables graceful degradation when clients and servers have mismatched feature support.

Sources: [docs/sdk/java/mcp-client.mdx:14-150](), [docs/clients.mdx:1-220]()

## Ecosystem Growth Metrics

The client ecosystem experienced explosive growth through 2024-2025:

- **September 2024**: Initial batch of clients documented in MCP Registry
- **November 2025**: 96+ clients documented, representing significant diversification across:
  - Desktop applications (Claude Desktop, BoltAI, Chatbox)
  - IDE extensions (VS Code, JetBrains, Continue, Cline)
  - Web platforms (Claude.ai, ChatGPT, Glama)
  - CLI tools (Amazon Q CLI, goose, gptme)
  - Specialized frameworks (fast-agent, Swarms, BeeAI)

The 96+ documented clients represent only clients with verified MCP support. The actual ecosystem is likely larger, as the registry focuses on clients with public documentation or community-verified implementations.

**Platform Distribution**

Clients span multiple computing platforms:
- Desktop: macOS, Windows, Linux native applications
- Web: Browser-based platforms requiring no installation
- Mobile: iOS and Android clients (BoltAI mobile, WhatsMCP)
- CLI: Terminal-based tools for developer workflows
- IDE: Editor extensions and plugins

This platform diversity validates MCP's design as a universal protocol for AI-to-application integration, independent of deployment environment.

Sources: [docs/clients.mdx:1-220](), [blog/content/posts/2025-11-25-first-mcp-anniversary.md:1-272]()