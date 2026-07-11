

# Connect to DevOps Agent remote servers
<a name="accessing-devops-agent-connect-to-devops-agent-remote-servers"></a>

AWS DevOps Agent provides dedicated remote servers for the Model Context Protocol (MCP) and Agent-to-Agent (A2A) protocol. Use these servers to connect your IDE, CLI, or custom agent integrations to an Agent Space.

## Supported protocols
<a name="supported-protocols"></a>
+ **MCP (Model Context Protocol)** – Connect IDE and CLI clients such as Kiro, Claude Code, Cursor, and other MCP-compatible tools.
+ **A2A (Agent-to-Agent) v1.0** – Connect autonomous agents for agent-to-agent communication.

## Endpoints
<a name="endpoints"></a>

Remote servers are available at a regional URL:

```
https://connect.aidevops.{region}.api.aws
```


| Protocol | Path | Method | 
| --- | --- | --- | 
| MCP | /mcp | POST | 
| A2A | /a2a/\* | POST | 
| A2A agent card | /.well-known/agent-card.json | GET | 

For the list of available Regions, see [Supported Regions](about-aws-devops-agent-supported-regions.md).

## Authentication
<a name="authentication"></a>

Two authentication methods are available for both MCP and A2A endpoints:
+ **Access token (Bearer)** – A single token scoped to one Agent Space. Simplest setup for individual use.
+ **AWS SigV4** – AWS credential-based authentication. Supports multiple Agent Spaces and integrates with existing AWS identity governance. Handled automatically by [mcp-proxy-for-aws](https://github.com/aws/mcp-proxy-for-aws), a local proxy that signs requests using your AWS credentials.

## Create an access token
<a name="create-an-access-token"></a>

### Prerequisites
<a name="prerequisites"></a>
+ The access tokens feature must be enabled on your Agent Space.
+ You must have IAM permissions to manage access tokens (`aidevops:CreateAccessToken`, `aidevops:RevokeAccessToken`, `aidevops:RotateAccessToken`). For the full list, see [DevOps Agent IAM permissions](aws-devops-agent-security-devops-agent-iam-permissions.md).

### Enable access tokens
<a name="enable-access-tokens"></a>

1. Sign in to the AWS Management Console and open the AWS DevOps Agent console.

1. Choose your Agent Space.

1. Choose the **Configuration** tab.

1. In the **Access tokens** section, choose **Enable**.

1. Confirm the action.

### Create a token
<a name="create-a-token"></a>

1. Open the DevOps Agent web app for your Agent Space, then from the navigation menu, choose **Settings**, then choose **Access Tokens**.

1. Choose **Generate token**.

1. Enter a name for the token.

1. Choose a scope:
   + `read` – View investigations, recommendations, chats, and Agent Space resources.
   + `operate` – Full access. Includes everything in `read`, plus send messages, create chats, and manage backlog tasks and recommendations.

1. Choose a client type:
   + `human` – For IDE and CLI usage (Kiro, Claude Code, Cursor, and other interactive tools).
   + `agent` – For autonomous A2A integrations and programmatic agents.

1. Set an expiration (1 to 60 days).

1. Copy the token value and store it in a safe, secure location, such as [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html). You cannot retrieve it again.

After creating a token, the web app displays a configuration example that you can copy directly into your client.

## Connect with Kiro
<a name="connect-with-kiro"></a>

For [Kiro](https://kiro.dev/) users, a dedicated **AWS DevOps Agent** power is available from the IDE or from the [Kiro Powers marketplace](https://kiro.dev/powers/#aws-devops-agent).

**Step 1: Install the power**

Install the **aws-devops-agent** power from the Powers marketplace.

**Step 2: Set environment variables**

Set the following environment variables to configure the connection:

```
DEVOPS_AGENT_TOKEN=<your-access-token>
DEVOPS_AGENT_REGION=<your-agent-space-region>
```

**Step 3: Approve the variables in Kiro**

Go to **Settings** > **MCP Approved Env Vars** and approve `DEVOPS_AGENT_TOKEN` and `DEVOPS_AGENT_REGION`. Kiro does not pass environment variables to MCP servers until they are approved.

**Step 4: Restart Kiro**

Restart Kiro to apply the changes.

The Kiro power includes `aws-mcp` as a fallback, which provides direct AWS API access when the remote server endpoint is unavailable.

## Connect with Claude Code
<a name="connect-with-claude-code"></a>

For [Claude Code](https://code.claude.com/docs/en/overview) users, AWS DevOps Agent is available from the **aws-agents-for-devsecops** Claude plugin, which brings both AWS DevOps Agent and AWS Security Agent capabilities into Claude. Install it from [Claude plugins](https://claude.com/plugins/aws-agents-for-devsecops) or the [source repository](https://github.com/aws/agent-toolkit-for-aws/tree/main/plugins/aws-agents-for-devsecops).

1. Install the **aws-agents-for-devsecops** plugin.

1. Run the `/aws-agents-for-devsecops:setup-devops-agent` command to configure your connection.

## Connect with other MCP clients
<a name="connect-with-other-mcp-clients"></a>

For any MCP-compatible client, configure the server with:
+ **URL** – `https://connect.aidevops.{region}.api.aws/mcp`
+ **Authorization header** – `Bearer <your-token>`
+ **Timeout** – 120 seconds minimum (initial responses can take 5–30 seconds; ongoing chat sessions may take longer)

This configuration also works with Kiro and Claude Code if you prefer to configure the connection manually instead of using the dedicated power or plugin.

Example MCP configuration:

```
{
  "mcpServers": {
    "aws-devops-agent": {
      "url": "https://connect.aidevops.{region}.api.aws/mcp",
      "headers": {
        "Authorization": "Bearer <your-access-token>"
      }
    }
  }
}
```

Replace `{region}` with your Agent Space's Region (for example, `us-east-1`) and `<your-access-token>` with the token value.

## Use SigV4 authentication
<a name="use-sigv4-authentication"></a>

SigV4 authentication uses your AWS credentials instead of an access token. The Kiro power and Claude Code plugin include built-in SigV4 support through `mcp-proxy-for-aws`, which signs requests using your local AWS credentials.

### When SigV4 is used
<a name="when-sigv4-is-used"></a>
+ As a **fallback** when the access token is not configured or fails (expired, invalid).
+ As the **primary** auth when you have multiple Agent Spaces and need to route by `agent_space_id` per tool call.
+ As a **user choice** – in Claude Code, run the setup skill to switch from Bearer token to SigV4 auth.

### Prerequisites
<a name="prerequisites"></a>
+ AWS credentials available in the environment (through SSO, environment variables, or credential file).
+ Your credentials must have permission to invoke AWS DevOps Agent actions. For the required permissions, see [DevOps Agent IAM permissions](aws-devops-agent-security-devops-agent-iam-permissions.md).
+ `uvx` installed (the proxy runs through `uvx mcp-proxy-for-aws@latest`).

### Example configuration
<a name="example-configuration"></a>

To configure an MCP client to use SigV4 instead of an access token, run the server through `mcp-proxy-for-aws`. Replace `{region}` with your Agent Space's Region (for example, `us-east-1`):

```
{
  "mcpServers": {
    "aws-devops-agent": {
      "command": "uvx",
      "timeout": 120000,
      "args": [
        "mcp-proxy-for-aws@latest",
        "https://connect.aidevops.{region}.api.aws/mcp",
        "--service", "aidevops",
        "--region", "{region}"
      ]
    }
  }
}
```

The proxy signs each request with your local AWS credentials, so no access token is required.

### Multi-Agent-Space routing
<a name="multi-agent-space-routing"></a>

In SigV4 mode, pass `agent_space_id` on each tool call to specify which Agent Space to use. This makes it possible to route across multiple Agent Spaces from a single client.

## A2A integration
<a name="a2a-integration"></a>

The A2A endpoint implements the [A2A v1.0 specification](https://a2a-protocol.org/latest/specification/) using HTTP\+JSON binding.

### Agent card discovery
<a name="agent-card-discovery"></a>

Retrieve the agent card at:

```
GET https://connect.aidevops.{region}.api.aws/.well-known/agent-card.json
```

### Supported operations
<a name="supported-operations"></a>
+ `SendMessage` – Send a message and receive a response.
+ `SendStreamingMessage` – Stream responses as they are generated.
+ `GetTask` – Check the status of an asynchronous task.
+ `ListTasks` – List tasks for an Agent Space.
+ `CancelTask` – Cancel a running task.
+ `SubscribeToTask` – Subscribe to task updates through server-sent events.

### Skills
<a name="skills"></a>
+ **investigate** – Deep asynchronous analysis of operational issues (5–8 minutes).
+ **chat** – Instant answers to operational questions.

## Security considerations
<a name="security-considerations"></a>

### Token scoping
<a name="token-scoping"></a>
+ Use least privilege: choose `read` for read-only integrations, `operate` only when the client needs to send messages or manage tasks.
+ Rotate tokens periodically. Tokens expire after the configured duration (maximum 60 days).
+ Store tokens in environment variables or secrets managers. Do not hardcode tokens in source code.
+ Do not auto-execute agent responses without human review.

### IP allowlist
<a name="ip-allowlist"></a>

When creating an access token, you can optionally specify an IP allowlist. When configured, the token can only be used from the specified IP addresses or CIDR ranges. Requests from other IPs are rejected with an access denied error.

### Token rotation and revocation
<a name="token-rotation-and-revocation"></a>
+ **Rotation** – Rotate a token to generate a new token value while preserving the token's name, scopes, and IP allowlist. The old token is immediately invalidated. Update your client configuration with the new token value.
+ **Revocation** – If a token is compromised, revoke it immediately. Revoked tokens cannot be used and cannot be restored.

#### Responding to a compromised token
<a name="responding-to-a-compromised-token"></a>

If you suspect a token has been compromised, follow these steps:

1. **Block all token access** – In the AWS DevOps Agent console, open your Agent Space, choose the **Configuration** tab, and choose **Disable** in the Access tokens section. This immediately blocks all token-based access to the Agent Space.

1. **Revoke compromised tokens** – In the web app, go to **Settings** > **Access Tokens**, choose the compromised token, and choose **Revoke**. You can revoke tokens even while access tokens are disabled.

1. **Re-enable access tokens** – After revoking the compromised tokens, re-enable access tokens from the **Configuration** tab if you still need token-based access.

#### Revoking tokens programmatically
<a name="revoking-tokens-programmatically"></a>

You can also revoke tokens programmatically using `awscurl`. The following commands use SigV4 authentication. Replace the Region (`us-east-1`) with the Region where your Agent Space is created.

**Note:** Step 1 uses the AWS CLI. Steps 2 and 3 use [awscurl](https://github.com/okigan/awscurl), a command-line tool that signs HTTP requests with SigV4, because access token operations do not yet have dedicated AWS CLI commands.

**Step 1: List your Agent Spaces**

```
aws aidevops list-agent-spaces --region us-east-1
```

**Step 2: List access tokens for an Agent Space**

```
awscurl --service aidevops --region us-east-1 \
  -H "Accept: application/json" \
  "https://cp.aidevops.us-east-1.api.aws/v1/agentspaces/{agentSpaceId}/access-tokens"
```

**Step 3: Revoke a token**

```
awscurl --service aidevops --region us-east-1 -X POST \
  -H "Accept: application/json" \
  "https://cp.aidevops.us-east-1.api.aws/v1/agentspaces/{agentSpaceId}/access-tokens/{accessTokenId}/revoke"
```

Replace `{agentSpaceId}` and `{accessTokenId}` with the values from the previous responses.

### Traceability
<a name="traceability"></a>

When an access token is used, AWS DevOps Agent assumes a role on your behalf to perform actions. This `AssumeRole` call is logged in AWS CloudTrail with session tags that identify the token and caller:
+ `AgentSpaceId` – Identifier of the Agent Space.
+ `UserId` – Identity of the token creator.
+ `AccessTokenId` – Unique identifier of the token.
+ `TokenName` – Name of the access token used.
+ `ClientType` – The protocol used (MCP, A2A).
+ `SourceIp` – IP address of the client.
+ `UserAgent` – Client User-Agent string (when available).

Direct MCP and A2A endpoint invocations are not logged in CloudTrail for either authentication method. Each invocation has a corresponding downstream AWS API call logged in CloudTrail, with an identifiable role session name in the format `token_{spaceId}_{timestamp}_{tokenName}`.

### VPC endpoint policy limitation
<a name="vpc-endpoint-policy-limitation"></a>

The remote server endpoints do not support VPC endpoint policies. Calls using either access tokens or SigV4 authentication cannot be restricted by VPC endpoint policies.

### Disabling access tokens
<a name="disabling-access-tokens"></a>

The access tokens feature is off by default. To disable it after enabling:

1. Open the **Configuration** tab of your Agent Space.

1. In the **Access tokens** section, choose **Disable**.

Disabling immediately blocks all token-based access. Existing tokens are not deleted but cannot be used until the feature is re-enabled.

To prevent users in your organization from enabling access tokens, create a Service Control Policy (SCP) that denies the access token API actions and the `UpdateAgentSpace` action (which controls the access tokens toggle):

**Note:** Denying `aidevops:UpdateAgentSpace` also prevents other Agent Space updates (name, description, locale). If this is too broad, omit it from the SCP — the remaining denies still prevent token creation and use, even if someone enables the feature.

```
{
  "Version": "2012-10-17",		 	 	 		 	 	 
  "Statement": [
    {
      "Sid": "DenyAccessTokenOperations",
      "Effect": "Deny",
      "Action": [
        "aidevops:UpdateAgentSpace",
        "aidevops:CreateAccessToken",
        "aidevops:GetAccessToken",
        "aidevops:ListAccessTokens",
        "aidevops:RotateAccessToken",
        "aidevops:RevokeAccessToken"
      ],
      "Resource": "*"
    }
  ]
}
```

## Troubleshooting
<a name="troubleshooting"></a>


| Symptom | Cause | Resolution | 
| --- | --- | --- | 
| HTTP 401 Unauthorized | Token is invalid or expired. | Create a new token or rotate the existing token in the web app. | 
| HTTP 400 "A2A-Version header required" | Missing protocol version header. Only A2A v1.0 is supported. | Add A2A-Version: 1.0 header to A2A requests. | 
| Request timeout | Initial responses take 5–30 seconds. Investigations take 5–8 minutes. | Set client timeout to at least 120 seconds. | 
| Connection refused | Incorrect endpoint URL or Region. | Verify the URL format: https://connect.aidevops.{region}.api.aws | 