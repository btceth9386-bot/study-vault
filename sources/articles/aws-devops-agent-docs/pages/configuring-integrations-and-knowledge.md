

# Configuring integrations and knowledge
<a name="configuring-integrations-and-knowledge"></a>

AWS DevOps Agent capabilities extend your agent's functionality by connecting it to your existing tools and infrastructure. Configure these capabilities to enable comprehensive incident investigation, automated response workflows, and seamless integration with your DevOps ecosystem.

The following capabilities help you maximize your DevOps Agent's effectiveness:
+ **AWS EKS Access Setup** - Enable introspection of Kubernetes clusters, pod logs, and cluster events for both public and private EKS environments
+ **Azure Integration** - Connect Azure subscriptions and Azure DevOps organizations to investigate Azure resources and correlate Azure DevOps deployments with incidents
+ **CI/CD Pipeline Integration** - Connect GitHub and GitLab pipelines to correlate deployments with incidents and track code changes during investigations
+ **MCP Server Connections** - Extend investigation capabilities by connecting external observability tools and custom monitoring systems through Model Context Protocol
+ **Multi-Account AWS Access** - Configure secondary AWS accounts to investigate resources across your entire organization during incident response
+ **Telemetry Source Integration** - Connect monitoring platforms like Datadog, Dynatrace, Grafana, New Relic, and Splunk for comprehensive observability data access
+ **Ticketing and Chat Integration** - Connect ServiceNow, PagerDuty, and Slack to automate incident response workflows and enable team collaboration
+ **Webhook Configuration** - Allow external systems to automatically trigger DevOps Agent investigations through HTTP requests. For details on webhook setup, authentication methods, and request format, see [Invoking DevOps Agent through Webhook](configuring-integrations-and-knowledge-invoking-devops-agent-through-webhook.md).
+ **Amazon EventBridge Integration** - Incorporate AWS DevOps Agent into event-driven applications by routing investigation and mitigation lifecycle events to Amazon EventBridge targets

You can configure each capability independently based on your team's specific needs and existing tool stack. Start with the integrations most critical to your incident response workflow, then expand to additional capabilities as needed.