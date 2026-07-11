

# Connecting MCP Servers
<a name="configuring-integrations-and-knowledge-connecting-mcp-servers"></a>

Model Context Protocol (MCP) servers extend AWS DevOps Agent's investigation capabilities by providing access to data from your external observability tools, custom monitoring systems, and operational data sources. This guide explains how to connect an MCP server to AWS DevOps Agent.

## Requirements
<a name="requirements"></a>

Before connecting an MCP server, ensure your server meets these requirements:
+ **Streamable HTTP transport protocol** – Only MCP servers that implement the Streamable HTTP transport protocol are supported.
+ **Authentication support** – Your MCP server must support one of the following authentication methods: OAuth 2.0 (Client Credentials or 3LO), API key/token-based authentication, or AWS Signature Version 4 (SigV4).

## Security considerations
<a name="security-considerations"></a>

When connecting MCP servers to AWS DevOps Agent, consider these security aspects:
+ **Tool allowlisting – ** You should allowlist only the specific tools your Agent Space needs, rather than exposing all tools from your MCP server. See [Configuring MCP tools in an Agent Space](#configuring-integrations-and-knowledge-connecting-mcp-servers) for how to allow list tools per Agent Space.

Please note that the maximum tool name length of any MCP tool is 64 characters. For the maximum number of MCP tools allowed per agent space, see [Quotas](quotas.md).
+ **Prompt injection risks** – Custom MCP servers can introduce additional risk of prompt injection attacks. See [Prompt injection protection: AWS DevOps Agent Security](aws-devops-agent-security.md) for more information.
+ **Read-only tools and access –** Only allowlist read-only MCP tools and ensure that authentication credentials are only permitted read-only access.

See [AWS DevOps Agent Security](aws-devops-agent-security.md) for more information on prompt injection and the shared responsibility model.

**Note**  
If your MCP server is on a private network, see [Connecting to privately hosted tools](configuring-integrations-and-knowledge-connecting-to-privately-hosted-tools.md)

## Registering an MCP server (account-level)
<a name="registering-an-mcp-server-account-level"></a>

MCP servers are registered at the AWS account level and shared among all Agent Spaces in that account. Individual Agent Spaces can then choose which specific tools they need from each MCP server.

### Step 1: MCP server details
<a name="step-1-mcp-server-details"></a>

1. Sign in to the AWS Management Console

1. Navigate to the AWS DevOps Agent console

1. Go to the **Capability Providers** page (accessible from the side navigation)

1. Find **MCP Server** in the **Available** providers section and choose **Register**

1. On the **MCP server details** page, enter the following information:
   + **Name** – Enter a descriptive name for your MCP server
   + **Endpoint URL** – Enter the full HTTPS URL of your MCP server endpoint
   + **Description** (optional) – Add a description to help identify the server's purpose
   + **Enable Dynamic Client Registration** – Select this checkbox if you want to allow AWS DevOps Agent to automatically register with your MCP server's authorization server
   + **Connect to endpoint using private connection** – Select this checkbox if you want AWS DevOps Agent to make requests to your MCP server privately. You may select an existing private connection or create a new one. If you use OAuth authentication, the private connection applies to both the MCP server endpoint and the token exchange endpoint. Ensure the private connection is configured with a host address that can route traffic to both endpoints. For more information, see [Connecting to privately hosted tools](configuring-integrations-and-knowledge-connecting-to-privately-hosted-tools.md).

1. Choose **Next**

**Note**  
** The MCP server endpoint URL will be displayed in AWS CloudTrail logs in your account.

### Step 2: Authorization flow
<a name="step-2-authorization-flow"></a>

Select the authentication method for your MCP server:

**OAuth Client Credentials** – If your MCP server uses OAuth Client Credentials flow:

1. Select **OAuth Client Credentials**

1. Choose **Next**

**OAuth 3LO (Three-Legged OAuth)** – If your MCP server uses OAuth 3LO for authentication:

1. Select **OAuth 3LO**

1. Choose **Next**

**API Key** – If your MCP server uses API key authentication:

1. Select **API Key**

1. Choose **Next**

**AWS SigV4** – If your MCP server uses AWS Signature Version 4 authentication:

1. Select **AWS SigV4**

1. Choose **Next**

### Step 3: Authorization configuration
<a name="step-3-authorization-configuration"></a>

Configure additional authorization parameters based on the selected authentication method:

**For OAuth Client Credentials:**

1. **Client ID** – Enter the client ID of the OAuth client

1. **Client Secret** – Enter the client secret of the OAuth client

1. **Exchange URL** – Enter the OAuth token exchange endpoint URL

1. **Exchange Parameters** – Enter OAuth token exchange parameters for authenticating with the service

1. **Add Scope** – Add OAuth scopes for authentication

1. Choose **Next**

**For OAuth 3LO:**

1. **Client ID** – Enter the client ID of the OAuth client

1. **Client Secret** – Enter the client secret of the OAuth client if it’s required by your OAuth client

1. **Exchange URL** – Enter the OAuth token exchange endpoint URL

1. **Authorization URL ** - Enter the OAuth authorization endpoint URL

1. **Code Challenge Support ** - Select this checkbox if your OAuth client supports code challenge

1. **Add Scope** – Add OAuth scopes for authentication

1. Choose **Next**

**For API Key:**

1. Enter an API key name

1. Enter the the name of the header that will contain the API key in the request

1. Enter your API key value

1. Choose **Next**

**For AWS SigV4:**

AWS SigV4 authentication allows AWS DevOps Agent to connect to MCP servers that use AWS Signature Version 4 for request signing. This is useful for MCP servers hosted behind Amazon API Gateway or other AWS services that support SigV4 authentication.

**Note:** Private connections are not supported for MCP servers using SigV4 authentication. Your MCP server endpoint must be publicly accessible. For MCP servers on private networks using other authentication methods, see [Connecting to privately hosted tools](configuring-integrations-and-knowledge-connecting-to-privately-hosted-tools.md).

1. **Configure IAM role** – Choose one of the following options:
   + **Use an existing role** – Select an existing IAM role from the dropdown. The role must have a trust policy that allows the AWS DevOps Agent service principal to assume it (see [Creating an IAM role for SigV4 authentication](configuring-integrations-and-knowledge-connecting-mcp-servers.html#creating-an-iam-role-for-sigv4-authentication)).
   + **Create a new role manually** – Follow the step-by-step instructions displayed in the console to create a new IAM role with the correct trust policy.

1. **AWS Region** – Enter the AWS Region for SigV4 signing (for example, `us-east-1`). To use SigV4a multi-region signing, enter `*`.

1. **Service Name** – Enter the AWS service name for SigV4 signing (for example, `execute-api` for API Gateway).

1. **Custom Headers** (optional) – Add up to 10 custom key-value header pairs to include with each signed request.

1. Choose **Next**

### Step 4: Review and submit
<a name="step-4-review-and-submit"></a>

1. Review all the MCP server configuration details

1. Choose **Submit** to complete the registration

1. AWS DevOps Agent will validate the connection to your MCP server

1. Upon successful validation, your MCP server will be registered at the account level

## Configuring MCP tools in an Agent Space
<a name="configuring-mcp-tools-in-an-agent-space"></a>

After registering an MCP server at the account level, you can configure which tools from that server are available to specific Agent Spaces:

1. In the AWS DevOps Agent console, select your Agent Space

1. Go to the **Capabilities** tab

1. In the **MCP Servers** section, choose **Add**

1. Select the registered MCP server you want to connect to this Agent Space

1. Configure which tools from this MCP server should be available to the Agent Space:
   + **Allow all tools** – Makes all tools from the MCP server available
   + **Select specific tools** – Allows you to choose which tools to allowlist

1. Choose **Add** to connect the MCP server to your Agent Space

AWS DevOps Agent will now be able to use the allowlisted tools from your MCP server during investigations in this Agent Space.

## Managing MCP server connections
<a name="managing-mcp-server-connections"></a>

**Updating authentication credentials** – If your authentication credentials need to be updated, you will need to re-register your MCP server. Navigate to the **Capability Providers** page in the AWS DevOps Agent console, locate your MCP server, remove any active associations, and choose **Deregister**. Next, **register** your MCP server with the new authentication credentials and re-create any necessary associations with your Agent Space.

**Viewing connected MCP servers** – To see all MCP servers connected to your Agent Space, select your Agent Space, go to the **Capabilities** tab, and check the **MCP Servers** section. You can also update selected tools here.

**Removing MCP server connections** – To disconnect an MCP server from an Agent Space, select the server in the **MCP Servers** section and choose **Remove**. To completely delete an MCP server registration, remove it from all Agent Spaces first, then delete the account-level registration.

## Creating an IAM role for SigV4 authentication
<a name="creating-an-iam-role-for-sigv4-authentication"></a>

When using AWS SigV4 authentication, AWS DevOps Agent assumes an IAM role in your account to sign requests to your MCP server. This role must have a trust policy that allows the AWS DevOps Agent service principal (`aidevops.amazonaws.com`) to assume it, with confused deputy protection.

### Trust policy
<a name="trust-policy"></a>

Create an IAM role with the following trust policy. Replace `REGION` with your AWS Region (for example, `us-east-1`) and `ACCOUNT_ID` with your AWS account ID.

```
{
  "Version": "2012-10-17",		 	 	 		 	 	 
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "aidevops.amazonaws.com"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "aws:SourceAccount": "ACCOUNT_ID"
        },
        "ArnLike": {
          "aws:SourceArn": "arn:aws:aidevops:REGION:ACCOUNT_ID:service/*"
        }
      }
    }
  ]
}
```

The trust policy includes the following conditions to prevent the [confused deputy problem](https://docs.aws.amazon.com/IAM/latest/UserGuide/confused-deputy.html) :
+ `aws:SourceAccount` – Restricts role assumption to requests originating from your AWS account.
+ `aws:SourceArn` – Restricts role assumption to requests originating from AWS DevOps Agent service resources in your account.

### Permissions policy
<a name="permissions-policy"></a>

Attach a permissions policy to the role that grants the minimum permissions required to invoke your MCP server. For example, if your MCP server is hosted behind Amazon API Gateway, the role should have `execute-api:Invoke` permission on the API Gateway resource.

### Multi-region signing (SigV4a)
<a name="multi-region-signing-sigv4a"></a>

If your MCP server is deployed across multiple AWS Regions, you can use [SigV4a (Signature Version 4a)](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_sigv.html) for multi-region signing. To enable this, enter `*` as the AWS Region when configuring the SigV4 authorization. SigV4a uses asymmetric signing, which allows a single signed request to be valid across multiple Regions.

## Related topics
<a name="related-topics"></a>
+ Security in AWS DevOps Agent
+ Setting up an Agent Space
+ Prompt Injection Protection