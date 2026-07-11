

# What is a DevOps Agent Topology?
<a name="about-aws-devops-agent-what-is-a-devops-agent-topology"></a>

AWS DevOps Agent's automatically discovers and visualizes the resources and relationships within your applications and uses the resulting topology to understand your infrastructure during incident investigations and when making preventative recommendations.

## How topology graphs are created
<a name="how-topology-graphs-are-created"></a>

AWS DevOps Agent builds topology graphs through several automated processes:
+ **Resource discovery** – The agent automatically scans your AWS accounts to identify resources like compute instances, storage services, networking components, and databases that are part of your applications.
+ **Relationship detection** – The agent analyzes configuration data, CloudFormation stacks, and resource tags to determine how resources relate to one another.
+ **Code and deployment mapping** – When connected to CI/CD pipelines, the agent links infrastructure resources back to their deployment processes and changed application and infrastructure code.
+ **Observability behavior mapping** – Data from observability systems such as Amazon CloudWatch Application Signals and Dynatrace are used to identify observed behaviors that indicate relationships between resources.

## Key capabilities
<a name="key-capabilities"></a>

Resource mapping provides several capabilities that enhance incident investigation and prevention:
+ **Interactive visualization** – Explore your application topology through an interactive graph in the Operator Web App. You can zoom and navigate the topology to understand complex relationships between resources. You can also use Chat to query topology information using natural language, such as 'Show me all Lambda functions connected to this DynamoDB table' or 'What resources are affected by this alarm?'.
+ **Contextual investigation** – During incident investigations, AWS DevOps Agent is assisted by the resource topology to identify affected components, understand blast radius, and trace the impact path through your systems.
+ **Root cause analysis** – The detailed understanding of resource relationships helps pinpoint where issues originate, even in complex distributed systems with many interdependencies.
+ **Impact assessment** – When analyzing incidents, the agent can better determine which downstream services might be affected by identifying dependency chains in the topology.
+ **Preventative recommendations** – The agent uses topology insights to make targeted recommendations for resilience improvements, suggesting changes that will have the most significant impact on system stability.

## Topology views
<a name="topology-views"></a>

The topology visualization in the Topology page in the Operator Web App offers multiple levels of detail, organized into two categories:

### Learned
<a name="learned"></a>

Learned view is generated from the Agent Space understanding and pipeline skill and display structured summaries of your infrastructure. The following learned views are available:
+ **Topology** – The default view, generated from the Agent Space Understanding skill. Displays a structured summary of your infrastructure organized by logical services and request paths.
+ **Pipeline** – Displays your CI/CD pipeline topology, showing deployment stages, actions, and their relationships to infrastructure resources. This view is only available when pipeline topology has been generated for your agent space.

### Others
<a name="others"></a>

This view shows your infrastructure at different levels of granularity based on raw resource discovery data:
+ **System** – Shows high-level account and region boundaries.
+ **Container** – Displays deployment stacks like CloudFormation stacks that contain related resources.
+ **Components** – Shows individual components within containers and their relationships.
+ **All Resources** – Shows the complete view with all discovered resources and their relationships.

## Resource discovery
<a name="resource-discovery"></a>

Resources are discovered through two methods:
+ **CloudFormation stacks** – The agent lists all CloudFormation stacks and their resources in the primary AWS account and any connected secondary accounts. This is supported for any infrastructure-as-code tooling that uses CloudFormation for deployment, including AWS Cloud Development Kit (AWS CDK).
+ **Resource Explorer** – For resources not deployed from CloudFormation, tagged resources are discovered from AWS Resource Explorer. The target AWS account must have Resource Explorer enabled. This is useful for identifying application boundaries for resources deployed through the AWS Management Console, the AWS service APIs, or other infrastructure-as-code frameworks.

## Investigation scope beyond topology
<a name="investigation-scope-beyond-topology"></a>

While the application topology provides important context during investigations, AWS DevOps Agent is not limited to investigating only the resources shown in the topology. The agent may use additional data sources, such as AWS service APIs or connected observability tools, to investigate resources that are not in the application topology.

To limit the resources the agent has access to, restrict the policy for the role assigned to the agent to access cross-account resources. For more information, see [Limiting Agent Access in an AWS Account](aws-devops-agent-security-limiting-agent-access-in-an-aws-account.md).

## Topology and the Agent Space Understanding skill
<a name="topology-and-the-agent-space-understanding-skill"></a>

The topology graph feeds into the Agent Space Understanding learned skill, which encodes a structured summary of your infrastructure for use during investigations. When topology discovery completes for a new agent space, the system automatically generates the Agent Space Understanding skill. For more information about learned skills, see [Learned Skills](about-aws-devops-agent-learned-skills.md).