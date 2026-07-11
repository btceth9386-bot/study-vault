

# Connecting to privately hosted tools
<a name="configuring-integrations-and-knowledge-connecting-to-privately-hosted-tools"></a>

## Private connections overview
<a name="private-connections-overview"></a>

AWS DevOps Agent can be extended with custom Model Context Protocol (MCP) tools and other integrations that give the agent access to internal systems such as private package registries, self-hosted observability platforms, internal documentation APIs, and source control instances (see: [Configuring integrations and knowledge](configuring-integrations-and-knowledge.md)). These services often run inside an [Amazon Virtual Private Cloud (Amazon VPC)](https://docs.aws.amazon.com/vpc/latest/userguide) with restricted or no public internet access, which means AWS DevOps Agent can't reach them by default.

Private connections for AWS DevOps Agent let you securely connect your Agent Space to services running in your VPC without exposing them to the public internet. Private connections work with any integration that needs to reach a private endpoint, including MCP servers, self-hosted Grafana or Splunk instances, and source control systems like GitHub Enterprise Server and GitLab Self-Managed.

**Note**  
** If your privately hosted tools make outbound requests to the AWS DevOps Agent from within your VPC, this traffic can also be secured by using a VPC Endpoint so it stays within the AWS network. For example, this can be used with tools that trigger the DevOps Agent via webhook events (see: [Invoking DevOps Agent through Webhook](configuring-integrations-and-knowledge-invoking-devops-agent-through-webhook.md)). For more information, see [VPC Endpoints (AWS PrivateLink)](aws-devops-agent-security-vpc-endpoints-aws-privatelink.md).

### How private connections work
<a name="how-private-connections-work"></a>

A private connection creates a secure network path between AWS DevOps Agent and a target resource in your VPC. Under the hood, AWS DevOps Agent uses Amazon [VPC Lattice](https://docs.aws.amazon.com/vpc-lattice/latest/ug/) to establish this secure private connectivity path. VPC Lattice is an application networking service that lets you connect, secure, and monitor communication between applications across VPCs, accounts, and compute types, without managing the underlying network infrastructure.

When you create a private connection, the following occurs:
+ You provide the VPC, subnets, and (optionally) security groups that have network connectivity to your target service.
+ AWS DevOps Agent creates a service-managed [resource gateway](https://docs.aws.amazon.com/vpc/latest/privatelink/resource-gateway.html) and provisions its elastic network interfaces (ENIs) in the subnets you specified.
+ The agent uses the resource gateway to route traffic to your target service's IP address or DNS name over the private network path.

The resource gateway is fully managed by AWS DevOps Agent and appears as a read-only resource in your account (named `aidevops-{your-private-connection-name}`). You don't need to configure or maintain it. The only resources created in your VPC are ENIs in the subnets you specify. These ENIs serve as the entry point for private traffic and are managed entirely by the service. They don't accept inbound connections from the internet, and you retain full control over their traffic through your own security groups.

### Security
<a name="security"></a>

Private connections are designed with multiple layers of security:
+ **No public internet exposure** – All traffic between AWS DevOps Agent and your target service stays on the AWS network. Your service never needs a public IP address or internet gateway.
+ **Service-controlled resource gateway** – The service-managed resource gateway is read-only in your account. It can only be used by AWS DevOps Agent, and no other service or principal can route traffic through it. You can verify this in [AWS CloudTrail](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/) logs, which record all VPC Lattice API calls.
+ **Your security groups, your rules** – You control inbound and outbound traffic to the ENIs through security groups that you own and manage. If you don't specify security groups, AWS DevOps Agent creates a default security group scoped to the ports you define.
+ **Service-linked roles with least privilege** – AWS DevOps Agent uses a [service-linked role](https://docs.aws.amazon.com/IAM/latest/UserGuide/using-service-linked-roles.html) to create only the necessary VPC Lattice and Amazon EC2 resources. This role is scoped to resources tagged with `AWSAIDevOpsManaged` and cannot access any other resources in your account.

**Note**  
** If your organization has [service control policies (SCPs)](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html) that restrict VPC Lattice API actions, the service-managed resource gateway is created through a service-linked role. Ensure your SCPs permit the necessary actions for the service-linked role.

### Architecture
<a name="architecture"></a>

The following diagram shows the network path for a private connection.

![Network architecture showing AWS DevOps Agent connecting through VPC Lattice.](http://docs.aws.amazon.com/devopsagent/latest/userguide/images/7cd6182e6b8d.png)


In this architecture:
+ AWS DevOps Agent initiates a request to your target service.
+ Amazon VPC Lattice routes the request through the service-managed resource gateway in your VPC. For advanced setups using your own VPC Lattice resources, see [Advanced setup using existing VPC Lattice resources](#advanced-setup-using-existing-vpc-lattice-resources).
+ An ENI in your VPC receives the traffic and forwards it to your target service's IP address or DNS name.
+ Your security groups govern which traffic is allowed through the ENIs.
+ From your target service's perspective, the request originates from private IP addresses of ENIs within your VPC.

## Configuring firewall rules for private connections
<a name="configuring-firewall-rules-for-private-connections"></a>

With private connections, traffic from AWS DevOps Agent to your privately-hosted tool originates from the Resource Gateway ENIs in the subnets you specified during private connection creation. This is different from publicly-hosted tool connections, which use the static IP addresses listed on the [Security](aws-devops-agent-security.md) page.

**Important**  
** The static IP addresses published on the [Security](aws-devops-agent-security.md) page do ** not ** apply to private connections. Do not use those IPs in your firewall rules for privately-hosted tools.

To allow AWS DevOps Agent traffic to reach your privately-hosted tool:

1. Identify the subnets you specified when creating the private connection.

1. In your target tool's security group (for example, the security group on your Grafana ALB), add an inbound rule using one of the following approaches:
   + **Security group referencing (recommended)** – Allow inbound traffic from the security group attached to the private connection ENIs. If you specified a security group during private connection creation, use that security group ID as the source. For example: allow TCP 443 from `sg-0123456789abcdef0`.
   + **Subnet CIDR allowlisting** – Allow inbound traffic from the CIDR blocks of the subnets you specified during private connection creation. For example, if your subnet CIDR is `10.0.1.0/24`: allow TCP 443 from `10.0.1.0/24`.

To find your subnet CIDR blocks, run the following command with the subnet IDs you specified during private connection creation:

```
aws ec2 describe-subnets \
    --subnet-ids subnet-0123456789abcdef0 subnet-0123456789abcdef1 \
    --query 'Subnets[*].[SubnetId,CidrBlock]' \
    --output table
```

**Note**  
** The ENI IP addresses remain stable for the lifetime of your private connection. If you delete and recreate a private connection, the ENI IP addresses may change. Using subnet CIDR blocks or security group referencing avoids needing to update rules after recreation.

## Create a private connection
<a name="create-a-private-connection"></a>

You can create a private connection using the AWS Management Console or the AWS CLI.

**Note**  
** The following Availability Zones aren't supported by VPC Lattice: `use1-az3`, `usw1-az2`, `apne1-az3`, `apne2-az2`, `euc1-az2`, `euw1-az4`, `cac1-az3`, `ilc1-az2`.

### Prerequisites
<a name="prerequisites"></a>

Before creating a private connection, verify that you have the following:
+ **An active Agent Space** – You need an existing Agent Space in your account. If you don't have one, see [Getting started with AWS DevOps Agent](getting-started-with-aws-devops-agent.md).
+ **A privately reachable target service** – Your MCP server, observability platform, or other service must be reachable at a known private IP address or DNS name from the VPC where the resource gateway is deployed. The service can run in the same VPC, a peered VPC, or on-premises, as long as it's routable from the resource gateway subnets. The service must serve HTTPS traffic with a minimum TLS version of 1.2 on a port that you specify when creating the connection.
+ **Subnets in your VPC** – Identify 1–20 subnets where the ENIs will be created. We recommend selecting subnets in multiple Availability Zones for high availability. These subnets must have network connectivity to your target service. One subnet per Availability Zone can be used by VPC Lattice.
+ **(Optional) Security groups** – If you want to control traffic with specific rules, prepare up to five security group IDs to attach to the ENIs. If you omit security groups, AWS DevOps Agent creates a default security group.

Private connections are account-level resources. After you create a private connection, you can reuse it across multiple integrations and Agent Spaces that need to reach the same host.

### Create a private connection using the console
<a name="create-a-private-connection-using-the-console"></a>

1. Open the AWS DevOps Agent console.

1. In the navigation pane, choose **Capability providers**, then choose **Private connections**.

1. Choose **Create a new connection**.

1. For **Name**, enter a descriptive name for the connection, such as `my-mcp-tool-connection`.

1. For **VPC**, select the VPC where the resource gateway ENIs will be deployed.

1. For **Subnets**, select one or more subnets (up to 20). We recommend choosing subnets in at least two Availability Zones.

1. For **IP address type**, select the type of IP address of your target service (`IPv4`, `IPv6`, or `DualStack`).

1. (Optional) For **Number of IPv4 addresses**, if you selected IPv4 or Dualstack for the IP address type, you can enter the number of IPv4 addresses per ENI for your resource gateway. The default is 16 IPv4 addresses per ENI.

1. (Optional) For **Security groups**, select existing security groups (up to 5) to restrict what traffic is allowed to reach your target service. If you don't select any, a default security group is created.

1. (Optional) For **Port ranges**, specify the TCP ports your target application listens on (for example, `443` or `8080-8090`). You can specify up to 11 port ranges.

1. For **Host address**, enter the IP address or DNS name of your target service (for example, `mcp.internal.example.com` or `10.0.1.50`). The service must be reachable from the selected VPC. If you enter a DNS name, how it is resolved depends on the **DNS resolution** mode you choose in the next step.

1. For **DNS resolution**, choose how the host address DNS name is resolved:
   + **Public** (default) – The DNS name is resolved using public DNS. If you enter a DNS name as the host address, it must be publicly resolvable. Use this mode when your hostname has a public DNS record (which can point to a private IP address). If you specify an IP address as the host address, this setting has no effect.
   + **In VPC** – The DNS name is resolved from within your VPC context, so hostnames that exist only in a [private hosted zone](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/hosted-zones-private.html) resolve correctly without any public DNS record. Use this mode when your target service's hostname is private to your VPC.

1. (Optional) Complete this step if a private certificate authority (CA) issued the TLS certificates for your host address. For **Certificate public key**, enter the **full PEM-encoded certificate chain** for the target service. List the certificates in order: the leaf (server) certificate first, then all intermediate CA certificates, then the root CA certificate. If the chain is incomplete, the connection fails. AWS DevOps Agent then verifies and trusts the TLS connection.

1. Choose **Create connection**.

The connection status changes to **Create in progress**. This process can take up to 10 minutes. When the status changes to **Active**, the network path is ready.

If the status changes to **Create failed**, verify the following:
+ The subnets you specified have available IP addresses.
+ Your account has not reached VPC Lattice service quotas.
+ No restrictive IAM policies are preventing the service-linked role from creating resources.

**Note**  
** These steps can also be performed by selecting `Create a new private connection` during the registration of a capability provider. For more information, see [Use a private connection with a capability provider](#use-a-private-connection-with-a-capability-provider).

### Create a private connection using the AWS CLI
<a name="create-a-private-connection-using-the-aws-cli"></a>

Run the following command to create a private connection. Replace the placeholder values with your own.

```
aws devops-agent create-private-connection \
    --name my-mcp-tool-connection \
    --mode '{
        "serviceManaged": {
            "hostAddress": "mcp.internal.example.com",
            "vpcId": "vpc-0123456789abcdef0",
            "subnetIds": [
                "subnet-0123456789abcdef0",
                "subnet-0123456789abcdef1"
            ],
            "securityGroupIds": [
                "sg-0123456789abcdef0"
            ],
            "portRanges": ["443"],
            "dnsResolution": "PUBLIC"
        }
    }'
```

The `dnsResolution` field controls how the `hostAddress` DNS name is resolved. Valid values are `PUBLIC` (the default when omitted) and `IN_VPC`. Use `IN_VPC` when your host address only resolves inside your VPC (for example, a name in a private hosted zone). If you specify an IP address for `hostAddress`, this field has no effect.

The response includes the connection name and a status of `CREATE_IN_PROGRESS`:

```
{
    "name": "my-mcp-tool-connection",
    "status": "CREATE_IN_PROGRESS",
    "resourceGatewayId": "rgw-0123456789abcdef0",
    "hostAddress": "mcp.internal.example.com",
    "vpcId": "vpc-0123456789abcdef0"
}
```

To check the connection status, use the `describe-private-connection` command:

```
aws devops-agent describe-private-connection \
    --name my-mcp-tool-connection
```

When the status is `ACTIVE`, your private connection is ready to use.

## Use a private connection with a capability provider
<a name="use-a-private-connection-with-a-capability-provider"></a>

To use a private connection, you can link to it during the registration of a capability provider. Supported capabilities that can be used with private connections include: `GitHub`, `GitLab`, `MCP Server`, and `Grafana`. You can perform this step using the AWS Management Console or the AWS CLI.

**Note**  
** When registering a capability provider, AWS DevOps Agent validates that the endpoint is reachable and responding. Ensure your target service is running and accepting connections before completing registration.

### Use a private connection with a capability provider using the console
<a name="use-a-private-connection-with-a-capability-provider-using-the-console"></a>

In the AWS DevOps Agent console, private connections can be linked to a capability during registration by selecting the "Connect to endpoint using a private connection" option.

![Connect to endpoint using a private connection checkbox selected.](http://docs.aws.amazon.com/devopsagent/latest/userguide/images/a2a7ffb70ffe.png)


1. Open the AWS DevOps Agent console and navigate to your Agent Space.

1. In the **Capability Providers** section, choose **Registration**.

1. Select **Register** for the capability type you want to use with the private connection.

1. On the registration details view, enter the Endpoint URL you want to connect to using the private connection (for example, `https://mcp.internal.example.com`).

1. Select **Connect to endpoint using a private connection**.

1. Either select an existing private connection that corresponds to the Endpoint URL you want to connect to, or select **Create a new private connection** to create one.

1. Complete the registration process for the capability provider.

**Note**  
** When you select a private connection for a capability provider that uses OAuth authentication (Client Credentials or 3LO), the private connection applies to both the capability provider endpoint and the token exchange endpoint. Ensure the private connection is configured with a host address that can route traffic to both endpoints.

#### Routing the endpoint and the OAuth token exchange through different private connections
<a name="routing-the-endpoint-and-the-oauth-token-exchange-through-different-private-connections"></a>

For OAuth-based MCP server capability providers, the agent makes requests to two different endpoints: the **target URL** (the MCP server endpoint you register) and the **exchange URL** (the OAuth token exchange endpoint). By default, a single `privateConnectionName` is used for both. If these two endpoints are reachable through different private network paths, you can route each one through its own private connection by using `targetUrlPrivateConnectionName` and `exchangeUrlPrivateConnectionName` instead:
+ `targetUrlPrivateConnectionName` – the private connection used to reach the MCP server endpoint (target URL).
+ `exchangeUrlPrivateConnectionName` – the private connection used to reach the OAuth token exchange endpoint (exchange URL).

You can specify either or both. If you set only one, the other endpoint is reached over the public internet (it does not fall back to the other private connection).

**Important**  
** `targetUrlPrivateConnectionName` and `exchangeUrlPrivateConnectionName` cannot be combined with `privateConnectionName` in the same request. Use either the single `privateConnectionName` (applies to both endpoints) or the per-endpoint names — not both.

The following example registers an OAuth Client Credentials MCP Server that reaches its endpoint and its token exchange endpoint through two separate private connections:

```
aws devops-agent register-service \
    --service mcpserver \
    --target-url-private-connection-name my-target-connection \
    --exchange-url-private-connection-name my-exchange-connection \
    --service-details '{
        "mcpserver": {
            "name": "my-mcp-tool",
            "endpoint": "https://mcp.internal.example.com",
            "authorizationConfig": {
                "oAuthClientCredentials": {
                    "clientName": "MyOAuthClient",
                    "clientId": "client-id",
                    "clientSecret": "secret-value",
                    "exchangeUrl": "https://auth.internal.example.com/token"
                }
            }
        }
    }' \
    --region us-east-1
```

### Use a private connection with a capability provider using the AWS CLI
<a name="use-a-private-connection-with-a-capability-provider-using-the-aws-cli"></a>

You can register capabilities with a private connection by including the `private-connection-name` argument. Below is an example of registering an MCP Server with API Key authorization using the `my-mcp-tool-connection` private connection. Replace the placeholder values with your own.

```
aws devops-agent register-service \
    --service mcpserver \
    --private-connection-name my-mcp-tool-connection \
    --service-details '{
        "mcpserver": {
            "name": "my-mcp-tool",
            "endpoint": "https://mcp.internal.example.com",
            "authorizationConfig": {
                "apiKey": {
                    "apiKeyName": "api-key",
                    "apiKeyValue": "secret-value",
                    "apiKeyHeader": "x-api-key"
                }
            }
        }
    }' \
    --region us-east-1
```

## Verify a private connection
<a name="verify-a-private-connection"></a>

After the private connection reaches the **Active** state and has been utilized by a capability provider, verify that AWS DevOps Agent can reach your target service:

1. Open the AWS DevOps Agent console and navigate to your Agent Space.

1. Start a new chat session.

1. Invoke a command that uses the integration backed by your private connection. For example, if your MCP tool provides access to an internal knowledge base, ask the agent a question that requires that knowledge base.

1. Confirm that the agent returns results from the private service.

If the connection fails, check the following:
+ **VPC Lattice limits** - Verify that you have not reached any resource gateway or other [VPC Lattice quota](https://docs.aws.amazon.com/vpc-lattice/latest/ug/quotas.html) limits
+ **Security group rules** – Verify that the security groups attached to the ENIs allow outbound traffic on the port your service listens on. Also verify that your service's security group allows inbound traffic on the target port. Traffic arrives from VPC Lattice data plane IPs within your VPC CIDR range. You can use security group referencing (allowing the ENI security group as a source) or allow inbound from the VPC CIDR.
+ **Subnet connectivity** – Verify that the subnets you selected can route traffic to your service. If the service runs in a different subnet, confirm that the route tables allow traffic between them.
+ **Service availability** – Confirm that your service is running and accepting connections on the expected port.
+ **Unsupported Availability Zone** - Verify your subnets are in supported Availability Zones. Run `aws ec2 describe-subnets --subnet-ids <your-subnet-ids> --query 'Subnets[*].[SubnetId,AvailabilityZoneId]'` and check against the unsupported Availability Zones listed above.

## Delete a private connection
<a name="delete-a-private-connection"></a>

You can delete unused private connections using the AWS Management Console or the AWS CLI.

### Delete a private connection using the console
<a name="delete-a-private-connection-using-the-console"></a>

1. Open the AWS DevOps Agent console.

1. In the navigation pane, choose **Capability providers**, then choose **Private connections**.

1. Select the **Actions** menu for the private connection you want to delete, and select **Remove**.

The private connection will be displayed with a status of "Removing connection" while AWS DevOps Agent removes the managed resource gateway and ENIs from your VPC. After deletion completes, the connection no longer appears in your list of private connections.

### Delete a private connection using the AWS CLI
<a name="delete-a-private-connection-using-the-aws-cli"></a>

```
aws devops-agent delete-private-connection \
    --name my-mcp-tool-connection
```

The response returns a status of `DELETE_IN_PROGRESS`. AWS DevOps Agent removes the managed resource gateway and ENIs from your VPC. After deletion completes, the connection no longer appears in your list of private connections.

## Advanced setup using existing VPC Lattice resources
<a name="advanced-setup-using-existing-vpc-lattice-resources"></a>

If your organization already uses Amazon VPC Lattice and manages your own resource configurations, you can create a private connection in self-managed mode. Instead of having AWS DevOps Agent create a resource gateway for you, you provide the Amazon Resource Name (ARN) of an existing resource configuration that points to your target service.

This approach is useful when you:
+ Want full control over the resource gateway and resource configuration lifecycle.
+ Need to share resource configurations across multiple AWS accounts or services.
+ Require VPC Lattice access logs for detailed traffic monitoring.
+ Run a hub-and-spoke network architecture.

To create a self-managed private connection with the AWS CLI:

```
aws devops-agent create-private-connection \
    --name my-advanced-connection \
    --mode '{
        "selfManaged": {
            "resourceConfigurationId": "arn:aws:vpc-lattice:us-east-1:123456789012:resourceconfiguration/rcfg-0123456789abcdef0"
        }
    }'
```

For more details on setting up VPC Lattice resource gateways and resource configurations, see the [Amazon VPC Lattice User Guide](https://docs.aws.amazon.com/vpc-lattice/latest/ug/).

### Cross-region connectivity
<a name="cross-region-connectivity"></a>

Private connections must be created in the same AWS Region as your Agent Space. If your target service runs in a different Region, use self-managed mode with inter-region VPC peering or Transit Gateway peering to bridge the gap.

The pattern is:

1. Establish inter-region connectivity (VPC peering or Transit Gateway peering) between a VPC in the Agent Space's Region and the service's VPC. VPC CIDRs must not overlap.

1. Create a resource gateway in the Agent Space's Region, in a VPC with the peering connection.

1. Create a resource configuration in the Agent Space's Region pointing to the service's IP address (routable via the peering connection).

1. Create a self-managed private connection using that resource configuration ARN.

For example, if your agent space is in `us-east-1` and your MCP server is in `ap-southeast-2`:

```
aws devops-agent create-private-connection \
    --name cross-region-connection \
    --mode '{
        "selfManaged": {
            "resourceConfigurationId": "arn:aws:vpc-lattice:us-east-1:123456789012:resourceconfiguration/rcfg-0123456789abcdef0"
        }
    }' \
    --region us-east-1
```

## Related topics
<a name="related-topics"></a>
+ [VPC Endpoints (AWS PrivateLink)](aws-devops-agent-security-vpc-endpoints-aws-privatelink.md)
+ [Connecting MCP Servers](configuring-integrations-and-knowledge-connecting-mcp-servers.md)
+ [Configuring integrations and knowledge](configuring-integrations-and-knowledge.md)
+ [AWS DevOps Agent Security](aws-devops-agent-security.md)
+ [DevOps Agent IAM permissions](aws-devops-agent-security-devops-agent-iam-permissions.md)