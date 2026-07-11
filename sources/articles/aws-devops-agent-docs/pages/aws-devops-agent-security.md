

# AWS DevOps Agent Security
<a name="aws-devops-agent-security"></a>

This document provides information about security considerations, data protection, access controls, and compliance capabilities for AWS DevOps Agent. Use this information to understand how AWS DevOps Agent is designed to meet your security and compliance requirements.

## Multi-layered security
<a name="multi-layered-security"></a>

AWS DevOps Agent implements security at multiple layers. Even if broader permissions are granted to the agent's IAM role, the agent enforces its own internal access controls to limit the scope of its actions.

We recommend following the principle of least privilege when configuring IAM permissions for AWS DevOps Agent, and implementing security at multiple layers. Defense in depth ensures that no single misconfiguration can compromise the security of your environment.

## Agent Spaces
<a name="agent-spaces"></a>

Agent Spaces serve as the primary security boundary in AWS DevOps Agent. Each Agent Space:
+ Operates independently with its own configurations and permissions
+ Defines which AWS accounts and resources the agent can access
+ Establishes connections to third-party platforms

Agent Spaces maintain strict isolation to ensure security and prevent unintended access across different environments or teams.

## Regional processing and data flow
<a name="regional-processing-and-data-flow"></a>

AWS DevOps Agent operates globally with regional processing capabilities. The agent retrieves operational data from AWS regions across all AWS accounts granted access within the configured Agent Space. This multi-region cross-account data collection ensures comprehensive incident analysis while respecting geographical boundaries for inference processing.

### Amazon Bedrock usage and cross-region inference
<a name="amazon-bedrock-usage-and-cross-region-inference"></a>

AWS DevOps Agent will automatically select the optimal region within your geography to process your inference requests. This maximizes available compute resources, model availability, and delivers the best customer experience. Your data will remain stored only in the region where your Agent Space is created, however, input prompts and output results may be processed outside that region as described in the following list. All data will be transmitted encrypted across Amazon's secure network.

AWS DevOps Agent will securely route your inference requests to available compute resources within the geographic area where the request originated, as follows:
+ Inference requests originating in the European Union will be processed within the European Union.
+ Inference requests originating in the United States will be processed within the United States.
+ Inference requests originating in Australia will be processed within Australia.
+ Inference requests originating within Japan will be processed within Japan.
+ If an inference request originates in an area not listed, it will be processed by default within the United States.
+ DevOps Agent and Bedrock are not impacted by customer policies in Service Control Policies (SCPs) or Control Tower that restrict customer content to specific regions
+ Bedrock may use regions other than the originating region within your geography to perform stateless inference to optimize performance and availability

### Global cross-Region inference for specific Regions
<a name="global-cross-region-inference-for-specific-regions"></a>

For the following Regions, the geography-based routing described above does not apply. Instead, AWS DevOps Agent will automatically select the optimal region globally to process your inference requests.
+ Asia Pacific (Singapore) – `ap-southeast-1`
+ Asia Pacific (Mumbai) – `ap-south-1`
+ South America (São Paulo) – `sa-east-1`

## Identity and access management
<a name="identity-and-access-management"></a>

### Authentication methods
<a name="authentication-methods"></a>

AWS DevOps Agent provides two authentication methods to log into the AWS DevOps Agent Space web app:
+ **AWS Identity Center integration** – The primary authentication method uses OAuth 2.0 with session-based authentication using HTTP-only cookies. AWS Identity Center can federate with external identity providers through standard OIDC and SAML protocols, including providers like Okta, Ping Identity, and Microsoft Entra ID. This method supports multi-factor authentication through your identity provider. AWS Identity Center defaults to session durations of up to 12 hours and can be configured to a desired duration.
+ **IAM authentication link** – An alternative method provides direct access to the web app from the AWS Management Console using JWT-based tokens derived from an existing AWS Management Console session. This option is useful for evaluating AWS DevOps Agent before implementing full Identity Center integration as well as gaining administrative access if the AWS DevOps Agent web app becomes inaccessible through Identity Center based authentication. Sessions are limited to 10 minutes.

### IAM roles
<a name="iam-roles"></a>

AWS DevOps Agent uses IAM roles to define access permissions:
+ **Primary account role** – Grants the agent access to resources in the AWS account where you create the Agent Space as well as access to secondary account roles.
+ **Secondary account roles** – Grants the agent access to resources in additional AWS accounts connected to the Agent Space.
+ **Web app role** – Grants users access to AWS DevOps Agent investigation data and findings in the web app.

These roles should be configured following the principle of least privilege, granting only the necessary read-only permissions required for investigations.

## Data protection
<a name="data-protection"></a>

### Data encryption
<a name="data-encryption"></a>

AWS DevOps Agent encrypts all customer data:
+ **Encryption at rest** – All data is encrypted with AWS-managed keys.
+ **Encryption in transit** – All retrieved logs, metrics, knowledge items, ticket metadata, and other data are encrypted in transit inside the agent's private network and to outside networks.

### Data storage and retention
<a name="data-storage-and-retention"></a>

Data is stored in the region where your Agent Space is created, while inference processing may occur within your geography as described in the Amazon Bedrock usage section above.

### Personal identifiable information (PII)
<a name="personal-identifiable-information-pii"></a>

AWS DevOps Agent does not filter PII information when summarizing data gathered during investigations, recommendation evaluations, or chat responses. It is recommended that PII data be redacted before storing in observability logs.

## Agent journal and audit logging
<a name="agent-journal-and-audit-logging"></a>

### Agent journal
<a name="agent-journal"></a>

Both the Incident Investigation and Prevention capabilities maintain detailed journals that:
+ Log every reasoning step and action taken
+ Create complete transparency into agent decision-making processes
+ Cannot be modified by the agents once recorded, minimizing attacks such as prompt injection from hiding important actions
+ Include all chat messages from the Investigation page

### AWS CloudTrail integration
<a name="aws-cloudtrail-integration"></a>

All AWS DevOps Agent API calls are automatically captured by AWS CloudTrail within the hosting AWS account. Using the information collected by CloudTrail, you can determine:
+ The request that was made to the agent
+ The IP address from which the request was made
+ Who made the request
+ When it was made

## Prompt injection protection
<a name="prompt-injection-protection"></a>

A prompt injection attack occurs when an attacker embeds malicious instructions into external data, such as a webpage or document, that a generative AI system will later process. AWS DevOps Agent natively consumes many data sources as part of its normal operations, including logs, resource tags, and other operational data. AWS DevOps Agent protects against prompt injection attacks through the safeguards below, but it is important to ensure all connected data sources and user access to those data sources are trusted. See [Shared responsibility model](#aws-devops-agent-security) section for more.

Prompt injection safeguards:
+ **Limited write capabilities** – The tools available to the agent are not able to mutate resources, with the exception of opening tickets and support cases. This prevents malicious instructions from modifying your infrastructure or applications.
+ **Account boundary enforcement** – AWS DevOps Agent only operates within the boundary permitted by the roles assigned to the agent in the primary and connected secondary AWS accounts. The agent cannot access or modify resources outside of its configured scope.
+ **AI safety protections** – AWS DevOps Agent uses models with AI Safety Level 3 (ASL-3) protections, which include built-in classifiers that detect and resist prompt injection attempts. The agent also leverages the [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-prompt-attack.html) prompt attack filter to detect and block prompt injection and jailbreak attempts before they can affect agent behavior.
+ **Immutable audit trail** – The agent journal logs every reasoning step and action taken. Journal entries cannot be modified by the agent once recorded, preventing prompt injection attacks from hiding malicious actions.

While AWS DevOps Agent provides multiple layers of protection against prompt injection attacks, certain configurations can increase risk:
+ **Custom MCP server tools** – The bring-your-own MCP feature allows you to introduce custom tools to the agent, which can present additional opportunities for prompt injection. Custom tools may not have the same security controls as native AWS DevOps Agent tools, and malicious instructions could potentially use these tools in unintended ways. See [Shared responsibility model](#aws-devops-agent-security) section for more.
+ **Authorized user attacks** – Users who are authorized to operate within the AWS account boundary or connected tools have a higher chance of attempting an attack against the agent. These users may have the ability to modify data sources that the agent consumes, such as logs or resource tags, making it easier to embed malicious instructions that the agent will process.

To mitigate these risks:

1. Carefully review and test custom MCP servers before deploying them in Agent Spaces.

   1. Ensure they are only permitted to perform read-only actions

   1. Verify that users of external tools accessed by MCP servers are trusted entities, as AWS DevOps Agents interfacing with MCP rely on the implicit trust relationship established between these tool users and the AWS DevOps Agent

1. Apply the principle of least privilege when granting users access to systems that provide data to the agent

1. Regularly audit which MCP servers are connected to your Agent Spaces

1. Since any content retrieved from allowlisted URLs could attempt to manipulate the agent's behavior, only include trusted sources in your allowlist.

## Integration security
<a name="integration-security"></a>

AWS DevOps Agent supports several integration types, each with its own security model:
+ **Native bidirectional integrations** – Built-in integrations that can send data to the agent and receive updates from the agent. This uses the vendor’s authentication methods
+ **MCP servers** – Remote Model Context Protocol servers that use OAuth 2.0 authentication flows and API keys to securely communicate with external systems.
+ **Webhook triggers** – Investigation triggers from remote services such as tickets or observability systems. Webhooks use either Hash-based Message Authentication Code (HMAC) signatures or an API key (bearer token) for security.
+ **Outbound communication** – Integrations like Slack and ticketing systems receive updates from the agent but do not yet support bidirectional communication.

### Registration providers
<a name="registration-providers"></a>

Some external tools are authenticated at the account level and shared among all Agent Spaces in the account. When you register these tools, you authenticate once at the account level, and then each Agent Space can connect to specific resources within that registered connection.

The following tools use account-level registration:
+ **GitHub** – Uses OAuth flow for authentication. After registering GitHub at the account level, each Agent Space can connect to specific repositories within your GitHub organization.
+ **Dynatrace** – Uses OAuth token authentication. After registering Dynatrace at the account level, each Agent Space can connect to specific Dynatrace environments or monitoring configurations.
+ **Slack** – Uses OAuth token authentication. After registering Slack at the account level, each Agent Space can connect to specific Slack channels channels.
+ **Datadog** – Uses MCP with OAuth flow for authentication. After registering Datadog at the account level, each Agent Space can connect to specific Datadog monitoring resources.
+ **New Relic** – Uses API key authentication. After registering New Relic at the account level, each Agent Space can connect to specific New Relic monitoring configurations.
+ **Splunk** – Uses bearer token authentication. After registering Splunk at the account level, each Agent Space can connect to specific Splunk data sources.
+ **GitLab** – Uses access token authentication. After registering GitLab at the account level, each Agent Space can connect to specific GitLab repositories.
+ **ServiceNow** – Uses OAuth client key/token authentication. After registering ServiceNow at the account level, each Agent Space can connect to specific ServiceNow instances or ticket queues.
+ **General public accessible remote MCP servers** – Use OAuth flow for authentication. After registering a remote MCP server at the account level, each Agent Space can connect to specific resources exposed by that server.

## Network connectivity
<a name="network-connectivity"></a>

AWS DevOps Agent connects to your third-party systems and remote MCP servers to perform investigations and other operations.

### Inbound traffic from AWS DevOps Agent to your systems
<a name="inbound-traffic-from-aws-devops-agent-to-your-systems"></a>

AWS DevOps Agent initiates outbound connections to your third-party systems and remote MCP servers, which arrive as inbound traffic to your infrastructure. How you secure this traffic depends on how your tools are hosted:
+ **Privately hosted tools** – If your tools are reachable from within an AWS VPC, you can use AWS DevOps Agent *private connections* to keep traffic isolated to AWS networks, and off of the public internet. For more information, see [Connecting to privately hosted tools](configuring-integrations-and-knowledge-connecting-to-privately-hosted-tools.md).
+ **Publicly hosted tools** – If your tools are reachable over the public internet and use IP allowlisting or firewall rules, you must allow inbound traffic from the following AWS DevOps Agent source IP addresses:
  + Asia Pacific (Sydney) (ap-southeast-2)
    + `13.237.95.197`
    + `13.238.84.102`
    + `52.64.174.242`
    + `13.211.249.13`
    + `15.134.235.54`
    + `3.107.145.226`
  + Asia Pacific (Tokyo) (ap-northeast-1)
    + `13.192.12.233`
    + `35.74.181.230`
    + `57.183.50.158`
    + `13.114.228.89`
    + `54.150.140.28`
    + `46.51.224.121`
  + Europe (Frankfurt) (eu-central-1)
    + `18.158.110.140`
    + `52.57.96.160`
    + `52.59.55.56`
    + `63.183.67.111`
    + `63.184.95.132`
    + `63.184.36.38`
  + Europe (Ireland) (eu-west-1)
    + `34.251.85.24`
    + `52.30.157.157`
    + `52.51.192.222`
    + `99.81.41.52`
    + `54.246.170.103`
    + `52.212.224.65`
  + US East (N. Virginia) (us-east-1)
    + `34.228.181.128`
    + `44.219.176.187`
    + `54.226.244.221`
    + `100.56.22.59`
    + `3.234.39.4`
    + `44.215.92.10`
  + US West (Oregon) (us-west-2)
    + `34.212.16.133`
    + `52.89.67.212`
    + `54.187.135.61`
    + `34.209.115.89`
    + `44.224.219.86`
    + `54.201.89.243`

### Outbound traffic from your VPC to AWS DevOps Agent
<a name="outbound-traffic-from-your-vpc-to-aws-devops-agent"></a>

For outbound traffic from your AWS VPC to AWS DevOps Agent (for example, using [Invoking DevOps Agent through Webhook](configuring-integrations-and-knowledge-invoking-devops-agent-through-webhook.md)), you can use VPC Endpoints to keep this network traffic isolated to AWS networks. For more information, see [VPC Endpoints (AWS PrivateLink)](aws-devops-agent-security-vpc-endpoints-aws-privatelink.md).

## Shared responsibility model
<a name="shared-responsibility-model"></a>

### AWS responsibilities
<a name="aws-responsibilities"></a>

AWS is responsible for:
+ Maintaining the security of data retrieved by the agent
+ Securing native tools available for use by the agent
+ Protecting the infrastructure that runs AWS DevOps Agent

### Customer responsibilities
<a name="customer-responsibilities"></a>

Customers are responsible for:
+ Managing user access to the agent space
+ Limiting access to trusted users of external systems that provide inputs to the agent, such as services and resources that produce logs, CloudTrail events, tickets, and more – that may be used to attempt malicious prompt injection.
+ Ensure all connected data sources have trusted data that is unlikely to be used to attempt prompt injection attacks
+ Ensuring bring-your-own MCP server integrations operate securely
+ Ensuring IAM roles assigned to the agent are properly scoped
+ Redacting PII data before storing in observability logs and other agent data sources
+ Following the recommended practice of granting only read-only permissions to connected data sources, including bring-your-own MCP servers

## Data usage
<a name="data-usage"></a>

AWS does not use agent data, chat messages, or data from integrated data sources to train models or improve the product. The AWS DevOps Agent Space uses customer in-product feedback to improve the agent’s responses and investigations, but AWS does not use it to improve the service itself.