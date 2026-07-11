

# Migrating from public preview to general availability
<a name="configuring-integrations-and-knowledge-migrating-from-public-preview-to-general-availability"></a>

If you used AWS DevOps Agent during public preview, you must update your IAM roles before the GA release. This guide walks through updating the monitoring roles and operator roles in your accounts.

## What's changing
<a name="whats-changing"></a>

1. [On-demand chat histories during preview are no longer accessible](#on-demand-chat-history-from-public-preview)

1. [New managed policies replace policies available during preview](#new-managed-policies)

1. [Agent Spaces may have an outdated IAM Identity Center application access scope](#reconnect-iam-identity-center-if-applicable)

## On-demand chat history from public preview
<a name="on-demand-chat-history-from-public-preview"></a>

The GA release introduces additional security measures to harden access controls for chat histories. As a result of these changes, on-demand chat histories from the public preview period (before March 30, 2026) are no longer accessible. Investigation journals and findings created during public preview are not affected. **This change applies only to on-demand chat conversations.**

## New Managed Policies
<a name="new-managed-policies"></a>

For GA, AWS provides new managed policies that replace the preview-era policies:


| Role type | Remove | Add | 
| --- | --- | --- | 
| Monitoring | AIOpsAssistantPolicy managed policy | AIDevOpsAgentAccessPolicy managed policy | 
| Operator (IAM and IDC) | Inline policy | AIDevOpsOperatorAppAccessPolicy managed policy | 

In addition, operator roles require updated trust policies, and IDC operator roles require a new inline policy.

### Prerequisites
<a name="prerequisites"></a>
+ Access to the AWS accounts where your DevOps Agent roles are configured (primary and all secondary accounts)
+ IAM permissions to modify roles, policies, and trust relationships
+ Your Agent Space ID, AWS account ID, and Region (visible in the DevOps Agent console)

### Step 1: Update monitoring roles
<a name="step-1-update-monitoring-roles"></a>

Update the monitoring role in your primary account and in each secondary account. These are the Primary/Secondary source roles configured under the **Capabilities** tab in your agent space (example primary/secondary role: `DevOpsAgentRole-AgentSpace-3xj2396z`).

1. In the DevOps Agent console, go to your Agent Space and choose the **Capabilities** tab.

1. Find the monitoring role for your Primary/Secondary Sources (for example, `DevOpsAgentRole-AgentSpace-3xj2396z`) and choose **Edit**.

1. Under **Permissions policies**, remove the `AIOpsAssistantPolicy` AWS managed policy.

1. Choose **Add permissions**, **Attach policies**, and attach the `AIDevOpsAgentAccessPolicy` managed policy.

1. Edit the inline policy and replace its contents with the following, substituting your account ID:

```
{
    "Version": "2012-10-17",		 	 	 		 	 	 
    "Statement": [
        {
            "Sid": "AllowCreateServiceLinkedRoles",
            "Effect": "Allow",
            "Action": [
                "iam:CreateServiceLinkedRole"
            ],
            "Resource": [
                "arn:aws:iam::<account-id>:role/aws-service-role/resource-explorer-2.amazonaws.com/AWSServiceRoleForResourceExplorer"
            ]
        }
    ]
}
```

1. The trust policy for the monitoring role does not require changes. Verify it matches the following:

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
                    "aws:SourceAccount": "<account-id>"
                },
                "ArnLike": {
                    "aws:SourceArn": "arn:aws:aidevops:<region>:<account-id>:agentspace/*"
                }
            }
        }
    ]
}
```
+ Repeat steps 2–6 for the monitoring role in each secondary account.

### Step 2: Update the operator role (IAM)
<a name="step-2-update-the-operator-role-iam"></a>

1. In the DevOps Agent console, choose the **Access** tab and find the operator role.

1. In the IAM console, remove the existing inline policy from the operator role.

1. Choose **Add permissions**, **Attach policies**, and attach the `AIDevOpsOperatorAppAccessPolicy` managed policy.

1. Choose the **Trust relationships** tab and choose **Edit trust policy**. Replace the trust policy with the following, substituting your account ID, Region, and Agent Space ID:

```
{
    "Version": "2012-10-17",		 	 	 		 	 	 
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "aidevops.amazonaws.com"
            },
            "Action": ["sts:AssumeRole", "sts:TagSession"],
            "Condition": {
                "StringEquals": {
                    "aws:SourceAccount": "<account-id>"
                },
                "ArnEquals": {
                    "aws:SourceArn": "arn:aws:aidevops:<region>:<account-id>:agentspace/<agentspace-id>"
                }
            }
        }
    ]
}
```

### Step 3: Update operator roles (IDC)
<a name="step-3-update-operator-roles-idc"></a>

If you use IAM Identity Center with DevOps Agent, update each IDC operator role.

1. In the IAM console, go to **Roles** and search for `WebappIDC` to find your DevOps Agent IDC roles (for example, `DevOpsAgentRole-WebappIDC-<id>`).

1. For each IDC role:

a. Remove the existing inline policy.

b. Choose **Add permissions**, **Attach policies**, and attach the `AIDevOpsOperatorAppAccessPolicy` managed policy.

c. Choose the **Trust relationships** tab and choose **Edit trust policy**. Replace the trust policy with the following, substituting your account ID, Region, and Agent Space ID:

```
{
    "Version": "2012-10-17",		 	 	 		 	 	 
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "aidevops.amazonaws.com"
            },
            "Action": ["sts:AssumeRole", "sts:TagSession"],
            "Condition": {
                "StringEquals": {
                    "aws:SourceAccount": "<account-id>"
                },
                "ArnEquals": {
                    "aws:SourceArn": "arn:aws:aidevops:<region>:<account-id>:agentspace/<agentspace-id>"
                }
            }
        },
        {
            "Sid": "TrustedIdentityPropagation",
            "Effect": "Allow",
            "Principal": {
                "Service": "aidevops.amazonaws.com"
            },
            "Action": "sts:SetContext",
            "Condition": {
                "StringEquals": {
                    "aws:SourceAccount": "<account-id>"
                },
                "ArnEquals": {
                    "aws:SourceArn": "arn:aws:aidevops:<region>:<account-id>:agentspace/<agentspace-id>"
                },
                "ForAllValues:ArnEquals": {
                    "sts:RequestContextProviders": [
                        "arn:aws:iam::aws:contextProvider/IdentityCenter"
                    ]
                },
                "Null": {
                    "sts:RequestContextProviders": "false"
                }
            }
        }
    ]
}
```

d. Create a new inline policy with the following permissions, substituting your account ID:

```
{
    "Version": "2012-10-17",		 	 	 		 	 	 
    "Statement": [
        {
            "Sid": "AllowDevOpsAgentSSOAccess",
            "Effect": "Allow",
            "Action": [
                "sso:ListInstances",
                "sso:DescribeInstance"
            ],
            "Resource": "*"
        },
        {
            "Sid": "AllowDevOpsAgentIDCUserAccess",
            "Effect": "Allow",
            "Action": "identitystore:DescribeUser",
            "Resource": [
                "arn:aws:identitystore::<account-id>:identitystore/*",
                "arn:aws:identitystore:::user/*"
            ]
        }
    ]
}
```

## Reconnect IAM Identity Center (if applicable)
<a name="reconnect-iam-identity-center-if-applicable"></a>

Agent Spaces created during public preview may have an IAM Identity Center application configured with an outdated access scope. For GA, the correct scope is **`aidevops:read_write`**. If your IAM Identity Center application has the previous scope (**`awsaidevops:read_write`**), you must disconnect and reconnect IAM Identity Center.

### How to check your IAM Identity Center application scope
<a name="how-to-check-your-idc-application-scope"></a>

Run the following AWS CLI command to check the scope on your IAM Identity Center application. You can find the application ARN in the IAM Identity Center console under **Applications**.

```
aws sso-admin list-application-access-scopes \
  --application-arn arn:aws:sso::<account-id>:application/<instance-id>/<application-id>
```

The output should show the correct scope **`aidevops:read_write`**:

```
{
    "Scopes": [
        {
            "Scope": "aidevops:read_write"
        }
    ]
}
```

If the scope shows **`awsaidevops:read_write`**, it is outdated. Follow the steps below to update it.

### How to reconnect IAM Identity Center
<a name="how-to-reconnect-iam-identity-center"></a>

The access scope on an AWS managed IAM Identity Center application cannot be updated directly. You must disconnect and reconnect:

1. In the AWS DevOps Agent console, go to your Agent Space and choose the **Access** tab.

1. Choose **Disconnect** next to the IAM Identity Center configuration.

1. Confirm the disconnection.

1. Choose **Connect** to set up IAM Identity Center again. The service creates a new IAM Identity Center application with the correct scope.

1. Reassign users and groups to the new application in the IAM Identity Center console.

**Important**  
Disconnecting removes individual user chat and artifact history associated with IAM Identity Center user accounts. Users will need to log in again after reconnection.

## Verification
<a name="verification"></a>

After completing all steps:

1. Return to the DevOps Agent console and verify that no permission errors appear on the Agent Space **Access** tab.

1. Test the operator web app to confirm it loads and functions correctly.

1. If you use IDC, verify that users can authenticate and access the operator experience.

## Troubleshooting
<a name="troubleshooting"></a>

**Permission denied errors after migration**
+ Verify that `AIOpsAssistantPolicy` was removed and `AIDevOpsAgentAccessPolicy` is attached to monitoring roles.
+ Verify that old inline policies were removed and `AIDevOpsOperatorAppAccessPolicy` is attached to operator roles.
+ Check that operator trust policies include `sts:TagSession`.
+ Confirm you replaced all placeholder values (`<account-id>`, `<region>`, `<agentspace-id>`) with actual values.

**Secondary accounts not working**
+ Each secondary account's monitoring role must be updated independently. Log into each account and repeat Step 1.

**IDC authentication failures**
+ Verify the IDC trust policy includes both the `sts:AssumeRole`/`sts:TagSession` statement and the `TrustedIdentityPropagation` statement.
+ Confirm the inline policy with `sso:ListInstances`, `sso:DescribeInstance`, and `identitystore:DescribeUser` was created.

**On-demand chat history missing after migration**
+ On-demand chat histories from the public preview period are not accessible after the GA release. This is expected behavior due to enhanced security measures introduced in GA. Investigation journals and findings from public preview are not affected.