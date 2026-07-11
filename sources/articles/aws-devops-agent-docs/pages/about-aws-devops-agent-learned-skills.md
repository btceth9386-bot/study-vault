

# Learned Skills
<a name="about-aws-devops-agent-learned-skills"></a>

## What Are Learned Skills?
<a name="what-are-learned-skills"></a>

Learned skills are structured knowledge files that the DevOps Agent generates from your Agent Space data. Each learned skill encodes a specific type of knowledge that the AWS DevOps Agent uses as it performs tasks. At launch, four learned skills are available: Agent Space Understanding, Understanding Code Dependencies, Understanding Pipeline Topology, and Tool Use Best Practices.

### Agent Space Understanding
<a name="agent-space-understanding"></a>

The Agent Space Understanding skill (`understanding-agent-space`) analyzes your connected cloud accounts, code repositories, and telemetry integrations to build a map of the resources and relationships in an Agent Space.

The skill produces a main `SKILL.md` file and a set of reference files. The main file contains a plain-language system overview with key domain concepts, the deployment environments (AWS account and region pairs, Azure subscriptions and regions, and so on), a container-level architecture diagram showing how logical services connect, the request paths that are central to your application with the components they traverse, and a mapping of code repositories to containers.

Each logical container receives a dedicated reference file describing its internal components (compute, data, messaging, network, and others) with resource types and physical identifiers such as ARNs, table names, and queue URLs. The reference file also captures observability coverage, including the alarms, dashboards, and monitors linked to each component. It also maps each component to its associated code repositories, packages, and infrastructure-as-code definitions, providing a complete traceability chain from source code to deployed resources.

Each critical request path receives a dedicated reference file describing the full end-to-end request flow at component granularity, from the entry point through each intermediate service, data store, and external dependency. The file includes a sequenced flow diagram showing the order of operations and interaction mechanisms between components, along with the responsibility of each participant. It also catalogs the observability signals relevant to the path: log group patterns for each hop, key metrics (latency, error rates, throttling, token quotas) with their alarm names and dimensions, and distributed trace spans that can be correlated across services and accounts.

### Understanding Code Dependencies
<a name="understanding-code-dependencies"></a>

The Understanding Code Dependencies skill (`understanding-code-dependencies`) produces a complete service-to-service and package dependency map. Use this skill to understand how repositories connect: which services call which, what events flow between them, which packages are shared, and where infrastructure boundaries lie. This skill is essential for assessing blast radius of changes, identifying upstream/downstream impacts, and understanding deployment ordering.

### Understanding Pipeline Topology
<a name="understanding-pipeline-topology"></a>

The Understanding Pipeline Topology skill (`understanding-pipeline-topology`) maps project pipelines from start to finish, including steps, environment promotions, and deployments along the way to release. This helps the agent distinguish between production and pre-production environments and understand the status of a change in the release process.

### Tool Use Best Practices
<a name="tool-use-best-practices"></a>

The Tool Use Best Practices skill analyzes past investigation tool uses to extract effective usage patterns, common failure modes, and parameter guidance. This helps the DevOps Agent avoid known pitfalls and run investigations with fewer wasted steps. The skill produces a main file and a set of per-tool reference files. The main file serves as a routing index that lists each tool with the investigation scenarios it supports and links to the corresponding reference file.

Each per-tool reference file can include up to three sections:
+ **Best Practices** — Investigation-driven techniques extracted from successful tool usage, such as CloudWatch Logs Insights query templates, environment-specific metric namespaces and dimensions, and CloudTrail event source filters. Each entry is organized around an investigation scenario and includes concrete parameter values and examples observed in past investigations.
+ **Common Errors** — Recurring failure modes and their fixes. Each entry describes a specific error condition, such as querying an inaccessible account or constructing a malformed aggregation query, and provides a corrective action so the agent can avoid or recover from the error without wasting investigation steps.
+ **Output Management** — Guidance for tool calls that tend to return large responses. Each entry describes a parameter change or processing strategy that reduces output size while preserving diagnostic value.

When live infrastructure access is available, the skill validates patterns against your environment before including them. Confirmed patterns are stated with confidence, unconfirmed patterns use cautious language, and disproved patterns are excluded. This keeps the skill aligned with the current state of your infrastructure.

## Managing Learned Skills
<a name="managing-learned-skills"></a>

The DevOps Agent automatically generates and updates learned skills based on activity in your Agent Space. The following describes when each skill is updated.

The DevOps Agent generates an updated **Tool Use Best Practices** skill every 30 investigations.

The **Agent Space Understanding** skill is generated by the learning agent, which runs whenever you add, update, or remove an Agent Space capability or integration. It is also periodically refreshed every 3 days for active Agent Spaces. An Agent Space is considered active if it has had at least one investigation in the last 30 days. If your Agent Space has no investigations for 30 days, skill refresh pauses automatically. It resumes when a new investigation starts.

To regenerate learned skills manually, choose the **Regenerate** button on the Topology page in the operator app, or chat with the agent and ask it to update the learned skills.

**Deactivation** — Learned skills are active by default. When active, the DevOps Agent loads them at the start of each DevOps Agent task. To stop a learned skill from being applied, deactivate it from the **Knowledge** page **Skills** tab in the operator app. Deactivating a skill does not delete it. The skill is retained and can be reactivated at any time. When a skill is deactivated, the DevOps Agent operates without that skill's knowledge. You can also deactivate the corresponding managed memory store from the **Memories** tab independently.

**Topology view** — The Topology page in your Agent Space’s web app uses the Agent Space Understanding Skill to visually display your Agent Space environment as logical containers and components . Choose any container to see its components, resource identifiers, and telemetry.

**Summary report** — The summary report is a versioned, read-only view of what the DevOps Agent knows about your environment, derived from the Agent Space Understanding skill. You can find it in two places: the **Summary report** tab on the Agent Space details page in the AWS DevOps Agent admin console, and the **Artifacts** section of the DevOps Agent web app.

Depending on what you have configured for your Agent Space, the report can include the deployment environments, the container architecture, the critical request paths, and the code-repository mapping. Each report is versioned, so you can browse earlier versions to see how your environment has changed over time. From the web app, choose **Chat about report** to discuss any section with the DevOps Agent or compare it to an earlier version.