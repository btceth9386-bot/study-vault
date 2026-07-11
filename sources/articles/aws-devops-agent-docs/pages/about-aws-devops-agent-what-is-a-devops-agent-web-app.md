

# What is a DevOps Agent Web App?
<a name="about-aws-devops-agent-what-is-a-devops-agent-web-app"></a>

AWS DevOps Agent uses a dual-console architecture that separates administrative functions from day-to-day operational activities. This design enables administrators to configure the service while operations teams focus on incident response and prevention.

## Consoles
<a name="consoles"></a>

AWS DevOps Agent provides two distinct interfaces:
+ **AWS Management Console** – Administrators use the AWS Management Console to set up and manage AWS DevOps Agent. In this console, you can [Creating an Agent Space](getting-started-with-aws-devops-agent-creating-an-agent-space.md) connect AWS services and third-party tools, and manage access permissions for your organization.
+ **DevOps Agent web app - ** Operations teams use DevOps Agent Space web apps for daily incident response activities. This standalone application provides an interface where on-call engineers can launch investigations, interact with the agent through natural language chat, view application topologies, and review incident prevention recommendations.

## Web app capabilities
<a name="web-app-capabilities"></a>

The DevOps Agent web app provides the following primary capabilities:
+ **Natural language Chat interface** – Available throughout the web app, Chat is an AI-powered conversational assistant that enables you to query your infrastructure, analyze system health, and work with investigations using natural language. Chat provides context-aware responses based on the page you're viewing.
+ **Incidents** – The Incidents page is where you create and track incident investigations and generate mitigation plans to resolve incidents. After an investigation completes, you can provide accuracy feedback on the root cause analysis.
+ **Improvements** – The Improvements page provides recommendations to improve your observability posture, delivery processes, and infrastructure architecture to prevent future incidents.
+ **Topology** – The Topology page provides an interactive visual representation of the account resources and their relationships across all of the resources in the connected accounts. You can view the topology with different levels of detail using the "Show" dropdown to switch between System, Container, and Resource views.
+ **Agents** – Create and manage custom agents that you can schedule, for example to generate weekly operations reports.
+ **Knowledge** – Three tabs, Instructions, Skills, and Memories, hold different kinds of knowledge that extend AWS DevOps Agent. Instructions are similar to local AGENTS.md general instructions, applied every time to all agents or to specific agents. Skills are modular instruction sets that extend AWS DevOps Agent with specialized capabilities. Skills contain domain knowledge, investigation methodologies, and tool configurations tailored to your infrastructure, and each skill enables specific tools and provides progressive disclosure of instructions only when relevant to the investigation. Memories are learned knowledge. The agent learns them through directives in chat or through a managed skill that performs learning from past experience and creates memories.
+ **Settings** – General settings, including the agent space ARN, usage information, light/dark theme configuration, access tokens, and a link to the What's new documentation for recent changes.

## Authentication
<a name="authentication"></a>

AWS DevOps Agent supports flexible authentication methods to accommodate different organizational requirements:
+ **IAM Identity Center integration (User access)** – Organizations can use AWS Identity Center (IAM Identity Center) to centrally manage user access to the DevOps Agent Space web apps. IAM Identity Center can federate with external identity providers through standard OIDC and SAML protocols, including providers like Okta, Ping Identity, and Microsoft Entra ID. This method supports multi-factor authentication from your identity provider.
+ **External identity provider (IdP) authentication** – Organizations can connect an OIDC-compatible identity provider, such as Okta or Microsoft Entra ID, directly to the Agent Space web app without requiring IAM Identity Center. Users sign in with their corporate credentials through the IdP. For setup instructions, see [Setting Up External Identity Provider (IdP) Authentication](aws-devops-agent-security-setting-up-external-identity-provider-idp-authentication.md).
+ **IAM authentication link (Admin access)** – An alternative method provides direct access to the web app from the AWS Management Console using your existing console session. This option is useful before implementing full Identity Center integration, but sessions are limited to 10 minutes.