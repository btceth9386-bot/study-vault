

# Setting Up IAM Identity Center Authentication
<a name="aws-devops-agent-security-setting-up-iam-identity-center-authentication"></a>

IAM Identity Center authentication provides a centralized way to manage user access to the AWS DevOps Agent Space web application. This guide explains how to configure IAM Identity Center authentication and manage users.

## Prerequisites
<a name="prerequisites"></a>

Before setting up IAM Identity Center authentication, ensure you have:
+ IAM Identity Center enabled in your organization or account
+ Administrator permissions in AWS DevOps Agent
+ An Agent Space configured or ready to create

## Authentication options
<a name="authentication-options"></a>

AWS DevOps Agent offers two authentication methods for accessing the Agent Space web app:

**IAM Identity Center authentication** – Recommended for production environments. Provides centralized user management, integration with external identity providers, and sessions up to 12 hours.

**Admin access (IAM authentication)** – Provides quick access for administrators during initial setup and configuration. Sessions are limited to 30 minutes.

## Configuring IAM Identity Center during Agent Space creation
<a name="configuring-iam-identity-center-during-agent-space-creation"></a>

When you create an Agent Space, you can configure IAM Identity Center authentication on the **Access** tab:

### Step 1: Navigate to the Web app configuration
<a name="step-1-navigate-to-the-web-app-configuration"></a>

1. After configuring your Agent Space details and AWS account access, proceed to the **Access** tab

1. You'll see two sections: "Connect IAM Identity Center" and "Admin access"

### Step 2: Configure IAM Identity Center integration
<a name="step-2-configure-iam-identity-center-integration"></a>

In the **Connect [Agent Space] to IAM Identity Center** section:

1. **Verify the IAM Identity Center instance** – The console displays which Identity Center instance will manage Web App user access (for example, `ssoins-7223a9580931edbe`). Your closest IAM Identity Center instance will automatically be pre-populated.

1. **Select the IAM Identity Center Application Role Name option** – Choose one of three options:

**Auto-create a new DevOps Agent role** (recommended):
+ The system automatically creates a new service role with appropriate permissions
+ This is the simplest option and works for most use cases

**Assign an existing role**:
+ Use an existing IAM role that you've already created
+ The system will verify the role has the required permissions
+ Choose this option if your organization has pre-created roles for AWS DevOps Agent

**Create a new DevOps Agent role using a policy template**:
+ Use the provided policy details to create your own custom role in the IAM Console
+ Choose this option if you need to customize the role permissions

After choosing Connect, the system automatically:
+ Creates or configures the specified IAM role
+ Sets up an IAM Identity Center application for your Agent Space
+ Establishes trust relationships between IAM Identity Center and the Agent Space web app
+ Configures OAuth 2.0 authentication flows for secure user access

### Alternative: Using admin access
<a name="alternative-using-admin-access"></a>

If you want to access the Agent Space web app immediately without setting up IAM Identity Center:

1. In the **Admin access** section, note the IAM Role ARN that provides administrator access (for example, `arn:aws:iam::440491339484:role/service-role/DevOpsAgentRole-WebappAdmin-15ppoc42`)

1. Choose the **Admin access** button to launch the Agent Space web app with IAM authentication

1. Sessions using this method are limited to 30 minutes

**Note**  
** Admin access is intended for initial setup and configuration. For production use and ongoing operations, configure IAM Identity Center authentication.

## Adding users and groups
<a name="adding-users-and-groups"></a>

To connect your IAM Identity Center instance with DevOps Agent, you need the following IAM permissions:
+ aidevops:EnableOperatorApp
+ sso:CreateApplicationAssignment
+ sso:DeleteApplicationAssignment
+ sso:ListApplicationAssignments
+ sso:DescribeApplication

After configuring IAM Identity Center authentication, you need to grant specific users and groups access to the Agent Space web app:

### Step 1: Access user management
<a name="step-1-access-user-management"></a>

1. In the AWS DevOps Agent console, select your Agent Space

1. Go to the **Access** tab

1. Under **User Access**, choose **Manage Users and Groups**

### Step 2: Add users or groups
<a name="step-2-add-users-or-groups"></a>

1. Choose **Add Users or Groups**

1. Search for users or groups in your IAM Identity Center directory

1. Select the checkboxes next to the users or groups you want to add

1. Choose **Add** to grant them access

The selected users can now access the Agent Space web app using their IAM Identity Center credentials.

### Working with external identity providers
<a name="working-with-external-identity-providers"></a>

If you're using an external identity provider (such as Okta, Microsoft Entra ID, or Ping Identity) with IAM Identity Center:
+ Users and groups are synchronized from your external identity provider to IAM Identity Center
+ When you add users and groups to the Agent Space web app, you're selecting from the synchronized directory
+ User attributes and group memberships are maintained by your external identity provider
+ Changes in your identity provider are automatically reflected in IAM Identity Center after synchronization

## How users access the Agent Space web app
<a name="how-users-access-the-agent-space-web-app"></a>

After you've added users to your Agent Space:

1. Share the Agent Space web app URL with authorized users

1. When users navigate to the URL, they're redirected to the IAM Identity Center login page

1. After entering their credentials (and completing MFA if configured), they're redirected back to the Agent Space web app

1. Their session is valid for 8 hours by default (configurable by the Identity Center administrator)

## Managing user access
<a name="managing-user-access"></a>

You can update user access at any time:

**Adding more users or groups:**
+ Follow the same steps described above to add additional users or groups

**Removing access:**

1. In the **User Access** section, find the user or group to remove

1. Choose the **Remove** button next to their name

1. Confirm the removal

Removed users will lose access immediately, but active sessions may continue until they expire.

## Session management
<a name="session-management"></a>

IAM Identity Center sessions for the Agent Space web app have the following characteristics:
+ **Default session duration** – 8 hours
+ **Session security** – HTTP-only cookies for enhanced protection
+ **Multi-factor authentication** – Supported when configured in IAM Identity Center
+ **API credentials** – Short-duration (15-minute) SigV4 credentials are issued for API calls and renewed automatically

To configure session duration:

1. Navigate to the IAM Identity Center console

1. Go to **Settings** > **Authentication**

1. Under **Session duration**, configure your preferred duration (from 1 hour to 12 hours)

1. Choose **Save changes**

## Disconnecting Identity Center
<a name="disconnecting-identity-center"></a>

1. In your Agent Space’s console, choose **Actions** in the top-right and select **Disconnect from IAM Identity Center**

1. Confirm in confirmation dialog