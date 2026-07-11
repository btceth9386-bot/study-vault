

# Custom Agents
<a name="working-with-devops-agent-custom-agents-index"></a>

Custom agents are user-defined AI agents that automate operational tasks specific to your infrastructure and workflows. Unlike the built-in AWS DevOps Agent capabilities — which focus on incident response, on-demand queries, and proactive prevention — custom agents let you define your own agent with a tailored system prompt, a curated set of tools, and specialized skills.

Custom agents execute autonomously, using the MCP tools and skills available in your Agent Space. You can run them on demand or on a schedule to perform recurring operational work such as generating reports, auditing configurations, analyzing trends, or executing multi-step workflows across your connected tools.

## Key concepts
<a name="key-concepts"></a>

**System prompt** – A set of instructions written in Markdown that defines what the agent does, how it approaches tasks, and what output it produces. The system prompt is the core of your custom agent's behavior.

**Tools** – MCP tools available in your Agent Space that the custom agent can invoke during invocation. You select which tools the agent has access to from the full set of tools provided by your connected integrations and custom MCP servers.

**Skills** – Modular instruction sets that provide additional domain knowledge, investigation procedures, or specialized capabilities to the agent at runtime. Skills can also enable output capabilities such as creating artifacts or recommendations. For more information about skills, see [DevOps Agent Skills](about-aws-devops-agent-devops-agent-skills.md).

**Triggers** – Events or conditions that automatically invoke a custom agent. AWS DevOps Agent currently supports schedule-based triggers, which execute the agent at defined intervals using cron or rate expressions.

**Invocation** – A single run of a custom agent. Each invocation produces a trajectory showing the agent's reasoning steps, tool calls, and outputs.

## How custom agents work
<a name="how-custom-agents-work"></a>

When a custom agent executes, it:

1. Loads its system prompt, tools, and skills from the configuration you defined.

1. Connects to the Agent Space MCP toolbox and accesses only the tools you assigned to it.

1. Loads its assigned skill documents, making their instructions and domain knowledge available during invocation.

1. Reasons through the task, calling tools and following skill instructions to accomplish its objective.

1. Produces outputs — text responses, artifacts, or recommendations — based on its instructions and assigned skills.

1. Records a complete invocation trajectory, including all reasoning steps, tool calls, and results.

Custom agents have access to the same tools that power the built-in AWS DevOps Agent capabilities — including tools for your connected AWS accounts, observability platforms, CI/CD pipelines, ticketing systems, and custom MCP servers — but only the specific tools you assign to each agent.

## Custom agents compared to built-in capabilities
<a name="custom-agents-compared-to-built-in-capabilities"></a>


| Capability | Built-in Agent | Custom Agent | 
| --- | --- | --- | 
| Purpose | Incident response, prevention, on-demand queries | User-defined operational tasks | 
| Configuration | Managed by AWS DevOps Agent | You define the prompt, tools, and skills | 
| Invocation | Automatic (incidents, schedules) or conversational | On demand or through triggers you configure | 
| Tools available | All tools in the Agent Space | Only the tools you select | 
| Outputs | Investigations, recommendations, chat responses | Text responses, artifacts, recommendations | 
| Concurrency | Subject to built-in concurrency quotas | Subject to custom agent concurrency quota | 

## What custom agents can do
<a name="what-custom-agents-can-do"></a>

Custom agents are flexible and can automate a wide range of operational tasks. Common use cases include:
+ **Operational reporting** – Generate daily or weekly health summaries, deployment reports, or compliance audits across your infrastructure.
+ **Configuration auditing** – Periodically check resource configurations against your organization's standards and produce findings.
+ **Trend analysis** – Analyze metrics, error patterns, or cost trends over time and surface actionable insights.
+ **Multi-step workflows** – Orchestrate sequences of tool calls across multiple integrations to complete complex operational procedures.
+ **Cross-tool correlation** – Combine data from observability platforms, CI/CD pipelines, and AWS services to answer complex operational questions.

For information about custom agent limits, see [Quotas](quotas.md).

## Next steps
<a name="next-steps"></a>
+ [Creating a custom agent](custom-agents-creating-a-custom-agent.md) – Define your first custom agent with a system prompt, tools, and skills.
+ [Executing custom agents](custom-agents-executing-custom-agents.md) – Run agents on demand or set up scheduled triggers.
+ [Managing custom agents](custom-agents-managing-custom-agents.md) – Edit, disable, or delete custom agents and view invocation history.
+ [Custom agent outputs](custom-agents-custom-agent-outputs.md) – Configure agents to produce artifacts and recommendations.