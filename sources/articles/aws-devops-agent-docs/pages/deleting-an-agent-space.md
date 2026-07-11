

# Deleting an Agent space
<a name="deleting-an-agent-space"></a>

This page explains how to delete an AWS DevOps Agent agent space and remove the IAM resources that were created in your AWS account when you enabled AWS DevOps Agent. AWS DevOps Agent does not provide an automatic disable or uninstall action. You remove resources by following the procedures on this page.

**Important**  
** Deleting the agent space permanently removes all investigation data, chat history, agent journals, recommendations, and the application topology graph. Deleting IAM roles removes the agent's access to your AWS account and users' access to the operator web app. These actions cannot be undone.

## Prerequisites
<a name="prerequisites"></a>

Before you begin, make sure that you have the following:
+ Sign-in access to the AWS Management Console as an IAM user or user in IAM Identity Center.
+ Permissions to delete agent spaces in the AWS DevOps Agent service (`aidevops:ListAgentSpaces` and `aidevops:DeleteAgentSpace`).
+ Permissions to manage IAM roles and policies in your AWS account (`iam:ListRoles`, `iam:ListPolicies`, `iam:ListAttachedRolePolicies`, `iam:DetachRolePolicy`, `iam:DeleteRole`, and `iam:DeletePolicy`).

AWS DevOps Agent is a regional service. The agent space and the data it generates are stored in the AWS Region where you enabled the agent. You must perform the agent space deletion procedure in each Region where your account has an agent space. IAM resources are global, so you only delete them once. For the list of Regions where AWS DevOps Agent is available, see [Supported Regions](about-aws-devops-agent-supported-regions.md).

**Important**  
** You must delete resources in the following order. The IAM roles cannot be safely removed while the agent space still references them.

The following table lists the resources created when you enable AWS DevOps Agent. Use it as a checklist while you work through the procedures.


| AWS service | Resource type | Resource name | 
| --- | --- | --- | 
| AWS DevOps Agent | Agent space | The name you gave the agent space (default: DevOpsAgentSpace) | 
| AWS Identity and Access Management (IAM) | Role | AgentSpace role (typically named DevOpsAgentRole-AgentSpace-\*) | 
| AWS Identity and Access Management (IAM) | Role | WebappAdmin role (typically named DevOpsAgentRole-WebappAdmin-\*) | 
| AWS Identity and Access Management (IAM) | Customer-managed policy | Any customer-managed policies attached to the AgentSpace role | 

The exact role and policy names depend on your onboarding path. Use the AWS CLI procedures below or search by the `DevOpsAgentRole-` prefix in the IAM console to find the actual names in your account.

**Note**  
** The two AWS managed policies attached to the IAM roles (`AIDevOpsAgentAccessPolicy` and `AIDevOpsOperatorAppAccessPolicy`) are owned by AWS and are not deleted. You only detach them as part of role deletion.

## Delete the agent space
<a name="delete-the-agent-space"></a>

Deleting the agent space removes its service association, its operator app configuration, and all investigation data, chat history, agent journals, recommendations, and the application topology graph.

### Using the AWS DevOps Agent console
<a name="using-the-aws-devops-agent-console"></a>

1. Open the AWS DevOps Agent console at [https://console.aws.amazon.com/aidevops/](https://console.aws.amazon.com/aidevops/).

1. Change your AWS Region to the Region where the agent space lives.

1. In the navigation pane, choose **Agent spaces**.

1. From the table, select the agent space you want to remove. The **Agent space details** page opens.

1. From **Actions**, choose **Delete agent space**.

1. In the dialog box that opens, review the information to make sure it is accurate, enter the name of the agent space to confirm, and then choose **Delete**.

### Using the AWS CLI
<a name="using-the-aws-cli"></a>

**Step 1.** List the agent spaces in your Region to find your `agentSpaceId`. Save the value from the response. Replace `REGION` with the Region where your agent space lives, for example, `us-east-1`.

```
aws devops-agent list-agent-spaces --region REGION
```

**Step 2.** Delete the agent space. Replace `AGENT_SPACE_ID` with the value from Step 1.

```
aws devops-agent delete-agent-space --agent-space-id AGENT_SPACE_ID --region REGION
```

### Verifying that the agent space is deleted
<a name="verifying-that-the-agent-space-is-deleted"></a>

Run the following command and confirm that the response contains an empty list.

```
aws devops-agent list-agent-spaces --region REGION
```

## Delete IAM resources
<a name="delete-iam-resources"></a>

These procedures walk you through how to remove the IAM roles and any customer-managed IAM policies that were created in your AWS account when you enabled AWS DevOps Agent. Because the role and policy names depend on your onboarding path, the procedures below either search for them by prefix in the IAM console or discover their full names through the AWS CLI.

**Important**  
** Leaving customer-managed policies in your account is the most common cause of failures the next time you re-enable AWS DevOps Agent through the same onboarding path. Complete all steps in this section to avoid issues if you re-enable later.

### Deleting the AWS DevOps Agent IAM roles (console)
<a name="deleting-the-aws-devops-agent-iam-roles-console"></a>

1. Open the IAM console at [https://console.aws.amazon.com/iam/](https://console.aws.amazon.com/iam/).

1. In the navigation pane, choose **Roles**.

1. From the table, search for roles with the name **DevOpsAgentRole**. Two roles are returned, with names of the form `DevOpsAgentRole-AgentSpace-<suffix>` and `DevOpsAgentRole-WebappAdmin-<suffix>`.

1. For each role in the table, select the check box for the role, choose **Delete**, then in the confirmation dialog enter the role name to confirm and choose **Delete**.

### Deleting any customer-managed IAM policies (console)
<a name="deleting-any-customer-managed-iam-policies-console"></a>

If your onboarding path attached a customer-managed policy to the AgentSpace role, delete the policy after you delete the role.

1. Open the IAM console at [https://console.aws.amazon.com/iam/](https://console.aws.amazon.com/iam/).

1. In the navigation pane, choose **Policies**.

1. Filter by **Type: Customer managed**, and look for any policies whose name starts with `AIDevOps` or any other identifier you used during onboarding.

1. For each policy you want to remove, select the check box for the policy, choose **Actions**, and then choose **Delete** from the dropdown menu. In the dialog box that opens, review the information, enter the name of the policy to confirm, and then choose **Delete**.

### Using the AWS CLI
<a name="using-the-aws-cli"></a>

**Step 1.** Discover the role names created by activation. Save the role names from the responses for use in the following steps.

```
aws iam list-roles --query "Roles[?starts_with(RoleName, 'DevOpsAgentRole-AgentSpace')].RoleName" --output text
aws iam list-roles --query "Roles[?starts_with(RoleName, 'DevOpsAgentRole-WebappAdmin')].RoleName" --output text
```

**Step 2.** List the policies attached to each role. Replace `ROLE_NAME` with each role name from Step 1.

```
aws iam list-attached-role-policies --role-name ROLE_NAME
```

In the response, customer-managed policy ARNs contain your 12-digit AWS account ID (for example, `arn:aws:iam::123456789012:policy/...`). AWS managed policy ARNs contain the literal `aws` (for example, `arn:aws:iam::aws:policy/AIDevOpsAgentAccessPolicy`). Save the customer-managed policy ARNs for Step 4.

**Step 3.** Detach all policies from each role and then delete the role. Run the `detach-role-policy` command once for each policy ARN that the previous step returned. Replace `ROLE_NAME` with the role name and `POLICY_ARN` with each ARN.

```
aws iam detach-role-policy --role-name ROLE_NAME --policy-arn POLICY_ARN
aws iam delete-role --role-name ROLE_NAME
```

**Step 4.** Delete any customer-managed policies that you saved in Step 2. Replace `CUSTOMER_POLICY_ARN` with each ARN.

```
aws iam delete-policy --policy-arn CUSTOMER_POLICY_ARN
```

### Verifying that the IAM resources are removed
<a name="verifying-that-the-iam-resources-are-removed"></a>

Run the following commands. The first call should return an empty result. The second call should not return any policies that you owned and deleted.

```
aws iam list-roles --query "Roles[?starts_with(RoleName, 'DevOpsAgentRole-')].RoleName" --output text
aws iam list-policies --scope Local --query "Policies[?starts_with(PolicyName, 'AIDevOps')].PolicyName" --output text
```

## Re-enabling AWS DevOps Agent after cleanup
<a name="re-enabling-aws-devops-agent-after-cleanup"></a>

If you removed AWS DevOps Agent resources by following the procedures above and you later want to enable AWS DevOps Agent again, see [Getting started with AWS DevOps Agent](getting-started-with-aws-devops-agent.md). Keep the following in mind:
+ If you did not delete the customer-managed IAM policies, the next enablement attempt through the same onboarding path may fail with a role-already-exists error. Delete the leftover policies first.
+ After you delete an agent space, the name is reserved for a short period. If you re-enable immediately and use the same name, creation may be delayed.

## Related resources
<a name="related-resources"></a>
+ [What are DevOps Agent Spaces?](about-aws-devops-agent-what-are-devops-agent-spaces.md)
+ [DevOps Agent IAM permissions](aws-devops-agent-security-devops-agent-iam-permissions.md)
+ [AWS DevOps Agent Security](aws-devops-agent-security.md)
+ [Getting started with AWS DevOps Agent](getting-started-with-aws-devops-agent.md)