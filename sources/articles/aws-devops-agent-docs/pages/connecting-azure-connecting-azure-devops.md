

# Connecting Azure DevOps
<a name="connecting-azure-connecting-azure-devops"></a>

Azure DevOps integration enables AWS DevOps Agent to access repositories and pipeline execution history in your Azure DevOps organization. The agent can correlate code changes and deployments with operational incidents to help identify potential root causes.

**Note:** Azure DevOps pipelines can use source code from Azure Repos, GitHub, or Bitbucket. The Azure DevOps integration provides access to pipeline execution history regardless of the source provider. However, to access the actual source code during investigations, the repository must be connected separately through a supported integration such as [Connecting GitHub](connecting-to-cicd-pipelines-connecting-github.md). Source code in Bitbucket is not directly accessible through this integration.

This integration follows a two-step process: register Azure DevOps at the AWS account level, then associate specific projects with individual Agent Spaces.

## Prerequisites
<a name="prerequisites"></a>

Before connecting Azure DevOps, ensure you have:
+ Access to the AWS DevOps Agent console
+ An Azure DevOps organization with at least one project containing a repository and pipeline history
+ Permissions to add users to your Azure DevOps organization
+ For Admin Consent method: an account with permission to perform admin consent in Microsoft Entra ID
+ For App Registration method: an Entra application with permissions to configure federated identity credentials, and [Outbound Identity Federation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_enable-federation.html) enabled in your AWS account

**Note:** You can also start registration from within an Agent Space. Navigate to the **Pipelines** section, choose **Add**, and select **Azure DevOps**. If Azure DevOps is not yet registered, the console guides you through registration first.

## Registering Azure DevOps via Admin Consent
<a name="registering-azure-devops-via-admin-consent"></a>

The Admin Consent method uses a consent-based flow with the AWS DevOps Agent managed application.

### Step 1: Start the registration
<a name="step-1-start-the-registration"></a>

1. Sign in to the AWS Management Console and navigate to the AWS DevOps Agent console

1. Go to the **Capability Providers** page

1. Locate the **Azure DevOps** section and choose **Register**

1. Enter your **Azure DevOps organization name** when prompted

### Step 2: Complete Admin Consent
<a name="step-2-complete-admin-consent"></a>

1. Choose to proceed - you are redirected to the Microsoft Entra admin consent page

1. Sign in with a user principal account that has permission to perform admin consent

1. Review and grant consent for the AWS DevOps Agent application

### Step 3: Complete user authorization
<a name="step-3-complete-user-authorization"></a>

1. After admin consent, you are prompted for user authorization to verify your identity as a member of the authorized tenant

1. Sign in with an account belonging to the same Azure tenant

1. After authorization, you are redirected back to the AWS DevOps Agent console with a success status

### Step 4: Grant access in Azure DevOps
<a name="step-4-grant-access-in-azure-devops"></a>

See [Granting access in Azure DevOps](#granting-access-in-azure-devops) below. Search for **AWS DevOps Agent** when adding users.

## Registering Azure DevOps via App Registration
<a name="registering-azure-devops-via-app-registration"></a>

App Registration is shared between Azure Resources and Azure DevOps. If you have already completed App Registration for Azure Resources, you can skip to [Granting access in Azure DevOps](#granting-access-in-azure-devops).

### Step 1: Start the ADO App Registration
<a name="step-1-start-the-ado-app-registration"></a>

1. In the AWS DevOps Agent console, go to the **Capability Providers** page

1. Locate the **Azure Cloud** section and choose **Register**

1. Select the **App Registration** method

### Step 2: Create and configure your Entra application
<a name="step-2-create-and-configure-your-entra-application"></a>

Follow the instructions displayed in the console to:

1. Enable Outbound Identity Federation in your AWS account (in the IAM console, go to **Account settings** → **Outbound Identity Federation**)

1. Create an Entra application in your Microsoft Entra ID, or use an existing one

1. Configure federated identity credentials on the application

### Step 3: Provide registration details
<a name="step-3-provide-registration-details"></a>

Fill in the registration form with:
+ **Tenant ID** – Your Azure tenant identifier
+ **Tenant Name** – A display name for the tenant
+ **Client ID** – The application (client) ID of the Entra application
+ **Audience** – The audience identifier for the federated credential

### Step 4: Create the IAM role
<a name="step-4-create-the-iam-role"></a>

An IAM role will be automatically created when you submit the registration through the console. It permits AWS DevOps Agent to assume credentials and invoke `sts:GetWebIdentityToken`.

### Step 5: Complete the registration
<a name="step-5-complete-the-registration"></a>

1. Confirm the configuration in the AWS DevOps Agent console

1. Choose **Submit** to complete the registration

### Step 6: Grant access in Azure DevOps
<a name="step-6-grant-access-in-azure-devops"></a>

See [Granting access in Azure DevOps](#granting-access-in-azure-devops) below. Search for the Entra application you created during App Registration when adding users.

## Granting access in Azure DevOps
<a name="granting-access-in-azure-devops"></a>

After registration, grant the application access to your Azure DevOps organization. This step is the same for both the Admin Consent and App Registration methods.

1. In Azure DevOps, go to **Organization Settings** > **Users** > **Add Users**

1. Search for the application (either **AWS DevOps Agent** for Admin Consent, or your own Entra application for App Registration)

1. Set the access level to **Basic**

1. Under **Add to projects**, select the projects you want the agent to access

1. Under **Azure DevOps Groups**, select **Project Readers**

1. Choose **Add** to complete

**Security Requirement:** Assign only the **Project Readers** group. Read-only access serves as a security boundary that restricts the agent to read-only operations and limits the impact of indirect prompt injection attacks. Assigning groups with write or action permissions significantly increases the blast radius of prompt injection and may result in compromise of Azure DevOps resources.

## Associating a project with an Agent Space
<a name="associating-a-project-with-an-agent-space"></a>

After registering Azure DevOps at the account level, associate specific projects with your Agent Spaces:

1. In the AWS DevOps Agent console, select your Agent Space

1. Go to the **Capabilities** tab

1. In the **Pipelines** section, choose **Add**

1. Select **Azure DevOps** from the list of available providers

1. Select the project from the dropdown of available projects

1. Choose **Add** to complete the association

## Managing Azure DevOps connections
<a name="managing-azure-devops-connections"></a>
+ **Viewing connected projects** – In the **Capabilities** tab, the **Pipelines** section lists all connected Azure DevOps projects.
+ **Removing a project** – To disconnect a project from an Agent Space, select it in the **Pipelines** section and choose **Remove**.
+ **Removing the registration** – To remove the Azure DevOps registration entirely, go to the **Capability Providers** page and delete the registration. All Agent Space associations must be removed first.