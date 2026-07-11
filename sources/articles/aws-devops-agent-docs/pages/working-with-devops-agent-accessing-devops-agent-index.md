

# Accessing DevOps Agent
<a name="working-with-devops-agent-accessing-devops-agent-index"></a>

AWS DevOps Agent supports several access methods: the web app console, Model Context Protocol (MCP) integration, Agent-to-Agent (A2A) integration, Agent Client Protocol (ACP) integration, webhooks for event-driven automation, and direct API access. Choose the method that best fits your workflow and technical requirements.

The following diagram illustrates these access methods and how they connect to the DevOps Agent service.

![Architecture diagram showing methods for accessing AWS DevOps Agent: Browser connects to Web App, IDE and MCP Client connect to MCP, Agent and Orchestrator connect to A2A and ACP, Monitoring and Ticketing systems connect to Webhooks, and Custom Apps connect to the API.](http://docs.aws.amazon.com/devopsagent/latest/userguide/images/engaging-devops-agent.png)


## DevOps Agent web app
<a name="devops-agent-web-app"></a>

The web app is the primary interface for DevOps Agent. Use conversational chat to investigate incidents, query your infrastructure, and manage recommendations. For more information, see [What is a DevOps Agent Web App?](about-aws-devops-agent-what-is-a-devops-agent-web-app.md).

## Model Context Protocol (MCP) integration
<a name="model-context-protocol-mcp-integration"></a>

You can access AWS DevOps Agent capabilities directly from MCP-compatible clients and IDEs such as Kiro, Claude Code, and Cursor. AWS DevOps Agent provides a dedicated remote MCP endpoint that you connect to using an access token or AWS SigV4 credentials. From your development environment, you can investigate incidents, optimize costs, review architecture, and map topology. For setup instructions, including the Kiro power and Claude Code plugin, see [Connect to DevOps Agent remote servers](accessing-devops-agent-connect-to-devops-agent-remote-servers.md).

The [AWS MCP Server](https://docs.aws.amazon.com/aws-mcp/latest/userguide/what-is-mcp-server.html) is also available for direct AWS API access, and serves as a fallback when the remote server endpoint is unavailable.

## Agent-to-Agent (A2A) integration
<a name="agent-to-agent-a2a-integration"></a>

You can connect autonomous agents to AWS DevOps Agent through a dedicated Agent-to-Agent (A2A) v1.0 remote endpoint, using an access token or AWS SigV4 credentials. Agents can send messages, stream responses, and manage asynchronous tasks for agent-to-agent communication. For setup instructions, see [Connect to DevOps Agent remote servers](accessing-devops-agent-connect-to-devops-agent-remote-servers.md).

## Agent Client Protocol (ACP) integration
<a name="agent-client-protocol-acp-integration"></a>

You can invoke AWS DevOps Agent programmatically using the [Agent Client Protocol (ACP)](https://agentclientprotocol.com/get-started/introduction). For a sample implementation, see the [sample-aws-devops-agent-acp-mcp](https://github.com/aws-samples/sample-aws-devops-agent-acp-mcp) repository on GitHub.

## Webhooks
<a name="webhooks"></a>

Webhooks allow external systems to automatically trigger AWS DevOps Agent investigations. External systems such as ticketing platforms and monitoring tools can send HTTP requests when incidents occur. For more information, see [Invoking DevOps Agent through Webhook](configuring-integrations-and-knowledge-invoking-devops-agent-through-webhook.md).

## AWS DevOps Agent API
<a name="aws-devops-agent-api"></a>

AWS DevOps Agent provides APIs for programmatic access to agent capabilities. You can create and manage Agent Spaces, trigger investigations, and retrieve findings. For more information, see the [AWS DevOps Agent API Reference](https://docs.aws.amazon.com/devopsagent/latest/APIReference/).