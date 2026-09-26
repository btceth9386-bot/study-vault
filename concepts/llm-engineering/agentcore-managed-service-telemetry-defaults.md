---
id: agentcore-managed-service-telemetry-defaults
title: AgentCore Managed-Service Telemetry Defaults
depth: 2
lab_status: not-started
last_reviewed: 2026-09-26
review_due: 2026-09-29
sources:
  - sources/papers/bedrock-agentcore-observability-evals/
  - sources/papers/bedrock-agentcore-eval-framework-examples
related:
  - agentcore-session-trace-span-hierarchy
  - genai-observability-dashboard-abstraction
  - agentcore-external-agent-observability-onboarding
  - llm-observability
  - opentelemetry-api-sdk-separation
tags:
  - llm-engineering
  - observability
  - aws
  - agentcore
---

# AgentCore Managed-Service Telemetry Defaults

- **One-sentence definition**: AgentCore provides metrics by default for its managed resource types, but spans and logs follow resource-specific rules — Agent and Memory spans need explicit enablement, Gateway spans are provided by the service itself, and richer application-level traces still require compatible instrumentation such as the AWS Distro for OpenTelemetry (ADOT).
- **Why it exists / what problem it solves**: Teams evaluating a managed agent platform's observability often assume "it's managed, so everything is automatic." AgentCore's actual behavior is asymmetric: default service metrics do not imply complete trace coverage, and understanding what a single tool call actually did still depends on tracing being turned on and the agent or framework emitting compatible spans. Knowing this boundary in advance prevents a team from mistaking dashboard-level metrics, or spans the service happens to provide at its own edge, for full visibility into a custom agent loop.
- **Keywords**: default telemetry, metrics vs. spans, ADOT, instrumentation gap, managed observability
- **Related concepts**: [[agentcore-session-trace-span-hierarchy]], [[genai-observability-dashboard-abstraction]], [[agentcore-external-agent-observability-onboarding]], [[llm-observability]], [[opentelemetry-api-sdk-separation]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: sources/papers/bedrock-agentcore-observability-evals/

## Summary

Imagine a car that comes with a dashboard showing speed and fuel level out of the box, but recording exactly which parts moved when — the engine timing, the transmission shifts — needs a separate diagnostic kit plugged in. AgentCore's telemetry works the same way: turn on any agent, gateway, or memory resource, and you immediately get metrics — counts, latencies, error rates — in CloudWatch with zero setup. But if you want to see the actual sequence of what happened inside one request (which spans make up a trace), the depth of that visibility depends on the resource: Gateway provides its own spans, Agent and Memory spans need to be explicitly turned on, and getting a rich, application-level trace of your own agent's internal reasoning still needs you to instrument the code with ADOT. The lesson: "managed" gives you the dashboard for free, but the diagnostic depth you get without extra work varies by resource, and full trace detail is opt-in everywhere.

"Opt-in" turns out to mean different things for different framework integrations, though, and the difference matters for how much work it actually takes. For several supported agent frameworks (LangGraph, OpenAI Agents, LlamaIndex, Google ADK, the Claude Agent SDK), running under ADOT with a compatible instrumentation library already added to the project's dependencies is enough — ADOT discovers and activates that library at startup with no instrumentation code required, so "opt-in" here means a dependency-file entry, not writing tracing code. Strands is a distinct case: its SDK ships with telemetry built directly into the framework, so there is no separate auto-discovered package at all. Vercel AI SDK agents, and other ADOT-native TypeScript integrations, get their instrumentation from the AWS Distro Node auto-instrumentation package rather than a per-framework library. In every case, dependency-only activation only produces spans — actually exporting that telemetry so it reaches CloudWatch still requires the separate observability setup (log group, export configuration) this concept already describes.

## Example

A team deploys an agent behind an AgentCore Gateway with a Memory resource attached, and does zero instrumentation work. In CloudWatch, they immediately see request counts and latency metrics for the Gateway and the Memory resource. When a customer reports a strange answer, the team opens the trace view expecting to see exactly what the agent did step by step — but without having enabled Agent and Memory spans, and without ADOT instrumentation in the agent's own code, they only see the Gateway's own service-provided spans, not what happened inside the agent's reasoning. They then enable spans for Agent and Memory and add ADOT to the agent code; the next request produces a full trace showing each tool call and model inference as separate spans.

## Relationship to existing concepts

- [[agentcore-session-trace-span-hierarchy]]: Describes the structural relationship between sessions, traces, and spans; this concept describes which of those tiers shows up automatically and which requires setup.
- [[genai-observability-dashboard-abstraction]]: The CloudWatch generative-AI view can only show trace and span detail once the underlying data is actually being emitted, per this concept's rules.
- [[agentcore-external-agent-observability-onboarding]]: Agents outside AgentCore Runtime start with none of these defaults and must configure the full instrumentation and export path manually — though for the frameworks with dependency-only auto-instrumentation, that manual path still skips writing instrumentation code, leaving only ADOT execution and export configuration to set up.
- [[llm-observability]]: Reinforces the general point that structured, step-level traces require deliberate instrumentation — they are not a byproduct of simply calling an LLM.
- [[opentelemetry-api-sdk-separation]]: ADOT is AWS's redistribution of the OpenTelemetry SDK, used here as the standard instrumentation path for richer application-level traces.

## Open questions

- Does enabling Agent and Memory spans introduce a measurable latency or cost overhead compared to metrics-only operation?
- How does AWS decide which future AgentCore resources will emit spans by default versus require explicit enablement?
