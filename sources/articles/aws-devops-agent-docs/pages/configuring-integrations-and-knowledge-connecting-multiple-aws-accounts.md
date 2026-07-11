

# Connecting multiple AWS Accounts
<a name="configuring-integrations-and-knowledge-connecting-multiple-aws-accounts"></a>

Secondary AWS accounts allow AWS DevOps Agent to investigate resources across multiple AWS accounts in your organization. When your applications span multiple accounts, adding secondary accounts ensures the agent has visibility into all relevant resources during incident investigations. Greater access to the accounts and resources composing an application ensures greater investigation accuracy.

## Prerequisites
<a name="prerequisites"></a>

Before adding a secondary AWS account, ensure you have:
+ Access to the AWS DevOps Agent console in the primary account
+ Administrative access to the secondary AWS account
+ IAM permissions to create roles in the secondary account

## Adding a secondary AWS account
<a name="adding-a-secondary-aws-account"></a>

In addition to the steps below, you can use the [AWS DevOps Agent CLI onboarding guide](getting-started-with-aws-devops-agent-cli-onboarding-guide.md) to programmatically add secondary accounts.

### Step 1: Start the secondary account configuration
<a name="step-1-start-the-secondary-account-configuration"></a>

1. Sign in to the AWS Management Console and navigate to the AWS DevOps Agent console

1. Select your Agent Space

1. Go to the **Capabilities** tab

1. In the **Cloud** section, locate the **Secondary sources** subsection

1. Choose **Add**

### Step 2: Specify the role name
<a name="step-2-specify-the-role-name"></a>

1. In the **Name your role** field, enter a name for the role you'll create in the secondary account

1. Note this name—you'll use it again when creating the role in the secondary account

1. Copy the trust policy provided in the console and save it in a scratch space

### Step 3: Create the role in the secondary account
<a name="step-3-create-the-role-in-the-secondary-account"></a>

1. Open a new browser tab and sign in to the IAM console in the secondary AWS account

1. Navigate to **IAM >****Roles** > **Create role**

1. Select **Custom trust policy**

1. Paste the trust policy you copied from Step 2

1. Choose **Next**

### Step 4: Attach the AWS managed policy
<a name="step-4-attach-the-aws-managed-policy"></a>

1. In the **Permissions policies** section, search for **AIDevOpsAgentAccessPolicy**

1. Select the checkbox next to the **AIDevOpsAgentAccessPolicy** managed policy

1. Choose **Next**

### Step 5: Name and create the role
<a name="step-5-name-and-create-the-role"></a>

1. In the **Role name** field, enter the same role name you provided in Step 2

1. (Optional) Add a description to help identify the role's purpose

1. Review the trust policy and attached permissions

1. Choose **Create role**

### Step 6: Attach the inline policy
<a name="step-6-attach-the-inline-policy"></a>

1. In the IAM console, locate and select the role you just created

1. Go to the **Permissions** tab

1. Choose **Add permissions** > **Create inline policy**

1. Switch to the **JSON** tab

1. Paste the policy you saved in Step 2

1. Paste the policy into the JSON editor in the IAM console

1. Choose **Next**

1. Provide a name for the inline policy (for example, "DevOpsAgentInlinePolicy")

1. Choose **Create policy**

### Step 7: Complete the configuration
<a name="step-7-complete-the-configuration"></a>

1. Return to the AWS DevOps Agent console in the primary account

1. Choose **Next** to complete the secondary account configuration

1. Verify the connection status shows as **Active**

## Understanding the required policies
<a name="understanding-the-required-policies"></a>

AWS DevOps Agent requires three policy components to access resources in a secondary account:
+ **Trust policy** – Allows AWS DevOps Agent in the primary account to assume the role in the secondary account. This establishes the trust relationship between accounts.
+ **AIDevOpsAgentAccessPolicy (AWS managed policy)** – Provides the core read-only permissions AWS DevOps Agent needs to investigate resources in the secondary account. This policy is maintained by AWS and updated as new capabilities are added.
+ **Inline policy** – Provides additional permissions specific to your Agent Space configuration. This policy is generated based on your Agent Space settings and may include permissions for specific integrations or features.

In the primary account, the AWS DevOps Agent IAM Role must be able to assume the role created in the secondary account.

## Managing secondary accounts
<a name="managing-secondary-accounts"></a>
+ **Viewing connected accounts** – In the **Capabilities** tab, the **Secondary sources** subsection lists all connected secondary accounts with their connection status.
+ **Updating the IAM role** – If you need to modify permissions, update the inline policy attached to the role in the secondary account. Changes take effect immediately.
+ **Removing a secondary account** – To disconnect a secondary account, select it in the **Secondary sources** list and choose **Remove**. This does not delete the IAM role in the secondary account.