# Amazon Bedrock AgentCore Developer Guide — Evaluations framework examples (selected chapters)

## Summary

This filtered excerpt documents, framework by framework, exactly how AgentCore Evaluations instruments and extracts data from seven agent frameworks: Strands Agents, LangGraph, OpenAI Agents, Vercel AI SDK, LlamaIndex, Google ADK, and the Claude Agent SDK. Each framework's section follows the same template — which instrumentation library or libraries to use, which attribute identifies each of the three evaluation-relevant span kinds (invoke-agent, execute-tool, inference), and where the actual prompt/response/tool content lives in the resulting telemetry.

That repetition is itself the finding: across all seven frameworks, three structural patterns recur identically. First, two separate, non-interoperable OpenTelemetry semantic conventions coexist in the wild — native OTel GenAI (`gen_ai.operation.name`) and OpenInference (`openinference.span.kind`) — and several frameworks support both as alternative instrumentation choices, with the evaluation service extracting identical values from either. Second, when an agent runs under the AWS Distro for OpenTelemetry (ADOT), such as on AgentCore Runtime, no instrumentation code is needed at all — adding the library to the project's dependencies is sufficient, because ADOT discovers and activates it automatically at startup. Third, conversation content arrives in one of two delivery shapes, split telemetry (content in a correlated event record) or unified telemetry (content as inline span events), with the span's classifying attribute staying in the same place either way.

A closing, framework-specific detail worth noting: not every framework's instrumentation emits all three span kinds. The Claude Agent SDK, for instance, emits only AGENT and TOOL spans, folding model metadata onto the AGENT span rather than emitting a separate inference span — illustrating that a robust extraction contract has to tolerate a framework collapsing multiple logical operations into fewer physical spans, not assume a fixed one-span-per-kind shape.

## Knowledge Map

- The seven-framework reference: which instrumentation library, which identifying attribute, where the content lives, for Strands, LangGraph, OpenAI Agents, Vercel AI SDK, LlamaIndex, Google ADK, and Claude Agent SDK
- Two competing, coexisting OpenTelemetry semantic conventions for agent spans (native OTel GenAI vs. OpenInference) and how an evaluator normalizes both
- Dependency-only auto-instrumentation under ADOT — no instrumentation code required when the runtime performs auto-discovery
- Split vs. unified telemetry delivery modes as two equally-supported shapes for where conversation content lives relative to its span
- Real-world non-conformance to a clean span taxonomy: a framework may legitimately omit or collapse span kinds

## Key Takeaways

- When an ecosystem has two competing semantic conventions for the same concept, a robust consumer recognizes both rather than picking a side.
- Under an auto-instrumenting runtime (ADOT), instrumentation is a dependency-management decision, not a coding task.
- Design a telemetry extraction contract around "recognize whichever spans and delivery shape are actually present," not around a fixed, assumed structure.
- A framework's own instrumentation choices (which spans it emits, how granular they are) are outside a consuming service's control and must be treated as a source of natural variation, not an error condition.

## Source Text

Source: Amazon Bedrock AgentCore Developer Guide (3,428-page PDF), filtered to selected page ranges.


## Sample agents and supported frameworks (pp. 2160–2164)

Sample agents
The following examples show how to instrument a Strands agent hosted outside Amazon Bedrock
AgentCore Runtime. Each example exports telemetry to Amazon CloudWatch using ADOT. They
focus on observability setup rather than the evaluation API. The examples use Strands, but the
same hosting and telemetry-export pattern applies to other supported frameworks, such as
LangGraph.
• Amazon EKS: Observability for an EKS-hosted agent and Strands agent on Amazon EKS, both on
the GitHub website.
• Amazon ECS: Strands agent on Amazon ECS on the GitHub website.
• AWS Lambda: Strands agent in AWS Lambda on the GitHub website.

Supported agent frameworks
Amazon Bedrock AgentCore Evaluations evaluates agents built with several agent frameworks.
What an agent emits as telemetry, and how that telemetry is structured, depends on the agent
framework you build with and the instrumentation library you use to record it.
For each supported framework, this section describes:
• The instrumentation libraries you can use.
• How to instrument your agent.
• What the resulting spans and event records look like.
• How the evaluation service locates the values it needs, such as the user prompt, the agent
response, and tool calls.
AgentCore Evaluations supports the following frameworks and instrumentation libraries. Several
frameworks are supported in both Python and TypeScript. The Python and TypeScript versions of
a library emit diﬀerent scope names, so each language has its own row. For a given framework and
instrumentation library, the evaluation service extracts the same values from either language.

Sample agents

2160

Agent
framework

Instrumen
tation
library

Language

Scope name

Recommend
ed version

Strands
Agents

Built-in
(Strands
Agents SDK)

Python

strands.telemetry.

Latest

Strands
Agents

Built-in
(Strands
Agents SDK)

TypeScript

tracer

strands-agents

@strandsagents/
sdk >=
1.5.0

LangGraph

OpenTelem
etry

Python

opentelemetry.inst

>= 0.55.0

rumentation.langch

(opentelem

ain

etry-inst
rumentati
on-langch
ain )
LangGraph

OpenInfer
ence

Python

openinference.inst

>= 0.1.62

rumentation.langch

(openinfer

ain

ence-inst
rumentati
on-langch
ain )
LangGraph

LangGraph

OpenTelem
etry, ADOTnative

TypeScript

OpenTelem
etry

TypeScript

@aws/aws-distro-op

>= 0.12.0

entelemetry-instru
mentation-langchain
@traceloop/instrum

>= 0.27.0

entation-langchain

(@traceloo
p/instrum

Supported frameworks

2161

Amazon Bedrock AgentCore

Agent
framework

Developer Guide

Instrumen
tation
library

Language

Scope name

Recommend
ed version

TypeScript

@arizeai/openinfer

>= 4.0.14

entationlangchain
)
LangGraph

OpenInfer
ence

ence-instrumentati

(@arizeai/

on-langchain

openinfer
ence-inst
rumentati
on-langch
ain )
OpenAI
Agents

OpenTelem
etry

Python

opentelemetry.inst

>= 0.61.0

rumentation.openai

(opentelem

_agents

etry-inst
rumentati
on-openai
-agents )
OpenAI
Agents

OpenInfer
ence

Python

openinference.inst

>= 1.5.0

rumentation.openai

(openinfer

_agents

ence-inst
rumentati
on-openai
-agents )
OpenAI
Agents

OpenTelem
etry, ADOTnative

TypeScript

@aws/aws-distro-op

>= 0.12.0

entelemetry-instru
mentation-openai-a
gents

Supported frameworks

2162

Agent
framework

Instrumen
tation
library

Language

Scope name

Recommend
ed version

OpenAI
Agents

OpenInfer
ence

TypeScript

@arizeai/openinfer

>= 0.2.2

ence-instrumentati

(@arizeai/

on-openai-agents

openinfer
ence-inst
rumentati
on-openai
-agents )
Vercel AI SDK

LlamaIndex

OpenTelem
etry, ADOTnative

TypeScript

OpenTelem
etry

Python

@aws/aws-distro-op

>= 0.12.0

entelemetry-instru
mentation-vercel-ai
opentelemetry.inst

>= 0.61.0

rumentation.llamai

(opentelem

ndex

etry-inst
rumentati
on-llamai
ndex )
LlamaIndex

OpenInfer
ence
(openinfer

Python

openinference.inst

>= 4.4.1

rumentation.llama_
index

ence-inst
rumentati
on-llamaindex )

Supported frameworks

2163

Agent
framework

Instrumen
tation
library

Language

Scope name

Recommend
ed version

Google ADK

OpenInfer
ence

Python

openinference.inst

>= 0.1.13

rumentation.google

(openinfer

_adk

ence-inst
rumentati
on-google
-adk )
Claude Agent
SDK

OpenInfer
ence
(openinfer

Python

openinference.inst

>= 0.1.3

rumentation.claude
_agent_sdk

ence-inst
rumentati
on-claude
-agent-sd
k )

Each span your agent emits carries a scope name, which identiﬁes the instrumentation library
that produced it. The evaluation service reads this name to tell which library it is dealing with, and
therefore whether it can process the span and which attributes to look for. The scope name is the
value of the scope.name ﬁeld on each span and event record.
The attribute names and the location of the conversation content diﬀer by framework and
instrumentation library. For the attributes and example spans of a single framework, see that
framework’s page.

Note
Instrumenting your agent is only one part of producing telemetry that the evaluation
service can read. Your agent must also have observability enabled, so that it exports its
telemetry to Amazon CloudWatch.

Supported frameworks

2164


## Strands Agents (pp. 2165–2175)

For how AgentCore delivers that telemetry, where the service ﬁnds the values it needs, and
the setup steps for your hosting option, see Telemetry setup and delivery.

Topics
• Set up Strands Agents telemetry for AgentCore Evaluations
• Set up LangGraph telemetry for AgentCore Evaluations
• OpenAI Agents
• Set up Vercel AI SDK telemetry for AgentCore Evaluations
• LlamaIndex
• Google ADK
• Claude Agent SDK
• Generic framework support

Set up Strands Agents telemetry for AgentCore Evaluations
This page explains how to instrument a Strands Agents agent, how spans are identiﬁed, and how
evaluation ﬁelds are extracted.
Topics
• Python agent support
• Instrument your agent
• How spans are identiﬁed
• How evaluation ﬁelds are extracted
• From event records
• From inline span events
• Example spans in split telemetry
• Example spans in uniﬁed telemetry
• TypeScript agent support
• Instrument your agent
• How spans are identiﬁed
• How evaluation ﬁelds are extracted
Strands Agents

2165

• Example spans from a TypeScript agent
AgentCore Evaluations supports Strands agents built with the Python SDK and the TypeScript SDK.
The two produce the same span types, identifying attributes, and content layout, under diﬀerent
scope names, so the evaluation service reads them the same way. This page covers each language
separately: for Python, see Python agent support; for TypeScript, see TypeScript agent support.

Python agent support
A Python Strands agent produces spans under the scope name strands.telemetry.tracer.
Instrument your agent
The Strands Agents SDK includes built-in telemetry and requires no additional instrumentation
library. It produces spans and event records under the scope name strands.telemetry.tracer.
When deployed on Amazon Bedrock AgentCore Runtime with the AWS Distro for OpenTelemetry
(ADOT), the Runtime injects the session.id attribute and exports spans and event records
automatically.

Note
Instrumentation is one step in setting up observability. To export telemetry for evaluation,
complete the full setup in Set up observability.

How spans are identiﬁed
Strands sets the gen_ai.operation.name attribute on each span. The evaluation service uses
this attribute to classify spans:

Span type

Identifying attribute

Invoke agent

gen_ai.operation.name

Example span name
=

invoke_agent TravelAgent

=

execute_tool search_fl

invoke_agent
Execute tool

gen_ai.operation.name
execute_tool

Strands Agents

ights

2166

Span type

Identifying attribute

Inference

gen_ai.operation.name

Example span name
=

chat

chat

How evaluation ﬁelds are extracted
Where the conversation content sits depends on the telemetry delivery mode. With split telemetry,
the content is in a separate event record. With uniﬁed telemetry, the content stays on the span,
as events attached to it. For more information, see Telemetry setup and delivery. The identifying
attribute (gen_ai.operation.name) is on the span in both modes.
From event records
With split telemetry, the service reads content from the event record correlated to each span:
• User prompt: from the agent input messages (input.messages), the content of the message
with a user role.
• Agent response: from the agent output messages (output.messages), the content of the
message with an assistant role.
• Tool call: the tool name from the gen_ai.tool.name attribute on the execute tool span. The
tool arguments and result come from that span’s event record (input and output).
For more information, see Example spans in split telemetry.
From inline span events
With uniﬁed telemetry, the same content is carried in inline span events instead of a separate event
record:
• User prompt: from the gen_ai.user.message event, the content attribute.
• Agent response: from the gen_ai.choice event, the message attribute.
• Tool call: the tool name from the gen_ai.tool.name attribute on the span. The tool
arguments come from the gen_ai.tool.message event, and the result comes from the
gen_ai.choice event.
For more information, see Example spans in uniﬁed telemetry.
Strands Agents

2167

Example spans in split telemetry
With split telemetry, the span carries the identifying attributes and the content lives in a correlated
event record. The following examples are from a Python Strands travel-planning agent deployed
on Amazon Bedrock AgentCore Runtime.
Note
These examples are not complete spans. They show representative data from a real agent
interaction, with some ﬁelds omitted and long values truncated for readability.

Example
Invoke agent span
The gen_ai.operation.name attribute (invoke_agent) identiﬁes this as an invoke agent
span. The gen_ai.agent.tools attribute lists the tools available to the agent.
{
"traceId": "69e9cc4771d7cabe0d8e8cea33b6b338",
"spanId": "d24936b8989b6d42",
"parentSpanId": "0ff3498548044e4b",
"name": "invoke_agent TravelAgent",
"kind": "INTERNAL",
"scope": {
"name": "strands.telemetry.tracer",
"version": ""
},
"startTimeUnixNano": 1776929864011990383,
"endTimeUnixNano": 1776929869634304466,
"durationNano": 5622314083,
"attributes": {
"gen_ai.operation.name": "invoke_agent",
"gen_ai.system": "strands-agents",
"gen_ai.agent.name": "TravelAgent",
"gen_ai.request.model": "us.anthropic.claude-sonnet-4-20250514-v1:0",
"gen_ai.usage.input_tokens": 983,
"gen_ai.usage.output_tokens": 232,
"gen_ai.usage.total_tokens": 1215,
"gen_ai.agent.tools": "[\"search_flights\", \"book_flight\", \"search_hotels\",
\"book_hotel\", \"search_activities\", \"book_activity\"]",
Strands Agents

2168

"session.id": "sea-nyc-trip-2-turns-adot_v17-20260423003743"
},
"status": {
"code": "OK"
}
}

The correlated event record carries the conversation content. The user prompt is the userrole message in input.messages, and the agent response is the assistant-role message in
output.messages.
{
"spanId": "d24936b8989b6d42",
"traceId": "69e9cc4771d7cabe0d8e8cea33b6b338",
"scope": {
"name": "strands.telemetry.tracer"
},
"body": {
"input": {
"messages": [
{
"role": "user",
"content": "Hey, how can you help me"
}
]
},
"output": {
"messages": [
{
"role": "assistant",
"content": {
"message": "Hi there! I'm your travel planning assistant ...",
"finish_reason": "end_turn"
}
}
]
}
}
}

Strands Agents

2169

Execute tool span
The gen_ai.operation.name attribute (execute_tool) identiﬁes this as an execute tool
span. The gen_ai.tool.name attribute holds the tool name.
{
"traceId": "69e9cc4d132b180909ba49f613f273dd",
"spanId": "fff785ce12d6fda8",
"parentSpanId": "96915bf5ecc78743",
"name": "execute_tool search_flights",
"kind": "INTERNAL",
"scope": {
"name": "strands.telemetry.tracer",
"version": ""
},
"startTimeUnixNano": 1776929872258292842,
"endTimeUnixNano": 1776929872259611427,
"durationNano": 1318585,
"attributes": {
"gen_ai.operation.name": "execute_tool",
"gen_ai.tool.name": "search_flights",
"gen_ai.tool.call.id": "tooluse_hiWwdtThuD67G5cK8cp5mj",
"gen_ai.tool.status": "success",
"gen_ai.tool.description": "Search for available flights between cities.",
"session.id": "sea-nyc-trip-2-turns-adot_v17-20260423003743"
},
"status": {
"code": "OK"
}
}

The correlated event record carries the tool input (arguments) and output (result).
{
"spanId": "fff785ce12d6fda8",
"traceId": "69e9cc4d132b180909ba49f613f273dd",
"scope": {
"name": "strands.telemetry.tracer"
},
"body": {
"input": {
"messages": [
{
Strands Agents

2170

"role": "tool",
"content": {
"content": "{\"origin\": \"SEA\", \"destination\": \"NYC\", \"date\":
\"2025-03-15\"}",
"role": "tool",
"id": "tooluse_hiWwdtThuD67G5cK8cp5mj"
}
}
]
},
"output": {
"messages": [
{
"role": "assistant",
"content": {
"message": "[{\"text\": \"{\\\"origin\\\": \\\"SEA\\\", \\\"destination\
\\": \\\"NYC\\\", \\\"flights\\\": [ ... ]}\"}]",
"id": "tooluse_hiWwdtThuD67G5cK8cp5mj"
}
}
]
}
}
}

Example spans in uniﬁed telemetry
With uniﬁed telemetry, the same content is carried in inline span events on the span, with no
separate event record. The following examples are from a Python Strands travel-planning agent.
Note
These examples are not complete spans. They show representative data from a real agent
interaction, with some ﬁelds omitted and long values truncated for readability.

Example
Invoke agent span
The gen_ai.user.message event holds the user prompt, and the gen_ai.choice event
holds the agent response.
Strands Agents

2171

{
"traceId": "69e9cc4771d7cabe0d8e8cea33b6b338",
"spanId": "d2ee0e4765cc773e",
"name": "invoke_agent TravelAgent",
"kind": "INTERNAL",
"scope": {
"name": "strands.telemetry.tracer"
},
"attributes": {
"gen_ai.operation.name": "invoke_agent",
"gen_ai.agent.name": "TravelAgent",
"session.id": "sea-nyc-trip-2-turns-unified"
},
"events": [
{
"name": "gen_ai.user.message",
"attributes": {
"content": "[{\"text\": \"Hey, how can you help me\"}]"
}
},
{
"name": "gen_ai.choice",
"attributes": {
"message": "Hi there! I'm your travel planning assistant ...",
"finish_reason": "end_turn"
}
}
]
}

Execute tool span
The gen_ai.tool.message event holds the tool arguments, and the gen_ai.choice event
holds the tool result.
{
"traceId": "69e9cc4d132b180909ba49f613f273dd",
"spanId": "0a988e27758ebb53",
"name": "execute_tool search_flights",
"kind": "INTERNAL",
"scope": {
"name": "strands.telemetry.tracer"
},
Strands Agents

2172

"attributes": {
"gen_ai.operation.name": "execute_tool",
"gen_ai.tool.name": "search_flights",
"gen_ai.tool.call.id": "tooluse_JuGterOaZfQV2c55Rp3S7C",
"gen_ai.tool.status": "success",
"session.id": "sea-nyc-trip-2-turns-unified"
},
"events": [
{
"name": "gen_ai.tool.message",
"attributes": {
"content": "{\"origin\": \"SEA\", \"destination\": \"NYC\", \"date\":
\"2025-03-15\"}",
"role": "tool",
"id": "tooluse_JuGterOaZfQV2c55Rp3S7C"
}
},
{
"name": "gen_ai.choice",
"attributes": {
"message": "[{\"text\": \"{\\\"origin\\\": \\\"SEA\\\", \\\"destination\\\":
\\\"NYC\\\", \\\"flights\\\": [ ... ]}\"}]",
"id": "tooluse_JuGterOaZfQV2c55Rp3S7C"
}
}
]
}

TypeScript agent support
A TypeScript Strands agent produces spans under the scope name strands-agents. It emits the
same span types and content layout as a Python agent, so the evaluation service reads it the same
way.
Instrument your agent
The TypeScript Strands Agents SDK (@strands-agents/sdk >= 1.5.0) includes built-in
telemetry and requires no additional instrumentation library. When deployed on Amazon Bedrock
AgentCore Runtime with the AWS Distro for OpenTelemetry (ADOT), the Runtime injects the
session.id attribute and exports spans and event records automatically. The TypeScript SDK
produces spans under the scope name strands-agents.
Strands Agents

2173

Note
Instrumentation is one step in setting up observability. To export telemetry for evaluation,
complete the full setup in Set up observability.

How spans are identiﬁed
Span identiﬁcation is the same as for a Python agent. The gen_ai.operation.name attribute
classiﬁes each span. For the values and example span names, see How spans are identiﬁed under
Python support.
How evaluation ﬁelds are extracted
Field extraction is the same as for a Python agent. The conversation content is carried in inline span
events (gen_ai.user.message, gen_ai.choice, and gen_ai.tool.message). For where each
ﬁeld is read from, see From inline span events under Python support.
Example spans from a TypeScript agent
The following examples are from a TypeScript Strands travel-planning agent deployed on Amazon
Bedrock AgentCore Runtime.
Note
These examples are not complete spans. They show representative data from a real agent
interaction, with some ﬁelds omitted and long values truncated for readability.

Example
Invoke agent span
The gen_ai.operation.name attribute (invoke_agent) identiﬁes this as an invoke
agent span, and gen_ai.agent.tools lists the tools available to the agent. The
gen_ai.user.message event holds the user prompt, and the gen_ai.choice event holds
the agent response.
{
"traceId": "6a6bc695459e41aa14a172bb41d3246d",
"spanId": "c2c44e69bdab6ef1",
Strands Agents

2174

"parentSpanId": "f18d96d107e793ba",
"name": "invoke_agent Strands Agent",
"kind": "INTERNAL",
"scope": {
"name": "strands-agents",
"version": ""
},
"attributes": {
"gen_ai.operation.name": "invoke_agent",
"gen_ai.agent.name": "Strands Agent",
"gen_ai.system": "strands-agents",
"gen_ai.request.model": "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
"gen_ai.agent.tools": "[\"search_flights\", \"book_flight\", \"search_hotels\",
\"book_hotel\", \"search_activities\", \"book_activity\"]",
"session.id": "sea-nyc-trip-2-turns"
},
"events": [
{
"name": "gen_ai.user.message",
"attributes": {
"content": "[{\"text\": \"Hey, how can you help me\"}]"
}
},
{
"name": "gen_ai.choice",
"attributes": {
"message": "Hello! I'm your travel planning assistant, and I can help you
with the following: ..."
}
}
]
}

Execute tool span
The gen_ai.operation.name attribute (execute_tool) identiﬁes this as an execute tool
span; gen_ai.tool.name holds the tool name. The gen_ai.tool.message event holds the
tool arguments, and the gen_ai.choice event holds the tool result.
{
"traceId": "6a6bc69e6eaa1e994481bef349f4c72e",
"spanId": "4227ac5525f22dd2",
"parentSpanId": "8a989e0dbb9dc22f",
Strands Agents

2175


## LangGraph (pp. 2176–2201)

"name": "execute_tool search_flights",
"kind": "INTERNAL",
"scope": {
"name": "strands-agents",
"version": ""
},
"attributes": {
"gen_ai.operation.name": "execute_tool",
"gen_ai.tool.name": "search_flights",
"gen_ai.tool.call.id": "tooluse_AoP0OTnq2YcOZDvY7ldSUQ",
"gen_ai.tool.status": "success",
"session.id": "sea-nyc-trip-2-turns"
},
"events": [
{
"name": "gen_ai.tool.message",
"attributes": {
"content": "{\"origin\": \"SEA\", \"destination\": \"NYC\", \"date\":
\"2025-03-15\"}",
"role": "tool",
"id": "tooluse_AoP0OTnq2YcOZDvY7ldSUQ"
}
},
{
"name": "gen_ai.choice",
"attributes": {
"message": "[{\"text\": \"{\\\"origin\\\": \\\"SEA\\\", \\\"destination\\\":
\\\"NYC\\\", \\\"flights\\\": [ ... ]}\"}]",
"id": "tooluse_AoP0OTnq2YcOZDvY7ldSUQ"
}
}
]
}

Set up LangGraph telemetry for AgentCore Evaluations
This page explains how to instrument a LangGraph agent, how spans are identiﬁed, and how
evaluation ﬁelds are extracted. AgentCore Evaluations supports LangGraph agents built in Python
and TypeScript; this page covers each language separately, in Python agent support and TypeScript
agent support. It closes with best practices for structuring a LangGraph agent so that it can be
evaluated reliably.

LangGraph

2176

Topics
• Python agent support
• Instrument your agent
• How spans are identiﬁed
• How evaluation ﬁelds are extracted
• From event records
• From span attributes
• Example spans in split telemetry
• Example spans in uniﬁed telemetry
• TypeScript agent support
• Instrument your agent
• How spans are identiﬁed
• How evaluation ﬁelds are extracted
• Example spans from a TypeScript agent
• Best practices for LangGraph agents

Python agent support
A Python LangGraph agent emits spans under the scope name
opentelemetry.instrumentation.langchain (OpenTelemetry) or
openinference.instrumentation.langchain (OpenInference).
Instrument your agent
You can instrument a LangGraph agent with either of two instrumentation libraries:
OpenTelemetry (opentelemetry-instrumentation-langchain) or OpenInference
(openinference-instrumentation-langchain). Amazon Bedrock AgentCore Evaluations
supports both libraries. The libraries emit diﬀerent scope names and use diﬀerent span attributes.
The evaluation service extracts the same values from each.
When your agent runs with the AWS Distro for OpenTelemetry (ADOT), such as on Amazon
Bedrock AgentCore Runtime, you do not need to add explicit instrumentation code. Adding the
instrumentation library to your project’s dependencies is enough. ADOT discovers it at startup and
activates it automatically.
LangGraph

2177

Add the instrumentation library for the path you want to your dependencies. The following
examples pin a minimum version; use the latest available version unless you have a reason to pin.
Example
OpenTelemetry
NOTE: Use version 0.55.0 or later. Version 0.55.0 added support for the newer OpenTelemetry
generative-AI agent span conventions on the GitHub website, which the evaluation service relies
on.
Add opentelemetry-instrumentation-langchain to your dependencies. The scope name
emitted is opentelemetry.instrumentation.langchain.
requirements.txt:
opentelemetry-instrumentation-langchain>=0.55.0

pyproject.toml:
[project]
dependencies = [
"opentelemetry-instrumentation-langchain>=0.55.0",
]

OpenInference
Add openinference-instrumentation-langchain to your dependencies. The scope name
emitted is openinference.instrumentation.langchain.
requirements.txt:
openinference-instrumentation-langchain>=0.1.62

pyproject.toml:
[project]
dependencies = [
"openinference-instrumentation-langchain>=0.1.62",
LangGraph

2178

]

Note
Instrumentation is one step in setting up observability. To export telemetry for evaluation,
complete the full setup in Set up observability.

How spans are identiﬁed
The attribute used to classify spans diﬀers between the two instrumentation libraries.
Example
OpenTelemetry
The OpenTelemetry instrumentation library classiﬁes spans using the traceloop.span.kind
attribute, and recent versions also set gen_ai.operation.name.
Span type

Identifying attribute

Invoke agent

traceloop.span.kind
eration.name

Execute tool

Inference

= invoke_agent )

traceloop.span.kind
eration.name

= workflow (also gen_ai.op

= tool (also gen_ai.op

= execute_tool )

gen_ai.operation.name

= chat

OpenInference
The OpenInference instrumentation library classiﬁes spans using the
openinference.span.kind attribute.
Span type

Identifying attribute

Invoke agent

openinference.span.kind

LangGraph

= CHAIN or AGENT
2179

Span type

Identifying attribute

Execute tool

openinference.span.kind

= TOOL

Inference

openinference.span.kind

= LLM

How evaluation ﬁelds are extracted
For the invoke agent span, the input and output do not contain a clean per-message list. Instead,
the content is the serialized LangChain graph state: a JSON string that wraps the full state. The
exact shape of this serialized state diﬀers between the two instrumentation libraries. In both cases,
the service parses it to ﬁnd the user prompt (the human message) and the agent response (the AI
message).
LangGraph also serializes message roles in more than one form. A role can appear as a lowercase
value (human, ai, tool) or as a LangChain message class name (HumanMessage, AIMessage,
ToolMessage). The service recognizes both forms.
The location of this content depends on how telemetry was collected. The identifying attribute
(traceloop.span.kind or openinference.span.kind) is on the span in both cases. For more
information, see Telemetry setup and delivery.
From event records
With split telemetry, the service reads content from the event record correlated to each span:
• User prompt and agent response: from the invoke agent span’s event record, in body.input
and body.output.
• Tool call: the tool name from the execute tool span. The tool arguments and result come from
that span’s event record, in body.input and body.output.
For more information, see Example spans in split telemetry.
From span attributes
With uniﬁed telemetry, the same content stays on the span as attributes. The attributes depend on
the instrumentation library:
• OpenTelemetry:
LangGraph

2180

• User prompt and agent response: from gen_ai.task.input and gen_ai.task.output on
the invoke agent span.
• Tool call: the tool name from gen_ai.tool.name, and the arguments and result from
gen_ai.tool.call.arguments and gen_ai.tool.call.result, on the execute tool
span.
• OpenInference:
• User prompt and agent response: from input.value and output.value on the invoke
agent span.
• Tool call: the tool name from tool.name, and the arguments and result from input.value
and output.value, on the execute tool span.
For more information, see Example spans in uniﬁed telemetry.
Example spans in split telemetry
With split telemetry, the span carries the identifying attributes and the content lives in a
correlated event record. The following examples are from a Python LangGraph travel-planning
agent deployed on Amazon Bedrock AgentCore Runtime. The same agent is shown under each
instrumentation library.
Note
These examples are not complete spans. They show representative data from a real agent
interaction, with some ﬁelds omitted and long values truncated for readability.

OpenTelemetry
Example
Invoke agent span
The traceloop.span.kind attribute (workflow) identiﬁes this as an invoke agent span;
recent library versions also set gen_ai.operation.name = invoke_agent.
{
"traceId": "6a01eef11066751d68f90def0da1f80a",
"spanId": "ba1833fa7f097041",
LangGraph

2181

"parentSpanId": "836a5ccf9a2186cc",
"name": "travel_agent.workflow",
"kind": "INTERNAL",
"scope": {
"name": "opentelemetry.instrumentation.langchain",
"version": "0.60.0"
},
"startTimeUnixNano": 1778511607308521744,
"endTimeUnixNano": 1778511610930280395,
"durationNano": 3621758651,
"attributes": {
"traceloop.span.kind": "workflow",
"gen_ai.operation.name": "invoke_agent",
"gen_ai.agent.name": "travel_agent",
"gen_ai.provider.name": "langgraph",
"traceloop.workflow.name": "travel_agent",
"session.id": "sea-nyc-trip-2-turns-adot_v17_opentelemetry_0_60_0"
},
"status": {
"code": "OK"
}
}

The correlated event record carries the conversation. Each message’s content is the serialized
LangChain graph state. The input wraps the state under an inputs key. The output wraps it
under an outputs key, with each message as a LangChain constructor object. The user prompt
is the human message and the agent response is the AI message inside that serialized state.
{
"spanId": "ba1833fa7f097041",
"traceId": "6a01eef11066751d68f90def0da1f80a",
"scope": {
"name": "opentelemetry.instrumentation.langchain"
},
"body": {
"input": {
"messages": [
{
"content": "{\"inputs\": {\"messages\": [{\"role\": \"user\", \"content
\": \"Hey, how can you help me\"}]}, \"tags\": [], \"metadata\": {\"ls_integration
\": \"langchain_create_agent\", \"lc_agent_name\": \"travel_agent\", \"thread_id\":
\"sea-nyc-trip-2-turns-adot_v17_opentelemetry_0_60_0\"}, \"kwargs\": {\"name\":
\"travel_agent\"}}",
LangGraph

2182

"role": "user"
}
]
},
"output": {
"messages": [
{
"content": "{\"outputs\": {\"messages\": [{\"lc\": 1, \"type\":
\"constructor\", \"id\": [\"langchain\", \"schema\", \"messages\", \"HumanMessage
\"], \"kwargs\": {\"content\": \"Hey, how can you help me\", \"type\": \"human
\", \"id\": \"12345678-1234-1234-1234-123456789012\"}}, {\"lc\": 1, \"type\":
\"constructor\", \"id\": [\"langchain\", \"schema\", \"messages\", \"AIMessage\"],
\"kwargs\": {\"content\": \"Hello! I'm your travel planning assistant ...\", \"type
\": \"ai\"}}]}, \"kwargs\": {\"tags\": []}}",
"role": "assistant"
}
]
}
}
}

Execute tool span
The traceloop.span.kind attribute (tool) identiﬁes this as an execute tool span;
gen_ai.tool.name holds the tool name and gen_ai.operation.name = execute_tool.
{
"traceId": "6a01eefa5c52f3d86a35038f35f5ba30",
"spanId": "5b332f3cd15ace04",
"parentSpanId": "922a21edc04eba29",
"name": "execute_tool search_flights",
"kind": "INTERNAL",
"scope": {
"name": "opentelemetry.instrumentation.langchain",
"version": "0.60.0"
},
"startTimeUnixNano": 1778511614892698232,
"endTimeUnixNano": 1778511614893399618,
"durationNano": 701386,
"attributes": {
"traceloop.span.kind": "tool",
"gen_ai.operation.name": "execute_tool",
"gen_ai.tool.name": "search_flights",
LangGraph

2183

"gen_ai.tool.type": "function",
"gen_ai.tool.description": "Search for available flights between cities.",
"gen_ai.provider.name": "langgraph",
"traceloop.workflow.name": "travel_agent",
"session.id": "sea-nyc-trip-2-turns-adot_v17_opentelemetry_0_60_0"
},
"status": {
"code": "OK"
}
}

The correlated event record carries the tool input (arguments) and output (result, serialized as a
LangChain ToolMessage).
{
"spanId": "5b332f3cd15ace04",
"traceId": "6a01eefa5c52f3d86a35038f35f5ba30",
"scope": {
"name": "opentelemetry.instrumentation.langchain"
},
"body": {
"input": {
"messages": [
{ "content": "{\"origin\": \"SEA\", \"destination\": \"NYC\", \"date\":
\"2025-03-15\"}" }
]
},
"output": {
"messages": [
{
"role": "tool",
"name": "search_flights",
"content": "{\"origin\": \"SEA\", \"destination\": \"NYC\", \"flights\":
[ ... ]}"
}
]
}
}
}

LangGraph

2184

OpenInference
With the OpenInference library, the span type is carried in the openinference.span.kind
attribute, and the agent input and output are serialized in the correlated event record.
Example
Invoke agent span
The openinference.span.kind attribute (CHAIN, or AGENT when the graph is compiled with
a name) identiﬁes this as an invoke agent span.
{
"traceId": "6a387ee61078243c1cc455ed45c6c313",
"spanId": "0a7990d804132a9b",
"parentSpanId": "29ae22014173881c",
"name": "LangGraph",
"kind": "INTERNAL",
"scope": {
"name": "openinference.instrumentation.langchain",
"version": "0.1.66"
},
"startTimeUnixNano": 1782087405949310976,
"endTimeUnixNano": 1782087408945828864,
"durationNano": 2996517888,
"attributes": {
"openinference.span.kind": "CHAIN",
"input.mime_type": "application/json",
"output.mime_type": "application/json",
"llm.input_messages.0.message.role": "user",
"session.id": "sea-nyc-trip-2-turns-oi-0-1-66"
},
"status": {
"code": "OK"
}
}

The correlated event record carries the conversation. The user prompt is the human-role
message and the agent response is the AI-role message in the serialized messages.
{
"spanId": "0a7990d804132a9b",
"traceId": "6a387ee61078243c1cc455ed45c6c313",
LangGraph

2185

"scope": {
"name": "openinference.instrumentation.langchain"
},
"body": {
"input": {
"messages": [
{
"role": "user",
"content": "{\"messages\": [{\"role\": \"user\", \"content\": \"Hey, how
can you help me\"}]}"
}
]
},
"output": {
"messages": [
{
"content": "{\"messages\": [{\"type\": \"human\", \"data\": {\"content\":
\"Hey, how can you help me\", ...}}, {\"type\": \"ai\", \"data\": {\"content\":
\"Hello! I'm your travel planning assistant ...\", ...}}]}",
"role": "assistant"
}
]
}
}
}

Execute tool span
The openinference.span.kind attribute (TOOL) identiﬁes this as an execute tool span;
tool.name holds the tool name.
{
"traceId": "6a387ef07b8f4f3732fab45d3c0b51ff",
"spanId": "ab105c12cc40048f",
"parentSpanId": "9b2d4e72760690b4",
"name": "search_flights",
"kind": "INTERNAL",
"scope": {
"name": "openinference.instrumentation.langchain",
"version": "0.1.66"
},
"startTimeUnixNano": 1782087411724620032,
"endTimeUnixNano": 1782087411725306880,
LangGraph

2186

"durationNano": 686848,
"attributes": {
"openinference.span.kind": "TOOL",
"tool.name": "search_flights",
"tool.description": "Search for available flights between cities.",
"input.mime_type": "application/json",
"output.mime_type": "application/json",
"session.id": "sea-nyc-trip-2-turns-oi-0-1-66"
},
"status": {
"code": "OK"
}
}

The correlated event record carries the tool input (arguments) and output (result, serialized as a
LangChain ToolMessage).
{
"spanId": "ab105c12cc40048f",
"traceId": "6a387ef07b8f4f3732fab45d3c0b51ff",
"scope": {
"name": "openinference.instrumentation.langchain"
},
"body": {
"input": {
"messages": [
{
"role": "user",
"content": "{\"origin\": \"SEA\", \"destination\": \"NYC\", \"date\":
\"2025-03-15\"}"
}
]
},
"output": {
"messages": [
{
"content": "{\"type\": \"tool\", \"data\": {\"content\": \"{\\
\"origin\\\": \\\"SEA\\\", \\\"destination\\\": \\\"NYC\\\", \\\"flights\\\":
[ ... ]}\", \"type\": \"tool\", \"name\": \"search_flights\", \"tool_call_id\":
\"toolu_bdrk_01LzXXJCfpfuS7Bpf7e1qLMg\", \"status\": \"success\"}}",
"role": "assistant"
}
]
LangGraph

2187

}
}
}

Example spans in uniﬁed telemetry
With uniﬁed telemetry, the same content stays on the span attributes and no separate event record
is produced. The following examples are from a Python LangGraph travel-planning agent. The
same agent is shown under each instrumentation library.

Note
These examples are not complete spans. They show representative data from a real agent
interaction, with some ﬁelds omitted and long values truncated for readability.

OpenTelemetry
Example
Invoke agent span
The gen_ai.task.input attribute holds the user prompt, and the gen_ai.task.output
attribute holds the serialized state with the agent response. Both are the serialized LangChain
graph state.
{
"traceId": "6a4de7b85e61747e6b568a1f4768e89d",
"spanId": "31ea3d5882dac680",
"name": "LangGraph.workflow",
"kind": "INTERNAL",
"scope": {
"name": "opentelemetry.instrumentation.langchain",
"version": "0.62.1"
},
"attributes": {
"traceloop.span.kind": "workflow",
"gen_ai.operation.name": "invoke_agent",
"gen_ai.agent.name": "LangGraph",

LangGraph

2188

"gen_ai.task.input": "{\"inputs\": {\"messages\": [{\"role\": \"user\",
\"content\": \"Hey, how can you help me\"}]}, \"tags\": [], \"metadata\": { ... },
\"kwargs\": {\"name\": \"LangGraph\"}}",
"gen_ai.task.output": "{\"outputs\": {\"messages\": [{\"lc\": 1, \"type\":
\"constructor\", \"id\": [\"langchain\", \"schema\", \"messages\", \"HumanMessage
\"], \"kwargs\": {\"content\": \"Hey, how can you help me\", \"type\": \"human
\"}}, {\"lc\": 1, \"type\": \"constructor\", \"id\": [\"langchain\", \"schema\",
\"messages\", \"AIMessage\"], \"kwargs\": {\"content\": \"Hello! I'm your travel
planning assistant ...\", \"type\": \"ai\"}}]}, \"kwargs\": {\"tags\": []}}",
"session.id": "sea-nyc-trip-2-turns-unified"
},
"status": {
"code": "OK"
}
}

Execute tool span
The gen_ai.tool.call.arguments attribute holds the tool arguments, and the
gen_ai.tool.call.result attribute holds the tool result, serialized as a LangChain
ToolMessage.
{
"traceId": "6a4de7c376913db82e6f0f336a16731d",
"spanId": "b64c37adefae74f0",
"name": "execute_tool search_flights",
"kind": "INTERNAL",
"scope": {
"name": "opentelemetry.instrumentation.langchain",
"version": "0.62.1"
},
"attributes": {
"traceloop.span.kind": "tool",
"gen_ai.operation.name": "execute_tool",
"gen_ai.tool.name": "search_flights",
"gen_ai.tool.description": "Search for available flights between cities.",
"gen_ai.tool.call.arguments": "{\"input_str\": \"{'origin': 'SEA',
'destination': 'NYC', 'date': '2025-03-15'}\", \"inputs\": {\"origin\": \"SEA\",
\"destination\": \"NYC\", \"date\": \"2025-03-15\"}, \"metadata\": { ... }}",
"gen_ai.tool.call.result": "{\"output\": {\"lc\": 1, \"type\": \"constructor
\", \"id\": [\"langchain\", \"schema\", \"messages\", \"ToolMessage\"], \"kwargs
\": {\"content\": \"{\\\"origin\\\": \\\"SEA\\\", \\\"destination\\\": \\\"NYC\\

LangGraph

2189

\", \\\"flights\\\": [ ... ]}\", \"type\": \"tool\", \"name\": \"search_flights\",
\"status\": \"success\"}}}",
"session.id": "sea-nyc-trip-2-turns-unified"
},
"status": {
"code": "OK"
}
}

OpenInference
Example
Invoke agent span
The input.value attribute holds the user prompt, and the output.value attribute holds the
serialized state with the agent response.
{
"traceId": "6a387ee61078243c1cc455ed45c6c313",
"spanId": "b8c0b67876b78b91",
"name": "LangGraph",
"kind": "INTERNAL",
"scope": {
"name": "openinference.instrumentation.langchain",
"version": "0.1.66"
},
"attributes": {
"openinference.span.kind": "CHAIN",
"input.value": "{\"messages\": [{\"role\": \"user\", \"content\": \"Hey, how can
you help me\"}]}",
"output.value": "{\"messages\": [{\"type\": \"human\", \"data\": {\"content\":
\"Hey, how can you help me\"}}, {\"type\": \"ai\", \"data\": {\"content\": \"Hello!
I'm your travel planning assistant ...\"}}]}",
"session.id": "sea-nyc-trip-2-turns-oi-0-1-66"
},
"status": {
"code": "OK"
}
}

LangGraph

2190

Execute tool span
The input.value attribute holds the tool arguments, and the output.value attribute holds
the tool result, serialized as a LangChain ToolMessage.
{
"traceId": "6a387ef07b8f4f3732fab45d3c0b51ff",
"spanId": "58752612d9b22ae1",
"name": "search_flights",
"kind": "INTERNAL",
"scope": {
"name": "openinference.instrumentation.langchain",
"version": "0.1.66"
},
"attributes": {
"openinference.span.kind": "TOOL",
"tool.name": "search_flights",
"tool.description": "Search for available flights between cities.",
"input.value": "{\"origin\": \"SEA\", \"destination\": \"NYC\", \"date\":
\"2025-03-15\"}",
"output.value": "{\"type\": \"tool\", \"data\": {\"content\": \"{\\\"origin\\\":
\\\"SEA\\\", \\\"destination\\\": \\\"NYC\\\", \\\"flights\\\": [ ... ]}\", \"name
\": \"search_flights\"}}",
"session.id": "sea-nyc-trip-2-turns-oi-0-1-66"
},
"status": {
"code": "OK"
}
}

TypeScript agent support
A TypeScript LangGraph agent emits the same span types as a Python agent, so the evaluation
service reads it the same way. There are three TypeScript instrumentation libraries, each with its
own scope name and span-classiﬁcation convention.
Instrument your agent
Add the instrumentation library for the path you want to your TypeScript dependencies. The
following examples pin a minimum version; use the latest available version unless you have a
reason to pin.
LangGraph

2191

Example
ADOT (OpenTelemetry)
For TypeScript agents on ADOT, add the AWS Distro Node autoinstrumentation package (@aws/
aws-distro-opentelemetry-node-autoinstrumentation) to your dependencies. It
includes the built-in LangChain instrumentation, which activates at startup and emits the scope
name @aws/aws-distro-opentelemetry-instrumentation-langchain.
package.json:
{
"dependencies": {
"@aws/aws-distro-opentelemetry-node-autoinstrumentation": "^0.12.0"
}
}

Traceloop (OpenTelemetry)
Add the Traceloop LangChain instrumentation (@traceloop/instrumentation-langchain)
to your dependencies. The scope name emitted is @traceloop/instrumentationlangchain.
package.json:
{
"dependencies": {
"@traceloop/instrumentation-langchain": "^0.27.0"
}
}

OpenInference
Add @arizeai/openinference-instrumentation-langchain to your dependencies. The
scope name emitted is @arizeai/openinference-instrumentation-langchain.
package.json:
{
"dependencies": {
"@arizeai/openinference-instrumentation-langchain": "^4.0.14"
LangGraph

2192

}
}

Note
Instrumentation is one step in setting up observability. To export telemetry for evaluation,
complete the full setup in Set up observability.

How spans are identiﬁed
Span identiﬁcation depends on the instrumentation library:
• ADOT (OpenTelemetry): the AWS Distro Node autoinstrumentation package (@aws/
aws-distro-opentelemetry-node-autoinstrumentation), which emits the scope
name @aws/aws-distro-opentelemetry-instrumentation-langchain, sets
gen_ai.operation.name (invoke_agent, execute_tool, chat), the same as the other
ADOT-native frameworks.
• Traceloop (OpenTelemetry): the OpenTelemetry JS library from Traceloop (@traceloop/
instrumentation-langchain) sets traceloop.span.kind (workflow for the invoke agent
span, task for the tool span), matching the Python OpenTelemetry library. See How spans are
identiﬁed under Python agent support.
• OpenInference: the OpenInference JS library (@arizeai/openinferenceinstrumentation-langchain) sets openinference.span.kind (CHAIN or AGENT, TOOL,
LLM), the same as the Python OpenInference library.
How evaluation ﬁelds are extracted
Field extraction depends on the instrumentation library:
• ADOT (OpenTelemetry): the invoke agent span is a structural container, and the conversation
content lives on the inference (chat) span, in the parts-format gen_ai.input.messages and
gen_ai.output.messages attributes.
• Traceloop (OpenTelemetry): with the OpenTelemetry JS library from Traceloop, the
conversation is in the traceloop.entity.input and traceloop.entity.output
attributes, as serialized LangChain state. This matches the Python OpenTelemetry library; see
How evaluation ﬁelds are extracted under Python agent support.
LangGraph

2193

• OpenInference: with the OpenInference JS library, the conversation is in the input.value
and output.value attributes, and inference messages also appear on the indexed
llm.input_messages.* and llm.output_messages.* attributes. This matches the Python
OpenInference library.
Example spans from a TypeScript agent
The following examples are from a TypeScript LangGraph travel-planning agent deployed on
Amazon Bedrock AgentCore Runtime with uniﬁed telemetry. The same agent is shown under each
of the three TypeScript instrumentation libraries.
Note
These examples are not complete spans. They show representative data from a real agent
interaction, with some ﬁelds omitted and long values truncated for readability.

OpenTelemetry (ADOT native)
With the ADOT-native library (from the AWS Distro Node autoinstrumentation package @aws/
aws-distro-opentelemetry-node-autoinstrumentation, emitting the scope name @aws/
aws-distro-opentelemetry-instrumentation-langchain), the invoke agent span is a
structural container and the conversation content lives on the inference (chat) span, in the partsformat gen_ai.input.messages and gen_ai.output.messages attributes.
Example
Invoke agent span
The gen_ai.operation.name attribute (invoke_agent) identiﬁes this as an invoke agent
span. The span carries the agent name and model but no conversation content.
{
"traceId": "6a6bd0a1c8d91ed1e70a3906b551618",
"spanId": "ba1833fa7f097041",
"name": "invoke_agent LangGraph",
"kind": "INTERNAL",
"scope": {
"name": "@aws/aws-distro-opentelemetry-instrumentation-langchain",
"version": "0.12.0"
LangGraph

2194

},
"attributes": {
"gen_ai.operation.name": "invoke_agent",
"gen_ai.agent.name": "LangGraph",
"gen_ai.provider.name": "openai",
"gen_ai.request.model": "gpt-4o-mini",
"session.id": "sea-nyc-trip-2-turns"
},
"status": {
"code": "OK"
}
}

Execute tool span
The gen_ai.operation.name attribute (execute_tool) identiﬁes this as an execute tool
span; gen_ai.tool.name holds the tool name. The gen_ai.tool.call.arguments and
gen_ai.tool.call.result attributes hold the tool arguments and result.
{
"traceId": "6a6bd0a25c52f3d86a35038f35f5ba30",
"spanId": "5b332f3cd15ace04",
"name": "execute_tool search_flights",
"kind": "INTERNAL",
"scope": {
"name": "@aws/aws-distro-opentelemetry-instrumentation-langchain",
"version": "0.12.0"
},
"attributes": {
"gen_ai.operation.name": "execute_tool",
"gen_ai.tool.name": "search_flights",
"gen_ai.tool.type": "function",
"gen_ai.tool.call.arguments": "{\"origin\": \"SEA\", \"destination\": \"NYC\",
\"date\": \"2025-03-15\"}",
"gen_ai.tool.call.result": "{\"origin\": \"SEA\", \"destination\": \"NYC\",
\"flights\": [ ... ]}",
"session.id": "sea-nyc-trip-2-turns"
},
"status": {
"code": "OK"
}
}

LangGraph

2195

Inference span
The gen_ai.operation.name attribute (chat) identiﬁes this as an inference span. The
gen_ai.input.messages and gen_ai.output.messages attributes hold the conversation
in the parts-format, and gen_ai.system_instructions holds the system prompt.
{
"traceId": "6a6bd0a1c8d91ed1e70a3906b551618",
"spanId": "7c1f9a2b4d6e8a03",
"name": "chat gpt-4o-mini",
"kind": "INTERNAL",
"scope": {
"name": "@aws/aws-distro-opentelemetry-instrumentation-langchain",
"version": "0.12.0"
},
"attributes": {
"gen_ai.operation.name": "chat",
"gen_ai.provider.name": "openai",
"gen_ai.request.model": "gpt-4o-mini",
"gen_ai.input.messages": "[{\"role\": \"user\", \"parts\": [{\"type\": \"text\",
\"content\": \"Hey, how can you help me\"}]}]",
"gen_ai.output.messages": "[{\"role\": \"assistant\", \"parts\": [{\"type\":
\"text\", \"content\": \"I can assist you with planning your trip ...\"}]}]",
"gen_ai.system_instructions": "[{\"type\": \"text\", \"content\": \"You are a
travel planning assistant ...\"}]",
"session.id": "sea-nyc-trip-2-turns"
},
"status": {
"code": "OK"
}
}

OpenTelemetry (Traceloop)
With the OpenTelemetry JS library from Traceloop (@traceloop/instrumentationlangchain), the span type is carried in the traceloop.span.kind attribute (workflow for
the invoke agent span, task for the tool span), and gen_ai.operation.name = workflow
on the invoke agent span. The conversation is in the traceloop.entity.input and
traceloop.entity.output attributes, as serialized LangChain state.

LangGraph

2196

Example
Invoke agent span
The traceloop.span.kind attribute (workflow) identiﬁes this as an invoke agent span.
The traceloop.entity.input and traceloop.entity.output attributes hold the
serialized LangChain state, from which the user prompt (human message) and agent response
(AI message) are parsed.
{
"traceId": "6a6bd0b1c8d91ed1e70a3906b551618",
"spanId": "ba1833fa7f097041",
"name": "workflow RunnableSequence",
"kind": "INTERNAL",
"scope": {
"name": "@traceloop/instrumentation-langchain",
"version": "0.27.0"
},
"attributes": {
"traceloop.span.kind": "workflow",
"gen_ai.operation.name": "workflow",
"gen_ai.provider.name": "langchain",
"traceloop.workflow.name": "RunnableSequence",
"traceloop.entity.input": "{\"messages\": [{\"lc\": 1, \"type\": \"constructor
\", \"id\": [\"langchain_core\", \"messages\", \"HumanMessage\"], \"kwargs\":
{\"content\": \"Hey, how can you help me\"}}]}",
"traceloop.entity.output": "{\"messages\": [{\"lc\": 1, \"type\": \"constructor
\", \"id\": [\"langchain_core\", \"messages\", \"AIMessage\"], \"kwargs\":
{\"content\": \"I can assist you with planning your trip ...\"}}]}",
"session.id": "sea-nyc-trip-2-turns"
},
"status": {
"code": "OK"
}
}

Execute tool span
The traceloop.span.kind attribute (task) identiﬁes this as an execute tool span. The
traceloop.entity.input and traceloop.entity.output attributes hold the tool
arguments and result.

LangGraph

2197

{
"traceId": "6a6bd0b25c52f3d86a35038f35f5ba30",
"spanId": "5b332f3cd15ace04",
"name": "task search_flights",
"kind": "INTERNAL",
"scope": {
"name": "@traceloop/instrumentation-langchain",
"version": "0.27.0"
},
"attributes": {
"traceloop.span.kind": "task",
"traceloop.entity.name": "search_flights",
"traceloop.entity.input": "{\"origin\": \"SEA\", \"destination\": \"NYC\",
\"date\": \"2025-03-15\"}",
"traceloop.entity.output": "{\"output\": {\"lc\": 1, \"type\": \"constructor\",
\"id\": [\"langchain_core\", \"messages\", \"ToolMessage\"], \"kwargs\": {\"status
\": \"success\", \"content\": \"{\\\"origin\\\": \\\"SEA\\\", \\\"destination\\\": \
\\"NYC\\\", \\\"flights\\\": [ ... ]}\"}}}",
"session.id": "sea-nyc-trip-2-turns"
},
"status": {
"code": "OK"
}
}

OpenInference
With the OpenInference JS library (@arizeai/openinference-instrumentationlangchain), the span type is carried in the openinference.span.kind attribute. The
conversation content is in the input.value and output.value attributes, and inference
messages also appear on the indexed llm.input_messages.* and llm.output_messages.*
attributes.
Example
Invoke agent span
The openinference.span.kind attribute (CHAIN) identiﬁes this as an invoke agent span.
The input.value and output.value attributes hold the serialized LangChain state.
{
LangGraph

2198

"traceId": "6a6bd0c1c8d91ed1e70a3906b551618",
"spanId": "0a7990d804132a9b",
"name": "LangGraph",
"kind": "INTERNAL",
"scope": {
"name": "@arizeai/openinference-instrumentation-langchain",
"version": "4.0.14"
},
"attributes": {
"openinference.span.kind": "CHAIN",
"input.value": "{\"messages\": [{\"lc\": 1, \"type\": \"constructor\", \"id\":
[\"langchain_core\", \"messages\", \"HumanMessage\"], \"kwargs\": {\"content\":
\"Hey, how can you help me\"}}]}",
"output.value": "{\"messages\": [{\"lc\": 1, \"type\": \"constructor\", \"id\":
[\"langchain_core\", \"messages\", \"AIMessage\"], \"kwargs\": {\"content\": \"I
can assist you with planning your trip ...\"}}]}",
"session.id": "sea-nyc-trip-2-turns"
},
"status": {
"code": "OK"
}
}

Execute tool span
The openinference.span.kind attribute (TOOL) identiﬁes this as an execute tool span;
tool.name holds the tool name. The input.value and output.value attributes hold the
tool arguments and result (serialized as a LangChain ToolMessage).
{
"traceId": "6a6bd0c25c52f3d86a35038f35f5ba30",
"spanId": "ab105c12cc40048f",
"name": "search_flights",
"kind": "INTERNAL",
"scope": {
"name": "@arizeai/openinference-instrumentation-langchain",
"version": "4.0.14"
},
"attributes": {
"openinference.span.kind": "TOOL",
"tool.name": "search_flights",
"input.value": "{\"origin\": \"SEA\", \"destination\": \"NYC\", \"date\":
\"2025-03-15\"}",
LangGraph

2199

"output.value": "{\"output\": {\"lc\": 1, \"type\": \"constructor\", \"id\":
[\"langchain_core\", \"messages\", \"ToolMessage\"], \"kwargs\": {\"status\":
\"success\", \"content\": \"{\\\"origin\\\": \\\"SEA\\\", \\\"destination\\\": \\
\"NYC\\\", \\\"flights\\\": [ ... ]}\"}}}",
"session.id": "sea-nyc-trip-2-turns"
},
"status": {
"code": "OK"
}
}

Inference span
The openinference.span.kind attribute (LLM) identiﬁes this as an inference span. The
llm.input_messages.* attributes hold the system prompt and user prompt, and the
llm.output_messages.* attributes hold the agent response.
{
"traceId": "6a6bd0c1c8d91ed1e70a3906b551618",
"spanId": "1221a062c7f90a8e",
"name": "ChatOpenAI",
"kind": "INTERNAL",
"scope": {
"name": "@arizeai/openinference-instrumentation-langchain",
"version": "4.0.14"
},
"attributes": {
"openinference.span.kind": "LLM",
"llm.model_name": "gpt-4o-mini",
"llm.input_messages.0.message.role": "system",
"llm.input_messages.0.message.content": "You are a travel planning
assistant ...",
"llm.input_messages.1.message.role": "user",
"llm.input_messages.1.message.content": "Hey, how can you help me",
"llm.output_messages.0.message.role": "assistant",
"llm.output_messages.0.message.content": "I can assist you with planning your
trip ...",
"session.id": "sea-nyc-trip-2-turns"
},
"status": {
"code": "OK"
}
}

LangGraph

2200

Best practices for LangGraph agents
How you build and invoke a LangGraph agent aﬀects what appears in its telemetry, and therefore
how reliably the agent can be evaluated. The following practices help ensure the user prompt,
agent response, and tool activity are recoverable.
1. Choose an agent construction pattern
There are two common ways to build a LangGraph agent:
• Prebuilt create_agent : the quickest way to get started. It produces a single invoke agent span
per turn, with the conversation passed through LangGraph’s built-in execution loop. Use this
when you want a standard reason-act agent without custom control ﬂow.
from langchain.agents import create_agent
agent = create_agent(model=model, tools=[search_flights, book_flight])

• Custom StateGraph : gives you full control over nodes, edges, and conditional routing. Each
node execution becomes its own span, so traces are more granular. Use this when you need
custom orchestration.
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
class State(TypedDict):
messages: list
graph = StateGraph(State)
graph.add_node("generate_response", generate_response)
graph.add_node("tools", run_tools)
graph.add_edge(START, "generate_response")
agent = graph.compile()

Both patterns are evaluated the same way; the diﬀerence is the granularity of the trace.
2. Use messages in your graph State (recommended)
The evaluation service reconstructs the conversation from the agent’s input and output messages.
Using a messages ﬁeld is not mandatory, but it enables the most reliable extraction. For a custom
StateGraph, keep the conversation in a messages ﬁeld in your State:
LangGraph

2201


## OpenAI Agents (pp. 2202–2225)

• Include messages in your State (recommended). You can add other custom ﬁelds (such
as user_id or metadata). When messages is present, the standard extraction ﬁnds the
user prompt and agent response directly. If messages is absent, the service falls back to
reconstructing the conversation from individual inference spans, which is less reliable.
• Append, don’t replace. Follow the LangGraph convention of appending new messages to the list
rather than overwriting it, so the full conversation history is preserved.
• Use canonical LangChain message types (HumanMessage, AIMessage, ToolMessage,
SystemMessage). The instrumentation serializes these correctly, and the service recognizes their
roles.
3. Pass the user message in a supported format
When you invoke a LangGraph agent, you add the user message to the graph’s messages state.
LangGraph accepts the message in three interchangeable formats, and AgentCore Evaluations
supports all of them. Each produces spans and event records that the service can read.
• Tuple: a (role, content) pair:
agent.invoke({"messages": [("user", user_message)]}, config=config)

• LangChain message object: a HumanMessage (or other message class):
from langchain_core.messages import HumanMessage
agent.invoke({"messages": [HumanMessage(content=user_message)]}, config=config)

• Dictionary: a {"role", "content"} dictionary:
agent.invoke({"messages": [{"role": "user", "content": user_message}]},
config=config)

All three formats result in the same messages state, so the user prompt and agent response are
extracted identically regardless of which you choose.

OpenAI Agents
This page explains how to instrument an OpenAI Agents agent, how spans are identiﬁed, and how
evaluation ﬁelds are extracted. AgentCore Evaluations supports OpenAI Agents built in Python and
OpenAI Agents

2202

TypeScript; this page covers each language separately, in Python agent support and TypeScript
agent support.
Topics
• Python agent support
• Instrument your agent
• How spans are identiﬁed
• How evaluation ﬁelds are extracted
• From event records
• From span attributes
• Example spans in split telemetry
• Example spans in uniﬁed telemetry
• TypeScript agent support
• Instrument your agent
• How spans are identiﬁed
• How evaluation ﬁelds are extracted
• Example spans from a TypeScript agent

Python agent support
A Python OpenAI Agents agent emits spans under the scope name
opentelemetry.instrumentation.openai_agents (OpenTelemetry) or
openinference.instrumentation.openai_agents (OpenInference).
Instrument your agent
You can instrument an OpenAI Agents agent with either of two instrumentation libraries:
OpenTelemetry (opentelemetry-instrumentation-openai-agents) or OpenInference
(openinference-instrumentation-openai-agents). Amazon Bedrock AgentCore
Evaluations supports both libraries. The libraries emit diﬀerent scope names and use diﬀerent span
attributes. The evaluation service extracts the same values from each.
When your agent runs with the AWS Distro for OpenTelemetry (ADOT), such as on Amazon
Bedrock AgentCore Runtime, you do not need to add explicit instrumentation code. Adding the
OpenAI Agents

2203

instrumentation library to your project’s dependencies is enough. ADOT discovers it at startup and
activates it automatically.
Add the instrumentation library for the path you want to your dependencies. Use the latest
available version unless you have a reason to pin.
Example
OpenTelemetry
NOTE: Use version 0.61.0 or later. This is the earliest version tested with the evaluation
service.
Add opentelemetry-instrumentation-openai-agents to your dependencies. The scope
name emitted is opentelemetry.instrumentation.openai_agents.
requirements.txt:
opentelemetry-instrumentation-openai-agents>=0.61.0

pyproject.toml:
[project]
dependencies = [
"opentelemetry-instrumentation-openai-agents>=0.61.0",
]

OpenInference
NOTE: Use version 1.5.0 or later. This is the earliest version tested with the evaluation service.
Add openinference-instrumentation-openai-agents to your dependencies. The scope
name emitted is openinference.instrumentation.openai_agents.
requirements.txt:
openinference-instrumentation-openai-agents>=1.5.0

pyproject.toml:
[project]
dependencies = [
OpenAI Agents

2204

"openinference-instrumentation-openai-agents>=1.5.0",
]

Note
Instrumentation is one step in setting up observability. To export telemetry for evaluation,
complete the full setup in Set up observability.

How spans are identiﬁed
The attribute used to classify spans diﬀers between the two instrumentation libraries.
Example
OpenTelemetry
The OpenTelemetry instrumentation library classiﬁes spans using the
gen_ai.operation.name attribute.
Span type

Identifying attribute

Invoke agent

gen_ai.operation.name

= invoke_agent

Execute tool

gen_ai.operation.name

= execute_tool

Inference

gen_ai.operation.name

= chat

Note
OpenAI Agents also emits internal turn-boundary spans with
gen_ai.operation.name = unknown. The evaluation service skips these.

OpenInference
The OpenInference instrumentation library classiﬁes spans using the
openinference.span.kind attribute.
OpenAI Agents

2205

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

Note
With the OpenInference library, the AGENT and CHAIN spans are empty structural
containers: they carry no conversation content. The user prompt and agent response are
reconstructed from the inference (LLM) spans in the same trace.

How evaluation ﬁelds are extracted
OpenAI Agents serializes messages in a parts-based format, in which each message carries
a parts array of typed content blocks (for example, [{"role": "user", "parts":
[{"type": "text", "content": "…"}]}] ). With the OpenTelemetry library, AgentCore
Evaluations parses the text out of these parts. With the OpenInference library, the model output
is the full OpenAI Response object, and AgentCore Evaluations reads the response text from
output[].content[].text.
The location of this content depends on how telemetry was collected. The identifying attribute
(gen_ai.operation.name or openinference.span.kind) is on the span in both cases. For
more information, see Telemetry setup and delivery.
From event records
With split telemetry, AgentCore Evaluations reads conversation content from the event record
correlated to each span. The location of tool inputs and outputs diﬀers between the two libraries:
• OpenTelemetry:
• User prompt and agent response: from the invoke agent span’s event record, in body.input
and body.output.
• Tool call: the tool name from gen_ai.tool.name, and the arguments and result from
gen_ai.tool.call.arguments and gen_ai.tool.call.result on the execute tool
OpenAI Agents

2206

span. With the OpenTelemetry library, tool arguments and results remain on the span
attributes even with split telemetry.
• OpenInference:
• User prompt and agent response: reconstructed from the inference span’s event record.
AgentCore Evaluations reads the messages from body.input and body.output, then
backﬁlls the empty invoke agent span with the user prompt and agent response.
• Tool call: the tool name from tool.name on the execute tool span. The tool arguments and
result come from that span’s event record, in body.input and body.output.
For more information, see Example spans in split telemetry.
From span attributes
With uniﬁed telemetry, the same content stays on the span as attributes. The attributes depend on
the instrumentation library:
• OpenTelemetry:
• User prompt and agent response: from gen_ai.input.messages and
gen_ai.output.messages on the invoke agent span.
• Tool call: the tool name from gen_ai.tool.name, and the arguments and result from
gen_ai.tool.call.arguments and gen_ai.tool.call.result, on the execute tool
span.
• OpenInference:
• User prompt and agent response: from the indexed message attributes on the inference span
(llm.input_messages.* and llm.output_messages.*), then backﬁlled onto the empty
invoke agent span.
• Tool call: the tool name from tool.name, and the arguments and result from input.value
and output.value, on the execute tool span.
For more information, see Example spans in uniﬁed telemetry.
Example spans in split telemetry
With split telemetry, the span carries the identifying attributes and the content lives in a
correlated event record. The following examples are from a Python OpenAI Agents travel-planning
OpenAI Agents

2207

agent deployed on Amazon Bedrock AgentCore Runtime. The same agent is shown under each
instrumentation library.

Note
These examples are not complete spans. They show representative data from a real agent
interaction, with some ﬁelds omitted and long values truncated for readability.

OpenTelemetry
Example
Invoke agent span
The gen_ai.operation.name attribute (invoke_agent) identiﬁes this as an invoke agent
span.
{
"traceId": "6a01eef11066751d68f90def0da1f80a",
"spanId": "3a300b0b3fe650e4",
"name": "invoke_agent openaiOtelTravel",
"kind": "INTERNAL",
"scope": {
"name": "opentelemetry.instrumentation.openai_agents",
"version": "0.62.1"
},
"attributes": {
"gen_ai.operation.name": "invoke_agent",
"gen_ai.agent.name": "openaiOtelTravel",
"gen_ai.system": "openai",
"gen_ai.provider.name": "openai",
"gen_ai.request.model": "gpt-4o-mini-2024-07-18",
"session.id": "sea-nyc-trip-2-turns-openai-otel"
},
"status": {
"code": "OK"
}
}

OpenAI Agents

2208

The correlated event record carries the conversation. Each message’s content is the OpenAI
parts-format array; the user prompt is the text of the user message and the agent response is
the text of the assistant message.
{
"spanId": "3a300b0b3fe650e4",
"traceId": "6a01eef11066751d68f90def0da1f80a",
"scope": {
"name": "opentelemetry.instrumentation.openai_agents"
},
"body": {
"input": {
"messages": [
{
"role": "user",
"content": "[{\"role\": \"user\", \"parts\": [{\"type\": \"text\",
\"content\": \"Hey, how can you help me\"}]}]"
}
]
},
"output": {
"messages": [
{
"role": "assistant",
"content": "[{\"role\": \"assistant\", \"parts\": [{\"type\": \"text\",
\"content\": \"I can assist you with planning your trips ...\"}]}]"
}
]
}
}
}

Execute tool span
The gen_ai.operation.name attribute (execute_tool) identiﬁes this as an execute tool
span; gen_ai.tool.name holds the tool name. With the OpenTelemetry library, the tool
arguments and result stay on the span attributes even with split telemetry.
{
"traceId": "6a01eefa5c52f3d86a35038f35f5ba30",
"spanId": "3cbc4ea5f73fef81",
"name": "execute_tool search_flights",
OpenAI Agents

2209

"kind": "INTERNAL",
"scope": {
"name": "opentelemetry.instrumentation.openai_agents",
"version": "0.62.1"
},
"attributes": {
"gen_ai.operation.name": "execute_tool",
"gen_ai.tool.name": "search_flights",
"gen_ai.tool.type": "function",
"gen_ai.tool.call.arguments": "{\"origin\": \"SEA\", \"destination\": \"NYC\",
\"date\": \"2025-03-15\"}",
"gen_ai.tool.call.result": "{\"origin\": \"SEA\", \"destination\": \"NYC\",
\"flights\": [ ... ]}",
"session.id": "sea-nyc-trip-2-turns-openai-otel"
},
"status": {
"code": "OK"
}
}

Inference span
The gen_ai.operation.name attribute (chat) identiﬁes this as an inference span. This span
carries the model metadata and, in gen_ai.tool.definitions, the list of tools available to
the agent. The conversation messages for the model call live in the correlated event record, in
body.input and body.output.
{
"traceId": "6a01eef11066751d68f90def0da1f80a",
"spanId": "7c1f9a2b4d6e8a03",
"name": "openai.response",
"kind": "INTERNAL",
"scope": {
"name": "opentelemetry.instrumentation.openai_agents",
"version": "0.62.1"
},
"attributes": {
"gen_ai.operation.name": "chat",
"gen_ai.provider.name": "openai",
"gen_ai.request.model": "gpt-4o-mini-2024-07-18",
"gen_ai.response.model": "gpt-4o-mini-2024-07-18",
"gen_ai.usage.input_tokens": 269,
"gen_ai.usage.output_tokens": 78,
OpenAI Agents

2210

"gen_ai.tool.definitions": "[{\"type\": \"function\", \"function\": {\"name\":
\"search_flights\", \"description\": \"Search for available flights between cities.
\", \"parameters\": { ... }}}]",
"session.id": "sea-nyc-trip-2-turns-openai-otel"
},
"status": {
"code": "OK"
}
}

{
"spanId": "7c1f9a2b4d6e8a03",
"traceId": "6a01eef11066751d68f90def0da1f80a",
"scope": {
"name": "opentelemetry.instrumentation.openai_agents"
},
"body": {
"input": {
"messages": [
{
"role": "user",
"content": "[{\"role\": \"user\", \"parts\": [{\"type\": \"text\",
\"content\": \"Hey, how can you help me\"}]}]"
}
]
},
"output": {
"messages": [
{
"role": "assistant",
"content": "[{\"role\": \"assistant\", \"parts\": [{\"type\": \"text\",
\"content\": \"I can assist you with planning your trips ...\"}]}]"
}
]
}
}
}

OpenAI Agents

2211

OpenInference
With the OpenInference library, the invoke agent (AGENT) span is an empty container. AgentCore
Evaluations reconstructs the user prompt and agent response from the inference (LLM) span, whose
content lives in a correlated event record.
Example
Invoke agent span
The openinference.span.kind attribute (AGENT) identiﬁes this as an invoke agent span.
The span carries no conversation content.
{
"traceId": "6a387ee61078243c1cc455ed45c6c313",
"spanId": "9a1c7dce81b692cd",
"name": "openaiOInfTravel",
"kind": "INTERNAL",
"scope": {
"name": "openinference.instrumentation.openai_agents",
"version": "1.5.0"
},
"attributes": {
"openinference.span.kind": "AGENT",
"graph.node.id": "openaiOInfTravel",
"llm.system": "openai",
"session.id": "sea-nyc-trip-2-turns-openai-oi"
},
"status": {
"code": "OK"
}
}

Execute tool span
The openinference.span.kind attribute (TOOL) identiﬁes this as an execute tool span;
tool.name holds the tool name. The tool arguments and result live in the correlated event
record.
{
"traceId": "6a387ef07b8f4f3732fab45d3c0b51ff",
"spanId": "b4e78cb0a06a6fe2",
"name": "search_flights",
OpenAI Agents

2212

"kind": "INTERNAL",
"scope": {
"name": "openinference.instrumentation.openai_agents",
"version": "1.5.0"
},
"attributes": {
"openinference.span.kind": "TOOL",
"tool.name": "search_flights",
"input.mime_type": "application/json",
"output.mime_type": "application/json",
"session.id": "sea-nyc-trip-2-turns-openai-oi"
},
"status": {
"code": "OK"
}
}

{
"spanId": "b4e78cb0a06a6fe2",
"traceId": "6a387ef07b8f4f3732fab45d3c0b51ff",
"scope": {
"name": "openinference.instrumentation.openai_agents"
},
"body": {
"input": {
"messages": [
{ "role": "user", "content": "{\"origin\": \"SEA\", \"destination\": \"NYC
\", \"date\": \"2025-03-15\"}" }
]
},
"output": {
"messages": [
{ "role": "assistant", "content": "{\"origin\": \"SEA\", \"destination\":
\"NYC\", \"flights\": [ ... ]}" }
]
}
}
}

Inference span
The openinference.span.kind attribute (LLM) identiﬁes this as an inference span. Message
roles and tool deﬁnitions are on the span attributes; the message content lives in the correlated
OpenAI Agents

2213

event record. ADOT ﬂattens the input roles to user, so AgentCore Evaluations uses the last
plain-text input message as the user prompt. The output message is the OpenAI Response
object, from which AgentCore Evaluations reads the response text.
{
"traceId": "6a387ee61078243c1cc455ed45c6c313",
"spanId": "1221a062c7f90a8e",
"name": "response",
"kind": "INTERNAL",
"scope": {
"name": "openinference.instrumentation.openai_agents",
"version": "1.5.0"
},
"attributes": {
"openinference.span.kind": "LLM",
"llm.model_name": "gpt-4o-mini-2024-07-18",
"llm.input_messages.0.message.role": "system",
"llm.input_messages.1.message.role": "user",
"llm.output_messages.0.message.role": "assistant",
"llm.tools.0.tool.json_schema": "{\"type\": \"function\", \"function\": {\"name
\": \"search_flights\", ...}}",
"session.id": "sea-nyc-trip-2-turns-openai-oi"
},
"status": {
"code": "OK"
}
}

{
"spanId": "1221a062c7f90a8e",
"traceId": "6a387ee61078243c1cc455ed45c6c313",
"scope": {
"name": "openinference.instrumentation.openai_agents"
},
"body": {
"input": {
"messages": [
{ "role": "user", "content": "[{\"content\": \"Hey, how can you help me\",
\"role\": \"user\"}]" },
{ "role": "user", "content": "You are a travel planning assistant. Help
users plan trips ..." },
{ "role": "user", "content": "Hey, how can you help me" }
]
OpenAI Agents

2214

},
"output": {
"messages": [
{
"role": "assistant",
"content": "{\"id\": \"resp_abc123...\", \"output\": [{\"type\": \"message
\", \"content\": [{\"type\": \"output_text\", \"text\": \"I can assist you with
planning your trips ...\"}]}]}"
}
]
}
}
}

Example spans in uniﬁed telemetry
With uniﬁed telemetry, the same content stays on the span attributes and no separate event record
is produced. The following examples are from a Python OpenAI Agents travel-planning agent. The
same agent is shown under each instrumentation library.
Note
These examples are not complete spans. They show representative data from a real agent
interaction, with some ﬁelds omitted and long values truncated for readability.

OpenTelemetry
Example
Invoke agent span
The gen_ai.input.messages attribute holds the user prompt, and the
gen_ai.output.messages attribute holds the agent response. Both are OpenAI parts-format
arrays.
{
"traceId": "6a4de7b85e61747e6b568a1f4768e89d",
"spanId": "50656fd77904d125",
"name": "invoke_agent openaiOtelTravel",
"kind": "INTERNAL",
OpenAI Agents

2215

"scope": {
"name": "opentelemetry.instrumentation.openai_agents",
"version": "0.62.1"
},
"attributes": {
"gen_ai.operation.name": "invoke_agent",
"gen_ai.agent.name": "openaiOtelTravel",
"gen_ai.system": "openai",
"gen_ai.input.messages": "[{\"role\": \"user\", \"parts\": [{\"type\": \"text\",
\"content\": \"Hey, how can you help me\"}]}]",
"gen_ai.output.messages": "[{\"role\": \"assistant\", \"parts\": [{\"type\":
\"text\", \"content\": \"I can assist you with planning your trips ...\"}]}]",
"session.id": "sea-nyc-trip-2-turns-unified"
},
"status": {
"code": "OK"
}
}

Execute tool span
The gen_ai.tool.call.arguments attribute holds the tool arguments, and the
gen_ai.tool.call.result attribute holds the tool result.
{
"traceId": "6a4de7c376913db82e6f0f336a16731d",
"spanId": "8840e8e23724ebd7",
"name": "execute_tool search_flights",
"kind": "INTERNAL",
"scope": {
"name": "opentelemetry.instrumentation.openai_agents",
"version": "0.62.1"
},
"attributes": {
"gen_ai.operation.name": "execute_tool",
"gen_ai.tool.name": "search_flights",
"gen_ai.tool.call.arguments": "{\"origin\": \"SEA\", \"destination\": \"NYC\",
\"date\": \"2025-03-15\"}",
"gen_ai.tool.call.result": "{\"origin\": \"SEA\", \"destination\": \"NYC\",
\"flights\": [ ... ]}",
"session.id": "sea-nyc-trip-2-turns-unified"
},
"status": {
OpenAI Agents

2216

"code": "OK"
}
}

Inference span
The gen_ai.operation.name attribute (chat) identiﬁes this as an inference span. The model
metadata and the gen_ai.tool.definitions attribute (the list of tools available to the
agent) stay inline on the span.
{
"traceId": "6a4de7b85e61747e6b568a1f4768e89d",
"spanId": "9b2c1e5f7a3d0846",
"name": "openai.response",
"kind": "INTERNAL",
"scope": {
"name": "opentelemetry.instrumentation.openai_agents",
"version": "0.62.1"
},
"attributes": {
"gen_ai.operation.name": "chat",
"gen_ai.provider.name": "openai",
"gen_ai.request.model": "gpt-4o-mini-2024-07-18",
"gen_ai.response.model": "gpt-4o-mini-2024-07-18",
"gen_ai.usage.input_tokens": 269,
"gen_ai.usage.output_tokens": 78,
"gen_ai.tool.definitions": "[{\"type\": \"function\", \"function\": {\"name\":
\"search_flights\", \"description\": \"Search for available flights between cities.
\", \"parameters\": { ... }}}]",
"session.id": "sea-nyc-trip-2-turns-unified"
},
"status": {
"code": "OK"
}
}

OpenAI Agents

2217

OpenInference
Example
Execute tool span
The input.value attribute holds the tool arguments, and the output.value attribute holds
the tool result.
{
"traceId": "6a387ef07b8f4f3732fab45d3c0b51ff",
"spanId": "d5a1c9e70b46f312",
"name": "search_flights",
"kind": "INTERNAL",
"scope": {
"name": "openinference.instrumentation.openai_agents",
"version": "1.5.1"
},
"attributes": {
"openinference.span.kind": "TOOL",
"tool.name": "search_flights",
"input.value": "{\"origin\": \"SEA\", \"destination\": \"NYC\", \"date\":
\"2025-03-15\"}",
"output.value": "{\"origin\": \"SEA\", \"destination\": \"NYC\", \"flights\":
[ ... ]}",
"session.id": "sea-nyc-trip-2-turns-oi"
},
"status": {
"code": "OK"
}
}

Inference span
The message content is inline on the indexed attributes. The llm.input_messages.*
attributes hold the system prompt and user prompt, and the llm.output_messages.*
attributes hold the agent response. AgentCore Evaluations reconstructs the user prompt and
agent response from this span and backﬁlls the empty invoke agent (AGENT) span.
{
"traceId": "6a387ee61078243c1cc455ed45c6c313",
"spanId": "c9f0a2b41d773e88",
"name": "response",
OpenAI Agents

2218

"kind": "INTERNAL",
"scope": {
"name": "openinference.instrumentation.openai_agents",
"version": "1.5.1"
},
"attributes": {
"openinference.span.kind": "LLM",
"llm.model_name": "gpt-4o-mini-2024-07-18",
"llm.input_messages.0.message.role": "system",
"llm.input_messages.0.message.content": "You are a travel planning
assistant ...",
"llm.input_messages.1.message.role": "user",
"llm.input_messages.1.message.content": "Hey, how can you help me",
"llm.output_messages.0.message.role": "assistant",
"llm.output_messages.0.message.contents.0.message_content.text": "I can assist
you with planning your trips ...",
"session.id": "sea-nyc-trip-2-turns-oi"
},
"status": {
"code": "OK"
}
}

TypeScript agent support
A TypeScript OpenAI Agents agent emits the same span types, identifying attributes, and content
layout as a Python agent, so the evaluation service reads it the same way. There are two TypeScript
instrumentation libraries, each with its own scope name.
Instrument your agent
Add the instrumentation library for the convention you want to your TypeScript dependencies. Use
the latest available version unless you have a reason to pin.
Example
ADOT (OpenTelemetry)
For TypeScript agents on ADOT, add the AWS Distro Node autoinstrumentation package (@aws/
aws-distro-opentelemetry-node-autoinstrumentation) to your dependencies. It
includes the built-in OpenAI Agents instrumentation, which activates at startup and emits the
scope name @aws/aws-distro-opentelemetry-instrumentation-openai-agents.
OpenAI Agents

2219

package.json:
{
"dependencies": {
"@aws/aws-distro-opentelemetry-node-autoinstrumentation": "^0.12.0"
}
}

OpenInference
Add @arizeai/openinference-instrumentation-openai-agents to your
dependencies. The scope name emitted is @arizeai/openinference-instrumentationopenai-agents.
package.json:
{
"dependencies": {
"@arizeai/openinference-instrumentation-openai-agents": "^0.2.2"
}
}

Note
Instrumentation is one step in setting up observability. To export telemetry for evaluation,
complete the full setup in Set up observability.

How spans are identiﬁed
Span identiﬁcation is the same as for a Python agent. The ADOT-native OpenTelemetry
library (from the AWS Distro Node autoinstrumentation package @aws/aws-distroopentelemetry-node-autoinstrumentation, emitting the scope name @aws/aws-distroopentelemetry-instrumentation-openai-agents) sets gen_ai.operation.name, and the
OpenInference JS library (@arizeai/openinference-instrumentation-openai-agents)
sets openinference.span.kind. For the values, see How spans are identiﬁed under Python
agent support.

OpenAI Agents

2220

How evaluation ﬁelds are extracted
Field extraction reads the same attributes as for a Python agent. Note that with the ADOT-native
TypeScript library, the invoke agent span is a structural container: the user prompt and agent
response are reconstructed from the inference (chat) span rather than the invoke agent span,
unlike the Python OpenTelemetry library, which keeps them on the invoke agent span. For where
each ﬁeld is read from, see How evaluation ﬁelds are extracted under Python agent support.
Example spans from a TypeScript agent
The following examples are from a TypeScript OpenAI Agents travel-planning agent deployed on
Amazon Bedrock AgentCore Runtime with uniﬁed telemetry. The same agent is shown under each
instrumentation library.
Note
These examples are not complete spans. They show representative data from a real agent
interaction, with some ﬁelds omitted and long values truncated for readability.

OpenTelemetry
With the ADOT-native library (from the AWS Distro Node autoinstrumentation package @aws/
aws-distro-opentelemetry-node-autoinstrumentation, emitting the scope name @aws/
aws-distro-opentelemetry-instrumentation-openai-agents), the invoke agent span
is a structural container and the conversation content lives on the inference (chat) span, in the
parts-format gen_ai.input.messages and gen_ai.output.messages attributes. AgentCore
Evaluations reconstructs the user prompt and agent response from the inference span.
Example
Invoke agent span
The gen_ai.operation.name attribute (invoke_agent) identiﬁes this as an invoke agent
span. The span carries the agent name and tool list but no conversation content.
{
"traceId": "6a6bc695459e41aa14a172bb41d3246d",
"spanId": "9a1c7dce81b692cd",
"name": "invoke_agent openaiAdotTS",
"kind": "INTERNAL",
OpenAI Agents

2221

"scope": {
"name": "@aws/aws-distro-opentelemetry-instrumentation-openai-agents",
"version": "0.12.0"
},
"attributes": {
"gen_ai.operation.name": "invoke_agent",
"gen_ai.agent.name": "openaiAdotTS",
"gen_ai.provider.name": "openai",
"open_ai.agent.tools": "[\"search_flights\", \"book_flight\", \"search_hotels\",
\"book_hotel\", \"search_activities\", \"book_activity\"]",
"session.id": "sea-nyc-trip-2-turns"
},
"status": {
"code": "OK"
}
}

Execute tool span
The gen_ai.operation.name attribute (execute_tool) identiﬁes this as an execute tool
span; gen_ai.tool.name holds the tool name. The gen_ai.tool.call.arguments and
gen_ai.tool.call.result attributes hold the tool arguments and result.
{
"traceId": "6a6bc695459e41aa14a172bb41d3246d",
"spanId": "3cbc4ea5f73fef81",
"name": "execute_tool search_flights",
"kind": "INTERNAL",
"scope": {
"name": "@aws/aws-distro-opentelemetry-instrumentation-openai-agents",
"version": "0.12.0"
},
"attributes": {
"gen_ai.operation.name": "execute_tool",
"gen_ai.tool.name": "search_flights",
"gen_ai.tool.type": "function",
"gen_ai.tool.call.arguments": "{\"origin\": \"SEA\", \"destination\": \"NYC\",
\"date\": \"2025-03-15\"}",
"gen_ai.tool.call.result": "{\"origin\": \"SEA\", \"destination\": \"NYC\",
\"flights\": [ ... ]}",
"session.id": "sea-nyc-trip-2-turns"
},
"status": {
OpenAI Agents

2222

"code": "OK"
}
}

Inference span
The gen_ai.operation.name attribute (chat) identiﬁes this as an inference span. The
gen_ai.input.messages and gen_ai.output.messages attributes hold the conversation
in the parts-format, gen_ai.system_instructions holds the system prompt, and
gen_ai.tool.definitions lists the tools available to the agent.
{
"traceId": "6a6bc695459e41aa14a172bb41d3246d",
"spanId": "7c1f9a2b4d6e8a03",
"name": "chat gpt-4o-mini-2024-07-18",
"kind": "INTERNAL",
"scope": {
"name": "@aws/aws-distro-opentelemetry-instrumentation-openai-agents",
"version": "0.12.0"
},
"attributes": {
"gen_ai.operation.name": "chat",
"gen_ai.provider.name": "openai",
"gen_ai.response.model": "gpt-4o-mini-2024-07-18",
"gen_ai.input.messages": "[{\"role\": \"user\", \"parts\": [{\"type\": \"text\",
\"content\": \"Hey, how can you help me\"}]}]",
"gen_ai.output.messages": "[{\"role\": \"assistant\", \"parts\": [{\"type\":
\"text\", \"content\": \"I can assist you with planning your trips ...\"}]}]",
"gen_ai.system_instructions": "[{\"type\": \"text\", \"content\": \"You are a
travel planning assistant ...\"}]",
"gen_ai.tool.definitions": "[{\"type\": \"function\", \"name\": \"search_flights
\", \"description\": \"Search for available flights between cities.\", ...}]",
"gen_ai.usage.input_tokens": 422,
"gen_ai.usage.output_tokens": 82,
"session.id": "sea-nyc-trip-2-turns"
},
"status": {
"code": "OK"
}
}

OpenAI Agents

2223

OpenInference
With the OpenInference JS library, the invoke agent (AGENT) and turn (CHAIN) spans are empty
containers. AgentCore Evaluations reconstructs the user prompt and agent response from
the inference (LLM) span, whose messages are on the indexed llm.input_messages.* and
llm.output_messages.* attributes.
Example
Invoke agent span
The openinference.span.kind attribute (AGENT) identiﬁes this as an invoke agent span.
The span carries no conversation content.
{
"traceId": "6a6bc695459e41aa14a172bb41d3246d",
"spanId": "9a1c7dce81b692cd",
"name": "openaiAgentsOInf",
"kind": "INTERNAL",
"scope": {
"name": "@arizeai/openinference-instrumentation-openai-agents",
"version": "0.2.2"
},
"attributes": {
"openinference.span.kind": "AGENT",
"graph.node.id": "openaiAgentsOInf",
"llm.system": "openai",
"session.id": "sea-nyc-trip-2-turns"
},
"status": {
"code": "OK"
}
}

Execute tool span
The openinference.span.kind attribute (TOOL) identiﬁes this as an execute tool span;
tool.name holds the tool name. The input.value and output.value attributes hold the
tool arguments and result.
{
"traceId": "6a6bc695459e41aa14a172bb41d3246d",
"spanId": "b4e78cb0a06a6fe2",
OpenAI Agents

2224

"name": "search_flights",
"kind": "INTERNAL",
"scope": {
"name": "@arizeai/openinference-instrumentation-openai-agents",
"version": "0.2.2"
},
"attributes": {
"openinference.span.kind": "TOOL",
"tool.name": "search_flights",
"input.value": "{\"origin\": \"SEA\", \"destination\": \"NYC\", \"date\":
\"2025-03-15\"}",
"output.value": "{\"origin\": \"SEA\", \"destination\": \"NYC\", \"flights\":
[ ... ]}",
"session.id": "sea-nyc-trip-2-turns"
},
"status": {
"code": "OK"
}
}

Inference span
The openinference.span.kind attribute (LLM) identiﬁes this as an inference
span. The llm.input_messages.* attributes hold the system prompt and user
prompt, the llm.output_messages.* attributes hold the agent response, and the
llm.tools.*.tool.json_schema attributes hold the tool deﬁnitions. AgentCore
Evaluations reconstructs the user prompt and agent response from this span and backﬁlls the
empty invoke agent (AGENT) span.
{
"traceId": "6a6bc695459e41aa14a172bb41d3246d",
"spanId": "1221a062c7f90a8e",
"name": "response",
"kind": "INTERNAL",
"scope": {
"name": "@arizeai/openinference-instrumentation-openai-agents",
"version": "0.2.2"
},
"attributes": {
"openinference.span.kind": "LLM",
"llm.model_name": "gpt-4o-mini-2024-07-18",
"llm.input_messages.0.message.role": "system",
OpenAI Agents

2225


## Vercel AI SDK (pp. 2226–2230)

"llm.input_messages.0.message.content": "You are a travel planning
assistant ...",
"llm.input_messages.1.message.role": "user",
"llm.input_messages.1.message.content": "Hey, how can you help me",
"llm.output_messages.0.message.role": "assistant",
"llm.output_messages.0.message.contents.0.message_content.text": "I can assist
you with travel planning by ...",
"llm.tools.0.tool.json_schema": "{\"type\": \"function\", \"function\": {\"name
\": \"search_flights\", ...}}",
"session.id": "sea-nyc-trip-2-turns"
},
"status": {
"code": "OK"
}
}

Set up Vercel AI SDK telemetry for AgentCore Evaluations
This page explains how to instrument a Vercel AI SDK agent, how spans are identiﬁed, and how
evaluation ﬁelds are extracted. The Vercel AI SDK is a TypeScript-only framework, so all support on
this page applies to TypeScript agents.

Note
AgentCore Evaluations supports the Vercel AI SDK for TypeScript agents only. Python is not
supported at this time.

Topics
• TypeScript agent support
• Instrument your agent
• How spans are identiﬁed
• How evaluation ﬁelds are extracted
• Example spans from a TypeScript agent

Vercel AI SDK

2226

TypeScript agent support
A Vercel AI SDK agent produces spans under the scope name @aws/aws-distroopentelemetry-instrumentation-vercel-ai.
Instrument your agent
Instrument a Vercel AI SDK agent with the AWS Distro for OpenTelemetry (ADOT). Add the
AWS Distro Node autoinstrumentation package (@aws/aws-distro-opentelemetry-nodeautoinstrumentation) to your dependencies. It includes the built-in Vercel AI instrumentation,
which activates at startup and emits the scope name @aws/aws-distro-opentelemetryinstrumentation-vercel-ai.
package.json:
{
"dependencies": {
"@aws/aws-distro-opentelemetry-node-autoinstrumentation": "^0.12.0"
}
}

The instrumentation follows the OpenTelemetry generative-AI semantic conventions: it classiﬁes
spans with gen_ai.operation.name and carries the conversation in gen_ai.* attributes.
Note
Instrumentation is one step in setting up observability. To export telemetry for evaluation,
complete the full setup in Set up observability.

How spans are identiﬁed
The Vercel AI instrumentation sets the gen_ai.operation.name attribute on each span. The
evaluation service uses this attribute to classify spans:

Span type

Identifying attribute

Invoke agent

gen_ai.operation.name

Vercel AI SDK

= invoke_agent
2227

Span type

Identifying attribute

Execute tool

gen_ai.operation.name

= execute_tool

Inference

gen_ai.operation.name

= chat

How evaluation ﬁelds are extracted
The Vercel AI SDK serializes messages in two shapes, and AgentCore Evaluations reads both:
• An object-dict shape on the input of the invoke agent and inference spans, in which
gen_ai.input.messages is a JSON object with a system ﬁeld (the system prompt) and a
messages array (for example, {"system": "…", "messages": [{"role": "user",
"content": "…"}]} ).
• A parts-list shape on the output, in which each message carries a parts array of typed
content blocks (for example, [{"role": "assistant", "parts": [{"type": "text",
"content": "…"}]}] ).
AgentCore Evaluations pulls the text out of both shapes: the user prompt from the last user
message in the input, the system prompt from the system ﬁeld, and the agent response from the
text parts of the output.
The Vercel AI instrumentation uses uniﬁed telemetry, so the conversation content stays on the span
as attributes:
• User prompt and agent response: from gen_ai.input.messages and
gen_ai.output.messages on the invoke agent span.
• System prompt: from the system ﬁeld of the object-dict in gen_ai.input.messages.
• Tool call: the tool name from gen_ai.tool.name, and the arguments and result from
gen_ai.tool.call.arguments and gen_ai.tool.call.result, on the execute tool span.
For more information, see Example spans from a TypeScript agent.
Example spans from a TypeScript agent
With uniﬁed telemetry, the conversation content stays on the span attributes and no separate
event record is produced. The following examples are from a TypeScript Vercel AI SDK travelVercel AI SDK

2228

planning agent deployed on Amazon Bedrock AgentCore Runtime, using an Amazon Bedrock
model.

Note
These examples are not complete spans. They show representative data from a real agent
interaction, with some ﬁelds omitted and long values truncated for readability.

Example
Invoke agent span
The gen_ai.operation.name attribute (invoke_agent) identiﬁes this as an invoke agent
span. The gen_ai.input.messages attribute holds the system prompt and conversation in
the object-dict shape, and gen_ai.output.messages holds the agent response in the partslist shape.
{
"traceId": "6a6bd3b14c8d91ed1e70a3906b551618",
"spanId": "fa0dce44446e3d24",
"name": "invoke_agent",
"kind": "INTERNAL",
"scope": {
"name": "@aws/aws-distro-opentelemetry-instrumentation-vercel-ai",
"version": "0.12.0"
},
"attributes": {
"gen_ai.operation.name": "invoke_agent",
"gen_ai.provider.name": "aws.bedrock",
"gen_ai.request.model": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
"gen_ai.input.messages": "{\"system\": \"You are a travel planning assistant ...
\", \"messages\": [{\"role\": \"user\", \"content\": \"Hey, how can you help me
\"}]}",
"gen_ai.output.messages": "[{\"role\": \"assistant\", \"parts\": [{\"type\":
\"text\", \"content\": \"Hello! I'm your travel planning assistant ...\"}]}]",
"session.id": "sea-nyc-trip-2-turns"
},
"status": {
"code": "OK"
}

Vercel AI SDK

2229

}

Execute tool span
The gen_ai.operation.name attribute (execute_tool) identiﬁes this as an execute tool
span; gen_ai.tool.name holds the tool name. The gen_ai.tool.call.arguments
attribute holds the tool arguments, and the gen_ai.tool.call.result attribute holds the
tool result.
{
"traceId": "6a6bd3b14c8d91ed1e70a3906b551618",
"spanId": "b64c37adefae74f0",
"name": "execute_tool search_flights",
"kind": "INTERNAL",
"scope": {
"name": "@aws/aws-distro-opentelemetry-instrumentation-vercel-ai",
"version": "0.12.0"
},
"attributes": {
"gen_ai.operation.name": "execute_tool",
"gen_ai.tool.name": "search_flights",
"gen_ai.tool.type": "function",
"gen_ai.tool.call.id": "toolu_bdrk_01LzXXJCfpfuS7Bpf7e1qLMg",
"gen_ai.tool.call.arguments": "{\"origin\": \"SEA\", \"destination\": \"NYC\",
\"date\": \"2025-03-15\"}",
"gen_ai.tool.call.result": "{\"origin\": \"SEA\", \"destination\": \"NYC\",
\"flights\": [ ... ]}",
"session.id": "sea-nyc-trip-2-turns"
},
"status": {
"code": "OK"
}
}

Inference span
The gen_ai.operation.name attribute (chat) identiﬁes this as an inference span. It carries
the model metadata and, in gen_ai.tool.definitions, the list of tools available to the
agent. The conversation messages for the model call are in gen_ai.input.messages (objectdict shape) and gen_ai.output.messages (parts-list shape).
{
Vercel AI SDK

2230


## LlamaIndex (pp. 2231–2246)

"traceId": "6a6bd3b14c8d91ed1e70a3906b551618",
"spanId": "1865614ca1b88dfb",
"name": "chat us.anthropic.claude-sonnet-4-5-20250929-v1:0",
"kind": "INTERNAL",
"scope": {
"name": "@aws/aws-distro-opentelemetry-instrumentation-vercel-ai",
"version": "0.12.0"
},
"attributes": {
"gen_ai.operation.name": "chat",
"gen_ai.provider.name": "aws.bedrock",
"gen_ai.request.model": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
"gen_ai.response.model": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
"gen_ai.usage.input_tokens": 1258,
"gen_ai.usage.output_tokens": 241,
"gen_ai.input.messages": "{\"system\": \"You are a travel planning assistant ...
\", \"messages\": [{\"role\": \"user\", \"content\": \"Hey, how can you help me
\"}]}",
"gen_ai.output.messages": "[{\"role\": \"assistant\", \"parts\": [{\"type\":
\"text\", \"content\": \"Hello! I'm your travel planning assistant ...\"}]}]",
"gen_ai.tool.definitions": "[{\"type\": \"function\", \"name\": \"search_flights
\", \"description\": \"Search for available flights between cities.\", ...}]",
"session.id": "sea-nyc-trip-2-turns"
},
"status": {
"code": "OK"
}
}

LlamaIndex
This page explains how to instrument a LlamaIndex agent, how spans are identiﬁed, and how
evaluation ﬁelds are extracted. It closes with best practices for structuring a LlamaIndex agent so
that it can be evaluated reliably.
Topics
• Instrument your agent
• How spans are identiﬁed
• How evaluation ﬁelds are extracted
• From event records
LlamaIndex

2231

• From span attributes
• Example spans in split telemetry
• Example spans in uniﬁed telemetry
• Best practices for LlamaIndex agents

Instrument your agent
You can instrument a LlamaIndex agent with either of two instrumentation libraries:
OpenTelemetry (opentelemetry-instrumentation-llamaindex) or OpenInference
(openinference-instrumentation-llama-index). Amazon Bedrock AgentCore Evaluations
supports both libraries. The libraries emit diﬀerent scope names and use diﬀerent span attributes.
The evaluation service extracts the same values from each.
When your agent runs with the AWS Distro for OpenTelemetry (ADOT), such as on Amazon
Bedrock AgentCore Runtime, you do not need to add explicit instrumentation code. Adding the
instrumentation library to your project’s dependencies is enough. ADOT discovers it at startup and
activates it automatically.
Add the instrumentation library for the path you want to your dependencies. Use the latest
available version unless you have a reason to pin.
Example
OpenTelemetry
NOTE: Use version 0.61.0 or later. This is the earliest version tested with the evaluation
service.
Add opentelemetry-instrumentation-llamaindex to your dependencies. The scope
name emitted is opentelemetry.instrumentation.llamaindex.
requirements.txt:
opentelemetry-instrumentation-llamaindex>=0.61.0

pyproject.toml:
[project]
dependencies = [
LlamaIndex

2232

"opentelemetry-instrumentation-llamaindex>=0.61.0",
]

OpenInference
NOTE: Use version 4.4.1 or later. This is the earliest version tested with the evaluation service.
Add openinference-instrumentation-llama-index to your dependencies. The scope
name emitted is openinference.instrumentation.llama_index.
requirements.txt:
openinference-instrumentation-llama-index>=4.4.1

pyproject.toml:
[project]
dependencies = [
"openinference-instrumentation-llama-index>=4.4.1",
]

Note
Instrumentation is one step in setting up observability. To export telemetry for evaluation,
complete the full setup in Set up observability.

How spans are identiﬁed
The attribute used to classify spans diﬀers between the two instrumentation libraries.
Example
OpenTelemetry
The OpenTelemetry instrumentation library classiﬁes spans using the traceloop.span.kind
attribute. Because LlamaIndex tags both inference and tool operations as task, AgentCore
Evaluations disambiguates them by the traceloop.entity.name attribute: a task whose
entity name ends in Tool.task is an execute tool span; any other task is an inference span.
LlamaIndex

2233

Span type

Identifying attribute

Invoke agent

traceloop.span.kind

= workflow

Execute tool

traceloop.span.kind

= tool, or traceloop

.span.kind

= task with traceloop.entity.name

ending in Tool.task
Inference

traceloop.span.kind

= task (not a tool task)

OpenInference
The OpenInference instrumentation library classiﬁes spans using the
openinference.span.kind attribute. LlamaIndex emits CHAIN, LLM, and TOOL spans; it does
not emit AGENT spans. The root workﬂow span (a CHAIN) acts as the invoke agent span.
Span type

Identifying attribute

Invoke agent

openinference.span.kind
span)

= CHAIN (root workﬂow

Execute tool

openinference.span.kind

= TOOL

Inference

openinference.span.kind

= LLM

Note
LlamaIndex emits several intermediate CHAIN spans (for example, for output parsing
and tool routing). AgentCore Evaluations treats only the root workﬂow span as the
invoke agent span and reconstructs the user prompt and agent response from the
inference (LLM) spans in the trace.

How evaluation ﬁelds are extracted
The LlamaIndex agent is a workﬂow, and its top-level span is emitted before its child spans.
That workﬂow span carries no usable conversation content of its own, so AgentCore Evaluations
LlamaIndex

2234

reconstructs the user prompt and agent response from the child spans (the inference and tool
spans) and attaches them to the invoke agent span.
LlamaIndex also serializes content as nested JSON. Tool arguments are wrapped as {"kwargs":
{…}} , and tool results are wrapped as {"blocks": [{"text": "…"}], …} . AgentCore
Evaluations unwraps these forms. When a LlamaIndex ReAct agent produces output in the form
Thought: … Answer: <response> , AgentCore Evaluations extracts the text after Answer: as
the agent response.
The location of this content depends on how telemetry was collected. The identifying attribute
(traceloop.span.kind or openinference.span.kind) is on the span in both cases. For more
information, see Telemetry setup and delivery.
From event records
With split telemetry, AgentCore Evaluations reads content from the event record correlated to each
span:
• User prompt and agent response: reconstructed from the inference spans' event records, in
body.output. With the OpenTelemetry library, the user prompt comes from the chat-history
content and the agent response from the model-result content. With the OpenInference library,
the user prompt is the plain-text input message and the agent response is the model output
(with the text after Answer: used for a ReAct agent).
• Tool call: the tool name from the execute tool span. The tool arguments and result come
from that span’s event record, in body.input (unwrapped from {"kwargs": {…}} ) and
body.output (unwrapped from {"blocks": […]} ).
For more information, see Example spans in split telemetry.
From span attributes
With uniﬁed telemetry, the same content stays on the span as attributes. The attributes depend on
the instrumentation library:
• OpenTelemetry: the content is on the traceloop.entity.input and
traceloop.entity.output attributes of each span. AgentCore Evaluations applies the same
chat-history, result, and tool unwrapping to these values.
• OpenInference: the inference content is on the indexed message attributes
(llm.input_messages.* and llm.output_messages.*). Tool arguments come from
LlamaIndex

2235

input.value (unwrapped from {"kwargs": {…}} ) and the tool result from output.value
(unwrapped from {"blocks": […]} ).
For more information, see Example spans in uniﬁed telemetry.

Example spans in split telemetry
With split telemetry, the span carries the identifying attributes and the content lives in a correlated
event record. The following examples are from a LlamaIndex ReAct travel-planning agent deployed
on Amazon Bedrock AgentCore Runtime. The same agent is shown under each instrumentation
library.
Note
These examples are not complete spans. They show representative data from a real agent
interaction, with some ﬁelds omitted and long values truncated for readability.

OpenTelemetry
Example
Invoke agent span
The traceloop.span.kind attribute (workflow) identiﬁes this as an invoke agent span. The
workﬂow span carries no conversation content; AgentCore Evaluations reconstructs the user
prompt and agent response from the child spans.
{
"traceId": "6a01eef11066751d68f90def0da1f80a",
"spanId": "ba1833fa7f097041",
"name": "ReActAgent.workflow",
"kind": "INTERNAL",
"scope": {
"name": "opentelemetry.instrumentation.llamaindex",
"version": "0.61.0"
},
"attributes": {
"traceloop.span.kind": "workflow",
"traceloop.entity.name": "ReActAgent.workflow",
LlamaIndex

2236

"session.id": "sea-nyc-trip-2-turns-llamaindex-otel"
},
"status": {
"code": "OK"
}
}

Execute tool span
The traceloop.span.kind attribute (task) with a traceloop.entity.name ending in
Tool.task identiﬁes this as an execute tool span. The correlated event record carries the tool
arguments (wrapped in kwargs) and the tool result (wrapped in blocks), along with the tool
name.
{
"traceId": "6a01eefa5c52f3d86a35038f35f5ba30",
"spanId": "5b332f3cd15ace04",
"name": "FunctionTool.task",
"kind": "INTERNAL",
"scope": {
"name": "opentelemetry.instrumentation.llamaindex",
"version": "0.61.0"
},
"attributes": {
"traceloop.span.kind": "task",
"traceloop.entity.name": "FunctionTool.task",
"session.id": "sea-nyc-trip-2-turns-llamaindex-otel"
},
"status": {
"code": "OK"
}
}

{
"spanId": "5b332f3cd15ace04",
"traceId": "6a01eefa5c52f3d86a35038f35f5ba30",
"scope": {
"name": "opentelemetry.instrumentation.llamaindex"
},
"body": {
"input": {
"messages": [
LlamaIndex

2237

{ "role": "user", "content": "{\"kwargs\": {\"origin\": \"SEA\",
\"destination\": \"NYC\", \"date\": \"2025-03-15\"}}" }
]
},
"output": {
"messages": [
{ "content": "{\"blocks\": [{\"block_type\": \"text\", \"text\": \"{\\
\"origin\\\": \\\"SEA\\\", \\\"destination\\\": \\\"NYC\\\", \\\"flights\\\":
[ ... ]}\"}], \"tool_name\": \"search_flights\"}" }
]
}
}
}

Inference span
The traceloop.span.kind attribute (task), with a traceloop.entity.name that does not
end in Tool.task, identiﬁes this as an inference span. A LlamaIndex agent produces several
of these spans per turn. In each one, the content is packed into body.output (there is no
body.input), as a serialized JSON string. AgentCore Evaluations reads the user prompt from
the chat-history string (a {"input": […]} object) on the ﬁrst inference span, and the agent
response from the model-result string (a {"result": {"response": …}} object) on the
last inference span.
The following is the inference span itself.
{
"traceId": "6a01eef11066751d68f90def0da1f80a",
"spanId": "d9a1f0c7b3e64a20",
"name": "BaseWorkflowAgent.task",
"kind": "INTERNAL",
"scope": {
"name": "opentelemetry.instrumentation.llamaindex",
"version": "0.61.0"
},
"attributes": {
"traceloop.span.kind": "task",
"traceloop.entity.name": "BaseWorkflowAgent.task",
"session.id": "sea-nyc-trip-2-turns-llamaindex-otel"
},
"status": {
"code": "OK"
LlamaIndex

2238

}
}

On the ﬁrst inference span, the event record’s body.output content is the chat history. The
user prompt is the user-role text inside the nested input array.
{
"spanId": "d9a1f0c7b3e64a20",
"traceId": "6a01eef11066751d68f90def0da1f80a",
"scope": {
"name": "opentelemetry.instrumentation.llamaindex"
},
"body": {
"output": {
"messages": [
{
"content": "{\"input\": [{\"role\": \"user\", \"blocks\": [{\"block_type
\": \"text\", \"text\": \"Hey, how can you help me\"}]}], \"current_agent_name\":
\"Agent\"}"
}
]
}
}
}

On the last inference span, the event record’s body.output content is the model result. The
agent response is the assistant-role text inside the nested result.response object.
{
"spanId": "826bc829697a9610",
"traceId": "6a01eef11066751d68f90def0da1f80a",
"scope": {
"name": "opentelemetry.instrumentation.llamaindex"
},
"body": {
"output": {
"messages": [
{
"content": "{\"result\": {\"response\": {\"role\": \"assistant\", \"blocks
\": [{\"block_type\": \"text\", \"text\": \"Here are the available flights from
Seattle to New York City ...\"}]}}, \"current_agent_name\": \"Agent\"}"
}
LlamaIndex

2239

]
}
}
}

OpenInference
Example
Invoke agent span
The openinference.span.kind attribute (CHAIN) on the root workﬂow span identiﬁes
this as an invoke agent span. The span carries no usable conversation content; AgentCore
Evaluations reconstructs the user prompt and agent response from the inference spans.
{
"traceId": "6a387ee61078243c1cc455ed45c6c313",
"spanId": "0a7990d804132a9b",
"name": "ReActAgent.run",
"kind": "INTERNAL",
"scope": {
"name": "openinference.instrumentation.llama_index",
"version": "4.4.1"
},
"attributes": {
"openinference.span.kind": "CHAIN",
"input.mime_type": "application/json",
"output.mime_type": "text/plain",
"session.id": "sea-nyc-trip-2-turns-llamaindex-oi"
},
"status": {
"code": "OK"
}
}

Execute tool span
The openinference.span.kind attribute (TOOL) identiﬁes this as an execute tool span;
tool.name holds the tool name. The tool arguments and result live in the correlated event
record, wrapped in kwargs and blocks respectively.
{
LlamaIndex

2240

"traceId": "6a387ef07b8f4f3732fab45d3c0b51ff",
"spanId": "ab105c12cc40048f",
"name": "FunctionTool.acall",
"kind": "INTERNAL",
"scope": {
"name": "openinference.instrumentation.llama_index",
"version": "4.4.1"
},
"attributes": {
"openinference.span.kind": "TOOL",
"tool.name": "search_flights",
"tool.description": "search_flights(origin: str, destination: str, date: str) ->
str ...",
"session.id": "sea-nyc-trip-2-turns-llamaindex-oi"
},
"status": {
"code": "OK"
}
}

{
"spanId": "ab105c12cc40048f",
"traceId": "6a387ef07b8f4f3732fab45d3c0b51ff",
"scope": {
"name": "openinference.instrumentation.llama_index"
},
"body": {
"input": {
"messages": [
{ "content": "{\"kwargs\": {\"origin\": \"SEA\", \"destination\": \"NYC\",
\"date\": \"2025-03-15\"}}" }
]
},
"output": {
"messages": [
{ "content": "{\"blocks\": [{\"text\": \"{\\\"origin\\\": \\\"SEA\\\",
\\\"destination\\\": \\\"NYC\\\", \\\"flights\\\": [ ... ]}\"}], \"tool_name\":
\"search_flights\"}" }
]
}
}
}

LlamaIndex

2241

Inference span
The openinference.span.kind attribute (LLM) identiﬁes this as an inference span. Message
roles are on the span attributes; the content lives in the correlated event record. ADOT ﬂattens
the input roles to user, so AgentCore Evaluations uses the last plain-text input message as
the user prompt. LlamaIndex emits a duplicate assistant:-preﬁxed output message, which
AgentCore Evaluations skips in favor of the clean copy.
{
"traceId": "6a387ee61078243c1cc455ed45c6c313",
"spanId": "1221a062c7f90a8e",
"name": "OpenAI.astream_chat",
"kind": "INTERNAL",
"scope": {
"name": "openinference.instrumentation.llama_index",
"version": "4.4.1"
},
"attributes": {
"openinference.span.kind": "LLM",
"llm.system": "openai",
"llm.model_name": "gpt-4o-mini",
"llm.input_messages.0.message.role": "system",
"llm.input_messages.1.message.role": "user",
"llm.output_messages.0.message.role": "assistant",
"session.id": "sea-nyc-trip-2-turns-llamaindex-oi"
},
"status": {
"code": "OK"
}
}

{
"spanId": "1221a062c7f90a8e",
"traceId": "6a387ee61078243c1cc455ed45c6c313",
"scope": {
"name": "openinference.instrumentation.llama_index"
},
"body": {
"input": {
"messages": [
{ "role": "user", "content": "{\"messages\": [ ... ]}" },

LlamaIndex

2242

{ "role": "user", "content": "You are designed to help with a variety of
tasks ..." },
{ "role": "user", "content": "Hey, how can you help me" }
]
},
"output": {
"messages": [
{ "role": "assistant", "content": "assistant: Thought: ... Answer: I can
help you plan your trip ..." },
{ "role": "assistant", "content": "Thought: ... Answer: I can help you plan
your trip ..." }
]
}
}
}

Example spans in uniﬁed telemetry
With uniﬁed telemetry, the same content stays on the span attributes and no separate event record
is produced. The following examples are from a LlamaIndex ReAct travel-planning agent. The same
agent is shown under each instrumentation library.
Note
These examples are not complete spans. They show representative data from a real agent
interaction, with some ﬁelds omitted and long values truncated for readability.

OpenTelemetry
Example
Execute tool span
The traceloop.entity.input attribute holds the tool arguments (wrapped in kwargs), and
the traceloop.entity.output attribute holds the tool result (wrapped in blocks).
{
"traceId": "6a4de7c376913db82e6f0f336a16731d",
"spanId": "b64c37adefae74f0",
"name": "FunctionTool.task",
LlamaIndex

2243

"kind": "INTERNAL",
"scope": {
"name": "opentelemetry.instrumentation.llamaindex",
"version": "0.61.0"
},
"attributes": {
"traceloop.span.kind": "task",
"traceloop.entity.name": "FunctionTool.task",
"traceloop.entity.input": "{\"kwargs\": {\"origin\": \"SEA\", \"destination\":
\"NYC\", \"date\": \"2025-03-15\"}}",
"traceloop.entity.output": "{\"blocks\": [{\"block_type\": \"text\", \"text
\": \"{\\\"origin\\\": \\\"SEA\\\", \\\"flights\\\": [ ... ]}\"}], \"tool_name\":
\"search_flights\"}",
"session.id": "sea-nyc-trip-2-turns-unified"
},
"status": {
"code": "OK"
}
}

Inference span
The traceloop.entity.output attribute holds the chat history, from which AgentCore
Evaluations reads the user prompt. The response comes from the model result on the last
inference span.
{
"traceId": "6a4de7b85e61747e6b568a1f4768e89d",
"spanId": "31ea3d5882dac680",
"name": "BaseWorkflowAgent.task",
"kind": "INTERNAL",
"scope": {
"name": "opentelemetry.instrumentation.llamaindex",
"version": "0.61.0"
},
"attributes": {
"traceloop.span.kind": "task",
"traceloop.entity.name": "BaseWorkflowAgent.task",
"traceloop.entity.output": "{\"input\": [{\"role\": \"user\", \"blocks
\": [{\"block_type\": \"text\", \"text\": \"Hey, how can you help me\"}]}],
\"current_agent_name\": \"Agent\"}",
"session.id": "sea-nyc-trip-2-turns-unified"
},
LlamaIndex

2244

"status": {
"code": "OK"
}
}

OpenInference
Example
Execute tool span
The input.value attribute holds the tool arguments (wrapped in kwargs), and the
output.value attribute holds the tool result (wrapped in blocks).
{
"traceId": "6a387ef07b8f4f3732fab45d3c0b51ff",
"spanId": "d5a1c9e70b46f312",
"name": "FunctionTool.acall",
"kind": "INTERNAL",
"scope": {
"name": "openinference.instrumentation.llama_index",
"version": "4.4.2"
},
"attributes": {
"openinference.span.kind": "TOOL",
"tool.name": "search_flights",
"input.value": "{\"kwargs\": {\"origin\": \"SEA\", \"destination\": \"NYC\",
\"date\": \"2025-03-15\"}}",
"output.value": "{\"blocks\": [{\"text\": \"{\\\"origin\\\": \\\"SEA\\\", \\
\"flights\\\": [ ... ]}\"}], \"tool_name\": \"search_flights\"}",
"session.id": "sea-nyc-trip-2-turns-oi"
},
"status": {
"code": "OK"
}
}

Inference span
The message content is inline on the indexed attributes. The llm.input_messages.*
attributes hold the system prompt and user prompt, and the llm.output_messages.*
LlamaIndex

2245

attributes hold the model output, from which AgentCore Evaluations extracts the text after
Answer: as the agent response.
{
"traceId": "6a387ee61078243c1cc455ed45c6c313",
"spanId": "c9f0a2b41d773e88",
"name": "OpenAI.astream_chat",
"kind": "INTERNAL",
"scope": {
"name": "openinference.instrumentation.llama_index",
"version": "4.4.2"
},
"attributes": {
"openinference.span.kind": "LLM",
"llm.model_name": "gpt-4o-mini",
"llm.input_messages.0.message.role": "system",
"llm.input_messages.0.message.content": "You are designed to help with a variety
of tasks ...",
"llm.input_messages.1.message.role": "user",
"llm.input_messages.1.message.content": "Hey, how can you help me",
"llm.output_messages.0.message.role": "assistant",
"llm.output_messages.0.message.content": "Thought: ... Answer: I can help you
plan your trip ...",
"session.id": "sea-nyc-trip-2-turns-oi"
},
"status": {
"code": "OK"
}
}

Best practices for LlamaIndex agents
How you build and invoke a LlamaIndex agent aﬀects what appears in its telemetry, and therefore
how reliably the agent can be evaluated. The following practices help ensure the user prompt,
agent response, and tool activity are recoverable.
• Use a LlamaIndex agent workﬂow. Build your agent as a LlamaIndex agent workﬂow (for
example, a ReActAgent or FunctionAgent) so that the framework emits a top-level workﬂow
span with inference and tool child spans. AgentCore Evaluations reconstructs the invoke agent
span from these child spans.

LlamaIndex

2246


## Google ADK (pp. 2247–2255)

• Register tools as FunctionTool objects. Deﬁne each tool as a LlamaIndex FunctionTool
(or use @tool-style helpers that produce one). Tool spans are identiﬁed by their entity name,
and their arguments and results are serialized in the kwargs and blocks structures AgentCore
Evaluations unwraps.
• Keep tool results text-serializable. Return tool results as strings or JSON-serializable values.
LlamaIndex wraps them in a text block; keeping them serializable ensures the tool result is
captured cleanly.
• For ReAct agents, use the standard output format. AgentCore Evaluations extracts the ﬁnal
answer from the Answer: section of a ReAct agent’s output. Using the standard ReAct prompt
(the LlamaIndex default) keeps the agent response recoverable.

Google ADK
This page explains how to instrument a Google Agent Development Kit (ADK) agent, how spans are
identiﬁed, and how evaluation ﬁelds are extracted.
Topics
• Instrument your agent
• How spans are identiﬁed
• How evaluation ﬁelds are extracted
• From event records
• From span attributes
• Example spans in split telemetry
• Example spans in uniﬁed telemetry

Instrument your agent
You can instrument a Google ADK agent with the OpenInference instrumentation library
(openinference-instrumentation-google-adk). This library emits telemetry under the
scope name openinference.instrumentation.google_adk, which Amazon Bedrock
AgentCore Evaluations reads.
When your agent runs with the AWS Distro for OpenTelemetry (ADOT), such as on Amazon
Bedrock AgentCore Runtime, you do not need to add explicit instrumentation code. Adding the
Google ADK

2247

instrumentation library to your project’s dependencies is enough. ADOT discovers it at startup and
activates it automatically.
Add the instrumentation library to your dependencies.
Note
Use version 0.1.13 or later. This is the earliest version tested with the evaluation service.

requirements.txt:
openinference-instrumentation-google-adk>=0.1.13

pyproject.toml:
[project]
dependencies = [
"openinference-instrumentation-google-adk>=0.1.13",
]

Note
Instrumentation is one step in setting up observability. To export telemetry for evaluation,
complete the full setup in Set up observability.

How spans are identiﬁed
Google ADK is instrumented with the OpenInference convention, so AgentCore Evaluations
classiﬁes spans using the openinference.span.kind attribute.
Span type

Identifying attribute

Invoke agent

openinference.span.kind

= CHAIN or AGENT

Execute tool

openinference.span.kind

= TOOL

Inference

openinference.span.kind

= LLM

Google ADK

2248

Google ADK emits a nested span tree: an outer invocation span (CHAIN) wraps an agent_run
span (AGENT), which in turn wraps the call_llm (LLM) and execute_tool (TOOL) spans. The
outer CHAIN span carries the user prompt; AgentCore Evaluations uses it as the invoke agent span.

How evaluation ﬁelds are extracted
Google ADK wraps its conversation content in the Gemini content format. The user prompt
is nested under a new_message object as {"new_message": {"parts": [{"text":
"…"}], "role": "user"}} , and the agent response is nested under a content object
as {"content": {"parts": [{"text": "…"}], "role": "model"}} . AgentCore
Evaluations unwraps these structures and joins the parts text with newlines. Tool deﬁnitions
arrive as a serialized Gemini request; AgentCore Evaluations reads the available tools from
config.tools[].function_declarations[].
The location of this content depends on how telemetry was collected. The identifying attribute
(openinference.span.kind) is on the span in both cases. For more information, see Telemetry
setup and delivery.
From event records
With split telemetry, AgentCore Evaluations reads content from the event record correlated to each
span:
• User prompt: from the invoke agent span’s event record, in body.input. AgentCore Evaluations
unwraps the new_message.parts text.
• Agent response: from the invoke agent span’s event record, in body.output. AgentCore
Evaluations unwraps the content.parts text.
• Tool call: the tool name from the tool.name attribute on the execute tool span. The tool
arguments and result come from that span’s event record, in body.input and body.output.
For more information, see Example spans in split telemetry.
From span attributes
With uniﬁed telemetry, the same content stays on the span as attributes:
• User prompt and agent response: from input.value and output.value on the invoke agent
span. AgentCore Evaluations unwraps the new_message.parts and content.parts text.
Google ADK

2249

• Tool call: the tool name from tool.name, and the arguments and result from input.value
and output.value, on the execute tool span.
For more information, see Example spans in uniﬁed telemetry.

Example spans in split telemetry
With split telemetry, the span carries the identifying attributes and the content lives in a correlated
event record. The following examples are from a Google ADK travel-planning agent deployed on
Amazon Bedrock AgentCore Runtime.
Note
These examples are not complete spans. They show representative data from a real agent
interaction, with some ﬁelds omitted and long values truncated for readability.

Example
Invoke agent span
The openinference.span.kind attribute (CHAIN) on the outer invocation span identiﬁes
this as an invoke agent span. The span carries no conversation content; it lives in the correlated
event record.
{
"traceId": "6a387ee61078243c1cc455ed45c6c313",
"spanId": "70f2e87a30c34420",
"name": "invocation",
"kind": "INTERNAL",
"scope": {
"name": "openinference.instrumentation.google_adk",
"version": "0.1.14"
},
"attributes": {
"openinference.span.kind": "CHAIN",
"input.mime_type": "application/json",
"output.mime_type": "application/json",
"user.id": "default_user",
"session.id": "sea-nyc-trip-2-turns-google-adk-adot"
},
Google ADK

2250

"status": {
"code": "OK"
}
}

The correlated event record carries the conversation. The user prompt is nested under
new_message.parts, and the agent response is nested under content.parts.
{
"spanId": "70f2e87a30c34420",
"traceId": "6a387ee61078243c1cc455ed45c6c313",
"scope": {
"name": "openinference.instrumentation.google_adk"
},
"body": {
"input": {
"messages": [
{
"role": "user",
"content": "{\"new_message\": {\"parts\": [{\"text\": \"Hey, how can you
help me\"}], \"role\": \"user\"}, \"state_delta\": null, \"run_config\": null}"
}
]
},
"output": {
"messages": [
{
"role": "assistant",
"content": "{\"model_version\": \"gemini-2.5-flash\", \"content\":
{\"parts\": [{\"text\": \"I can help you with your travel plans! I can:\\n- Search
and book flights\\n- Find and book hotels\\n- Suggest and book activities\"}],
\"role\": \"model\"}, \"finish_reason\": \"STOP\"}"
}
]
}
}
}

Execute tool span
The openinference.span.kind attribute (TOOL) identiﬁes this as an execute tool span;
tool.name holds the tool name. The tool arguments and result live in the correlated event
record.
Google ADK

2251

{
"traceId": "6a387ef07b8f4f3732fab45d3c0b51ff",
"spanId": "9028a8dd94943456",
"name": "execute_tool search_flights",
"kind": "INTERNAL",
"scope": {
"name": "openinference.instrumentation.google_adk",
"version": "0.1.14"
},
"attributes": {
"openinference.span.kind": "TOOL",
"gen_ai.operation.name": "execute_tool",
"gen_ai.tool.name": "search_flights",
"gen_ai.tool.type": "FunctionTool",
"gen_ai.tool.call.id": "adk-12345678-1234-1234-1234-123456789012",
"tool.name": "search_flights",
"tool.parameters": "{\"origin\": \"SEA\", \"destination\": \"NYC\", \"date\":
\"2025-03-15\"}",
"session.id": "sea-nyc-trip-2-turns-google-adk-adot"
},
"status": {
"code": "OK"
}
}

{
"spanId": "9028a8dd94943456",
"traceId": "6a387ef07b8f4f3732fab45d3c0b51ff",
"scope": {
"name": "openinference.instrumentation.google_adk"
},
"body": {
"input": {
"messages": [
{ "role": "user", "content": "{\"origin\": \"SEA\", \"destination\": \"NYC
\", \"date\": \"2025-03-15\"}" }
]
},
"output": {
"messages": [
{
"role": "assistant",

Google ADK

2252

"content": "{\"id\": \"adk-12345678-...\", \"name\": \"search_flights
\", \"response\": {\"origin\": \"SEA\", \"destination\": \"NYC\", \"flights\":
[ ... ]}}"
}
]
}
}
}

Inference span
The openinference.span.kind attribute (LLM) on the call_llm span identiﬁes this as an
inference span. It carries the model metadata and, in the indexed llm.input_messages.*
and llm.output_messages.* attributes, the messages for the model call.
{
"traceId": "6a387ee61078243c1cc455ed45c6c313",
"spanId": "1c4e5f8a2b9d0e73",
"name": "call_llm",
"kind": "INTERNAL",
"scope": {
"name": "openinference.instrumentation.google_adk",
"version": "0.1.14"
},
"attributes": {
"openinference.span.kind": "LLM",
"gen_ai.operation.name": "generate_content",
"gen_ai.request.model": "gemini-2.5-flash",
"llm.model_name": "gemini-2.5-flash",
"llm.input_messages.0.message.role": "system",
"llm.input_messages.1.message.role": "user",
"llm.input_messages.1.message.contents.0.message_content.text": "Hey, how can
you help me",
"llm.output_messages.0.message.role": "model",
"llm.output_messages.0.message.contents.0.message_content.text": "I can help you
plan your trip ...",
"session.id": "sea-nyc-trip-2-turns-google-adk-adot"
},
"status": {
"code": "OK"
}
}

Google ADK

2253

Example spans in uniﬁed telemetry
With uniﬁed telemetry, the same content stays on the span attributes and no separate event record
is produced. The following examples are from a Google ADK travel-planning agent.
Note
These examples are not complete spans. They show representative data from a real agent
interaction, with some ﬁelds omitted and long values truncated for readability.

Example
Invoke agent span
The input.value attribute holds the user prompt (nested under new_message.parts), and
the output.value attribute holds the agent response (nested under content.parts).
{
"traceId": "6a4de7b85e61747e6b568a1f4768e89d",
"spanId": "31ea3d5882dac680",
"name": "invocation",
"kind": "INTERNAL",
"scope": {
"name": "openinference.instrumentation.google_adk",
"version": "0.1.13"
},
"attributes": {
"openinference.span.kind": "CHAIN",
"input.value": "{\"user_id\": \"test_user\", \"session_id\": \"sea-nyc-trip-2turns-google-adk-unified\", \"new_message\": {\"parts\": [{\"text\": \"Hey, how can
you help me\"}], \"role\": \"user\"}}",
"input.mime_type": "application/json",
"output.value": "{\"model_version\": \"gemini-2.5-flash\", \"content\": {\"parts
\": [{\"text\": \"I can help you plan your trip! I can:\\n- Search and book flights\
\n- Find and book hotels\\n- Suggest and book activities\"}], \"role\": \"model\"},
\"finish_reason\": \"STOP\"}",
"output.mime_type": "application/json",
"session.id": "sea-nyc-trip-2-turns-google-adk-unified"
},
"status": {
"code": "OK"
Google ADK

2254

}
}

Execute tool span
The input.value attribute holds the tool arguments, and the output.value attribute holds
the tool result.
{
"traceId": "6a4de7c376913db82e6f0f336a16731d",
"spanId": "b64c37adefae74f0",
"name": "execute_tool search_flights",
"kind": "INTERNAL",
"scope": {
"name": "openinference.instrumentation.google_adk",
"version": "0.1.13"
},
"attributes": {
"openinference.span.kind": "TOOL",
"gen_ai.operation.name": "execute_tool",
"gen_ai.tool.name": "search_flights",
"gen_ai.tool.call.id": "adk-12345678-1234-1234-1234-123456789012",
"tool.name": "search_flights",
"tool.parameters": "{\"origin\": \"SEA\", \"destination\": \"NYC\", \"date\":
\"2025-03-15\"}",
"input.value": "{\"origin\": \"SEA\", \"destination\": \"NYC\", \"date\":
\"2025-03-15\"}",
"output.value": "{\"id\": \"adk-12345678-...\", \"name\": \"search_flights
\", \"response\": {\"origin\": \"SEA\", \"destination\": \"NYC\", \"flights\":
[ ... ]}}",
"session.id": "sea-nyc-trip-2-turns-google-adk-unified"
},
"status": {
"code": "OK"
}
}

Inference span
The openinference.span.kind attribute (LLM) on the call_llm span identiﬁes
this as an inference span. The messages for the model call are inline on the indexed
llm.input_messages.* and llm.output_messages.* attributes.
Google ADK

2255


## Claude Agent SDK (pp. 2256–2263)

{
"traceId": "6a4de7b85e61747e6b568a1f4768e89d",
"spanId": "2d5f6a9b3c0e1f84",
"name": "call_llm",
"kind": "INTERNAL",
"scope": {
"name": "openinference.instrumentation.google_adk",
"version": "0.1.13"
},
"attributes": {
"openinference.span.kind": "LLM",
"gen_ai.operation.name": "generate_content",
"gen_ai.request.model": "gemini-2.5-flash",
"llm.model_name": "gemini-2.5-flash",
"llm.input_messages.0.message.role": "system",
"llm.input_messages.1.message.role": "user",
"llm.input_messages.1.message.contents.0.message_content.text": "Hey, how can
you help me",
"llm.output_messages.0.message.role": "model",
"llm.output_messages.0.message.contents.0.message_content.text": "I can help you
plan your trip ...",
"session.id": "sea-nyc-trip-2-turns-google-adk-unified"
},
"status": {
"code": "OK"
}
}

Claude Agent SDK
This page explains how to instrument a Claude Agent SDK agent, how spans are identiﬁed, and
how evaluation ﬁelds are extracted.
Topics
• Instrument your agent
• How spans are identiﬁed
• How evaluation ﬁelds are extracted
• From event records
• From span attributes
Claude Agent SDK

2256

• Example spans in split telemetry
• Example spans in uniﬁed telemetry

Instrument your agent
You can instrument a Claude Agent SDK agent with the OpenInference instrumentation library
(openinference-instrumentation-claude-agent-sdk). This library emits telemetry under
the scope name openinference.instrumentation.claude_agent_sdk, which Amazon
Bedrock AgentCore Evaluations reads.
When your agent runs with the AWS Distro for OpenTelemetry (ADOT), such as on Amazon
Bedrock AgentCore Runtime, you do not need to add explicit instrumentation code. Adding the
instrumentation library to your project’s dependencies is enough. ADOT discovers it at startup and
activates it automatically.
Add the instrumentation library to your dependencies.
Note
Use version 0.1.3 or later. This is the earliest version tested with the evaluation service.

requirements.txt:
openinference-instrumentation-claude-agent-sdk>=0.1.3

pyproject.toml:
[project]
dependencies = [
"openinference-instrumentation-claude-agent-sdk>=0.1.3",
]

Note
Instrumentation is one step in setting up observability. To export telemetry for evaluation,
complete the full setup in Set up observability.

Claude Agent SDK

2257

How spans are identiﬁed
Claude Agent SDK is instrumented with the OpenInference convention, so AgentCore Evaluations
classiﬁes spans using the openinference.span.kind attribute.

Span type

Identifying attribute

Invoke agent

openinference.span.kind

= AGENT

Execute tool

openinference.span.kind

= TOOL

The Claude Agent SDK emits only AGENT and TOOL spans; it does not emit separate inference (LLM)
spans. The model metadata (model name, token usage) and the agent response are carried on the
AGENT span itself.

How evaluation ﬁelds are extracted
The Claude Agent SDK produces clean, plain-text agent input and output, so the user prompt and
agent response require no special parsing. Tool results, however, arrive as Anthropic content blocks
in the form [{"type": "text", "text": "…"}] . AgentCore Evaluations unwraps these
blocks and concatenates their text.
The location of this content depends on how telemetry was collected. The identifying attribute
(openinference.span.kind) is on the span in both cases. For more information, see Telemetry
setup and delivery.
From event records
With split telemetry, AgentCore Evaluations reads content from the event record correlated to each
span:
• User prompt and agent response: from the invoke agent span’s event record, in body.input
and body.output.
• Tool call: the tool name from the tool.name attribute and the tool call ID from tool.id on
the execute tool span. The tool arguments and result come from that span’s event record, in
body.input and body.output. AgentCore Evaluations unwraps the Anthropic content blocks
in the tool result.
Claude Agent SDK

2258

For more information, see Example spans in split telemetry.
From span attributes
With uniﬁed telemetry, the same content stays on the span as attributes:
• User prompt and agent response: from input.value and output.value on the invoke agent
span.
• Tool call: the tool name from tool.name, the tool call ID from tool.id, the arguments from
input.value, and the result from output.value, on the execute tool span. AgentCore
Evaluations unwraps the Anthropic content blocks in the tool result.
For more information, see Example spans in uniﬁed telemetry.

Example spans in split telemetry
With split telemetry, the span carries the identifying attributes and the content lives in a correlated
event record. The following examples are from a Claude Agent SDK travel-planning agent deployed
on Amazon Bedrock AgentCore Runtime.
Note
These examples are not complete spans. They show representative data from a real agent
interaction, with some ﬁelds omitted and long values truncated for readability.

Example
Invoke agent span
The openinference.span.kind attribute (AGENT) identiﬁes this as an invoke agent span.
The span carries the model metadata; the conversation content lives in the correlated event
record.
{
"traceId": "6a292d74406894815807e2751e61dd49",
"spanId": "a63aab3320ed8718",
"name": "ClaudeAgentSDK.ClaudeSDKClient.receive_response",
"kind": "INTERNAL",
Claude Agent SDK

2259

"scope": {
"name": "openinference.instrumentation.claude_agent_sdk",
"version": "0.1.5"
},
"attributes": {
"openinference.span.kind": "AGENT",
"llm.system": "anthropic",
"llm.model_name": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
"input.mime_type": "text/plain",
"output.mime_type": "text/plain",
"session.id": "sea-nyc-trip-2-turns-claude-adot"
},
"status": {
"code": "OK"
}
}

{
"spanId": "a63aab3320ed8718",
"traceId": "6a292d74406894815807e2751e61dd49",
"scope": {
"name": "openinference.instrumentation.claude_agent_sdk"
},
"body": {
"input": {
"messages": [
{ "role": "user", "content": "Hey, how can you help me" }
]
},
"output": {
"messages": [
{ "role": "assistant", "content": "Hello! I'm your travel planning
assistant ..." }
]
}
}
}

Execute tool span
The openinference.span.kind attribute (TOOL) identiﬁes this as an execute tool span;
tool.name holds the tool name and tool.id the tool call ID. The tool result lives in the
correlated event record as Anthropic content blocks, which AgentCore Evaluations unwraps.
Claude Agent SDK

2260

{
"traceId": "6a292deb7450b3155895da4f38cb579a",
"spanId": "909dcb4eb5f851ae",
"name": "mcp__travel__search_flights",
"kind": "INTERNAL",
"scope": {
"name": "openinference.instrumentation.claude_agent_sdk",
"version": "0.1.5"
},
"attributes": {
"openinference.span.kind": "TOOL",
"tool.name": "mcp__travel__search_flights",
"tool.id": "toolu_bdrk_01KmJhCRuEJJo6fswHbjCgFp",
"tool.parameters": "{\"origin\": \"SEA\", \"destination\": \"NYC\", \"date\":
\"2025-03-15\"}",
"input.mime_type": "application/json",
"output.mime_type": "application/json",
"session.id": "sea-nyc-trip-2-turns-claude-adot"
},
"status": {
"code": "OK"
}
}

{
"spanId": "909dcb4eb5f851ae",
"traceId": "6a292deb7450b3155895da4f38cb579a",
"scope": {
"name": "openinference.instrumentation.claude_agent_sdk"
},
"body": {
"input": {
"messages": [
{ "role": "user", "content": "{\"origin\": \"SEA\", \"destination\": \"NYC
\", \"date\": \"2025-03-15\"}" }
]
},
"output": {
"messages": [
{
"role": "assistant",
"content": "[{\"type\": \"text\", \"text\": \"{\\\"origin\\\": \\\"SEA\\
\", \\\"destination\\\": \\\"NYC\\\", \\\"flights\\\": [ ... ]}\"}]"
Claude Agent SDK

2261

}
]
}
}
}

Example spans in uniﬁed telemetry
With uniﬁed telemetry, the same content stays on the span attributes and no separate event record
is produced. The following examples are from a Claude Agent SDK travel-planning agent.
Note
These examples are not complete spans. They show representative data from a real agent
interaction, with some ﬁelds omitted and long values truncated for readability.

Example
Invoke agent span
The input.value attribute holds the user prompt, and the output.value attribute holds the
agent response, both as plain text.
{
"traceId": "561876bb17e9eaeb2f194ee515742b2f",
"spanId": "3b6815f5b3909a51",
"name": "ClaudeAgentSDK.ClaudeSDKClient.receive_response",
"kind": "INTERNAL",
"scope": {
"name": "openinference.instrumentation.claude_agent_sdk",
"version": "0.1.3"
},
"attributes": {
"openinference.span.kind": "AGENT",
"llm.system": "anthropic",
"llm.model_name": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
"input.value": "Hey, how can you help me",
"input.mime_type": "text/plain",
"output.value": "Hi there! ... How can I help you plan your next adventure?",
"output.mime_type": "text/plain",
Claude Agent SDK

2262

"session.id": "sea-nyc-trip-2-turns-claude-unified"
},
"status": {
"code": "OK"
}
}

Execute tool span
The input.value attribute holds the tool arguments, and the output.value attribute holds
the tool result as Anthropic content blocks, which AgentCore Evaluations unwraps.
{
"traceId": "7bb7e59a30d03fc0b9da5bf009a3b429",
"spanId": "d27b488965bbba99",
"name": "mcp__travel__search_flights",
"kind": "INTERNAL",
"scope": {
"name": "openinference.instrumentation.claude_agent_sdk",
"version": "0.1.3"
},
"attributes": {
"openinference.span.kind": "TOOL",
"tool.name": "mcp__travel__search_flights",
"tool.id": "toolu_bdrk_019yE7Gne1rZKE3UnVPAWjLq",
"tool.parameters": "{\"origin\": \"SEA\", \"destination\": \"NYC\", \"date\":
\"2025-03-15\"}",
"input.value": "{\"origin\": \"SEA\", \"destination\": \"NYC\", \"date\":
\"2025-03-15\"}",
"input.mime_type": "application/json",
"output.value": "[{\"type\": \"text\", \"text\": \"{\\\"origin\\\": \\\"SEA\\\",
\\\"destination\\\": \\\"NYC\\\", \\\"flights\\\": [ ... ]}\"}]",
"output.mime_type": "application/json",
"session.id": "sea-nyc-trip-2-turns-claude-unified"
},
"status": {
"code": "OK"
}
}

Claude Agent SDK

2263
