# Amazon Bedrock AgentCore Developer Guide — Operations, reliability, and governance (selected chapters)

## Summary

This filtered excerpt of the AWS Bedrock AgentCore Developer Guide covers the operational, reliability, and governance concerns of running agents in production, once the basic multi-agent architecture from `bedrock-agentcore-multi-agent` is already in place. It opens with cost and lifecycle controls: harness billing is per-second CPU/memory consumption rather than wall-clock time, and hard caps (max iterations, timeout, token budget, idle timeout, max session lifetime) bound a runaway agent regardless of the agent's own stopping logic. Immutable, auto-versioned configurations paired with named endpoints let a team pin production to a specific version while iterating freely elsewhere, and roll back by simply repointing an endpoint.

A large security section documents concrete, AWS-specific failure modes and their fixes: a `prompt` field left untyped can let a caller smuggle a `toolUse` content block that some frameworks execute directly, bypassing the model and its guardrails entirely; execution roles need `aws:SourceArn`/`aws:SourceAccount` trust-policy conditions to prevent confused-deputy impersonation; cross-account access requires resource-based policies on both the runtime and its endpoint, with an explicit deny on either one winning; and a policy-enforcing Gateway only protects traffic that can't reach the Runtime directly. Gateway rate limits add a further, explicitly weaker control — multi-dimension, fail-open throttling that must never be relied on as a security boundary.

The governance section covers Policy in AgentCore: Cedar-language authorization policies enforced deterministically at the Gateway boundary, outside agent code, with default-deny and forbid-wins semantics, an auto-generated schema from the Gateway's own tool definitions, and natural-language policy authoring with automated safety analysis. Dogwood extends Cedar with temporal, session-aware conditions — prior approval, repeat-count limits, running-total budgets — for rules a single stateless request can't express. A two-level `LOG_ONLY` mechanism lets a policy or an entire policy engine be shadow-tested against real traffic, with decision-flip telemetry showing whether it's safe to promote to enforcement. Finally, the optimization workflow closes the loop: immutable configuration bundles and Gateway-routed, statistically-scored A/B testing let a team validate a prompt or config change against live traffic before committing to a full rollout.

## Knowledge Map

- Cost attribution (per-second CPU/memory billing) and hard operational limits that bound a runaway agent independent of its own logic
- Immutable auto-versioning and named endpoints as the safe-deployment and rollback mechanism
- Concrete, documented security failure modes: type-confusion payload injection, confused-deputy trust-policy gaps, incomplete dual-resource cross-account policies, and gateway-bypass risk
- Gateway rate limiting as a throughput control with explicit fail-open semantics, not a security boundary
- Cedar-based deterministic policy authorization enforced outside agent code, with natural-language authoring and automated safety analysis
- Dogwood's temporal, session-aware policy conditions for history-dependent authorization rules
- Two-level LOG_ONLY shadow testing with decision-flip telemetry as a safe policy-promotion signal
- Configuration bundles and gateway-routed A/B testing as the statistically-validated rollout mechanism for agent behavior changes

## Key Takeaways

- Bill and bound an agent loop by actual consumption and hard caps, not by trusting either wall-clock estimates or the agent's own sense of when to stop.
- Treat every version as an immutable, complete snapshot, and treat promotion to production as a separate, explicit endpoint repoint.
- Validate the type of every field in an agent's request payload — an untyped `prompt` field is a documented, concrete bypass of model reasoning and guardrails.
- A defense (a policy-enforcing gateway, a resource-based policy) only holds if the bypass path around it is also closed.
- Never rely on a fail-open control, such as a rate limit, as a security boundary.
- Move authorization outside agent code and make it deterministic; add session-aware temporal conditions only where a stateless rule genuinely can't express the requirement.
- Shadow-test a new policy against real traffic and check its decision-flip rate before trusting it in enforcement.
- Validate a config or prompt change with a statistically significant live A/B test before routing all traffic to it.

## Source Text

Source: Amazon Bedrock AgentCore Developer Guide (3,428-page PDF), filtered to selected page ranges.


## Harness costs, limits, versioning (pp. 97–105)

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

Capability

When charges apply

What determines usage

AgentCore
Memory

AgentCore Memory bills
when the harness writes
events or retrieves records.
Managed Memory is enabled
by default; charges also apply
to attached Memory.

AgentCore Memory meters new short-term
events, stored long-term memory records, and
long-term memory retrieval requests.

AgentCore
Browser
and Code
Interpreter

Browser and Code Interpret
er bill when the agent uses
these conﬁgured tools.

Each service meters active CPU and memory
consumption for its sessions. Their tool
deﬁnitions can still add model input tokens
when allowed, even if the agent doesn’t call
them.

AgentCore
Gateway and
Web Search

Gateway bills when the
harness discovers or invokes
tools, performs searches,
or uses indexed tools. Web
Search bills when the harness
submits a query.

Gateway meters API operations, search
queries, and indexed tools, as applicable. Web
Search meters its queries separately.

Observability

CloudWatch bills for the
traces, logs, and metrics that
every invocation emits.

CloudWatch meters ingestion, storage, and
query usage.

Storage and
network

Storage and network services
bill when you use a custom
container, persistent ﬁlesyste
ms, or data transfer.

Amazon ECR meters image storage. Amazon
S3 and EFS meter resource usage. Standard
data transfer rates apply to network traﬃc.

Estimate Runtime cost
Runtime billing uses per-second active consumption rather than provisioned instance time:
CPU cost = consumed vCPU-seconds / 3,600 * vCPU-hour rate
Memory cost = sum of peak GB consumed in each second / 3,600 * GB-hour rate

Understand harness costs

98

Don’t estimate CPU cost from wall-clock invocation or session duration alone. Model and tool I/O
waits don’t incur CPU charges when no other process uses CPU. However, memory consumption
remains billable. A shorter idleRuntimeSessionTimeout can reduce how long memory remains
billable after the last invocation, at the cost of more frequent cold starts.

Measure and attribute usage
• Read metadata events in the invocation stream for model token usage.
• Use AgentCore Observability traces, CloudWatch Logs, and X-Ray APIs to identify model calls,
tool calls, memory operations, and their duration. Observability explains activity but is not a
billing report.
• Use AWS Cost Explorer or the AWS Cost and Usage Report for billed usage. Activate your harness
tags as cost allocation tags to ﬁlter supported charges.
Harness tags propagate to the managed Runtime, Runtime endpoint, and managed Memory
created for the harness. Tag separately created resources, such as Gateway, EFS, S3, or a bringyour-own Memory resource, independently.

Control cost with limits
Set hard caps so a runaway agent can’t burn through resources:
• maxIterations - reasoning/action cycles per invocation. Default 75.
• timeoutSeconds - wall-clock timeout for a single invocation. Default 3600.
• maxTokens - token budget per invocation. Default N/A.
• idleRuntimeSessionTimeout - how long an idle microVM stays warm. Default 900.
• maxLifetime - maximum lifetime of a microVM session. Default 28800.
All limits are optional; omit them to use service defaults. Because harness is backed by AgentCore
Runtime, harness invocations are also subject to Runtime service quotas. For more information, see
AgentCore harness Service Quotas and AgentCore Runtime Service Quotas.
Example
AWS CLI/boto3
aws bedrock-agentcore-control update-harness \
Control cost with limits

99

--harness-id "MyHarness-UuFdkQoXSL" \
--max-iterations 50 \
--timeout-seconds 1800 \
--max-tokens 8192

Or override on a single invocation by passing maxIterations, timeoutSeconds, or
maxTokens in invoke_harness.
AgentCore CLI
Set defaults:
agentcore add harness --name bounded-agent \
--max-iterations 50 --timeout 1800 --max-tokens 8192 \
--truncation-strategy sliding_window \
--idle-timeout 600 --max-lifetime 14400
agentcore deploy

The --truncation-strategy ﬂag accepts sliding_window or summarization. The -idle-timeout and --max-lifetime ﬂags set lifecycle limits in seconds.
Override on a single call:
agentcore invoke --harness bounded-agent --max-iterations 20 --harness-timeout 600 \
"Quick lookup: what's the weather in Seattle?"

Tags
Apply tags to your harness for cost allocation and access control.
Example
AWS CLI/boto3
aws bedrock-agentcore-control create-harness \
--harness-name "MyHarness" \
--execution-role-arn "arn:aws:iam::123456789012:role/MyHarnessRole" \
--tags '{"team": "platform", "environment": "staging"}'

AgentCore CLI
Set tags in harness.json:
Tags

100

{
"tags": {
"team": "platform",
"environment": "staging"
}
}

Run agentcore deploy to apply.
Harness tags propagate to the managed Runtime, Runtime endpoint, and managed Memory
created for the harness. Separately created resources retain their own tags.

Related topics
• the section called “Memory” - memory persists conversation context across sessions
• the section called “Environment and ﬁlesystem” - environment variables and custom containers
• the section called “Security” - execution role policy and IAM permissions
• the section called “API Documentation”

AgentCore harness versioning and endpoints
Amazon Bedrock AgentCore implements automatic versioning for AgentCore harnesses and lets
you manage diﬀerent conﬁgurations using endpoints. Harness versioning works the same way as
AgentCore Runtime versioning - harness is a managed abstraction over Runtime - but you manage
it through the harness control plane APIs.
Each harness in Amazon Bedrock AgentCore is automatically versioned:
• When you create a harness, AgentCore automatically creates version 1 (V1)
• Each update to the harness creates a new version with a complete, self-contained conﬁguration
• Versions are immutable once created
• Each version contains all the conﬁguration needed for execution: model, system prompt, tools,
memory, limits, and environment

Versioning and endpoints

101

How endpoints reference versions
Endpoints provide a way to reference speciﬁc versions of your harness:
• The DEFAULT endpoint automatically points to the latest version of your harness
• Endpoints can point to speciﬁc versions, allowing you to maintain diﬀerent environments (e.g.,
development, staging, production)
• When you update a harness, the DEFAULT endpoint is automatically updated to point to the new
version
• Endpoints must be explicitly updated to point to new versions
Example Updating an endpoint to a new version
Example
AWS CLI/boto3
import boto3
control_client = boto3.client('bedrock-agentcore-control', region_name='us-west-2')
response = control_client.update_harness_endpoint(
harnessId='MyHarness-UuFdkQoXSL',
endpointName='production-endpoint',
targetVersion='2',
description='Updated production endpoint'
)
print(response)

Or with the AWS CLI:
aws bedrock-agentcore-control update-harness-endpoint \
--harness-id "MyHarness-UuFdkQoXSL" \
--endpoint-name "production-endpoint" \
--target-version "2" \
--description "Updated production endpoint"

How endpoints reference versions

102

Versioning scenarios
The following table illustrates how versioning and endpoints interact during the lifecycle of a
harness:
Change Type

Version Creation
Behavior

Latest Version

Endpoint Behavior

Initial Creation

Creates Version 1
(V1) automatically

V1

DEFAULT points to V1

Model Change

Creates a new version
with the updated
model selection

V2

DEFAULT automatic
ally updates to V2

Create "PROD"
endpoint with V2

No new version
created

V2

PROD endpoint
points to V2

Tool or Skill Update

Creates a new version
with the updated tool
conﬁguration

V3

DEFAULT updates to
V3, PROD remains on
V2

Update "PROD" to V3

No new version
created

V3

PROD updates to V3

Limits or Environme
nt Modiﬁcation

Creates a new
version with updated
execution parameters

V4

DEFAULT updates to
V4, PROD remains on
V3

Endpoint lifecycle states
Harness endpoints go through various states during their lifecycle:
CREATING
Initial state when an endpoint is being created
CREATE_FAILED
Indicates creation failure due to permissions, conﬁguration, or other issues
Versioning scenarios

103

READY
Endpoint is ready to accept requests
UPDATING
Endpoint is being updated to a new version
UPDATE_FAILED
Indicates update operation failure

Creating an endpoint
Create a named endpoint to pin an environment to a speciﬁc harness version. If you omit
targetVersion, the endpoint points to the latest version at creation time.
Example
AWS CLI/boto3
import boto3
control_client = boto3.client('bedrock-agentcore-control', region_name='us-west-2')
response = control_client.create_harness_endpoint(
harnessId='MyHarness-UuFdkQoXSL',
endpointName='production-endpoint',
targetVersion='2',
description='Production endpoint pinned to V2'
)
print(response)

Or with the AWS CLI:
aws bedrock-agentcore-control create-harness-endpoint \
--harness-id "MyHarness-UuFdkQoXSL" \
--endpoint-name "production-endpoint" \
--target-version "2" \
--description "Production endpoint pinned to V2"

Creating an endpoint

104

Listing harness versions and endpoints
You can list all versions of a harness by calling the ListHarnessVersions operation. To list the
endpoints for a harness, call ListHarnessEndpoints.
Example
AWS CLI/boto3
import boto3
control_client = boto3.client('bedrock-agentcore-control', region_name='us-west-2')
# List all versions of a harness
versions = control_client.list_harness_versions(
harnessId='MyHarness-UuFdkQoXSL'
)
for version in versions['harnessVersions']:
print(version)
# List all endpoints for a harness
endpoints = control_client.list_harness_endpoints(
harnessId='MyHarness-UuFdkQoXSL'
)
for endpoint in endpoints['endpoints']:
print(endpoint)

Or with the AWS CLI:
aws bedrock-agentcore-control list-harness-versions \
--harness-id "MyHarness-UuFdkQoXSL"
aws bedrock-agentcore-control list-harness-endpoints \
--harness-id "MyHarness-UuFdkQoXSL"

Both operations support pagination through maxResults and nextToken. To retrieve
the conﬁguration of a single endpoint, call GetHarnessEndpoint; to remove one, call
DeleteHarnessEndpoint.

Listing harness versions and endpoints

105


## Runtime versioning and endpoints (pp. 467–469)

• Check the issuer url - "issuer": "https://cognito-idp.useast-1.amazonaws.com/us-east-1_12345566" . This should match the iss claim value
in the token.
• client_id claim in the token must match one of the authorizer allowedClients entries if
provided
• Note the client id you provided when you created the agent
• Conﬁrm this matches the client_id claim in the decoded token
• aud claim in the token must match one of the authorizer allowedAudience entries, if provided
• Note the audience list you provided when you created the agent
• Conﬁrm this matches the aud claim in the decoded token
• Tokens are only valid for several minutes (the default Amazon Cognito expiry is 60 minutes).
Fetch a new token as needed.

AgentCore Runtime versioning and endpoints
Amazon Bedrock AgentCore implements automatic versioning for AgentCore Runtimes and lets
you manage diﬀerent conﬁgurations using endpoints.
Each AgentCore Runtime in Amazon Bedrock AgentCore is automatically versioned:
• When you create an AgentCore Runtime, AgentCore Runtime automatically creates version 1 (V1)
• Each update to the AgentCore Runtime creates a new version with a complete, self-contained
conﬁguration
• Versions are immutable once created
• Each version contains all the conﬁguration needed for execution

How endpoints reference versions
Endpoints provide a way to reference speciﬁc versions of your AgentCore Runtime:
• The DEFAULT endpoint automatically points to the latest version of your AgentCore Runtime
• Endpoints can point to speciﬁc versions, allowing you to maintain diﬀerent environments (e.g.,
development, staging, production)
AgentCore Runtime versioning and endpoints

467

• When you update an AgentCore Runtime, the DEFAULT endpoint is automatically updated to
point to the new version
• Endpoints must be explicitly updated to point to new versions
Example Updating an endpoint to a New Version
bedrock_agentcore_client = boto3.client('bedrock-agentcore', region_name='us-west-2')
response = bedrock_agentcore_client.update_agent_runtime_endpoint(
agentRuntimeId='agent-runtime-12345',
endpointName='production-endpoint',
agentRuntimeVersion='v2.1',
description='Updated production endpoint'
)
print(response)

Versioning scenarios
The following table illustrates how versioning and endpoints interact during the lifecycle of an
AgentCore Runtime:
Change Type

Version Creation
Behavior

Latest Version

Endpoint Behavior

Initial Creation

Creates Version 1
(V1) automatically

V1

DEFAULT points to V1

Protocol Change

Creates a new
version with updated
protocol settings

V2

DEFAULT automatic
ally updates to V2

Create "PROD"
endpoint with V2

No new version
created

V2

PROD endpoint
points to V2

Container Image
Update

Creates a new version
with new container
reference

V3

DEFAULT updates to
V3, PROD remains on
V2

Versioning scenarios

468

Change Type

Version Creation
Behavior

Latest Version

Endpoint Behavior

Update "PROD" to V3

No new version
created

V3

PROD updates to V3

Network Settings
Modiﬁcation

Creates a new version
with updated security
parameters

V4

DEFAULT updates to
V4, PROD remains on
V3

Endpoint lifecycle states
AgentCore Runtime endpoints go through various states during their lifecycle:
CREATING
Initial state when an endpoint is being created
CREATE_FAILED
Indicates creation failure due to permissions, container, or other issues
READY
Endpoint is ready to accept requests
UPDATING
Endpoint is being updated to a new version
UPDATE_FAILED
Indicates update operation failure

Listing AgentCore Runtime versions and endpoints
You can list all versions of an AgentCore Runtime by calling the ListAgentRuntimeVersions
operation. To list the endpoints for an AgentCore Runtime, call ListAgentRuntimeEndpoints.

Endpoint lifecycle states

469


## Invocation error handling and best practices (pp. 470–473)

Invoke an AgentCore Runtime agent
The InvokeAgentRuntime operation lets you send requests to speciﬁc AgentCore Runtime
endpoints identiﬁed by their Amazon Resource Name (ARN) and receive streaming responses
containing the agent’s output. The API supports session management through session identiﬁers,
enabling you to maintain conversation context across multiple interactions. You can target speciﬁc
agent endpoints using optional qualiﬁers.
To call InvokeAgentRuntime , you need bedrock-agentcore:InvokeAgentRuntime
permissions. In the call you can also pass a bearer token that the agent can use for user
authentication.
The InvokeAgentRuntime operation accepts your request payload as binary data up to 100 MB
in size and returns a streaming response that delivers chunks of data in real-time as the agent
processes your request. This streaming approach allows you to receive partial results immediately
rather than waiting for the complete response, making it ideal for interactive applications.
To execute shell commands (such as running tests, git operations, or environment setup) in the
same session, use the Execute shell commands in AgentCore Runtime sessions operation. Both
operations work on the same agent runtime and session.
If you plan on integrating your agent with OAuth, you can’t use the AWS SDK to call
InvokeAgentRuntime . Instead, make a HTTPS request to InvokeAgentRuntime. For more
information, see Authenticate and authorize with Inbound Auth and Outbound Auth.

Invoke streaming agents
The following example shows how to use boto3 to invoke an agent runtime:
import boto3
import json
# Initialize the Bedrock AgentCore client
agent_core_client = boto3.client('bedrock-agentcore')
# Prepare the payload
payload = json.dumps({"prompt": prompt}).encode()
# Invoke the agent
response = agent_core_client.invoke_agent_runtime(
Invoke an agent

470

agentRuntimeArn=agent_arn,
runtimeSessionId=session_id,
payload=payload
)

# Process and print the response
if "text/event-stream" in response.get("contentType", ""):
# Handle streaming response
content = []
for line in response["response"].iter_lines(chunk_size=10):
if line:
line = line.decode("utf-8")
if line.startswith("data: "):
line = line[6:]
print(line)
content.append(line)
print("\nComplete response:", "\n".join(content))
elif response.get("contentType") == "application/json":
# Handle standard JSON response
content = []
for chunk in response.get("response", []):
content.append(chunk.decode('utf-8'))
print(json.loads(''.join(content)))
else:
# Print raw response for other content types
print(response)

Invoke multi-modal agents
You can use the InvokeAgentRuntime operation to send multi-modal requests that include both
text and images. The following example shows how to invoke a multi-modal agent:
import boto3
import json
import base64
# Read and encode image
with open("image.jpg", "rb") as image_file:
image_data = base64.b64encode(image_file.read()).decode('utf-8')
Invoke multi-modal agents

471

# Prepare multi-modal payload
payload = json.dumps({
"prompt": "Describe what you see in this image",
"media": {
"type": "image",
"format": "jpeg",
"data": image_data
}
}).encode()
# Invoke the agent
response = agent_core_client.invoke_agent_runtime(
agentRuntimeArn=agent_arn,
runtimeSessionId=session_id,
payload=payload
)

Session management
The InvokeAgentRuntime operation supports session management through the
runtimeSessionId parameter. By providing the same session identiﬁer across multiple requests,
you can maintain conversation context, allowing the agent to reference previous interactions.
To start a new conversation, generate a unique session identiﬁer. To continue an existing
conversation, use the same session identiﬁer from previous requests. This approach enables you to
build interactive applications that maintain context over time.

Tip
For best results, use a UUID or other unique identiﬁer for your session IDs to avoid collisions
between diﬀerent users or conversations.

Error handling
When using the InvokeAgentRuntime operation, you might encounter various errors. Here are
some common errors and how to handle them:

Session management

472

ValidationException
Occurs when the request parameters are invalid. Check that your agent ARN, session ID, and
payload are correctly formatted.
ResourceNotFoundException
Occurs when the speciﬁed agent runtime cannot be found. Verify that the agent ARN is correct
and that the agent exists in your AWS account.
AccessDeniedException
Occurs when you don’t have the necessary permissions. Ensure that your IAM policy includes
the bedrock-agentcore:InvokeAgentRuntime permission.
ThrottlingException
Occurs when you exceed the request rate limits. Implement exponential backoﬀ and retry logic
in your application.
RetryableConﬂictException
Occurs (HTTP 409) when a second operation targets a session while the service is provisioning
or tearing down that session. The message is Session operation in progress, please
retry. This condition is transient and retryable. The window is brief and already-running
sessions are not aﬀected. Retry with short exponential backoﬀ. The AWS SDKs auto-retry this
exception when default retries are enabled. If you disabled retries or call the API directly, retry it
yourself.
Implement proper error handling in your application to provide a better user experience and to
troubleshoot issues eﬀectively.

Best practices
Follow these best practices when using the InvokeAgentRuntime operation:
• Validate the prompt ﬁeld is a string in your agent entrypoint—The payload arrives as parsed
JSON, so the prompt ﬁeld can be any JSON type (string, list, object). If a non-string value
containing a toolUse content block reaches your agent framework, the framework might
execute the named tool directly. Model reasoning and guardrail evaluation are bypassed. Always
enforce isinstance(prompt, str) before passing input to the agent. For more information,
see Security best practices for AgentCore Runtime.
Best practices

473


## Runtime security best practices and troubleshooting (pp. 499–530)

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

• Session isolation and data protection
• IAM and least privilege
• Resource-based policies and cross-account access
• Confused deputy prevention
• Input validation
• Front your runtime with an AgentCore Gateway
• Authentication best practices
• Credential and secret management
• Network security
• Encryption
• Auditing and monitoring
• Shared responsibility model
• Command execution security
• VM platform server

Session isolation and data protection
Amazon Bedrock AgentCore Runtime provides strong isolation boundaries through dedicated
microVMs. Follow these practices to maintain data protection:
• Understand the isolation boundary — Each user session runs in a dedicated microVM with
isolated CPU, memory, and ﬁlesystem. Commands and agent code cannot access other
customers' workloads or escape the VM boundary. After session completion, the entire microVM
is terminated and memory is sanitized.
• Enforce session-to-user mappings in your backend — AgentCore does not enforce sessionto-user mappings. Your client backend must maintain the relationship between users and their
session IDs, and implement lifecycle management such as maximum number of sessions per user.
• Be aware of ﬁlesystem permission behavior — When using persistent ﬁle systems, permissions
are stored but not enforced within the session. chmod and stat work correctly, but access checks
always succeed because the agent runs as the only user in the microVM.
• Understand credential exposure within the VM — Any code or actor running inside the
microVM can access execution role credentials by calling the metadata endpoint (MMDS). Scope
your execution role permissions carefully. For more information, see Credentials Management.
Session isolation and data protection

500

IAM and least privilege
Apply the principle of least privilege to all IAM policies associated with your AgentCore Runtime
resources:
• Do not use CLI-generated policies in production — The IAM policies created by the AgentCore
CLI are designed for development and testing purposes. These permissions grant broad access
and are not suitable for production. Create custom IAM policies that restrict permissions to
only the speciﬁc resources and actions required. For the full reference, see IAM Permissions for
AgentCore Runtime.
• Scope permissions to speciﬁc runtime ARNs — Avoid wildcard resource statements. Use the full
ARN of your runtime resources in IAM policy Resource ﬁelds.
• Restrict InvokeAgentRuntimeForUser — Only trusted principals should have this
permission. Scope it to speciﬁc runtime resources using IAM resource conditions.
• Deny user-id delegation where not needed — For runtimes where user-id delegation is not
required, explicitly deny the action:
{
"Statement": [
{
"Sid": "DenyUserIdDelegation",
"Effect": "Deny",
"Action": "bedrock-agentcore:InvokeAgentRuntimeForUser",
"Resource": "arn:aws:bedrock-agentcore:REGION:ACCOUNT_ID:runtime/*"
}
]
}

• Prevent privilege escalation — Ensure that the execution role associated with your runtime
has equal or fewer privileges than the principals who can invoke it. For more information, see
Credentials Management.
• Use IAM condition keys to enforce VPC deployments — Use bedrock-agentcore:subnets
and bedrock-agentcore:securityGroups condition keys to require that all runtimes are
deployed in approved VPCs. For examples, see Use VPC condition keys with AgentCore Runtime.
• Use IAM Access Analyzer — Validate your IAM policies to ensure they adhere to best practices
and least-privilege principles.

IAM and least privilege

501

Resource-based policies and cross-account access
Resource-based policies provide ﬁne-grained access control directly on your runtime resources:
• Understand hierarchical authorization — For runtime API operations
such as InvokeAgentRuntime, InvokeAgentRuntimeCommand, and
InvokeAgentRuntimeCommandShell, AWS evaluates policies on both the agent runtime and
the agent endpoint. Both must allow the action.
• Conﬁgure both resources for cross-account access — To grant cross-account access, create
resource-based policies on both the agent runtime and the agent endpoint. If either resource
lacks an explicit allow, the request is denied.
• Remember that explicit deny always wins — If any policy (identity-based or resource-based)
explicitly denies an action, access is denied regardless of other policies.
For complete details, see Resource-based policies for Amazon Bedrock AgentCore.

Confused deputy prevention
Protect your execution roles from the confused deputy problem by using global condition context
keys in trust policies:
• Use aws:SourceArn and aws:SourceAccount — Add these conditions to your execution role
trust policy to limit which AgentCore resources can assume the role:
{
"Statement": [
{
"Effect": "Allow",
"Principal": {
"Service": "bedrock-agentcore.amazonaws.com"
},
"Action": "sts:AssumeRole",
"Condition": {
"StringEquals": {
"aws:SourceAccount": "123456789012"
},
"ArnLike": {
"aws:SourceArn": "arn:aws:bedrock-agentcore:us-east-1:123456789012:*"
}
}
Resource-based policies and cross-account access

502

}
]
}

• Use the full ARN when possible — If you know the speciﬁc runtime resource, use its full ARN in
aws:SourceArn instead of wildcards.
For more information, see Cross-service confused deputy prevention.

Input validation
Validate all input that your agent entrypoint receives before passing it to an agent framework:
• Enforce string type on the prompt ﬁeld—The payload your entrypoint receives is parsed from
arbitrary JSON. A caller can send a non-string value (such as a list or object) in the prompt ﬁeld.
If your agent framework accepts non-string content blocks—particularly toolUse blocks—the
framework might dispatch a tool directly. This bypasses model reasoning, guardrails, and system
prompt enforcement. Always validate that the prompt is a string before passing it to the agent:
@app.entrypoint
def invoke(payload, context):
user_message = payload.get("prompt", "")
if not isinstance(user_message, str) or not user_message.strip():
return {"error": "Invalid input: 'prompt' must be a non-empty string"}
result = agent(user_message)
return {"response": result.message}

• Reject or strip toolUse content blocks—If your agent accepts structured message arrays (for
multi-turn conversation), ﬁlter out any toolUse content blocks from user-supplied messages. A
toolUse block in the message history can cause the agent framework’s event loop to execute
the named tool immediately without model evaluation.
• Validate payload structure with a schema—Use Pydantic, Zod, or an equivalent schema library
to enforce that the request body conforms to your expected structure. Deﬁne prompt as str
(not Any) in your schema:
from pydantic import BaseModel
class InvocationRequest(BaseModel):
prompt: str # Enforces string type at the schema level

Input validation

503

• Do not rely on default values as validation—A pattern like payload.get("prompt",
"Hello") provides a default but does not reject non-string input. The value returned is
whatever the caller sent, which might be a dict or list containing content blocks.

Front your runtime with an AgentCore Gateway
A common pattern is to front your AgentCore Runtime with an AgentCore Gateway so that the
gateway becomes the single, governed entry point to the runtime. Placing a gateway in front lets
you apply controls outside of the agent’s own environment:
• Policy-based authorization — Use the gateway’s policy engine to control which callers can
invoke which targets and under what conditions. For more information, see Use policies to
control access to gateway targets.
• Guardrails — Apply Amazon Bedrock Guardrails through the policy engine to screen requests
and responses. For more information, see Use guardrails in policies.
• Request and response interceptors — Inspect or transform traﬃc with interceptor Lambda
functions conﬁgured on the gateway.
These controls only protect you if all traﬃc actually ﬂows through the gateway. If a caller can
reach the runtime directly, it bypasses the gateway’s policies, guardrails, and interceptors entirely.
To prevent this, restrict the runtime to accept invocations only when they originate from your
gateway. How you do this depends on the runtime’s inbound authorization type:
• IAM (SigV4) runtimes — Attach a resource-based policy that restricts invocation to the
gateway’s execution role. See Restrict IAM (SigV4) inbound invocation to your gateway.
• OAuth (JWT) runtimes — Conﬁgure allowedWorkloadConfiguration on the runtime’s
authorizer. See Restrict invocation to your gateway.
To set this up, you create the gateway, deploy your runtime, and then add the runtime as a
gateway target on that gateway. For the target conﬁguration, outbound authorization, and the
invocation URL format, see AgentCore Runtime targets.

Authentication best practices
AgentCore Runtime supports IAM SigV4 and JWT bearer token authentication. Follow these
practices to secure access:
Front your runtime with an AgentCore Gateway

504

• Choose the right authentication method — Use IAM SigV4 for service-to-service calls within
AWS. Use JWT bearer token authentication when end users authenticate directly through an
identity provider. A runtime can support one method at a time; create separate versions for
diﬀerent authentication types.
• Prefer JWT-based user identiﬁcation for production — When your agent
retrieves OAuth tokens on behalf of end users, prefer the JWT bearer token path
(GetWorkloadAccessTokenForJWT), which validates the token’s issuer, signature, and expiry.
The UserId path (GetWorkloadAccessTokenForUserId / X-Amzn-Bedrock-AgentCoreRuntime-User-Id header) treats the user identiﬁer as an opaque string without IdP veriﬁcation
— use it only for development, quickstart scenarios, or enterprise architectures that resolve user
identity upstream. For more information, see Get workload access token.
• Conﬁgure JWT authorizers completely — When using JWT authentication, conﬁgure all
available validation ﬁelds: discovery URL, allowed audiences, allowed clients, allowed scopes, and
required custom claims.
• Never hardcode tokens in production code — Use secure token retrieval mechanisms.
Hardcoded tokens are a security risk in source control and deployed artifacts.
• Derive user-id from the authenticated principal — If you use the X-Amzn-BedrockAgentCore-Runtime-User-Id header, the value should be derived from the authenticated
principal’s context (IAM caller identity or user token claims), not from arbitrary client-supplied
values. This prevents authenticated users from impersonating other users.
• Deny ForUserId where not needed — For workloads that always have a JWT available,
explicitly deny bedrock-agentcore:GetWorkloadAccessTokenForUserId and bedrockagentcore:InvokeAgentRuntimeForUser in IAM policies. This ensures all user identiﬁcation
goes through the cryptographically veriﬁed JWT path.
• Conﬁgure VPC endpoint policies for your auth method — VPC endpoint policies can only
restrict callers based on IAM principals, not OAuth users. For OAuth-based requests, set
Principal to * in the endpoint policy. For SigV4-based authentication, specify the allowed IAM
identities.
For implementation details, see Authenticate and authorize with Inbound Auth and Outbound
Auth.

Credential and secret management
Protect credentials used by your agents and runtime environments:
Credential and secret management

505

• Use AgentCore Identity for outbound authentication — AgentCore Identity manages OAuth
credentials and API keys securely, preventing credential exposure in agent code or logs. Use it for
all third-party service access (Slack, GitHub, Zoom).
• Understand MMDS credential exposure — The MicroVM Metadata Service (MMDS) provides
execution role credentials to any code running in the VM, similar to EC2’s IMDS. Scope execution
role permissions to only what your agent requires.
• Enable MMDSv2 — Starting June 30, 2026, your agent runtimes must have MMDSv2
enabled. Runtimes without MMDSv2 enabled cannot be invoked and return a
ValidationException. To enable, call UpdateAgentRuntime with requireMMDSV2 set
to true in metadataConfiguration. For more information about resolving this error, see
MMDSv2 ValidationException troubleshooting.
• Run containers as non-root users — When building custom container images, conﬁgure them to
run as a non-root user. This limits the impact of potential code execution vulnerabilities.
• Separate user-delegated and autonomous credentials — Use user-delegated authentication
(Authorization Code Grant) when your agent acts on behalf of a speciﬁc user. Use autonomous
authentication (Client Credentials Grant) when the agent operates independently.
For more information, see Credentials Management and AgentCore Identity.

Network security
Secure network access to and from your AgentCore Runtime environments:
• Deploy runtimes in a VPC for private resource access — Conﬁgure VPC connectivity to access
private databases, internal APIs, and services without exposing them to the internet. For
conﬁguration details, see Conﬁgure AgentCore Runtime for VPC.
• Use AWS PrivateLink for API access — Create interface VPC endpoints for the AgentCore
data plane (com.amazonaws.region.bedrock-agentcore) and control plane
(com.amazonaws.region.bedrock-agentcore-control) to avoid internet traversal. For
more information, see Use AWS PrivateLink.
• Apply least privilege to security groups — Deﬁne outbound rules that allow only the minimum
required traﬃc. Do not open broad outbound access unless necessary.
• Conﬁgure required VPC endpoints for container agents — For VPC-mode container
agents, conﬁgure VPC endpoints for ECR (com.amazonaws.region.ecr.dkr,
com.amazonaws.region.ecr.api), S3 (com.amazonaws.region.s3 gateway endpoint),
Network security

506

and CloudWatch Logs (com.amazonaws.region.logs). The S3 gateway endpoint eliminates
NAT gateway data processing charges for ECR image layer pulls.
• Scope the S3 gateway endpoint policy for container agents — Restrict the S3 gateway
endpoint policy to only the bucket that Amazon ECR uses for image layer storage:
{
"Statement": [
{
"Sid": "AllowECRLayerAccess",
"Principal": "*",
"Action": [
"s3:GetObject"
],
"Effect": "Allow",
"Resource": ["arn:aws:s3:::prod-region-starport-layer-bucket/*"]
}
]
}

Replace region with your AWS Region identiﬁer (for example, us-east-2).
• Scope the S3 gateway endpoint policy for direct code deploy agents — For zip-based
deployments, restrict the policy to the internal service-owned code artifact bucket. Add an
aws:PrincipalServiceName condition to ensure only the AgentCore service principal can
access buckets through this endpoint policy:
{
"Statement": [
{
"Effect": "Allow",
"Principal": "*",
"Action": "s3:GetObject",
"Resource": [
"arn:aws:s3:::acr-code-*-region-an",
"arn:aws:s3:::acr-code-*-region-an/*"
],
"Condition": {
"StringEquals": {
"aws:PrincipalServiceName": "bedrock-agentcore.amazonaws.com"
}
}
}
Network security

507

]
}

Replace region with your AWS Region identiﬁer (for example, us-west-2). The AgentCore
code artifact buckets are created in Account regional namespace general purpose buckets. Only
AWS can own the actual bucket names used by the service. The aws:PrincipalServiceName
condition ensures that only the AgentCore service principal can access buckets through this
endpoint policy. If you also use persistent ﬁle systems, add the session storage bucket to this
policy. For more information, see Conﬁgure AgentCore Runtime for VPC.
• Use private subnets with NAT gateways — Public subnets do not provide internet access for
AgentCore Runtime. Always place runtime ENIs in private subnets with a route to a NAT gateway
for outbound internet access.
• Transport security — All connections use TLS 1.2 or higher. WebSocket connections, including
InvokeAgentRuntimeCommandShell, use WSS (WebSocket Secure) over HTTPS exclusively.
Plaintext ws:// connections are not supported.
• Enforce header limits — Custom headers are limited to 4KB per value and 20 headers per
runtime. The Authorization header is reserved for agents with OAuth inbound access.

Encryption
AgentCore Runtime protects data with encryption at rest and in transit:
• Encryption in transit — All communication between clients and AgentCore Runtime, and
between AgentCore Runtime and its dependencies, is protected using TLS 1.2 or higher. This is
conﬁgured by default and requires no additional setup.
• Encryption at rest — Data at rest is encrypted using AWS owned encryption keys from AWS Key
Management Service (AWS KMS) by default.
• Use TLS 1.3 where possible — While TLS 1.2 is the minimum, AWS recommends TLS 1.3 for
improved security and performance.
For more information, see Data encryption.

Auditing and monitoring
Implement comprehensive auditing to detect and investigate security events:
Encryption

508

• Enable CloudTrail logging — AWS CloudTrail records API calls
including InvokeAgentRuntime, InvokeAgentRuntimeCommand,
InvokeAgentRuntimeCommandShell, and control plane operations. Each record includes
caller identity, timestamp, source IP address, and response status.
• Use CloudWatch Logs for command auditing — AgentCore Runtime sends the request ID and
input command to your agent’s CloudWatch Logs log group. Use these logs to maintain an audit
trail of commands executed in your sessions.
• Correlate logs using request IDs — Use the request ID to correlate CloudTrail records (who
called the API) with CloudWatch Logs (what command was executed).
• Set up metric ﬁlters and alarms — Conﬁgure CloudWatch Logs metric ﬁlters to detect
unexpected command patterns or unauthorized access attempts. Create alarms to notify your
team of anomalies.
• Log user-id delegation relationships — When using the X-Amzn-Bedrock-AgentCoreRuntime-User-Id header, log the relationship between the authenticated IAM principal and
the user-id value for audit purposes.
• Enable VPC Flow Logs — For VPC-connected runtimes, enable VPC Flow Logs to audit networklevel traﬃc and identify unexpected communication patterns.
• Review CloudTrail logs regularly — Periodically review logs for unauthorized access attempts,
especially for sensitive workloads.

Shared responsibility model
Understand the division of security responsibilities between AWS and you:
AWS responsibilities:
• Secure infrastructure and microVM isolation at the hardware level
• OS kernel patching for all deployment modes
• Language runtime patching for direct code deployments
• Network infrastructure security
• Service availability and resilience
Your responsibilities:
• Agent code security and dependency management
Shared responsibility model

509

• IAM access controls and resource policies
• Security of commands executed in runtime sessions
• Session-to-user mapping enforcement
• Container image updates (for container deployments) — rebuild with the latest secure base
image regularly
• Input validation and prompt injection prevention — including validating InvokeHarness input
when using the managed harness (see Harness shares the AgentCore Runtime trust boundary)
• Network conﬁguration (security groups, VPC endpoints, route tables)

Important
For direct code deployments, AgentCore Runtime applies security patches to the runtime
OS automatically. AgentCore Runtime does not apply security patches to programming
language runtimes after they reach their end of support date. Deprecated runtimes are
provided as-is and may contain unpatched vulnerabilities. For supported runtimes, see
Supported runtimes for code deployment.

Note
Security patches can expose issues with existing code that relies on previous insecure
behavior. If this risk is not acceptable, use container images to deploy your agent.

Harness shares the AgentCore Runtime trust boundary
The managed harness is built on AgentCore Runtime. It does not add a security layer between the
caller and the microVM. The security boundary is the same as AgentCore Runtime: IAM or JWT
authentication combined with microVM isolation.
For the full harness security model, including trust boundary details, model conﬁguration
parameter risks, and input validation guidance, see Harness shared responsibility model.

Command execution security
AgentCore Runtime provides two command execution APIs:
Command execution security

510

• InvokeAgentRuntimeCommand — One-shot, non-interactive command execution over HTTP/2.
IAM action: bedrock-agentcore:InvokeAgentRuntimeCommand.
• InvokeAgentRuntimeCommandShell — Interactive WebSocket shell session with persistent
PTY access. IAM action: bedrock-agentcore:InvokeAgentRuntimeCommandShell.
Both APIs operate within the same microVM isolation boundary and share the same security model.
Apply these practices to both:
• Understand the security boundary — Commands have full access to the container ﬁlesystem
and any conﬁgured credentials or secrets within the microVM. The isolation boundary is the
microVM itself. Under the shared responsibility model, you are responsible for the security of any
code executed in your runtime container.
• Use deterministic operations for deterministic tasks — Use InvokeAgentRuntimeCommand
or InvokeAgentRuntimeCommandShell for operations like tests, git, and builds. Don’t route
deterministic operations through the LLM via InvokeAgentRuntime.
• Restrict who can execute commands — Use IAM policies to limit which principals can call
InvokeAgentRuntimeCommand or InvokeAgentRuntimeCommandShell. Not all users who
can invoke an agent should be able to execute arbitrary commands. Example resource ARN:
arn:aws:bedrock-agentcore:us-west-2:123456789012:runtime/my-agent.
• WebSocket shell uses wss:// only — InvokeAgentRuntimeCommandShell connections are
established exclusively over WSS (WebSocket Secure). Plaintext ws:// connections are not
supported. Callers authenticate via SigV4 at WebSocket upgrade.
• Keep traﬃc within your network — Conﬁgure VPC endpoints to avoid internet traversal for
command execution API calls.
• Set appropriate timeouts — Conﬁgure command timeouts based on expected execution
duration to prevent resource waste from runaway processes.
For complete details, see Execute commands in runtime sessions.

VM platform server
Each AgentCore Runtime microVM includes a platform server running on localhost. This server
manages VM session lifecycle, storage operations, and provides shell access to support runtime
operations. The platform server runs entirely within the agent’s microVM, which is the isolation

VM platform server

511

boundary — it contains no service-critical infrastructure code and has no access to other sessions
or customers' workloads.
Important
Everything running within the microVM, including interactions with the platform server, is
your responsibility under the shared responsibility model. If agent code or tools interact
with the platform server, the impact is limited to the current VM session — it cannot aﬀect
other sessions or cross isolation boundaries. However, unauthorized access can disrupt the
session’s VM lifecycle or provide shell access within that session.

Follow these practices to limit unnecessary access to the platform server:
• Restrict localhost access in agent code — Conﬁgure your agent and any networking tools to
prevent unrestricted access to localhost. Agent code should not make arbitrary HTTP calls to
localhost unless required for a speciﬁc integration.
• Allowlist only required ports for sidecar setups — If your architecture uses a container-incontainer or sidecar pattern on localhost, explicitly allowlist only the speciﬁc ports your sidecar
services use. Do not open broad localhost access.
• Audit network tools for localhost reach — Review any tools you provide to your agent (such
as HTTP request tools or general networking utilities) to ensure they cannot make unintended
requests to localhost endpoints. Apply URL ﬁltering or allowlisting at the tool level.

Troubleshoot AgentCore Runtime
This troubleshooting topic helps you identify and resolve common issues when working with
AgentCore Runtime. By following these solutions, you can quickly diagnose and ﬁx problems with
your agent runtimes.
Topics
• My agent invocations fail with "This runtime is not MMDSv2-enabled" ValidationException
• My agent invocations fail with 504 Gateway Timeout errors
• My Docker build fails with "403 Forbidden" when pulling Python base images
• I get "Unknown service: 'bedrock-agent-core-runtime'" error when using boto3
• I get "AccessDeniedException" when trying to create an Amazon Bedrock AgentCore Runtime
Troubleshoot

512

• My Docker build fails with "exec /bin/sh: exec format error"
• What are the requirements for Docker containers used with Amazon Bedrock AgentCore
Runtime?
• My long-running tool gets interrupted after 15 minutes
• My idle sessions are not being released and I am exhausting my session quota
• How do I access the runtimeSessionId in my agent code for tagging or grouping resources?
• I have RuntimeClientError (403) issues
• I have missing or empty CloudWatch Logs
• I have payload format issues
• I need help understanding HTTP error codes
• I need recommendations for testing my agent
• I need help debugging container issues
• I need help troubleshooting MCP protocol agents
• I need help troubleshooting bidirectional streaming using WebSocket
• My code changes aren’t reﬂected in existing sessions
• Spans are missing when my runtime is invoked from a Lambda function
• My S3 Files or EFS mount fails with "Access denied"
• My S3 Files or EFS mount fails with "ResourceNotFound"
• My S3 Files or EFS mount times out
• I get "Permission Denied" when writing to my mounted ﬁlesystem
• My container fails to start with HTTP 424 error on high-layer images
• My capacity provider is in state CREATE_FAILED
• My agents on Instances do not have access to their credentials
• Best practices

My agent invocations fail with "This runtime is not MMDSv2-enabled"
ValidationException
When this occurs: When invoking an agent runtime via InvokeAgentRuntime,
ExecuteCommand, InvokeAgentRuntimeWithWebSocketStream,
InvokeAgentRuntimeCommandShell, or GetAgentCard
My agent invocations fail with "This runtime is not MMDSv2-enabled" ValidationException

513

Why this happens: Starting June 30, 2026, Amazon Bedrock AgentCore Runtime requires all agent
runtimes to use MMDSv2 (MicroVM Metadata Service Version 2). The service rejects invocations
targeting runtimes without metadataConfiguration set, or with requireMMDSV2 set to false
or null.
Solution: Call UpdateAgentRuntime with requireMMDSV2 set to true in
metadataConfiguration:
import boto3
client = boto3.client('bedrock-agentcore-control', region_name='us-west-2')
try:
client.update_agent_runtime(
agentRuntimeId='your-agent-runtime-id',
metadataConfiguration={
'requireMMDSV2': True
}
)
print("MMDSv2 enabled successfully.")
except client.exceptions.ResourceNotFoundException as e:
print(f"Runtime not found: {e}")
except Exception as e:
print(f"Error enabling MMDSv2: {e}")

After you update, new invocations will succeed. Existing sessions are not aﬀected.

My agent invocations fail with 504 Gateway Timeout errors
When this occurs: During agent invocation via SDK or console
Why this happens: Multiple factors can prevent your agent from responding within the timeout
period
Several factors can cause this:
• Container Issues: Make sure your Docker image exposes port 8080 and has the /invocations
path
• ARM64 Compatibility: Currently your container must be ARM64 compatible
• Retry Logic: Review retry mechanisms for handling transient issues
My agent invocations fail with 504 Gateway Timeout errors

514

My Docker build fails with "403 Forbidden" when pulling Python base
images
When this occurs: During docker build or docker run when using public.ecr.aws base
images
Why this happens: ECR Public authentication issues — expired or missing authentication is a
common issue.
Solution: Either login to ECR Public or logout completely:
# Option 1: Login to ECR Public
aws ecr-public get-login-password --region us-east-1 | docker login --username AWS -password-stdin public.ecr.aws
# Option 2: Logout (recommended for avoiding token expiration)
docker logout public.ecr.aws
# Option 3: Use Docker Hub directly in Dockerfile
FROM python:3.10-slim
# instead of public.ecr.aws/docker/library/python:3.10-slim

I get "Unknown service: 'bedrock-agent-core-runtime'" error when
using boto3
When this occurs: When invoking Amazon Bedrock AgentCore APIs using boto3 SDK
Why this happens: Outdated boto3 library — common issue as most installations don’t have latest
SDK
Solution: Update to latest boto3 and botocore versions:
pip install --upgrade boto3 botocore
# Minimum versions: boto3 1.39.8+, botocore 1.33.8+

I get "AccessDeniedException" when trying to create an Amazon
Bedrock AgentCore Runtime
When this occurs: During agent creation via console, SDK, or CLI
My Docker build fails with "403 Forbidden" when pulling Python base images

515

Why this happens: Either your user lacks permissions, or the execution role isn’t properly
conﬁgured for Amazon Bedrock AgentCore
Solution: Several factors can cause this:
• Missing permissions for the caller. Make sure that the caller’s credentials has bedrockagentcore:CreateAgentRuntime.
• Execution Role cannot be assumed by Amazon Bedrock AgentCore. Make sure that the
execution role follows this guidance on permissions for Amazon Bedrock AgentCore Runtime
execution role.

My Docker build fails with "exec /bin/sh: exec format error"
When this occurs: When building containers for Amazon Bedrock AgentCore deployment
Why this happens: Building ARM64 containers on x86 systems without proper cross-platform
setup
Solution: Build ARM64 compatible containers. You can consider using buildx for cross-platform
builds. Alternatively, you can use CodeBuild. For example code, see the Amazon Bedrock AgentCore
Samples.

What are the requirements for Docker containers used with Amazon
Bedrock AgentCore Runtime?
Review Amazon Bedrock AgentCore Runtime requirements for full details.
In summary, your Docker container must meet these requirements:
• Port: Expose port 8080 (additional ports will be supported soon)
• Endpoint: Must have /invocations path available
• Architecture: Must be ARM64 compatible
• Response: Should handle the expected payload format

My long-running tool gets interrupted after 15 minutes
For information, see Handle asynchronous and long-running agents with Amazon Bedrock
AgentCore Runtime for full details.
My Docker build fails with "exec /bin/sh: exec format error"

516

When this occurs: During long-running agent operations or complex workﬂows
Why this happens: Amazon Bedrock AgentCore automatically terminates sessions after 15 minutes
of inactivity. The platform determines activity from the /ping response: a session reporting
HealthyBusy is kept alive, while a session reporting Healthy is treated as idle-eligible and its
idle time is measured from when the status last changed (see the time_of_last_update ﬁeld
below).
Solution: Ensure your /ping endpoint returns HealthyBusy while background work is in
progress:
{"status": "HealthyBusy"}

If you are using the Bedrock AgentCore SDK, the ping response is handled automatically. For
custom implementations, ensure your ping handler returns HealthyBusy while processing.

My idle sessions are not being released and I am exhausting my session
quota
When this occurs: Session count climbs continuously under load and sessions are not released
after the idle timeout (for example, ServiceQuotaExceededException / maxVms errors during
a burst of invocations), even though each session is idle.
Why this happens: When a session reports Healthy, the platform measures how long it has been
idle from the time_of_last_update ﬁeld in your /ping response, which must reﬂect when the
status last changed. If your ping handler sets time_of_last_update to the current time on
every ping, the reported idle time keeps resetting, which prevents the idle timeout from ﬁring.
Sessions then live until MaxLifetime and can exhaust your session quota.
Solution: Update time_of_last_update only when the status actually changes, or omit it
entirely so the platform tracks status changes on its own:
{"status": "Healthy"}

If you are using the Bedrock AgentCore SDK, upgrade to the latest version, where the ping
response is handled correctly. As a stopgap, calling StopRuntimeSession releases stuck sessions.

My idle sessions are not being released and I am exhausting my session quota

517

How do I access the runtimeSessionId in my agent code for tagging or
grouping resources?
When this applies: You want to group, tag, or trace resources (e.g., S3 objects, logs) by the current
agent runtime session.
Solutions:
• If you’re using the Bedrock Agents SDK, use context.session_id.
• If you’re building a custom runtime server, extract it from the X-Amzn-Bedrock-AgentCoreRuntime-Session-Id HTTP header.
Solution 1: For agents using the Bedrock Amazon Bedrock AgentCore SDK, use
context.session_id from your agent entrypoint
@app.entrypoint
def my_agent(payload, context):
session_id = context.session_id
# Use session_id for S3 object tagging/organization
s3_client = boto3.client('s3')
s3_client.put_object(
Bucket='my-bucket',
Key=f'agent-outputs/{session_id}/output.json',
Body=json.dumps(result),
Tagging=f'SessionId={session_id}'
)
return result

Solution 2: For custom runtime HTTP servers
The runtime session ID is passed in this HTTP header. Parse it from the incoming request and use it
for tagging, correlation, or downstream propagation.
X-Amzn-Bedrock-AgentCore-Runtime-Session-Id: <value>

I have RuntimeClientError (403) issues
Problem
How do I access the runtimeSessionId in my agent code for tagging or grouping resources?

518

You receive a 403 "RuntimeClientError" when attempting to invoke your agent runtime.
Causes
This error typically occurs due to:
• Container startup failures
• Permissions issues with execution role
• Authentication issues with bearer token
Resolution
Follow these steps to resolve the issue:
1. Check CloudWatch Logs : Any issues with starting up the container will reﬂect as a 403 RuntimeClientError. Navigate to the following CloudWatch log group to check for startup errors:
/aws/bedrock-agentcore/runtimes/<agent_id>-<endpoint_name>/[runtime-logs]

2. Verify Execution Role : Ensure your agent’s execution role has the necessary permissions. For
more information, see AgentCore Runtime execution role.
3. Validate Authentication : For MCP protocol agents, ensure your bearer token is valid and not
expired.

I have missing or empty CloudWatch Logs
Problem
You encounter errors but don’t see any relevant logs in CloudWatch.
Solution
Try these approaches to diagnose the issue:
1. Check Correct Log Group : Ensure you’re looking in the right CloudWatch log group. The
standard pattern is:
/aws/bedrock-agentcore/runtimes/<agent_id>-<endpoint_name>/runtime-logs

I have missing or empty CloudWatch Logs

519

2. Run Locally for Diagnostics : If there are no CloudWatch Logs, try running the agent container
locally using the exact same payload you used for invocation in AgentCore Runtime. This can
help identify issues that might not be visible in the logs.
3. Enable Verbose Logging : Update your agent code to include more detailed logging, especially
around the entry points and any error handling logic.

I have payload format issues
Problem
Your agent runtime invocation fails even though the container starts successfully.
Resolution
Follow these steps to resolve payload format issues:
1. Verify Payload Structure : Ensure your payload structure matches what your agent expects. Pay
special attention to:
• If your agent code expects input keyword in the payload, make sure to include it:
{
"input": {
"prompt": "Your question here"
}
}

• Not just:
{
"prompt": "Your question here"
}

2. Check Documentation : Review the expected input format in the documentation.

I need help understanding HTTP error codes
Problem
Your agent returns HTTP error codes that are diﬃcult to interpret.
I have payload format issues

520

Example error message
You may see an error like:
An error occurred (RuntimeClientError) when calling the InvokeAgentRuntime operation:
Received error (<HTTP Status Code>) from runtime. Please check your CloudWatch logs
for more information

Resolution
Here are the most common error codes and their meanings:
422 Unprocessable Entity
This happens when the container encounters validation issues with the input payload.
Common causes:
• Missing required ﬁelds in the payload (e.g., missing "input" ﬁeld)
• Incorrect data types for ﬁelds
• Invalid format for the payload
403 Forbidden
Authentication or authorization issues.
Check your bearer token or IAM permissions.
409 RetryableConﬂictException
A second operation reached a session while it was still being provisioned or torn down. You see
the message Session operation in progress, please retry.
What it means: This is a transient, retryable conﬂict — not a terminal error. The window is brief.
Already-running sessions are not aﬀected.
How to ﬁx: Retry the operation with short exponential backoﬀ. For HTTP-based APIs (such as
InvokeAgentRuntime, InvokeAgentRuntimeCommand, and StopRuntimeSession), the
AWS SDKs auto-retry this when default retries are enabled. If you disabled retries or call the
API directly without an AWS SDK, add the retry yourself. For WebSocket-based APIs (such as
InvokeAgentRuntimeWithWebSocketStream and InvokeAgentRuntimeCommandShell),
the AWS SDKs do not auto-retry. Always retry these yourself.
I need help understanding HTTP error codes

521

500 Internal Server Error
Runtime exceptions in your agent code.
Check CloudWatch logs for detailed stack traces.

I need recommendations for testing my agent
To systematically debug agent runtime issues:
Test locally ﬁrst
Before deploying to AgentCore Runtime:
• Run your agent container locally using the same Docker image
• Verify it works with the exact same payload
Compare payloads
Ensure consistency between environments:
• Ensure the payload structure between local testing and AgentCore Runtime invocation is
identical
• Pay special attention to nesting of ﬁelds like "input" and "prompt"

I need help debugging container issues
If you suspect container-related issues:
Pull and run locally
Test your container image on your local machine:
docker pull <your-ecr-repo-uri>
docker run -p 8080:8080 <your-ecr-repo-uri>

Test with curl
Send test requests to your local container:
I need recommendations for testing my agent

522

curl -X POST http://localhost:8080/invocations \
-H "Content-Type: application/json" \
-d '{"input": {"prompt": "Hello world!"}}'

Check container logs
Examine the container’s output for errors:
docker logs <container-id>

I need help troubleshooting MCP protocol agents
For MCP protocol agents, follow these speciﬁc troubleshooting steps:
Verify endpoint path
MCP servers should listen on 0.0.0.0:8000/mcp/
Use MCP Inspector
Test with the MCP Inspector tool:
1. Install and run the MCP Inspector: npx @modelcontextprotocol/inspector
2. Connect to your local server at http://localhost:8000/mcp
3. For deployed agents, use the properly URL-encoded endpoint
Authentication issues
Check authentication conﬁguration:
• Ensure bearer token is correctly set in the headers
• Verify your Cognito user pool is correctly set up

I need help troubleshooting bidirectional streaming using WebSocket
For bidirectional streaming using WebSocket agents, follow these speciﬁc troubleshooting steps:
Verify endpoint conﬁguration
I need help troubleshooting MCP protocol agents

523

WebSocket agents must run on port 8080 and serve WebSocket connections at /ws path
Test locally with incremental complexity
Start with simple local testing before deploying:
1. Test basic connection: Verify your agent accepts WebSocket connections at ws://
localhost:8080/ws
2. Test message handling: Send simple text messages and verify responses
3. Test session management: Verify persistent conversations work as expected
4. Test error handling: Ensure your agent gracefully handles connection drops and malformed
messages
Authentication issues
Check authentication conﬁguration for deployed agents:
• For OAuth: Ensure bearer token is valid and not expired
• For SigV4: Make sure input to the signing algorithm is correct, including the WebSocket URL,
headers, and request method
• Use the correct authentication method that matches your agent’s conﬁguration
Common connection issues
Address common WebSocket connection problems:
• Verify message format compatibility between your agent and client expectations
• Conﬁgure message frame fragmentation or implement chunking to stay within message frame
size (64 KB) and message frame rate (250 frames per second) limits to prevent connection
closure

My code changes aren’t reﬂected in existing sessions
Problem
You’ve updated your agent runtime with new code, but existing sessions continue to use the old
version.
My code changes aren’t reﬂected in existing sessions

524

Why this happens
Each microVM session is created with the code assets ( agentRuntimeArtifact ) that were
deployed at the time of session creation. Once a session is established, it continues using that
version of the code until the session terminates, even when code assets are updated as part of
performing the UpdateAgentRuntime operation.
Solution
To access your updated code, use a new session ID.

Spans are missing when my runtime is invoked from a Lambda function
When this occurs: When invoking AgentCore Runtime from a Lambda function
Why this happens: Lambda generates its own X-Amzn-Trace-Id header. If the Lambda trace has
Sampled=0 , this unsampled context propagates to AgentCore Runtime and the runtime skips span
generation for that invocation.
Solution:
• Enable Lambda active tracing: Turn on X-Ray active tracing on your Lambda function so that it
produces sampled traces ( Sampled=1 ).
• Verify CloudWatch Transaction Search: Ensure you have completed the setup in Conﬁgure
observability and that your trace segment destination is set to CloudWatch Logs.
• Check the sampling decision: Log the _X_AMZN_TRACE_ID environment variable inside your
Lambda function. If it shows Sampled=0 , active tracing is not enabled or an upstream caller is
making the sampling decision.

My S3 Files or EFS mount fails with "Access denied"
When this occurs: During invocation of an agent with S3 Files or EFS storage conﬁgured
Why this happens: The execution role is missing required ﬁlesystem permissions. For more
information about conﬁguring persistent storage, see File system conﬁgurations for AgentCore
Runtime.
Solution:
Spans are missing when my runtime is invoked from a Lambda function

525

For S3 Files, ensure your execution role has:
{
"Effect": "Allow",
"Action": [
"s3files:ClientMount",
"s3files:ClientWrite"
],
"Resource": "arn:aws:s3files:<region>:<account>:file-system/*",
"Condition": {
"StringEquals": {
"s3files:AccessPointArn": "<your-access-point-arn>"
}
}
}

For EFS, ensure your execution role has:
{
"Effect": "Allow",
"Action": [
"elasticfilesystem:ClientMount",
"elasticfilesystem:ClientWrite"
],
"Resource": "arn:aws:elasticfilesystem:<region>:<account>:file-system/<fs-id>",
"Condition": {
"StringEquals": {
"elasticfilesystem:AccessPointArn": "<your-access-point-arn>"
}
}
}

Omit s3files:ClientWrite or elasticfilesystem:ClientWrite if your agent only needs
read access.

My S3 Files or EFS mount fails with "ResourceNotFound"
When this occurs: During invocation of an agent with S3 Files or EFS storage conﬁgured
Why this happens: The ﬁlesystem or access point was deleted after the agent was created, or the
IDs are incorrect.
My S3 Files or EFS mount fails with "ResourceNotFound"

526

Solution:
• Verify the ﬁlesystem exists:
• S3 Files: aws s3files list-file-systems --region <region>
• EFS: aws efs describe-file-systems --region <region>
• Verify the access point exists:
• S3 Files: aws s3files list-access-points --file-system-id <fs-id> --region
<region>
• EFS: aws efs describe-access-points --file-system-id <fs-id> --region
<region>
• Verify mount targets exist in all required availability zones:
• S3 Files: aws s3files list-mount-targets --file-system-id <fs-id> --region
<region>
• EFS: aws efs describe-mount-targets --file-system-id <fs-id> --region
<region>
• Ensure each mount target shows Available status and is in the same VPC as the agent runtime.
• If the resource was deleted, recreate it and update the agent runtime with the new access point
ARN

My S3 Files or EFS mount times out
When this occurs: During invocation of an agent with S3 Files or EFS storage conﬁgured. The
invocation may take longer than usual before failing.
Why this happens: The VPC network conﬁguration is blocking NFS traﬃc (port 2049) between the
agent’s compute and the ﬁlesystem mount targets.
Solution:
• Check security groups on mount targets: Verify the security group attached to your mount
targets allows inbound TCP on port 2049 from the security group used by your agent runtime
• Check security groups on agent runtime: Verify the security group used by your agent runtime
allows outbound TCP on port 2049 to the mount target security group
• Verify mount targets exist in the correct availability zones: Mount targets must exist in the
same availability zones as the subnets conﬁgured on your agent runtime:
My S3 Files or EFS mount times out

527

• S3 Files: aws s3files list-mount-targets --file-system-id <fs-id> --region
<region>
• EFS: aws efs describe-mount-targets --file-system-id <fs-id> --region
<region>
• Verify subnet routing: Ensure your subnets have proper routing (local VPC route for the CIDR
range)

I get "Permission Denied" when writing to my mounted ﬁlesystem
When this occurs: Agent invocation succeeds and the agent can read ﬁles from the mount, but
writing fails with "Permission denied"
Why this happens: Either the IAM role is missing write permissions, or the POSIX permissions on
the directory set during access point creation don’t allow writes for the agent’s user.
Solution:
• Check IAM permissions: Ensure your execution role includes s3files:ClientWrite (S3 Files)
or elasticfilesystem:ClientWrite (EFS). Without write permissions, the mount is readonly. For more information, see permissions for Amazon Bedrock AgentCore Runtime execution
role.
• Check POSIX permissions: If the directory is owned by a diﬀerent user than your container
process, writes will be denied. Either:
• Set your access point’s posixUser to match the uid/gid your container runs as, so all operations
are performed as that user.
• Set directory permissions to 777 to allow all users to write.

My container fails to start with HTTP 424 error on high-layer images
When this occurs: Your InvokeAgentRuntime calls return HTTP 424 (Failed Dependency) and
your agent logs show Failed to mount overlay: No such file or directory. This
occurs when your container image has more than 53 layers AND uses a non-numeric USER directive
(e.g., USER myuser instead of USER 1000).
Why this happens: Container images with many layers combined with non-numeric USER
directives can cause initialization failures.
I get "Permission Denied" when writing to my mounted ﬁlesystem

528

Solution: Use one of these workarounds:
• Use a numeric USER directive: In your Dockerﬁle, replace USER myuser with the numeric UID
(e.g., USER 1000). You can ﬁnd your user’s UID by running id myuser inside the container. This
avoids the ﬁlesystem mount entirely.
• Reduce image layers: Use multi-stage Docker builds to reduce your image to fewer than 53
layers. You can check your image’s layer count with:

docker inspect <image> | jq '.[0].RootFS.Layers | length'

• Squash layers: Use docker build --squash or a tool like docker-squash to ﬂatten your
image layers.

My capacity provider is in state CREATE_FAILED
When this occurs: After you call CreateCapacityProvider for the Instances compute type, the
capacity provider does not reach ACTIVE and instead enters CREATE_FAILED.
Why this happens: A capacity provider relies on multiple resources (such as a launch template and
an Auto Scaling group) that the capacity provider operator role must be able to create. Missing
permissions on that role lead to a creation failure.
Solution: Call the GetCapacityProvider API to retrieve the failure reason in the statusReason
ﬁeld. The statusReason identiﬁes the resources that failed to create. Grant the capacity provider
operator role the permissions it needs to create those resources, and then create the capacity
provider again. For more information about the operator role, see Security model and permissions
for Runtime Instances.

My agents on Instances do not have access to their credentials
When this occurs: An agent running on an Instances session cannot obtain the credentials it needs
to call AWS services.
Why this happens: The runtime execution role is missing or cannot be assumed by AgentCore.
Solution: Make sure the execution role you conﬁgured for your runtime exists and allows
bedrock-agentcore.amazonaws.com to call sts:AssumeRole. For more information, see
permissions for Amazon Bedrock AgentCore Runtime execution role.
My capacity provider is in state CREATE_FAILED

529

Best practices
Enable comprehensive logging
Implement thorough logging in your agent:
• Include request/response logging in your agent
• Log critical paths and error conditions
Use structured error handling
Implement clear error reporting:
• Return clear error messages with speciﬁc codes
• Include actionable information in error responses
Test incremental changes
Follow a methodical testing approach:
• When modifying your agent, test locally before deployment
• Validate payload compatibility with both local and deployed environments
Monitor performance
Set up monitoring for your agent:
• Use CloudWatch metrics to track invocation patterns
• Set up alarms for error rates and latency

Best practices

530


## Gateway rate limits (pp. 1242–1281)

awscurl --service bedrock-agentcore --region us-west-2 -X POST \
"https://GATEWAY_ID.gateway.bedrock-agentcore.us-west-2.amazonaws.com/inference/v1/
responses" \
-H "Content-Type: application/json" \
-d '{"model": "auto-claude", "input": "Hello!", "max_output_tokens": 50}'

Add rate limits to a gateway
With rate limits, you control how much traﬃc individual callers, targets, or tools can consume
on your gateway. You deﬁne dimension keys that determine how traﬃc is grouped, then set rate
entries that specify the allowed throughput for each group.
Use rate limits to accomplish the following goals:
• Protect backend models and tools from traﬃc spikes
• Enforce per-caller quotas based on JWT claims or IAM identity
• Block speciﬁc callers by setting a rate of zero
• Control tokens per minute (TPM) for inference targets
• Limit concurrent connections to endpoints
Topics
• How rate limits work
• Relationship with service-managed limits
• Rate limit components
• Status lifecycle
• Limits
• Common API errors
• Rate limit dimensions
• Rate limit metrics
• Rate limit enforcement
• Rate limit API examples
• Rate limit best practices
Rate limits

1242

How rate limits work
Each rate limit deﬁnes one or more dimension keys that determine how the gateway groups traﬃc
into buckets. Within a rate limit, you create entries that match speciﬁc dimension values and
specify the allowed rate for that bucket.
When the gateway receives a request, it evaluates all active rate limits. For each rate limit, the
gateway resolves the dimension keys from the request context. It ﬁnds the matching entry and
checks whether the request exceeds the allowed rate. All rate limits must pass for the request to
proceed (AND logic).
Rate limit changes propagate to the data plane within 30 seconds.

Relationship with service-managed limits
The gateway enforces both customer-deﬁned rate limits and service-managed limits. Customerdeﬁned rate limits cannot exceed the service ceiling. The eﬀective rate for any request is the
minimum of the customer-deﬁned limit and the service-managed limit. For current servicemanaged limits, see Gateway service quotas.

Rate limit components
Component

Description

rateLimitId

A unique identiﬁer for the rate limit (2–64 characters,
alphanumeric with -, _, .). You can specify your own ID on
creation, or omit it and the service generates one automatic
ally. Appears in throttled responses and metrics.

dimensionKeys

An ordered list of 1 to 10 keys that determine how traﬃc is
grouped into buckets. Dimension keys are immutable after
creation.

entries

A list of 1 to 1,000 rate entries. Each entry speciﬁes dimension
values and the allowed rate for that bucket.

description

An optional text description of the rate limit’s purpose.

Rate limits

1243

Status lifecycle
Status

Description

CREATING

The rate limit is being provisioned. It is not yet enforced.

ACTIVE

The rate limit is active and enforced on the data plane.

UPDATING

The rate limit is being updated. The previous conﬁguration
remains enforced until the update completes.

DELETING

The rate limit is being removed. Enforcement stops when
deletion completes.

Limits
Resource

Limit

Rate limits per gateway

50

Entries per rate limit

1,000

Dimension keys per rate limit

10

Description maximum length

512 characters

Entry dimension values

Must match the number of
dimension keys

Rate value range

0 to 10,000,000 (0 blocks all
matching traﬃc)

Propagation time

≤ 30 seconds

Rate limits

1244

Important
Rate limits use fail-open behavior by default. If the rate limit service is unavailable or a
dimension cannot be resolved, the gateway allows the request to proceed. Design your
security posture accordingly and do not rely solely on rate limits as a security boundary.

Common API errors
The following errors might be returned when managing rate limits through the control plane API:

HTTP status

Error

Description

400

ValidationException

Invalid request parameters (for
example, unsupported metric/pe
riod combination, invalid dimension
values).

404

ResourceNotFoundException

The speciﬁed gateway or rate limit
does not exist.

409

ConflictException

A rate limit with the same dimension
keys already exists, or the gateway
is in a state that does not allow
modiﬁcation.

Rate limit dimensions
Dimension keys determine how the gateway groups traﬃc into rate limit buckets. Each dimension
key references a value from the request context. The gateway resolves these values at runtime to
ﬁnd the matching rate limit entry.

Rate limits

1245

Supported dimensions

Dimension key

Description

Example
value

targetName

The name of the target being invoked.
Resolved from the request path.

my-llm-ta

The fully-qualiﬁed name of the tool

my-mcp-ta

being invoked, in the format targetNam

rget___ge

e___toolName
requests.

t_weather

toolName

qualifiedModelId

. Available for MCP tool-use

The fully qualiﬁed model identiﬁer for
inference targets.

rget

anthropic
.claude-3
-sonnet-2
0240229-v
1:0

$.context.jwt.<cla

A claim extracted from the caller’s JWT token.

im>

Replace <claim> with the claim name (for

user-123

example, $.context.jwt.sub , $.context
.jwt.team
$.context.iam.prin

).

The IAM principal ARN of the caller.

cipal

arn:aws:i
am::12345
6789012:r
ole/MyRol
e

$.context.iam.sour
ceIdentity

The source identity set by the caller when
assuming a role.

developer
@example.
com

The default value (*)
Rate limit entries support the special value * as a catch-all default for a dimension.

Rate limits

1246

• An entry with * for a dimension means "apply this rate to all values of this dimension."
• If a more speciﬁc entry exists for the actual value, the speciﬁc entry takes precedence (mostspeciﬁc match wins).
• * creates independent per-entity buckets — each distinct value that matches gets its own rate
bucket at the conﬁgured rate.
Trailing-only constraint for multi-dimension rate limits:
When a rate limit has multiple dimension keys,

can only appear in trailing positions. If you use

at position N, all subsequent positions must also be *.
For example, with dimensionKeys: ["targetName", "toolName",
"$.context.jwt.sub"]:

Entry dimensions

Valid

Why

["target1", "readData",

Yes

All positions are speciﬁc values.

Yes

Only the last position is *.

["target1", "*", "*"]

Yes

Trailing positions are *.

["*", "*", "*"]

Yes

All positions are * (default for any
combination).

["*", "readData", "alice"]

No

* at position 1 followed by speciﬁc
values.

["*", "*", "alice"]

No

* at positions 1-2 followed by
speciﬁc value.

["target1", "*", "alice"]

No

* at position 2 followed by speciﬁc
value at position 3.

"alice"]
["target1", "readData",
"*"]

How matching works:
Rate limits

1247

When a request arrives, the gateway resolves the actual dimension values and looks for the most
speciﬁc matching entry. For example, if the resolved values are ["target1", "readData",
"alice"], the gateway checks entries in this order:
1. ["target1", "readData", "alice"] — exact match (most speciﬁc)
2. ["target1", "readData", "*"] — last dimension uses default
3. ["target1", "*", "*"] — last two dimensions use default
4. ["*", "*", "*"] — fully default (least speciﬁc)
The ﬁrst match wins.

Tip
Use speciﬁc entries for known high-value or restricted entities, and * entries as default rate
tiers for everything else.

Dimension resolution behavior
When the gateway evaluates a rate limit, it resolves each dimension key from the request context:
• If a dimension key cannot be resolved from the request (for example, toolName on a nontool request, or a JWT claim that does not exist), the gateway skips that rate limit entirely. The
request is not throttled by that rate limit.
• Only validated context is used for resolution. JWT claims are extracted from tokens that have
been validated by the gateway’s authentication conﬁguration. IAM context is available only for
SigV4-authenticated requests.
Shared vs individual limits
The combination of dimension keys and entry values determines whether traﬃc shares a single
rate bucket or each entity gets its own independent bucket.

Rate limits

1248

dimensionKeys

Entry dimensions

Behavior

["targetName"]

{"targetName": "my-

All traﬃc to my-target
shares one bucket (shared
limit for that target).

target"}

["targetName"]

{"targetName": "*"}

Each target gets its own
independent bucket at this
rate (per-entity).

["$.context.jwt.su

{"$.context.jwt.su

b"]

b": "*"}

Each unique caller gets their
own bucket (individual percaller limit).

["targetName",

{"targetName": "my-

Each caller gets their own

"$.context.jwt.sub"]

target", "$.contex

bucket, scoped to my-target
.

t.jwt.sub": "*"}
["targetName",

{"targetName": "*",

"$.context.jwt.sub"]

"$.context.jwt.sub":
"*"}

Each unique target-and-caller
combination gets its own
bucket.

Warning
Avoid using high-cardinality or unbounded JWT claims as dimension keys (for example,
$.context.jwt.jti, $.context.jwt.nonce, or request IDs). These create an
unbounded number of rate buckets, which might reduce the eﬀectiveness of rate limiting.
Use stable, bounded identiﬁers such as sub, team, or tier instead.

Rate limit metrics
Rate limit entries specify one or more metrics that deﬁne what is being measured and the time
window for enforcement. Each metric type has speciﬁc constraints on supported periods and target
types.

Rate limits

1249

Request rate limits
Request rate limits control the number of API requests allowed within a time window.
• Supported periods: second, minute
• Supported target types: All target types
• Setting rate to 0: Blocks all matching requests once propagation completes (up to 30 seconds)
Request rate limits are evaluated synchronously before the request is forwarded to the target.
Token rate limits
Token rate limits control the number of tokens (input + output) consumed within a time window.
Token rate limits apply only to inference targets.
• Supported periods: minute
• Supported target types: Inference targets only (connector targets and provider targets with
known inference paths)
• Known inference paths: /v1/chat/completions, /v1/messages, /v1/responses
Token rate limits use budget-based enforcement:
1. The gateway estimates input token usage before forwarding the request.
2. The actual token count (input + output) is recorded after the response completes.
3. Due to response latency, the budget might temporarily exceed the conﬁgured rate before
enforcement catches up.

Note
For streaming chat completions requests (/v1/chat/completions), the gateway
automatically adds "stream_options": {"include_usage": true} to the request
body. This happens when a token rate limit is active and the option is not already
present. It ensures accurate token counts are available in the streamed response for TPM
enforcement.

Rate limits

1250

Connection rate limits
Connection rate limits control the number of concurrent in-ﬂight requests allowed at any given
time. Each request occupies a connection slot from acceptance until the response completes. If a
new request arrives and the number of active connections has reached the conﬁgured limit, the
request is rejected with an HTTP 429 response.
• Supported periods: second
• Supported target types: All target types (MCP, HTTP, Inference)
• Measurement: Maximum concurrent in-ﬂight requests
Metric constraints
Metric

Supported periods

Supported targets

requests

second, minute

All

tokens

minute

Inference targets only
(connector, provider
with known paths)

connections

second

All

Combined metrics
A single rate limit entry can specify multiple metrics. When an entry has multiple metrics, all
metrics are evaluated independently — the request is throttled if any single metric exceeds its
limit.
The following example shows a rate limit that enforces both requests per minute and tokens per
minute:
{
"rateLimitId": "inference-rps-and-tpm",
"dimensionKeys": ["targetName", "$.context.jwt.sub"],
"entries": [
{
"dimensions": {
Rate limits

1251

"targetName": "my-inference-target",
"$.context.jwt.sub": "*"
},
"requests": [{"rate": 300, "period": "minute"}],
"tokens": [{"rate": 50000, "period": "minute"}]
}
]
}

In this example, each caller is throttled if they exceed either 300 requests per minute or 50,000
tokens per minute to my-inference-target, whichever limit is reached ﬁrst.

Rate limit enforcement
This topic describes how the gateway evaluates and enforces rate limits at runtime, including
interaction with other gateway features, throttled response formats, and observability.
Interaction with gateway rules
The gateway evaluates rate limits before gateway rules. If a rate limit throttles a request, the
request never reaches the rule evaluation stage.
Stacking semantics
When multiple rate limits apply to a request, the gateway uses AND logic — all rate limits must
pass for the request to proceed. If any single rate limit denies the request, the gateway throttles it.
Entry matching and speciﬁcity
When a rate limit has multiple entries, the gateway selects the most speciﬁc matching entry for the
resolved dimension values:
• An exact value match takes precedence over a * entry.
• The * value means "apply this rate to all values of this dimension" — it acts as a default entry.
• For multi-dimension rate limits, the gateway uses progressive trailing fallback: it ﬁrst attempts a
full exact match, then replaces trailing dimensions with * one at a time until a match is found.
The following example shows how entries are matched for a rate limit with dimensionKeys:
["targetName", "toolName"] when the resolved values are ["my-target", "readData"]:
Rate limits

1252

Entry dimensions

Matches?

Why

{"targetName": "my-targe

Yes (checked
ﬁrst)

Exact match on both dimensions.
Most speciﬁc.

Yes (checked
second)

Exact match on ﬁrst dimension, * on
second.

Yes (checked
last)

Default entry. Least speciﬁc.

t", "toolName": "readData
"}
{"targetName": "my-targe
t", "toolName": "*"}
{"targetName": " ",
"toolName": " "}

The ﬁrst matching entry wins. If no entry matches (and no * default exists), the rate limit is skipped
for that request.
Evaluation order
The gateway evaluates rate limits in the following order:
1. The gateway evaluates rate limits with more dimension keys ﬁrst (more speciﬁc limits take
priority).
2. Within the same number of dimensions, the gateway evaluates rate limits with tighter (lower)
rates ﬁrst.
3. Evaluation short-circuits on the ﬁrst denial — the gateway does not evaluate remaining rate
limits.
Interaction with service-managed limits
The gateway enforces both customer-deﬁned rate limits and service-managed limits. The eﬀective
rate for any request is the minimum of both:
• The gateway evaluates customer-deﬁned rate limits ﬁrst.
• If the request passes customer limits, service-managed limits are evaluated.
• A denial from either source results in throttling.

Rate limits

1253

Throttled responses
When a request is throttled, the gateway returns a protocol-speciﬁc error response containing the
retryAfter value in the response body.
HTTP protocol:
{
"error": "Rate limit exceeded",
"success": false,
"limitKey": "rl-abc123/targetName=my-target",
"metric": "requests",
"retryAfter": 1
}

MCP protocol (JSON-RPC):
{
"jsonrpc": "2.0",
"id": "request-1",
"error": {
"code": -32003,
"message": "Rate limit exceeded",
"data": {
"limitKey": "rl-abc123/targetName=my-target",
"metric": "requests",
"retryAfter": 1
}
}
}

OpenAI-compatible protocol:
{
"error": {
"message": "Rate limit exceeded",
"type": "rate_limit_error",
"code": "429",
"limitKey": "rl-abc123/qualifiedModelId=anthropic.claude-3-sonnet",
"metric": "tokens",
"retryAfter": 60
}
Rate limits

1254

}

Anthropic-compatible protocol:
{
"type": "error",
"error": {
"type": "rate_limit_error",
"message": "Rate limit exceeded",
"limitKey": "rl-abc123/qualifiedModelId=anthropic.claude-3-sonnet",
"metric": "tokens",
"retryAfter": 60
}
}

The retryAfter ﬁeld indicates how many seconds the caller should wait before retrying. Use this
value directly in your client-side retry logic.
Propagation timing
Rate limit changes (create, update, delete) propagate to the data plane within 30 seconds. During
propagation:
• New rate limits are not enforced until propagation completes.
• Updated rate limits continue enforcing the previous conﬁguration until the update propagates.
• Deleted rate limits continue enforcing until the deletion propagates.
Enforcement accuracy and eventual consistency
Rate limit enforcement is eventually consistent rather than exact. Enforcement accuracy is
approximate in the moments after a limit begins receiving traﬃc, and it improves as traﬃc
continues. The accuracy you observe therefore depends on your traﬃc pattern.
The following behaviors are expected:
• Cold limits over-admit at ﬁrst. A cold limit is one that is newly created or that has had no recent
traﬃc. For a short initial period, the gateway might over-admit (allow more requests than the
conﬁgured rate) before enforcement converges. Once a limit is under continuous traﬃc, accuracy
improves and the observed throttle rate settles close to the conﬁgured rate.
Rate limits

1255

• Sustained traﬃc enforces accurately, but short bursts might not. A brief burst against a
cold limit can pass through without being throttled. The same rate sent as sustained traﬃc
is enforced, because accuracy improves as a limit warms up. To observe or demonstrate
enforcement, send sustained traﬃc to the limit for several minutes rather than a single short
burst. For example, for a limit of 4 requests per second, the gateway might not throttle the 5th
request in the ﬁrst second. If you send 5 requests per second continuously, you will consistently
see the extra request throttled after the limit warms up.
• Very low rates are less accurate. Rates below roughly 1 request per second (for example, a small
requests-per-minute limit) are harder to enforce precisely and will show more variability. Prefer
higher rates where precise enforcement matters, and treat very low limits as approximate.
• Token limits converge more slowly. Token-per-minute limits update (reconcile) the tracked
usage total only after the model responds. A request that is in ﬂight for several seconds or
minutes holds only its estimated cost against the budget until it completes. This extends the
window during which the gateway might over-admit requests, relative to request limits. See
Token rate limit FAQ for details.
Design your limits around fair usage and backend protection. This means smoothing bursts and
protecting targets from noisy neighbors over a sustained window, rather than blocking an exact
request number the instant a threshold is crossed. Rate limits are not a precise, request-exact gate.
Rate limits are also not a security boundary, as explained in the following section.
Fail-open behavior
The gateway uses fail-open semantics for rate limit evaluation. The following table describes
behavior when the rate limit system encounters errors:

Scenario

Decision

Rationale

Rate limit service timeout

Allow

Availability takes precedence over
enforcement.

Dimension key unresolvable from
request

Skip (allow)

The rate limit does not apply to this
request type.

Rate limit cache refresh failure

Retry with stale
data

Last known conﬁguration is used
until cache recovers.

Rate limits

1256

Important
Because of fail-open behavior, do not rely solely on rate limits as a security boundary.
Use rate limits for traﬃc management and quality of service, and use authentication,
authorization, and WAF rules for security enforcement.

Tracing with OpenTelemetry spans
The gateway emits OpenTelemetry (OTEL) span attributes on the server span for every request
where customer rate limits are evaluated. Use these attributes for debugging and monitoring.
Attribute

Description

Example

aws.agentcore.gate

The enforcement decision for this
request.

allowed or throttled

per-target-rps

way.throt

The rateLimitId of the rate limit
that rejected the request. Only present

tle.custo

when decision is throttled .

way.throt
tle.custo
mer.decision
aws.agentcore.gate

mer.limit_key

way.throt

The metric type that was exhausted
. Only present when decision is

tle.custo

throttled .

aws.agentcore.gate

requests

mer.metric

tle.custo

Comma-separated resolved dimension
values of the entry that triggered the
throttle. Only present when decision is

mer.matched_entry

throttled .

aws.agentcore.gate

Ordered list of all rate limit buckets
checked for this request. Each entry
shows the rate limit ID, metric, and
resolved dimension values. Present

aws.agentcore.gate
way.throt

way.throt
tle.custo
mer.evaluated
Rate limits

my-target,alice

["per-targetrps:requests:m
y-target", "per-

1257

Amazon Bedrock AgentCore

Attribute

Developer Guide

Description

Example

for both allowed and throttled
decisions.

caller-rpm:re
quests:alice"]

The evaluated attribute is useful for understanding which rate limits applied to a request, even
when it was allowed. Each entry in the list follows the format {rateLimitId}:{metric}:
{resolvedDimVal1,dimVal2,…} .

Rate limit API examples
The following examples show how to manage rate limits using the AWS CLI and AWS Python SDK
(Boto3).
Create a per-target requests-per-second limit
The following example creates a rate limit that controls requests per second on a per-target basis.
A speciﬁc target gets 100 RPS, and all other targets each get their own 10 RPS bucket.
Example
AWS CLI
1. Run the following command:
aws bedrock-agentcore-control create-gateway-rate-limit \
--gateway-identifier my-gateway-abc1234567 \
--dimension-keys '["targetName"]' \
--description "Per-target RPS limit" \
--entries '[
{
"dimensions": {"targetName": "my-high-traffic-target"},
"requests": [
{
"rate": 100,
"period": "second"
}
]
},
{
"dimensions": {"targetName": "*"},
"requests": [
Rate limits

1258

{
"rate": 10,
"period": "second"
}
]
}
]'

AWS Python SDK (Boto3)
1.
import boto3
client = boto3.client("bedrock-agentcore-control", region_name="us-west-2")
response = client.create_gateway_rate_limit(
gatewayIdentifier="my-gateway-abc1234567",
dimensionKeys=["targetName"],
description="Per-target RPS limit",
entries=[
{
"dimensions": {"targetName": "my-high-traffic-target"},
"requests": [
{
"rate": 100,
"period": "second",
}
],
},
{
"dimensions": {"targetName": "*"},
"requests": [
{
"rate": 10,
"period": "second",
}
],
},
],
)
print(f"Rate Limit ID: {response['rateLimitId']}")

Rate limits

1259

Create a per-caller requests-per-minute limit
The following example creates a rate limit based on the caller’s JWT sub claim. Premium users get
300 RPM, and all other users get 60 RPM.
Example
AWS CLI
1. Run the following command:
aws bedrock-agentcore-control create-gateway-rate-limit \
--gateway-identifier my-gateway-abc1234567 \
--dimension-keys '["$.context.jwt.sub"]' \
--description "Per-caller RPM by subscription tier" \
--entries '[
{
"dimensions": {"$.context.jwt.sub": "premium-user-001"},
"requests": [
{
"rate": 300,
"period": "minute"
}
]
},
{
"dimensions": {"$.context.jwt.sub": "premium-user-002"},
"requests": [
{
"rate": 300,
"period": "minute"
}
]
},
{
"dimensions": {"$.context.jwt.sub": "*"},
"requests": [
{
"rate": 60,
"period": "minute"
}
]
}

Rate limits

1260

]'

AWS Python SDK (Boto3)
1.
import boto3
client = boto3.client("bedrock-agentcore-control", region_name="us-west-2")
response = client.create_gateway_rate_limit(
gatewayIdentifier="my-gateway-abc1234567",
dimensionKeys=["$.context.jwt.sub"],
description="Per-caller RPM by subscription tier",
entries=[
{
"dimensions": {"$.context.jwt.sub": "premium-user-001"},
"requests": [
{
"rate": 300,
"period": "minute",
}
],
},
{
"dimensions": {"$.context.jwt.sub": "premium-user-002"},
"requests": [
{
"rate": 300,
"period": "minute",
}
],
},
{
"dimensions": {"$.context.jwt.sub": "*"},
"requests": [
{
"rate": 60,
"period": "minute",
}
],
},
],

Rate limits

1261

)
print(f"Rate Limit ID: {response['rateLimitId']}")

Create a multi-dimension limit with tokens
The following example creates a rate limit with three dimension keys that limits both requests and
tokens per minute. Each caller gets their own budget scoped to a speciﬁc target and model.
Example
AWS CLI
1. Run the following command:
aws bedrock-agentcore-control create-gateway-rate-limit \
--gateway-identifier my-gateway-abc1234567 \
--dimension-keys '["targetName", "qualifiedModelId", "$.context.jwt.sub"]' \
--description "Per-caller token and request budget per target and model" \
--entries '[
{
"dimensions": {"targetName": "my-inference-target",
"qualifiedModelId": "anthropic.claude-3-sonnet-20240229-v1:0",
"$.context.jwt.sub": "*"},
"requests": [
{
"rate": 100,
"period": "minute"
}
],
"tokens": [
{
"rate": 50000,
"period": "minute"
}
]
},
{
"dimensions": {"targetName": "*", "qualifiedModelId": "*",
"$.context.jwt.sub": "*"},
"requests": [
{
Rate limits

1262

"rate": 30,
"period": "minute"
}
],
"tokens": [
{
"rate": 10000,
"period": "minute"
}
]
}
]'

AWS Python SDK (Boto3)
1.
import boto3
client = boto3.client("bedrock-agentcore-control", region_name="us-west-2")
response = client.create_gateway_rate_limit(
gatewayIdentifier="my-gateway-abc1234567",
dimensionKeys=["targetName", "qualifiedModelId", "$.context.jwt.sub"],
description="Per-caller token and request budget per target and model",
entries=[
{
"dimensions": {"targetName": "my-inference-target",
"qualifiedModelId": "anthropic.claude-3-sonnet-20240229-v1:0",
"$.context.jwt.sub": "*"},
"requests": [
{
"rate": 100,
"period": "minute",
}
],
"tokens": [
{
"rate": 50000,
"period": "minute",
}
],
},

Rate limits

1263

{
"dimensions": {"targetName": "*", "qualifiedModelId": "*",
"$.context.jwt.sub": "*"},
"requests": [
{
"rate": 30,
"period": "minute",
}
],
"tokens": [
{
"rate": 10000,
"period": "minute",
}
],
},
],
)
print(f"Rate Limit ID: {response['rateLimitId']}")

Create a connection rate limit
The following example creates a connection rate limit per model. This limits the number of
concurrent in-ﬂight requests to each model, which is useful for protecting targets that have limited
concurrency capacity.
Example
AWS CLI
1. Run the following command:
aws bedrock-agentcore-control create-gateway-rate-limit \
--gateway-identifier my-gateway-abc1234567 \
--dimension-keys '["qualifiedModelId"]' \
--description "Connection rate limit per model" \
--entries '[
{
"dimensions": {"qualifiedModelId": "anthropic.claude-3sonnet-20240229-v1:0"},
"connections": [
Rate limits

1264

{
"rate": 50,
"period": "second"
}
]
},
{
"dimensions": {"qualifiedModelId": "*"},
"connections": [
{
"rate": 20,
"period": "second"
}
]
}
]'

AWS Python SDK (Boto3)
1.
import boto3
client = boto3.client("bedrock-agentcore-control", region_name="us-west-2")
response = client.create_gateway_rate_limit(
gatewayIdentifier="my-gateway-abc1234567",
dimensionKeys=["qualifiedModelId"],
description="Connection rate limit per model",
entries=[
{
"dimensions": {"qualifiedModelId": "anthropic.claude-3sonnet-20240229-v1:0"},
"connections": [
{
"rate": 50,
"period": "second",
}
],
},
{
"dimensions": {"qualifiedModelId": "*"},
"connections": [

Rate limits

1265

{
"rate": 20,
"period": "second",
}
],
},
],
)
print(f"Rate Limit ID: {response['rateLimitId']}")

Block a caller with rate zero
The following example blocks a speciﬁc caller by setting their rate to 0. This denies all requests
from the blocked caller once the change propagates (up to 30 seconds).
Example
AWS CLI
1. Run the following command:
aws bedrock-agentcore-control create-gateway-rate-limit \
--gateway-identifier my-gateway-abc1234567 \
--dimension-keys '["$.context.jwt.sub"]' \
--description "Block abusive caller" \
--entries '[
{
"dimensions": {"$.context.jwt.sub": "blocked-user-789"},
"requests": [
{
"rate": 0,
"period": "second"
}
]
},
{
"dimensions": {"$.context.jwt.sub": "*"},
"requests": [
{
"rate": 100,
"period": "second"
Rate limits

1266

}
]
}
]'

AWS Python SDK (Boto3)
1.
import boto3
client = boto3.client("bedrock-agentcore-control", region_name="us-west-2")
response = client.create_gateway_rate_limit(
gatewayIdentifier="my-gateway-abc1234567",
dimensionKeys=["$.context.jwt.sub"],
description="Block abusive caller",
entries=[
{
"dimensions": {"$.context.jwt.sub": "blocked-user-789"},
"requests": [
{
"rate": 0,
"period": "second",
}
],
},
{
"dimensions": {"$.context.jwt.sub": "*"},
"requests": [
{
"rate": 100,
"period": "second",
}
],
},
],
)
print(f"Rate Limit ID: {response['rateLimitId']}")

Rate limits

1267

Get a rate limit
The following example retrieves the details of a speciﬁc rate limit.
Example
AWS CLI
1. Run the following command:
aws bedrock-agentcore-control get-gateway-rate-limit \
--gateway-identifier my-gateway-abc1234567 \
--rate-limit-id rl-abc123def456

AWS Python SDK (Boto3)
1.
import boto3
client = boto3.client("bedrock-agentcore-control", region_name="us-west-2")
response = client.get_gateway_rate_limit(
gatewayIdentifier="my-gateway-abc1234567",
rateLimitId="rl-abc123def456",
)
print(f"Status: {response['status']}")
print(f"Dimension Keys: {response['dimensionKeys']}")
print(f"Entries: {len(response['entries'])}")

Update a rate limit
The following example updates the entries of an existing rate limit to increase the rate for a
speciﬁc target.

Note
The dimensionKeys ﬁeld is immutable after creation. To change dimension keys, delete
the rate limit and create a new one.

Rate limits

1268

Example
AWS CLI
1. Run the following command:
aws bedrock-agentcore-control update-gateway-rate-limit \
--gateway-identifier my-gateway-abc1234567 \
--rate-limit-id rl-abc123def456 \
--description "Updated per-target RPS limit" \
--entries '[
{
"dimensions": {"targetName": "my-high-traffic-target"},
"requests": [
{
"rate": 200,
"period": "second"
}
]
},
{
"dimensions": {"targetName": "*"},
"requests": [
{
"rate": 20,
"period": "second"
}
]
}
]'

AWS Python SDK (Boto3)
1.
import boto3
client = boto3.client("bedrock-agentcore-control", region_name="us-west-2")
response = client.update_gateway_rate_limit(
gatewayIdentifier="my-gateway-abc1234567",
rateLimitId="rl-abc123def456",
description="Updated per-target RPS limit",

Rate limits

1269

entries=[
{
"dimensions": {"targetName": "my-high-traffic-target"},
"requests": [
{
"rate": 200,
"period": "second",
}
],
},
{
"dimensions": {"targetName": "*"},
"requests": [
{
"rate": 20,
"period": "second",
}
],
},
],
)
print(f"Status: {response['status']}")

List rate limits
The following example lists all rate limits for a gateway.
Example
AWS CLI
1. Run the following command:
aws bedrock-agentcore-control list-gateway-rate-limits \
--gateway-identifier my-gateway-abc1234567

AWS Python SDK (Boto3)
1.
import boto3
Rate limits

1270

client = boto3.client("bedrock-agentcore-control", region_name="us-west-2")
paginator = client.get_paginator("list_gateway_rate_limits")
for page in paginator.paginate(gatewayIdentifier="my-gateway-abc1234567"):
for rate_limit in page["rateLimits"]:
print(
f"ID: {rate_limit['rateLimitId']}, "
f"Status: {rate_limit['status']}, "
f"Dimensions: {rate_limit['dimensionKeys']}"
)

Note
Results might be paginated. Use the nextToken value from the response to retrieve
additional pages, or use the Boto3 paginator as shown above.

Delete a rate limit
The following example deletes a rate limit from a gateway.
Example
AWS CLI
1. Run the following command:
aws bedrock-agentcore-control delete-gateway-rate-limit \
--gateway-identifier my-gateway-abc1234567 \
--rate-limit-id rl-abc123def456

AWS Python SDK (Boto3)
1.
import boto3
client = boto3.client("bedrock-agentcore-control", region_name="us-west-2")

Rate limits

1271

response = client.delete_gateway_rate_limit(
gatewayIdentifier="my-gateway-abc1234567",
rateLimitId="rl-abc123def456",
)
print(f"Status: {response['status']}")

Batch put rate limits
The following example creates or updates multiple rate limits in a single call. Batch put uses upsert
semantics — if a rate limit with the same dimension keys exists, it is updated; otherwise, a new rate
limit is created.
Note
Batch put is idempotent. You can safely retry failed calls without creating duplicate rate
limits.

Example
AWS CLI
1. Run the following command:
aws bedrock-agentcore-control batch-put-gateway-rate-limits \
--gateway-identifier my-gateway-abc1234567 \
--rate-limits '[
{
"dimensionKeys": ["targetName"],
"description": "Per-target RPS",
"entries": [
{
"dimensions": {"targetName": "*"},
"requests": [{"rate": 50, "period": "second"}]
}
]
},
{
"dimensionKeys": ["$.context.jwt.sub"],
"description": "Per-caller RPM",
Rate limits

1272

"entries": [
{
"dimensions": {"$.context.jwt.sub": "*"},
"requests": [{"rate": 120, "period": "minute"}]
}
]
}
]'

AWS Python SDK (Boto3)
1.
import boto3
client = boto3.client("bedrock-agentcore-control", region_name="us-west-2")
response = client.batch_put_gateway_rate_limits(
gatewayIdentifier="my-gateway-abc1234567",
rateLimits=[
{
"dimensionKeys": ["targetName"],
"description": "Per-target RPS",
"entries": [
{
"dimensions": {"targetName": "*"},
"requests": [
{"rate": 50, "period": "second"}
],
}
],
},
{
"dimensionKeys": ["$.context.jwt.sub"],
"description": "Per-caller RPM",
"entries": [
{
"dimensions": {"$.context.jwt.sub": "*"},
"requests": [
{"rate": 120, "period": "minute"}
],
}
],

Rate limits

1273

},
],
)
for result in response["rateLimits"]:
print(f"ID: {result['rateLimitId']}, Status: {result['status']}")

Rate limit best practices
This topic provides guidance on designing, deploying, and operating rate limits eﬀectively on your
gateway.
Design patterns
Tiered access
Create multiple rate limits with the same dimension key ($.context.jwt.sub or
$.context.jwt.tier) but diﬀerent entries for each tier. Use exact entries for known
premium users and a * entry as the default tier.
Defense in depth
Layer rate limits at multiple granularities. For example, combine a per-target RPS limit (protects
backend capacity) with a per-caller RPM limit (prevents individual abuse) and a per-tool token
limit (controls cost).
Infrastructure as Code with BatchPut
Use BatchPutGatewayRateLimits to declaratively manage your rate limit conﬁguration.
Batch put uses upsert semantics, making it safe to run repeatedly from CI/CD pipelines or
infrastructure templates.
Gradual rollout
Start with generous rate limits and tighten them over time based on observed traﬃc patterns.
Monitor the aws.agentcore.gateway.throttle.customer.decision OTEL span
attribute and 429 response rates before reducing limits.
Emergency block
Use rate: 0 entries to block speciﬁc callers, targets, or tools during an incident. The block
takes eﬀect once propagation completes (up to 30 seconds).
Rate limits

1274

Dimension key selection guidance
Choose dimension keys that produce a bounded, predictable number of rate buckets:
Dimension key

Cardinality

Recommendation

targetName

Low (known set)

Excellent choice. Use for per-target
protection.

toolName

Low-medium

Good choice for MCP gateways with
known tool sets.

qualifiedModelId

Low (known set)

Excellent for inference gateways.

$.context.jwt.sub

Medium-high

Good for per-user limits. Cardinality
bounded by your user base.

$.context.jwt.team

Low

Excellent for per-team quotas.

$.context.iam.principal

Medium

Good for per-role limits in IAMauthenticated setups.

$.context.jwt.jti

Unbounded

Do not use. Creates a unique bucket
per token.

$.context.jwt.nonce

Unbounded

Do not use. Creates a unique bucket
per request.

Warning
Unbounded dimension keys (such as $.context.jwt.jti or request-scoped claims)
create an inﬁnite number of rate buckets. This wastes memory, degrades performance,
and eﬀectively disables rate limiting because each request gets its own bucket and is never
throttled.

Token rate limit considerations
Token rate limits require special consideration due to their budget-based enforcement model:
Rate limits

1275

• Budget utilization: The gateway estimates input tokens before forwarding and records actual
usage after the response. Short-lived bursts might temporarily exceed the conﬁgured rate.
• Stream options: For streaming chat completions requests (/v1/chat/completions), the
gateway automatically adds "stream_options": {"include_usage": true} to the
request body when a token rate limit is active and the option is not already present. This enables
accurate token accounting for TPM enforcement.
• Supported paths: Token rate limits apply only to requests on known inference paths (/v1/
chat/completions, /v1/messages, /v1/responses). Requests to other paths are not
subject to token limits.
• Pass-through targets: If your target proxies to a model provider without using a known
inference path, token rate limits do not apply. Consider using request rate limits or restructuring
your target to use a supported path.
Token rate limit FAQ
This section answers common questions about how token-per-minute (TPM) enforcement works in
practice.
How does TPM enforcement work?
The gateway uses a budget-based enforcement model. When a request arrives, the gateway
estimates the input token count and reserves that amount from your conﬁgured TPM budget. If
the estimate exceeds the remaining budget, the request is rejected with an HTTP 429 response
before it reaches the model. After a successful request completes, the gateway reconciles the
budget by replacing the initial estimate with the actual token usage (input + output tokens)
reported by the model provider.
How does TPM work with prompt caching?
The gateway accounts for tokens based on the input_tokens and output_tokens values
that the model provider returns in the inference response. The gateway does not independently
track or adjust for prompt caching. Whether cached tokens are included in input_tokens
depends on how your model provider reports usage — this behavior varies between providers.
Consult your model provider’s documentation to understand how prompt caching aﬀects
reported token counts and your eﬀective TPM consumption.

Rate limits

1276

If my TPM limit is 50 and the tokenizer estimates 51 input tokens, is the request throttled?
Yes. The gateway evaluates the tokenizer’s estimate against the remaining TPM budget before
forwarding the request. If the estimate exceeds the available budget, the request is rejected
with an HTTP 429 response. The response includes a retryAfter ﬁeld indicating when
suﬃcient budget will be available.
If a long-running request consumes more tokens than initially estimated, is the response
throttled?
No. Once the gateway accepts and forwards a request, the response is always delivered in
full. The gateway reserves estimated tokens at request time, and other requests continue to
be evaluated against the remaining budget while the request is in ﬂight. When the response
completes, the gateway reconciles actual usage against the estimate. If the actual consumption
was higher, the budget is adjusted — this may cause subsequent requests to be throttled, but
the original response is never interrupted.
How does token accounting work with streaming responses?
The gateway uses the ﬁnal response chunk as the source of truth for token reconciliation.
Not all model providers report token usage in every streamed chunk — some include it
only in the ﬁnal chunk. The gateway waits for the complete response before reconciling
the TPM budget. For OpenAI Chat Completions streaming, the gateway automatically adds
"stream_options": {"include_usage": true} to the request body when a token
rate limit is active and this option is not already present, ensuring accurate token counts are
available in the ﬁnal chunk.
Operational considerations
Propagation timing
Rate limit changes take up to 30 seconds to propagate. Plan for this delay during incidents — a
block entry (rate: 0) is not immediate.
Rate zero behavior
A rate of 0 blocks all matching traﬃc. Use this deliberately for emergency blocking. Doublecheck entry dimension values before setting rate: 0 to avoid accidentally blocking legitimate
traﬃc.

Rate limits

1277

Immutable dimension keys
You cannot change the dimensionKeys of an existing rate limit. If you need diﬀerent
dimensions, delete the existing rate limit and create a new one. Plan your dimension key
structure before creating production rate limits.

Important
Rate limits use fail-open behavior. If the rate limit service is temporarily unavailable, traﬃc
is allowed through. Do not use rate limits as your sole security mechanism. Combine them
with authentication, authorization, gateway rules, and WAF for defense in depth.

Monitoring
Use the following signals to monitor rate limit eﬀectiveness:
Throttled response signals:
• Monitor HTTP 429 responses from your gateway.
• Parse the limitKey ﬁeld in throttled responses to identify which rate limit is triggering.
• Use the retryAfter value to understand the enforcement window.
OpenTelemetry span attributes:
Attribute

What to monitor

aws.agentcore.gate

Count of throttled requests. Alert on unexpected spikes.

way.throttle.custo
mer.decision = throttled
aws.agentcore.gate
way.throttle.custo

Identify which rate limits are most active. Look for
imbalanced enforcement.

mer.limit_key
aws.agentcore.gate
way.throttle.custo

Determine whether requests, tokens, or connections are
the bottleneck.

mer.metric
Rate limits

1278

Attribute

What to monitor

aws.agentcore.gate

Identify which callers or targets are hitting limits most
frequently.

way.throttle.custo
mer.matched_entry
aws.agentcore.gate
way.throttle.custo

Ordered list of all checked buckets. Useful for understan
ding which limits applied to a speciﬁc request.

mer.evaluated

Example monitoring queries:
Use Amazon CloudWatch Logs Insights on the aws/spans log group to query your gateway’s OTEL
spans. The following examples help identify throttling patterns.
Count throttled requests by rate limit:
filter attributes.`aws.agentcore.gateway.throttle.customer.decision` = "throttled"
| stats count(*) as throttle_count by
attributes.`aws.agentcore.gateway.throttle.customer.limit_key`
| sort throttle_count desc

Identify which callers are being throttled most:
filter attributes.`aws.agentcore.gateway.throttle.customer.decision` = "throttled"
| stats count(*) as throttle_count by
attributes.`aws.agentcore.gateway.throttle.customer.matched_entry`
| sort throttle_count desc
| limit 20

Compare allowed vs throttled requests over time:
filter ispresent(attributes.`aws.agentcore.gateway.throttle.customer.decision`)
| stats count(*) as total,
sum(attributes.`aws.agentcore.gateway.throttle.customer.decision` =
"throttled") as throttled
by bin(5m)

If a single rate limit accounts for most throttle events, consider whether the conﬁgured rate is too
restrictive or whether the traﬃc pattern indicates abuse.
Rate limits

1279

Creating alarms from rate limit spans
You can convert rate limit OTEL span attributes into CloudWatch metrics and alarms to proactively
monitor throttling behavior. This requires enabling gateway observability (see Enabling
observability for AgentCore gateway resources).
Step 1: Enable gateway spans
Ensure your gateway has observability enabled. Gateway spans are exported to CloudWatch and
are viewable in CloudWatch Transaction Search and the generative AI observability page.
Step 2: Create a CloudWatch metric ﬁlter
Create a metric ﬁlter on the aws/spans log group to extract throttle events as a custom metric.
The following example creates a metric that counts throttled requests per rate limit:
{
"filterPattern": "{ $.attributes.aws\\.agentcore\\.gateway\\.throttle\\.customer\
\.decision = \"throttled\" }",
"metricTransformations": [
{
"metricName": "GatewayRateLimitThrottleCount",
"metricNamespace": "AgentCore/Gateway/RateLimits",
"metricValue": "1",
"defaultValue": 0,
"dimensions": {
"LimitKey": "$.attributes.aws\\.agentcore\\.gateway\\.throttle\\.customer\
\.limit_key"
}
}
]
}

Step 3: Create a CloudWatch alarm
After the metric ﬁlter is in place, create an alarm that triggers when the throttle rate exceeds a
threshold.
Example
AWS CLI
1. Run the following command:
Rate limits

1280

aws cloudwatch put-metric-alarm \
--alarm-name "GatewayRateLimitThrottleSpike" \
--namespace "AgentCore/Gateway/RateLimits" \
--metric-name "GatewayRateLimitThrottleCount" \
--statistic Sum \
--period 300 \
--evaluation-periods 1 \
--threshold 100 \
--comparison-operator GreaterThanThreshold \
--alarm-description "Alert when rate limit throttles exceed 100 in 5 minutes"
\
--alarm-actions "arn:aws:sns:us-west-2:123456789012:my-alarm-topic"

AWS Python SDK (Boto3)
1.
import boto3
cloudwatch = boto3.client("cloudwatch", region_name="us-west-2")
cloudwatch.put_metric_alarm(
AlarmName="GatewayRateLimitThrottleSpike",
Namespace="AgentCore/Gateway/RateLimits",
MetricName="GatewayRateLimitThrottleCount",
Statistic="Sum",
Period=300,
EvaluationPeriods=1,
Threshold=100,
ComparisonOperator="GreaterThanThreshold",
AlarmDescription="Alert when rate limit throttles exceed 100 in 5 minutes",
AlarmActions=["arn:aws:sns:us-west-2:123456789012:my-alarm-topic"],
)
print("Alarm created successfully")

Step 4: Build a dashboard
Create a CloudWatch dashboard to visualize throttle rates over time. The following widget
conﬁguration shows throttle counts grouped by rate limit:

Rate limits

1281


## Policy in AgentCore: overview (pp. 1971–1973)

Policy in Amazon Bedrock AgentCore: Control Agent
Interactions
Policy in Amazon Bedrock AgentCore enables developers to deﬁne and enforce security controls
for AI agent interactions with tools by creating a protective boundary around agent operations. AI
agents can dynamically adapt to solve complex problems - from processing customer inquiries to
automating workﬂows across multiple tools and systems. However, this ﬂexibility introduces new
security challenges, as agents may inadvertently misinterpret business rules, or act outside their
intended authority.
With Policy in AgentCore, developers can create policy engines, create and store deterministic
policies in them and associate policy engines with gateways. Policy in AgentCore intercepts all
agent traﬃc through Amazon Bedrock AgentCore Gateways and evaluates each request against
deﬁned policies in the policy engine before allowing tool access.
Policies are constructed using Cedar language , an open source language for writing and enforcing
authorization policies. This allows developers to precisely specify what agents can access and
what actions they can perform. Policy in AgentCore also provides the capability to author policies
using natural language by allowing developers to describe rules in plain English instead of writing
formal policy code in Cedar. Natural language-based policy authoring interprets what the user
intends, generates candidate policies, validates them against the tool schema, and uses automated
reasoning to check safety conditions such as identifying policies that are overly permissive, overly
restrictive, or contain conditions that can never be satisﬁed - ensuring customers catch these issues
before enforcing policies.
Policy in AgentCore also supports authoring policies in Dogwood on the Dogwood Policy
website, an open-source policy language. A single Dogwood policy can combine several kinds of
authorization conditions. At the simplest level, you write input-based rules that permit or forbid
a tool call based on the current request itself — who the principal is, which tool they are calling,
the resource involved, and the input parameters of that call. You can then add session-aware
temporal conditions that decide based on what has already happened earlier in the same session
— for example, requiring that an approval was granted before a transfer, blocking an action
after it has run a set number of times, or keeping a running total under a budget. You can also
consult information providers, such as Guardrails, that emit a signal at evaluation time — such as a
content-safety or prompt-attack score — and make decisions based on the emitted score. Because
input-based, temporal, and provider-based conditions all compose within one policy under the
1971

same permit and forbid model, you can layer them to express the control your agents need — from
a simple access rule to a multi-step, session-aware safeguard.
Policy in AgentCore supports ﬁne-grained permissions based on user identity and tool input
parameters, making it possible to safely deploy autonomous agents at enterprise scale. By
moving security controls outside of agent code, developers can focus on building innovative
agent capabilities while maintaining strong security guarantees - eliminating the need for custom
security implementation and reducing the risk of policy bypass through agent manipulation.
Topics
• Key beneﬁts
• Key features
• Getting started with Policy in AgentCore
• Core concepts
• AgentCore Gateway and Policy in AgentCore IAM Permissions
• Create a policy engine
• Create a policy
• Writing policies in natural language
• Validate and test policies
• Use policies
• Example policies
• Advanced features and topics for Policy in AgentCore

Key beneﬁts
Policy in AgentCore provides three key beneﬁts that enable secure, scalable deployment of AI
agents in enterprise environments:
Fine-grained control over agent actions
Deﬁne what actions an agent is allowed to perform - including which tools it can call and the
precise conditions under which those actions are permitted.

Key beneﬁts

1972

Deterministic enforcement with strong guarantees
Every agent action through Amazon Bedrock AgentCore Gateway is intercepted and evaluated
at the boundary outside of agent’s code - ensuring consistent, deterministic enforcement that
remains reliable regardless of how the agent is implemented.
Simple, accessible authoring with organization-wide consistency
Write policies using natural language prompts or directly in Cedar (AWS's open-source policy
language for ﬁne-grained permissions), making it easy for builders with varying degree of
expertise to deﬁne rules for their agents. Teams can set boundaries once and have them
applied consistently across all agents and tools, with every enforcement decision logged
through CloudWatch metrics and logs, so security and compliance teams can audit and validate
behavior.

Key features
Policy in AgentCore oﬀers comprehensive capabilities for policy-based governance of agent
interactions, including the following key features:
• Policy Enforcement - Intercepts and evaluates all agent requests against deﬁned policies before
allowing tool access
• Access Controls - Enables ﬁne-grained based on user identity and tool input parameters
• Policy Authoring - Provides Cedar policy language support for writing clear, validated policies.
Policies can also be authored in natural language using English prompts which are translated
into Cedar policies and validated
• Policy Monitoring - Oﬀers CloudWatch integration for monitoring policy evaluations and
decisions
• Infrastructure Integration - Integrates with VPC security groups and other AWS security
infrastructure
• Audit Logging - Maintains detailed logs of policy decisions for compliance and troubleshooting
• Temporal Policies - Session-scoped rules that reason over the history of actions within a
conversation. For more information, see Temporal policies.

Key features

1973


## Policy core concepts (pp. 1990–1993)

agentcore remove gateway --name PolicyGateway
agentcore remove policy-engine --name RefundPolicyEngine
agentcore deploy

Removing a gateway does not automatically remove its attached policy engine. You must remove
the policy engine separately using agentcore remove policy-engine.

Core concepts
Before using Policy in Amazon Bedrock AgentCore, it’s important to understand the key concepts
and components that work together to provide policy-based governance for your AI agents.
Topics
• Gateway
• Gateway Target
• Principal types
• Cedar
• Cedar Policy
• Dogwood
• Temporal policies
• Guardrails
• Policy session
• Policy engine
• Cedar Schema
• Cedar validation
• Cedar analysis
• Policy authoring service

Gateway
An Amazon Bedrock AgentCore Gateway provides an endpoint to connect to MCP servers and
convert APIs and lambda to MCP compatible tools, providing a single access point for an agent to
interact with its tools. A Gateway can have multiple targets, each representing a diﬀerent tool or
set of tools.
Core concepts

1990

Gateway Target
A target deﬁnes the APIs or Lambda function that a Gateway will provide as tools to an agent.
Targets can be Lambda functions, OpenAPI speciﬁcations, Smithy models, or other tool deﬁnitions.

Principal types
Cedar policies use principals to represent the entity making an authorization request. Policy in
AgentCore supports two principal types depending on how your AgentCore Gateway is conﬁgured
for authentication:
• AgentCore::OAuthUser - Represents OAuth-authenticated users. When a AgentCore Gateway
uses OAuth authorization, the principal is created from the JWT token’s sub claim. OAuth
principals support tags that contain JWT claims such as username, scope, role, etc.
• AgentCore::IamEntity - Represents IAM-authenticated callers. When a AgentCore Gateway uses
AWS_IAM authorization, the principal is created from the caller’s IAM identity. IAM principals
have an id attribute containing the IAM ARN (format: arn:aws:sts::<account>:assumedrole/<role-name> for assumed roles), enabling stable principal == matching. See Policy
conditions for details.

Cedar
Cedar is an open-source policy language developed by AWS for writing and enforcing authorization
policies. Cedar policies are human-readable, analyzable, and can be validated against a schema.
Policy in AgentCore uses Cedar to provide precise, veriﬁable access control for gateway tools.

Cedar Policy
A Cedar policy is a declarative statement that permits or forbids access to gateway tools. Each
policy speciﬁes who (principal) can perform what action (tool invocation) on which resource
(gateway) under what conditions. Policies are evaluated for every tool invocation request.

Dogwood
Dogwood is an open-source policy language on the Dogwood Policy website that is compatible
with Cedar: every valid Cedar policy is also a valid Dogwood policy, so your existing Cedar policies
work unchanged. Beyond the point-in-time conditions you can already express, Dogwood also
supports session-aware temporal conditions and information providers, such as Guardrails, that
Gateway Target

1991

supply computed signals to a policy. Dogwood policies are evaluated against a policy session that
groups related requests.

Temporal policies
Most Cedar policies are stateless: each request is evaluated on its own. A temporal policy adds
conditions that depend on what happened earlier in the same session, such as requiring a prior
approval, limiting how often an action runs, or keeping a running total under a threshold. Temporal
policies are written in Dogwood, which is compatible with Cedar, and are evaluated against a policy
session that groups related requests. For more information, see Temporal policies.

Guardrails
Guardrails are information providers that a Dogwood policy can consult inline. At evaluation time,
a guardrail computes a content-safety signal for the request — such as a content-ﬁlter, promptattack, or sensitive-information score — and the policy permits or forbids the action based on that
result. For more information, see Guardrails in policies.

Policy session
A policy session is a sequence of related Gateway invocations grouped under one session ID, which
you supply on requests in the x-amzn-bedrock-agentcore-policy-session-id header.
Temporal policies evaluate against a policy session: a temporal condition considers only the events
recorded for the same session as the request being authorized. For more information, see Policy
sessions and identity propagation.

Policy engine
The policy engine is the core component of Policy in AgentCore that stores and evaluates Cedar
policies. When you create policies, they apply to every gateway which is associated with the engine,
as long as the policy scope matches the request. For every tool invocation, the policy engine
evaluates all applicable policies against the request to determine whether to allow or deny access.
The engine enforces default-deny and forbid-wins semantics automatically.

Cedar Schema
A Cedar schema deﬁnes the structure of entities, actions, and context for policy validation. The
policy engine automatically generates a schema from the gateway’s tool deﬁnitions, mapping each
Temporal policies

1992

tool to an action and deﬁning the expected input parameters. The schema ensures policies are
validated at creation time, catching errors before deployment.

Cedar validation
Cedar validation checks that policies are syntactically correct and comply with the schema.
When you associate policies to a gateway, the policy engine validates them against the autogenerated schema to ensure they reference valid actions, use correct data types, and access only
deﬁned context ﬁelds. Validation catches errors before policies are deployed, preventing runtime
authorization failures.

Cedar analysis
Cedar analysis uses automated reasoning to examine policies and detect potential issues. Policy in
AgentCore uses automated reasoning to identify policies that always allow (no conditions restrict
access) or always deny (forbid policies with no exceptions), helping ensure policies implement
intended access control rather than being overly permissive or unnecessarily restrictive.

Policy authoring service
The policy authoring service automatically converts natural language authorization requirements
into Cedar policies. When you submit a natural language policy, the service generates syntactically
correct Cedar code, validates it against the gateway schema, and runs automated analysis to detect
potential issues. This ensures all generated policies are valid and helps identify overly permissive or
restrictive rules before deployment.

AgentCore Gateway and Policy in AgentCore IAM Permissions
This guide provides the required IAM permissions for using Amazon Bedrock AgentCore Gateway
with Policy in AgentCore for ﬁne-grained authorization control using Cedar policies.

Overview
When integrating Amazon Bedrock AgentCore Gateway with Policy in AgentCore, two distinct IAM
roles are required:
1. Gateway Execution Role - The IAM role that Amazon Bedrock AgentCore Gateway assumes at
runtime to invoke targets and evaluate Cedar policies
Cedar validation

1993


## Validate and test policies (LOG_ONLY) (pp. 2092–2099)

Good: "Allow when (A or B) and C" or "Allow when A or (B and C)"

Validate and test policies
Before deploying policies to production, Policy in AgentCore provides validation capabilities to
catch errors and identify potential issues. Validation works diﬀerently depending on whether you
are generating policies from natural language or creating and updating policies directly.
Schema checks always run to verify that policies comply with the Cedar schema for your gateways.
Semantic validation (automated reasoning) detects security and logic issues and can be controlled
through the validationMode parameter. For more information about these capabilities and the
validation modes, see Validation and analysis overview.
Topics
• Test a policy in LOG_ONLY mode
• Validation and analysis overview
• Policy generation: per-policy validation
• Policy create and update: per-policy engine validation

Test a policy in LOG_ONLY mode
Using the policy-level enforcement mode, you can toggle between ACTIVE and LOG_ONLY
to answer the question: "What would this policy do to my traﬃc if it was applied?" Per policy
LOG_ONLY mode lets you test a policy on real traﬃc without aﬀecting authorization decisions.
The policy evaluates every request as if it were enforced, but only writes results to logs. Nothing is
blocked or permitted as a result of a policy whose enforcement mode is LOG_ONLY. Once you trust
the results, promote it to ACTIVE.
Topics
• How LOG_ONLY mode works
• LOG_ONLY policies and LOG_ONLY policy engines
• Set the enforcement mode of a policy
• Observe LOG_ONLY results
• Promote a policy to enforcement
Validate and test policies

2092

• Choosing a threshold with LOG_ONLY mode
• Considerations and limitations

How LOG_ONLY mode works
Every policy in a policy engine has an enforcement mode of either ACTIVE or LOG_ONLY. The
default is ACTIVE, so existing policies, and any new policy you create without specifying the
ﬁeld, continue to enforce as before. When the policy engine evaluates a request, it evaluates
your ACTIVE policies and your LOG_ONLY policies side by side, but only enforces on your ACTIVE
policies.
ACTIVE policies determine the decision that is returned to the AgentCore Gateway and enforced.
The policy engine applies "default-deny" and "forbid-wins" semantics, which means that a request
is allowed only if a policy permits it, and a single forbid from any active policy denies it.
LOG_ONLY policies are evaluated against the same request, but their outcomes are kept separate.
They are reported in traces and emitted as Amazon CloudWatch metrics. They are never combined
into the enforced decision.
Enforcement Mode

Evaluated on each request?

Aﬀects the returned
decision?

ACTIVE (default)

Yes

Yes

LOG_ONLY

Yes

No

A request is evaluated in two stages:
1. The policy engine computes a decision. Only ACTIVE policies contribute to it. LOG_ONLY policies
are evaluated and reported separately, but are never factored in.
2. If the engine is associated to a gateway in ENFORCE mode, the Gateway either allows or denies
the action according to the policy engine’s decision. If the engine is associated to a gateway in
LOG_ONLY mode, the Gateway takes no action; the decision is recorded but not enforced.
ACTIVE and LOG_ONLY are treated as two isolated sets; a LOG_ONLY policy can never change what
your callers experience. The decision a request receives is not impacted by any LOG_ONLY policies.
Test a policy in LOG_ONLY mode

2093

In addition to recording the LOG_ONLY policies that matched on a request, the policy engine
reports which of those policies would have changed the decision if they were ACTIVE. This is a
key signal to use when assessing a policy’s eﬃcacy and safety (i.e., whether it can be promoted to
ACTIVE). For example, a LOG_ONLY policy that matches frequently and appears in the decisionﬂipping set would have blocked your traﬃc during the observation window. Each LOG_ONLY policy
is evaluated independent of all other LOG_ONLY policies to determine the set of decision-ﬂipping
policies. However, each LOG_ONLY policy evaluation does consider all current ACTIVE policies.

LOG_ONLY policies and LOG_ONLY policy engines
Policy in AgentCore has two separate controls that both use the value LOG_ONLY. They operate at
diﬀerent layers and answer diﬀerent questions, so it is important to understand which one you are
setting.
Policy engine enforcement mode: controls the overall behavior of the engine. When set to
LOG_ONLY, no policy in the engine is enforced, regardless of its individual policy mode. All
decisions are logged. This is set using the mode ﬁeld of the policyEngineConfiguration when
you associate a policy engine with a gateway using the CreateGateway or UpdateGateway
operations. The two values that mode accepts are ENFORCE (default) and LOG_ONLY.
Policy mode controls the behavior of a single policy within an enforcing engine. When set
to LOG_ONLY, that policy is still evaluated, but its decision is logged rather than enforced.
All other ACTIVE policies in the engine continue to enforce normally. The two values that
enforcementMode accepts are ACTIVE (default) and LOG_ONLY.
Use policy-level LOG_ONLY to shadow-test a new guardrail in production without aﬀecting traﬃc.
Use engine-level LOG_ONLY to observe the behavior of all policies before enabling enforcement.
Policy Enforcement Mode

Policy Engine
Enforcement Mode

Test a policy in LOG_ONLY mode

ENFORCE

ACTIVE

LOG_ONLY

Evaluated and
enforced. May block
or modify requests.

Evaluated but not
enforced. Decision
is logged only;
other ACTIVE
policies in the
engine still enforce.
2094

LOG_ONLY

Evaluated but not
enforced. Decision is
logged only.

Evaluated but not
enforced. Decision is
logged only.

Note
Policy engine enforcement mode takes precedence. When a policy engine is associated
in LOG_ONLY mode, no policy can deny a Gateway action — not even a policy in ACTIVE
enforcement mode — because the Gateway does not act on the policy engine’s decision at
all. The engine still computes the decision and you still receive LOG_ONLY telemetry; the
decision is simply not enforced.

Set the enforcement mode of a policy
You can set the enforcementMode ﬁeld on a policy when you create or update the policy (i.e.,
CreatePolicy and UpdatePolicy), and it is returned by GetPolicy and ListPolicies.
Create a policy in LOG_ONLY mode Create a policy in LOG_ONLY mode by setting
enforcementMode to LOG_ONLY in the CreatePolicy request. The following example creates a
guardrail in policy that forbids violent content above a conﬁdence threshold, but only observes it.
For more information about guardrails in policy, see guardrails in policies.
aws bedrock-agentcore-control create-policy \
--policy-engine-id my-policy-engine-id \
--name "LogOnlyViolenceFilter" \
--enforcement-mode LOG_ONLY \
--validation-mode IGNORE_ALL_FINDINGS \
--definition '{"policy":{"statement":"forbid (principal, action ==
AgentCore::Action::\"MyTarget\", resource == AgentCore::Gateway::\"arn:aws:bedrockagentcore:us-east-1:111122223333:gateway/my-gateway\") when guardrails
{ BedrockGuardrails::ContentFilter([\"VIOLENCE\"], [context.input.userMessage])
[\"VIOLENCE\"].confidenceScore.greaterThan(decimal(\"0.7\")) };"}}'

The response echoes the policy with "enforcementMode": "LOG_ONLY". The policy begins
evaluating against traﬃc and from that point its matches appear in traces and CloudWatch metrics
— without aﬀecting any decision.
List policies and their enforcement modes
Test a policy in LOG_ONLY mode

2095

ListPolicies returns enforcementMode in each policy summary, so you can see at a glance which
policies are observing and which are enforcing.
aws bedrock-agentcore-control list-policies \
--policy-engine-id my-policy-engine-id \
--query 'policies[].{name:name,enforcementMode:enforcementMode,status:status}'

response
[
{ "name": "LogOnlyViolenceFilter", "enforcementMode": "LOG_ONLY", "status":
"ACTIVE" },
{ "name": "RefundLimit",
"ACTIVE" }

"enforcementMode": "ACTIVE",

"status":

]

Observe LOG_ONLY results
When a caller makes a tools/call request through the AgentCore Gateway, the gateway evaluates
all policies — including LOG_ONLY policies — before returning the MCP response to the caller.
The caller’s response is never aﬀected by LOG_ONLY policies; those results are reported through
observability only.
You observe LOG_ONLY policy behavior through traces and Amazon CloudWatch metrics:
Traces and spans: When you enable tracing on your gateway, policy evaluation spans include
LOG_ONLY match information. You can inspect these spans in the AgentCore Observability console
to see which LOG_ONLY policies ﬁred on a given request and whether they would have ﬂipped
the decision. For more information, see Observe your agent applications on Amazon Bedrock
AgentCore Observability.
CloudWatch metrics: Policy in AgentCore emits metrics under the AWS/Bedrock-AgentCore
namespace. The following metrics are speciﬁc to LOG_ONLY evaluation:

Metric

What it tells you

ConfidenceScore (with PolicyEnf

The conﬁdence score the guardrail returned

orcementMode=LOG_ONLY)

for a matched LOG_ONLY policy. Use this to

Test a policy in LOG_ONLY mode

2096

Metric

What it tells you
understand your traﬃc’s score distribution
when choosing a threshold.

ConfidenceThreshold
orcementMode=LOG_ONLY

(with PolicyEnf
)

LogOnlyMatches

The threshold conﬁgured on the LOG_ONLY
policy. Useful when comparing score against
threshold across policies.
The count of requests where a LOG_ONLY
policy ﬁred. Emitted per policy and as a group
rollup across all LOG_ONLY policies on the
engine.

LogOnlyDecisionFlips

The count of requests where a LOG_ONLY
policy would have changed the decision if
promoted. This is the key promotion signal:
a sustained zero means promoting the policy
will not block current traﬃc.

LogOnlyEvalIncomplete

Emitted when LOG_ONLY evaluation was
partial. Use this to alarm on a sustained rate
of incomplete evaluations.

All metrics include PolicyEngine and OperationName dimensions for ﬁltering. Per-policy metrics
additionally include a Policy dimension with the policy ID.
For more information about viewing metrics for your AgentCore resources, see Bedrock AgentCore
generated observability data.

Promote a policy to enforcement
When you are conﬁdent in a LOG_ONLY policy, promote it to enforcement with UpdatePolicy,
setting enforcementMode to ACTIVE. No other change is required, and the policy keeps its ID,
name, and deﬁnition.
aws bedrock-agentcore-control update-policy \
--policy-engine-id my-policy-engine-id \
--policy-id LogOnlyViolenceFilter-a1b2c3d4e5 \
Test a policy in LOG_ONLY mode

2097

--enforcement-mode ACTIVE

The reverse is also supported: you can move an ACTIVE policy back to LOG_ONLY to take it out of
enforcement while keeping it in place and continuing to observe it.
A typical lifecycle is therefore to create a policy in LOG_ONLY, observe traﬃc and metrics, and
then promote it to ACTIVE — and, if needed, demote it back to LOG_ONLY without deleting and
recreating the policy.

Choosing a threshold with LOG_ONLY mode
LOG_ONLY mode is particularly useful for guardrail policies, where you need to select a conﬁdencescore threshold that balances security against disruption to legitimate traﬃc. A threshold that is
too low blocks legitimate requests; one that is too high may let threats through.
The recommended workﬂow: Deploy the guardrail in LOG_ONLY mode with a threshold you
believe is reasonable (for example, 0.7). The policy evaluates every request and emits a conﬁdence
score to CloudWatch metrics, but never blocks traﬃc.
Accumulate data over a representative window — days or weeks of real production traﬃc. The
ConﬁdenceScore metric (with PolicyEnforcementMode=LOG_ONLY) gives you the distribution of
scores your traﬃc produces.
Analyze the scores against ground truth. If you have a labeled test set (prompts marked as benign
or malicious), you can compute precision and recall at each threshold value and select the one
that best meets your goals. If you do not have labeled data, sample prompts from the high-score
range (for example, 0.8–1.0), the low-score range (0–0.2), and the ambiguous middle zone (0.4–
0.7), then classify each sample to build conﬁdence in your threshold choice. Update the policy with
your chosen threshold and promote it to ACTIVE:
aws bedrock-agentcore-control update-policy \
--policy-engine-id my-policy-engine-id \
--policy-id LogOnlyViolenceFilter-a1b2c3d4e5 \
--enforcement-mode ACTIVE \
--definition '{"policy":{"statement":"forbid (principal, action ==
AgentCore::Action::\"MyTarget\", resource == AgentCore::Gateway::\"arn:aws:bedrockagentcore:us-east-1:111122223333:gateway/my-gateway\") when guardrails
{ BedrockGuardrails::ContentFilter([\"VIOLENCE\"], [context.input.userMessage])
[\"VIOLENCE\"].confidenceScore.greaterThan(decimal(\"0.65\")) };"}}'

Test a policy in LOG_ONLY mode

2098

This workﬂow ensures the threshold reﬂects your actual traﬃc patterns rather than a generic
default.

Considerations and limitations
LOG_ONLY policies never aﬀect decisions. A LOG_ONLY policy cannot cause an action to be
allowed or denied. The decision a request receives is identical to the decision it would receive if the
LOG_ONLY policy did not exist. This is the core guarantee of the feature.
Changes are eventually consistent. Creating, updating, or promoting a policy is applied to the
evaluation path within a few seconds. Plan your observation windows and promotion steps
accordingly rather than expecting an instantaneous switch.
Result lists are bounded. LOG_ONLY match and decision-ﬂipping lists are each capped at 1,000
entries per request. For engines with very large numbers of LOG_ONLY policies, rely on the
CloudWatch metrics for complete aggregate counts.
Evaluation can be partial. When LOG_ONLY evaluation is incomplete for a request, the LOG_ONLY
signals for that request might be missing entries. The enforced decision is never aﬀected.

Validation and analysis overview
Schema checks
Schema checks verify that policies comply with the Cedar schema for your gateways:
• Schema compliance — Checks that policies reference valid actions (tools), use correct data
types, and access only deﬁned context ﬁelds
• Type safety — Ensures parameter types match the gateway’s tool deﬁnitions

Semantic validation (automated reasoning)
Semantic validation uses automated reasoning to detect potential security and logic issues:
• Overly permissive policies — If created, the policy engine will allow all requests for the speciﬁed
principal, action, and resource combination
• Overly restrictive policies — If created, the policy engine will deny all requests for the speciﬁed
principal, action, and resource combination
Validation and analysis overview

2099


## Policy enforcement modes (pp. 2113–2113)

Policy enforcement modes
Enforcement mode deﬁnes how the gateway applies policy decisions. The policy engine supports
two modes:
• In LOG_ONLY mode, the policy engine evaluates and logs whether the action would be allowed
or denied without enforcing the the decision
• In ENFORCE mode, the policy engine evaluates the action and enforces decisions by allowing or
denying agent operations.

Restrict permission to change enforcement mode
If you have the bedrock-agentcore:UpdateGateway permission, you can change a Gateway’s
policyEngineConfiguration.mode from ENFORCE to LOG_ONLY. In LOG_ONLY mode, all
policies are evaluated but not enforced, and every tool call succeeds regardless of forbid policies.
The same permission can set policyEngineConfiguration to null, which removes the policy
engine entirely. No separate action or condition key protects the mode ﬁeld beyond bedrockagentcore:UpdateGateway, so grant this permission only to trusted principals.

Use an AgentCore Gateway with Policy in AgentCore
Follow the gateway authorization and authentication guide to obtain the credentials needed for
gateway access.
MCP tools only
Policy evaluation applies only to MCP tools. Regardless of the policy evaluation mode,
the gateway always allows MCP prompts (prompts/list, prompts/get) and resources
(resources/list, resources/read, resources/templates/list).

Topics
• List AgentCore Gateway Tools with Policy in AgentCore
• Call gateway tools with policy
• Passing the policy session ID for temporal policies
• Policy responses
Policy enforcement modes

2113


## AgentCore optimization: how it works (pp. 2546–2548)

AgentCore optimization: Improve agent quality loop
with recommendations and A/B tests
Amazon Bedrock AgentCore optimization provides tools to continuously improve your agent’s
performance through data-driven conﬁguration changes. Instead of manually rewriting prompts
and testing by hand, you use agent traces to generate improvements and validate them with
controlled experiments.
AgentCore optimization builds on AgentCore Evaluations and introduces three capabilities:
• Recommendations: AI-generated improvements to system prompts and tool descriptions based
on real agent traces and a target evaluator. The service analyzes failure patterns based on the
target evaluator and produces an optimized variant of the system prompt or tool descriptions.
• Conﬁguration bundles: Versioned, immutable snapshots of agent conﬁguration (system
prompts, model IDs, tool descriptions) that decouple agent behavior from code, enabling
behavioral changes without requiring redeployment. Conﬁguration bundles are optional; you can
also validate changes by deploying to a separate runtime endpoint.
• A/B testing: Controlled traﬃc splitting between two variants through AgentCore Gateway, with
online evaluation scoring for each session and reporting statistical signiﬁcance. Variants can
be diﬀerent conﬁguration bundle versions on the same runtime, or diﬀerent gateway targets
pointing to diﬀerent runtime endpoints.
Together, these capabilities form a continuous improvement loop:

Topics
• How it works
• Prerequisites
2546

• Conﬁguration bundles
• Recommendations
• A/B testing
• AgentCore insights: Triage agent failures with pattern analysis

How it works
AgentCore optimization connects evaluation ﬁndings to validated improvements through a
repeatable cycle. A typical iteration follows these steps:
1. Generate a recommendation: Point the Recommendations API at agent traces in CloudWatch
Logs and specify the evaluator you want to optimize for. The service analyzes failure patterns
and returns an optimized system prompt or set of tool descriptions, along with an explanation
of what changed and why.
2. (Optional) Package as a conﬁguration bundle: Create a bundle version with the recommended
conﬁguration. A bundle is a versioned, immutable snapshot of an agent’s conﬁguration
(system prompts, model IDs, tool descriptions) that can be dynamically changed without code
deployments. Conﬁguration bundles are useful when you want to decouple agent behavior from
code; they are not required. You can also validate changes by deploying to a separate runtime
endpoint.
3. Validate with an A/B test: Split production traﬃc between the current agent (control) and
the improved version (treatment) through AgentCore Gateway. Online evaluation scores each
session and reports results with statistical signiﬁcance. A/B tests support two patterns:
• Conﬁguration bundle variants: Same runtime, diﬀerent bundle versions. Use when the
change is purely conﬁguration (prompt, model ID, tool descriptions).
• Target-based variants: Diﬀerent gateway targets pointing to diﬀerent runtime endpoints. Use
when the change includes code changes, a framework upgrade, or when you want to compare
entirely diﬀerent agent implementations. Each variant can have its own online evaluation
conﬁguration.
4. Deploy the winning variant and repeat: Route 100% of traﬃc to the winning variant. New
traces from the new baseline provide the foundation for the next iteration.

How it works

2547

Prerequisites
Before using AgentCore optimization features, make sure the following are in place.

Requirements and supported frameworks
Recommendations and A/B testing have the same agent requirements as AgentCore Evaluations:
• An agent deployed on AgentCore Runtime with observability enabled, or an agent built with a
supported framework conﬁgured with AgentCore Observability. For more information about
supported frameworks and instrumentation libraries, see Supported agent frameworks.
• Transaction Search enabled in CloudWatch.
• Agent sessions with telemetry data in CloudWatch Logs. Invoke your agent and wait 2–5 minutes
for CloudWatch to ingest the telemetry before starting a recommendation or A/B test.

SDK and CLI requirements
• AgentCore CLI: Install the latest version by running agentcore update.
• AWS SDK (boto3): Python 3.10 or later. Install or upgrade with pip install --upgrade
boto3.
• AgentCore SDK: If using the bedrock-agentcore-sdk-python, version 1.8 or later is
required.

IAM permissions
The following IAM policy grants permissions for all three optimization features:
{
"Version": "2012-10-17",
"Statement": [
{
"Sid": "ConfigurationBundles",
"Effect": "Allow",
"Action": [
"bedrock-agentcore:CreateConfigurationBundle",
"bedrock-agentcore:GetConfigurationBundle",
"bedrock-agentcore:GetConfigurationBundleVersion",
"bedrock-agentcore:ListConfigurationBundles",
Prerequisites

2548


## A/B testing (pp. 2637–2642)

• DescribeKey — When validating the key at recommendation creation time.

Behavior when a key becomes unavailable
If you disable or delete the customer managed KMS key used by a recommendation:
• StartRecommendation — Fails at validation with ValidationException.
• GetRecommendation — Fails with ValidationException indicating the KMS key is disabled
or deleted.
• ListRecommendations — Succeeds because listing returns metadata only and does not require
KMS operations.
• DeleteRecommendation — Succeeds because deletion does not require decrypting
recommendation data.

A/B testing
A/B testing splits live production traﬃc between two variants and continuously evaluates
performance with statistical signiﬁcance. The AgentCore Gateway handles traﬃc routing; your
agent code does not change.
A/B testing is the validation step in the AgentCore optimization improvement loop. After
generating a recommendation and validating it with oﬄine batch evaluations, you run an A/B test
to conﬁrm the change improves performance on live traﬃc before committing to a full rollout. You
can route traﬃc to separate AgentCore Runtimes (target-based) or deliver diﬀerent conﬁgurations
to the same AgentCore Runtime (conﬁguration bundles).

When to use A/B testing
Use A/B testing when you need to:
• Validate a recommendation before routing all production traﬃc to the optimized conﬁguration.
• Compare two model versions (for example, moving from one foundation model to another) on
live traﬃc with statistical rigor.
• Measure the impact of a prompt change across real user sessions rather than a curated test set.
• Gradually roll out a new capability (new tools, updated system prompt) by validating it on a
subset of live traﬃc before full deployment.
A/B testing

2637

How it works
An A/B test follows this ﬂow:
1. You initiate an A/B test with agentcore run ab-test, specifying an already-deployed
AgentCore Gateway, two variants (control and treatment), traﬃc weights, and online evaluation
conﬁguration(s) for scoring. (The execution role is optional — pass --role-arn to bring your
own, or let the CLI create one.) Each variant references either an AgentCore Gateway target or a
conﬁguration bundle version. The test starts RUNNING as soon as the command returns (use -disable-on-create to start it stopped).
2. The AgentCore Gateway splits traﬃc. Once the test is running, the gateway splits incoming
traﬃc between the two variants based on the runtime session ID. Assignment is sticky; a given
session ID always routes to the same variant.
3. Online evaluation scores each session. The online evaluation conﬁguration you speciﬁed runs
evaluators against each session as it completes. The A/B test aggregation pipeline maps scores
to variants.
4. The service computes statistical signiﬁcance. As sample sizes grow, the service calculates
per-evaluator metrics for each variant: mean score, absolute and percent change, p-value,
conﬁdence interval, and a signiﬁcance ﬂag. A p-value below 0.05 indicates the diﬀerence is
statistically signiﬁcant. Poll results with agentcore view ab-test <id> at any time without
aﬀecting statistical validity.
5. You promote the treatment variant. When results are signiﬁcant, run agentcore promote
ab-test -i <id> to stop the test and write the treatment variant into agentcore.json,
then agentcore deploy to roll it out. (You can also agentcore stop ab-test -i <id>
without promoting.)

A/B test patterns
A/B tests support two variant conﬁguration patterns:

Target-based variants
Use when the change includes code changes, a framework upgrade, or when you want to compare
entirely diﬀerent agent implementations. Each variant routes to a diﬀerent AgentCore Gateway
target pointing to a diﬀerent runtime endpoint.
How it works

2638

Conﬁguration bundle variants
Use when the change is purely conﬁguration (system prompt, model ID, or tool descriptions). Both
variants run on the same AgentCore Runtime with diﬀerent conﬁguration bundle versions. The
AgentCore Gateway injects the bundle reference into each request via W3C baggage headers,
which the runtime can use to pull the conﬁgurations using the AgentCore SDK.

Choosing a pattern
Aspect

Target-based variants

Conﬁguration bundle
variants

What varies

Entire runtime endpoint
(code, framework, model)

System prompt, tool descripti
ons, model parameters

Routing

Diﬀerent targets per variant

Same target, diﬀerent conﬁg
bundles

Evaluation conﬁg

One online eval conﬁg per
AgentCore Runtime

Single shared online eval
conﬁg

When to use

Code changes, framework
upgrades, comparing
diﬀerent agents

Conﬁguration-only changes
on a single AgentCore
Runtime

A/B testing prerequisites
Before you create an A/B test, ensure the following resources are in place.

Required resources
Resource

Description

AgentCore Gateway

An active AgentCore Gateway with at least one HTTP target
pointing to your agent runtime. The AgentCore Gateway
handles traﬃc splitting between variants.

Conﬁguration bundle variants

2639

Resource

Description

Agent runtime

At least one deployed agent runtime using the Amazon
Bedrock AgentCore SDK (version 1.8+). The SDK’s BaggageSp
anProcessor automatically attaches A/B test experiment
details (experiment ARN and variant name) to all OpenTelem
etry spans emitted by the runtime.
• Conﬁguration bundle based variants: One runtime is
suﬃcient. Both variants run on the same runtime with
diﬀerent conﬁguration bundle versions.
• Target-based variants: Deploy one runtime per variant (two
total).

Online evaluation conﬁgura
tion

An active online evaluation conﬁg that speciﬁes which
evaluators to run against sessions.
• Conﬁguration bundle based variants: One online evaluation
conﬁg that points to the single runtime where both variants
run.
• Target-based variants: One online evaluation conﬁg per
runtime endpoint that you are using for your A/B test (two
total), since each endpoint has its own log group.

Conﬁguration bundles
(optional)

Required when using conﬁguration bundle based variants. Two
bundle versions or two separate bundles: one for control and
one for treatment.

SDK requirements
The Amazon Bedrock AgentCore SDK version 1.8 or later is required. The SDK includes a
BaggageSpanProcessor that reads experiment baggage headers propagated by the AgentCore
Gateway and automatically stamps all runtime OpenTelemetry spans with the experiment ARN and
variant name. The online evaluation pipeline reads these attributes to map session scores to the
correct variant. No additional instrumentation is required in your agent code.

Prerequisites

2640

Evaluator requirements
Note
A/B testing supports built-in, custom LLM-as-judge, and code-based evaluators, but
requires each evaluator to return a numerical value for statistical signiﬁcance computation.
For custom LLM-as-judge evaluators, conﬁgure the ratingScale with a numerical scale
(not categorical). For code-based evaluators, include the value ﬁeld in the response
schema.

IAM permissions
The A/B test execution role must trust the bedrock-agentcore.amazonaws.com service
principal and have permissions for AgentCore Gateway operations, conﬁguration bundle reads,
online evaluation conﬁg reads, and CloudWatch Logs access.
Note
You only need to create this role manually if you bring your own execution role and pass
it with agentcore run ab-test --role-arn <arn>. If you omit --role-arn, the
AgentCore CLI auto-creates an execution role for the test.

Example trust policy:
{
"Version": "2012-10-17",
"Statement": [
{
"Effect": "Allow",
"Principal": {
"Service": "bedrock-agentcore.amazonaws.com"
},
"Action": "sts:AssumeRole",
"Condition": {
"StringEquals": {
"aws:SourceAccount": "${aws:PrincipalAccount}"
},
"ArnLike": {
Prerequisites

2641

"aws:SourceArn": "arn:aws:bedrock-agentcore:*:
${aws:PrincipalAccount}:ab-test/*"
}
}
}
]
}

Example permissions policy:
{
"Version": "2012-10-17",
"Statement": [
{
"Sid": "AgentCoreResources",
"Effect": "Allow",
"Action": [
"bedrock-agentcore:GetGateway",
"bedrock-agentcore:GetGatewayTarget",
"bedrock-agentcore:ListGatewayTargets",
"bedrock-agentcore:CreateGatewayRule",
"bedrock-agentcore:UpdateGatewayRule",
"bedrock-agentcore:GetGatewayRule",
"bedrock-agentcore:DeleteGatewayRule",
"bedrock-agentcore:ListGatewayRules",
"bedrock-agentcore:GetOnlineEvaluationConfig",
"bedrock-agentcore:GetEvaluator",
"bedrock-agentcore:GetConfigurationBundle",
"bedrock-agentcore:GetConfigurationBundleVersion",
"bedrock-agentcore:ListConfigurationBundleVersions"
],
"Resource": "arn:aws:bedrock-agentcore:*:${aws:PrincipalAccount}:*",
"Condition": {
"StringEquals": {
"aws:ResourceAccount": "${aws:PrincipalAccount}"
}
}
},
{
"Sid": "CloudWatchLogsDescribe",
"Effect": "Allow",
"Action": [
"logs:DescribeLogGroups"

Prerequisites

2642


## Resilience (pp. 3306–3307)

Compliance validation for Amazon Bedrock AgentCore
Amazon Bedrock AgentCore is HIPAA eligible and FedRAMP (Class C and Class D), SOC 2 and ISO
(27001:2022, 27017:2015, 27018:2019, 27701:2019, 22301:2019, 20000-1:2018, 9001:2015)
and CSA STAR compliant. In addition, AWS has completed its internal assessment to validate that
Amazon Bedrock AgentCore aligns with the following AWS compliance programs: BIO, C5, CISPE,
CPSTIC, ENS High, FINMA, GNS, GSMA, HITRUST, IRAP, ISMAP, MTCS, OSPAR, PCI, Pinakes and
PiTuKri. Our third-party auditors will review and test Amazon Bedrock AgentCore during the next
audit cycles for these compliance programs.
To learn whether an AWS service is within the scope of speciﬁc compliance programs, see AWS
services in Scope by Compliance Program and choose the compliance program that you are
interested in. For general information, see AWS Compliance Programs.
You can download third-party audit reports using AWS Artifact. For more information, see
Downloading Reports in AWS Artifact.
Your compliance responsibility when using AWS services is determined by the sensitivity of your
data, your company’s compliance objectives, and applicable laws and regulations. For more
information about your compliance responsibility when using AWS services, see AWS Security
Documentation.

Resilience in Amazon Bedrock AgentCore
The AWS global infrastructure is built around AWS Regions and Availability Zones. AWS Regions
provide multiple physically separated and isolated Availability Zones, which are connected with
low-latency, high-throughput, and highly redundant networking. With Availability Zones, you
can design and operate applications and databases that automatically fail over between zones
without interruption. Availability Zones are more highly available, fault tolerant, and scalable than
traditional single or multiple data center infrastructures.
For more information about AWS Regions and Availability Zones, see AWS Global Infrastructure.
In addition to the AWS global infrastructure, AgentCore oﬀers several features to help support your
data resiliency and backup needs.

Compliance validation

3306

Cross-service confused deputy prevention
The confused deputy problem is a security issue where an entity that doesn’t have permission to
perform an action can coerce a more-privileged entity to perform the action. In AWS, cross-service
impersonation can result in the confused deputy problem. Cross-service impersonation can occur
when one service (the calling service ) calls another service (the called service ). The calling service
can be manipulated to use its permissions to act on another customer’s resources in a way it should
not otherwise have permission to access. To prevent this, AWS provides tools that help you protect
your data for all services with service principals that have been given access to resources in your
account.
We recommend using the aws:SourceArn and aws:SourceAccount global condition context keys in
resource policies to limit the permissions that Amazon Bedrock AgentCore gives another service to
the resource. Use aws:SourceArn if you want only one resource to be associated with the crossservice access. Use aws:SourceAccount if you want to allow any resource in that account to be
associated with the cross-service use.
The most eﬀective way to protect against the confused deputy problem is to use the
aws:SourceArn global condition context key with the full ARN of the resource. If you don’t know
the full ARN of the resource or if you are specifying multiple resources, use the aws:SourceArn
global context condition key with wildcard characters ( * ) for the unknown portions of the ARN.
For example, arn:aws:servicename:*:123456789012:*.
If the aws:SourceArn value does not contain the account ID, such as an Amazon S3 bucket ARN,
you must use both global condition context keys to limit permissions.
The following example shows how you can use the aws:SourceArn and aws:SourceAccount
global condition context keys in AgentCore to prevent the confused deputy problem.
{
"Version":"2012-10-17",
"Statement": [
{
"Sid": "AssumeRolePolicy",
"Effect": "Allow",
"Principal": {
"Service": "bedrock-agentcore.amazonaws.com"
},
"Action": "sts:AssumeRole",
"Condition": {
Cross-service confused deputy prevention

3307


## Runtime service quotas (pp. 3317–3325)

For conﬁgurable per-invocation controls (such as iteration, timeout, and token caps), see Control
cost with limits.

AgentCore Runtime Service Quotas
When working with AgentCore Runtime, you need to be aware of the service limits that apply to
your account. These limits help ensure service stability and availability for all users.

Resource allocation limits
The following table describes the resource allocation limits for AgentCore Runtime. You can
request increases for some quotas using the Service Quotas console.
Limit

Default Value

Adjustable

Notes

Active session
workloads per
account

5,000 in US East
(N. Virginia) and US
West (Oregon), and
2,500 in other AWS
Regions.

Yes

Can be increased via
Service Quotas

Total agents per
account

1,000

Yes

Can be increased via
Service Quotas

Versions per agent

1,000

Yes

Can be increased via
Service Quotas

Endpoints (aliases)
per agent

10

Yes

Can be increased via
Service Quotas

Maximum size for a
Docker image in an
AgentCore Runtime

2 GB

No

Maximum size
for a direct code
deployment package
(compressed)

250 MB

No

AgentCore Runtime Service Quotas

ZIP ﬁle size limit
for direct code
deployment

3317

Limit

Default Value

Adjustable

Notes

Maximum size
for a direct code
deployment package
(uncompressed)

750 MB

No

Unzipped package
size limit for direct
code deployment

Maximum hardware
allocation per session

2vCPU/8GB

No

The maximum
memory/CPU usage
and allocation per
Runtime session

Capacity providers
per account

1,000

No

Applies to the
Instances compute
type in your account.
Counts all capacity
providers that you
have not deleted,
including those being
created or deleted.

Agents per capacity
provider session

20

No

Applies to the
Instances compute
type. The maximum
number of agents
that you can run on
a single capacity
provider session.

For more information about service quotas and how to request increases, see Requesting a quota
increase in the Service Quotas User Guide.

Note
Because the Instances compute type provisions Amazon EC2 resources in your own
account, your account’s quotas for those resources apply in addition to the AgentCore
quotas in the preceding table. AgentCore calls the following services on your behalf
Resource allocation limits

3318

to provision and manage instances, which consumes your account’s quotas. For highthroughput workloads, you might need to request increases for the following:
• Amazon EC2 – the running instance count for the instance families you select, and the
request rates for the instance operations that AgentCore calls, such as RunInstances,
CreateFleet, DescribeInstances, TerminateInstances, and CreateTags. For
more information, see Amazon EC2 service quotas.
• Amazon EBS – the volume quotas for the volume types you use, and the request rates
for the volume operations that AgentCore calls, such as CreateVolume, AttachVolume,
DetachVolume, DeleteVolume, and DescribeVolumes. For more information, see
Quotas for Amazon EBS.
• Amazon VPC – the number of network interfaces, and the request rates for the network
interface operations that AgentCore calls, such as AttachNetworkInterface and
DescribeNetworkInterfaces. For more information, see Amazon VPC quotas.
• Amazon EC2 Auto Scaling – a single shared quota that applies to all Amazon EC2 Auto
Scaling API calls, rather than to an individual operation. This quota isn’t available in the
Service Quotas console. To request an increase, open an AWS Support case. For more
information, see Request throttling for the Amazon EC2 Auto Scaling API.
To request an increase for a quota that is available in the Service Quotas console, see
Requesting a quota increase in the Service Quotas User Guide.

Invocation limits
The following table describes the invocation limits for AgentCore Runtime. You can request
increases for some quotas using the Service Quotas console.
Limit

Value

Adjustable

Notes

Request timeout

15 minutes

No

Maximum time for
synchronous requests

Maximum payload
size

100 MB

No

Maximum size for
request/response
payloads

Invocation limits

3319

Limit

Value

Adjustable

Notes

Streaming chunk size

10 MB

No

Maximum size for
individual chunks

Streaming maximum
duration

60 mins

No

Maximum time
for streaming
connections
(Response streaming,
WebSocket connectio
ns)

Asynchronous job
maximum duration

8 hours

No

Maximum execution
time for asynchron
ous jobs

WebSocket frame size

64 KB

No

Maximum size for
individual WebSocket
frames

For more information about service quotas and how to request increases, see Requesting a quota
increase in the Service Quotas User Guide.

Throttling limits
The following table describes the rate limits for AgentCore Runtime after which you will be
throttled. You can request increases for some quotas using the Service Quotas console.

Limit

Value

Adjustable

Notes

Data plane API
request rate

1,000 TPS

Yes

Transactions per
second per account.
This quota is shared
across all data plane
APIs and is not
enforced for each API
individually. It applies

Throttling limits

3320

Amazon Bedrock AgentCore

Limit

Developer Guide

Value

Adjustable

Notes
to the following
APIs: InvokeAge
ntRuntime
, InvokeAge
ntRuntime
Command ,
InvokeAge
ntRuntime
WithWebSo
cketStrea
m , InvokeAge
ntRuntime
CommandSh
ell , StopRunti
meSession
, GetAgentC
ard , GetRuntim
eProtecte
dResource
Metadata .
Additional
InvokeAge
ntRuntime
Command limits:
command size 1
byte–64 KB, response
size up to 100 MB,
timeout 1–3600
seconds (default 300
seconds). Streaming
chunk size is up
to 64 KB for each
event; session ID
minimum is 33

Throttling limits

3321

Amazon Bedrock AgentCore

Limit

Developer Guide

Value

Adjustable

Notes
characters. Additiona
l InvokeAge
ntRuntime
CommandShell
limits: maximum
connection duration
1 hour, maximum
frame payload 64 KB,
up to 10 concurren
t shell sessions per
runtime, reconnect
ion buﬀer 256 KB.

New Runtime session
creation rate

25 TPS

Yes

Transactions per
second per account.
This quota is shared
across all endpoints
and is not enforced
for each endpoint
individually. It applies
to new session
creation for both
container-image
and direct code
deployment agents.

WebSocket frame
rate per connection

Throttling limits

250 frames per
second

No

3322

Limit

Value

Adjustable

Notes

Control plane
mutation API rate

50 TPS

No

Transactions per
second per account.
This quota is shared
across all control
plane mutation
APIs and is not
enforced for each API
individually. It applies
to CreateAge
ntRuntime
, CreateAge
ntRuntime
Endpoint ,
UpdateAge
ntRuntime
, UpdateAge
ntRuntime
Endpoint ,
DeleteAge
ntRuntime

,

and DeleteAge
ntRuntime
Endpoint .

Throttling limits

3323

Limit

Value

Adjustable

Notes

Control plane Get API
rate

150 TPS

No

Transactions per
second per account.
This quota is shared
across all control
plane Get APIs and
is not enforced for
each API individua
lly. It applies to
GetAgentRuntime
and GetAgentR
untimeEndpoint

Control plane List API
rate

25 TPS

No

.

Transactions per
second per account.
This quota is shared
across all control
plane List APIs and
is not enforced for
each API individua
lly. It applies
to ListAgent
Runtimes ,
ListAgent
RuntimeEn
dpoints , and
ListAgent
RuntimeVe
rsions .

For more information about service quotas and how to request increases, see Requesting a quota
increase in the Service Quotas User Guide.

Lifetime session lifecycle parameters
The following table describes the lifetime session lifecycle parameters for AgentCore Runtime:
Lifetime session lifecycle parameters

3324

Phase

Timeout

Adjustable

Notes

Idle session timeout

15 minutes of
inactivity

Yes, through

When this limit
is reached, the
execution environme
nt is terminated and
a new one is created
for the session

the idleRunti
meSession
Timeout API
parameter in
the Lifecycle
Configuration
data type

Maximum session
duration

8 hrs

Yes, through the
maxLifetime
API parameter in
the Lifecycle
Configuration
data type

Session storage limits
The following table describes the limits for session storage:
Limit

Value

Adjustable

Description

Maximum storage
size

1 GB

No

Maximum total
storage size per
session

Maximum ﬁlesystem
metadata

~50 MB

No

Approximately
100,000–200,000
ﬁles

Maximum directory
depth

200 levels

No

Maximum nested
directory depth

Maximum ﬁlename
length

255 bytes

No

Maximum length of a
single ﬁlename

Session storage limits

3325


## Memory service quotas (pp. 3326–3334)

Limit

Value

Adjustable

Description

Maximum symlink
target length

4,095 bytes

No

Maximum length of a
symlink target path

AgentCore Memory Service Quotas
The following table describes the lifetime session lifecycle parameters for AgentCore Memory:
Limit

Value

Adjustable

Maximum number of
AgentCore Memory
resources per AWS
Region in an AWS
account

150

Yes

Maximum number
of memory strategie
s per AgentCore
Memory resource

6

No

Maximum memory
strategies per
account

900

Yes

Maximum CreateMem
ory requests

3

Yes

Notes

The maximum
number of
CreateMemory
requests per second
that you can perform
in this AWS account
in the current AWS
Region.

Maximum
GetMemory requests
AgentCore Memory Service Quotas

50

Yes

The maximum
number of
3326

Amazon Bedrock AgentCore

Limit

Developer Guide

Value

Adjustable

Notes
GetMemory
requests per second
that you can perform
in this AWS account
in the current AWS
Region.

Maximum DeleteMem
ory requests

3

Yes

The maximum
number of
DeleteMemory
requests per second
that you can perform
in this AWS account
in the current AWS
Region.

Maximum ListMemor
ies requests

5

Yes

The maximum
number of
ListMemories
requests per second
that you can perform
in this AWS account
in the current AWS
Region.

Maximum
UpdateMemory
requests

3

Yes

The maximum
number of
UpdateMemory
requests per second
that you can perform
in this AWS account
in the current AWS
Region.

AgentCore Memory Service Quotas

3327

Limit

Value

Adjustable

Minimum EventExpi
rationDuration days
in a CreateEvent
operation

7

No

Maximum EventExpi
rationDuration days
in a CreateEvent
operation

365

No

Maximum prompt
size (AppendTo
Prompt) for custom
memory strategy
(Extraction/Consol
idation)

30 KB

No

Maximum number
of messages
per CreateEvent
operation

100

No

Maximum message
size in a CreateEvent
operation

100 KB

No

Maximum event size
in a CreateEvent
operation

10 MB

No

Maximum number of
payload items in an
IngestData operation

100

No

AgentCore Memory Service Quotas

Notes

3328

Limit

Value

Adjustable

Notes

Maximum payload
item size in an
IngestData operation

100 KB

No

Maximum total
payload size per
IngestData request

100 KB

No

The combined size of
all payload items.

Maximum CreateEve
nt requests

200

Yes

The maximum
number of
CreateEvent
requests per second
that you can perform
in this AWS account
in the current AWS
Region.

Maximum CreateEve
nt requests per
actor, per session,
including conversat
ional payloads

AgentCore Memory Service Quotas

5

No

The maximum
number of
CreateEvent
requests per second,
per actor, per session,
including conversat
ional payloads that
you can perform in
this AWS account
in the current AWS
Region.

3329

Limit

Value

Adjustable

Notes

Maximum CreateEve
nt requests per actor,
per session, not
including conversat
ional payloads

10

No

The maximum
number of

Maximum IngestData
requests

10

CreateEvent
requests per second,
per actor, per
session, not including
conversational
payloads that you can
perform in this AWS
account in the current
AWS Region.
No

The maximum
number of
IngestData
requests per second
that you can perform
in this AWS account
in the current AWS
Region.

Maximum IngestDat
a requests per actor,
per session, including
conversational
payloads

AgentCore Memory Service Quotas

5

No

The maximum
number of
IngestData
requests per second,
per actor, per session,
including conversat
ional payloads that
you can perform in
this AWS account
in the current AWS
Region.

3330

Limit

Value

Adjustable

Notes

Maximum IngestDat
a requests per actor,
per session, not
including conversat
ional payloads

10

No

The maximum
number of

Maximum DeleteEve
nt requests

20

IngestData
requests per second,
per actor, per
session, not including
conversational
payloads that you can
perform in this AWS
account in the current
AWS Region.
Yes

The maximum
number of
DeleteEvent
requests per second
that you can perform
in this AWS account
in the current AWS
Region.

Maximum DeleteEve
nt requests per actor,
per session

5

Yes

The maximum
number of
DeleteEvent
requests per second,
per actor, per session
that you can perform
in this AWS account
in the current AWS
Region.

AgentCore Memory Service Quotas

3331

Limit

Value

Adjustable

Notes

Maximum ListEvents
requests

200

Yes

The maximum
number of
ListEvents
requests per second
that you can perform
in this AWS account
in the current AWS
Region.

Maximum ListEvent
s requests per actor,
per session

20

No

The maximum
number of
ListEvents
requests per second,
per actor, per session
that you can perform
in this AWS account
in the current AWS
Region.

Maximum RetrieveM
emoryRecords
requests

30

Yes

The maximum
number of
RetrieveM
emoryRecords
requests per second
that you can perform
in this AWS account
in the current AWS
Region.

AgentCore Memory Service Quotas

3332

Limit

Value

Adjustable

Notes

Maximum ListMemor
yRecords requests

30

Yes

The maximum
number of
ListMemor
yRecords requests
per second that you
can perform in this
AWS account in the
current AWS Region.

Maximum requests
for all other
AgentCore Memory
APIs

20

Yes

The maximum
transactions per
second (TPS) that
can be processed in
this AWS account
in the current AWS
Region for all other
AgentCore Memory
APIs.

AgentCore Memory Service Quotas

3333

Limit

Value

Adjustable

Notes

Maximum number of
tokens per minute for
long-term memory
extraction

150,000

Yes

The maximum
number of tokens
per minute that can
be processed for
long-term memory
extraction for built-in
strategies in this AWS
account in the current
AWS Region. You can
monitor token use
through the Amazon
CloudWatch metric
named TokenCoun
t in the BedrockAgentCore
namespace. You can
request an increase
to this limit through
the Service Quotas
console.

Maximum number of
tokens per minute for
episodic long-term
memory extraction
per session

50,000

No

The per-session,
tokens per minute
limit that can be
processed for
episodic long-term
memory extraction
in this AWS account
in the current AWS
Region.

AgentCore Memory Service Quotas

3334


## Gateway service quotas (pp. 3338–3340)

Limit

Value

Adjustable

Notes

UpdatePaymentCrede
ntialProvider API rate

20 TPS

Yes

Transactions per
second per account

DeletePaymentCrede
ntialProvider API rate

20 TPS

Yes

Transactions per
second per account

ListPaymentCredent
ialProviders API rate

20 TPS

Yes

Transactions per
second per account

GetResourceOauth2T
oken API rate

200 TPS

Yes

Transactions per
second per account

GetResourceApiKey
API rate

200 TPS

Yes

Transactions per
second per account

GetResourcePayment
Token API rate

200 TPS

Yes

Transactions per
second per account

CompleteResourceTo
kenAuth API rate

100 TPS

Yes

Transactions per
second per account

For more information about service quotas and how to request increases, see Requesting a quota
increase in the Service Quotas User Guide.

AgentCore Gateway Service Quotas
This section provides information about Amazon Bedrock AgentCore Gateway endpoints and
service limits.

Endpoints
Amazon Bedrock AgentCore Gateway provides AWS Region-speciﬁc endpoints for management
operations and runtime access.
The Amazon Bedrock AgentCore Gateway control plane endpoints use the following format, where
you can replace <region> with any of the AWS Regions listed in Supported AWS Regions.
AgentCore Gateway Service Quotas

3338

bedrock-agentcore-control.<region>.amazonaws.com

The AgentCore Gateway URLs for runtime access have the following format:
https://{gateway-Id}.gateway.bedrock-agentcore.{Region}.amazonaws.com

Where:
• {gateway-Id} is the unique identiﬁer for your gateway
• {Region} is the AWS Region where your gateway is deployed
Gateway ARNs have the following format:
arn:${Partition}:bedrock-agentcore:${Region}:${Account}:gateway/${gateway-Id}

The AgentCore service principal is: bedrock-agentcore.amazonaws.com

Service quotas
Amazon Bedrock AgentCore Gateway has the following service quotas. You can request increases
for some quotas using the Service Quotas console.

Quota

Default value

Adjustable

Number of gateways per
account

1000

Yes

Number of targets per
gateway

100

Yes

Number of tools per target

1000

Yes

Timeout for a gateway
invocation

15 minutes

Yes

Maximum inline schema size

1 MB

Yes

Service quotas

3339

Quota

Default value

Adjustable

Maximum S3 payload schema
size

10 MB

Yes

Tool name character limit

256 characters

Yes

CreateGateway API rate

5 transactions per second

Yes

UpdateGateway API rate

5 transactions per second

Yes

GetGateway API rate

10 transactions per second

Yes

ListGateways API rate

10 transactions per second

Yes

DeleteGateway API rate

5 transactions per second

Yes

CreateGatewayTarget API rate

5 transactions per second

Yes

UpdateGatewayTarget API
rate

5 transactions per second

Yes

GetGatewayTarget API rate

10 transactions per second

Yes

ListGatewayTargets API rate

10 transactions per second

Yes

DeleteGatewayTarget API rate

5 transactions per second

Yes

Concurrent target operations
(total of Create/Update/Dele
teTarget) on same gateway

5

Yes

tool-call/tool-list rate at
gateway level

200 transactions per second

Yes

tool-call/tool-list rate at
account level

200 transactions per second

Yes

tool-call/tool-list concurrent
connections at gateway level

5000 concurrent connections

Yes

Service quotas

3340
