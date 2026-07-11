

# Connecting GitHub
<a name="connecting-to-cicd-pipelines-connecting-github"></a>

GitHub integration enables AWS DevOps Agent to access code repositories and receive deployment events during incident investigations. This integration follows a two-step process: account-level registration of GitHub, followed by connecting specific repositories to individual Agent Spaces.

AWS DevOps Agent supports both GitHub.com (SaaS) and GitHub Enterprise Server (self-hosted) instances.

## Prerequisites
<a name="prerequisites"></a>

Before connecting GitHub, ensure you have:
+ Access to the AWS DevOps Agent admin console
+ A GitHub user account or organization with admin permissions
+ Authorization to install GitHub apps in your account or organization

For GitHub Enterprise Server, you also need:
+ A GitHub Enterprise Server instance (version 3.x or later) accessible over HTTPS
+ The HTTPS URL of your GitHub Enterprise Server instance (for example, `https://github.example.com`)
+ (Optional) A private connection, if your GitHub Enterprise Server instance is not publicly accessible

## Registering GitHub (account-level)
<a name="registering-github-account-level"></a>

GitHub is registered at the AWS account level and shared among all Agent Spaces in that account. Each registration corresponds to one GitHub user, one organization, or one GitHub Enterprise Server instance.

### Step 1: Navigate to pipeline providers
<a name="step-1-navigate-to-pipeline-providers"></a>

1. Sign in to the AWS Management Console

1. Navigate to the AWS DevOps Agent console

1. Go to the **Capabilities** tab

1. In the **Pipeline** section, choose **Add**

1. Select **GitHub** from the list of available providers

If GitHub hasn't been registered yet, you'll be prompted to register it first.

### Step 2: Choose connection type
<a name="step-2-choose-connection-type"></a>

On the "Register GitHub Account / Organization" screen, select whether you're connecting as a user or organization:
+ **User** – Your personal GitHub account with a username and profile
+ **Organization** – A shared GitHub account where multiple people can collaborate across many projects at once. If you select **Organization**, enter the GitHub organization name. The name must match your GitHub organization name exactly, because you must authorize and install the app on that organization in the following steps.

Select the **GitHub App permissions** for your GitHub App. The permission level determines the actions the GitHub App can perform in your repository:
+ **Read & Write** (default): The GitHub App requests both read and write permissions. This enables all features. DevOps Agent can post inline pull request comments, propose fixes, and trigger workflows.
+ **Read Only**: The GitHub App requests only read permissions. DevOps Agent can view code and pull requests but cannot post comments, propose fixes, or trigger workflows.

If you are connecting to a GitHub Enterprise Server instance, check the **Use GitHub Enterprise Server** checkbox and enter the HTTPS URL of your instance (for example, `https://github.example.com`).

If your GitHub Enterprise Server instance is not publicly accessible, you can optionally configure a private connection to allow AWS DevOps Agent to securely reach your instance. For more information, see [Connecting to privately hosted tools](configuring-integrations-and-knowledge-connecting-to-privately-hosted-tools.md).

**Note**  
** Do not include `/api/v3` or any trailing path in the URL — enter only the base URL.

### Step 3: Set up the GitHub App
<a name="step-3-set-up-the-github-app"></a>

Choose **Submit** to begin the app setup process. The next steps differ depending on whether you are connecting to GitHub.com or GitHub Enterprise Server.

#### For GitHub.com
<a name="for-githubcom"></a>

1. GitHub redirects you to sign in and authorize AWS DevOps Agent.

1. Review the authorization request and authorize AWS DevOps Agent.

1. After you authorize, AWS DevOps Agent completes the registration. If the GitHub App is not yet installed on the account or organization you specified, you continue to the installation page (see Step 4). If the app is already installed, registration completes without reinstalling it.

1. After installation, AWS DevOps Agent receives events from your connected repositories, including deployment events.

**Note**  
** You must authorize and install the app on the same User or Organization you specified during registration. If you authorize or install on a different account or organization, registration fails and you must restart the process, selecting the correct account or organization.

**Note**  
** AWS DevOps Agent uses a separate GitHub App for each permission level (Read & Write and Read Only), and each app is authorized independently. GitHub remembers an authorization until you revoke it under Settings > Applications > Authorized GitHub Apps. If you previously authorized the app at this permission level, GitHub might skip the authorization screen. If you change the permission level, GitHub prompts you to authorize the corresponding app the first time.

#### For GitHub Enterprise Server
<a name="for-github-enterprise-server"></a>

GitHub Enterprise Server uses a GitHub App Manifest flow, which automatically sets up a new GitHub App on your instance. This involves two redirects to your GitHub Enterprise Server instance.

1. Your browser will be redirected to your GitHub Enterprise Server instance's "Create GitHub App" page.

1. You'll see the app name pre-filled. Feel free to change the name as needed. Choose **Create GitHub App**.

1. You'll be redirected back to AWS DevOps Agent, which exchanges the manifest code for app credentials.

### Step 4: Select repositories and complete installation
<a name="step-4-select-repositories-and-complete-installation"></a>

Skip this step if the GitHub App is already installed on your account or organization.

1. The **Install & Authorize** page for the GitHub App appears.

1. Select which repositories to allow the app to access:
   + **All repositories** – Grant access to all current and future repositories
   + **Only select repositories** – Choose specific repositories from your account or organization

1. Choose **Install & Authorize**.

1. You'll be redirected back to the AWS DevOps Agent console, where GitHub will appear as registered at the account level.

## Connecting repositories to an Agent Space
<a name="connecting-repositories-to-an-agent-space"></a>

After registering GitHub at the account level, you can connect specific repositories to individual Agent Spaces:

1. In the AWS DevOps Agent console, select your Agent Space

1. Go to the **Capabilities** tab

1. In the **Pipeline** section, choose **Add**

1. Select **GitHub** from the list of available providers

1. Select the GitHub registration that contains the repositories you want to use

1. Select the subset of repositories relevant to this Agent Space

1. Choose **Add** to complete the connection

You can connect different sets of repositories to different Agent Spaces based on your organizational needs. A single Agent Space can use repositories from multiple registrations. To add repositories from another registration, repeat these steps.

## Configuring Code Review and Automated Testing
<a name="configuring-code-review-and-automated-testing"></a>

When you select repositories in the GitHub connection step, they are automatically added to the **Code Review and Automated Testing** section. This section configures which repositories automatically trigger a [Release readiness code reviews](release-management-release-readiness-code-review.md) and automated testing capabilities.

The Code Review and Automated Testing configuration includes:
+ **Capabilities** — Choose code review and automated testing capabilities for each repository. The section provides two per-repository settings:
  + **Auto trigger change review** — When enabled for a repository, DevOps Agent automatically runs a [Release readiness code reviews](release-management-release-readiness-code-review.md) each time a pull request is opened or updated. Review findings appear as inline comments on the pull request. This is enabled by default for all connected repositories.
  + **Automated verification testing** — When enabled for a repository, DevOps Agent builds, runs, and tests your code changes in a managed verification environment during code reviews. This provides functional validation beyond static analysis. For more information, see [Automated verification testing](release-management-release-readiness-code-review.md). This is enabled by default for all connected repositories.
+ **Repository list** — Shows all repositories you selected during the connection step. Use the search field to filter repositories by name. Each repository has independent checkboxes for both capabilities.
+ **Runtime role** (optional) — Choose the IAM role that DevOps Agent assumes to run automated capabilities on your selected repositories. This role is used when accessing internal services needed during builds, such as private package registries and artifact storage systems. We recommend using a different role from your primary agent role.

To configure automated reviews:

1. After connecting your repositories, navigate to the **Code Review and Automated Testing** section in your GitHub integration settings.

1. For each repository, enable or disable the **Auto trigger change review** capability depending on whether you want automatic pull request reviews.

1. For each repository, enable or disable the **Automated verification testing** capability depending on whether you want [automated verification testing](release-management-release-readiness-code-review.md) in a managed verification environment.

1. Optionally, select an IAM role from the **Runtime role** dropdown that DevOps Agent will assume when running automated capabilities on your selected repositories.

1. Choose **Save** to apply your configuration.

Once configured, any new pull request in a repository with **Auto trigger change review** enabled will automatically trigger a release readiness code review. If **Automated verification testing** is also enabled, the review includes functional validation in a verification environment. For more information about code reviews, see [Release readiness code reviews](release-management-release-readiness-code-review.md).

## Understanding the GitHub app
<a name="understanding-the-github-app"></a>

The AWS DevOps Agent GitHub app:
+ Requests access to your repositories — you can review the specific permissions during GitHub App installation
+ Receives deployment events and other repository events
+ Allows AWS DevOps Agent to correlate code changes with operational incidents
+ Can be uninstalled at any time through your GitHub settings

For GitHub Enterprise Server, the GitHub App is automatically created on your instance during registration. You can manage the app's repository access or uninstall it through **Settings > Applications > Installed GitHub Apps**. To delete the app definition entirely, go to **Settings > Developer settings > GitHub Apps**.

## GitHub App permission updates
<a name="github-app-permission-updates"></a>

AWS DevOps Agent may request permission updates after you install the GitHub App to support new features. When this happens:

1. You will receive a notification from GitHub regarding the permission update request.

1. Review the update details to understand what new permissions are being requested.

1. Choose **Accept new permissions** to grant the updated permissions.

No changes are required in your service or application. After you accept the updated permissions, the next installation access token that AWS DevOps Agent requests from GitHub will automatically include the new permissions.

**Note**  
** Until you accept a permission update, AWS DevOps Agent continues to operate with the previously granted permissions. New capabilities that depend on the updated permissions will not be available until you approve the request. The app will retain its current permissions if you choose not to accept the new permissions.

### Requested permissions
<a name="requested-permissions"></a>

The following table describes each permission the AWS DevOps Agent GitHub App requests and why it is needed.

If you selected **Read Only** during registration, the GitHub App requests read-level access only for each permission in the following table. With Read Only permissions, the GitHub App cannot perform write-level actions listed in the **Purpose** column.


| Permission | Access level | Purpose | 
| --- | --- | --- | 
| Checks | Read and write | Post release readiness code review results as check runs on pull requests, allowing review status to appear directly in the GitHub UI. | 
| Workflows | Read and write | Read workflow definitions and trigger GitHub Actions workflows for release testing in your CI/CD pipelines. | 
| Actions | Read and write | Monitor GitHub Actions workflow runs and access run logs during incident investigations and release testing. | 
| Contents | Read and write | Read repository source code for code review analysis and dependency mapping. Write access enables the agent to propose fixes for identified issues. | 
| Pull requests | Read and write | Read pull request details to trigger automated code reviews. Write access enables posting inline review comments with findings and recommended fixes. | 

## Managing GitHub connections
<a name="managing-github-connections"></a>
+ **Updating repository access** – To change which repositories the GitHub app can access, go to your GitHub account or organization settings (or your GitHub Enterprise Server instance settings), navigate to installed GitHub apps, and modify the AWS DevOps Agent app configuration.
+ **Viewing connected repositories** – In the AWS DevOps Agent console, select your Agent Space and go to the Capabilities tab to view connected repositories in the Pipeline section.
+ **Removing GitHub connection** – To disconnect GitHub from an Agent Space, select the connection in the Pipeline section and choose **Remove**. To uninstall the GitHub app completely, uninstall it from your GitHub account or organization settings. For GitHub Enterprise Server, because the GitHub App is created directly on your instance during registration, you can optionally clean up the app entirely by performing both of the following:
  + **Uninstall the app** – Go to **Settings > Applications > Installed GitHub Apps**, choose **Configure** on the app, then uninstall it.
  + **Delete the app** – Go to **Settings > Developer settings > GitHub Apps**, select the app, go to the **Advanced** tab, and choose **Delete GitHub App**. **Warning:** Deleting the GitHub App is permanent and cannot be undone. If you delete it, you will need to re-register GitHub Enterprise Server from the beginning in the AWS DevOps Agent console to create a new app.