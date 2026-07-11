

# Limiting Agent Access in an AWS Account
<a name="aws-devops-agent-security-limiting-agent-access-in-an-aws-account"></a>

AWS DevOps Agent uses IAM roles to discover and describe AWS resources during incident investigations and preventative evaluations. You can control the level of access the agent has by configuring IAM policies attached to these roles. The application topology doesn't show everything the agent has access to—IAM policies are the only way to truly limit what AWS service APIs and resources the agent can access.

## Understanding IAM roles for AWS DevOps Agent
<a name="understanding-iam-roles-for-aws-devops-agent"></a>

AWS DevOps Agent uses IAM roles to access resources in two types of accounts:
+ **Primary account role** – Grants the agent access to resources in the AWS account where you create the Agent Space.
+ **Secondary account roles** – Grants the agent access to resources in additional AWS accounts that you connect to the Agent Space.

For either type of account, you can restrict which AWS services the agent can access, limit access to specific resources within those services, and control which regions the agent can operate in.

## Understanding permission guardrails
<a name="understanding-permission-guardrails"></a>

AWS DevOps Agent applies a permission guardrail to every session it creates when accessing your AWS resources. This guardrail acts as a ceiling — it defines the maximum set of permissions the agent can ever use, regardless of what permissions you grant on the IAM role.

### How it works
<a name="how-it-works"></a>

When the agent assumes your IAM role, it passes a [session policy](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html#policies_session) that limits the effective permissions for that session. The effective permissions are the intersection of:

1. **Your IAM role policies** — The managed policy and any inline policies you attach to the role.

1. **The permission guardrail** — A session policy applied by AWS DevOps Agent at assume-role time.

A permission must be present in both layers to take effect. If you add a permission to your role that is not included in the guardrail, the agent cannot use it.

### Default permissions
<a name="default-permissions"></a>

The `AIDevOpsAgentAccessPolicy` managed policy provides the default set of read-only permissions the agent uses for investigations. These permissions are included in the guardrail, so they work without additional configuration.

### Extending permissions beyond the default
<a name="extending-permissions-beyond-the-default"></a>

AWS DevOps Agent supports a curated set of additional permissions beyond the default managed policy. These permissions are included in the guardrail but are not enabled by default. To use them, add the specific permissions to your role as an inline policy.

For example, to allow the agent to read objects from your S3 buckets during investigations, add an inline policy to your role:

```
{
  "Version": "2012-10-17",		 	 	 		 	 	 
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-application-bucket",
        "arn:aws:s3:::my-application-bucket/*"
      ]
    }
  ]
}
```

Because `s3:GetObject` and `s3:ListBucket` are included in the guardrail, this inline policy takes effect. You can scope the `Resource` to specific buckets to follow the principle of least privilege.

### Supported additional permissions
<a name="supported-additional-permissions"></a>

The following permissions are included in the guardrail and can be enabled by adding them to your role as an inline policy. These are not granted by default — you must explicitly opt in.


| Service | Actions | Use case | 
| --- | --- | --- | 
| Amazon Athena | athena:GetQuery\*, athena:StartQueryExecution, athena:StopQueryExecution | Run Athena queries against your data catalog and retrieve managed query results | 
| Amazon CloudWatch Logs | logs:GetLogRecord | Retrieve individual log records when investigating application issues | 
| Amazon DynamoDB | dynamodb:Scan, dynamodb:Query, dynamodb:GetItem, dynamodb:BatchGetItem | Read items from your DynamoDB tables during investigations | 
| Amazon S3 | s3:GetObject, s3:ListBucket | Read application data, logs, or configuration stored in S3 | 
| AWS Glue | glue:GetPartition | Read partition metadata from the Glue Data Catalog for Athena queries | 
| AWS KMS | kms:Decrypt | Decrypt encrypted resources such as S3 objects | 
| AWS Support | support:DescribeCommunications | Read AWS Support case communications relevant to an investigation | 
| AWS Systems Manager | ssm:GetParameter | Read Systems Manager parameters used by your applications | 

**Note:** This list may expand over time as new capabilities are added to AWS DevOps Agent. Permissions not listed here or in the `AIDevOpsAgentAccessPolicy` managed policy are blocked by the guardrail.

### Permissions blocked by the guardrail
<a name="permissions-blocked-by-the-guardrail"></a>

If you add a permission to your role that is not in the guardrail, the agent cannot use it. This is by design — the guardrail prevents the agent from performing actions outside its intended scope, even if the role would otherwise allow them.

For example, write operations like `s3:PutObject`, `ec2:TerminateInstances`, or `dynamodb:DeleteItem` are not included in the guardrail. Even if your role grants these permissions, the agent cannot perform these actions.

### Summary
<a name="summary"></a>


| Layer | Who controls it | Purpose | 
| --- | --- | --- | 
| IAM role policies | You | Define what you intend the agent to be able to do | 
| Permission guardrail | AWS DevOps Agent | Defines the maximum the agent can ever do | 
| Effective permissions | Intersection of both | What the agent can actually do | 

This model ensures that the agent operates within a well-defined security boundary while giving you flexibility to extend its capabilities for your specific use case.

## Choosing your resource boundaries
<a name="choosing-your-resource-boundaries"></a>

When limiting resource access, you need to include enough permissions for the agent to successfully investigate application incidents. This includes:
+ All resources for in-scope applications that the agent should monitor and investigate
+ All supporting infrastructure that those applications depend on

Supporting infrastructure may include:
+ Networking components (VPCs, subnets, load balancers, API gateways)
+ Data stores (databases, caches, object storage)
+ Compute resources (EC2 instances, Lambda functions, containers)
+ Monitoring and logging services (CloudWatch, CloudTrail)
+ Identity and access management resources needed to understand permissions

If you restrict access too narrowly, the agent may not be able to identify root causes that originate in supporting infrastructure outside your defined boundaries.

## Restricting service access
<a name="restricting-service-access"></a>

You can limit which AWS services the agent can access by modifying the IAM policies attached to the agent's roles. When creating custom policies, follow these best practices:
+ **Grant only read-only permissions** – The agent needs to read resource configurations, metrics, and logs during investigations. Avoid granting permissions that allow the agent to modify or delete resources.
+ **Limit to necessary services** – Include only the AWS services that contain resources relevant to your applications. For example, if your application doesn't use Amazon RDS, don't include RDS permissions in the policy.
+ **Use specific actions instead of wildcards** – Instead of granting `service:*` permissions, specify individual actions like `cloudwatch:GetMetricData` or `ec2:DescribeInstances`.

Example policy restricting to specific services:

```
json

{
  "Version": "2012-10-17",		 	 	 		 	 	 
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:GetMetricData",
        "cloudwatch:GetMetricStatistics",
        "cloudwatch:DescribeAlarms",
        "logs:GetLogEvents",
        "logs:FilterLogEvents",
        "ec2:DescribeInstances",
        "lambda:GetFunction",
        "lambda:GetFunctionConfiguration"
      ],
      "Resource": "*"
    }
  ]
}
```

## Restricting resource access
<a name="restricting-resource-access"></a>

To limit the agent to specific resources within a service, use resource-level permissions in your IAM policies. This allows you to grant access only to resources that match specific patterns.

**Using resource ARN patterns:**

```
{
  "Version": "2012-10-17",		 	 	 		 	 	 
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:GetFunction",
        "lambda:GetFunctionConfiguration"
      ],
      "Resource": "arn:aws:lambda:*:*:function:production-*"
    }
  ]
}
```

This example limits the agent to accessing only Lambda functions with names that begin with "production-".

**Using tag-based restrictions:**

```
{
  "Version": "2012-10-17",		 	 	 		 	 	 
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeInstanceStatus"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:ResourceTag/Environment": "production"
        }
      }
    }
  ]
}
```

This example limits the agent to accessing only EC2 instances tagged with `Environment=production`.

## Restricting regional access
<a name="restricting-regional-access"></a>

To limit which AWS regions the agent can access, use the `aws:RequestedRegion` condition key in your IAM policies:

```
{
  "Version": "2012-10-17",		 	 	 		 	 	 
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "lambda:Get*",
        "cloudwatch:Get*"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": [
            "us-east-1",
            "us-west-2"
          ]
        }
      }
    }
  ]
}
```

This example limits the agent to accessing resources only in the us-east-1 and us-west-2 regions.

## Creating custom IAM policies
<a name="creating-custom-iam-policies"></a>

When you create an Agent Space or add secondary accounts, you have the option to create a custom IAM role using a policy template. This allows you to implement the principle of least privilege.

**When creating an Agent Space**

From the DevOps Agent console in the AWS Management Console...
+ Choose **Create a new DevOps Agent role using a policy document** and follow the instructions

**When editing an Agent Space**

From the DevOps Agent console in the AWS Management Console...
+ Select the **Capabilities** tab
+ Select the secondary account you want to edit from the **Cloud** section and choose Edit
+ Chose **Create a new DevOps Agent policy using a template** and follow the instructions

## Custom policy best practices
<a name="custom-policy-best-practices"></a>
+ **Grant only read-only permissions** – Avoid permissions that allow resource modification or deletion
+ **Use resource-level permissions when possible** – Restrict access to specific resources using ARN patterns or tags
+ **Regularly review and audit permissions** – Periodically review the agent's IAM policies to ensure they still align with your security requirements