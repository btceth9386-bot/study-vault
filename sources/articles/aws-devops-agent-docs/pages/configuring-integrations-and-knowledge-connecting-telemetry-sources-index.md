

# Connecting telemetry sources
<a name="configuring-integrations-and-knowledge-connecting-telemetry-sources-index"></a>

AWS DevOps Agent provides three ways to connect to your telemetry sources.

## Built-in, 2-way integration
<a name="built-in-2-way-integration"></a>

Currently, AWS DevOps Agent supports Dynatrace users with a built-in, 2-way integration enabling the following:
+ **Topology resource mapping** - AWS DevOps Agent will augment your DevOps Agent Space Topology with entities and relationships available to it via a AWS DevOps Agent-hosted Dynatrace MCP server.
+ **Automated Investigation triggering** - Dynatrace Workflows can be configured to trigger incident resolution Investigations from Dynatrace Problems.
+ **Telemetry introspection** - AWS DevOps Agent can introspect Dynatrace telemetry as it investigates an issue via the AWS DevOps Agent-hosted Dynatrace MCP server.
+ **Status updates** - AWS DevOps Agent will publish key investigation findings, root cause analyses, and generated mitigation plans to the Dynatrace user interface.

To learn about 2-way integrations, see
+ [Connecting Dynatrace](connecting-telemetry-sources-connecting-dynatrace.md)

## Built-in, 1-way integration
<a name="built-in-1-way-integration"></a>

Currently, AWS DevOps Agent supports AWS CloudWatch, Amazon S3, Datadog, Grafana, New Relic, and Splunk users with built-in, 1 way integrations.

**Security best practice:** When configuring credentials for built-in 1-way integrations, we recommend scoping API keys and tokens to read-only access. AWS DevOps Agent uses these credentials for telemetry introspection only and does not require write access to your telemetry provider.

The AWS CloudWatch built-in, 1-way integration requires no additional setup and enables the following:
+ **Topology resource mapping** - AWS DevOps Agent will augment your DevOps Agent Space Topology with entities and relationships available to it via your configured primary and secondary AWS cloud accounts.
+ **Telemetry introspection** - AWS DevOps Agent can introspect AWS CloudWatch telemetry as it investigates an issue via the IAM role(s) provided during primary and secondary AWS cloud account configuration.

The Amazon S3 built-in, 1-way integration enables the following:
+ **Telemetry introspection** - AWS DevOps Agent can read objects from Amazon S3 buckets as it investigates an issue. This is useful for accessing logs, configuration files, and other artifacts stored in S3.

To use the Amazon S3 integration, add the `s3:GetObject` and `s3:ListBucket` permissions to the DevOps Agent's IAM role. Following the principle of least privilege, scope these permissions to only the specific S3 buckets that the agent needs to access. For more information about configuring IAM permissions, see [DevOps Agent IAM permissions](aws-devops-agent-security-devops-agent-iam-permissions.md).

The Datadog, Grafana, New Relic, and Splunk built-in, 1-way integrations require setup and enable the following:
+ **Automated Investigation triggering** - Datadog, Grafana, New Relic, and Splunk events can be configured to trigger AWS DevOps Agent incident resolution Investigations via AWS DevOps Agent webhooks.
+ **Telemetry introspection** - AWS DevOps Agent can introspect Datadog, Grafana, New Relic, and Splunk telemetry as it investigates an issue via each provider's remote MCP server.

To learn about 1-way integrations, see the following:
+ [Connecting DataDog](connecting-telemetry-sources-connecting-datadog.md)
+ [Connecting Grafana](connecting-telemetry-sources-connecting-grafana.md)
+ [Connecting New Relic](connecting-telemetry-sources-connecting-new-relic.md)
+ [Connecting Splunk](connecting-telemetry-sources-connecting-splunk.md)

## Bring-your-own telemetry sources
<a name="bring-your-own-telemetry-sources"></a>

For any other telemetry source, including Prometheus metrics, you can use AWS DevOps Agent’s support for both webhook and MCP server integration.

To learn about bring-your-own integrations, see the following
+ [Invoking DevOps Agent through Webhook](configuring-integrations-and-knowledge-invoking-devops-agent-through-webhook.md)
+ [Connecting MCP Servers](configuring-integrations-and-knowledge-connecting-mcp-servers.md)