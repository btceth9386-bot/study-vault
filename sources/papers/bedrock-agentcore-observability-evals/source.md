# Amazon Bedrock AgentCore Developer Guide — Observability and Evaluations (selected chapters)

Source: Amazon Bedrock AgentCore Developer Guide (3,428-page PDF), filtered to selected page ranges.


## Harness observability (pp. 96–97)

Related topics
• the section called “Skills” - attach skills from Git, S3, or AWS Skills
• the section called “Memory” - persist conversations across sessions
• the section called “Tools” - connect tools to your harness
• the section called “Security” - execution role policies and VPC conﬁguration
• the section called “API Documentation”

Observability and cost controls
This page covers monitoring your harness, controlling execution costs, and managing resource tags.

Observability
Every harness invocation automatically generates traces, logs, and metrics through AgentCore
Observability in CloudWatch. Model calls, tool invocations, memory operations, shell commands:
each step appears with timing and payload details. No extra conﬁguration. Traces are available
from the ﬁrst invocation.
Traces, logs, and metrics ﬂow to CloudWatch through the harness execution role. View them in the
AgentCore Observability dashboard, or query programmatically through the CloudWatch Logs and
X-Ray APIs.
Before you see traces, enable Transaction Search in CloudWatch (one-time per account). See
AgentCore Observability getting started for setup details.
Learn more: Observability overview · metrics · telemetry

CloudTrail
Harness operations are logged to AWS CloudTrail as management events (control
plane) and data events (data plane). In CloudTrail, harness resources appear under the
AWS::BedrockAgentCore::Runtime resource type rather than a harness-speciﬁc type. Harness
is a managed abstraction over AgentCore Runtime, and CloudTrail events reﬂect the underlying
runtime resource for consistency.
All harness CloudTrail events use resources.type = AWS::BedrockAgentCore::Runtime. The
event names are:
Observability and cost controls

96

• CreateHarness, UpdateHarness, DeleteHarness, GetHarness, ListHarnesses
(management events)
• InvokeAgentRuntime, InvokeAgentRuntimeCommand (data events)

Note
Data plane operations appear as InvokeAgentRuntime and
InvokeAgentRuntimeCommand in CloudTrail, matching the underlying Runtime API. The
resources.ARN ﬁeld contains the harness ARN for control plane events and the runtime
ARN for data plane events.

Understand harness costs
There is no additional charge for the harness itself. You pay standard rates for the underlying
capabilities that the harness uses. For current rates, see Amazon Bedrock AgentCore pricing and
the pricing page for your model provider.
The following table describes the capabilities that can incur charges when you use the harness.
Capability

When charges apply

What determines usage

AgentCore
Runtime

AgentCore Runtime starts a
microVM for every harness
session.

AgentCore Runtime bills for actual CPU
consumed and peak memory consumed
each second from microVM startup through
termination, including system overhead. CPU
charges don’t apply during model or tool I/
O wait if no background process uses CPU.
Memory remains billable while the session
runs.

Model
inference

Understand harness costs

The model provider bills
each time the agent calls
the conﬁgured model. One
harness invocation can make
multiple model calls.

The provider calculates charges from input
and output tokens. Input includes the system
prompt, conversation history, retrieved
memory, skill instructions, and deﬁnitions for
allowed tools. For tool-deﬁnition overhead,
see the section called “Tools”.
97


## Runtime: observe agents (pp. 499–499)

Quotas and limits
Limit

Value

Description

Maximum frame payload size

64 KB

Frames exceeding this limit
result in close code 1009.

Frame rate

250 frames/sec

Exceeding this triggers close
code 1008.

Maximum connection
duration

1 hour

The connection closes with
code 1008. Reconnect
using the same shellId to
continue.

Concurrent shell sessions
(terminals) per runtime

10

New connections are rejected
if 10 sessions are already
open. Close an existing
session and retry.

Reconnection buﬀer

256 KB

Maximum output replayed
when reconnecting to a shell.

For complete service limits, see Quotas for Amazon Bedrock AgentCore.

Observe agents in Amazon Bedrock AgentCore Runtime
For information about the AgentCore Runtime observability metrics, see Add observability to your
Amazon Bedrock AgentCore resources.

Security best practices for AgentCore Runtime
This topic consolidates security best practices for Amazon Bedrock AgentCore Runtime. Use these
recommendations to secure your agent deployments, protect data, and follow the principle of least
privilege.
Topics
Observe agents

499


## AgentCore Observability: get started, instrumentation, best practices, concepts (pp. 1875–1910)

Observe your agent applications on Amazon Bedrock
AgentCore Observability
With AgentCore, you can trace, debug, and monitor AI agents' performance in production
environments.
AgentCore Observability helps you trace, debug, and monitor agent performance in production
environments. It oﬀers detailed visualizations of each step in the agent workﬂow, enabling you to
inspect an agent’s execution path, audit intermediate outputs, and debug performance bottlenecks
and failures.
AgentCore Observability gives you real-time visibility into agent operational performance through
access to dashboards powered by Amazon CloudWatch and telemetry for key metrics such as
session count, latency, duration, token usage, and error rates. Rich metadata tagging and ﬁltering
simplify issue investigation and quality maintenance at scale. AgentCore emits telemetry data in
standardized OpenTelemetry (OTEL)-compatible format, enabling you to easily integrate it with
your existing monitoring and observability stack.
By default, AgentCore outputs a set of key built-in metrics for agents, gateway resources, and
memory resources. For memory resources, AgentCore also outputs spans and log data if you enable
it. You can also instrument your agent code to provide additional span and trace data and custom
metrics and logs. See Add observability to your Amazon Bedrock AgentCore resources to learn
more.
All of the metrics, spans, and logs output by AgentCore are stored in Amazon CloudWatch, and can
be viewed in the CloudWatch console or downloaded from CloudWatch using the AWS CLI or one
of the AWS SDKs.
In addition to the raw data stored in CloudWatch Logs, for agent runtime data only, the
CloudWatch console provides an observability dashboard containing trace visualizations, graphs
for custom span metrics, error breakdowns, and more. To learn more about viewing your agents'
observability data, see View observability data for your Amazon Bedrock AgentCore agents
Topics
• Get started with AgentCore Observability
• Add observability to your Amazon Bedrock AgentCore resources
• Understand observability for agentic resources in AgentCore
1875

• Amazon Bedrock AgentCore generated observability data
• View observability data for your Amazon Bedrock AgentCore agents
• Monitor AgentCore resources across accounts

Get started with AgentCore Observability
Amazon Bedrock AgentCore Observability helps you trace, debug, and monitor agent performance
in production environments. This guide helps you implement observability features in your agent
applications.
Topics
• Prerequisites
• Step 1: Enable transaction search on CloudWatch
• Step 2: Enable observability for Amazon Bedrock AgentCore Runtime hosted agents
• Step 3: Enable observability for non-Amazon Bedrock AgentCore-hosted agents
• Step 4: Observe your agent with GenAI observability on Amazon CloudWatch
• Best practices

Prerequisites
Before starting, make sure you have:
• AWS Account with credentials conﬁgured ( aws configure ) with model access enabled to the
Foundation Model you would like to use.
• Python 3.10+ installed
• Enable transaction search on Amazon CloudWatch. Only once, ﬁrst-time users must enable
CloudWatch Transaction Search to view Bedrock Amazon Bedrock AgentCore spans and traces
• (Non-runtime agents only) Add the OpenTelemetry library – Include aws-opentelemetrydistro (ADOT) in your requirements.txt ﬁle. If you host your agent on AWS Lambda, use the
AWS Lambda Layer for OpenTelemetry on the AWS Distro for OpenTelemetry website instead.
• (Non-runtime agents only) Make sure that your framework is conﬁgured to emit traces (for
example, strands-agents[otel] package). You may sometimes need to include your
agent framework’s auto-instrumentor (for example, opentelemetry-instrumentationlangchain ).
Get started with AgentCore Observability

1876

Amazon Bedrock AgentCore Observability oﬀers two ways to conﬁgure monitoring to match
diﬀerent infrastructure needs:
1. Amazon Bedrock AgentCore Runtime-hosted agents
2. Non-runtime hosted agents
As a one time setup per AWS account, ﬁrst time users need to enable Transaction Search on
Amazon CloudWatch. There are two ways to do this, via the API and via the CloudWatch Console.

Step 1: Enable transaction search on CloudWatch
After you enable Transaction Search, it can take ten minutes for spans to become available for
search and analysis. Choose one of the options below:

Option 1: Enable transaction search using an API
To enable transaction search using the API
1. Create a policy that grants access to ingest spans in CloudWatch Logs using AWS CLI.
An example is shown below on how to format your AWS CLI command with
PutResourcePolicy.
aws logs put-resource-policy --policy-name MyResourcePolicy --policy-document
'{ "Version": "2012-10-17", "Statement": [ { "Sid": "TransactionSearchXRayAccess",
"Effect": "Allow", "Principal": { "Service": "xray.amazonaws.com" }, "Action":
"logs:PutLogEvents", "Resource": [ "arn:partition:logs:region:account-id:loggroup:aws/spans:*", "arn:partition:logs:region:account-id:log-group:/aws/
application-signals/data:*" ], "Condition": { "ArnLike": { "aws:SourceArn":
"arn:partition:xray:region:account-id:*" }, "StringEquals": { "aws:SourceAccount":
"account-id" } } } ]}'

2. Conﬁgure the destination of trace segments.
An example is shown below on how to format your AWS CLI command with
UpdateTraceSegmentDestination.
aws xray update-trace-segment-destination --destination CloudWatchLogs

3. Optional Conﬁgure the amount of spans to index.
Step 1: Enable transaction search on CloudWatch

1877

Conﬁgure your desired sampling percentage with UpdateIndexingRule.
aws xray update-indexing-rule --name "Default" --rule '{"Probabilistic":
{"DesiredSamplingPercentage": number}}'

Option 2: Enable transaction search in the CloudWatch console
To enable transaction search in the CloudWatch console
1. Open the CloudWatch console at https://console.aws.amazon.com/cloudwatch/.
2. In the navigation pane under Setup , choose Settings.
3. Select Account and choose X-Ray traces tab.
4. In the Transaction Search section, choose View settings.
5. On the page that opens, choose Edit.
6. Choose Enable Transaction Search.
7. Select For X-Ray users and enter the percentage of traces to index. You can index 1% of traces
at no cost and adjust this percentage later based on your needs.
8. Choose Save . Wait till Ingest OpenTelemetry spans shows Enabled before sending traces.
Let’s now proceed to exploring the two ways to conﬁgure observability.

Step 2: Enable observability for Amazon Bedrock AgentCore Runtime
hosted agents
Amazon Bedrock AgentCore Runtime-hosted agents are deployed and executed directly within
the Amazon Bedrock AgentCore environment, providing automatic instrumentation with minimal
conﬁguration. When you deploy an agent using the AgentCore CLI, the runtime automatically
instruments your agent with OpenTelemetry — no additional OTEL libraries or conﬁguration are
needed.
For a complete example, refer to the AgentCore Observability samples on GitHub

Create your agent project
Create a new project using the AgentCore CLI. This sets up your project folder, virtual environment,
and dependencies:

Step 2: Enable observability for Amazon Bedrock AgentCore Runtime hosted agents

1878

npm install -g @aws/agentcore
agentcore create \
--project-name StrandsObservability \
--name StrandsClaudeGettingStarted \
--language Python \
--framework Strands \
--model-provider Bedrock \
--memory none
cd StrandsObservability/app/StrandsClaudeGettingStarted
uv add strands-agents-tools
cd ../..

In the project’s agent directory, replace the default agent code with your own agent logic. The
following is an example using the Strands Agents SDK:
## app/StrandsClaudeGettingStarted/main.py
from strands import Agent, tool
from strands_tools import calculator
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands.models import BedrockModel
app = BedrockAgentCoreApp()
@tool
def weather():
"""Get weather"""
return "sunny"
model = BedrockModel(
model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
)
agent = Agent(
model=model,
tools=[calculator, weather],
system_prompt="You're a helpful assistant. You can do simple math calculation, and
tell the weather."
)
@app.entrypoint
def strands_agent_bedrock(payload):
"""Invoke the agent with a payload"""
user_input = payload.get("prompt")
if not isinstance(user_input, str) or not user_input:
Step 2: Enable observability for Amazon Bedrock AgentCore Runtime hosted agents

1879

return "Error: 'prompt' must be a non-empty string"
response = agent(user_input)
return response.message['content'][0]['text']
if __name__ == "__main__":
app.run()

Deploy and invoke your agent
Deploy the agent to AgentCore Runtime. The AgentCore CLI handles packaging, deployment, and
automatic OTEL instrumentation:
agentcore deploy

After deployment, your agent runs on AgentCore Runtime and is automatically instrumented
using OpenTelemetry. Invoke your agent and view the traces, sessions, and metrics on the GenAI
Observability dashboard in Amazon CloudWatch:
agentcore invoke

Alternatively, you can invoke your agent programmatically using the AWS SDK:
import boto3, json
client = boto3.client('bedrock-agentcore')
response = client.invoke_agent_runtime(
agentRuntimeArn="YOUR_AGENT_RUNTIME_ARN",
runtimeSessionId="my-observability-session-001",
payload=json.dumps({"prompt": "What is 2 + 2?"}),
qualifier="DEFAULT"
)
print(json.loads(response['response'].read()))

Step 3: Enable observability for non-Amazon Bedrock AgentCorehosted agents
For agents running outside of the Amazon Bedrock AgentCore runtime, you can deliver the same
monitoring capabilities for agents deployed on your own infrastructure. This allows consistent
Step 3: Enable observability for non-Amazon Bedrock AgentCore-hosted agents

1880

observability regardless of where your agents run. Use the following steps to conﬁgure the
environment variables needed to observe your agents.
For a complete example, see the Agents on Amazon EKS sample on the GitHub website.

Conﬁgure AWS environment variables
export AWS_ACCOUNT_ID=<account id>
export AWS_DEFAULT_REGION=<default region>
export AWS_REGION=<region>
export AWS_ACCESS_KEY_ID=<access key id>
export AWS_SECRET_ACCESS_KEY=<secret key>

Conﬁgure CloudWatch logging
Create a log group and log stream for your agent in Amazon CloudWatch which you can use to
conﬁgure below environment variables.

Conﬁgure OpenTelemetry environment variables
export AGENT_OBSERVABILITY_ENABLED=true # Activates the ADOT pipeline
export OTEL_PYTHON_DISTRO=aws_distro # Uses AWS Distro for OpenTelemetry
export OTEL_PYTHON_CONFIGURATOR=aws_configurator # Sets AWS configurator for ADOT SDK
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf # Configures export protocol
export OTEL_EXPORTER_OTLP_LOGS_HEADERS=x-aws-log-group=<YOUR-LOG-GROUP>,x-aws-logstream=<YOUR-LOG-STREAM>,x-aws-metric-namespace=<YOUR-NAMESPACE>
# Directs logs to CloudWatch groups
export OTEL_EXPORTER_OTLP_TRACES_HEADERS=x-aws-log-group=<YOUR-LOG-GROUP>,x-aws-logstream=<YOUR-TRACES-LOG-STREAM>
# (Optional) Directs spans to your log group instead of the aws/spans log group.
Requires ADOT version 0.18.0 or later.
export OTEL_RESOURCE_ATTRIBUTES=service.name=<YOUR-AGENT-NAME> # Identifies your agent
in observability data
export OTEL_AWS_APPLICATION_SIGNALS_ENABLED=false # AWS Lambda Layer for OpenTelemetry
only: disables Application Signals
export OTEL_LOGS_EXPORTER=otlp # AWS Lambda Layer for OpenTelemetry only: exports logs
over OTLP
export OTEL_METRICS_EXPORTER=awsemf # AWS Lambda Layer for OpenTelemetry only: exports
metrics as CloudWatch EMF

Replace <YOUR-AGENT-NAME> with a unique name to identify this agent in the GenAI
Observability dashboard and logs.
Step 3: Enable observability for non-Amazon Bedrock AgentCore-hosted agents

1881

Note
If you set OTEL_EXPORTER_OTLP_TRACES_HEADERS to deliver spans to your own log
group, you must also add an Amazon CloudWatch Logs resource policy. The policy must
allow X-Ray (xray.amazonaws.com) to call logs:PutLogEvents on that log group. Use
the same policy shown in Enable transaction search using an API, with your log group’s ARN
in Resource. Without this policy, X-Ray can’t deliver spans to your log group.

Create an agent locally
# Create agent.py - Strands agent that is a weather assistant
from strands import Agent
from strands_tools import http_request
# Define a weather-focused system prompt
WEATHER_SYSTEM_PROMPT = """You are a weather assistant with HTTP capabilities. You can:
1. Make HTTP requests to the National Weather Service API
2. Process and display weather forecast data
3. Provide weather information for locations in the United States
When retrieving weather information:
1. First get the coordinates or grid information using https://api.weather.gov/points/
{latitude},{longitude} or https://api.weather.gov/points/{zipcode}
2. Then use the returned forecast URL to get the actual forecast
When displaying responses:
- Format weather data in a human-readable way
- Highlight important information like temperature, precipitation, and alerts
- Handle errors appropriately
- Convert technical terms to user-friendly language
Always explain the weather conditions clearly and provide context for the forecast.
"""
# Create an agent with HTTP capabilities
weather_agent = Agent(
system_prompt=WEATHER_SYSTEM_PROMPT,
tools=[http_request], # Explicitly enable http_request tool
)

Step 3: Enable observability for non-Amazon Bedrock AgentCore-hosted agents

1882

response = weather_agent("What's the weather like in Seattle?")
print(response)

Run your agent with automatic instrumentation command
With aws-opentelemetry-distro in your requirements.txt, the opentelemetry-instrument
command will:
• Load your OTEL conﬁguration from your environment variables
• Automatically instrument Strands, Amazon Bedrock calls, agent tools and databases, and other
requests made by the agent
• Send traces to CloudWatch
• Enable you to visualize the agent’s decision-making process in the GenAI Observability
dashboard
Use the following command to run your agent with automatic instrumentation:
opentelemetry-instrument python agent.py

If you host your agent on AWS Lambda, use the AWS Lambda Layer for OpenTelemetry on
the AWS Distro for OpenTelemetry website. Add the layer to your function, and then set the
AWS_LAMBDA_EXEC_WRAPPER environment variable to /opt/otel-instrument. The layer
then auto-instruments your function. With this approach, you don’t need to add the awsopentelemetry-distro package or run the opentelemetry-instrument command described
earlier.

ADOT Collector not supported for agent observability
The ADOT Collector is not supported for agent observability. To send telemetry from an
agent hosted outside of AgentCore runtime, you must use either the ADOT SDK or the AWS
Lambda Layer for OpenTelemetry.

You can now view your traces, sessions and metrics on GenAI Observability Dashboard on Amazon
CloudWatch with the value of YOUR-AGENT-NAME that you conﬁgured in your environment
variables.
Step 3: Enable observability for non-Amazon Bedrock AgentCore-hosted agents

1883

To correlate traces across multiple agent runs, you can associate a session ID with your telemetry
data using OpenTelemetry baggage:
from opentelemetry import baggage, context
ctx = baggage.set_baggage("session.id", session_id)

Step 4: Observe your agent with GenAI observability on Amazon
CloudWatch
After implementing observability, you can view the collected data in CloudWatch:

Observe your agent
1. Open the GenAI Observability on CloudWatch console
2. You can view the data related to model invocations and agents on Bedrock Amazon Bedrock
AgentCore on the dashboard.
3. In the Bedrock Agentcore tab you can view Agents View, Sessions View and Traces View.
4. Agents View lists all your Agents that are on and not on runtime, you can also choose an agent
and view further details like runtime metrics, sessions and traces speciﬁc to an agent.
5. In the Sessions View tab, you can navigate across all the sessions associated with agents.
6. In the Trace View tab, you can look into the traces and span information for agents. Also explore
the trace trajectory and timeline by choosing a trace.

View logs in CloudWatch
To view logs in CloudWatch
1. Open the CloudWatch console
2. In the left navigation pane, expand Logs and select Log groups
3. Search for your agent’s log group:
• Standard logs (stdout/stderr) Location: /aws/bedrock-agentcore/runtimes/
<agent_id>-<endpoint_name>/[runtime-logs] <UUID>
• OTEL structured logs: /aws/bedrock-agentcore/runtimes/<agent_id><endpoint_name>/runtime-logs
Step 4: Observe your agent with GenAI observability on Amazon CloudWatch

1884

View traces and spans
To view traces and spans
1. Open the CloudWatch console
2. Select Transaction Search from the left navigation
3. Location: the spans log stream in the agent’s log group (/aws/bedrock-agentcore/
runtimes/<agent_id>-<endpoint_name>), or the default log stream in the aws/spans
log group for agents that use the shared span destination
4. Filter by service name or other criteria
5. Select a trace to view the detailed execution graph

View metrics
To view metrics
1. Open the CloudWatch console
2. Select Metrics from the left navigation
3. Browse to the bedrock-agentcore namespace
4. Explore the available metrics

Best practices
1. Start simple, then expand - The default observability provided by Amazon Bedrock AgentCore
captures most critical metrics automatically, including model calls, token usage, and tool
execution.
2. Conﬁgure for development stage - Tailor your observability conﬁguration to match your
current development phase and progressively adjust.
3. Use consistent naming - Establish naming conventions for services, spans, and attributes from
the start
4. Filter sensitive data - Prevent exposure of conﬁdential information by ﬁltering sensitive data
from observability attributes and payloads.
5. Set up alerts - Conﬁgure CloudWatch alarms to notify you of potential issues before they
impact users
Best practices

1885

Add observability to your Amazon Bedrock AgentCore
resources
Amazon Bedrock AgentCore provides a number of built-in metrics to monitor the performance of
resources for the AgentCore runtime, memory, gateway, built-in tools, and identity resource types.
This default data is available in Amazon CloudWatch. To view the full range of observability data in
the CloudWatch console, or to output custom runtime metrics for agents, you need to instrument
your code using the AWS Distro for Open Telemetry (ADOT) SDK.
To view the observability dashboard in CloudWatch, open the Amazon CloudWatch GenAi
Observability page.
See the following sections to learn more about conﬁguring your resources to view observability
metrics in the CloudWatch console generative AI observability page and in CloudWatch Logs.

Tip
Use of the ADOT SDK to output custom metrics is also supported for agents running
outside the AgentCore runtime. To learn how to enable observability for these agents, see
Enabling observability for agents hosted outside of AgentCore.

Topics
• Enabling AgentCore observability
• Enabling observability in agent code for AgentCore-hosted agents
• Enabling observability for agents hosted outside of AgentCore
• Enabling observability for AgentCore runtime, memory, gateway, built-in tools, and identity
resources
• Enhanced AgentCore runtime observability with custom headers
• Enhanced AgentCore built-in tools observability with custom headers
• Enhanced AgentCore identity observability with custom headers
• Observability best practices
• Using other observability platforms

Add observability to your agents

1886

Enabling AgentCore observability
To view metrics, spans, and traces generated by the AgentCore service, you ﬁrst need to complete a
one-time setup to turn on Amazon CloudWatch Transaction Search. To view service-provided spans
for memory resources, you also need to enable tracing when you create a memory. See Enabling
observability for AgentCore runtime, memory, gateway, built-in tools, and identity resources to
learn more.
The following sections describe how to perform these setup actions and to enable observability in
your agent code.

Enabling CloudWatch Transaction Search
You can enable CloudWatch Transaction Search either by using the CloudWatch console, or by
using an API through the AWS Command Line Interface (AWS CLI) or one of the AWS SDKs.
Use one of the following procedures to enable Transaction Search.
Example
CloudWatch console
1. ====== To enable CloudWatch Transaction Search in the CloudWatch console
2. Open the CloudWatch console.
3. In the navigation pane, expand Application Signals (APM) and choose Transaction search.
4. Choose Enable Transaction Search.
5. Select the checkbox to ingest spans as structured logs.
6. Choose Save.
API
1. ====== To enable CloudWatch Transaction Search using an API
2. When using the AWS CLI or an AWS SDK to enable Transaction Search, ﬁrst conﬁgure the
necessary permissions to ingest spans in CloudWatch Logs by adding a resource-based policy
with PutResourcePolicy.
The following AWS CLI command adds a resource policy that gives AWS X-Ray permissions to
send traces to CloudWatch Logs.
Enabling AgentCore observability

1887

aws logs put-resource-policy --policy-name MyResourcePolicy --policydocument '{ "Version": "2012-10-17",
"Statement": [ { "Sid":
"TransactionSearchXRayAccess", "Effect": "Allow", "Principal": { "Service":
"xray.amazonaws.com" }, "Action": "logs:PutLogEvents", "Resource":
[ "arn:partition:logs:region:account-id:log-group:aws/spans:*",
"arn:partition:logs:region:account-id:log-group:/aws/applicationsignals/data:*" ], "Condition": { "ArnLike": { "aws:SourceArn":
"arn:partition:logs:region:account-id:*" }, "StringEquals":
{ "aws:SourceAccount": "account-id" } } } ]}'

For clarity, the inline JSON policy in this command is shown expanded in the following
example:
{
"Version":"2012-10-17",
"Statement": [
{
"Sid": "TransactionSearchXRayAccess",
"Effect": "Allow",
"Principal": {
"Service": "xray.amazonaws.com"
},
"Action": "logs:PutLogEvents",
"Resource": [
"arn:aws:logs:us-east-1:123456789012:log-group:aws/spans:*",
"arn:aws:logs:us-east-1:123456789012:log-group:/aws/applicationsignals/data:*"
],
"Condition": {
"ArnLike": {
"aws:SourceArn": "arn:aws:xray:us-east-1:123456789012:*"
},
"StringEquals": {
"aws:SourceAccount": "123456789012"
}
}
}
]
}

3. Conﬁgure the destination of your trace segments using UpdateTraceSegmentDestination.

Enabling AgentCore observability

1888

To use the AWS CLI, run the following command.
aws xray update-trace-segment-destination --destination CloudWatchLogs

4. (Optional) Conﬁgure your desired sampling percentage using UpdateIndexingRule.
To use the AWS CLI, run the following command.
aws xray update-indexing-rule --name "Default" --rule '{"Probabilistic":
{"DesiredSamplingPercentage": number}}'

Span destination for agents hosted in Amazon Bedrock AgentCore runtime
Tip
You can now consolidate all of an agent’s telemetry—spans, structured logs, and standard
output—in a single log group for each agent.

With AgentCore runtime, a capability of Amazon Bedrock AgentCore, you can conﬁgure an agent
to deliver its spans to the same Amazon CloudWatch log group as the agent’s logs. With this
conﬁguration, spans go to the spans log stream in /aws/bedrock-agentcore/runtimes/
<agent_id>-<endpoint_name>, instead of the shared aws/spans log group. You can keep
spans, structured logs, and standard output together in one per-agent log group, scope access
control and encryption to an individual agent, and export telemetry from a single location.
In supported AWS Regions, newly created agents use the agent’s log group as the default span
destination. Agents created before a Region supports the uniﬁed span destination keep the shared
aws/spans log group as their default.
You can override the default for an individual agent with the
UNIFIED_TRACES_DESTINATION_ENABLED environment variable on your agent runtime:
• To opt in an existing agent that uses the shared aws/spans log group, set
UNIFIED_TRACES_DESTINATION_ENABLED=true. AgentCore then delivers the agent’s spans
to its own log group.

Enabling AgentCore observability

1889

• To opt out an agent that uses its own log group by default, set
UNIFIED_TRACES_DESTINATION_ENABLED=false. AgentCore then delivers the agent’s spans
to the shared aws/spans log group.
For AgentCore to deliver spans to the agent’s log group, the following must be true:
• Enable CloudWatch Transaction Search in your account and send trace segments to Amazon
CloudWatch Logs. Without Transaction Search, AgentCore can’t deliver spans to the agent’s log
group. For more information, see Enabling CloudWatch Transaction Search.
• Grant the logs:PutResourcePolicy action on the agent’s log group to the agent’s execution
role. AgentCore uses this permission to allow AWS X-Ray to deliver spans to the log group. For
more information, see Execution role for running an agent in AgentCore runtime.
• The agent uses ADOT version 0.18.0 or later (aws-opentelemetry-distro>=0.18.0). Earlier
versions ignore the span destination conﬁguration and deliver spans to the shared aws/spans
log group.
Changing the span destination doesn’t move existing span data. Spans that AgentCore already
delivered remain in their original log group.

Enabling observability in agent code for AgentCore-hosted agents
In addition to the service-generated metrics, with AgentCore you can also gather span and trace
data as well as custom metrics emitted from your agent code.
When you use agent frameworks like Strands , LangChain , or CrewAI with supported third-party
instrumentation libraries, the framework itself comes with built in support for OTEL and GenAI
semantic conventions, and it can also be instrumented with an auto-instrumentation package
such as opentelemetry-instrument-langchain . It is also possible to send Generative AI
semantic conventions telemetry and spans by deﬁning a custom tracer. AgentCore supports use of
the following instrumentation libraries in your agent framework:
• OpenInference
• Openllmetry
• OpenLit
• Traceloop

Enabling observability in agent code for AgentCore-hosted agents

1890

To view this data in the CloudWatch console generative AI observability page and in Amazon
CloudWatch, you need to add the AWS Distro for Open Telemetry (ADOT) SDK to your agent code.
Note
With AgentCore, you can also view metrics for agents that aren’t running in the AgentCore
runtime. Additional setup steps are required to conﬁgure telemetry outputs for nonAgentCore agents. See the instructions in Enabling observability for agents hosted outside
of AgentCore to learn more.

To add ADOT support and enable AgentCore observability, follow the steps in the following
procedure.
Add observability to your AgentCore agent
1. Ensure that your framework is conﬁgured to emit traces. For example, in the Strands framework,
the tracer object must be conﬁgured to instruct Strands to emit Open Telemetry (OTEL) logs.
2. Add the ADOT SDK and boto3 to your agent’s dependencies. For Python, add the following to
your requirements.txt ﬁle:
aws-opentelemetry-distro>=0.18.0
boto3

Alternatively, you can install the dependencies directly:
pip install aws-opentelemetry-distro>=0.18.0 boto3

3. Execute your agent code using the OpenTelemetry auto-instrumentation command:
opentelemetry-instrument python my_agent.py

This auto-instrumentation approach automatically adds the SDK to the Python path. You may
already be using this approach as part of your standard OpenTelemetry implementation.
For containerized environment (such as docker) add the following command:
CMD ["opentelemetry-instrument", "python", "main.py"]
Enabling observability in agent code for AgentCore-hosted agents

1891

When using ADOT, in order to propagate session id correctly, deﬁne the X-Amzn-BedrockAgentCore-Runtime-Session-Id in the request header. ADOT then sets the session_id
correctly in the downstream headers.
To propagate a trace ID, invoke the AgentCore runtime with the parameter
traceId=<traceId> set.
You can also invoke your agent with additional headers for additional observability options. See
Enhanced AgentCore runtime observability with custom headers to learn more.

Enabling observability for agents hosted outside of AgentCore
To enable observability for agents hosted outside of the AgentCore runtime, ﬁrst follow the steps
in the previous sections to enable CloudWatch Transaction Search and add the ADOT SDK to your
code.
If you host your agent on AWS Lambda, use the AWS Lambda Layer for OpenTelemetry on
the AWS Distro for OpenTelemetry website. Add the layer to your function, and then set the
AWS_LAMBDA_EXEC_WRAPPER environment variable to /opt/otel-instrument. The layer
then auto-instruments your function. With this approach, you don’t need to add the awsopentelemetry-distro package or run the opentelemetry-instrument command described
earlier.

ADOT Collector not supported for agent observability
The ADOT Collector is not supported for agent observability. To send telemetry from an
agent hosted outside of AgentCore runtime, you must use either the ADOT SDK or the AWS
Lambda Layer for OpenTelemetry.

For agents running outside of the AgentCore runtime, you also need to create an agent log-group
which you include in your environment variables.
Conﬁgure your AWS environment variables, and then set your Open Telemetry environment
variables as shown in the following.
AWS environment variables

Enabling observability for agents hosted outside of AgentCore

1892

AWS_ACCOUNT_ID=<account id>
AWS_DEFAULT_REGION=<default region>
AWS_REGION=<region>
AWS_ACCESS_KEY_ID=<access key id>
AWS_SECRET_ACCESS_KEY=<secret key>

OTEL environment variables
AGENT_OBSERVABILITY_ENABLED=true
AWS_GENAI_CONTENT_EXTRACTION_OPT_OUT=true # Keeps model payloads and tool request/
response data on spans. Requires ADOT >=0.18.0.
OTEL_PYTHON_DISTRO=aws_distro
OTEL_PYTHON_CONFIGURATOR=aws_configurator # required for ADOT Python only
OTEL_RESOURCE_ATTRIBUTES=service.name=<agent-name>,aws.log.group.names=/aws/bedrockagentcore/runtimes/<agent-id>,cloud.resource_id=<AgentEndpointArn:AgentEndpointName> #
endpoint is optional
OTEL_EXPORTER_OTLP_LOGS_HEADERS=x-aws-log-group=/aws/bedrock-agentcore/runtimes/<agentid>,x-aws-log-stream=runtime-logs,x-aws-metric-namespace=bedrock-agentcore
OTEL_EXPORTER_OTLP_TRACES_HEADERS=x-aws-log-group=/aws/bedrock-agentcore/runtimes/
<agent-id>,x-aws-log-stream=spans # (Optional) Directs spans to your log group instead
of the aws/spans log group. Requires ADOT version 0.18.0 or later.
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_TRACES_EXPORTER=otlp
OTEL_AWS_APPLICATION_SIGNALS_ENABLED=false # AWS Lambda Layer for OpenTelemetry only:
disables Application Signals
OTEL_LOGS_EXPORTER=otlp # AWS Lambda Layer for OpenTelemetry only: exports logs over
OTLP
OTEL_METRICS_EXPORTER=awsemf # AWS Lambda Layer for OpenTelemetry only: exports metrics
as CloudWatch EMF

Replace <agent-name> with your agent’s name and <agent-id> with a unique identiﬁer for your
agent.
Note
If you set OTEL_EXPORTER_OTLP_TRACES_HEADERS to deliver spans to your own log
group, you must also add an Amazon CloudWatch Logs resource policy. The policy must
allow X-Ray (xray.amazonaws.com) to call logs:PutLogEvents on that log group. Use
the same policy shown in Enabling CloudWatch Transaction Search, with your log group’s
ARN in Resource. Without this policy, X-Ray can’t deliver spans to your log group.

Enabling observability for agents hosted outside of AgentCore

1893

Note
(Optional) For Agent Frameworks other than Strands, LangChain, and CrewAI: You might
need to add an additional SDK and code to send Generative AI semantic conventions
telemetry and spans. AgentCore Observability, a capability of Amazon Bedrock AgentCore,
supports use of the following instrumentation libraries in your agent framework: *
OpenInference * Openllmetry * OpenLit * Traceloop

Session ID support
To propagate session ID, you need to invoke using session identiﬁer in the OTEL baggage:
from opentelemetry import baggage
ctx = baggage.set_baggage("session.id", session_id) # Set the session.id in baggage
attach(ctx) # Attach the context to make it active token

Enabling observability for AgentCore runtime, memory, gateway, builtin tools, and identity resources
When you create an AgentCore runtime resource (agent), by default, AgentCore runtime creates a
CloudWatch log group for the service-provided logs. However, for memory, gateway, and built-in
tool resources, AgentCore doesn’t conﬁgure log destinations for you automatically.
For memory and gateway resources, you can conﬁgure log destinations either in the console or by
using an AWS SDK. If you use the console to conﬁgure a CloudWatch Logs destination, the default
log group name for memory and gateway resources has the form /aws/vendedlogs/bedrockagentcore/{resource-type}/APPLICATION_LOGS/{resource-id} , where {resourcetype} is either memory or gateway.
For memory and gateway logs, you can also conﬁgure log destinations in Amazon S3 logs or
Firehose stream logs using the AgentCore console. To learn more about storing logs in Amazon S3
or Firehose, see Uploading, downloading, and working with objects in Amazon S3 and Creating an
Amazon Data Firehose delivery stream.
To learn more about the log data output by AgentCore for memory and gateway resources see
Provided log data (memory) or Provided log data (gateway).
Enabling observability for AgentCore runtime, memory, gateway, built-in tools, and identity resources

1894

For built-in tool resources, the AgentCore service doesn’t provide logs by default, but you can
output your own logs from your code. If you supply your own log outputs, you need to manually
conﬁgure log destinations to store this data.
To see what observability data AgentCore provides by default for each resource type, see Amazon
Bedrock AgentCore generated observability data.

Conﬁgure log destinations using the console
To conﬁgure log destinations for memory or gateway logs in the AgentCore console, use the
following procedures.
Example
Memory
1. ====== To conﬁgure log delivery for memory resources (console)
2. Open the Memory page in the AgentCore console.
3. In the Memory pane, select the memory you want to conﬁgure a log destination for.
4. Scroll down to the Log delivery pane and choose Add.
5. From the dropdown list, select the type of log destination you want to add (CloudWatch Logs
group, Amazon S3 bucket, or Amazon Data Firehose).
6. For Log type , select APPLICATION_LOGS.
7. For Amazon S3 and Firehose destinations, enter a Delivery destination ARN . For
CloudWatch Logs, the Destination log group is already populated with a default value.
8. (Optional) For CloudWatch Logs destinations, to change the default log group, enter a new
log group name or select an existing log group under Destination log group.
9. (Optional) To change the ﬁelds that are captured in each log record or the logs' output
format, expand Additional settings - optional , and modify the Field selection , Output
format , and Field delimiter to your desired conﬁguration.
10.Choose Add.
Gateway
1. ====== To conﬁgure log delivery for gateway resources (console)
2. Open the Gateways page in the AgentCore console.
Enabling observability for AgentCore runtime, memory, gateway, built-in tools, and identity resources

1895

3. In the Gateways pane, select the gateway you want to conﬁgure a log destination for.
4. Scroll down to the Log delivery pane and choose Add.
5. From the dropdown list, select the type of log destination you want to add (CloudWatch Logs
group, Amazon S3 bucket, or Amazon Data Firehose).
6. For Amazon S3 and Firehose destinations, enter a Delivery destination ARN . For
CloudWatch Logs, the Destination log group is already populated with a default value.
7. (Optional) For CloudWatch Logs destinations, to change the default log group, enter a new
log group name or select an existing log group under Destination log group.
8. (Optional) To change the ﬁelds that are captured in each log record or the logs' output
format, expand Additional settings - optional , and modify the Field selection , Output
format , and Field delimiter to your desired conﬁguration.
9. Choose Add.
Runtime
1. ====== To conﬁgure log delivery for agent runtime resources (console)
2. Open the Agent Runtime page in the AgentCore console.
3. In the Runtime agents pane, select the runtime agent for which you want to conﬁgure a log
destination.
4. Scroll down to the Log delivery pane and from the Add drop-down, choose the Logging
destination - either Amazon CloudWatch Logs, Amazon S3, or Amazon Data Firehose.
5. Conﬁgure the following log delivery details and then choose Add :
• For Log type , choose APPLICATION_LOGS.
• If using Amazon CloudWatch Logs as the logging destination, specify the destination log
group.
• If using Amazon S3 as the logging destination, specify the destination Amazon S3 bucket.
• If using Amazon Data Firehose as the logging destination, specify a destination delivery
stream.
6. Verify that the log delivery status is set to Delivery active.
Built-in tools
1. ====== To conﬁgure log delivery for built-in tools resources (console)
Enabling observability for AgentCore runtime, memory, gateway, built-in tools, and identity resources

1896

2. Open the Built-in tools page in the AgentCore console.
3. In the Built-in tools pane, either in the Code interpreter tools or the Browser tools tab,
select the code interpreter tool or browser tool for which you want to conﬁgure a log
destination.
4. Scroll down to the Log delivery pane and from the Add drop-down, choose the Logging
destination - either Amazon CloudWatch Logs, Amazon S3, or Amazon Data Firehose.
5. Conﬁgure the following log delivery details and then choose Add :
• For Log type , choose APPLICATION_LOGS.
• If using Amazon CloudWatch Logs as the logging destination, specify the destination log
group.
• If using Amazon S3 as the logging destination, specify the destination Amazon S3 bucket.
• If using Amazon Data Firehose as the logging destination, specify a destination delivery
stream.
6. Verify that the log delivery status is set to Delivery active.
Identity
1. WorkloadIdentity log delivery enablement is handled at the associated resource level,
including agent runtime or agent gateway resources.
To conﬁgure WorkloadIdentity log delivery for associated resources (console)
2. Open either the Gateway or the Agent Runtime page in the AgentCore console and select an
agent or a gateway for which you want to enable WorkloadIdentity logging.
3. In the Identity tab, scroll down to the Log delivery pane and from the Add drop-down,
choose the Logging destination - either Amazon CloudWatch Logs, Amazon S3, or Amazon
Data Firehose.
4. Conﬁgure the following log delivery details and then choose Add :
• For Log type , choose APPLICATION_LOGS.
• If using Amazon CloudWatch Logs as the logging destination, specify the destination log
group.
• If using Amazon S3 as the logging destination, specify the destination Amazon S3 bucket.
• If using Amazon Data Firehose as the logging destination, specify a destination delivery
stream.
5. Verify that the log delivery status is set to Delivery active.
Enabling observability for AgentCore runtime, memory, gateway, built-in tools, and identity resources

1897

Conﬁgure tracing delivery to CloudWatch using the console
This section describes how to enable trace delivery to CloudWatch to track the ﬂow of interactions
through your application allowing you to visualize requests, identify performance bottlenecks,
troubleshoot errors, and optimize performance.
Example
Memory
1. ====== To conﬁgure tracing for memory resources (console)
2. Open the Memory page in the AgentCore console.
3. In the Memory pane, select the memory resource for which you want to enable tracing.
4. In the Tracing pane, choose Edit , toggle the widget to Enable , and then choose Save.
Runtime
1. ====== To conﬁgure tracing for runtime resources (console)
2. Open the Agents runtime page in the AgentCore console.
3. In the Runtime agents pane, select the agent for which you want to enable tracing.
4. In the Tracing pane, choose Edit , toggle the widget to Enable , and then choose Save.
AgentCore enables tracing for the selected agent. Spans appear in the agent’s log group (/
aws/bedrock-agentcore/runtimes/<agent_id>-<endpoint_name>), or in the aws/
spans log group for agents that use the shared span destination. For more information, see
Span destination for agents hosted in Amazon Bedrock AgentCore runtime.
To conﬁgure WorkloadIdentity tracing for runtime resources (console)
5. Open the Agents runtime page in the AgentCore console.
6. In the Runtime agents pane, choose the Identity tab, and then select the agent for which
you want to enable WorkloadIdentity tracing.
7. In the Tracing pane, choose Edit , toggle the widget to Enable , and then choose Save.
WorkloadIdentity tracing will be enabled for the selected agent and spans will be available in
the aws/spans log group.
Enabling observability for AgentCore runtime, memory, gateway, built-in tools, and identity resources

1898

Built-in tools
1. ====== To conﬁgure tracing for built-in tools (console)
2. Open the Built-in tools page in the AgentCore console.
3. In the Built-in tools pane, either in the Code interpreter tools or the Browser tools tab,
select the code interpreter tool or browser tool for which you want to enable tracing.
4. In the Tracing pane, choose Edit , toggle the widget to Enable , and then choose Save.
Tracing will be enabled for the selected code interpreter or browser tool and spans will be
available in the aws/spans log group.
Gateway
1. ====== To conﬁgure tracing for gateway resources (console)
2. Open the Gateways page in the AgentCore console.
3. In the Gateways pane, select the gateway for which you want to enable tracing.
4. In the Tracing pane, choose Edit , toggle the widget to Enable , and then choose Save.
Tracing will be enabled for the selected gateway and spans will be available in the aws/
spans log group.
To conﬁgure WorkloadIdentity tracing for gateway resources (console)
5. Open the Gateways page in the AgentCore console.
6. In the Gateways pane, choose the Identity tab, and then select the gateway for which you
want to enable WorkloadIdentity tracing.
7. In the Tracing pane, choose Edit , toggle the widget to Enable , and then choose Save.
WorkloadIdentity tracing will be enabled for the selected gateway and spans will be available
in the aws/spans log group.

Note
You must have CloudWatch Transaction Search enabled before you can enable
tracing.

Enabling observability for AgentCore runtime, memory, gateway, built-in tools, and identity resources

1899

Identity
1. ====== To conﬁgure tracing for identity resources (console)
2. Open the Identity page in the AgentCore console.
3. In the Identity pane, select the OAuth client or the API key for which you want to enable
tracing.
4. In the Tracing pane, choose Edit , toggle the widget to Enable , and then choose Save.

Conﬁgure CloudWatch resources using an AWS SDK
To conﬁgure a delivery source for logs and traces (SDK)
• Run the following Python code to conﬁgure CloudWatch for your memory, gateway, and builtin tool resources. Note that delivery sources and destinations for tracing are only applicable for
memory and gateway resources.

import boto3
def enable_observability_for_resource(resource_arn, resource_id, account_id,
region='us-east-1'):
"""
Enable observability for a Bedrock AgentCore resource (e.g., Memory Store)
"""
logs_client = boto3.client('logs', region_name=region)
# Step 0: Create new log group for vended log delivery
log_group_name = f'/aws/vendedlogs/bedrock-agentcore/{resource_id}'
logs_client.create_log_group(logGroupName=log_group_name)
log_group_arn = f'arn:aws:logs:{region}:{account_id}:log-group:{log_group_name}'
# Step 1: Create delivery source for logs
logs_source_response = logs_client.put_delivery_source(
name=f"{resource_id}-logs-source",
logType="APPLICATION_LOGS",
resourceArn=resource_arn
)
# Step 2: Create delivery source for traces
traces_source_response = logs_client.put_delivery_source(
name=f"{resource_id}-traces-source",
Enabling observability for AgentCore runtime, memory, gateway, built-in tools, and identity resources

1900

logType="TRACES",
resourceArn=resource_arn
)
# Step 3: Create delivery destinations
logs_destination_response = logs_client.put_delivery_destination(
name=f"{resource_id}-logs-destination",
deliveryDestinationType='CWL',
deliveryDestinationConfiguration={
'destinationResourceArn': log_group_arn,
}
)
# Traces required
traces_destination_response = logs_client.put_delivery_destination(
name=f"{resource_id}-traces-destination",
deliveryDestinationType='XRAY'
)
# Step 4: Create deliveries (connect sources to destinations)
logs_delivery = logs_client.create_delivery(
deliverySourceName=logs_source_response['deliverySource']['name'],
deliveryDestinationArn=logs_destination_response['deliveryDestination']['arn']
)
# Traces required
traces_delivery = logs_client.create_delivery(
deliverySourceName=traces_source_response['deliverySource']['name'],
deliveryDestinationArn=traces_destination_response['deliveryDestination']
['arn']
)
print(f"Observability enabled for {resource_id}")
return {
'logs_delivery_id': logs_delivery['id'],
'traces_delivery_id': traces_delivery['id']
}
# Usage example
resource_arn = "arn:aws:bedrock-agentcore:us-east-1:123456789012:memory/my-memory-id"
resource_id = "my-memory-id"
account_id = "123456789012"

Enabling observability for AgentCore runtime, memory, gateway, built-in tools, and identity resources

1901

delivery_ids = enable_observability_for_resource(resource_arn, resource_id, account_id)

Enhanced AgentCore runtime observability with custom headers
You can invoke your agent with additional HTTP headers to provide enhanced observability
options. The following example shows invocations including optional additional header requests
for agents hosted in the AgentCore runtime.
Example Boto3 invocation
def invoke_agent(agent_id, payload, session_id=None):
client = boto3.client("bedrock-agentcore", region="us-west-2")
response = client.invoke_agent_runtime(
agentRuntimeArn="arn:aws:bedrock-agentcore:us-west-2:111122223333:runtime/
test_agent_boto2-nIg2xk3VSR",
runtimeSessionId="12345678-1234-5678-9abc-123456789012",
payload='{"query": "Plan a weekend in Seattle"}',
)

You can include the following optional headers when invoking your agent to enhance observability
and tracing capabilities:
Header

Description

Sample Value

Technical Explanati
on

X-Amzn-Trace-Id

Trace ID for request
tracking (X-Ray
Format)

Root=1-5759e988bd862e3fe1b
e46a994272793;Pare
nt=53995c3f42cd8ad
8;Sampled=1

Used for distributed
tracing across AWS
services. Contains
root ID (request
origin), parent ID
(previous service),
and sampling
decision for tracing.
Sampling=1 means
100% sampling.
Parent is X-Ray
Trace format as well.
OTEL will auto-gene

Enhanced AgentCore runtime observability with custom headers

1902

Amazon Bedrock AgentCore

Header

Developer Guide

Description

Sample Value

Technical Explanati
on
rate trace IDs if not
supplied.

traceparent

W3C standard tracing
header

00-4bf92f3577b34da
6a3ce929d
0e0e4736-00f067aa0
ba902b7-01

W3C format that
includes version,
trace ID, parent ID,
and ﬂags. Required
for cross-service trace
correlation when
using modern tracing
systems.

X-Amzn-Bedrock-Age
ntCore-Runtime-Ses
sion-Id

AgentCore session
identiﬁer

a1b2c3d4-5678-90ab
-cdef-EXAMPLEaaaaa

Identiﬁes a user
session within the
AgentCore system.
Helps with sessionbased analytics and
troubleshooting.

mcp-session-id

MCP session identiﬁer

mcp-a1b2c
3d4-5678-90ab-cdefEXAMPLEaaaaa

Identiﬁes a session in
the Managed Cloud
Platform. Enables
tracing of operation
s across the MCP
ecosystem.

tracestate

Additional tracing
state information

congo=t61rcWkgMzE,
rojo=00f067aa0ba90
2b7

Vendor-speciﬁc
tracing information.
Conveys additional
context for tracing
systems beyond
what’s in traceparent.

Enhanced AgentCore runtime observability with custom headers

1903

Header

Description

Sample Value

Technical Explanati
on

baggage

Context propagati
on for distributed
tracing

userId=alice,serve
rRegion=us-east-1

Key-value pairs that
propagate user-deﬁ
ned properties across
service boundarie
s for contextual
logging and analysis.

Enhanced AgentCore built-in tools observability with custom headers
You can invoke your Built-in Tools with additional HTTP headers to provide enhanced observability
options. You can include the following optional headers when integrating following Build-in Tools
APIs to enhance observability and tracing capabilities:
The following APIs support custom headers:
• StartCodeInterpreterSession
• InvokeCodeInterpreter
• StopCodeInterpreterSession
• StartBrowserSession
• StopBrowserSession

Header

Description

Sample Value

Technical Explanati
on

X-Amzn-Trace-Id

Trace ID for request
tracking (X-Ray
Format)

Root=1-5759e988bd862e3fe1b
e46a994272793;Pare
nt=53995c3f42cd8ad
8;Sampled=1

Used for distributed
tracing across AWS
services. Contains
root ID (request
origin), parent ID
(previous service),
and sampling
decision for tracing.

Enhanced AgentCore built-in tools observability with custom headers

1904

Amazon Bedrock AgentCore

Header

Developer Guide

Description

Sample Value

Technical Explanati
on
Sampling=1 means
100% sampling.
Parent is X-Ray
Trace format as well.
OTEL will auto-gene
rate trace IDs if not
supplied.

traceparent

W3C standard tracing
header

00-4bf92f3577b34da
6a3ce929d
0e0e4736-00f067aa0
ba902b7-01

W3C format that
includes version,
trace ID, parent ID,
and ﬂags. Required
for cross-service trace
correlation when
using modern tracing
systems.

Enhanced AgentCore identity observability with custom headers
You can invoke your identity resources with additional HTTP headers to provide enhanced
observability options. You can include the following optional headers when integrating following
identity APIs to enhance observability and tracing capabilities:
The following APIs support custom headers:
• GetWorkloadAccessToken
• GetWorkloadAccessTokenForJWT
• GetWorkloadAccessTokenForUserId
• GetResourceOauth2Token
• GetResourceAPIKey

Enhanced AgentCore identity observability with custom headers

1905

Header

Description

Sample Value

Technical Explanati
on

X-Amzn-Trace-Id

Trace ID for request
tracking (X-Ray
Format)

Root=1-5759e988bd862e3fe1b
e46a994272793;Pare
nt=53995c3f42cd8ad
8;Sampled=1

Used for distributed
tracing across AWS
services. Contains
root ID (request
origin), parent ID
(previous service),
and sampling
decision for tracing.
Sampling=1 means
100% sampling.
Parent is X-Ray
Trace format as well.
OTEL will auto-gene
rate trace IDs if not
supplied.

Observability best practices
Consider the following best practices when implementing observability for agents in AgentCore:
• Use consistent session IDs - When possible, reuse the same session ID for related requests to
maintain context across interactions.
• Implement distributed tracing - Use the provided headers to enable end-to-end tracing across
your application components.
• Add custom attributes - Enhance your traces and metrics with custom attributes that provide
additional context for troubleshooting and analysis.
• Monitor resource usage - Pay attention to memory usage metrics to optimize your agent’s
performance.
• Set up alerts - Conﬁgure CloudWatch alarms to help notify you of potential issues before they
impact your users.

Observability best practices

1906

Using other observability platforms
To integrate agents hosted in the AgentCore runtime with other observability platforms to capture
and view telemetry outputs, set the following environment variable:
DISABLE_ADOT_OBSERVABILITY=true

Setting this variable to true unsets the AgentCore runtime’s default ADOT environment variables,
ensuring that none of the default ADOT conﬁgurations are set.

Understand observability for agentic resources in AgentCore
This section deﬁnes the concepts of sessions, traces and spans as they relate to monitoring and
observability of agents.
Topics
• Sessions
• Traces
• Spans
• Relationship Between Sessions, Traces, and Spans

Sessions
A session represents a complete interaction context between a user and an agent. Sessions
encapsulate the entire conversation or interaction ﬂow, maintaining state and context across
multiple exchanges. Each session has a unique identiﬁer and captures the full lifecycle of user
engagement with the agent, from initialization to termination.
Sessions provide the following capabilities for agents:
• Context persistence across multiple interactions within the same conversation
• State management for maintaining user-speciﬁc information
• Conversation history tracking for contextual understanding
• Resource allocation and management for the duration of the interaction
• Isolation between diﬀerent user interactions with the same agent
Using other observability platforms

1907

From an observability perspective, sessions provide a high-level view of user engagement patterns,
allowing you to monitor agent performance across metrics, traces, and spans and to understand
how users interact with your agents over time and across diﬀerent use cases.
By default, AgentCore provides a set of observability metrics at the session level for agents
that are running in the AgentCore runtime. You can view the runtime metrics in the Amazon
CloudWatch console on the generative AI observability page. This page oﬀers a variety of graphs
and visualizations to help you interpret your agents' data. AgentCore also outputs a default set
of metrics for memory resources, gateway resources, and built-in tools. All of these metrics can
be viewed in CloudWatch. In addition to the provided metrics, logs and spans are provided by
default for memory resources, and by instrumenting your agent code, you can capture custom
metrics, logs, and spans for your agent which can also be viewed on the CloudWatch generative
AI observability page. See the following sections and View observability data for your Amazon
Bedrock AgentCore agents to learn more.

Traces
A trace represents a detailed record of a single request-response cycle beginning from with an
agent invocation and may include additional calls to other agents. Traces capture the complete
execution path of a request, including all internal processing steps, external service calls, decision
points, and resource utilization. Each trace is associated with a speciﬁc session and provides
granular visibility into the agent’s behavior for a particular interaction.
Traces include the following components for agents:
• Request details including timestamps, input parameters, and context
• Processing steps showing the sequence of operations performed
• Tool invocations with input/output parameters and execution times
• Resource utilization metrics such as processing time
• Error information including exception details and recovery attempts
• Response generation details and ﬁnal output
From an observability perspective, traces provide deep insights into the internal workings of your
agents, allowing you to troubleshoot issues, optimize performance, and understand behavior
patterns. By analyzing trace data, you can identify bottlenecks, detect anomalies, and verify that
your agent is functioning as expected across diﬀerent scenarios and inputs.
Traces

1908

To gather trace data, you need to instrument your agent code using the AWS Distro for Open
Telemetry (ADOT). See Enabling observability in agent code for AgentCore-hosted agents and
Enabling observability for agents hosted outside of AgentCore to learn more.

Spans
A span represents a discrete, measurable unit of work within an agent’s execution ﬂow. Spans
capture ﬁne-grained operations that occur during request processing, providing detailed visibility
into the internal components and steps that make up a complete trace. Each span has a deﬁned
start and end time, creating a precise timeline of agent activities and their durations.
Spans include the following essential attributes for agent observability:
• Operation name identifying the speciﬁc function or process being executed
• Timestamps marking the exact start and end times of the operation
• Parent-child relationships showing how operations nest within larger processes
• Tags and attributes providing contextual metadata about the operation
• Events marking signiﬁcant occurrences within the span’s lifetime
• Status information indicating success, failure, or other completion states
• Resource utilization metrics speciﬁc to the operation
Spans form a hierarchical structure within traces, with parent spans encompassing child spans that
represent more granular operations. For example, a high-level "process user query" span might
contain child spans for "parse input," "retrieve context," "generate response," and "format output."
This hierarchical organization creates a detailed execution tree that reveals the complete ﬂow of
operations within the agent.
By default, AgentCore outputs a set of span data for memory resources only. This data can be
viewed in CloudWatch Logs and CloudWatch Application signals. To record span data for your
agents or gateway resources, you need to instrument your agent. See Enabling observability in
agent code for AgentCore-hosted agents and Enabling observability for agents hosted outside of
AgentCore to learn more.

Relationship Between Sessions, Traces, and Spans
Sessions, traces, and spans form a three-tiered hierarchical relationship in the observability
framework for agents. A session contains multiple traces, with each trace representing a discrete
Spans

1909

interaction within the broader context of the session. Each trace, in turn, contains multiple spans
that capture the ﬁne-grained operations and steps within that interaction. This hierarchical
structure allows you to analyze agent behavior at diﬀerent levels of granularity, from high-level
session patterns to mid-level interaction ﬂows to detailed execution paths for speciﬁc operations.
The relationship between these three observability components can be visualized as:
• Sessions (highest level) - Represent complete user conversations or interaction contexts
• Traces (middle level) - Represent individual request-response cycles within a session
• Spans (lowest level) - Represent speciﬁc operations or steps within a trace
This multi-tiered relationship enables several important observability capabilities:
• Contextual analysis of individual interactions within their broader conversation ﬂow
• Correlation of related requests across a user’s interaction journey
• Progressive troubleshooting from session-level anomalies to trace-level patterns to span-level
root causes
• Comprehensive performance proﬁling across diﬀerent temporal and functional dimensions
• Holistic understanding of agent behavior patterns and evolution throughout a conversation
• Precise identiﬁcation of performance bottlenecks at the operation level through span analysis
While traces provide visibility into complete request-response cycles, spans oﬀer deeper insights
into the internal workings of those cycles. Spans reveal exactly which operations consume the
most time, where errors originate, and how diﬀerent components interact within a single trace.
This granularity is particularly valuable when troubleshooting complex issues or optimizing
performance in sophisticated agent implementations.
By leveraging session, trace, and span data in your observability strategy, you can gain
comprehensive insights into your agent’s behavior, performance, and eﬀectiveness at multiple
levels of detail. This multi-layered approach to observability supports continuous improvement,
robust troubleshooting, and informed optimization of your agent implementations, from highlevel conversation patterns down to individual operation performance.

Relationship Between Sessions, Traces, and Spans

1910


## Runtime observability data (pp. 1911–1919)

Amazon Bedrock AgentCore generated observability data
For agents running in the AgentCore runtime, AgentCore automatically generates a set of session
metrics which you can view in the Amazon CloudWatch Logs generative AI observability page. You
can also use AgentCore observability to monitor the performance of memory, gateway, and builtin tool resources, even if you’re not using the AgentCore runtime to host your agents. For memory,
gateway, and built-in tool resources, AgentCore outputs a default set of data to CloudWatch.
The following table summarizes the default data provided for each resource type, and where the
data is available.

Resource type

Service-provided
data

Available in Amazon
CloudWatch gen AI
observability

Available in
CloudWatch (Logs or
metrics)

Agent

Metrics, Spans*, Logs*

Yes

Yes

Memory

Metrics, Spans*, Logs*

Yes

Yes

Payments

Metrics, Spans, Logs

Yes

Yes

Gateway

Metrics, Spans, Logs*

Yes

Yes

Tools

Metrics, Spans*, Logs*

Yes

Yes

Policy

Metrics, Spans*, Logs

Yes

Yes

• Signals marked with an asterisk require explicit enablement. Metrics are provided by default for
all resource types. See Add observability to your Amazon Bedrock AgentCore resources to learn
more.
Policy related observability is displayed under the AgentCore Gateway tab in CloudWatch gen AI
observability.

AgentCore generated observability data

1911

Note
To view metrics, spans, and traces for AgentCore, you need to perform a one-time setup
process to enable CloudWatch Transaction Search. To learn more see Enabling AgentCore
observability.

Refer to the following topics to learn about the default service-provided observability metrics for
AgentCore runtime, memory, and gateway resources.
By instrumenting your agent code, you can also gather more detailed trace and span data as well
as custom metrics. See Enabling observability in agent code for AgentCore-hosted agents to learn
more.
Topics
• AgentCore generated runtime observability data
• AgentCore generate memory observability data
• AgentCore generated payments observability data
• AgentCore generated gateway observability data
• AgentCore generated built-in tools observability data
• AgentCore generated identity observability data
• AgentCore generated Policy in AgentCore observability data

AgentCore generated runtime observability data
The runtime metrics provided by AgentCore give you visibility into your agent execution activity
levels, processing latency, resource utilization, and error rates. AgentCore also provides aggregated
metrics for total invocations and sessions.
Topics
• Observability runtime metrics
• Resource usage metrics and logs
• Provided span data
• Application log data
Runtime observability data

1912

• Error types

Observability runtime metrics
The following list describes the runtime metrics provided by AgentCore. Runtime metrics
are batched at one minute intervals. To learn more about viewing runtime metrics, see View
observability data for your Amazon Bedrock AgentCore agents.
Invocations
Shows the total number of requests made to the Data Plane API. Each API call counts as one
invocation, regardless of the request payload size or response status.
Invocations (aggregated)
Shows the total number of invocations across all resources
Throttles
Displays the number of requests throttled by the service due to exceeding allowed TPS
(Transactions Per Second) or quota limits. These requests return ThrottlingException with HTTP
status code 429. Monitor this metric to determine if you need to review your service quotas or
optimize request patterns.
System Errors
Shows the number of server-side errors encountered by AgentCore during request processing.
High levels of server-side errors can indicate potential infrastructure or service issues that
require investigation. See Error types for a list of possible error codes.
User Errors
Represents the number of client-side errors resulting from invalid requests. These require user
action to resolve. High levels of client-side errors can indicate issues with request formatting or
permissions that need to be addressed. See Error types for a list of possible error codes.
Latency
The total time elapsed between receiving the request and sending the ﬁnal response token.
Represents complete end-to-end processing time of the request.
Total Errors
The total number of system and user errors. In the Amazon Bedrock AgentCore console, this
metric displays the number of errors as a percentage of the total number of invocations.
Runtime observability data

1913

Session Count
Shows the number of new agent sessions created within the reporting period. Each session is
counted once at creation time; subsequent invocations to the same session do not increment
this metric. This is a cumulative counter, not a gauge of currently active sessions. Useful for
monitoring overall platform usage, trending session creation rates, and understanding user
engagement patterns.
Sessions (aggregated)
Shows the total number of new sessions created across all resources within the reporting
period.
ActiveSessionCount
Shows the number of currently active sessions for your account. Unlike the SessionCount
metric (a cumulative counter), this metric is a real-time gauge showing how many sessions
are running at any given moment. Amazon Bedrock AgentCore publishes this metric once per
minute per service type. Use it to monitor current capacity utilization, set alarms for unexpected
usage spikes, and understand your session quota consumption. Use the Service dimension —
with values AgentCore.Runtime, AgentCore.CodeInterpreter, or AgentCore.Browser
— to ﬁlter this metric by workload type. Amazon Bedrock AgentCore publishes this metric
directly to your AWS account in the AWS/Bedrock-AgentCore namespace.
ActiveStreamingConnections
(WebSocket only) Shows the current number of active WebSocket connections per agent.
Monitor this metric to understand connection usage and detect connection drops or spikes for
capacity planning. The only meaningful statistic is a 1-minute sum.
InboundStreamingBytesProcessed
(WebSocket only) Displays the total number of bytes successfully processed in WebSocket
frames received from clients to agent containers. Use this metric to monitor data throughput
and identify usage patterns.
OutboundStreamingBytesProcessed
(WebSocket only) Shows the total number of bytes successfully processed in WebSocket
frames sent from agent containers to clients. Monitor this metric to understand agent response
patterns and ensure successful data transmission.
Runtime observability data

1914

Resource usage metrics and logs
Amazon Bedrock AgentCore runtime provides comprehensive resource usage telemetry, including
CPU and memory consumption metrics for your runtime resources.
Note
Resource usage data may be delayed by up to 60 minutes and precision might diﬀer across
metrics.

Vended metrics
Amazon Bedrock AgentCore runtime automatically provides resource usage metrics at account,
agent runtime, and agent endpoint levels. These metrics are published at 1-minute resolution.
Amazon CloudWatch aggregation and metric data retention will follow standard Amazon
CloudWatch data retention polices. For more information, see https://docs.aws.amazon.com/
AmazonCloudWatch/latest/monitoring/cloudwatch_concepts.html#Metric.
Here are the dimension sets and metrics available for monitoring your resources:
Name

Dimensions

Description

CPUUsed-vCPUHours

Service; Service, Resource;
Service, Resource, Name

The total amount of virtual
CPU consumed in vCPU-Hours
unit, available at the resource
and account levels. Useful
for resource tracking and
estimated billing visibility.

MemoryUsed-GBHours

Service; Service, Resource;
Service, Resource, Name

The total amount of memory
consumed in GB-Hours unit,
available at the resource
and account levels. Useful
for resource tracking and
estimated billing visibility.

Dimension explanation
Runtime observability data

1915

• Service - AgentCore.Runtime
• Resource - Agent Arn
• Name - Agent Endpoint name, in the format of AgentName::EndpointName
Account level metrics are available in Amazon CloudWatch Bedrock AgentCore Observability
Console under the Runtime tab. The dashboard displays Memory and CPU usage graphs generated
from these metrics, representing total resource usage across all agents in your account within the
region.
Agent Endpoint level metrics are available in AgentEndpoint page of Amazon CloudWatch
Bedrock AgentCore Observability Console. The dashboard displays Memory and CPU usage graphs
generated from these metrics, representing total resource usage across all sessions invoked by the
speciﬁed Agent Endpoint.
Note
Telemetry data is provided for monitoring purposes. Actual billing is calculated based
on metered usage data and may diﬀer from telemetry values due to aggregation timing,
reconciliation processes, and measurement precision. Refer to your AWS billing statement
for authoritative charges.

Vended logs
Bedrock AgentCore Runtime provides vended logs for session-level usage metrics
at 1-second granularity. Each log record contains resource consumption data
including CPU usage (agent.runtime.vcpu.hours.used) and memory consumption
(agent.runtime.memory.gb_hours.used).
Each log record will have following schema:
Log type

Log ﬁelds

Description

USAGE_LOGS

event_timestamp, resource_
arn, service.name, cloud.pro
vider, cloud.region, account.i
d, region, resource.id,

Resource Usage Logs for
session-level resource
tracking.

Runtime observability data

1916

Amazon Bedrock AgentCore

Log type

Developer Guide

Log ﬁelds

Description

session.id, agent.name,
elapsed_time_seconds,
agent.runtime.vcpu.hours.us
ed, agent.runtime.memo
ry.gb_hours.used

To enable USAGE_LOG log type for your agents, see Add observability to your Amazon Bedrock
AgentCore resources . The logs are then displayed in the conﬁgured destination (AWS LogGroup,
Amazon S3 or Amazon Kinesis Firehose) as conﬁgured.
In the Agent Session page of the Amazon CloudWatch Bedrock AgentCore Observability Console,
you can see resource usage metrics generated from these logs. To optimize your metric viewing
experience, select your desired time range using the selector in the top right to focus on speciﬁc
CPU and Memory Usage data.

Note
Telemetry data is provided for monitoring purposes. Actual billing is calculated based
on metered usage data and may diﬀer from telemetry values due to aggregation timing,
reconciliation processes, and measurement precision. Refer to your AWS billing statement
for authoritative charges.

Provided span data
To enhance observability, AgentCore provides structured spans that provide visibility into agent
runtime invocations. To enable this span data, you need to enable observability on your agent
resource. See Add observability to your Amazon Bedrock AgentCore resources for steps and details.
This span data is available in Amazon CloudWatch Logs. Spans appear in the agent’s log group
(/aws/bedrock-agentcore/runtimes/<agent_id>-<endpoint_name>), or in the aws/
spans log group for agents that use the shared span destination. For more information, see Span
destination for agents hosted in Amazon Bedrock AgentCore runtime. The following table deﬁnes
the operation for which spans are created and the attributes for each captured span.

Runtime observability data

1917

Operation name

Span attributes

Description

InvokeAgentRuntime

aws.operation.name,
aws.resource.arn, aws.reque
st_id, aws.agent.id, aws.endpo
int.name, aws.account.id,
session.id, latency_ms,
error_type, aws.resource.type,
aws.xray.origin, aws.region

Invokes the agent runtime.

• aws.operation.name - the operation name (InvokeAgentRuntime)
• aws.resource.arn - the Amazon resource name for the agent runtime
• aws.request_id - request ID for the invocation
• aws.agent.id - the unique identiﬁer for the agent runtime
• aws.endpoint.name - the name of the endpoint used to invoke the agent runtime
• aws.account.id - customer’s account id
• session.id - the session ID for the invocation
• latency_ms - the latency of the request in milliseconds
• error_type - either throttle, system, or user (only present if error)
• aws.resource.type - the CFN resource type
• aws.xray.origin - the CFN resource type used by x-ray to identify the service
• aws.region - the region the customer resource exists in

Application log data
AgentCore provides structured Application logs that help you gain visibility into your agent
runtime invocations and session-level resource consumption. This log data is provided when
enabling observability on your agent resource. See Add observability to your Amazon Bedrock
AgentCore resources for steps and details. AgentCore can output logs to CloudWatch Logs, Amazon
S3, or Firehose stream. If you use a CloudWatch Logs destination, these logs are stored under your
agent’s application logs or under your own custom log group.

Runtime observability data

1918

Log type

Log ﬁelds

Description

APPLICATION_LOGS

timestamp, resource_arn,
event_timestamp, account_i
d, request_id, session_id,
trace_id, span_id, service_n
ame, operation, request_p
ayload, response_payload

Application logs for
InvokeRuntimeOperation with
tracing ﬁelds, request, and
response payloads

• request_payload - the request payload of the agent invocation
• response_payload - the response from the agent invocation

Error types
The following list deﬁnes the possible error types for user, system, and throttling errors.
User error codes
• InvocationError.Validation - Client provided invalid input (400)
• InvocationError.ResourceNotFound - Requested resource doesn’t exist (404)
• InvocationError.AccessDenied - Client lacks permissions (403)
• InvocationError.Conflict - Resource conﬂict (409)
System error codes
• InvocationError.Internal - Internal server error (500)
Throttling error codes
• InvocationError.Throttling - Rate limiting (429)
• InvocationError.ServiceQuota - Service-side quota/limit reached (402)

Runtime observability data

1919


## Memory observability data (pp. 1920–1922)

AgentCore generate memory observability data
For the AgentCore memory resource type, AgentCore outputs metrics to Amazon CloudWatch by
default. AgentCore also outputs a default set of spans and logs, if you enable these. See Enabling
observability for AgentCore runtime, memory, gateway, built-in tools, and identity resources to
learn more about enabling spans and logs.
Refer to the following sections to learn more about the provided observability data for your agent
memory stores.

Provided memory metrics
The AgentCore memory resource type provides the following metrics by default.
Latency
The total time elapsed between receiving the request and sending the ﬁnal response token.
Represents complete end-to-end processing of the request.
Invocations
The total number of API requests made to the data plane and control plane. This metric also
tracks the number of memory ingestion events.
System Errors
Number of invocations that result in AWS server-side errors.
User Errors
Number of invocations that result in client-side errors.
Errors
Total number of errors that occur while processing API requests in the data plane and control
plane. This metric also tracks the total errors that occur during memory ingestion.
Throttles
Number of invocations that the system throttled. Throttled requests count as invocations,
errors, and user errors.
Creation Count
Counts the number of created memory events and memory records.
Memory observability data

1920

Provided span data
To enhance observability, AgentCore provides structured spans that trace the relationship between
events and the memories they generate or access. To enable this span data, you need to instrument
your agent code. See Add observability to your Amazon Bedrock AgentCore resources to learn
more.
This span data is available in full in CloudWatch Logs and CloudWatch Application Signals. To
learn more about viewing observability data, see View observability data for your Amazon Bedrock
AgentCore agents.
The following table deﬁnes the operations for which spans are created and the attributes for each
captured span.

Operation name

Span attributes

Description

CreateEvent

memory.id , session.i

Creates a new event within a
memory session

d , event.id , actor.id ,
throttled , error , fault
GetEvent

memory.id , session.i
d , event.id , actor.id ,

Retrieves an existing memory
event

throttled , error , fault
ListEvents

memory.id , session.i

Lists events within a session

d , event.id , actor.id ,
throttled , error , fault
DeleteEvent

memory.id , session.i
d , event.id , actor.id ,

Deletes an event from
memory

throttled , error , fault
RetrieveMemoryRecords

memory.id , namespace ,
throttled , error , fault

ListMemoryRecords

memory.id , namespace ,
throttled , error , fault

Memory observability data

Retrieves memory records for
a given namespace
Lists available memory
records

1921

Provided log data
AgentCore provides structured logs that help you monitor and troubleshoot key AgentCore
Memory resource processes. To enable this log data, you need to instrument your agent code. See
Add observability to your Amazon Bedrock AgentCore resources to learn more.
AgentCore can output logs to CloudWatch Logs, Amazon S3, or Firehose stream. If you use
a CloudWatch Logs destination, these logs are stored under the default log group /aws/
vendedlogs/bedrock-agentcore/memory/APPLICATION_LOGS/{memory_id} or under a
custom log group starting with /aws/vendedlogs/ . See Enabling observability for AgentCore
runtime, memory, gateway, built-in tools, and identity resources to learn more.
When the DeleteMemory operation is called, logs are generated for the start and completion of
the deletion process. Any corresponding deletion error logs will be provided with insights into why
the call failed.
We also provide logs for various stages in the long-term memory creation process, namely
extraction and consolidation. When new short term memory events are provided, AgentCore
extracts key concepts from responses to begin the formation of new long-term memory records.
Once these have been created, they are integrated with existing memory records to create a uniﬁed
store of distinct memories.
See the following breakdown to learn how each workﬂow helps you monitor the formation of new
memories:
Extraction logs
• Start and completion of extraction processing
• Number of memories successfully extracted
• Any errors in deserializing or processing input events
Consolidation logs:
• Start and completion of consolidation processing
• Number of memories requiring consolidation
• Success/failure of memory additions and updates
• Related memory retrieval status
Memory observability data

1922


## Gateway observability data (pp. 1926–1932)

Metric

Unit

Description

ActiveSessions

Count

Number of active payment
sessions

PaymentRequestCount

Count

Total payment requests

PaymentSuccessCount

Count

Successful payment transacti
ons

PaymentFailureCount

Count

Failed payment transactions

PaymentLatency

Milliseconds

Payment processing latency

Metrics are published with the following dimensions: Operation, PaymentManagerId,
PaymentConnectorId, AgentName, Currency (for SpendAmount).

AgentCore generated gateway observability data
The following sections describe the gateway metrics, logs, and spans output by AgentCore to
Amazon CloudWatch. These metrics aren’t available on the CloudWatch generative AI observability
page. Gateway metrics are batched at one minute intervals. To learn more about viewing gateway
metrics, see View observability data for your Amazon Bedrock AgentCore agents.

Note
To enable service-provided logs for AgentCore gateways, you need to conﬁgure the
necessary CloudWatch resources. See Enabling observability for AgentCore runtime,
memory, gateway, built-in tools, and identity resources to learn more.

Topics
• Provided metrics
• Provided log data
• Provided spans

Gateway observability data

1926

Provided metrics
Gateway publishes invocation and usage metrics to CloudWatch. You can view these metrics and
also set up alarms to alert you when certain metrics exceed thresholds. To learn more, select a
topic:
Topics
• Invocation metrics
• Usage metrics
• View gateway CloudWatch metrics
• Setting up CloudWatch alarms
Invocation metrics
These metrics provide information about API invocations, performance, and errors.
For these metrics, the following dimensions are used:
• Operation – The name of the API operation (ex. InvokeGateway).
• Protocol – The name of the protocol (ex. MCP).
• Method – Represents the MCP operation being invoked (ex. tools/list).
• Resource – Represents the identiﬁer of the resource (ex. gateway ARN).
• Name – Represents the name of the tool.

Metric

Description

Statistics

Units

Invocations

The total number
of requests made to
each Data Plane API.
Each API call counts
as one invocation
regardless of the
response status.

Sum

Count

Throttles

The number of
requests throttled

Sum

Count

Gateway observability data

1927

Amazon Bedrock AgentCore

Metric

Developer Guide

Description

Statistics

Units

(status code 429) by
the service.
SystemErrors

The number of
requests which failed
with 5xx status code.

Sum

Count

UserErrors

The number of
requests which failed
with 4xx status code
except 429.

Sum

Count

Latency

The time elapsed
between when the
service receives the
request and when it
begins sending the
ﬁrst response token.
In other words, initial

Average, Minimum,
Maximum, p50, p90,
p99

Milliseconds

Average, Minimum,
Maximum, p50, p90,
p99

Milliseconds

response time.
Duration

The total time
elapsed between
receiving the request
and sending the
ﬁnal response token.
Represents complete
end-to-end processin
g time of the request.

Gateway observability data

1928

Metric

Description

Statistics

Units

TargetExecutionTime

The total time taken
to execute the target
over Lambda /
OpenAPI / etc. This
helps determine the
contribution of the
target to the total

Average, Minimum,
Maximum, p50, p90,
p99

Milliseconds

Latency.

Usage metrics
These metrics provide information about how your gateway is being used.
Metric

Description

Statistics

Units

TargetType

The total number
of requests served
by each type of
target (MCP, Lambda,
OpenAPI).

Sum

Count

View gateway CloudWatch metrics
For more information about viewing CloudWatch metrics, see View available metrics in the
Amazon CloudWatch User Guide . The following procedure shows you how to view metrics for your
gateways:
To view gateway metrics in the console
1. Open the CloudWatch console at https://console.aws.amazon.com/cloudwatch/.
2. In the left navigation pane, choose All metrics under the Metrics section.
3. Under Browse , from the dropdown menu that displays the current AWS Region, select the
Region for which you want metrics.
4. Choose the AWS/Bedrock-AgentCore namespace.
Gateway observability data

1929

5. Choose a dimension (ex. Operation ) or combination of dimensions (ex. Method, Operation,
Protocol ) to view the metrics for it.
6. To add a metric to the CloudWatch graph, select the checkbox next to it.
Setting up CloudWatch alarms
You can use the PutMetricAlarm API operation to set up CloudWatch alarms to alert you when
certain metrics exceed thresholds. For example, you might want to be notiﬁed when the error rate
exceeds 5% or when the latency exceeds 1 second.
The following example shows you how to create an alarm for high error rates using the AWS CLI:
aws cloudwatch put-metric-alarm \
--alarm-name "HighErrorRate" \
--alarm-description "Alarm when error rate exceeds 5%" \
--metric-name "SystemErrors" \
--namespace "AWS/Bedrock-AgentCore" \
--statistic "Sum" \
--dimensions "Name=Resource,Value=my-gateway-arn" \
--period 300 \
--evaluation-periods 1 \
--threshold 5 \
--comparison-operator "GreaterThanThreshold" \
--alarm-actions "arn:aws:sns:us-west-2:123456789012:my-topic"

This alarm will trigger when the number of system errors exceeds 5 in a 5-minute period. When the
alarm triggers, it will send a notiﬁcation to the speciﬁed SNS topic.

Provided log data
AgentCore provides logs that help you monitor and troubleshoot key AgentCore gateway resource
processes. To enable this log data, you need to create a log destination.
AgentCore can output logs to CloudWatch Logs, Amazon S3, or Firehose stream. If you use
a CloudWatch Logs destination, these logs are stored under the default log group /aws/
vendedlogs/bedrock-agentcore/gateway/APPLICATION_LOGS/{gateway_id} or under
a custom log group starting with /aws/vendedlogs/ . See Enabling observability for AgentCore
runtime, memory, gateway, built-in tools, and identity resources to learn more.
AgentCore logs the following information for gateway resources:
Gateway observability data

1930

• Start and completion of gateway requests processing
• Error messages for Target conﬁgurations
• MCP Requests with missing or incorrect authorization headers
• MCP Requests with incorrect request parameters (tools, method)
You can also see request and response bodies as part of your Vended Logs integration when any
of the MCP Operations are performed on the Gateway. They can do further analysis on these logs,
using the span_id and trace_id ﬁelds to connect the vended spans and logs being emitted.
For more information about encrypting your gateways with customer-managed KMS keys, see
Advanced features and topics for Amazon Bedrock AgentCore Gateway.
Sample log:
{
"resource_arn": "arn:aws:bedrock-agentcore:us-east-1:123456789012:gateway/
<gatewayid>",
"event_timestamp": 1759370851622,
"body": {
"isError": false,
"log": "Started processing request with requestId: 1",
"requestBody": "{id=1, jsonrpc=2.0, method=tools/call, params={name=targetquick-start-f9scus___LocationTool, arguments={location=seattle}}}",
"id": "1"
},
"account_id": "123456789012",
"request_id": "12345678-1234-1234-1234-123456789012",
"trace_id": "160fc209c3befef4857ab1007d041db0",
"span_id": "81346de89c725310"
}

Sample log with response body:
{
"resource_arn": "arn:aws:bedrock-agentcore:us-east-1:123456789012:gateway/
<gatewayid>",
"event_timestamp": 1759370853807,
"body": {
"isError": false,
"responseBody": "{jsonrpc=2.0, id=1, result={isError=false,
content=[{type=text, text=\"good\"}]}}",
Gateway observability data

1931

"log": "Successfully processed request with requestId: 2",
"id": "1"
},
"account_id": "123456789012",
"request_id": "12345678-1234-1234-1234-123456789012",
"trace_id": "160fc209c3befef4857ab1007d041db0",
"span_id": "81346de89c725310"
}

Provided spans
AgentCore supports OTEL compliant vended spans that you can use to track invocations across
diﬀerent primitives that are being used.
Sample vended Spans for Tool Invocation:
• kind:SERVER - tracks the overall execution details, tool invoked, gateway details, AWS request
ID, trace and span ID.
• kind:CLIENT - covers the speciﬁc target that was invoked and details around it like target type,
target execution time, target execution start and end times, etc.
For other MCP method invocations, only the kind:SERVER span is emitted.
While these spans emit metrics, to investigate why a failure occurred for a speciﬁc span, a
Gateway user must check the logs that are vended. Various ﬁelds, for example, spanId or
aws.request.id can help in stitching these spans and logs together.

Operation

Span attributes

Description

List Tools

aws.operation.name,
aws.resource.arn, aws.reque
st.id, aws.account.id,
gateway.id, aws.xray.origin,
aws.resource.type, aws.regio
n, latency_ms, error_type,
jsonrpc.error.code, http.meth

List tools attached to a
gateway

od, http.response.stat
us_code, gateway.name,
Gateway observability data

1932


## View metrics and cross-account monitoring (pp. 1955–1962)

Amazon Bedrock AgentCore

Operation

Developer Guide

Span Attribute

Description

aws.agentcore.gateway.polic
y.mode

Policy Engine enforceme
nt mode conﬁgured on the
AgentCore Gateway, valid
values are LOG_ONLY and
ENFORCE

View observability data for your Amazon Bedrock AgentCore
agents
After implementing observability in your agent, you can view the collected metrics and traces in
both the CloudWatch console generative AI observability page and in CloudWatch Logs. Refer to
the following sections to learn how to view metrics for your agents.

View data using generative AI observability in Amazon CloudWatch
The CloudWatch generative AI observability page displays all of the service-provided metrics
output by the AgentCore agent runtime, as well as span- and trace-derived data if you have
enabled instrumentation in your agent code. To view the observability dashboard in CloudWatch,
open the Amazon CloudWatch GenAi Observability page.
With generative AI observability in CloudWatch, you can view tailored dashboards with graphs and
other visualizations of your data, as well as error breakdowns, trace visualizations and more. To
learn more about using generative AI observability in CloudWatch, including how to look at your
agents' individual session and trace data, see Amazon Bedrock AgentCore agents in the Amazon
CloudWatch user guide.

View other data in CloudWatch
All of the service-provided metrics and spans can also be viewed in CloudWatch, along with any
metrics that your instrumented agent code outputs.
To view this data, refer to the following sections.

Logs
1. Open the CloudWatch console.
View metrics for your agents

1955

2. In the left hand navigation pane, expand Logs and select Log groups
3. Use the search ﬁeld to ﬁnd the log group for your agent, memory, or gateway resource.
AgentCore agent log groups have the following format:
• Standard logs - stdout/stderr output
• Location : /aws/bedrock-agentcore/runtimes/<agent_id>-<endpoint_name>/[runtimelogs] <UUID>
• Contains : Runtime errors, application logs, debugging statements
• Example Usage :
• print("Processing request…") # Appears in standard logs
• logging.info("Request processed successfully") # Appears in standard logs
• OTEL structured logs - Detailed operation information
• Location : /aws/bedrock-agentcore/runtimes/<agent_id>-<endpoint_name>/otel-rt-logs
• Contains : Execution details, error tracking, performance data
• Automatic collection : No additional code required - generated by ADOT instrumentation
• Beneﬁts : Can include correlation IDs linking logs to relevant traces

Traces and Spans
Traces provide visibility into request execution paths through your agent:
• Location: the spans log stream in the agent’s log group (/aws/bedrock-agentcore/
runtimes/<agent_id>-<endpoint_name>), or the default log stream in the aws/spans
log group for agents that use the shared span destination. For more information, see Span
destination for agents hosted in Amazon Bedrock AgentCore runtime.
• Access via: CloudWatch Transaction Search console
• Requirements: CloudWatch Transaction Search must be enabled
Traces automatically capture:
• Agent invocation sequences
• Integration with framework components (LangChain, etc.)
• LLM calls and responses
• Tool invocations and results
View other data in CloudWatch

1956

• Error paths and exceptions
For distributed tracing across services, you can use standard HTTP headers:
• AWS X-Ray format: X-Amzn-Trace-Id: Root=1-5759e988bd862e3fe1be46a994272793;Parent=53995c3f42cd8ad8;Sampled=1
• W3C format: traceparent:
00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
To view traces:
• Navigate to CloudWatch console
• Select Transaction Search from the left navigation
• Filter by service name or other criteria
• Select a trace to view the detailed execution graph

Metrics
If you have enabled observability by instrumenting your agent code as described in Enabling
AgentCore observability , your agent automatically generates OTEL metrics, which are sent to
CloudWatch using Enhanced Metric Format (EMF):
• Namespace: bedrock-agentcore
• Access via: CloudWatch Metrics console
• Contents: Custom metrics generated by your agent code and frameworks
• Automatic collection: No additional code required - generated by ADOT instrumentation
In addition to agent-emitted metrics, the AgentCore service publishes standard service metrics to
CloudWatch. Refer to AgentCore generated runtime observability data for a list of these metrics.

Monitor AgentCore resources across accounts
You can use Amazon CloudWatch cross-account observability to monitor Amazon Bedrock
AgentCore resources across multiple AWS accounts from a single monitoring account. This enables
Cross-account monitoring

1957

you to view agent metrics, traces, sessions, and resource data from source accounts without
switching between accounts.
When cross-account observability is enabled, the AgentCore Observability console in your
monitoring account automatically displays data from all linked source accounts alongside your
local account data.

Prerequisites
Before you can monitor AgentCore resources across accounts, you must complete the following:
• Set up a monitoring account – Conﬁgure a central AWS account as your monitoring account in
CloudWatch Settings. For instructions, see CloudWatch cross-account observability.
• Link source accounts – Link one or more source accounts to your monitoring account using AWS
Organizations or individual account linking. Source accounts must share the required telemetry
types (Metrics and Logs).
• Deploy AgentCore resources – Ensure your AgentCore agents, gateways, memory, identity, and
built-in tool resources are deployed in the source accounts with observability enabled.

How to set up cross-account monitoring
Step 1: Conﬁgure the monitoring account
• Open the CloudWatch console.
• In the left navigation pane, choose Settings.
• In the Monitoring account conﬁguration section, choose Conﬁgure.
• Select the telemetry types to share:
• At minimum, select Metrics and Logs to enable AgentCore cross-account observability.
• Complete the monitoring account setup wizard.

Step 2: Link source accounts
Link your source accounts to the monitoring account using one of the following methods:
• AWS Organizations (recommended) – Automatically links all accounts in your organization or
organizational unit. New accounts are onboarded automatically.
Prerequisites

1958

• Individual account linking – Use a CloudFormation template or URL to link speciﬁc accounts.
When conﬁguring source accounts, ensure the same telemetry types selected in the monitoring
account are also enabled in the source account.
For detailed instructions, see Link monitoring accounts with source accounts.

Step 3: View cross-account data in AgentCore Observability
• Open the AgentCore Observability console in your monitoring account.
• The console automatically displays data from all linked source accounts.

Set up cross-account monitoring using infrastructure as code
You can use AWS CloudFormation to conﬁgure cross-account observability programmatically using
CloudWatch Observability Access Manager (OAM) resources.
For the required IAM permissions to create sinks and links, see Necessary permissions.

Monitoring account: Create a sink
In your monitoring account, create an OAM sink that accepts telemetry from source accounts.
You can scope the sink policy in one of the following ways:
• By organization (recommended) – Use aws:PrincipalOrgID to allow all accounts in your
AWS Organizations organization. This is the simplest approach and automatically includes new
accounts added to the organization.
• By individual account IDs – List speciﬁc source account IDs as principals. Use this approach if you
need ﬁne-grained control over which accounts can link.
Option 1: Allow all accounts in an organization
Replace <your-org-id> with your AWS Organizations organization ID (for example, oa1b2c3d4e5).
AWSTemplateFormatVersion: '2010-09-09'
Description: OAM Sink for cross-account AgentCore Observability (organization-wide)
Set up cross-account monitoring using infrastructure as code

1959

Resources:
ObservabilitySink:
Type: AWS::Oam::Sink
Properties:
Name: AgentCoreObservabilitySink
Policy:
Version: '2012-10-17'
Statement:
- Effect: Allow
Principal: '*'
Action:
- 'oam:CreateLink'
- 'oam:UpdateLink'
Resource: '*'
Condition:
StringEquals:
aws:PrincipalOrgID: '<your-org-id>'
ForAllValues:StringEquals:
oam:ResourceTypes:
- 'AWS::Logs::LogGroup'
- 'AWS::CloudWatch::Metric'
Tags:
Purpose: AgentCoreObservability
Outputs:
SinkArn:
Value: !GetAtt ObservabilitySink.Arn
Description: Share this ARN with source accounts to create links

Option 2: Allow speciﬁc source accounts
Replace <source-account-id-1> and <source-account-id-2> with the AWS account IDs of
your source accounts.
AWSTemplateFormatVersion: '2010-09-09'
Description: OAM Sink for cross-account AgentCore Observability (specific accounts)
Resources:
ObservabilitySink:
Type: AWS::Oam::Sink
Properties:
Name: AgentCoreObservabilitySink
Set up cross-account monitoring using infrastructure as code

1960

Policy:
Version: '2012-10-17'
Statement:
- Effect: Allow
Principal:
AWS:
- '<source-account-id-1>'
- '<source-account-id-2>'
Action:
- 'oam:CreateLink'
- 'oam:UpdateLink'
Resource: '*'
Condition:
ForAllValues:StringEquals:
oam:ResourceTypes:
- 'AWS::Logs::LogGroup'
- 'AWS::CloudWatch::Metric'
Tags:
Purpose: AgentCoreObservability
Outputs:
SinkArn:
Value: !GetAtt ObservabilitySink.Arn
Description: Share this ARN with source accounts to create links

Source account: Create a link
In each source account, create an OAM link to the monitoring account’s sink. Replace <sink-arnfrom-monitoring-account> with the sink ARN from the previous step.
AWSTemplateFormatVersion: '2010-09-09'
Description: OAM Link for cross-account AgentCore Observability
Resources:
ObservabilityLink:
Type: AWS::Oam::Link
Properties:
LabelTemplate: '$AccountName'
ResourceTypes:
- 'AWS::Logs::LogGroup'
- 'AWS::CloudWatch::Metric'
SinkIdentifier: '<sink-arn-from-monitoring-account>'
Tags:
Set up cross-account monitoring using infrastructure as code

1961

Purpose: AgentCoreObservability

To deploy this link across all member accounts in your organization, use AWS CloudFormation
StackSets. For instructions, see Link monitoring accounts with source accounts.
For more information about OAM resources, see the AWS CloudFormation OAM resource reference.

Filtering cross-account data
You can ﬁlter data by account in the sessions and traces tables:
• Use the property ﬁlter in the table.
• Select Account ID as the ﬁlter property.
• Enter the source account ID to ﬁlter results to a speciﬁc account.

Limitations
• Cross-account resource actions – Some actions are unavailable for cross-account resources, such
as navigating to the Bedrock console for resource details. You must sign in to the source account
directly to perform these actions.
• OAM link required – Cross-account data is only visible while the OAM link between the
monitoring and source accounts is active. If the link is removed, cross-account data will no longer
appear.
• Telemetry types – Both the monitoring account and source account must have Metrics and Logs
enabled for full AgentCore observability. If only a subset is shared, some data may be missing.
• Regional – Cross-account observability works within a single AWS Region. The monitoring
account and source accounts must be in the same Region.

Related resources
• CloudWatch cross-account observability
• Get started with AgentCore Observability
• View observability data for your Amazon Bedrock AgentCore agents
• Observability Access Manager API Reference

Filtering cross-account data

1962


## AgentCore Evaluations: concepts, evaluators, telemetry (pp. 2149–2159)

Evaluate agent performance with Amazon Bedrock
AgentCore Evaluations
Amazon Bedrock AgentCore Evaluations provides automated assessment tools to measure how
well your agent or tools perform speciﬁc tasks, handle edge cases, and maintain consistency across
diﬀerent inputs and contexts. The service enables data-driven optimization and ensures your
agents meet quality standards before and after deployment.
AgentCore Evaluations integrates with popular agent frameworks including Strands and
LangGraph with OpenTelemetry and OpenInference instrumentation libraries. Under the hood,
traces from these agents are converted to a uniﬁed format and scored using LLM-as-a-Judge
techniques for both built-in and custom evaluators.
Each evaluator has a unique Amazon Resource Name (ARN) and resource policy attached to it.
Evaluator ARNs follow these formats:
arn:aws:bedrock-agentcore:::evaluator/Builtin.Helpfulness (for built-in evaluators)

arn:aws:bedrock-agentcore:region:account:evaluator/my-evaluator-id (for custom
evaluators)

Built-in evaluators are public and accessible to all users. Custom evaluation resources are private
and can only be accessed by users who are explicitly granted access. To grant access, you can use
IAM resource-based policies for evaluators and evaluation conﬁgurations, and IAM identity-based
policies for users and roles.
By default, you can create up to 1,000 evaluation conﬁgurations per AWS Region in an AWS
account. The service supports up to 1 million input and output tokens per minute per account for
large regions.
Topics
• How it works
• Telemetry setup and delivery
• Supported agent frameworks
• Built-in evaluators
• Third-party evaluators
2149

• Custom evaluators
• Online evaluation
• On-demand evaluation
• Batch evaluation
• Dataset evaluation
• Simulation
• Diagnose AgentCore Evaluation issues with an AI coding assistant
• Encryption at rest for AgentCore Evaluations

How it works
Amazon Bedrock AgentCore Evaluations provides capabilities to assess the performance of AI
agents. It can compute metrics such as an agent’s end-to-end task completion (goal attainment)
correctness, the accuracy of a tool invoked by the agent while handling a user request, and any
custom metric deﬁned to evaluate speciﬁc dimensions of an agent’s behavior. The AgentCore
Evaluations can evaluate the AI agents that are hosted under AgentCore Runtime as well as AI
agents hosted outside of AgentCore.
You can create and manage evaluation or relevant resources using the AgentCore CLI, the
AgentCore Python SDK, the AWS Management Console or directly through AWS SDKs.
Topics
• Evaluation terminology
• Evaluators
• Evaluation types

Evaluation terminology
Understanding key concepts and terminology is essential for eﬀectively using AgentCore
Evaluations. The following terms deﬁne the core components and processes involved in agent
evaluation.
Topics
• Agent Framework
How it works

2150

• Instrumentation Library
• Instrumentation Agent
• Session
• Trace
• Tool Call
• Skill
• Reference Free Large Language Models (LLMs) as judges

Agent Framework
An agent framework provides the foundational components for building, orchestrating, and
running agent-based applications. Frameworks deﬁne structures such as steps, tools, control ﬂow,
and memory management. Common industry frameworks include Strands Agents on the Strands
website and LangGraph. These frameworks help standardize how agents are constructed and make
them easier to instrument and evaluate.
For more information about supported frameworks, see Supported agent frameworks.

Instrumentation Library
An instrumentation library records telemetry generated by your agent during execution. This
telemetry can include traces, spans, tool calls, model invocations, and intermediate steps. Libraries
such as OpenTelemetry and OpenInference oﬀer standardized APIs and semantic conventions
that allow you to capture agent behavior with minimal code changes. Instrumentation is required
for trace collection and evaluation.
For more information about supported instrumentation libraries, see Supported agent frameworks.

Instrumentation Agent
An instrumentation agent automatically captures telemetry from application code, processes it,
and exports it to a backend service for storage or evaluation. Tools such as ADOT (AWS Distro
for OpenTelemetry) provide a vendor-neutral, production-ready auto-instrumentation agent
that dynamically injects bytecode to capture traces without code changes. The agent is a key
component in enabling automated evaluation.
AgentCore Evaluations currently supports ADOT (AWS Distro for OpenTelemetry) as the
instrumentation agent.
Evaluation terminology

2151

Session
A session represents a logical grouping of related interactions from a single user or workﬂow. A
session may contain one or more traces. Sessions help you view and evaluate agent behavior across
multi-step interactions, rather than focusing on individual requests.

Trace
A trace is a complete record of a single agent execution or request. A trace contains one or more
spans, which represent the individual operations performed during that execution. Traces provide
end-to-end visibility into agent decisions and tool usage.

Tool Call
A tool call is a span that represents an agent’s invocation of an external function, API, or capability.
Tool call spans typically capture information such as the tool name, input parameters, execution
time, and output. Tool call details are used to evaluate whether the agent selected and used tools
correctly and eﬃciently.

Skill
A skill is a reusable instruction ﬁle that an agent loads at runtime to help with a task. Skills
follow the open Agent Skills standard for skill ﬁle structure. At runtime the agent selects a skill
from a catalog it was shown, or reads the SKILL.md ﬁle directly from the ﬁlesystem. AgentCore
Evaluations detects skill invocations from an agent’s traces. To evaluate them, use the built-in skill
evaluators or custom TOOL_CALL evaluators that reference the skill placeholders.

Reference Free Large Language Models (LLMs) as judges
Large Language Models (LLMs) as judges refers to an evaluation method that uses a large language
model (LLM) to automatically assess the quality, correctness, or eﬀectiveness of an agent or
another model’s output. Instead of relying on manual review or rule-based checks, the LLM is
prompted with evaluation criteria and produces a score, label, or explanation based on the input
and output being evaluated. Unlike traditional evaluations that rely on ground-truth data, LLMas-a-judge methods rely on the model’s internal knowledge to make judgments. This approach
enables scalable, consistent, and customizable qualitative assessments, such as correctness,
reasoning quality, or instruction adherence, across large numbers of agent interactions or model
responses.
Evaluation terminology

2152

Evaluators
Evaluators are the core components that assess your agent’s performance across diﬀerent
dimensions. They analyze agent traces and provide quantitative scores based on speciﬁc criteria
such as helpfulness, accuracy, or custom business metrics. AgentCore Evaluations oﬀers built-in
evaluators for common use cases and third-party evaluators from open source evaluation libraries.
You can also create custom evaluators tailored to your speciﬁc requirements.
Topics
• Built-in evaluators
• Third-party evaluators
• Custom evaluators

Built-in evaluators
Built-in evaluators are pre-conﬁgured solutions that use Large Language Models (LLMs) as judges
to evaluate agent performance. These evaluators come with predeﬁned conﬁgurations, including
carefully crafted prompt templates, selected evaluator models, and standardized scoring criteria.
Built-in evaluators are designed to address common evaluation needs while ensuring consistency
and reliability across assessments. Because they are part of our fully managed oﬀering, you can
use them immediately without any additional conﬁguration, and we will continue improving
their quality and adding new evaluators over time. To preserve consistency and reliability, the
conﬁgurations of built-in evaluators cannot be modiﬁed.

Third-party evaluators
Third-party evaluators come from the DeepEval and AutoEval open source libraries. Amazon
Bedrock AgentCore manages them the same way as built-in evaluators. Select a third-party
evaluator by ID and the service runs it—no model or conﬁguration required. You can also derive a
custom evaluator from a built-in or third-party evaluator to run its logic on your own model. For
more information, see Third-party evaluators.

Custom evaluators
Custom evaluators oﬀer more ﬂexibility by allowing you to deﬁne all aspects of your evaluation
process. AgentCore Evaluations supports the following types of custom evaluators:
Evaluators

2153

• LLM-as-a-judge evaluators – Deﬁne your own evaluator model, evaluation instructions, and
scoring schemas. You can tailor the evaluation to your speciﬁc needs by selecting the evaluator
model, crafting custom evaluation instructions, deﬁning speciﬁc evaluation criteria, and
designing your own scoring schema. For more information, see Custom evaluators.
• Code-based evaluators – Use your own AWS Lambda function to programmatically evaluate
agent performance. This approach gives you full control over the evaluation logic, enabling
deterministic checks, external API calls, regex matching, custom metrics, or any business-speciﬁc
rules without relying on an LLM judge. For more information, see Custom code-based evaluator.
• Evaluators derived from a base evaluator – Run an existing built-in or third-party evaluator’s
logic on your own model and inference, instead of the model the service picks. For more
information, see Third-party evaluators.
This level of customization is particularly valuable when you need to evaluate domain-speciﬁc
agents, apply unique quality standards, or implement specialized scoring systems. For example,
you might create custom evaluation criteria for speciﬁc industries like healthcare or ﬁnance, or
design scoring schemas that align with your organization’s quality metrics.

Evaluation types
AgentCore Evaluations provides three evaluation types, which diﬀer in when and how the
evaluation is performed:
Topics
• Online evaluation
• On-demand evaluation
• Batch evaluation

Online evaluation
Online evaluation continuously monitors the quality of deployed agents using live production
traﬃc. Unlike one-oﬀ evaluation in development environments, it provides continuous
performance assessment across multiple criteria, enabling persistent monitoring in production.
Online evaluation consists of three main components. First, session sampling and ﬁltering allows
you to conﬁgure speciﬁc rules to evaluate agent interactions. You can set percentage-based
sampling to evaluate a portion of all sessions (for example, 10%) or deﬁne conditional ﬁlters for
Evaluation types

2154

more targeted evaluation. Second, you can choose from multiple evaluation methods including
creating new Custom evaluators , using existing custom evaluators, or selecting from Built-in
evaluators . Finally, the monitoring and analysis capabilities lets you view aggregated scores in
dashboards, track quality trends over time, investigate low-scoring sessions, and analyze complete
interaction ﬂows from input to output.

On-demand evaluation
On-demand evaluation provides a ﬂexible way to evaluate speciﬁc agent interactions by directly
analyzing a chosen set of spans. Unlike online evaluation which continuously monitors production
traﬃc, on-demand evaluation lets you perform targeted assessments of selected interactions at
any time.
With on-demand evaluation, you specify the exact spans or traces you want to evaluate by
providing their span or trace IDs. You can then apply the same comprehensive evaluation methods
available in online evaluation, including Custom evaluators or Built-in evaluators . This evaluation
type is particularly useful when you need to try out your own custom evaluator, investigate speciﬁc
customer interactions, validate ﬁxes for reported issues, or analyze historical data for quality
improvements. Once you submit the evaluation request, the service processes only the spans and
traces you specify and returns detailed results for your analysis.
This evaluation type complements online evaluation by oﬀering precise control over which
interactions to assess, making it an eﬀective tool for focused quality analysis and issue
investigation. It is also well suited for early stages of the agent development lifecycle, such as
build-time testing.

Batch evaluation
Batch evaluation runs evaluators against multiple agent sessions in a single asynchronous job.
Unlike on-demand evaluation where you collect spans and call the Evaluate API per session,
batch evaluation handles session discovery, span collection, and scoring entirely on the service
side. You submit a job specifying the CloudWatch Logs location of your agent sessions and which
evaluators to run. The service processes all matching sessions and returns aggregate results with
per-evaluator average scores.
Batch evaluation supports ground truth through session metadata, enabling reference-based
scoring with expected responses, assertions, and expected tool trajectories. Results include both
aggregate summaries (per-evaluator averages and session counts) and per-session detail written to
CloudWatch Logs.
Evaluation types

2155

This evaluation type is designed for baseline measurement before making changes, pre/post
comparison after applying prompt or model updates, regression testing across curated session sets,
and periodic quality audits across production traﬃc from a speciﬁc time window.

Telemetry setup and delivery
Your agent emits spans that Amazon Bedrock AgentCore Evaluations uses to reconstruct each
session. For how AgentCore represents sessions, traces, and spans, see Understand observability for
agentic resources in AgentCore.
To score a session, the service needs the conversation content: the model prompts, the model
completions, and the tool inputs and outputs. Where that content sits depends on how your agent
delivers telemetry, and that is what this page explains.
Topics
• Set up observability
• Telemetry delivery modes
• Uniﬁed telemetry (recommended)
• Split telemetry
• What the service reads from a span
• References
• Sample agents

Set up observability
Instrumenting your agent is one part of producing telemetry that the evaluation service can
read. Your agent must also have observability enabled, so that it exports its telemetry to Amazon
CloudWatch. Complete the following steps:
1. Enable Amazon CloudWatch Transaction Search. Evaluation requires it in both delivery modes.
See Enabling AgentCore observability.
2. Enable observability for your agent, based on where you host it:
• On Amazon Bedrock AgentCore Runtime: see Enabling observability in agent code for
AgentCore-hosted agents.
Telemetry setup

2156

• Hosted outside AgentCore Runtime (Amazon ECS, Amazon EKS, AWS Lambda, or another
environment): see Enabling observability for agents hosted outside of AgentCore. This is also
where you set the log group that receives your telemetry.
3. Check which delivery mode your agent uses, so that you know where your telemetry lands.
Agents that you created on or after July 20, 2026 use uniﬁed telemetry by default, and agents
that you created before that date use split telemetry. Uniﬁed telemetry needs ADOT version
0.18.0 or later (aws-opentelemetry-distro>=0.18.0). Earlier versions send spans to the
shared aws/spans log group.
For an agent on AgentCore Runtime, you switch modes with the
UNIFIED_TRACES_DESTINATION_ENABLED environment variable: set it to true for uniﬁed
telemetry, or false for split telemetry. For the environment variables, the IAM permissions, and
the full procedure for each hosting option, see Span destination for agents hosted in Amazon
Bedrock AgentCore runtime.
Changing the delivery mode does not move telemetry that AgentCore already delivered. Older
spans stay in the log group they were written to, so the service still evaluates a session that you
recorded before the change.

Telemetry delivery modes
AgentCore delivers your agent’s telemetry in one of two modes:
• Uniﬁed telemetry (recommended) keeps everything together. The attributes carrying the model
payloads and the tool requests and responses stay on the span, and all of your agent’s telemetry
goes to one log group.
• Split telemetry separates the two. The AWS Distro for OpenTelemetry (ADOT) moves those
attributes oﬀ the span into separate records, which go to a diﬀerent log group than the spans.
AgentCore Evaluations reads both modes. You do not choose between them in the evaluation
service, and the same evaluators give you the same results either way. We recommend uniﬁed
telemetry, which is available in all AWS commercial Regions where AgentCore Runtime is available.

Uniﬁed telemetry (recommended)
With uniﬁed telemetry, all of your agent’s telemetry goes to one log group. Spans go to the spans
log stream in that log group, next to the agent’s own logs and console output. The span keeps the
Telemetry delivery modes

2157

attributes that carry the model payloads and the tool requests and responses, so the service reads
everything it needs from the span itself.

Which log group holds the spans depends on where you host the agent:
• On Amazon Bedrock AgentCore Runtime: the agent’s log group, /aws/bedrock-agentcore/
runtimes/<agent_id>-<endpoint_name>. AgentCore sets this up for you.
• Hosted outside AgentCore Runtime: the log group that you name in the
OTEL_EXPORTER_OTLP_TRACES_HEADERS environment variable.
Keeping spans and logs in one place helps beyond evaluation. You can look at traces and logs
together, you can write AWS Identity and Access Management (IAM) policies and set up customer
managed key encryption for a single agent, and you can export everything an agent produces by
subscribing to one log group.

Split telemetry
With split telemetry, ADOT takes the large payloads oﬀ the span. As it exports each span, it pulls
out the attributes carrying the model payloads and the tool requests and responses, and sends
them as separate event records, leaving the span with its metadata and its smaller attributes.
Event records exist only in this mode, and they follow the OpenTelemetry events convention.
Each event record links back to its span through a shared traceId and spanId, and the content
sits in the record body, for example in body.input.messages and body.output.messages.

The two kinds of record then go to diﬀerent places:

Telemetry delivery modes

2158

• Spans go to the shared aws/spans log group. CloudWatch creates this log group when you turn
on Transaction Search.
• Event records go to a separate log group. On AgentCore Runtime, that is the agent’s log group,
in the otel-rt-logs log stream, which AgentCore sets up for you. Outside AgentCore Runtime,
it is the log group that you name in the OTEL_EXPORTER_OTLP_LOGS_HEADERS environment
variable.
To evaluate a session, the service reads spans from aws/spans and matches them to their event
records.

What the service reads from a span
For each span in a session, the service does the following:
1. Works out what kind of span it is, based on the attributes the framework set. A span can be
an invoke agent span (the top-level agent run), an execute tool span (a single tool call), or an
inference span (a single model call).
2. Reads the values it needs, such as the user prompt, the agent response, and tool inputs and
outputs. For example, the user prompt comes from the user-role message in the agent input,
and the agent response comes from the assistant-role message in the agent output.
The attributes that identify a span always stay on the span, in both delivery modes. Only the
conversation content moves. Where that content sits within the span also depends on your
instrumentation library: most libraries record it as span attributes, and some attach it to the span
as events. For each library, the per-framework pages list the identifying attributes, say where the
content sits, and show example spans for both modes.

References
AgentCore Evaluations builds on the following OpenTelemetry speciﬁcations:
• Trace semantic conventions on the OpenTelemetry website: how spans and traces are structured
and what they mean.
• Event semantic conventions on the OpenTelemetry website: how event records are structured
and what they mean.
• Generative-AI semantic conventions on the GitHub website: the gen_ai.* attributes that
describe agent, model, and tool operations.
What the service reads from a span

2159


## Generic framework support and built-in evaluators (pp. 2264–2271)

Generic framework support
Amazon Bedrock AgentCore Evaluations reads telemetry through two open standards: the
OpenTelemetry generative AI semantic conventions and the OpenInference semantic conventions.
Alongside the frameworks that have their own page in this section, the service supports any agent
that emits telemetry in one of these two conventions. This is generic framework support.
Use generic framework support when you build with a framework that has no page in this section,
or when you write your own instrumentation for a custom agent. Conﬁgure your instrumentation
to emit the scope name, span attributes, and identifying attributes described on this page, and
the service identiﬁes your spans and extracts the values that evaluators need, using the same span
classiﬁcation and ﬁeld extraction as the named frameworks.
Because your framework’s own data structures are not known in advance, the service extracts
each value as a string rather than parsing it into a framework-speciﬁc structure. Keep prompts,
responses, and tool arguments in the attributes listed in How evaluation ﬁelds are extracted,
rather than wrapped in your own structure such as a nested request object or a custom message
envelope, so that evaluators receive clean values.
Topics
• Supported conventions
• How spans are identiﬁed
• How evaluation ﬁelds are extracted
• OpenTelemetry convention
• OpenInference convention
• Conﬁguration requirements

Supported conventions
The service selects how to read each span from the span’s scope.name. Set your instrumentation’s
scope name to one of the following preﬁxes, and the service reads the span with the matching
convention:
Convention

Scope name preﬁx

OpenTelemetry

opentelemetry.instrumentation.*

Generic framework support

2264

Convention

Scope name preﬁx

OpenInference

openinference.instrumentation.*

If a scope has a page of its own in this section, the service uses the handling described on that
page instead. Generic framework support applies to every other scope that matches one of these
preﬁxes.
Some scopes match the OpenTelemetry preﬁxes but are not GenAI agent frameworks. These are
transport and infrastructure instrumentation, such as HTTP clients (httpx, urllib3, urllib,
aiohttp_client), web frameworks (starlette, fastapi), the Model Context Protocol
(MCP) instrumentation, and the AWS SDK (botocore) instrumentation, including its bedrockagentcore and bedrock-runtime scopes. The service excludes these scopes from generic
framework support so that their spans do not produce spurious agent, tool, or inference spans.

How spans are identiﬁed
The service classiﬁes each span into one of three types using the standard identifying attribute
for its convention. Set this attribute on every span you want evaluated. Its value tells the service
what the span represents, and the service reads it from the span itself, regardless of where the
conversation content is stored.
Example
OpenTelemetry
The service classiﬁes spans using gen_ai.operation.name, and falls back to
traceloop.span.kind when the operation name is absent.
Span type

Identifying attribute

Invoke agent

gen_ai.operation.name
traceloop.span.kind

Execute tool

gen_ai.operation.name
traceloop.span.kind

Inference

gen_ai.operation.name

= invoke_agent (or
= workflow)
= execute_tool (or
= tool)
= chat (or llm.reque

st.type = chat)
Generic framework support

2265

OpenInference
The service classiﬁes spans using openinference.span.kind.

Span type

Identifying attribute

Invoke agent

openinference.span.kind

= AGENT or CHAIN

Execute tool

openinference.span.kind

= TOOL

Inference

openinference.span.kind

= LLM

How evaluation ﬁelds are extracted
For each classiﬁed span, the service reads the values it needs, such as the user prompt, agent
response, and tool inputs and outputs. As with the named frameworks, where the conversation
content sits depends on the telemetry delivery mode. With split telemetry, the content lives in
the correlated event record. With uniﬁed telemetry, it stays on the span as attributes. For more
information, see Telemetry setup and delivery.
The service tries several locations for each ﬁeld and uses the ﬁrst one that holds a value, so you
can emit whichever attribute your instrumentation already sets. Each extracted value is stringiﬁed
rather than parsed into a framework-speciﬁc structure.
OpenTelemetry convention
For frameworks using the OpenTelemetry convention, the service reads each ﬁeld from the
following locations, in order:
• User prompt (invoke agent span): from the event record body.input; then from the
gen_ai.task.input span attribute.
• Agent response (invoke agent span): from the event record body.output; then from the
gen_ai.task.output span attribute. If neither is present, the service falls back to the ﬁrst user
message and last assistant message it collected from the trace’s inference spans.
• Inference messages (inference span): from the event record body.input.messages
and body.output.messages; then from the gen_ai.input.messages and
gen_ai.output.messages span attributes.
Generic framework support

2266

• Tool name (execute tool span): from the gen_ai.tool.name span attribute; then from the
traceloop.entity.name span attribute.
• Tool arguments (execute tool span): from the gen_ai.tool.call.arguments span attribute;
then from the event record body.input; then from the traceloop.entity.input span
attribute.
• Tool result (execute tool span): from the gen_ai.tool.call.result span attribute; then
from the event record body.output; then from the traceloop.entity.output span
attribute.
• System prompt (inference span): from the gen_ai.system_instructions span attribute.
OpenInference convention
For frameworks using the OpenInference convention, the service reads each ﬁeld from the
following locations, in order:
• User prompt (invoke agent span): from the input.value span attribute; then from the event
record body input.
• Agent response (invoke agent span): from the output.value span attribute; then from the
event record body output.
• Inference messages (inference span): from the span’s OpenInference message attributes (for
example, llm.input_messages.* and llm.output_messages.*); then from input.value
and output.value; then from the event record body.
• Tool arguments (execute tool span): from the input.value span attribute; then from the event
record body input.
• Tool result (execute tool span): from the output.value span attribute; then from the event
record body output.
• System prompt (inference span): from the inference span attributes; then from the event record
body.
• Available tools: from the inference span’s tool-deﬁnition attributes (llm.tools.*); then parsed
from the serialized request in the event record body or input.value.

Conﬁguration requirements
To get evaluated with generic framework support, conﬁgure your instrumentation as follows:
Generic framework support

2267

• Use a recognized scope name. Emit spans under a scope name that starts with
opentelemetry.instrumentation.* or openinference.instrumentation.*. The
service reads only these preﬁxes with generic framework support.
• Set an identifying attribute on every span. Set gen_ai.operation.name or
traceloop.span.kind for the OpenTelemetry convention, or openinference.span.kind
for the OpenInference convention. The service skips a span that carries no recognized identifying
attribute.
• Put content in the documented attributes. Set the prompt, response, and tool attributes
listed in How evaluation ﬁelds are extracted. If you wrap these values in your own structure, the
extracted value includes that surrounding structure, because the service stringiﬁes content rather
than parsing your framework’s data model.
If you cannot set convention attributes, you can still evaluate the top-level agent turn. Set the
agentcore.invocation.user_prompt and agentcore.invocation.agent_response span
attributes, which the AgentCore SDK also emits. The service reads these attributes from any scope,
and they cover the agent prompt and response only, not inference or tool spans.

Built-in evaluators
Built-in evaluators in AgentCore Evaluations provide pre-conﬁgured evaluators for assessing your
agents. These evaluators use predeﬁned evaluator models and prompt templates that have been
optimized for common evaluation scenarios.
You can use built-in evaluators with on-demand, batch, and online evaluations. To specify
a built-in evaluator, use its ID in the following format: Builtin.EvaluatorName , such as
Builtin.Helpfulness.
Note
Built-in evaluator conﬁgurations, including their evaluator models and prompt templates,
cannot be modiﬁed.

For evaluators that only apply when a tool call loads a skill, see Skill evaluators.
Topics
• Cross region inference
Built-in evaluators

2268

• Skill evaluators
• Prompt templates

Cross region inference
AgentCore Evaluations will automatically select the optimal region within your geography to
process your inference requests. This maximizes available compute resources, model availability,
and delivers the best customer experience. Your data will remain stored only in the region where
the request originated, however, input prompts and output results may be processed outside that
region. All data will be transmitted encrypted across AWS's secure network.
For AgentCore Evaluations, inference requests originating in Asia Paciﬁc (Hyderabad) (ap-south-2),
Asia Paciﬁc (Malaysia) (ap-southeast-5), Asia Paciﬁc (Seoul) (ap-northeast-2), and Asia Paciﬁc
(Thailand) (ap-southeast-7) use global cross-region inference and will be securely routed to all
available compute resources across all global commercial AWS Regions. For more information, see
Global cross-region inference for AgentCore Evaluations.
If your use case requires avoiding cross region inference , you can create Custom evaluators that
operate without CRIS. Custom evaluators provide the ﬂexibility to:
• Replicate the functionality of built-in evaluators without using CRIS
• Deﬁne identical evaluation criteria and scoring schemas as built-in evaluators
• Maintain full control over the inference conﬁguration

Note
While custom evaluators can be conﬁgured to match built-in evaluator functionality, you
are responsible for managing model availability and compute resources.

Skill evaluators
A skill is a reusable SKILL.md instruction ﬁle that an agent loads at runtime to help with a task.
Skills follow the open Agent Skills standard for skill ﬁle structure. For terminology, see Skill.
AgentCore Evaluations provides two built-in evaluators for agents that use skills. Both are toollevel evaluators. AgentCore Evaluations emits one result per skill invocation and anchors each
Cross region inference

2269

result to the tool call span that loaded the skill. A session with three skill invocations produces
three results per evaluator.
You can use these evaluators with on-demand, batch, and online evaluations. For the exact prompt
bodies, see Skill selection accuracy and Skill instruction following on the Prompt templates page.

Builtin.SkillSelectionAccuracy
The Skill selection accuracy evaluator (Builtin.SkillSelectionAccuracy) judges whether the
skill the agent loaded ﬁts the task, given the catalog of available skills. It returns Yes (1.0) or No
(0.0).
Placeholders the evaluator uses:
• invoked_skill – The name of the skill the agent loaded in this tool call.
• available_skills – The catalog of skills the agent could choose from at runtime. Not every
framework exposes a catalog. When the catalog is not in the trace, this placeholder is empty
and the evaluator judges the invoked skill against the user request and the conversation context
alone.
• user_message – The user request in the turn that triggered the skill invocation.
• context – Previous turns up to the tool call being evaluated.
The evaluator runs whenever AgentCore Evaluations detects a skill invocation. It focuses on the
selection decision, not on how well the agent then executed the skill.

Builtin.SkillInstructionFollowing
The Skill instruction following evaluator (Builtin.SkillInstructionFollowing) judges how
fully the agent followed the loaded skill’s prescribed steps. It returns Fully Followed (1.0),
Mostly Followed (0.75), Partially Followed (0.5), Minimally Followed (0.25), or Not
Followed (0.0).
Placeholders the evaluator uses:
• invoked_skill – The name of the skill the agent loaded in this tool call.
• skill_content – The full body of the loaded skill’s SKILL.md instructions.
• context – The full session context — every turn from session start through session end.
Because the agent may carry out prescribed steps at any point after loading the skill, the judge
needs the entire session, not just the turns up to the tool call.
Skill evaluators

2270

The evaluator runs only when both the invoked skill and its SKILL.md body are present in the
trace. The judge identiﬁes the prescribed steps in the skill body, then, for each step, determines
from the conversation record whether the step was fully carried out, partially carried out, or
skipped, and produces an overall rating consistent with that per-step breakdown.

Framework support
AgentCore Evaluations detects skill invocations from two kinds of trace signals: a ﬁlesystem read of
a SKILL.md ﬁle, and a framework’s native skill-loading tool. The ﬁlesystem-read signal works for
any framework. The native-tool signal applies to the speciﬁc frameworks in the second row of the
following table.
Detection method

Frameworks

SKILL.md ﬁle read (universal)

LlamaIndex, OpenAI Agents, and any agent
that reads SKILL.md through a generic ﬁleread tool.

Native skill-loading tool (in addition to ﬁle
read)

Strands Agents, LangGraph Deep Agents,
Google ADK, Claude Agent SDK.

For the ﬁle-read path, AgentCore Evaluations matches a tool call as a skill load when its
parameters contain a path ending in /SKILL.md and the tool result body is a well-formed
SKILL.md ﬁle (frontmatter with name and description ﬁelds, followed by an instructions body).
An available-skills catalog is emitted natively by Strands Agents, LangGraph Deep
Agents, and Google ADK. Claude Agent SDK and ﬁle-read agents do not emit a catalog.
Builtin.SkillSelectionAccuracy still runs on those agents, with an empty
available_skills placeholder.
For general instrumentation setup and per-framework scope names, see Supported agent
frameworks.

Skipping behavior
AgentCore Evaluations classiﬁes a tool call as a skill invocation when the trace exposes
invoked_skill or skill_content for that call. If neither signal is present, AgentCore
Evaluations skips both skill evaluators for that call and emits no result. If your agent doesn’t load
any skills, both evaluators produce zero results for the session — this is expected, not an error.
Skill evaluators

2271


## Online evaluation overview (pp. 2345–2346)

Note
When an online evaluation conﬁguration referencing a code-based evaluator is enabled,
the evaluator is automatically locked and cannot be modiﬁed or deleted until the
conﬁguration is disabled or deleted. To make changes to the evaluator, disable the online
evaluation conﬁguration ﬁrst, or clone the evaluator and create a new conﬁguration.

Online evaluation
An online evaluation conﬁguration is a resource that deﬁnes how your agent is evaluated, including
which evaluators to apply, which data sources to monitor, and evaluation parameters.
Topics
• Prerequisites
• Create and deploy your agent
• Create online evaluation
• Get online evaluation
• List online evaluations
• Update online evaluation
• Delete online evaluation
• Results and output

Prerequisites
Before you begin using Amazon Bedrock AgentCore Evaluations, ensure you have the necessary
AWS permissions and service roles conﬁgured.
Topics
• Required permissions
• IAM user permissions
• Service execution role

Online evaluation

2345

Required permissions
To use AgentCore Evaluations online evaluation features, you need:
• AWS Account with appropriate IAM permissions
• Amazon Bedrock access with model invocation permissions (required when using a custom
evaluator)
• Amazon CloudWatch access for viewing evaluation results
• An agent built with a supported framework and instrumentation library. For more information
about supported frameworks and instrumentation libraries, see Supported agent frameworks.
• An agent deployed on AgentCore Runtime with observability enabled, or an agent built with a
supported framework conﬁgured with AgentCore Observability, including Transaction Search.
For more information about telemetry setup, see Telemetry setup and delivery.

IAM user permissions
Your IAM user or role needs the following permissions to create and manage evaluations:
Topics
• Console and API operations
Console and API operations
To use Amazon Bedrock AgentCore, you can attach the BedrockAgentCoreFullAccess AWS managed
policy to your IAM user or IAM role. This policy grants broad permissions for all AgentCore
capabilities. If you only use AgentCore Evaluations, we recommend creating a custom IAM policy
that includes only the permissions required for evaluation.
{
"Version": "2012-10-17",
"Statement": [
{
"Effect": "Allow",
"Action": [
"bedrock-agentcore:CreateEvaluator",
"bedrock-agentcore:GetEvaluator",
"bedrock-agentcore:ListEvaluators",
"bedrock-agentcore:UpdateEvaluator",
Prerequisites

2346


## Online evaluation results (pp. 2372–2374)

client = boto3.client('bedrock-agentcore-control')
delete_config_response = client.delete_online_evaluation_config(
onlineEvaluationConfigId='your_config_id'
)

AWS CLI
1.
aws bedrock-agentcore-control delete-online-evaluation-config \
--online-evaluation-config-id your_config_id

Console
Permanently remove an online evaluation conﬁguration using the console interface, which includes
conﬁrmation prompts to prevent accidental deletion.
To delete an online evaluation conﬁguration
1. Open the Amazon Bedrock AgentCore console.
2. In the navigation pane, choose Evaluation.
3. In the Evaluation conﬁgurations card, view the table that lists the evaluation conﬁgurations you
have created.
4. Choose one of the following methods to delete the conﬁguration:
• Choose the evaluation conﬁguration name to view its details, then choose Delete in the upper
right of the details page.
• Select the evaluation conﬁguration so that it is highlighted, then choose Delete at the top of
the Evaluation conﬁgurations card.
5. Enter confirm to conﬁrm the deletion.
6. Choose Delete to delete the conﬁguration.

Results and output
Online evaluation results are automatically saved to Amazon CloudWatch. By default, the service
writes them as JSON log entries to a dedicated CloudWatch log group.
Results and output

2372

Topics
• Log group structure
• Choose where results are written
• Publish metrics to a custom namespace
• Result format
• Viewing results in CloudWatch Observability Console
• Viewing evaluation scores in CloudWatch Metrics

Log group structure
If you use the default dedicated destination, the service writes evaluation results to /aws/
bedrock-agentcore/evaluations/results/<online-evaluation-config-id> . You
can see the resolved result log group for a conﬁguration on that evaluation’s details page in the
Amazon Bedrock AgentCore console.
Each evaluation generates a separate log entry within this log group. Additionally, evaluation
scores are emitted as CloudWatch metrics for monitoring and analysis.

Choose where results are written
Use resultDestination in outputConfig.cloudWatchConfig to choose where online
evaluation results are written. If you don’t set it, the service uses a dedicated log group:
• DEDICATED_LOG_GROUP (default) – Writes results to a dedicated result log group. If you
don’t set logGroupName, the service uses /aws/bedrock-agentcore/evaluations/
results/<online-evaluation-config-id>. To use a diﬀerent dedicated log group, set
logGroupName (see the section called “Use a custom output log group”).
• SOURCE_LOG_GROUP – Writes results back to the same log group that supplied the agent traces,
so evaluations appear alongside the traces they scored. Don’t set logGroupName when you use
this value.
Use a custom output log group
When resultDestination is DEDICATED_LOG_GROUP, you can set logGroupName to
send results to a log group that you choose. If the log group already exists, the service uses
Results and output

2373

it as-is. If it doesn’t exist, the service creates it, so the evaluation execution role must allow
logs:CreateLogGroup for that log group. The name can’t use the reserved /aws/bedrockagentcore/evaluations/ preﬁx, except for this conﬁguration’s own service-managed default
group.
# Write results back to the trace source log group
outputConfig={"cloudWatchConfig": {"resultDestination": "SOURCE_LOG_GROUP"}}
# Write results to a custom dedicated log group
outputConfig={"cloudWatchConfig": {"resultDestination": "DEDICATED_LOG_GROUP",
"logGroupName": "/my/team/evaluation-results"}}

Publish metrics to a custom namespace
Evaluation scores are also published as CloudWatch metrics. By default, the service uses
the Bedrock-AgentCore/Evaluations namespace. To publish metrics under your own
namespace, for example to separate results by team or tenant, set metricsNamespace in
outputConfig.cloudWatchConfig. The value can’t begin with AWS/.
outputConfig={"cloudWatchConfig": {"metricsNamespace": "MyTeam/Evaluations"}}

Result format
Evaluation results follow OpenTelemetry semantic conventions for GenAI evaluation result events.
When possible, each event is parented to the original span ID and includes the original trace ID and
session ID.
You can use CloudWatch Logs Insights to query and analyze your evaluation results, and
CloudWatch Metrics to monitor evaluation trends over time.

Viewing results in CloudWatch Observability Console
You can view and analyze your evaluation results using the CloudWatch Observability Console. The
console provides visualizations, metrics, and detailed logs of your agent evaluations.
To view evaluation results
1. Open the CloudWatch console at https://console.aws.amazon.com/cloudwatch/
2. In the navigation pane, choose GenAI Observability > Bedrock AgentCore
Results and output

2374


## Insights (preview) (pp. 2685–2690)

From

To

Description

RUNNING

PAUSED

Pause the test. Traﬃc stops splitting; all traﬃc
routes to control.

PAUSED

RUNNING

Resume a paused test.

RUNNING

STOPPED

Stop the test permanently. Traﬃc routing
ends immediately.

PAUSED

STOPPED

Stop a paused test permanently.

AgentCore insights: Triage agent failures with pattern analysis
Note
AgentCore insights is in public preview. Features and APIs may change before general
availability.

Note
When using AgentCore insights in ap-south-1, the service uses Bedrock APAC cross-region
inference proﬁles. When using AgentCore insights in ap-northeast-2, the service uses
Bedrock global cross-region inference proﬁles. In both cases, your request may be routed
to any of the destination Regions in the proﬁle. This routing can occur even if you have not
opted in to those Regions or have Service Control Policies explicitly denying inference in
them. Input prompts and output results may be stored in these destination Regions for
abuse detection purposes.

Amazon Bedrock AgentCore insights analyzes your agent sessions to identify failure patterns,
extract user intents, and summarize execution behavior. Insights extends AgentCore Evaluations
by providing triage analysis that goes beyond scoring — it tells you why your agent fails and what
your users are trying to accomplish.
AgentCore insights provides three analysis types:
Insights (preview)

2685

• Failure analysis: Identiﬁes failures in agent sessions, categorizes them using a detailed taxonomy
(tool errors, hallucinations, incorrect reasoning, repetitive behavior, and more), traces root causes
back to speciﬁc spans, and provides ﬁx recommendations.
• User intent extraction: Extracts what users were trying to accomplish in each session, then
clusters similar intents together to show you the most common use cases your agent handles.
• Execution summary: Summarizes the approach the agent took and the outcome for each
session, then clusters similar execution patterns to reveal how your agent typically solves
problems.
After per-session analysis, the service clusters results across sessions to surface recurring patterns.
For failure analysis, this produces a three-level hierarchy: failure categories → subcategories → root
cause clusters, each with aﬀected sessions, explanations, and remediation recommendations.

How insights are triggered
Insights analysis can be triggered in two ways:
• One time via batch evaluation: Call StartBatchEvaluation with insights to run analysis
over a time range of sessions. Results are returned through GetBatchEvaluation.
• Recurring via clustering schedule: Conﬁgure a ClusteringConfig on your online evaluation
conﬁguration with one or more frequencies (DAILY, WEEKLY, or MONTHLY). The service
automatically triggers batch evaluation jobs on the conﬁgured cadence. You can also create a
custom report in the recurring schedule to pin to a speciﬁc date and time.
Per-session insight analysis runs automatically when insights are conﬁgured via
CreateOnlineEvaluationConﬁg, but the clustered results that surface patterns are only generated
during batch evaluation jobs.

From triage to optimization
AgentCore insights works together with AgentCore optimization to close the improvement loop.
After insights identiﬁes failure patterns and root causes, you can feed those ﬁndings into the
Recommendations API to generate an improved system prompt that addresses the triaged issues.
This turns diagnostic output into actionable conﬁguration changes:
1. Triage: Run insights to identify recurring failure categories and root causes.
How insights are triggered

2686

2. Generate recommendation: Call StartRecommendation with your current system prompt and
point it at the same agent traces. The service produces a recommended system prompt with an
explanation of what it changed.
3. Validate: Use A/B testing to compare the original and recommended conﬁgurations with live
traﬃc.

How it works
AgentCore insights answers three questions about your agent’s production behavior: Why is it
failing? What are users asking for? and How is it solving problems?

What you get
When you run insights, you receive:
• A prioritized list of failure patterns — not individual errors, but recurring issues grouped by root
cause. Each pattern tells you what’s going wrong and why. Insights is integrated with AgentCore
recommendation capabilities to generate ﬁxes for the failure patterns.
• A map of user intents — the most common things your users are trying to accomplish, ranked
by frequency.
• A summary of agent behavior patterns — how your agent typically approaches problems and
what outcomes it achieves.
These correspond to three insight types you can conﬁgure:
• Builtin.Insight.FailureAnalysis — Failure pattern detection and root cause analysis
• Builtin.Insight.UserIntent — User intent extraction and clustering
• Builtin.Insight.ExecutionSummary — Agent behavior summarization and clustering

How the analysis works
Insights examines your agent’s session traces — the full record of user messages, agent reasoning,
tool calls, and responses — and produces ﬁndings at two levels:
Session-level analysis
Each session is individually analyzed to determine:
How it works

2687

• Whether the agent encountered failures during execution — including hidden failures within
traces that may not be visible to the end user even when the session appears successful
• What category of failure occurred (tool error, hallucination, wrong tool choice, etc.)
• Which speciﬁc step in the agent’s execution caused the failure
• What the root cause was
• What the user was trying to accomplish
• What approach the agent took and the ﬁnal outcome
Pattern discovery
After individual sessions are analyzed, the service identiﬁes recurring patterns across all sessions by
grouping similar ﬁndings together. For failure analysis, this produces a three-level hierarchy:
1. Failure categories: Broad groupings such as "execution errors," "hallucinations," or "incorrect
actions."
2. Subcategories: More speciﬁc failure types, such as "rate limiting" or "tool schema errors."
3. Root cause clusters: Within each subcategory, the speciﬁc recurring root causes. Each cluster
tells you:
• What the root cause is
• How many sessions are aﬀected
• Which sessions you can inspect for details
For user intents and execution summaries, the service produces ﬂat clusters ranked by frequency.

When it runs
You control when insights runs:
• One-time: Call StartBatchEvaluation with insights whenever you want an analysis — for
example, after a deployment, after a spike in user complaints, or as part of a weekly review.
• Recurring: Conﬁgure a clustering frequency (DAILY, WEEKLY, or MONTHLY) and the service runs
automatically, giving you periodic reports without manual intervention.

How it works

2688

Failure categories
Insights recognizes a broad taxonomy of agent failure types:
Category

Examples

Execution errors

Authentication failures, resource not found, service errors, rate
limiting, timeouts, tool schema violations

Task instruction issues

Non-compliance with instructions, problem identiﬁcation
failures

Incorrect actions

Wrong tool selection, poor information retrieval, inappropriate
clariﬁcation requests

Context handling

Context handling failures across turns

Hallucinations

Fabricated capabilities, misunderstanding, incorrect usage,
history fabrication, parameter hallucination, fabricated tool
outputs

Repetitive behavior

Tool call repetition, information request repetition, step
repetition

Orchestration errors

Reasoning mismatch, goal deviation, premature termination,
unaware termination

LLM output issues

Nonsensical outputs

Conﬁguration mismatch

Tool deﬁnition mismatches

Coding-speciﬁc

Edge case oversights, dependency issues

Prerequisites
Before you begin using AgentCore insights, ensure you have the following:
Topics
• Requirements
Prerequisites

2689

• IAM permissions
• Execution role

Requirements
• AWS Account with appropriate IAM permissions
• Amazon CloudWatch access for reading agent session traces and viewing insight results
• Transaction Search enabled in CloudWatch — see AgentCore Observability for setup
instructions
• AWS Distro for OpenTelemetry (ADOT) SDK instrumenting your agent — your agent must emit
traces to CloudWatch Logs
• An active agent with at least one completed session producing traces in CloudWatch Logs

IAM permissions
Your IAM user or role needs the following permissions to conﬁgure and run insights:
{
"Version": "2012-10-17",
"Statement": [
{
"Effect": "Allow",
"Action": [
"bedrock-agentcore:CreateOnlineEvaluationConfig",
"bedrock-agentcore:GetOnlineEvaluationConfig",
"bedrock-agentcore:ListOnlineEvaluationConfigs",
"bedrock-agentcore:UpdateOnlineEvaluationConfig",
"bedrock-agentcore:DeleteOnlineEvaluationConfig",
"bedrock-agentcore:StartBatchEvaluation",
"bedrock-agentcore:GetBatchEvaluation",
"bedrock-agentcore:ListBatchEvaluations"
],
"Resource": "*"
}
]
}

Prerequisites

2690
