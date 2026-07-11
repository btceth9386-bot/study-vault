

# VPC Endpoints (AWS PrivateLink)
<a name="aws-devops-agent-security-vpc-endpoints-aws-privatelink"></a>

You can use AWS PrivateLink to create a private connection between your VPC and AWS DevOps Agent. You can access AWS DevOps Agent as if it were in your VPC, without the use of an internet gateway, NAT device, VPN connection, or Direct Connect connection. Instances in your VPC don't need public IP addresses to access AWS DevOps Agent.

You establish this private connection by creating an interface endpoint, powered by AWS PrivateLink. We create an endpoint network interface in each subnet that you enable for the interface endpoint. These are requester-managed network interfaces that serve as the entry point for traffic destined for AWS DevOps Agent.

For more information, see [Access AWS services through AWS PrivateLink](https://docs.aws.amazon.com/vpc/latest/privatelink/privatelink-access-aws-services.html) in the \_AWS PrivateLink Guide\_.

## Considerations for AWS DevOps Agent VPC endpoints
<a name="considerations-for-aws-devops-agent-vpc-endpoints"></a>

Before you set up an interface endpoint for AWS DevOps Agent, review [Considerations](https://docs.aws.amazon.com/vpc/latest/privatelink/create-interface-endpoint.html#considerations-interface-endpoints) in the \_AWS PrivateLink Guide\_.

AWS DevOps Agent supports making API calls through the following VPC endpoints.


| Category | Endpoint suffix | 
| --- | --- | 
| AWS DevOps Agent Control Plane API Actions | aidevops | 
| AWS DevOps Agent Runtime Operations | aidevops-dataplane | 
| AWS DevOps Agent Webhook Events | event-ai | 

## Create an interface endpoint for AWS DevOps Agent
<a name="create-an-interface-endpoint-for-aws-devops-agent"></a>

You can create an interface endpoint for AWS DevOps Agent using either the Amazon VPC console or the AWS Command Line Interface (AWS CLI). For more information, see [Create an interface endpoint](https://docs.aws.amazon.com/vpc/latest/privatelink/create-interface-endpoint.html) in the \_AWS PrivateLink Guide\_.

Create an interface endpoint for AWS DevOps Agent using the following service names:
+ com.amazonaws.{region}.aidevops
+ com.amazonaws.{region}.aidevops-dataplane
+ com.amazonaws.{region}.event-ai

After you create the endpoint, you have the option to enable a private DNS hostname. Enable this setting by selecting **Enable Private DNS Name** in the VPC console when you create the VPC endpoint.

If you enable private DNS for the interface endpoint, you can make API requests to AWS DevOps Agent using its default Regional DNS name. The following example shows the format of the default Regional DNS name.
+ cp.aidevops.{region}.api.aws
+ dp.aidevops.{region}.api.aws
+ event-ai.{region}.api.aws

## Create an endpoint policy for your interface endpoint
<a name="create-an-endpoint-policy-for-your-interface-endpoint"></a>

An endpoint policy is an IAM resource that you can attach to an interface endpoint. The default endpoint policy allows full access to AWS DevOps Agent through the interface endpoint. To control the access allowed to AWS DevOps Agent from your VPC, attach a custom endpoint policy to the interface endpoint.

An endpoint policy specifies the following information:
+ The principals that can perform actions (AWS accounts, IAM users, and IAM roles).
+ The actions that can be performed.
+ The resources on which the actions can be performed.

For more information, see [Control access to services using endpoint policies](https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints-access.html) in the \_AWS PrivateLink Guide\_.