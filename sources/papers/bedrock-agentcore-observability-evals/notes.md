# Amazon Bedrock AgentCore Developer Guide — Observability and Evaluations (selected chapters)

## Summary

This is a filtered subset of the AWS Bedrock AgentCore Developer Guide (a 3,428-page PDF), covering the Observability and Evaluations chapters only. AgentCore's observability model organizes agent telemetry into a three-tier hierarchy: sessions (a full user-agent interaction context) contain traces (one request-response cycle, possibly spanning multiple agents), which contain spans (a single measurable operation such as a tool call or model inference). Session-level metrics for AgentCore Runtime, Memory, Gateway, and built-in tools are emitted by default with no instrumentation; trace and span data require instrumenting agent code with the AWS Distro for OpenTelemetry (ADOT), except for Memory resources, which emit spans by default. All of this surfaces in a purpose-built "generative AI observability" view in Amazon CloudWatch, distinct from raw metrics/log browsing, and can be aggregated across AWS accounts into one monitoring account via CloudWatch cross-account observability (OAM).

AgentCore Evaluations builds on this telemetry to score agent quality automatically. It reads spans through two open conventions — OpenTelemetry's generative-AI semantic conventions and OpenInference — so any framework that emits telemetry in one of those shapes is supported without a framework-specific integration, alongside first-class support for Strands, LangGraph, OpenAI Agents, Vercel AI SDK, LlamaIndex, Google ADK, and Claude Agent SDK. The service classifies each span (invoke-agent, execute-tool, or inference), extracts the fields evaluators need (user prompt, agent response, tool inputs/outputs), and scores them with LLM-as-a-judge and code-based evaluators. Evaluation can run on-demand, in batch, or continuously online against live production traffic. A newer "Insights" capability (preview) goes beyond scoring: it clusters failures into a taxonomy, extracts user intent, and feeds findings into AgentCore's Recommendations API to produce an improved system prompt — closing a triage-to-optimization loop that can then be validated with A/B testing.

## Knowledge Map

- The sessions → traces → spans observability data model, and which resources emit which tier by default vs. by instrumentation
- CloudWatch's generative-AI observability dashboard as a purpose-built view over standard OTel/X-Ray data
- Cross-account telemetry aggregation for centralized platform/security monitoring
- The evaluation service's span-reading contract: how it classifies and extracts fields from any conforming trace, enabling generic framework support
- On-demand, batch, and continuous online evaluation as different points on one quality-monitoring spectrum
- Insights: clustering failures and successes across sessions, and feeding results into automated prompt optimization

## Key Takeaways

- Default telemetry differs by resource: Runtime/Gateway/built-in tools give you metrics for free, but traces and spans need ADOT instrumentation in agent code; only Memory emits spans out of the box.
- A session is the unit of user-facing context, a trace is one request-response cycle inside it (which may itself fan out across agents), and a span is the smallest measured operation — this hierarchy is the basis for progressive troubleshooting from broad to granular.
- Because evaluators read a documented, framework-agnostic contract (span kind + specific attributes/events), teams using an unlisted framework can still get evaluation support by matching that contract in their own instrumentation.
- Online evaluation continuously samples live traffic against configured evaluators, distinct from one-off on-demand or batch runs over a fixed time range or dataset.
- Insights adds a diagnostic layer on top of scoring — failure taxonomy, root-cause clustering, and user-intent extraction — and links directly into system-prompt recommendation and A/B-test validation, turning observability data into a closed improvement loop.
- Cross-account observability requires explicit account linking (via AWS Organizations or individual linking) and telemetry-type sharing (Metrics and Logs) before a monitoring account can see source-account agent data.
