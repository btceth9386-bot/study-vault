

# AWS DevOps Agent CLI onboarding guide
<a name="getting-started-with-aws-devops-agent-cli-onboarding-guide"></a>

## Overview
<a name="overview"></a>

With AWS DevOps Agent, you can monitor and manage your AWS infrastructure. This guide walks you through setting up AWS DevOps Agent by using the AWS Command Line Interface (AWS CLI). You create IAM roles, set up an agent space, and associate your AWS account. You also enable the operator app and optionally connect third-party integrations. This guide takes approximately 20 minutes to complete.

AWS DevOps Agent is available in six AWS Regions: US East (N. Virginia), US West (Oregon), Asia Pacific (Sydney), Asia Pacific (Tokyo), Europe (Frankfurt), and Europe (Ireland). For more information about supported Regions, see [Supported Regions](about-aws-devops-agent-supported-regions.md).

## Prerequisites
<a name="prerequisites"></a>

Before you begin, make sure that you have the following:
+ AWS CLI version 2 installed and configured
+ Authentication to your AWS monitoring account
+ Permissions to create AWS Identity and Access Management (IAM) roles and attach policies
+ An AWS account to use as the monitoring account
+ Familiarity with the AWS CLI and JSON syntax

Throughout this guide, replace the following placeholder values with your own:
+ `<MONITORING_ACCOUNT_ID>` — Your 12-digit AWS account ID for the monitoring (primary) account
+ `<EXTERNAL_ACCOUNT_ID>` — The 12-digit AWS account ID of the secondary account to monitor (used in step 4)
+ `<REGION>` — The AWS Region code for your agent space (for example, `us-east-1` or `eu-central-1`)
+ `<AGENT_SPACE_ID>` — The agent space identifier that is returned by the `create-agent-space` command

## IAM roles setup
<a name="iam-roles-setup"></a>

### 1. Create the DevOps Agent space role
<a name="1-create-the-devops-agent-space-role"></a>

Create the IAM trust policy by running the following command:

```
cat > devops-agentspace-trust-policy.json << 'EOF'
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
          "aws:SourceAccount": "<MONITORING_ACCOUNT_ID>"
        },
        "ArnLike": {
          "aws:SourceArn": "arn:aws:aidevops:<REGION>:<MONITORING_ACCOUNT_ID>:agentspace/*"
        }
      }
    }
  ]
}
EOF
```

Create the IAM role:

```
aws iam create-role \
  --region <REGION> \
  --role-name DevOpsAgentRole-AgentSpace \
  --assume-role-policy-document file://devops-agentspace-trust-policy.json
```

Save the role ARN by running the following command:

```
aws iam get-role --role-name DevOpsAgentRole-AgentSpace --query 'Role.Arn' --output text
```

Attach the AWS managed policy:

```
aws iam attach-role-policy \
  --role-name DevOpsAgentRole-AgentSpace \
  --policy-arn arn:aws:iam::aws:policy/AIDevOpsAgentAccessPolicy
```

Create and attach an inline policy to allow creation of the Resource Explorer service-linked role:

```
cat > devops-agentspace-additional-policy.json << 'EOF'
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
        "arn:aws:iam::<MONITORING_ACCOUNT_ID>:role/aws-service-role/resource-explorer-2.amazonaws.com/AWSServiceRoleForResourceExplorer"
      ]
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name DevOpsAgentRole-AgentSpace \
  --policy-name AllowCreateServiceLinkedRoles \
  --policy-document file://devops-agentspace-additional-policy.json
```

### 2. Create the operator app IAM role
<a name="2-create-the-operator-app-iam-role"></a>

Create the IAM trust policy by running the following command:

```
cat > devops-operator-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",		 	 	 		 	 	 
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "aidevops.amazonaws.com"
      },
      "Action": [
        "sts:AssumeRole",
        "sts:TagSession"
      ],
      "Condition": {
        "StringEquals": {
          "aws:SourceAccount": "<MONITORING_ACCOUNT_ID>"
        },
        "ArnLike": {
          "aws:SourceArn": "arn:aws:aidevops:<REGION>:<MONITORING_ACCOUNT_ID>:agentspace/*"
        }
      }
    }
  ]
}
EOF
```

Create the IAM role:

```
aws iam create-role \
  --role-name DevOpsAgentRole-WebappAdmin \
  --assume-role-policy-document file://devops-operator-trust-policy.json \
  --region <REGION>
```

Save the role ARN by running the following command:

```
aws iam get-role --role-name DevOpsAgentRole-WebappAdmin --query 'Role.Arn' --output text
```

Attach the AWS managed operator app policy:

```
aws iam attach-role-policy \
  --role-name DevOpsAgentRole-WebappAdmin \
  --policy-arn arn:aws:iam::aws:policy/AIDevOpsOperatorAppAccessPolicy
```

This managed policy grants the operator app permissions to access agent space features. These features include investigations, recommendations, knowledge management, chat, and AWS Support integration. The policy scopes access to the specific agent space by using the `aws:PrincipalTag/AgentSpaceId` condition. For more information about the full list of actions, see [DevOps Agent IAM permissions](aws-devops-agent-security-devops-agent-iam-permissions.md).

## Onboarding steps
<a name="onboarding-steps"></a>

### 1. Create an agent space
<a name="1-create-an-agent-space"></a>

Run the following command to create an agent space:

```
aws devops-agent create-agent-space \
  --name "MyAgentSpace" \
  --description "AgentSpace for monitoring my application" \
  --region <REGION>
```

Optionally, specify `--kms-key-arn` to use a customer managed AWS KMS key for encryption. You can also use `--tags` to add resource tags and `--locale` to set the language for agent responses.

Save the `agentSpaceId` from the response (located at `agentSpace.agentSpaceId`).

To list your agent spaces later, run the following command:

```
aws devops-agent list-agent-spaces \
  --region <REGION>
```

### 2. Associate your AWS account
<a name="2-associate-your-aws-account"></a>

Associate your AWS account to turn on topology discovery. Set the `accountType` to one of the following values:
+ `monitor` — The primary account where the agent space exists. This account hosts the agent and is used for topology discovery.
+ `source` — An additional account that the agent monitors. Use this type when you associate external accounts in step 4.

```
aws devops-agent associate-service \
  --agent-space-id <AGENT_SPACE_ID> \
  --service-id aws \
  --configuration '{
    "aws": {
      "assumableRoleArn": "arn:aws:iam::<MONITORING_ACCOUNT_ID>:role/DevOpsAgentRole-AgentSpace",
      "accountId": "<MONITORING_ACCOUNT_ID>",
      "accountType": "monitor"
    }
  }' \
  --region <REGION>
```

### 3. Enable the operator app
<a name="3-enable-the-operator-app"></a>

Authentication flows can use IAM, IAM Identity Center (IDC), or an external identity provider (IdP). Run the following command to enable the operator app for your agent space:

```
aws devops-agent enable-operator-app \
  --agent-space-id <AGENT_SPACE_ID> \
  --auth-flow iam \
  --operator-app-role-arn "arn:aws:iam::<MONITORING_ACCOUNT_ID>:role/DevOpsAgentRole-WebappAdmin" \
  --region <REGION>
```

For IAM Identity Center authentication, use `--auth-flow idc` and provide `--idc-instance-arn`. For an external identity provider, use `--auth-flow idp` and provide `--issuer-url`, `--idp-client-id`, and `--idp-client-secret`. For more information, see [Setting Up IAM Identity Center Authentication](aws-devops-agent-security-setting-up-iam-identity-center-authentication.md) and [Setting Up External Identity Provider (IdP) Authentication](aws-devops-agent-security-setting-up-external-identity-provider-idp-authentication.md).

**Note:** If you previously created an operator app role for another agent space in your account, you can reuse that role ARN.

### 4. (Optional) Associate additional source accounts
<a name="4-optional-associate-additional-source-accounts"></a>

To monitor additional accounts with AWS DevOps Agent, create an IAM cross-account role.

#### Create the cross-account role in the external account
<a name="create-the-cross-account-role-in-the-external-account"></a>

Switch to the external account and create the trust policy. The `MONITORING_ACCOUNT_ID` is the main account that hosts the agent space that you set up in step 2. This configuration allows the AWS DevOps Agent service to assume a role in the secondary source accounts on behalf of the monitoring account.

Run the following command to create the trust policy:

```
cat > devops-cross-account-trust-policy.json << 'EOF'
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
          "aws:SourceAccount": "<MONITORING_ACCOUNT_ID>",
          "sts:ExternalId": "arn:aws:aidevops:<REGION>:<MONITORING_ACCOUNT_ID>:agentspace/<AGENT_SPACE_ID>"
        }
      }
    }
  ]
}
EOF
```

Create the cross-account IAM role:

```
aws iam create-role \
  --role-name DevOpsAgentCrossAccountRole \
  --assume-role-policy-document file://devops-cross-account-trust-policy.json
```

Save the role ARN by running the following command:

```
aws iam get-role --role-name DevOpsAgentCrossAccountRole --query 'Role.Arn' --output text
```

Attach the AWS managed policy:

```
aws iam attach-role-policy \
  --role-name DevOpsAgentCrossAccountRole \
  --policy-arn arn:aws:iam::aws:policy/AIDevOpsAgentAccessPolicy
```

Attach the inline policy to allow creation of the Resource Explorer service-linked role in the external account:

```
cat > devops-cross-account-additional-policy.json << 'EOF'
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
        "arn:aws:iam::<EXTERNAL_ACCOUNT_ID>:role/aws-service-role/resource-explorer-2.amazonaws.com/AWSServiceRoleForResourceExplorer"
      ]
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name DevOpsAgentCrossAccountRole \
  --policy-name AllowCreateServiceLinkedRoles \
  --policy-document file://devops-cross-account-additional-policy.json
```

#### Associate the external account
<a name="associate-the-external-account"></a>

Switch back to your monitoring account, and then run the following command to associate the external account:

```
aws devops-agent associate-service \
  --agent-space-id <AGENT_SPACE_ID> \
  --service-id aws \
  --configuration '{
    "sourceAws": {
      "accountId": "<EXTERNAL_ACCOUNT_ID>",
      "accountType": "source",
      "assumableRoleArn": "arn:aws:iam::<EXTERNAL_ACCOUNT_ID>:role/DevOpsAgentCrossAccountRole"
    }
  }' \
  --region <REGION>
```

### 5. (Optional) Associate GitHub
<a name="5-optional-associate-github"></a>

**Note:** You must first register GitHub through the AWS DevOps Agent console by using the OAuth flow before you can associate it through the CLI.

For instructions on registering GitHub through the console, see [Connecting to CI/CD pipelines](configuring-integrations-and-knowledge-connecting-to-cicd-pipelines-index.md).

List the registered services:

```
aws devops-agent list-services \
  --region <REGION>
```

Save the `<SERVICE_ID>` for serviceType: `github`.

After you register GitHub in the console, associate GitHub repositories by running the following command:

```
aws devops-agent associate-service \
  --agent-space-id <AGENT_SPACE_ID> \
  --service-id <SERVICE_ID> \
  --configuration '{
    "github": {
      "repoName": "<GITHUB_REPO_NAME>",
      "repoId": "<GITHUB_REPO_ID>",
      "owner": "<GITHUB_OWNER>",
      "ownerType": "organization"
    }
  }' \
  --region <REGION>
```

### 6. (Optional) Register and associate ServiceNow
<a name="6-optional-register-and-associate-servicenow"></a>

First, register the ServiceNow service with OAuth credentials:

```
aws devops-agent register-service \
  --service servicenow \
  --service-details  '{
    "servicenow": {
      "instanceUrl": "<SERVICENOW_INSTANCE_URL>",
      "authorizationConfig": {
        "oAuthClientCredentials": {
            "clientName": "<SERVICENOW_CLIENT_NAME>",
            "clientId": "<SERVICENOW_CLIENT_ID>",
            "clientSecret": "<SERVICENOW_CLIENT_SECRET>"
        }
      }
    }
  }' \
  --region <REGION>
```

Save the returned `<SERVICE_ID>`, then associate ServiceNow:

```
aws devops-agent associate-service \
  --agent-space-id <AGENT_SPACE_ID> \
  --service-id <SERVICE_ID> \
  --configuration '{
    "servicenow": {
      "instanceUrl": "<SERVICENOW_INSTANCE_URL>"
    }
  }' \
  --region <REGION>
```

### 7. (Optional) Register and associate Dynatrace
<a name="7-optional-register-and-associate-dynatrace"></a>

First, register the Dynatrace service with OAuth credentials:

```
aws devops-agent register-service \
  --service dynatrace \
  --service-details '{
  "dynatrace": {
    "accountUrn": "<DYNATRACE_ACCOUNT_URN>",
    "authorizationConfig": {
        "oAuthClientCredentials": {
            "clientName": "<DYNATRACE_CLIENT_NAME>",
            "clientId": "<DYNATRACE_CLIENT_ID>",
            "clientSecret": "<DYNATRACE_CLIENT_SECRET>"
        }
      }
    }
  }' \
  --region <REGION>
```

Save the returned `<SERVICE_ID>`, then associate Dynatrace. Resources are optional. The environment specifies which Dynatrace environment to associate with.

```
aws devops-agent associate-service \
  --agent-space-id <AGENT_SPACE_ID> \
  --service-id <SERVICE_ID> \
  --configuration '{
    "dynatrace": {
      "envId": "<DYNATRACE_ENVIRONMENT_ID>",
      "resources": [
        "<DYNATRACE_RESOURCE_1>",
        "<DYNATRACE_RESOURCE_2>"
      ]
    }
  }' \
  --region <REGION>
```

The response includes webhook information for integration. You can use this webhook to trigger an investigation from Dynatrace. For more information, see [Connecting Dynatrace](connecting-telemetry-sources-connecting-dynatrace.md).

### 8. (Optional) Register and associate Splunk
<a name="8-optional-register-and-associate-splunk"></a>

First, register the Splunk service with BearerToken credentials.

The endpoint uses the following format: `https://<XXX>.api.scs.splunk.com/<XXX>/mcp/v1/`

```
aws devops-agent register-service \
  --service mcpserversplunk \
  --service-details '{
  "mcpserversplunk": {
    "name": "<SPLUNK_NAME>",
    "endpoint": "<SPLUNK_ENDPOINT>",
    "authorizationConfig": {
        "bearerToken": {
            "tokenName": "<SPLUNK_TOKEN_NAME>",
            "tokenValue": "<SPLUNK_TOKEN_VALUE>"
        }
      }
    }
  }' \
  --region <REGION>
```

Save the returned `<SERVICE_ID>`, then associate Splunk:

```
aws devops-agent associate-service \
  --agent-space-id <AGENT_SPACE_ID> \
  --service-id <SERVICE_ID> \
  --configuration '{
    "mcpserversplunk":  {
      "name": "<SPLUNK_NAME>",
      "endpoint": "<SPLUNK_ENDPOINT>"
    }
  }' \
  --region <REGION>
```

The response includes webhook information for integration. You can use this webhook to trigger an investigation from Splunk. For more information, see [Connecting Splunk](connecting-telemetry-sources-connecting-splunk.md).

### 9. (Optional) Register and associate New Relic
<a name="9-optional-register-and-associate-new-relic"></a>

First, register the New Relic service with API key credentials.

Region: Either `US` or `EU`.

Optional fields: `applicationIds`, `entityGuids`, `alertPolicyIds`

```
aws devops-agent register-service \
  --service mcpservernewrelic \
  --service-details '{
    "mcpservernewrelic": {
      "authorizationConfig": {
        "apiKey": {
          "apiKey": "<YOUR_NEW_RELIC_API_KEY>",
          "accountId": "<YOUR_ACCOUNT_ID>",
          "region": "US",
          "applicationIds": ["<APP_ID_1>", "<APP_ID_2>"],
          "entityGuids": ["<ENTITY_GUID_1>"],
          "alertPolicyIds": ["<POLICY_ID_1>"]
        }
      }
    }
  }' \
  --region <REGION>
```

Save the returned `<SERVICE_ID>`, then associate New Relic:

```
aws devops-agent associate-service \
  --agent-space-id <AGENT_SPACE_ID> \
  --service-id <SERVICE_ID> \
  --configuration '{
    "mcpservernewrelic":  {
      "accountId": "<YOUR_ACCOUNT_ID>",
      "endpoint": "https://mcp.newrelic.com/mcp/"
    }
  }' \
  --region <REGION>
```

The response includes webhook information for integration. You can use this webhook to trigger an investigation from New Relic. For more information, see [Connecting New Relic](connecting-telemetry-sources-connecting-new-relic.md).

### 10. (Optional) Register and associate Datadog
<a name="10-optional-register-and-associate-datadog"></a>

You must first register Datadog through the AWS DevOps Agent console by using the OAuth flow before you can associate it through the CLI. For more information, see [Connecting DataDog](connecting-telemetry-sources-connecting-datadog.md).

List the registered services:

```
aws devops-agent list-services \
  --region <REGION>
```

Save the `<SERVICE_ID>` for serviceType: `mcpserverdatadog`.

Then associate Datadog:

```
aws devops-agent associate-service \
  --agent-space-id <AGENT_SPACE_ID> \
  --service-id <SERVICE_ID> \
  --configuration '{
    "mcpserverdatadog": {
      "name": "Datadog-MCP-Server",
      "endpoint": "<DATADOG_MCP_ENDPOINT>"
    }
  }' \
  --region <REGION>
```

The response includes webhook information for integration. You can use this webhook to trigger an investigation from Datadog. For more information, see [Connecting DataDog](connecting-telemetry-sources-connecting-datadog.md).

### 11. (Optional) Delete an agent space
<a name="11-optional-delete-an-agent-space"></a>

Deleting an agent space removes all associations, configurations, and investigation data for that agent space. This action can't be undone.

To delete an agent space, run the following command:

```
aws devops-agent delete-agent-space \
  --agent-space-id <AGENT_SPACE_ID> \
  --region <REGION>
```

## Verification
<a name="verification"></a>

To verify your setup, run the following commands:

```
# List your agent spaces
aws devops-agent list-agent-spaces \
  --region <REGION>

# Get details of a specific agent space
aws devops-agent get-agent-space \
  --agent-space-id <AGENT_SPACE_ID> \
  --region <REGION>

# List associations for an agent space
aws devops-agent list-associations \
  --agent-space-id <AGENT_SPACE_ID> \
  --region <REGION>
```

## Next steps
<a name="next-steps"></a>
+ To connect additional integrations, see [Configuring integrations and knowledge](configuring-integrations-and-knowledge.md).
+ To learn about agent skills and capabilities, see [DevOps Agent Skills](about-aws-devops-agent-devops-agent-skills.md).
+ To understand the operator web app, see [What is a DevOps Agent Web App?](about-aws-devops-agent-what-is-a-devops-agent-web-app.md).

## Notes
<a name="notes"></a>
+ Replace `<AGENT_SPACE_ID>`, `<MONITORING_ACCOUNT_ID>`, `<EXTERNAL_ACCOUNT_ID>`, `<REGION>`, and so on with your actual values.
+ For a list of supported Regions, see [Supported Regions](about-aws-devops-agent-supported-regions.md).