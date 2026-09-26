---
id: agentcore-external-agent-observability-onboarding
title: AgentCore External-Agent Observability Onboarding
depth: 2
lab_status: not-started
last_reviewed: 2026-09-26
review_due: 2026-09-29
sources:
  - sources/papers/bedrock-agentcore-observability-evals/
related:
  - agentcore-managed-service-telemetry-defaults
  - genai-observability-dashboard-abstraction
  - agentcore-session-trace-span-hierarchy
  - multi-platform-agent-gateway
  - protocol-based-agent-access-surface
tags:
  - llm-engineering
  - observability
  - aws
  - agentcore
---

# AgentCore External-Agent Observability Onboarding

- **One-sentence definition**: AgentCore documents two separate observability onboarding paths — agents deployed to AgentCore Runtime through the AgentCore CLI get automatic OpenTelemetry instrumentation, while agents hosted elsewhere (Lambda, ECS, EC2, or anywhere else) must configure compatible framework instrumentation, the ADOT SDK or Lambda layer, a CloudWatch log group, AWS settings, and OpenTelemetry export environment variables to send telemetry into the same generative-AI observability views.
- **Why it exists / what problem it solves**: A managed agent platform's observability story is incomplete if it only works for agents fully hosted on that platform — real organizations run agents across mixed infrastructure, keeping some on existing Lambda, ECS, or EC2 fleets for migration, cost, or compliance reasons, and still need one place to see all of them. By publishing the exact configuration that reproduces what AgentCore Runtime does automatically, AgentCore lets externally hosted agents opt into the identical observability surface — the same CloudWatch dashboard, the same trace and span shape — without a full migration to the managed runtime first.
- **Keywords**: external hosting, ADOT, OpenTelemetry environment variables, hybrid deployment, observability parity
- **Related concepts**: [[agentcore-managed-service-telemetry-defaults]], [[genai-observability-dashboard-abstraction]], [[agentcore-session-trace-span-hierarchy]], [[multi-platform-agent-gateway]], [[protocol-based-agent-access-surface]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: sources/papers/bedrock-agentcore-observability-evals/

## Summary

Deploying an agent through the AgentCore CLI onto AgentCore Runtime gets you OpenTelemetry instrumentation for free — the platform wires it up as part of that deployment path. But plenty of real agents will not live there: a team might keep an existing agent on Lambda because it is already deployed and working, or on ECS because of a compliance requirement that predates AgentCore. Rather than force a migration to get observability, AWS documents the exact recipe to reproduce the same result manually: pick an instrumentation library compatible with your framework, add the ADOT SDK or Lambda layer, point it at a CloudWatch log group, set the right AWS credentials, and set a specific list of OpenTelemetry environment variables. Follow that recipe correctly, and the externally hosted agent's telemetry lands in the exact same CloudWatch generative-AI observability view as a native AgentCore Runtime agent — same shape, same dashboard, no separate tooling.

## Example

A company has a customer-support agent already running on ECS, built with LangChain, from before AgentCore existed. Rather than rewrite and redeploy it onto AgentCore Runtime, they add the ADOT SDK to the ECS task, set `AGENT_OBSERVABILITY_ENABLED=true` and the documented OTLP export environment variables pointing at a CloudWatch log group, and configure AWS credentials for the task role. After redeploying with these settings, the ECS-hosted agent's sessions, traces, and spans appear in the same generative-AI observability dashboard the team already uses for their AgentCore Runtime agents — letting one team monitor both fleets from one screen.

## Relationship to existing concepts

- [[agentcore-managed-service-telemetry-defaults]]: Describes the defaults that apply to AgentCore Runtime-hosted resources; this concept covers the case where none of those defaults apply because the agent is not on AgentCore Runtime at all. That concept's dependency-only auto-instrumentation mechanism still applies here too: an externally hosted agent using a supported framework skips writing instrumentation code, but still needs ADOT actually running in that environment and the export configuration this concept describes.
- [[genai-observability-dashboard-abstraction]]: This onboarding path is the mechanism that lets externally hosted agents feed the same dashboard as native ones.
- [[agentcore-session-trace-span-hierarchy]]: The goal of correct onboarding is to reproduce this same session/trace/span structure for non-native agents.
- [[multi-platform-agent-gateway]]: Both concepts reflect a managed platform choosing interoperability over forcing full migration.
- [[protocol-based-agent-access-surface]]: Another instance of a managed platform defining an explicit, documented interop contract rather than requiring lock-in to its own hosting.

## Open questions

- Does telemetry parity between AgentCore-hosted and externally hosted agents extend to every AgentCore feature (e.g., Insights, online evaluation), or only to the base observability dashboard?
- How much does this environment-variable configuration drift as ADOT versions change, and how would a team detect that drift?
