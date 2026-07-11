

# What are DevOps Agent Spaces?
<a name="about-aws-devops-agent-what-are-devops-agent-spaces"></a>

A DevOps Agent Space is a logical container that defines the tools and infrastructure that AWS DevOps Agent has access to. Each Agent Space operates independently with its own AWS account access, third-party integrations, and user permissions.

An Agent Space represents the boundary of what AWS DevOps Agent can access and investigate during incident response. When you create an Agent Space, you define which AWS accounts the agent can access, which external tools it can connect to, and which users in your organization can interact with the agent.

Each Agent Space functions as an independent deployment of AWS DevOps Agent. You configure the Agent Space through the AWS Management Console, while your operations teams use the Agent Space’s web app to conduct investigations and review recommendations within that space.

## How Agent Spaces are isolated
<a name="how-agent-spaces-are-isolated"></a>

Agent Spaces maintain isolation to ensure security and prevent unintended access across different environments or teams:
+ **AWS account isolation** – Each Agent Space uses dedicated IAM roles that grant access only to specific AWS accounts and resources. The agent cannot access AWS resources outside of those explicitly configured for the Agent Space.
+ **User access isolation** – You control which users or groups can access each Agent Space. This allows you to align access permissions with your organizational structure, ensuring teams only interact with their designated Agent Spaces.
+ **Data isolation** – Investigation data, incident history, and recommendations are maintained separately within each Agent Space. Information from one Agent Space is not visible or accessible from another Agent Space.
+ **Chat data isolation ** - Chat conversation history is also isolated within each Agent Space. Conversations and queries in one Agent Space are not visible or accessible from another Agent Space.

## Agent Space Web App
<a name="agent-space-web-app"></a>

Each Agent Space has a dedicated web app that is accessible outside of the AWS Management Console. See [What is a DevOps Agent Web App?](about-aws-devops-agent-what-is-a-devops-agent-web-app.md) to learn more about the web app.

## When to use multiple Agent Spaces
<a name="when-to-use-multiple-agent-spaces"></a>

Consider creating multiple Agent Spaces to support different organizational needs:
+ **Team separation** – Create dedicated Agent Spaces for different application teams or business units to maintain clear ownership boundaries in the Agent Space.
+ **Environment isolation** – Separate production and non-production environments into different Agent Spaces to prevent accidental cross-environment access.
+ **Service boundaries** – Align Agent Spaces with specific services or application boundaries to keep investigations focused and relevant.
+ **Compliance requirements** – Configure separate Agent Spaces with different access controls or data residency settings to meet regulatory requirements.

**Note**  
** When creating multiple Agent Spaces, you can use a dedicated AWS account as the primary account for an Agent Space and connect distinct application accounts as secondary accounts. This approach allows you to maintain granular access controls while ensuring that each Agent Space can access only the resources specific to its intended scope, even when using automatic role creation.