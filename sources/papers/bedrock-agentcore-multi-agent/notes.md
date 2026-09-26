# Amazon Bedrock AgentCore Developer Guide — Multi-agent runtime, A2A, shared memory, and Agent Registry (selected chapters)

## Summary

This filtered excerpt of the AWS Bedrock AgentCore Developer Guide covers the parts of the 3,428-page manual relevant to running and coordinating multiple agents in production. It contrasts AgentCore Harness (a managed, configuration-driven agent loop) with AgentCore Runtime (a serverless hosting environment where you own the orchestration code), and lays out the four wire protocols Runtime supports for talking to agents — HTTP, MCP, A2A, and AG-UI — with A2A singled out as the protocol built specifically for agent-to-agent communication.

The A2A protocol contract section specifies exactly what an agent-to-agent server must implement: JSON-RPC 2.0 transport, a fixed container shape (port 9000, ARM64), a discovery endpoint (`/.well-known/agent-card.json`), and a health endpoint (`/ping`). Runtime enforces session isolation through per-session microVMs with defined lifecycle states (Active, Idle, Stopped) and default timeouts, while asynchronous long-running agents extend that lifecycle safely through a health-probe pattern (`Healthy` vs. `HealthyBusy`) instead of a separate task-tracking system. Inbound/outbound auth chains this together so one agent can call another under proper credentials.

The memory portion explains how AgentCore Memory separates short-term (per-session, turn-by-turn) from long-term (cross-session, extracted insights) memory, and how namespaces — hierarchical, trailing-slash-terminated paths keyed by actor, session, and strategy — let many actors or agents share one memory resource without collision, while also serving as IAM condition keys for access control. Cross-account access extends this to multi-account architectures via resource-based policies. A short section distinguishes long-term memory (personalized, evolving state about a specific user) from RAG (retrieval of authoritative, current external knowledge), and another covers memory poisoning: because long-term memory extraction runs asynchronously through an LLM, poisoned input becomes a persistent, repeatedly-retrieved corruption rather than a single-turn hijack, so defenses belong at the `CreateEvent` write boundary.

Finally, AWS Agent Registry addresses a governance problem specific to organizations running many agents and tools: a centralized, curated catalog with an approval workflow, hybrid (semantic + keyword) search, and a native MCP endpoint so both humans and other agents can discover approved resources instead of rebuilding what already exists.

## Knowledge Map

- Harness (config-driven loop) vs. Runtime (bring-your-own orchestration) as two ways to buy the same agent infrastructure
- The four Runtime wire protocols (HTTP, MCP, A2A, AG-UI) and the A2A protocol contract in detail
- microVM session isolation, lifecycle states, and health-probe-driven task liveness for long-running agents
- AgentCore Memory: short-term vs. long-term, namespace-based multi-tenant organization, and cross-account sharing
- Long-term memory vs. RAG as complementary, not competing, mechanisms
- Memory poisoning as a persistence-layer security concern distinct from single-turn prompt injection
- AWS Agent Registry: centralized discovery and governance for agents, MCP servers, and skills across an organization

## Key Takeaways

- Choose Harness when configuration agility matters more than orchestration control, and Runtime when the reverse is true — they are not competing products.
- A2A servers must meet a fixed contract (port 9000, ARM64, JSON-RPC 2.0, agent-card discovery, ping health) to interoperate with any AgentCore-hosted caller.
- Session isolation is infrastructure-guaranteed (per-session microVM), not something the agent's own logic has to enforce.
- A busy health probe (`HealthyBusy`) is a lightweight way to keep a long-running session alive without building custom task-tracking.
- Namespace design for shared memory is also an access-control mechanism, not just an organizational convenience.
- Treat memory poisoning as a durable, repeatedly-replayed risk that must be stopped at the write boundary, not cleaned up after the fact.
- A resource registry with an approval workflow prevents agent/tool sprawl at the same scale where multi-agent systems start to pay off.

## Source Text

Source: Amazon Bedrock AgentCore Developer Guide (3,428-page PDF), filtered to selected page ranges.


## Overview (pp. 1–8)

Overview
What is Amazon Bedrock AgentCore?
Amazon Bedrock AgentCore is an agentic platform for building, deploying, and operating highly
eﬀective agents securely at scale using any framework and foundation model. With AgentCore, you
can enable agents to take actions across tools and data with the right permissions and governance,
run agents securely at scale, and monitor agent performance and quality in production - all
without any infrastructure management. AgentCore services work together or independently with
any open-source framework such as CrewAI, LangGraph, LlamaIndex, and Strands Agents and with
any foundation model, so you don’t have to choose between open-source ﬂexibility and enterprisegrade security and reliability.

What is Amazon Bedrock AgentCore?

1

Core services in Amazon Bedrock AgentCore
Amazon Bedrock AgentCore includes the following modular services and capabilities that you can
use together or independently:
Service

Description

Integrations

Harness

A managed agent loop that
lets you deﬁne and invoke
AI agents with a single API
call. Specify a model, system
prompt, and tools inline.
Harness handles orchestra
tion, tool execution, memory

AgentCore Harness works
with Amazon Bedrock,
OpenAI, Google Gemini,
and any OpenAI-compatible
model provider. Integrate
s with AgentCore Memory,
Gateway, Browser, Code

management, and response
generation. Each session runs
in an isolated microVM with
ﬁlesystem and shell access,
supporting use cases like code
generation, data analysis, and
deep research. Bring your own
container image for custom
environments with additional
dependencies.

Interpreter, and Observability.
Supports remote MCP servers,
inline functions, and custom
container environments.

A secure, serverless runtime
environment purpose-built
for deploying and scaling
dynamic AI agents and tools.
Runtime provides fast cold
starts for real-time interacti
ons, extended runtime

AgentCore Runtime works
with custom frameworks and
any open-source framework,
including CrewAI, LangGraph
, LlamaIndex, Google ADK,
OpenAI Agents SDK, and
Strands Agents, any foundatio

support for asynchronous
agents, true session isolation
, built-in identity, and support
for multi-modal and multiagent agentic workloads.

n model in or outside of
Amazon Bedrock including
OpenAI, Google’s Gemini,
Anthropic’s Claude, Amazon
Nova, Meta Llama, and

Runtime

Core services in Amazon Bedrock AgentCore

2

Amazon Bedrock AgentCore

Service

Developer Guide

Description

Integrations
Mistral models, and popular
protocols like MCP and A2A.

Memory

A way to build context-a
ware agents with complete
control over what the agent
remembers and learns.
Supports for both short-ter
m memory for multi-turn
conversations and long-term

AgentCore Memory works
with LangGraph, LangChain,
Strands, LlamaIndex

memory that persists across
sessions, with the ability to
not only share memory stores
across agents but also learn
from experiences.
Gateway

A secure way to convert your
APIs, Lambda functions, and
existing services into Model
Context Protocol (MCP)-com
patible tools and also connect
to pre-existing MCP servers,
making them available to

Any APIs, MCP tools, Lambda,
and popular integrations
including Salesforce, Zoom,
JIRA, Slack etc.

AI agents through Gateway
endpoints with just a few
lines of code.
Identity

A secure, scalable agent
identity, access and authentic
ation management service
which is compatible with
existing identity providers
, eliminating needs for user
migration or rebuilding

Any IdP and credential
providers such as Amazon
Cognito, Okta, Microsoft
Azure Entra ID, Auth0 etc.

authentication ﬂows.

Core services in Amazon Bedrock AgentCore

3

Service

Description

Integrations

Code Interpreter

An isolated sandbox
environment for agents to
execute code enhancing their
accuracy and expanding their
ability to solve complex endto-end tasks.

Multiple languages including
Python, JavaScript and
TypeScript

Browser

A fast and secure cloudbased browser runtime
environment to enable AI
agents to interact with web
applications, ﬁll forms,
navigate websites, and
extract information in a fully

Any foundation model or
popular browser automatio
n frameworks including
Playwright and BrowserUse

managed environment.
Observability

A uniﬁed view to trace, debug
and monitor agent performan
ce in production. It oﬀers
detailed visualizations of each
step in the agent workﬂow,
enabling you to inspect an
agent’s execution path, audit

Any monitoring and
observability stack that
integrate with telemetry
data emitted in standardized
OpenTelemetry (OTEL)-co
mpatible format

intermediate outputs, and
debug performance bottlenec
ks and failures.

Core services in Amazon Bedrock AgentCore

4

Service

Description

Integrations

Payments

A fully managed service that
enables microtransaction
payments for AI agents to
access paid APIs, MCP servers,
and content using the x402
protocol and the Machine
Payments Protocol (MPP).

AgentCore payments
supports Coinbase CDP and
Stripe (Privy) wallet providers
, AgentCore Gateway, Strands
Agents, any x402-comp
atible or MPP-compatible
endpoint, AgentCore Identity

Payments provides wallet
integration, conﬁgurable
spending limits, and end-toend observability for agent
payment operations.

and AgentCore Observabi
lity powered by Amazon
CloudWatch for uniﬁed
monitoring.

A purpose-built evaluatio
n service for automated,
consistent, and data-driven
agent assessment. AgentCore
Evaluations measures how
well your agents and tools
execute tasks, handle edge

AgentCore Evaluations
supports evaluations on
sessions, traces, and spans
generated from Strands
Agent or LangGraph
frameworks, and instrumen
ted using OpenTelemetry or

cases, and maintain output
reliability across diverse
inputs and contexts. Evaluatio
ns provides measurable
quality signals, helps teams
optimize performance using
structured insights, and
ensures your agent meets
functional and behavioral
standards before and after
deployment.

OpenInference. All results
integrated into AgentCore
Observability powered by
Amazon CloudWatch for
uniﬁed monitoring.

Evaluations

Core services in Amazon Bedrock AgentCore

5

Service

Description

Integrations

Optimization

A continuous improvement
service that uses AI-generated
recommendations, versioned
conﬁguration bundles, and
A/B testing to improve agent
performance through datadriven conﬁguration changes.

AgentCore optimizat
ion builds on AgentCore
Evaluations and works with
agents instrumented using
OpenTelemetry via AgentCore
Observability. Supports
system prompt and tool

Instead of manual, guesswork
-driven optimization, you
point the service at agent
traces to generate improveme
nts and validate them with
controlled experiments.

description optimization
with traﬃc splitting through
AgentCore Gateway for A/B
testing.

A capability that provides
deterministic control to
ensure agents operate
within deﬁned boundaries
and business rules without
slowing them down. Easily
author ﬁne-grained rules

Integrates with AgentCore
Gateway, to intercept every
tool call before execution.
You can deﬁne which tools
agents can access, what
actions they can perform, and
under what conditions.

Policy

using natural language or
Cedar (AWS's open-source
policy language).

Core services in Amazon Bedrock AgentCore

6

Service

Description

Integrations

Registry

A centralized catalog for
discovering and managing
agents, MCP servers, tools,
skills and custom resources
across your organization.
Registry provides a governed
workﬂow for publishing,

AgentCore Registry works
with any MCP Server, Agent,
Skill or Custom Resource,
deployed on AWS, OnPrem or on any other Cloud
environment.

reviewing, and approving
resources, with hybrid
semantic and keyword search
so that agents and developers
can ﬁnd the right tools.

What can you build with Amazon Bedrock AgentCore?
With Amazon Bedrock AgentCore, developers can accelerate AI agents into production with the
scale, reliability, and security, critical to real-world deployment. Some common use cases for which
you must consider leveraging AgentCore are:
• Agents
Build autonomous AI apps that reason, use tools, and maintain context. Deploy agents for
customer support, workﬂow automation, data analysis, or coding assistance. Your agent runs
serverless with isolated sessions, persistent memory, and built-in observability.
• Tools and Model Context Protocol (MCP) Servers
Transform existing APIs, databases, or services into tools that any MCP-compatible agent
can use. Deploy a gateway that wraps your Lambda functions or OpenAPI specs making your
backend instantly accessible to agents without rewriting code.
• Agent Platforms
Provide your internal developers or customers with a paved path to build and deploy agents
using approved tools, shared memory stores, and governed access to enterprise services.
Centralize observability, authentication, and compliance while enabling teams to ship agentpowered features faster.
What can you build with Amazon Bedrock AgentCore?

7

Pricing for Amazon Bedrock AgentCore
AgentCore oﬀers ﬂexible, consumption-based pricing with no upfront commitments or minimum
fees. For more information, see AgentCore pricing . AgentCore may use and store your content
to improve your service experience or performance. Such improvements would be for your use of
AgentCore and not for other customers.

Next Steps
If you are a ﬁrst-time user of Amazon Bedrock AgentCore, we recommend that you begin by
reading the following sections:
• Get started with the AgentCore CLI
• Understand the available interfaces for using Amazon Bedrock AgentCore

Pricing for Amazon Bedrock AgentCore

8


## Harness vs. Runtime (pp. 139–142)

AgentCore harness vs. Runtime
AgentCore harness and AgentCore Runtime solve diﬀerent parts of the same problem. This page
explains the conceptual diﬀerence and provides a feature-by-feature comparison to help you
choose between them.

Conceptual diﬀerence
AgentCore Runtime is a serverless hosting environment. You bring agent code - written in
any framework or no framework - wrap it with the AgentCore SDK’s BedrockAgentCoreApp
entrypoint, package it into an ARM64 container, push it to Amazon ECR, and deploy. The
orchestration loop is yours. To use any other AgentCore primitive (Memory, Gateway, Browser, Code
Interpreter, outbound Identity), you call it from your code, typically through the AgentCore SDK.
Runtime provides the infrastructure - isolation, scaling, sessions, auth gating, and observability
plumbing - while the agent logic is code you write.
AgentCore harness is a managed agent harness - the orchestration loop itself is provided,
powered by Strands Agents. You declare what the agent is (model, system prompt, tools,
memory, limits) as conﬁguration, and AgentCore runs the loop. Most features are a single conﬁg
ﬁeld: switching a model or adding a tool is a conﬁg change, not a redeploy. The harness is a
managed abstraction that runs inside Runtime - CloudTrail records harness operations under
AWS::BedrockAgentCore::Runtime.
For nearly every feature, the pattern is the same:
• Harness - conﬁguration, no code.
• Runtime - you write code, usually with the AgentCore SDK plus your framework.
The grid below makes the per-feature exceptions explicit.

Feature grid
The Supported? columns use the following legend:
• # - Supported with no custom code required.
• # - Supported, but you must maintain your own implementation.
• # - Conﬁguration enables it, but code is required to fully use it.
Harness vs. Runtime

139

• # - Not supported.

Feature / Capability

Harness:
supported
?

Harness:
customer
code
required?

Runtime:
supported
?

Runtime:
customer
code
required?

Model selection (Bedrock / OpenAI /
Gemini / LiteLLM)

#

No

#

Yes

Switch model provider mid-session

#

No

#

Yes

Built-in shell and file_operations
tools

#

No

#

Yes

Agent Skills

#

No

#

Yes

Observability

#

No

#

Yes

AgentCore Memory - short-term

#

No

#

Yes

AgentCore Memory - long-term
(semantic, summarization, user-pref,
episodic)

#

No

#

Yes

Per-user memory scoping (actor ID)

#

No

#

Yes

AgentCore Gateway

#

No

#

Yes

AgentCore Browser

#

No

#

Yes

AgentCore Code Interpreter

#

No

#

Yes

MCP server tools (remote)

#

No

#

Yes

Inline / client-side tools

#

Yes

#

Yes

Context-window truncation

#

No

#

Yes

Custom container image / environment

#

Mixed

#

Mixed

Feature grid

140

Feature / Capability

Harness:
supported
?

Harness:
customer
code
required?

Runtime:
supported
?

Runtime:
customer
code
required?

Execution limits (maxIterations ,

#

No

#

Yes

Filesystem - service-managed session
storage

#

No

#

No

Filesystem - EFS access point

#

No

#

No

Filesystem - S3 Files access point

#

No

#

No

Environment variables

#

No

#

No

Direct shell command execution

#

No

#

No

Inbound auth - IAM (SigV4)

#

No

#

No

Inbound auth - OAuth

#

No

#

No

Outbound auth / Identity token vault
(OAuth and API keys)

#

No

#

Yes

Session isolation

#

No

#

No

VPC networking

#

No

#

No

Streaming responses

#

No

#

Yes

Versioning and endpoints

#

No

#

No

Choice of agent framework

#

N/A

#

Yes

Bidirectional streaming

#

N/A

#

Yes

timeoutSeconds , maxTokens ,
idle/lifetime)

(InvokeAgentRuntimeCommand
API)

Feature grid

141

Feature / Capability

Harness:
supported
?

Harness:
customer
code
required?

Runtime:
supported
?

Runtime:
customer
code
required?

Non-agent-loop patterns (graph,
workﬂow style)

#

N/A

#

Yes

Hooks

#

N/A

#

Yes

Related topics
• the section called “Get started” - create and invoke your ﬁrst harness
• the section called “Models and instructions” - conﬁgure agents, models, and providers
• the section called “Tools” - connect tools to your harness
• the section called “Environment and ﬁlesystem” - bring a custom container image or
environment

Related topics

142


## Runtime protocol comparison (pp. 167–168)

You can let the console create default roles for you, or supply existing roles. Because the
infrastructure role grants AgentCore the ability to manage compute in your account, scope it to
the least privilege your workloads require, and use IAM conditions to restrict it to speciﬁc VPCs,
subnets, or instance types where appropriate.

Understand the AgentCore Runtime service contract
The AgentCore Runtime service contract deﬁnes the standardized communication protocol that
your agent application must implement to integrate with the Amazon Bedrock agent hosting
infrastructure. This contract ensures seamless communication between your custom agent code
and AWS's managed hosting environment.
Topics
• Supported protocols
• Compare supported protocols
• HTTP protocol contract
• MCP protocol contract
• A2A protocol contract
• AG-UI protocol contract

Supported protocols
The AgentCore Runtime service contract supports the following communication protocols:
• HTTP : Direct REST API endpoints for traditional request/response patterns
• MCP : Model Context Protocol for tools and agent servers
• A2A : Agent-to-Agent protocol for multi-agent communication and discovery
• AG-UI : Agent-to-User Interface protocol for interactive agent experiences with UI rendering

Compare supported protocols
Compare the HTTP, MCP, A2A, and AG-UI protocols to understand the diﬀerences and use cases.

Understand the AgentCore Runtime service contract

167

Feature

HTTP Protocol

MCP Protocol

A2A Protocol

AG-UI Protocol

Port

8080

8000

9000

8080

Mount Path

/invocations
(HTTP), /ws
(WebSocket)

/mcp

/ (root)

/invocations
(SSE), /ws
(WebSocket)

Message Format

REST JSON/
SSE, WebSocket
(text/binary)

JSON-RPC

JSON-RPC 2.0

Event streams
(SSE/WebS
ocket)

Discovery

N/A

Tool listing

Agent Cards

N/A

Authentication

SigV4, OAuth
2.0; WebSocket
supports SigV4
by headers and
query params

SigV4, OAuth
2.0

SigV4, OAuth
2.0

SigV4, OAuth
2.0

Use Case

Direct API
calls, real-time
streaming

Tool servers

Agent-to-agent
communication

Interactive UI
experiences

HTTP protocol contract
Understand the requirements for implementing the HTTP protocol in your agent application. Use
the HTTP protocol to create direct REST API endpoints for traditional request/response patterns
and WebSocket endpoints for real-time bidirectional streaming connections.
Note
Both HTTP ( /invocations ) and WebSocket ( /ws ) endpoints can be deployed on the
same container using port 8080, allowing a single agent implementation to support both
traditional API interactions and real-time bidirectional streaming.

For example code, see Get started with the AgentCore CLI.
HTTP protocol contract

168


## A2A protocol contract (pp. 183–189)

OAuth authentication responses
OAuth-conﬁgured agents follow RFC 6749 (OAuth 2.0) authentication standards. When
authentication is missing, the service returns a 401 Unauthorized response with a WWWAuthenticate header (per RFC 7235 ), enabling clients to discover the authorization server
endpoints through the GetRuntimeProtectedResourceMetadata API.
401 Unauthorized
Returned when the Authorization header is missing or empty.
Response includes WWW-Authenticate header:
WWW-Authenticate: Bearer resource_metadata="https://bedrock-agentcore.
{region}.amazonaws.com/runtimes/{ESCAPED_ARN}/invocations/.well-known/oauth-protectedresource?qualifier={QUALIFIER}"

Note
SigV4-conﬁgured agents return HTTP 403 with an ACCESS_DENIED error and do not
include WWW-Authenticate headers.

A2A protocol contract
The A2A protocol contract deﬁnes the requirements for implementing agent-to-agent
communication in Amazon Bedrock AgentCore Runtime. This contract speciﬁes the technical
requirements, endpoints, and communication patterns that your A2A server must implement.
For example code, see Deploy A2A servers in AgentCore Runtime.
Topics
• Protocol implementation requirements
• Container requirements
• Path requirements
• Authentication requirements
• Error handling
A2A protocol contract

183

• OAuth authentication responses

Protocol implementation requirements
Your A2A server must implement these speciﬁc protocol requirements:
• Transport : JSON-RPC 2.0 over HTTP - Enables standardized agent-to-agent communication
• Session Management : Platform automatically adds X-Amzn-Bedrock-AgentCore-RuntimeSession-Id header for session isolation
• Agent Discovery : Must provide Agent Card at /.well-known/agent-card.json endpoint

Container requirements
Your A2A server must be deployed as a containerized application meeting these speciﬁcations:
• Host : 0.0.0.0
• Port : 9000 - Standard port for A2A server communication (diﬀerent from HTTP and MCP
protocols)
• Platform : ARM64 container - Required for compatibility with AWS Amazon Bedrock AgentCore
runtime environment

Path requirements
/ - POST
Purpose
Receives JSON-RPC 2.0 messages and processes them through your agent’s capabilities, complete
pass-through of InvokeAgentRuntime API payload with A2A protocol messages
Use cases
The root endpoint serves several key purposes:
• Agent-to-agent communication and collaboration
• Multi-step agent workﬂows and task delegation
• Real-time conversational experiences between agents
• Tool invocation and capability sharing
A2A protocol contract

184

Request format
A2A servers expect JSON-RPC 2.0 formatted requests:
Content-Type: application/json
{
"jsonrpc": "2.0",
"id": "req-001",
"method": "message/send",
"params": {
"message": {
"role": "user",
"parts": [
{
"kind": "text",
"text": "Your message content here"
}
],
"messageId": "unique-message-id"
}
}
}

Response format
A2A servers respond with JSON-RPC 2.0 formatted responses containing tasks and artifacts:
Content-Type: application/json
{
"jsonrpc": "2.0",
"id": "req-001",
"result": {
"artifacts": [
{
"artifactId": "unique-artifact-id",
"name": "agent_response",
"parts": [
{
"kind": "text",
"text": "Agent response content"
}
]
}
A2A protocol contract

185

]
}
}

/.well-known/agent-card.json - GET
Purpose
Provides Agent Card metadata for agent discovery and capability advertisement
Use cases
The Agent Card endpoint serves several key purposes:
• Agent discovery in multi-agent systems
• Capability and skill advertisement
• Authentication requirement speciﬁcation
• Service endpoint conﬁguration
Response format
Returns JSON metadata describing the agent’s identity and capabilities:
Content-Type: application/json
{
"name": "Agent Name",
"description": "Agent description and purpose",
"version": "1.0.0",
"url": "https://bedrock-agentcore.region.amazonaws.com/runtimes/agent-arn/
invocations/",
"protocolVersion": "0.3.0",
"preferredTransport": "JSONRPC",
"capabilities": {
"streaming": true
},
"defaultInputModes": ["text"],
"defaultOutputModes": ["text"],
"skills": [
{
"id": "skill-id",
"name": "Skill Name",
"description": "Skill description and capabilities",
A2A protocol contract

186

"tags": []
}
]
}

/ping - GET
Purpose
Veriﬁes that your A2A server is operational and ready to handle requests
Response format
Returns a status code indicating your agent’s health:
• Content-Type : application/json
• HTTP Status Code : 200 for healthy, appropriate error codes for unhealthy states

{
"status": "Healthy"
}

status is required and is one of Healthy or HealthyBusy. While the status is HealthyBusy, the
runtime session is kept alive.
An optional time_of_last_update ﬁeld (a Unix timestamp in seconds) may be included to
report when the status last changed.
Warning
Do not set time_of_last_update to the current time on every ping. A timestamp that
advances on every ping signals a continuous status change, which prevents the idle session
timeout from ever ﬁring — sessions then persist until MaxLifetime and can exhaust your
session quota. If you omit the ﬁeld, the platform tracks status changes on its own. If you
use the Bedrock AgentCore SDK, the ping response is handled for you.

Authentication requirements
A2A servers support multiple authentication mechanisms:
A2A protocol contract

187

OAuth 2.0 Bearer Tokens
For A2A client authentication, include the Bearer token in request headers:
Authorization: Bearer <oauth-token>
X-Amzn-Bedrock-AgentCore-Runtime-Session-Id: <session-id>

SigV4 Authentication
Standard AWS SigV4 authentication is also supported for programmatic access.

Error handling
A2A servers return errors as standard JSON-RPC 2.0 error responses. The following table maps
each runtime exception to its JSON-RPC error code, HTTP status code, and message. Some
exceptions share a JSON-RPC error code but return diﬀerent messages, so they are listed as
separate rows.
JSON-RPC Error
Code

Runtime Exception

HTTP Error Code

JSON-RPC Error
Message

Not applicable

AccessDeniedExcept
ion

403

Access denied
(returned as a
standard HTTP error,
not a JSON-RPC
error)

-32051

ResourceNotFoundEx
ception

404

Resource not found Requested resource
does not exist

-32052

ValidationException

400

Validation error Invalid request data

-32053

ThrottlingException

429

Rate limit exceeded Too many requests

-32053

ServiceQuotaExceed
edException

429

Rate limit exceeded Too many requests

A2A protocol contract

188

JSON-RPC Error
Code

Runtime Exception

HTTP Error Code

JSON-RPC Error
Message

-32054

ConﬂictException

409

Resource conﬂict
- Resource already
exists

-32054

RetryableConﬂictE
xception

409

Session operation in
progress, please retry

-32055

RuntimeClientError

424

Runtime client error
- Please check your
CloudWatch logs for
more information

-32603

Any other exception

500

Internal error - An
unexpected error
occurred while
processing the
request

ConflictException and RetryableConflictException both use JSON-RPC
error code -32054 (HTTP 409). Their messages distinguish them. The service returns
RetryableConflictException (Session operation in progress, please retry)
when a second operation targets a session that the service is provisioning or tearing down. This
condition is transient and retryable. The caller must retry with short exponential backoﬀ, because
A2A clients do not auto-retry it.

Note
Unlike the A2A speciﬁcation’s convention of delivering JSON-RPC errors over an HTTP 200
response, AgentCore Runtime returns the real HTTP status code (for example, 409 or 404).
Parse the JSON-RPC error body even on non-2xx responses, so your client does not miss
the error code (such as -32054) or the Session operation in progress, please
retry message it needs to drive a retry.

A2A protocol contract

189


## Deploy A2A servers (pp. 358–369)

Tip
You can also test your MCP server using the MCP Inspector, a visual tool for testing MCP
servers. For local testing instructions, see Local testing with MCP inspector . For remote
testing instructions, see Remote testing with MCP inspector.

Deploy A2A servers in AgentCore Runtime
Amazon Bedrock AgentCore Runtime lets you deploy and run Agent-to-Agent (A2A) servers in the
AgentCore Runtime. This guide walks you through creating, testing, and deploying your ﬁrst A2A
server.
In this section, you learn:
• How Amazon Bedrock AgentCore supports A2A
• How to create an A2A server with agent capabilities
• How to test your server locally
• How to deploy your server to AWS
• How to invoke your deployed server
• How to retrieve agent cards for discovery
For more information about A2A, see A2A protocol contract.
Topics
• How Amazon Bedrock AgentCore supports A2A
• Using A2A with AgentCore Runtime
• Appendix

How Amazon Bedrock AgentCore supports A2A
Amazon Bedrock AgentCore’s A2A protocol support enables seamless integration with A2A servers
by acting as a transparent proxy layer. When conﬁgured for A2A, Amazon Bedrock AgentCore
expects containers to run stateless, streamable HTTP servers on port 9000 at the root path (
0.0.0.0:9000/ ), which aligns with the default A2A server conﬁguration.
Deploy A2A servers

358

The service provides enterprise-grade session isolation while maintaining protocol transparency
- JSON-RPC payloads from the InvokeAgentRuntime API are passed through directly to the A2A
container without modiﬁcation. This architecture preserves the standard A2A protocol features like
built-in agent discovery through Agent Cards at /.well-known/agent-card.json and JSONRPC communication, while adding enterprise authentication (SigV4/OAuth 2.0) and scalability.
The key diﬀerentiators from other protocols are the port (9000 vs 8080 for HTTP), mount path ( /
vs /invocations ), and the standardized agent discovery mechanism, making Amazon Bedrock
AgentCore an ideal deployment platform for A2A agents in production environments.
Key diﬀerences from other protocols:
Port
A2A servers run on port 9000 (vs 8080 for HTTP, 8000 for MCP)
Path
A2A servers are mounted at / (vs /invocations for HTTP, /mcp for MCP)
Agent Cards
A2A provides built-in agent discovery through Agent Cards at /.well-known/agentcard.json
Protocol
Uses JSON-RPC for agent-to-agent communication
Authentication
Supports both SigV4 and OAuth 2.0 authentication schemes
For more information, see https://a2a-protocol.org/.

Using A2A with AgentCore Runtime
In this tutorial you create, test, and deploy an A2A server.
Topics
• Prerequisites
• Step 1: Create your A2A project
Using A2A with AgentCore Runtime

359

• Step 2: Test your A2A server locally
• Step 3: Deploy your A2A server to Bedrock AgentCore Runtime
• Step 4: Get the agent card
• Step 5: Invoke your deployed A2A server

Prerequisites
• Python 3.10 or higher installed and basic understanding of Python
• Node.js 20 or higher installed (required for the AgentCore CLI)
• The AgentCore CLI installed: npm install -g @aws/agentcore
• An AWS account with appropriate permissions and local credentials conﬁgured
• Understanding of the A2A protocol and agent-to-agent communication concepts

Step 1: Create your A2A project
This example uses Strands Agents, but the AgentCore CLI also supports A2A projects with
LangChain/LangGraph and Google ADK.
Scaﬀold the project
Run the following command:
agentcore create \
--project-name A2AProject \
--name A2AAgent \
--language Python \
--framework Strands \
--model-provider Bedrock \
--memory none \
--protocol A2A
cd A2AProject

The CLI scaﬀolds a complete project with all required dependencies and conﬁguration. The
generated main.py contains your A2A server:
from strands import Agent, tool
from strands.multiagent.a2a.executor import StrandsA2AExecutor
from bedrock_agentcore.runtime import serve_a2a
Using A2A with AgentCore Runtime

360

from model.load import load_model
@tool
def add_numbers(a: int, b: int) -> int:
"""Return the sum of two numbers."""
return a + b
tools = [add_numbers]
agent = Agent(
model=load_model(),
system_prompt="You are a helpful assistant. Use tools when appropriate.",
tools=tools,
)
if __name__ == "__main__":
serve_a2a(StrandsA2AExecutor(agent))

Understanding the code
Strands Agent
Creates an agent with speciﬁc tools and capabilities
StrandsA2AExecutor
Wraps the Strands agent to provide A2A protocol compatibility
serve_a2a
The Amazon Bedrock AgentCore SDK helper that starts a Bedrock-compatible A2A server.
It handles the /ping health endpoint, Agent Card serving, AGENTCORE_RUNTIME_URL
environment variable, Bedrock header propagation, and runs on port 9000 by default.
Port 9000
A2A servers run on port 9000 by default in AgentCore Runtime
To customize this agent, replace the add_numbers tool with your own tools and update the
system prompt.

Step 2: Test your A2A server locally
Run and test your A2A server in a local development environment.
Using A2A with AgentCore Runtime

361

Start your A2A server
Start your A2A server locally using the AgentCore CLI:
agentcore dev

This opens the AgentCore agent inspector in your web browser. To use the terminal-based TUI
instead, use agentcore dev --no-browser.
Alternatively, you can run the server directly:
python main.py

You should see output indicating the server is running on port 9000.
Invoke agent
curl -X POST http://localhost:9000/ \
-H "Content-Type: application/json" \
-d '{
"jsonrpc": "2.0",
"id": "req-001",
"method": "message/send",
"params": {
"message": {
"role": "user",
"parts": [
{
"kind": "text",
"text": "what is 101 * 11?"
}
],
"messageId": "12345678-1234-1234-1234-123456789012"
}
}
}' | jq .

Test agent card retrieval
You can test the agent card endpoint locally:
curl http://localhost:9000/.well-known/agent-card.json | jq.

Using A2A with AgentCore Runtime

362

You can also test your deployed server using the A2A Inspector as described in Remote testing with
A2A inspector.

Step 3: Deploy your A2A server to Bedrock AgentCore Runtime
Set up Cognito user pool for authentication
Before deploying, conﬁgure authentication for secure access to your deployed server. For detailed
Cognito setup instructions, see Set up Cognito user pool for authentication . This provides the
OAuth tokens required for secure access to your deployed server.
Deploy to AWS
Deploy your agent:
agentcore deploy

This command will:
1. Package your agent code and dependencies
2. Upload the deployment artifact to Amazon S3
3. Create a Amazon Bedrock AgentCore runtime
4. Deploy your agent to AWS
After deployment, you’ll receive an agent runtime ARN that looks like:
arn:aws:bedrock-agentcore:us-west-2:accountId:runtime/my_a2a_server-xyz123

Step 4: Get the agent card
Agent Cards are JSON metadata documents that describe an A2A server’s identity, capabilities,
skills, service endpoint, and authentication requirements. They enable automatic agent discovery in
the A2A ecosystem.
Set up environment variables
Set up environment variables
Using A2A with AgentCore Runtime

363

1. Export bearer token as an environment variable. For bearer token setup, see Bearer token setup.
export BEARER_TOKEN="<BEARER_TOKEN>"

2. Export the agent ARN.
export AGENT_ARN="arn:aws:bedrock-agentcore:us-west-2:accountId:runtime/
my_a2a_server-xyz123"

Retrieve agent card
import os
import json
import requests
from uuid import uuid4
from urllib.parse import quote
def fetch_agent_card():
# Get environment variables
agent_arn = os.environ.get('AGENT_ARN')
bearer_token = os.environ.get('BEARER_TOKEN')
if not agent_arn:
print("Error: AGENT_ARN environment variable not set")
return
if not bearer_token:
print("Error: BEARER_TOKEN environment variable not set")
return
# URL encode the agent ARN
escaped_agent_arn = quote(agent_arn, safe='')
# Construct the URL
url = f"https://bedrock-agentcore.us-west-2.amazonaws.com/runtimes/
{escaped_agent_arn}/invocations/.well-known/agent-card.json"
# Generate a unique session ID
session_id = str(uuid4())
print(f"Generated session ID: {session_id}")
# Set headers
Using A2A with AgentCore Runtime

364

headers = {
'Accept': '*/*',
'Authorization': f'Bearer {bearer_token}',
'X-Amzn-Bedrock-AgentCore-Runtime-Session-Id': session_id
}
try:
# Make the request
response = requests.get(url, headers=headers)
response.raise_for_status()
# Parse and pretty print JSON
agent_card = response.json()
print(json.dumps(agent_card, indent=2))
return agent_card
except requests.exceptions.RequestException as e:
print(f"Error fetching agent card: {e}")
return None
if __name__ == "__main__":
fetch_agent_card()

After you get the URL from the Agent Card, export AGENTCORE_RUNTIME_URL as an environment
variable:
export AGENTCORE_RUNTIME_URL="https://bedrock-agentcore.us-west-2.amazonaws.com/
runtimes/<ARN>/invocations/"

Step 5: Invoke your deployed A2A server
Create client code to invoke your deployed Amazon Bedrock AgentCore A2A server and send
messages to test the functionality.
Create a new ﬁle my_a2a_client_remote.py to invoke your deployed A2A server:
import asyncio
import logging
import os
from uuid import uuid4
import httpx
Using A2A with AgentCore Runtime

365

from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
from a2a.types import Message, Part, Role, TextPart
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
DEFAULT_TIMEOUT = 300

# set request timeout to 5 minutes

def create_message(*, role: Role = Role.user, text: str) -> Message:
return Message(
kind="message",
role=role,
parts=[Part(TextPart(kind="text", text=text))],
message_id=uuid4().hex,
)
async def send_sync_message(message: str):
# Get runtime URL from environment variable
runtime_url = os.environ.get('AGENTCORE_RUNTIME_URL')
# Generate a unique session ID
session_id = str(uuid4())
print(f"Generated session ID: {session_id}")
# Add authentication headers for Amazon Bedrock AgentCore
headers = {"Authorization": f"Bearer {os.environ.get('BEARER_TOKEN')}",
'X-Amzn-Bedrock-AgentCore-Runtime-Session-Id': session_id}
async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, headers=headers) as
httpx_client:
# Get agent card from the runtime URL
resolver = A2ACardResolver(httpx_client=httpx_client, base_url=runtime_url)
agent_card = await resolver.get_agent_card()
# Agent card contains the correct URL (same as runtime_url in this case)
# No manual override needed - this is the path-based mounting pattern
# Create client using factory
config = ClientConfig(
httpx_client=httpx_client,
streaming=False, # Use non-streaming mode for sync response
)
factory = ClientFactory(config)
client = factory.create(agent_card)

Using A2A with AgentCore Runtime

366

# Create and send message
msg = create_message(text=message)
# With streaming=False, this will yield exactly one result
async for event in client.send_message(msg):
if isinstance(event, Message):
logger.info(event.model_dump_json(exclude_none=True, indent=2))
return event
elif isinstance(event, tuple) and len(event) == 2:
# (Task, UpdateEvent) tuple
task, update_event = event
logger.info(f"Task: {task.model_dump_json(exclude_none=True,
indent=2)}")
if update_event:
logger.info(f"Update:
{update_event.model_dump_json(exclude_none=True, indent=2)}")
return task
else:
# Fallback for other response types
logger.info(f"Response: {str(event)}")
return event
# Usage - Uses AGENTCORE_RUNTIME_URL environment variable
asyncio.run(send_sync_message("what is 101 * 11"))

Appendix
Topics
• Set up Cognito user pool for authentication
• Remote testing with A2A inspector
• Troubleshooting

Set up Cognito user pool for authentication
For detailed Cognito setup instructions, see Set up Cognito user pool for authentication in the MCP
documentation.

Remote testing with A2A inspector
See https://github.com/a2aproject/a2a-inspector.
Appendix

367

Troubleshooting
Common A2A-speciﬁc issues
The following are common issues you might encounter:
Port conﬂicts
A2A servers must run on port 9000 in the AgentCore Runtime environment
JSON-RPC errors
Check that your client is sending properly formatted JSON-RPC 2.0 messages
Authorization method mismatch
Make sure your request uses the same authentication method (OAuth or SigV4) that the agent
was conﬁgured with
Exception handling
A2A speciﬁcations for Error handling: https://a2a-protocol.org/latest/speciﬁcation/#81-standardjson-rpc-errors
A2A servers return most errors as standard JSON-RPC error responses. The service returns
authentication and authorization failures (for example, AccessDeniedException) as native
HTTP errors with their own status codes, as shown in the following table. The service automatically
translates internal runtime errors to JSON-RPC internal errors to maintain protocol compliance.
The service provides A2A-compliant error responses with standardized JSON-RPC error codes:

JSON-RPC Error
Code

Runtime Exception

HTTP Error Code

JSON-RPC Error
Message

Not applicable

AccessDen

403

Access denied
(returned as a
standard HTTP error,
not a JSON-RPC
error)

iedException

Appendix

368

JSON-RPC Error
Code

Runtime Exception

HTTP Error Code

JSON-RPC Error
Message

-32051

ResourceN

404

Resource not found –
Requested resource
does not exist

400

Validation error –
Invalid request data

429

Rate limit exceeded –
Too many requests

429

Rate limit exceeded –
Too many requests

409

Resource conﬂict
– Resource already
exists

409

Session operation in
progress, please retry

424

Runtime client
error – Check your
CloudWatch logs for
more information.

500

Internal error - An
unexpected error
occurred while
processing the
request

otFoundEx
ception
-32052

Validatio
nException

-32053

Throttlin
gException

-32053

ServiceQu
otaExceed
edException

-32054

ConflictE
xception

-32054

Retryable
ConflictE
xception

-32055

RuntimeCl
ientError

-32603

Any other
exception

Appendix

369


## Isolated sessions and session lifecycle (pp. 380–384)

Event format errors
Ensure your events follow the AG-UI protocol speciﬁcation. See AG-UI Events Documentation

Use isolated sessions for agents
Amazon Bedrock AgentCore Runtime lets you isolate each user session and safely reuse context
across multiple invocations in a user session. Session isolation is critical for AI agent workloads due
to their unique operational characteristics:
• Complete execution environment separation : Each user session in AgentCore Runtime receives
its own dedicated microVM with isolated Compute, memory, and ﬁlesystem resources. This
prevents one user’s agent from accessing another user’s data. After session completion, the
entire microVM is terminated and memory is sanitized to remove all session data, eliminating
cross-session contamination risks.
• Stateful reasoning processes : Unlike stateless functions, AI agents maintain complex
contextual state throughout their execution cycle, beyond simple message history for multi-turn
conversations. AgentCore Runtime preserves this state securely within a session while ensuring
complete isolation between diﬀerent users, enabling personalized agent experiences without
compromising data boundaries.
• Privileged tool operations : AI agents perform privileged operations on users' behalf through
integrated tools accessing various resources. AgentCore Runtime’s isolation model ensures these
tool operations maintain proper security contexts and prevents credential sharing or permission
escalation between diﬀerent user sessions.
• Deterministic security for non-deterministic processes : AI agent behavior can be nondeterministic due to the probabilistic nature of foundation models. AgentCore Runtime provides
consistent, deterministic isolation boundaries regardless of agent execution patterns, delivering
the predictable security properties required for enterprise deployments.

Note
AgentCore does not enforce session-to-user mappings - your client backend should
maintain the relationship between users and their session IDs. Additionally, your client
backend should implement logic for user to session lifecycle management like maximum

Use isolated sessions for agents

380

number of sessions per user. For complete session isolation guidance, see Security best
practices for AgentCore Runtime.

Topics
• Understanding ephemeral context
• Extended conversations and multi-step workﬂows
• AgentCore Runtime session lifecycle
• How to use sessions
• Session headers by protocol
• Conﬁgure Amazon Bedrock AgentCore lifecycle settings
• Stop a running session

Understanding ephemeral context
By default, the compute (microVM) associated with a session is ephemeral. Any data stored in
memory or written to disk persists only for the compute lifecycle. This includes conversation
history, user preferences, intermediate calculation results, and any other state information your
agent maintains.
To persist ﬁlesystem data across session stop/resume cycles, conﬁgure session storage — a
persistent directory that survives compute termination. See File system conﬁgurations for
AgentCore Runtime.
For structured data that needs to be retained beyond the session lifetime (such as user
conversation history, learned preferences, or important insights), use AgentCore Memory. This
service provides purpose-built persistent storage designed speciﬁcally for agent workloads, with
both short-term and long-term memory capabilities.

Extended conversations and multi-step workﬂows
Unlike traditional serverless functions that terminate after each request, AgentCore supports
isolated sessions backed by ephemeral computes. Sessions last up to 8 hours for each lifecycle on
microVMs, or up to 14 days on Instances. With these sessions, you can build multi-step agentic
workﬂows, making multiple calls to the same environment with each invocation building upon the
Understanding ephemeral context

381

context of previous interactions. You can use both InvokeAgentRuntime for agent reasoning
and InvokeAgentRuntimeCommand for deterministic shell command execution within the same
session.

AgentCore Runtime session lifecycle
Session creation
A new session is created on the ﬁrst invoke with a unique runtimeSessionId provided by your
application. AgentCore Runtime provisions a dedicated execution environment (microVM)
for each session. Context is preserved between invocations to the same session. Both
InvokeAgentRuntime and InvokeAgentRuntimeCommand operate on the same session — a
command sees the same container, ﬁlesystem, and environment as the agent.
Session states
Session state is determined by the compute lifecycle and can be one of the following:
• Active : Either processing a sync request, executing a command, or doing background tasks. Sync
invocation and command execution activity is automatically tracked based on invocations to
a runtime session. Background tasks are communicated by the agent code by responding with
"HealthyBusy" status in pings.
• Idle : When not processing any requests or background tasks. The session has completed
processing but remains available for future invocations.
• Stopped : The compute (microVM) provisioned for the session has been terminated and the
session is stopped. This can occur due to inactivity (default 15 minutes), reaching max compute
lifetime (default 8 hours), an explicit stop by invoking the StopRuntimeSession API, or if the
compute is deemed unhealthy based on health checks. The session transitions back to Active on
the next invocation and a new compute is provisioned, with the same lifecycle conﬁguration (i.e.
idleRuntimeSessionTimeout and maxLifetime that can be up to another 8 hours). The session
itself remains valid until the AgentCore Runtime ARN is deleted. If the runtime is conﬁgured with
session storage, ﬁlesystem data at the conﬁgured mount path persists across stop/resume cycles.
See File system conﬁgurations for AgentCore Runtime.

Note
While the service provisions or tears down a session, a second operation targeting that
same session returns a retryable HTTP 409 RetryableConflictException (Session
AgentCore Runtime session lifecycle

382

operation in progress, please retry). This window is brief. Already-running
sessions are not aﬀected. Retry with short exponential backoﬀ.

How to use sessions
To use sessions eﬀectively:
• Generate a unique session ID for each user or conversation with at least 33 characters
• Pass the same session ID for all related invocations
• Use diﬀerent session IDs for diﬀerent users or conversations
Example Using sessions for a conversation
# First message in a conversation
response1 = agent_core_client.InvokeAgentRuntime(
agentRuntimeArn=agent_arn,
runtimeSessionId="user-123456-conversation-12345678", # or uuid.uuid4()
payload=json.dumps({"prompt": "Tell me about AWS"}).encode()
)
# Follow-up message in the same conversation reuses the runtimeSessionId.
response2 = agent_core_client.InvokeAgentRuntime(
agentRuntimeArn=agent_arn,
runtimeSessionId="user-123456-conversation-12345678", # or uuid.uuid4()
payload=json.dumps({"prompt": "How does it compare to other cloud
providers"}).encode()
)

By using the same runtimeSessionId for related invocations, you ensure that context is maintained
across the conversation, allowing your agent to provide coherent responses that build on previous
interactions.

Session headers by protocol
When invoking agents, include the appropriate session header to ensure requests are routed to the
same microVM. The header depends on your agent’s conﬁgured protocol:
How to use sessions

383

Protocol

Session Header

MCP

Mcp-Session-Id

HTTP

X-Amzn-Bedrock-AgentCore-Ru
ntime-Session-Id

A2A

X-Amzn-Bedrock-AgentCore-Ru
ntime-Session-Id

AG-UI

X-Amzn-Bedrock-AgentCore-Ru
ntime-Session-Id

MicroVM stickiness : Amazon Bedrock AgentCore uses the session header to route requests to the
same microVM instance. Clients must capture the session ID returned in the response and include it
in all subsequent requests to ensure session aﬃnity. Without a consistent session ID, each request
may be routed to a new microVM, which may result in additional latency due to cold starts.
For MCP protocol speciﬁcs including stateless and stateful modes, see MCP session management
and microVM stickiness.

Conﬁgure Amazon Bedrock AgentCore lifecycle settings
The LifecycleConfiguration input parameter to CreateAgentRuntime lets you manage
the lifecycle of runtime sessions and resources in Amazon Bedrock AgentCore Runtime. This
conﬁguration helps optimize resource utilization by automatically cleaning up idle sessions and
preventing long-running instances from consuming resources indeﬁnitely.
You can also conﬁgure lifecycle settings for an existing AgentCore Runtime with the
UpdateAgentRuntime operation.
Topics
• Conﬁguration attributes
• Default behavior
• Create an AgentCore Runtime with lifecycle conﬁguration
• Update the lifecycle conﬁguration for an AgentCore Runtime
• Get the lifecycle conﬁguration for an AgentCore Runtime
Conﬁgure lifecycle settings

384


## Asynchronous and long-running agents (pp. 426–430)

Symptom

Likely cause

Quick ﬁx

Mount hangs then
fails (~30s)

Security group
blocking port 2049
or no mount target
in agent’s Availability
Zone

Allow TCP 2049; verify Availability Zone
overlap

"Permission denied"
on writes

Missing ClientWri

Add write permission or align access point
POSIX user

te or POSIX UID/
GID mismatch

Each mount has a 30-second timeout. All conﬁgured ﬁle systems mount in parallel – a single failure
causes the entire invocation to fail.
For more information, see Troubleshoot BYO storage.

Handle asynchronous and long running agents with Amazon
Bedrock AgentCore Runtime
Amazon Bedrock AgentCore Runtime can handle asynchronous processing and long running
agents. Asynchronous tasks allow your agent to continue processing after responding to the client
and handle long-running operations without blocking responses. With async processing, your agent
can:
• Start a task that might take minutes or hours
• Immediately respond to the user saying "I’ve started working on this"
• Continue processing in the background
• Allow the user to check back later for results

Key concepts
Asynchronous processing model
The Amazon Bedrock AgentCore SDK supports both synchronous and asynchronous processing
through a uniﬁed API. This creates a ﬂexible implementation pattern for both clients and
Handle asynchronous and long running agents

426

agent developers. Agent clients can work with the same API without diﬀerentiating between
synchronous and asynchronous on the client side. With the ability to invoke the same session
across invocations, agent developers can reuse context and build upon this context incrementally
without implementing complex task management logic.

Runtime session lifecycle management
Agent code communicates its processing status using the "/ping" endpoint health status. The /
ping endpoint must return an HTTP 200 response with the following JSON payload:
{"status": "HealthyBusy"}

The response contains a required ﬁeld and an optional ﬁeld:
• status (required) — either "Healthy" (idle, waiting for requests) or "HealthyBusy"
(processing background tasks). The platform uses this ﬁeld to determine whether the session is
still active.
• time_of_last_update (optional) — Unix timestamp in seconds of when the status last
changed. Set it only on an actual status change, not on every ping.
A session in idle state ("Healthy") for 15 minutes gets automatically terminated. A session
returning "HealthyBusy" remains alive beyond the idle timeout.
Warning
If you include time_of_last_update, do not set it to the current time on every ping. A
timestamp that advances on every ping signals a continuous status change, which prevents
the idle session timeout from ever ﬁring — sessions then persist until MaxLifetime and
can exhaust your session quota. Omit the ﬁeld (the platform tracks status changes on its
own) or update it only when the status actually changes. If you use the Bedrock AgentCore
SDK, this is handled for you.

Implementing asynchronous tasks
To get started, install the bedrock-agentcore package:
pip install bedrock-agentcore

Implementing asynchronous tasks

427

AgentCore SDK provides following options for integration asynchronous processing.
Example
API based task management
1. To build interactive agents that perform asynchronous tasks, you need to call
add_async_task when starting a task and complete_async_task when the task
completes. The SDK handles task tracking and manages Ping status automatically.
# Start tracking a task manually
task_id = app.add_async_task("data_processing")
# Do work...
# Mark task as complete
app.complete_async_task(task_id)

Custom ping handler
1. You can implement your own custom ping handler to manage the Runtime Session’s state.
Your agent’s health is reported through the /ping endpoint:
@app.ping
def custom_status():
if system_busy():
return PingStatus.HEALTHY_BUSY
return PingStatus.HEALTHY

Status values:
• "Healthy": Ready for new work
• "HealthyBusy": Processing background task

Important
Ensure @app.entrypoint handler does not perform blocking operations, as this might
also block the /ping health check endpoint. Use separate threads or async methods for
blocking operations.

Implementing asynchronous tasks

428

Complete example
First, install the required package:
pip install strands-agents

Then, create a Python ﬁle with the following code:
import threading
import time
from strands import Agent, tool
from bedrock_agentcore.runtime import BedrockAgentCoreApp
# Initialize app with debug mode for task management
app = BedrockAgentCoreApp()
@tool
def start_background_task(duration: int = 5) -> str:
"""Start a simple background task that runs for specified duration."""
# Start tracking the async task
task_id = app.add_async_task("background_processing", {"duration": duration})
# Run task in background thread
def background_work():
time.sleep(duration) # Simulate work
app.complete_async_task(task_id) # Mark as complete
threading.Thread(target=background_work, daemon=True).start()
return f"Started background task (ID: {task_id}) for {duration} seconds. Agent
status is now BUSY."
# Create agent with the tool
agent = Agent(tools=[start_background_task])
@app.entrypoint
def main(payload):
"""Main entrypoint - handles user messages."""
user_message = str(payload.get("prompt", "Try: start_background_task(3)"))
return {"message": agent(user_message).message}
if __name__ == "__main__":
print("# Simple Async Strands Example")
Complete example

429

print("Test: curl -X POST http://localhost:8080/invocations -H 'Content-Type:
application/json' -d '{\"prompt\": \"start a 3 second task\"}'")
app.run()

This example demonstrates:
• Creating a background task that runs asynchronously
• Tracking the task’s status with add_async_task and complete_async_task
• Responding immediately to the user while processing continues
• Managing the agent’s health status automatically

Common issues and solutions
Long-running agent gets terminated after 15 minutes
This can happen when the application is single threaded and the ping thread is blocked.
• Check that blocking calls in the invocation path are in a separate thread or async non-blocking
• Run async agent server locally and simulate scenarios while checking for ping status.

Stream agent responses
The following Strands Agents example shows how an AgentCore Runtime agent can stream a
response back to a client.
from strands import Agent
from bedrock_agentcore import BedrockAgentCoreApp
app = BedrockAgentCoreApp()
agent = Agent()
@app.entrypoint
async def agent_invocation(payload):
"""Handler for agent invocation"""
user_message = payload.get("prompt", "")
if not isinstance(user_message, str) or not user_message.strip():
yield {"error": "Invalid input: 'prompt' must be a non-empty string"}
return
stream = agent.stream_async(user_message)
Common issues and solutions

430


## Inbound and outbound auth (pp. 443–447)

--language Python \
--framework Strands \
--model-provider Bedrock \
--memory none \
--authorizer-type CUSTOM_JWT \
--discovery-url "https://cognito-idp.us-east-1.amazonaws.com/user-pool-id/.wellknown/openid-configuration" \
--allowed-audience "your-client-id" \
--allowed-clients "your-client-id" \
--request-header-allowlist Authorization

Deploy to apply the conﬁguration:
agentcore deploy

With this conﬁguration, the Authorization header from incoming requests is validated
against your OIDC provider and forwarded to your agent code.
AWS SDK
1. For information about setting up an agent with OAuth inbound access using the AWS SDK,
see Authenticate and authorize with Inbound Auth and Outbound Auth.

Authenticate and authorize with Inbound Auth and Outbound
Auth
This section shows you how to implement authentication and authorization for your agent runtime
using OAuth and JWT bearer tokens with AgentCore Identity . You’ll learn how to set up Cognito
user pools, conﬁgure your agent runtime for JWT authentication (Inbound Auth), and implement
OAuth-based access to third-party resources (outbound Auth).
For a complete example, see https://github.com/awslabs/amazon-bedrock-agentcore-samples/.
For information about using OAuth with an MCP server, see Deploy MCP servers in AgentCore
Runtime.
Amazon Bedrock AgentCore runtime provides two authentication mechanisms for hosted agents:

Authenticate and authorize with Inbound Auth and Outbound Auth

443

IAM SigV4 Authentication
The default authentication and authorization mechanism that works automatically without
additional conﬁguration, similar to other AWS APIs.
X-Amzn-Bedrock-AgentCore-Runtime-User-Id Header
If your solution requires the hosted agent to retrieve OAuth tokens on behalf of end users
(using Authorization Code Grant), you can specify the user identiﬁer by including the X-AmznBedrock-AgentCore-Runtime-User-Id header in your requests. This header uses the
GetWorkloadAccessTokenForUserId path internally.

Note
Invoking InvokeAgentRuntime with the X-Amzn-Bedrock-AgentCoreRuntime-User-Id header will require a new IAM action: bedrockagentcore:InvokeAgentRuntimeForUser , in addition to the existing bedrockagentcore:InvokeAgentRuntime action.

When to use this header versus JWT Bearer Token authentication
This header is designed for the following use cases:
• Enterprise customers with customer-managed user identiﬁers — Organizations that
maintain their own user identity strings and need to pass them through to AgentCore Identity
for credential binding.
• Development and quickstart scenarios — Builders who don’t yet have an IdP token available
and need a fast path to test user-scoped credential ﬂows.
For production deployments where you have an identity provider conﬁgured, use JWT Bearer
Token authentication instead. The JWT path (GetWorkloadAccessTokenForJWT) validates
the token’s issuer, signature, and expiry, providing cryptographic proof of the user’s identity.
The X-Amzn-Bedrock-AgentCore-Runtime-User-Id header path does not verify the
userId against an authenticated end-user identity — it relies on the calling workload to pass
the correct value and on your IAM policies to restrict who can supply it.
Security Best Practices for X-Amzn-Bedrock-AgentCore-Runtime-User-Id Header
Authenticate and authorize with Inbound Auth and Outbound Auth

444

Tip
For a consolidated view of all Runtime security recommendations, see Security best
practices for AgentCore Runtime.

Because AgentCore treats the header value as an opaque identiﬁer without verifying it
against an authenticated identity, you must apply the following controls to maintain the
security boundary:
• Restrict the IAM permission — Only trusted principals should have the bedrockagentcore:InvokeAgentRuntimeForUser permission. Scope this permission to speciﬁc
runtime resources using IAM resource conditions. Do not grant it broadly via managed policies
or wildcard resource statements.
• Derive user-id from the authenticated principal — The user-id value should be derived from
the authenticated principal’s context (for example, IAM caller identity or user token claims)
rather than accepting arbitrary client-supplied values. This prevents an authenticated user
from impersonating another user by manually specifying a diﬀerent user-id .
• Implement audit logging — Log the relationship between the authenticated IAM principal
(from SigV4 context) and the user-id value being passed. Use AWS CloudTrail to monitor
InvokeAgentRuntime calls that include the runtimeUserId parameter.
• Deny the header in untrusted contexts — For runtimes where user-id delegation is not
needed, explicitly deny the bedrock-agentcore:InvokeAgentRuntimeForUser action in
IAM policies to prevent the header from being accepted:
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

Authenticate and authorize with Inbound Auth and Outbound Auth

445

JWT Bearer Token Authentication
You can conﬁgure your agent runtime to accept JWT bearer tokens by providing authorizer
conﬁguration during agent creation.
This conﬁguration includes:
• Discovery URL - A string that must match the pattern ^.+/\.well-known/openidconfiguration$ for OpenID Connect discovery URLs
• Allowed audiences - A list of permitted audiences that will be validated against the aud claim
in the JWT token
• Allowed clients - A list of permitted client identiﬁers that will be validated against the
client_id claim in the JWT token
• Allowed scopes - A list of permitted scopes that will be validated against the scope claim in
the JWT token. The allowedScopes authorization ﬁeld will be conﬁgured as a list of strings.
• Required custom claims - A list of required claims that will be validated against the claim
name and value contained in the incoming JWT token. For details on conﬁguring the
authorizer, see Conﬁgure inbound JWT authorizer

Note
An AgentCore Runtime can support either IAM SigV4 or JWT Bearer Token based inbound
auth, but not both simultaneously. You can always create diﬀerent versions of your
AgentCore Runtime and conﬁgure them for diﬀerent inbound authorization types. When
you create a runtime with Amazon Bedrock AgentCore, a Workload Identity is created
automatically for your runtime with AgentCore Identity service.

Topics
• Restrict IAM (SigV4) inbound invocation to your gateway
• JWT inbound authorization and OAuth outbound access sample
• Prerequisites
• Step 1: Create your agent project
• Step 2: Set up AWS Cognito user pool and add a user
• Step 3 (Optional): Front your runtime with an AgentCore Gateway
• Step 4: Deploy your agent
Authenticate and authorize with Inbound Auth and Outbound Auth

446

• Step 5: Use bearer token to invoke your agent
• OAuth Error Responses
• Step 6: Set up your agent to access tools using OAuth
• Step 7: (Optional) Propagate a JWT token to AgentCore Runtime
• Troubleshooting

Restrict IAM (SigV4) inbound invocation to your gateway
You can front your AgentCore Runtime with an AgentCore Gateway so that the gateway becomes
the single, governed entry point to the runtime — giving you policy-based authorization, Amazon
Bedrock Guardrails, request and response interceptors, and uniﬁed observability, all applied
outside the agent’s own environment. For the full rationale and how to set this up, see Front your
runtime with an AgentCore Gateway.
But this is only useful if callers can’t reach the runtime directly bypassing the gateway. If your
runtime uses the default IAM (SigV4) inbound authorization, you can restrict invocation to the
gateway so that traﬃc reaches the runtime only through it. To achieve this, attach a resourcebased policy to the runtime that restricts invocation to your gateway’s execution role. The gateway
assumes its service role to sign requests to the runtime, so the gateway role is the principal that
invokes the runtime. Allow that role, and add an explicit Deny for every other principal so that
no other identity can invoke the runtime even with a permissive identity-based policy. For more
information about resource-based policies on runtimes, see Resource-based policies for Amazon
Bedrock AgentCore.
{
"Version": "2012-10-17",
"Statement": [
{
"Sid": "AllowOnlyGatewayRole",
"Effect": "Allow",
"Principal": { "AWS": "arn:aws:iam::111122223333:role/
MyGatewayExecutionRole" },
"Action": "bedrock-agentcore:InvokeAgentRuntime",
"Resource": "arn:aws:bedrock-agentcore:us-west-2:111122223333:runtime/
RUNTIME_ID"
},
{
"Sid": "DenyOtherPrincipals",
Restrict IAM (SigV4) inbound invocation to your gateway

447


## AgentCore Memory: overview, terminology, types, strategies intro (pp. 531–540)

Add memory to your Amazon Bedrock AgentCore agent
AgentCore Memory is a fully managed service that gives your AI agents the ability to remember
past interactions, enabling them to provide more intelligent, context-aware, and personalized
conversations. It provides a simple and powerful way to handle both short-term context and longterm knowledge retention without the need to build or manage complex infrastructure.
AgentCore Memory addresses a fundamental challenge in agentic AI: statelessness. Without
memory capabilities, AI agents treat each interaction as a new instance with no knowledge of
previous conversations. AgentCore Memory provides this critical capability, allowing your agent to
build a coherent understanding of users over time.

AgentCore Memory supports a variety of SDKs and agent frameworks. For examples, see Amazon
Bedrock AgentCore Memory examples.
Topics
• Memory types
• Memory key beneﬁts
• Common use cases of memory
• How it works
• Get started with AgentCore Memory
• Create an AgentCore Memory
• Use short-term memory
531

• Use long-term memory
• Amazon Bedrock AgentCore Memory examples
• Amazon Bedrock capacity for built-in with overrides strategies
• Observability
• Best practices
• Advanced features and topics for Amazon Bedrock AgentCore Memory

Memory types
AgentCore Memory oﬀers two types of memory that work together to create intelligent, contextaware AI agents:
Short-term memory
Short-term memory captures turn-by-turn interactions within a single session. This lets agents
maintain immediate context without requiring users to repeat information.
Example: When a user asks, "What’s the weather like in Seattle?" and follows up with "What
about tomorrow?", the agent relies on recent conversation history to understand that
"tomorrow" refers to the weather in Seattle.
Long-term memory
Long-term memory automatically extracts and stores key insights from conversations across
multiple sessions, including user preferences, important facts, and session summaries — for
persistent knowledge retention across multiple sessions.
Example: If a customer mentions they prefer window seats during ﬂight booking, the agent
stores this preference in long-term memory. In future interactions, the agent can proactively
oﬀer window seats, creating a personalized experience.

Memory key beneﬁts
• Create more natural conversations: By remembering previous turns in a conversation, agents
can understand context, resolve ambiguous statements, and interact in a way that feels more
human.
Memory types

532

• Deliver personalized experiences: Retain user preferences, historical data, and key facts across
sessions to tailor responses and actions to individual users.
• Reduce development complexity: Oﬄoad the undiﬀerentiated heavy lifting of managing
conversational state and memory, allowing you to focus on building your agent’s core business
logic.

Common use cases of memory
• Conversational agents: A customer support chatbot remembers a user’s previous issues and
preferences, enabling it to provide more relevant assistance in future interactions.
• Task-oriented / workﬂow agents: An AI agent orchestrating a multi-step business process,
such as invoice approval, uses memory to track the status of each step and maintain workﬂow
progress.
• Multi-agent systems: A team of AI agents managing a supply chain shares memory to
synchronize inventory levels, anticipate demand, and optimize logistics.
• Autonomous or planning agents: An autonomous vehicle uses memory to plan routes, adjust to
traﬃc conditions, and learn from past experiences to improve future driving decisions.

How it works
AgentCore Memory provides a set of APIs that let your AI agents seamlessly store, retrieve, and
utilize both short-term and long-term memory. The architecture is designed to separate the
immediate context of a conversation from the persistent knowledge that should be retained over
time.
Topics
• Memory terminology
• Memory types
• Memory strategies
• Memory organization in AgentCore Memory
• Memory record streaming
• Cross-account memory access
• Compare long-term memory with Retrieval-Augmented Generation
Common use cases of memory

533

Memory terminology
AgentCore Memory
The primary, top-level container for your agent’s memory resource. Each AgentCore Memory
holds all the events and extracted insights for agents or applications.
Memory strategy
Memory strategies are conﬁgurable rules that determine how to process information from
short-term memory into long-term memory. They determine what type of information is kept,
turning raw conversations into structured and useful knowledge.
Namespace
A namespace is a structured path used to logically group and organize long-term memories. By
deﬁning a namespace in your memory strategy, you maintain that all extracted memories are
organized under predictable paths, which aids in retrieval, ﬁltering, and access control.
Memory record
A memory record is a structured unit of information within the memory resource. Each record
is associated with a unique identiﬁer and is stored within a speciﬁed namespace, allowing for
organized retrieval and management.
Session
Represents a single, continuous interaction between a user and the agent, such as a customer
support conversation. A unique sessionId is used to group all events within that conversation.
Actor
Represents the entity interacting with the agent. This can be a human user, another agent, or a
system (software or hardware component) that initiates interactions with the agent. A unique
actorId maintains that memory records are correctly associated with the individual or system.
Event
Event is the fundamental unit of short-term memory. It represents a discrete interaction
or activity within a session, associated with a speciﬁc actor. Events are stored using the
CreateEvent operation and are organized by actorId and sessionId . Each event is
immutable and timestamped, capturing real-time data such as user messages, system actions,
or tool invocations.
Memory terminology

534

Event metadata
Event metadata refers to the supplementary information that provides context about an event
in an AgentCore Memory. While not always explicitly required, metadata can enhance the
organization and retrieval of events.

Memory types
AgentCore Memory oﬀers two types of memory that work together to create intelligent, contextaware AI agents:
Topics
• Short-term memory
• Long-term memory

Short-term memory
Short-term memory stores raw interactions that help the agent maintain context within a single
session. For example, in a shopping website’s customer support AI agent , short-term memory
captures the entire conversation history as a series of events. Each customer question and agent
response is saved as a separate event (or in batches, depending on your implementation). This lets
the agent reload the entire conversation as it happened, maintaining context even if the service
restarts or the customer returns later to continue the same interaction seamlessly.
When a customer interacts with your agent, each interaction can be captured as an event using
the CreateEvent operation. Events can contain various types of data, including conversational
exchanges (questions, answers, instructions) or structured information (product details, order
status). Each event is associated with a session via a session identiﬁer ( sessionId ), which you
can deﬁne or let the system generate by default. You can use the sessionId parameter in future
requests to maintain conversation context.
To load previous sessions/conversations or enrich context, your agent needs to access the
raw interactions with the customer. Imagine a customer returns to follow up on their product
support case from last week. To provide seamless assistance, the agent uses ListSessions to locate
their previous support interactions. Through ListEvents , it retrieves the conversation history,
understanding the reported issue, troubleshooting steps attempted, and any temporary solutions
discussed. The agent uses GetEvent to access speciﬁc information from key moments in past
conversations. These operations work together to maintain support continuity across sessions,
Memory types

535

eliminating the need for customers to re-explain their issue or repeat troubleshooting steps already
attempted.
Event metadata
Event metadata lets you attach additional context information to your short-term memory events
as key-value pairs. When creating events using the CreateEvent operation, you can include
metadata that isn’t part of the core event content but provides valuable context for retrieval.
For example, a travel booking agent can attach location metadata to events, making it easy to
ﬁnd all conversations that mentioned speciﬁc destinations. You can then use the ListEvents
operation with metadata ﬁlters to eﬃciently retrieve events based on these attached properties,
enabling your agent to quickly locate relevant conversation history without scanning through
entire sessions. This capability is useful for agents that need to track and retrieve speciﬁc attributes
across conversations, such as product categories in e-commerce, case types in customer support, or
project identiﬁers in task management applications. Event metadata is not meant to store sensitive
content, as it is not encrypted with customer managed key.

Long-term memory
Long-term memory records store structured information extracted from raw agent interactions,
which is retained across multiple sessions. Long-term memory preserves only the key insights
such as summaries of the conversations, facts and knowledge, or user preferences. For example,
if a customer tells the agent their preferred shoe brand during a conversation, the AI agent stores
this as a long-term memory. Later, even in a diﬀerent conversation, the agent can remember and
suggest the shoe brand, making the interaction personalized and relevant.
Long-term memory generation is an asynchronous process that runs in the background and
automatically extracts insights after raw conversation/context is stored in short-term memory
via CreateEvent, or submitted directly through IngestData. This eﬃciently consolidates key
information without interrupting live interactions. As part of the long-term memory generation,
AgentCore Memory performs the following operations:
• Extraction : Extracts information from raw interactions with the agent
• Consolidation : Consolidates newly extracted information with existing information in the
AgentCore Memory.
Once long-term memory records are generated, you can retrieve these extracted memories to
enhance your agent’s responses. Extracted memories are stored as memory records and can
Memory types

536

be accessed using the GetMemoryRecord , ListMemoryRecords , or RetrieveMemoryRecords
operations. The RetrieveMemoryRecords operation is powerful as it performs a semantic search
to ﬁnd memory records that are most relevant to the query. For example, when a customer asks
about running shoes, the agent can use semantic search to retrieve related memory records, such
as customer’s preferred shoe size, favorite shoe brands, and previous shoe purchases. This lets the
AI support agent provide highly personalized recommendations without requiring the customer to
repeat information they’ve shared before.

Memory strategies
In AgentCore Memory, you can add memory strategies to your memory resource. These
strategies determine what types of information to extract from raw conversations. Strategies
are conﬁgurations that intelligently capture and persist key concepts from interactions, sent as
events in the CreateEvent operation. You can add strategies to the memory resource as part of
CreateMemory or UpdateMemory operations. Once enabled, these strategies are automatically
executed on raw conversation events associated with that memory resource to extract long-term
memories.
If no strategies are speciﬁed, long-term memory records will not be extracted for that memory.
AgentCore Memory supports a variety of memory strategies:
Topics
• Built-in strategies
• Built-in overrides
• Self-managed strategies
• Built-in strategies
• Customize a built-in strategy or create your own strategy
• Self-managed strategy

Built-in strategies
AgentCore handles all memory extraction and consolidation automatically with predeﬁned
algorithms.
• AgentCore handles all memory extraction and consolidation automatically
• No conﬁguration required beyond basic trigger settings
Memory strategies

537

• Uses predeﬁned algorithms optimized and benchmarked for common use cases
• Suitable for standard conversational AI applications
• Limited customization options
• Higher cost for storage

Built-in overrides
Extends built-in strategies with targeted customization while using an AgentCore managed
extraction pipeline.
• Extends built-in strategies with targeted customization
• Allows modiﬁcation of prompts while still using AgentCore managed extraction pipeline
• Provides support for bedrock models (invoked in your account)
• Lower cost for storage than built-ins

Self-managed strategies
You have complete ownership of memory processing pipeline with custom extraction and
consolidation algorithms.
• Complete ownership of memory processing pipeline
• Custom extraction and consolidation algorithms using any model, prompts, etc.
• Full control over memory record schemas, namespaces etc.
• Integration with external systems and databases
• Requires infrastructure setup and maintenance
• Lower cost for storage than built-in strategies
A single memory resource can be conﬁgured to utilize both built-in and custom strategies
simultaneously, providing ﬂexibility to address diverse memory requirements.

Built-in strategies
AgentCore Memory provides built-in strategies to create memories. Each built-in strategy consists
of steps to handle memory creation, including the following (diﬀerent strategies employ diﬀerent
steps):
Memory strategies

538

• Extraction – Identiﬁes useful insights from short-term memory to place into long-term memory
as memory records.
• Consolidation – Determines whether to write useful information to a new record or an existing
record.
• Reﬂection – Insights are generated across episodes.
Each step is deﬁned by a system prompt, which is a combination of the following:
• Instructions – Guide the LLM’s behavior. Can include step-by-step processing guidelines (how the
model should reason and extract or consolidate information).
• Output schema – How the model should present the result.
Each memory strategy provides a structured output format tailored to its purpose. The output is
not uniform across strategies, because the type of information being stored and retrieved diﬀers.
This maintains that each memory type exposes only the ﬁelds most relevant to its strategy. You
can ﬁnd the output formats in the system prompts for each strategy.
You can combine multiple strategies when creating memories.
Topics
• Semantic memory strategy
• User preference memory strategy
• Summary strategy
• Episodic memory strategy
Semantic memory strategy
The semantic memory strategy is designed to identify and extract key pieces of factual information
and contextual knowledge from conversational data. This lets your agent to build a persistent
knowledge base about the entities, events, and key details discussed during an interaction.
Steps in the strategy
The semantic memory strategy includes the following steps:
• Extraction – Identiﬁes useful insights from short-term memory to place into long-term memory
as memory records.
Memory strategies

539

• Consolidation – Determines whether to write useful information to a new record or an existing
record.

Note
The semantic strategy processes only USER and ASSISTANT role messages during
extraction. For more information about roles in agent conversations, see Conversational.

Strategy output
The semantic memory strategy returns facts as JSON objects, each representing a standalone
personal fact about the user.
Example of facts captured by this strategy
• An order number ( #XYZ-123 ) is associated with a speciﬁc support case.
• A project’s deadline of October 25th.
• The user is running version 2.1 of the software.
By referencing this stored knowledge, your agent can provide more accurate, context-aware
responses, perform multi-step tasks that rely on previously stated information, and avoid asking
users to repeat key details.
Default namespace
/strategy/{memoryStrategyId}/actors/{actorId}/
Topics
• System prompt for semantic memory strategy
System prompt for semantic memory strategy
The semantic strategy includes instructions and output schemas in the default prompts for the
extraction and consolidation steps.

Memory strategies

540


## Memory organization and record streaming intro (pp. 585–590)

• Right-sizing : Choose appropriate compute memory and timeout settings based on your
processing requirements
Processing considerations
• Trigger optimization : Conﬁgure trigger conditions based on your use case requirements balance between processing eﬃciency and memory freshness by considering your application’s
tolerance for latency versus processing costs.
• FIFO topics : Use FIFO SNS topics when session ordering is critical (e.g., for summarization
workﬂows)
• Memory consolidation : Implement deduplication logic to prevent storing redundant or
conﬂicting memory records, which reduces storage costs and improves retrieval accuracy
• Memory record organization : Always include meaningful namespaces and strategy IDs when
ingesting records to enable eﬃcient categorization, ﬁltering, and retrieval of memory records
Security
• Least privilege : Grant minimal required permissions to all IAM roles
• Encryption : Use KMS encryption for S3 buckets and SNS topics containing sensitive data

Memory organization in AgentCore Memory
You can set how short-term and long-term memories are organized in an AgentCore Memory.
This lets you isolate memories by session and by actor. For long-term memory, you can also set a
namespace to organize the extracted memories for a memory strategy.
• Actor – Refers to entities such as end users or agent/user combinations. For example, in a coding
support chatbot, the actor is usually the developer asking questions. Using the actor ID helps
the system know which user the memory belongs to, keeping each user’s data separate and
organized.
• Session – A single conversation or interaction period between the user and the AI agent. It
groups all related messages and events that happen during that conversation.
• Strategy (Long-term memory only) – Shows which long-term memory strategy is being used.
This strategy identiﬁer is auto-generated when you create an AgentCore Memory.

Memory organization

585

Short-term memory organization
When you create a short term memory event with CreateEvent , you specify a session ID (
sessionId ) and an actor ID ( actorId ) that uniquely identify the session and actor for the
event. Later, you can retrieve events for a user or session by using short-term memory operations.
For example code, see Step 3: Capture the conversation history.

Long-term memory organization
When you create or update an AgentCore Memory, you can optionally create one or more memory
strategies . Within a strategy, use a namespace to specify AgentCore Memory organizes long-term
memories.
Every time AgentCore Memory extracts a new long-term memory with a memory strategy, the
long-term memory is saved under the namespace you set. This means that all long-term memories
are scoped to their speciﬁc namespace, keeping them organized and preventing any conﬂicts with
other users or sessions. You should use a hierarchical format separated by forward slashes / ,
ending with a trailing slash. The trailing slash prevents preﬁx collisions in multi-tenant applications
—for example, use /actors/Alice/ instead of /actors/Alice . As needed, you can use
the following pre-deﬁned variables within braces in the namespace based on your application’s
organization needs:
• actorId – Identiﬁes who the long-term memory belongs to.
• strategyId – Shows which memory strategy is being used.
• sessionId – Identiﬁes which session or conversation the memory is from.
For example, if you deﬁne the following namespace as the input to your strategy when creating an
AgentCore Memory:
/strategy/{memoryStrategyId}/actor/{actorId}/session/{sessionId}/

After memory creation, this namespace might look like:
/strategy/summarization-93483043/actor/actor-9830m2w3/session/session-9330sds8/

A namespace can have diﬀerent levels of granularity:
Memory organization

586

Most granular Level of organization
/strategy/{memoryStrategyId}/actor/{actorId}/session/{sessionId}/
Granular at the actor Level across sessions
/strategy/{memoryStrategyId}/actor/{actorId}/
Granular at the strategy Level across actors
/strategy/{memoryStrategyId}/
Global across all strategies
/
For example code, see Enable long-term memory.
For more information about organizing long-term memories with namespaces, including custom
namespace variables and IAM access control, see Specify long-term memory organization with
namespaces.
Restrict access with IAM
You can create IAM policies to restrict memory access by the scopes you deﬁne, such as actor,
session, and namespace. Use the scopes as context keys in your IAM polices.
The following policy restricts access to retrieving memories to a speciﬁc namespace or records
under a particular namespacePath hierarchy. In this example, the policy allows access only to
memories with exact namespaces such as summaries/agent1/ OR with namespaces under the
following namespacePath hierarchy with summaries/agent1/ , such as summaries/agent1/
session1/ or summaries/agent1/session2/.
{
"Version":"2012-10-17",
"Statement": [
{
"Sid": "SpecificNamespaceAccess",
"Effect": "Allow",
"Action": [
"bedrock-agentcore:RetrieveMemoryRecords"
Memory organization

587

],
"Resource": "arn:aws:bedrock-agentcore:us-east-1:123456789012:memory/memory_id",
"Condition": {
"StringEquals": {
"bedrock-agentcore:namespace": "summaries/agent1/"
}
}
},
{
"Sid": "SpecificNamespacePathAccess",
"Effect": "Allow",
"Action": [
"bedrock-agentcore:RetrieveMemoryRecords"
],
"Resource": "arn:aws:bedrock-agentcore:us-east-1:123456789012:memory/memory_id",
"Condition": {
"StringLike": {
"bedrock-agentcore:namespacePath": "summaries/agent1/*"
}
}
}
]
}

Memory record streaming
Memory record streaming in Amazon Bedrock AgentCore Memory delivers real-time notiﬁcations
when memory records are created, updated, or deleted. Instead of polling APIs to detect changes,
you receive push-based events to a Kinesis Data Stream in your account, enabling event-driven
architectures that react to memory record lifecycle changes as they occur.
With memory record streaming, you can:
• Receive real-time events for memory record creation, updates, and deletion
• Build event-driven architectures without polling APIs
• Stream memory record data into data lakes for consolidation and proﬁle management
• Trigger downstream workﬂows when new insights are extracted
• Track memory record state changes across agents and sessions
Topics
Memory record streaming

588

• How it works
• Stream event types
• Event schema
• Prerequisites
• Set up streaming
• Conﬁgure event content level
• Test your implementation
• Manage streaming conﬁguration
• Observability

How it works
Memory record streaming uses a push-based delivery model. When memory records change,
events are automatically published to your Kinesis Data Stream.
Events are triggered by the following operations:
1. Creation – Asynchronous extraction from short-term memory events (via CreateEvent and
memory strategies), or direct creation via BatchCreateMemoryRecords API
2. Updates – Direct modiﬁcation via BatchUpdateMemoryRecords API
3. Deletion – Consolidation workﬂows (de-duplication/superseding), DeleteMemoryRecord API,
or BatchDeleteMemoryRecords API

Stream event types
The following table describes the supported stream event types and when they are triggered.
Operation

Stream event type

Triggered by

Create

MemoryRecordCreated

Long term memory extractio
n/consolidation, BatchCrea
teMemoryRecords

Update

MemoryRecordUpdated

API

BatchUpdateMemoryR
ecords API

Memory record streaming

589

Operation

Stream event type

Triggered by

Delete

MemoryRecordDeleted

BatchDeleteMemoryR
ecords , DeleteMem
oryRecord API, long term
memory consolidation

Event schema
MemoryRecordCreated / MemoryRecordUpdated
MemoryRecordCreated and MemoryRecordUpdated events share the same schema.
{
"memoryStreamEvent": {
"eventType": "<MemoryRecordCreated, MemoryRecordUpdated>",
"eventTime": "2026-03-06T16:45:00.000Z",
"memoryId": "<memory-id>",
"memoryRecordId": "<memory-record-id>",
"namespaces": ["<namespace>"],
"createdAt": 1736622300000,
"memoryStrategyId": "<memory-strategy-id>",
"memoryStrategyType": "<memory-strategy-type>",
"metadata": {<metadata>},
"memoryRecordText": "<memory-record-text>"
}
}

The memoryRecordText ﬁeld is only included when the content level on the stream delivery
conﬁguration is set to FULL_CONTENT . See Conﬁgure event content level for additional details.
MemoryRecordDeleted
{
"memoryStreamEvent": {
"eventType": "MemoryRecordDeleted",
"eventTime": "2026-02-16T00:13:54.912530116Z",
"memoryId": "<memory-id>",
"memoryRecordId": "<memory-record-id>"
}
Memory record streaming

590


## Cross-account memory access (intro) (pp. 599–601)

Cross-account memory access
Amazon Bedrock AgentCore Memory supports cross-account access, enabling you to build
multi-account architectures where memory resources and consuming agents span multiple AWS
accounts. Cross-account access covers two scenarios:
• Data plane operations from another account — Principals in Account B can call memory data
plane APIs (create events, write records, retrieve records) against a memory resource in Account
A. This is conﬁgured by attaching a resource-based policy to the memory resource.
High-level steps:
a. Conﬁgure your memory resource to allow cross-account access by attaching a resource-based
policy.
b. Reference the memory ARN in your data plane API calls from Account B.
• Delivery destinations in another account — Your memory resource in Account A can deliver
payloads and stream events to Amazon S3 buckets, Amazon SNS topics, and Amazon Kinesis
Data Streams that reside in Account B. This is conﬁgured at memory creation time through the
memory execution role and resource policies on the target resources.
High-level steps:
a. Create a memory execution role in Account A with permissions to access the target resources.
b. Add resource-based policies to the destination resources in Account B to allow the execution
role.
c. Create the memory in Account A, referencing the execution role and cross-account resource
ARNs.
Topics
• Prerequisites
• Cross-account data plane access
• Cross-account delivery destinations
• Best practices

Prerequisites
Before conﬁguring cross-account memory access, verify you have:
Cross-account memory access

599

• A memory resource created in the resource owner account (Account A)
• The full ARN of the memory resource (for example, arn:aws:bedrock-agentcore:useast-1:<account-id>:memory/<memory-id>)
• For data plane access: an IAM role or user in Account B with identity-based permissions that
allow the desired bedrock-agentcore actions
• For delivery destinations: the target S3 bucket, SNS topic, or Kinesis Data Stream created in
Account B

Cross-account data plane access
You can allow principals in another account to call memory data plane APIs directly against your
memory resource. This is conﬁgured by attaching a resource-based policy to the memory using
the PutResourcePolicy API. For more information about resource-based policies, see Resourcebased policies for Amazon Bedrock AgentCore.
How it works
1. Account A creates a memory resource.
2. Account A attaches a resource-based policy to the memory resource using the
PutResourcePolicy API, granting speciﬁc actions to a principal in Account B.
3. A principal in Account B calls memory data plane APIs, specifying the full ARN of the memory
resource in Account A as the memory-id.
4. AWS evaluates both the resource-based policy on the memory and the identity-based policy
attached to the Account B principal. If both allow the action (and no policy explicitly denies it),
the request succeeds.
Supported actions
You can grant cross-account access for any memory data plane action. The following table lists the
available actions:
Action

Description

bedrock-agentcore:CreateEvent

Create a short-term memory event

bedrock-agentcore:GetEvent

Retrieve a speciﬁc event

Cross-account memory access

600

Action

Description

bedrock-agentcore:DeleteEvent

Delete a speciﬁc event

bedrock-agentcore:ListEvents

List events in a session

bedrock-agentcore:ListActors

List actors in a memory

bedrock-agentcore:ListSessions

List sessions for an actor

bedrock-agentcore:GetMemory

Retrieve a speciﬁc memory record

Record
bedrock-agentcore:ListMemor

List memory records in a namespace

yRecords
bedrock-agentcore:RetrieveM

Semantically search memory records

emoryRecords
bedrock-agentcore:DeleteMem

Delete a speciﬁc memory record

oryRecord
bedrock-agentcore:BatchCrea

Create multiple memory records

teMemoryRecords
bedrock-agentcore:BatchUpda

Update multiple memory records

teMemoryRecords
bedrock-agentcore:BatchDele

Delete multiple memory records

teMemoryRecords
bedrock-agentcore:ListMemor

List extraction jobs for a memory

yExtractionJobs
bedrock-agentcore:StartMemo

Restart failed extraction jobs

ryExtractionJobs

Cross-account memory access

601


## Long-term memory vs. RAG (pp. 610–610)

"resources": [
{
"kinesis": {
"dataStreamArn": "arn:aws:kinesis:us-east-1:<account-B-id>:stream/memoryrecord-stream",
"contentConfigurations": [
{
"type": "MEMORY_RECORDS",
"level": "FULL_CONTENT"
}
]
}
}
]
}'

Best practices
• Grant least privilege — Only grant the speciﬁc actions needed by the cross-account principal.
• Use speciﬁc principals — Grant access to speciﬁc IAM roles rather than the entire account root to
limit blast radius.
• Audit cross-account access — Use AWS CloudTrail to monitor cross-account API calls to your
memory resources.
• Separate read and write access — Create separate policy statements for read-only consumers
and read-write producers.
• Validate before removing policies — Before removing a resource-based policy, verify that no
active workloads in other accounts depend on the access.

Compare long-term memory with Retrieval-Augmented Generation
Long-term memory in Amazon Bedrock AgentCore Memory serves as persistent storage for
session-speciﬁc context, enabling agents to maintain continuity and personalization across
interactions. Use long-term memory to store user preferences, past decisions, conversation history,
and behavioral patterns that help agents adapt and feel personal without repeatedly requesting
the same information. This memory type is ideal for tracking who the user is, what has happened
in previous sessions, and maintaining state across multi-step workﬂows.
Retrieval-Augmented Generation (RAG) complements long-term memory by providing access to
authoritative, current information from large-scale repositories. Use these system to retrieve up-toCompare long-term memory with Retrieval-Augmented Generation

610


## Memory observability, best practices, memory poisoning (pp. 717–719)

Since Amazon Bedrock usage is attributed to your account, it consumes your allocated capacity and
is subject to your Bedrock service quotas. If Amazon Bedrock calls are throttled due to quota limits,
memory ingestion operations might fail.
Note
Amazon Bedrock usage is attributed to customer account only for custom memory
strategies.

To monitor and troubleshoot these issues, enable log delivery on your memory conﬁguration to
observe error logs when ingestion failures occur. You can also request quota increases for the
Bedrock models you’re using to prevent throttling issues.

Observability
You can monitor usage metrics for your memory in CloudWatch metrics. Some of the critical
metrics are displayed in AgentCore Memory console.

CloudWatch metrics : AgentCore Memory emits metrics to CloudWatch under the BedrockAgentCore namespace. The metrics contains:
• Data plane usage statistics: CreateEvent/RetrieveMemoryRecord Invocations , Latency ,
Errors , etc
• Ingestion metrics: Invocations , Latency , Errors NumberOfMemoryRecords for
extraction/consolidation step during ingestion in each memory resource.

Observability

717

In addition to CloudWatch metrics, customer can monitor the memory extraction process via
CloudWatch logs if they enabled log delivery. Application logs during ingestion will be published
to a log group in customer account. Customer can use the application logs to debug any errors
encountered during asynchronous ingestion process.
For more information, see Observe your agent applications on Amazon Bedrock AgentCore
Observability.

Best practices
We recommend these best practices for using AgentCore Memory eﬀectively in your AI agent
applications.
Topics
• Encrypting your memory
• Memory poisoning or prompt injection
• Least-privilege principle

Encrypting your memory
Your data stored in AgentCore Memory is always encrypted at rest using AWS KMS keys. By default,
encryption uses an AWS-owned and managed KMS key. You can optionally conﬁgure a customermanaged KMS key from your own AWS account for additional control over encryption by specifying
encryptionKeyArn when creating memory.

Memory poisoning or prompt injection
When processing conversational data through the CreateEvent API and extracting long-term
memory via LLM, it is important to protect against memory poisoning and prompt injection attacks
that could compromise data integrity or system behavior. These security concerns are critical as
they can lead to corrupted memory stores and manipulated system responses.
Following the AWS shared responsibility model, AWS is responsible for securing Amazon Bedrock
AgentCore infrastructure. However, customers bear the responsibility for secure application
development, input validation, and preventing prompt injection vulnerabilities in the memory
extraction service. This is similar to how AWS provides secure database engines like RDS, but
customers must prevent SQL injection in their applications.
Best practices

718

Threats
• Memory poisoning represents a threat where attackers embed false information in
conversations to corrupt long-term memory stores. This can manifest as context pollution, where
misleading context inﬂuences future memory retrieval, or as deliberate data integrity attacks
designed to degrade service quality over time.
• Prompt injection attacks occur when users attempt to override system prompts during memory
extraction or when malicious content in conversational data manipulates LLM behavior. These
attacks can also involve privilege escalation attempts to access or modify memory beyond user
permissions.
Prevention techniques
• Input validation forms the foundation of protection at the CreateEvent API level. Sanitize the
user input data with guardrails prior to persistence to memory
• Security testing – Regularly test your applications for prompt injection and other security
vulnerabilities using techniques like penetration testing, static code analysis, and dynamic
application security testing (DAST).

Least-privilege principle
Identity-based policies determine whether you can create, access, or delete Amazon Bedrock
AgentCore resources in your account. These actions can incur costs for your AWS account. When
you create or edit identity-based policies, follow these guidelines and recommendations:
• Get started with AWS managed policies and move toward least-privilege permissions – To
get started granting permissions to your users and workloads, use the AWS managed policies
that grant permissions for many common use cases. They are available in your AWS account. We
recommend that you reduce permissions further by deﬁning AWS customer managed policies
that are speciﬁc to your use cases.
• Apply least-privilege permissions – When you set permissions with IAM policies, grant only the
permissions required to perform a task. You do this by deﬁning the actions that can be taken on
speciﬁc resources under speciﬁc conditions, also known as least-privilege permissions.
• Use conditions in IAM policies to further restrict access – You can add a condition to your
policies to limit access to actions and resources. For example, you can write a policy condition to
specify the service role can only be assumed by a particular AgentCore Memory resource.
Least-privilege principle

719


## AWS Agent Registry: overview and concepts (pp. 2715–2724)

AWS Agent Registry: Discover and manage agents, tools,
and resources
Topics
• What is AWS Agent Registry?
• Why use AWS Agent Registry?
• How it works
• Accessing AWS Agent Registry
• Related services
• Key capabilities
• Concepts and terminology
• Prerequisites
• Sample use cases
• Get started with AWS Agent Registry
• Creating and managing registries
• Creating and managing registry records
• Curating the registry
• Discovering the registry
• Notiﬁcations (Amazon EventBridge)
• Using AWS Agent Registry with AWS Organizations
• Sharing a registry across accounts with AWS RAM
• Log Registry API calls with AWS CloudTrail
• VPC and AWS PrivateLink with AWS Agent Registry
• IAM Permissions
• Data protection in AWS Agent Registry
• Using service-linked roles for AWS Agent Registry
• Troubleshooting
• Comprehensive registry migration guide
2715

What is AWS Agent Registry?
AWS Agent Registry is a fully managed discovery service that provides a centralized catalog for
organizing, curating, and discovering resources across your organization. With AWS Agent Registry,
you can publish MCP servers, tools, agents, agent skills, and custom resources into a searchable
registry, control access through an approval workﬂow, and enable both human users and AI agents
to discover the right tools and agents through hybrid search, catalog browsing, and a native MCP
endpoint.

Why use AWS Agent Registry?
As organizations scale their use of AI agents and tools, discovering the right resource becomes
increasingly diﬃcult. Teams build MCP servers, deploy agents, and create specialized tools —
but without a central catalog, these resources remain siloed and hard to ﬁnd. This also causes
duplication of eﬀort and increased technical debt as teams re-build resources that already exist
simply because they are unable to discover them. AWS Agent Registry solves this by providing:
• Centralized discovery – A single place to ﬁnd all published resources across your organization,
searchable by both humans and agents.
• Governance and curation – An approval workﬂow that ensures only records meeting your
organization’s criteria for security, compliance, and quality are discoverable. Administrators
control what builders in their organization can discover and use, and can remove resources being
discoverable at any time.
• Flexible resource types – Register MCP servers, agents, skills, and any custom resource. AWS
Agent Registry validates MCP and agent records against their respective protocol schemas, and
supports custom metadata for all resource types.
• Hybrid search – Combines semantic understanding with keyword matching so that both natural
language queries and exact name lookups return relevant results.
• Catalog browsing – Paginate through approved records with ﬁlters, or fetch details for many
records at once, for building directory-style discovery experiences.
• MCP-native access – The Registry is available at a remote MCP endpoint that lets MCPcompatible clients interact with the registry directly using the Model Context Protocol.
• Flexible authorization – Choose between AWS IAM credentials or JSON Web Tokens (JWT) from
your corporate identity provider to control who can search, browse, and invoke the registry’s
MCP endpoint.
What is AWS Agent Registry?

2716

How it works
AWS Agent Registry is organized around two core resources:
• Registries – A registry is a catalog that you create in your AWS account. Each registry has its
own Name, Description, Authorization conﬁguration (IAM or JWT), approval settings, and
set of records. You can create a single organization wide registry, create registries organized
by resource type (such as an agent registry, MCP server registry, or skill registry), by stage of
development (production, QA, development), by team or business unit — whatever setup works
best for you.
• Registry records – A record represents an individual resource published into a registry. Each
record captures key metadata that describes the underlying resource — providing information
about what it is, what it does, and how it can be found.

Typical workﬂow
1. Create a registry – An administrator creates a registry and conﬁgures authorization and
approval settings.
2. Publish records – A publisher creates registry records describing their MCP servers, agents, or
tools, and submits them for approval.
3. Curate the registry – A curator (or the administrator) reviews records pending approval and
approves or rejects them; They also deprecate records no longer in use.
4. Discover resources – Consumers/End-Users search, browse the approved-record catalog, or
connect to the registry’s MCP endpoint to ﬁnd resources relevant to their needs.
You can learn more about how to conﬁgure IAM Permissions speciﬁc to each Persona in Key
Personas.

Accessing AWS Agent Registry
You can interact with AWS Agent Registry by directly invoking the Registry service’s public APIs
via the AWS CLI or AWS SDKs, or by invoking the registry’s MCP endpoint with any valid MCPcompatible client.

How it works

2717

Related services
• Host agent or tools with Amazon Bedrock AgentCore Runtime – Deploy and run the agents and
MCP servers that you register.
• Amazon Bedrock AgentCore Gateway: Securely connect tools and other resources to your
Gateway – Convert APIs and Lambda functions into MCP-compatible tools that can be registered.
• Provide identity and credential management for agent applications with Amazon Bedrock
AgentCore Identity – Manage identity and credential providers used for JWT-based registry
authorization.
• Amazon EventBridge – Receive notiﬁcations when registry records are submitted for approval.
• AWS CloudTrail – Log and monitor all API calls made to AWS Agent Registry.

Key capabilities
Migration Now Open
AWS Agent Registry has launched under the new agent-registry namespace. Support
for the public preview bedrock-agentcore namespace will be discontinued on
September 17, 2026. For migration instructions, see Comprehensive registry migration
guide.

Flexible resource types
Add records of any type with a ﬂexible structure and custom metadata. AWS Agent Registry
directly supports MCP servers, agents, and skills. For MCP Server and Agent records, AWS Agent
Registry validates your deﬁnitions against the MCP and A2A protocol schemas respectively,
ensuring correctness before records are published. You can also register any kind of custom
resource — such as agents conforming to protocols other than A2A, APIs, Lambda functions,
knowledge bases, or databases — by deﬁning your own metadata schema. This means AWS
Agent Registry can serve as a uniﬁed catalog for all discoverable resources in your organization,
regardless of the underlying technology.

Related services

2718

Hybrid search
AWS Agent Registry combines semantic search with keyword matching to deliver relevant results
for any type of query. When you search using natural language — such as "ﬁnd a tool that can
book ﬂights" — semantic search understands the intent and ﬁnds conceptually relevant records,
even if those exact words don’t appear in the record metadata. When you search using exact terms
— such as "weather-api-v2" — keyword search matches the precise text. Both search modalities run
simultaneously on every query, with results ranked by a weighted combination of relevance scores.
You can further narrow results using metadata ﬁlters on ﬁelds such as record name, record types,
and version.

Governance and curation
AWS Agent Registry gives administrators control over what builders in their organization can
discover and use. Administrators can ensure that only records meeting internally deﬁned criteria
for security, metadata richness, compliance, safety, and any other organizational standards are
approved and made visible in search results. When a curator needs to remove a resource from
discovery — whether due to a newly discovered issue, a deprecation, or a policy change — they can
deprecate existing approved records, ensuring those resources can no longer be found by builders.
For development environments where manual review isn’t needed, administrators can enable autoapproval so that submitted records become discoverable immediately.

Amazon EventBridge notiﬁcations
AWS Agent Registry sends events to Amazon EventBridge when a record is submitted for approval.
You can use these events to trigger automated review workﬂows, send alerts to curators via email
or messaging, or integrate with ticketing systems and approval pipelines. Events are delivered to
the default Amazon EventBridge bus in your account and Region, and can be routed to any Amazon
EventBridge-supported target including AWS Lambda, Amazon Simple Notiﬁcation Service,
Amazon Simple Queue Service, and AWS Step Functions.

Integrate with existing approval workﬂows
Many organizations already have established mechanisms for reviewing and approving resources
— processes that include security reviews, compliance checks, safety assessments, and other
evaluations. AWS Agent Registry can be integrated with these existing workﬂows through
Amazon EventBridge and the UpdateRegistryRecordStatus API. When a publisher submits
a record for approval, AWS Agent Registry sends an Amazon EventBridge notiﬁcation that
Hybrid search

2719

can trigger your existing review pipeline. Once your pipeline completes its checks, it calls the
UpdateRegistryRecordStatus API to approve or reject the record. By integrating AWS Agent
Registry with your existing review pipeline, you can curate the registry directly from your existing
approval process without changing how your organization reviews resources.

Discovering Resources using the Registry’s MCP Server
Each registry exposes an MCP-compatible endpoint that MCP clients can connect to directly using
the Model Context Protocol. This allows agents and tools built on MCP to discover and interact
with registered resources using standard MCP protocol communication — without needing to use
the AWS SDK or integrate with AWS-speciﬁc APIs. Any valid MCP-compatible client can connect
to the registry’s MCP endpoint and search for available resources in the registry. This enables
developers using AI IDEs to easily discover existing agents and tools in the organization and
leverage them as they build new agentic workﬂows.

Flexible Authorization
AWS Agent Registry supports two authorization methods for the search and MCP invoke
operations, so you can choose the approach that ﬁts your organization:
• AWS IAM — Use your existing IAM credentials for authorization. This is the simplest option for
teams already working within AWS, requiring no additional conﬁguration.
• JSON Web Tokens (JWT) — Integrate the registry with your organization’s existing identity
provider — such as Amazon Cognito, Okta, Microsoft Azure AD, or any OAuth 2.0-compatible
provider. Your developers and agents can search the registry and invoke the MCP endpoint using
their existing corporate credentials, without needing individual IAM access.
Control plane operations (creating, updating, and managing registries and records) always use IAM
authorization regardless of the registry’s search authorization setting.

Record synchronization
AWS Agent Registry can synchronize record metadata from external sources, keeping your registry
up to date. When you conﬁgure a record with a URL pointing to an external MCP server, AWS
Agent Registry fetches the latest server (Details like Name, Description) and tool metadata
(Tool Names, Tool Descriptions) from that URL and updates the record. Synchronization can be
used both to create the record the ﬁrst time by pulling the metadata from the URL provided, or
update an existing record with fresh metadata due to changes in the underlying resource. When
Discovering Resources using the Registry’s MCP Server

2720

Synchronization is used for an existing record, a new revision for the existing record is created.
Synchronization supports both OAuth and IAM credential providers for authorization.

CloudTrail integration
AWS Agent Registry control plane API calls are logged in AWS CloudTrail, providing a complete
audit trail of who did what and when. Control plane operations are logged as management events
by default.

Organization-wide auto-detection
If you use AWS Organizations, AWS Agent Registry can automatically discover and catalog
supported resources across your member accounts, giving you a single, organization-wide catalog
with no per-account setup. To enable auto-detection, you enable it on a registry from a delegated
administrator account (recommended, following least-privilege best practices). AWS Agent Registry
then creates a record for each discovered resource (currently Amazon Bedrock AgentCore Runtimes
and Gateways). The catalog stays in sync as resources are created, updated, or deleted and as
accounts join or leave the organization. Auto-detected records are clearly marked and linked
back to the source resource they were detected from, and you can enrich them with your own
descriptions and metadata. Detection is fully managed — there is nothing to install or conﬁgure
in individual member accounts. For more information, see Using AWS Agent Registry with AWS
Organizations.

Concepts and terminology
Migration Now Open
AWS Agent Registry has launched under the new agent-registry namespace. Support
for the public preview bedrock-agentcore namespace will be discontinued on
September 17, 2026. For migration instructions, see Comprehensive registry migration
guide.

Registry
A registry is a centralized catalog that you create in your AWS account to organize and manage
resources. Each registry has a name, a description, an authorization conﬁguration that controls
CloudTrail integration

2721

how consumers access the discoverable data-plane APIs and the MCP endpoint, and an approval
conﬁguration that determines whether records require manual review before becoming
discoverable.
How you organize your registries depends on your needs — for example, dedicated registries
for diﬀerent resource types (an agent registry, an MCP server registry, a skill registry), registries
for diﬀerent stages of development (production, QA, development), independent registries for
diﬀerent teams or business units, or a single registry for your entire organization.

Registry record
A registry record represents the metadata for an individual resource published into a registry. Each
record captures key metadata that describes the underlying resource — providing information
about what it is, what it does, and how it can be found. Records have a name, an optional humanreadable displayName, an optional description, a recordVersion, a recordType (AGENT,
MCP, SKILL, or CUSTOM), and resource-type-speciﬁc descriptors that carry the actual content. The
combination of name and recordVersion must be unique within the registry (used as a dedup
key), so the same name can be reused across diﬀerent versions of the same resource.

Resource types
MCP servers — Model Context Protocol (MCP) servers provide tools that AI agents can discover and
invoke. An MCP server record contains a server deﬁnition describing the server’s conﬁguration and
tool deﬁnitions for all the tools the server provides, including their input parameters and output
formats. AWS Agent Registry validates MCP server records against the MCP protocol schema to
ensure correctness.
Agents — Agents are autonomous programs that can reason, plan, and take actions to accomplish
tasks. An agent record contains an agent card that describes the agent’s capabilities, skills, and
communication interface per the A2A (Agent-to-Agent) protocol speciﬁcation. AWS Agent Registry
validates agent records against the A2A protocol schema to ensure correctness.
Skills — Skills are reusable capabilities that can be shared across agents. A skill record contains
basic descriptor metadata like Name, Description, optional access information like Package or
Repository details, and optional markdown documentation describing what the skill does and how
to use it.
Custom resources — For resources that don’t ﬁt the standard types above you can deﬁne your own
metadata schema using any valid JSON structure.
Registry record

2722

Credential provider
When you conﬁgure a registry record to synchronize metadata from an external source (outbound
authorization) AWS Agent Registry needs credentials to access that source. A credential provider
stores the authorization details — either OAuth credentials or an IAM role — that AWS Agent
Registry uses to invoke the external resource’s endpoint during synchronization. You reference a
credential provider by its ARN when conﬁguring synchronization on a record. For more information,
see Manage credential providers.
Registry authorization has two types:
1. Inbound authorization: Use this conﬁguration to control how your consumers search, browse,
and invoke the registry’s discoverable data-plane APIs and MCP endpoint (via the AWS CLI, AWS
SDK, or an MCP-compatible client). The registry supports IAM-based and JWT-based inbound
authorization. You specify inbound authorization as part of the workﬂow for creating a registry.
2. Outbound authorization: When you conﬁgure a record for synchronization with a remote MCP
or A2A endpoint, the registry needs outbound credentials to invoke the remote resource at the
speciﬁed endpoint and retrieve metadata. You provide these credentials as part of setting up the
synchronization job for a particular registry record.

Tags
You can attach tags to registries and registry records for cost allocation, access control, and
organizational tracking. Each tag is a key-value pair, and both keys and values are strings you
deﬁne. Tags do not aﬀect the runtime behavior of a registry or a record — they exist as metadata
that you and your organization can use to categorize resources across an AWS account.

Key Personas
Personas that use the Registry can vary from organization to organization. However, we have
seen the following general personas that interact with the Registry, found commonly across
organizations.
Administrator
As an administrator, you own the registry infrastructure. You create and conﬁgure registries
within the AWS account, decide how each registry is organized (by team, environment, or
resource type), and choose the authorization method (IAM or JWT) that determines how
Credential provider

2723

consumers access the registry. You set up the approval workﬂow — deciding whether records
require manual review or are auto-approved — and conﬁgure Amazon EventBridge integrations
to connect the registry to your organization’s existing notiﬁcation and review systems. You
manage IAM permissions to control which publishers, curators, and consumers can access each
registry. As the admin, you also have full access to create, update, and delete records, and can
approve, reject, or deprecate records when needed.
Publisher
As a publisher, you are a builder within the organization who has created a resource — an MCP
server, an agent, a skill, or some other tool — and wants to make it discoverable to others.
You create registry records that describe your resources, providing the metadata, deﬁnitions,
and version information that helps others ﬁnd and understand what the resource does. You
iterate on records in Draft status, reﬁning descriptions and schemas until the record is ready,
then submit it for approval. If a record is rejected, you review the curator’s feedback, make the
necessary changes, and resubmit. You can also conﬁgure URL-based synchronization so that
your records stay in sync with live MCP servers without manual updates.
Curator / Approver
As a curator, you are the quality gatekeeper of the registry, and can often also be the
administrator of the registry. You review records that publishers have submitted for approval,
evaluating each record against your organization’s standards for security, compliance, metadata
completeness, and any other criteria your organization deﬁnes. You approve records that
meet these standards — making them visible via the discoverable data-plane APIs (search,
list, batch-get) and through the MCP endpoint — and reject records that don’t, providing clear
feedback on what needs to be ﬁxed. When a resource is decommissioned, has known issues,
or is superseded by a newer version, you deprecate the record to remove it from discovery. As
a curator, you help keep the registry a trusted, high-quality catalog that builders across the
organization can rely on.
Consumer
As a consumer, you are a human or agent that needs to ﬁnd and use resources. You can discover
approved records in three ways:
• Search with natural language queries or keyword lookups to ﬁnd records that match a topic,
capability, or use case (SearchDiscoverableRegistryRecords).
• Browse the catalog of approved records with a paginated list, optionally
ﬁltered by record type, and retrieve details for one or many records at a time
Key Personas

2724


## Registry sample use cases (pp. 2742–2744)

"bedrock-agentcore:InvokeRegistryMcp"
],
"Resource":
[
"arn:aws:bedrock-agentcore:*:<account>:registry/*"
]
}
]
}

For example IAM policies, see Identity and access management for Amazon Bedrock AgentCore.

(Optional) Identity provider for JWT authorization
If you plan to use JWT authorization for inbound identity (to enable consumers to search the
registry using Non-IAM identities), set up Amazon Cognito or your own identity provider before
creating the registry:
1. Create a Cognito User Pool (or use your existing identity provider)
2. Register an App Client and note the Client ID
3. Create a test user with a username and password
For detailed instructions, see Conﬁgure inbound JWT authorizer.

Sample use cases
Migration Now Open
AWS Agent Registry has launched under the new agent-registry namespace. Support
for the public preview bedrock-agentcore namespace will be discontinued on
September 17, 2026. For migration instructions, see Comprehensive registry migration
guide.

Below you will ﬁnd some examples use cases where registry can be used.

(Optional) Identity provider for JWT authorization

2742

Discover Agents or Tools for building an internal workﬂow
A builder is creating an internal HR workﬂow that generates a report of employee time-oﬀ
balances. The workﬂow needs access to an employee information service, a PTO tracking service,
and a document generation service like SharePoint. Rather than asking around or searching
through internal wikis, the builder searches the AWS Agent Registry for services matching their
needs. They ﬁnd all three services registered with their connection details and tool schemas,
and use this information to construct the workﬂow — reducing what would have been days of
discovery into minutes.

Add a new capability to a customer-facing agent
A builder maintains an external customer service agent that handles order inquiries. They need
to add a new use case: helping customers track delayed package deliveries. The agent already
has access to customer information and order history services, but needs a delivery tracking
service. The builder searches the registry, ﬁnds a registered delivery tracking service with the right
capabilities, attaches it to their Gateway, and updates the agent’s policy to allow calls to this new
service — all without needing to know which team built the delivery service or how to contact
them.

Manage agent sprawl across teams
An administrator reviewing the registry notices that a new team is building a travel booking
agent with capabilities very similar to an existing travel planning agent registered by another
team. By discovering this overlap through the registry, the administrator connects the two teams.
Instead of duplicating eﬀort, the existing agent is updated with the additional capabilities, and the
organization avoids maintaining two agents that do essentially the same thing.

Share reusable skills across agents
A team has developed a skill for extracting structured data from PDF documents. They received
positive feedback about the eﬀectiveness of this skill, and were asked to broadly share this skill
across the organization to boost collective productivity. Instead of reaching out to each team
independently, they publish the skill to the registry with detailed markdown documentation and
a structured deﬁnition. Other agent builders discover the skill through search or by browsing the
approved-record catalog, and integrate it into their own agents, accelerating development across
the organization.
Discover Agents or Tools for building an internal workﬂow

2743

Explore the registry catalog before committing to a search
A builder who is new to the registry doesn’t yet know what’s available and can’t craft
a speciﬁc search query. They browse the approved-record catalog through the console
or ListDiscoverableRegistryRecords, ﬁlter by record type (say, MCP servers),
and page through results to get a sense of what tools exist in the organization. When
they ﬁnd several records that look promising, they fetch full details in a single call with
BatchGetDiscoverableRegistryRecord and pick the ones that ﬁt their workﬂow.

Enforce quality standards through curation
A builder submits a new MCP server record to the registry. The submission triggers an Amazon
EventBridge notiﬁcation that kicks oﬀ the organization’s standard review pipeline. The automated
pipeline checks that the server deﬁnition includes complete tool descriptions, that input schemas
are properly deﬁned, and that the server meets the organization’s security requirements. The
review ﬁnds that several tool descriptions are missing required ﬁelds. The curator rejects the record
with a detailed reason, and the builder receives feedback on what to ﬁx before resubmitting.

Keep registry records synchronized with live servers
A team deploys MCP servers on AgentCore Runtime whose tool deﬁnitions evolve as new features
are added. Rather than manually updating registry records every time a tool changes, they
conﬁgure URL-based synchronization on each record and simply come to the registry periodically
to trigger synchronization. When they do so, AWS Agent Registry fetches the latest server and tool
metadata from the MCP server’s endpoint, keeping the registry accurate.

Get started with AWS Agent Registry
Migration Now Open
AWS Agent Registry has launched under the new agent-registry namespace. Support
for the public preview bedrock-agentcore namespace will be discontinued on
September 17, 2026. For migration instructions, see Comprehensive registry migration
guide.

In this guide, you’ll create your ﬁrst registry, add a record, approve it, and search for it.
Explore the registry catalog before committing to a search

2744
