

# Production operations
<a name="working-with-devops-agent-production-operations-index"></a>

Production operations is the set of capabilities that help you detect, respond to, and prevent incidents once your code is running in production. AWS DevOps Agent works alongside your operations team across the full incident lifecycle — from detection through investigation, recovery, and prevention.

## How production operations works
<a name="how-production-operations-works"></a>

AWS DevOps Agent monitors your production environment by integrating with your observability platforms — Amazon CloudWatch, Datadog, Dynatrace, Grafana, New Relic, and Splunk — along with ticketing systems like ServiceNow and PagerDuty, and communication tools like Slack. When an alert fires or a support ticket arrives, the agent begins investigating immediately.

The agent uses your application topology — an automatically generated map of your resources and their relationships — to correlate signals across services during an investigation. It traces metrics, logs, traces, code changes, and deployment history through the dependency graph to identify root cause, assess blast radius, and determine which downstream services may be affected.

Between incidents, the agent analyzes patterns across your investigation history to identify systemic improvements. It generates targeted recommendations across observability, infrastructure, governance, and code optimization that address root causes rather than symptoms.

For more information about how the agent discovers your infrastructure, see [What is a DevOps Agent Topology?](about-aws-devops-agent-what-is-a-devops-agent-topology.md). For details on connecting your monitoring tools, see [Connecting telemetry sources](configuring-integrations-and-knowledge-connecting-telemetry-sources-index.md).

## Getting started with production operations
<a name="getting-started-with-production-operations"></a>

To begin using production operations capabilities:

1. **Create an Agent Space** — An Agent Space is the logical container that defines what AWS DevOps Agent can access and investigate. Configure your primary AWS account and set up operator access for your team. See [Creating an Agent Space](getting-started-with-aws-devops-agent-creating-an-agent-space.md).

1. **Connect your telemetry sources** — Connect your monitoring platforms so the agent can access metrics, logs, and traces during investigations. AWS DevOps Agent supports built-in integrations with Amazon CloudWatch, Datadog, Dynatrace, Grafana, New Relic, and Splunk, plus webhook and MCP server integrations for other tools. See [Connecting telemetry sources](configuring-integrations-and-knowledge-connecting-telemetry-sources-index.md).

1. **Connect ticketing and communication tools (optional)** — Connect ServiceNow, PagerDuty, or Slack to enable automated investigation triggering from incidents and real-time status updates back to your team. See [Connecting to ticketing and chat](configuring-integrations-and-knowledge-connecting-to-ticketing-and-chat-index.md).

1. **Wait for topology discovery** — After connecting your accounts, the agent automatically discovers your resources and builds an application topology. This typically completes within minutes and provides the context the agent uses to correlate signals during investigations.

1. **Start your first investigation** — Investigations can start automatically from connected alerting sources, via webhooks, or manually from the Incident Response tab in the DevOps Agent web app. Try starting a manual investigation by describing an issue or choosing a pre-configured starting point such as "Latest alarm" or "Error rate spike." See [Autonomous incident response](production-operations-autonomous-incident-response.md).

Once your first investigation completes, you can provide feedback on the root cause analysis, review the investigation timeline, and explore proactive recommendations on the Improvements page.

## Production operations capabilities
<a name="production-operations-capabilities"></a>

Production operations includes three core capabilities:
+ **Autonomous incident response** — The agent automatically investigates issues the moment they occur, analyzing metrics, logs, traces, code changes, and deployment history to determine root cause and propose mitigation. See [Autonomous incident response](production-operations-autonomous-incident-response.md).
+ **Proactive incident prevention** — The agent analyzes patterns across your incident history to generate recommendations that prevent future incidents and reduce mean time to detection. See [Proactive incident prevention](production-operations-proactive-incident-prevention.md).
+ **On-demand DevOps tasks** — A conversational interface for querying your infrastructure, analyzing system health, and guiding investigations using natural language. See [On Demand DevOps Tasks](working-with-devops-agent-on-demand-devops-tasks.md).

## How production operations feeds back into release readiness
<a name="how-production-operations-feeds-back-into-release-readiness"></a>

Production operations and release management form a continuous feedback loop. Insights from production incidents inform pre-production validation, making your release process smarter over time.

**Incident patterns shape release reviews** — When the agent identifies recurring root causes through proactive incident prevention — such as missing error handling, inadequate retry logic, or over-permissioned IAM policies — these patterns inform what release readiness code reviews look for. The agent's growing understanding of what causes production failures in your environment makes future code reviews more relevant to your actual risk profile.

**Prevention recommendations drive code changes** — Proactive incident prevention generates agent-ready specifications that describe code and configuration improvements with specific file paths and implementation plans. These specifications can be handed to a coding agent during the release management workflow, closing the loop from production issue to validated fix.

**Topology knowledge improves dependency analysis** — The application topology built during production operations — including service relationships, request paths, and deployment boundaries — feeds directly into the cross-repository dependency analysis performed during release readiness reviews. The agent uses the same understanding of how your services interact to assess blast radius both during incident response and during code review.

**Investigation feedback refines learned skills** — Feedback you provide on investigations and the accuracy of recommendations updates the agent's learned skills. As these skills improve, both incident investigations and release reviews benefit from more accurate knowledge about your environment, operational patterns, and effective investigation techniques.