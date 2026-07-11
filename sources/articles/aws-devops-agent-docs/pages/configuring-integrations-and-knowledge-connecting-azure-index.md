

# Connecting Azure
<a name="configuring-integrations-and-knowledge-connecting-azure-index"></a>

Azure integration enables AWS DevOps Agent to investigate resources in your Azure environment and correlate Azure DevOps pipeline deployments with operational incidents. By connecting Azure, the agent gains visibility into your Azure infrastructure and can perform root cause analysis across both AWS and Azure resources.

Azure integration consists of two independent capabilities:
+ **Azure Resources** – Enables the agent to discover and investigate Azure cloud resources such as virtual machines, Azure Kubernetes Service (AKS) clusters, databases, and networking components. The agent uses Azure Resource Graph to query your resources during incident investigations.
+ **Azure DevOps** – Enables the agent to access Azure DevOps repositories and pipeline execution history. The agent can correlate code changes and deployments with incidents to help identify potential root causes.

Each capability is registered at the AWS account level and can then be associated with individual Agent Spaces.

## Registration methods
<a name="registration-methods"></a>

AWS DevOps Agent supports two methods for connecting to Azure:
+ **Admin Consent** – A streamlined consent-based flow where you authorize the AWS DevOps Agent Entra application in your Azure tenant. In the console, this appears as the **Admin Consent** option. This method requires signing in with an account that has permission to perform admin consent in Microsoft Entra ID.
+ **App Registration** – A self-managed approach where you create your own Entra application with federated identity credentials using Outbound Identity Federation. In the console, this appears as the **App Registration** option. This method is suitable when you need more control over the application configuration or when admin consent permissions are not available.

Both methods provide the same capabilities. You can use one or both methods within the same AWS account.

## Known limitations
<a name="known-limitations"></a>
+ **Admin Consent: one AWS account per Azure tenant** – Each Azure tenant can only have its AWS DevOps Agent Entra App associated with one AWS account at a time. To associate the same tenant with a different AWS account, you must deregister the existing registration first.
+ **App Registration: unique application per registration** – Each App Registration must use a different application (client ID). You cannot register multiple configurations with the same client ID.
+ **Azure DevOps: source code access** – The Azure DevOps integration provides access to pipeline execution history regardless of where the source code is hosted. However, to access the actual source code, the repository must be connected separately through a supported source provider (for example, [Connecting GitHub](connecting-to-cicd-pipelines-connecting-github.md)). Source code hosted in Bitbucket is not directly accessible through the Azure DevOps integration.

## Topics
<a name="topics"></a>
+ [Connecting Azure Resources](connecting-azure-connecting-azure-resources.md)
+ [Connecting Azure DevOps](connecting-azure-connecting-azure-devops.md)