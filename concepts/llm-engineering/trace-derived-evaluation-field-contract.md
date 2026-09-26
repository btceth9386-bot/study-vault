---
id: trace-derived-evaluation-field-contract
title: Trace-Derived Evaluation Field Contract
depth: 2
lab_status: not-started
last_reviewed: 2026-09-26
review_due: 2026-09-29
sources:
  - sources/papers/bedrock-agentcore-observability-evals/
  - sources/papers/bedrock-agentcore-eval-framework-examples
related:
  - model-agnostic-evaluation-provider-abstraction
  - trace-aware-agent-evaluation
  - genai-operation-span-taxonomy
  - agentcore-insights-triage-loop
tags:
  - llm-engineering
  - evaluation
  - observability
  - aws
  - agentcore
---

# Trace-Derived Evaluation Field Contract

- **One-sentence definition**: AgentCore Evaluations reads evaluation-compatible spans in a session, classifies each one as an invoke-agent, execute-tool, or inference span based on recognized OpenTelemetry or OpenInference attributes, and extracts the prompts, responses, and tool inputs and outputs it needs from documented span attributes or correlated event records — using the same logic whether or not the producing framework has dedicated support.
- **Why it exists / what problem it solves**: An evaluation service that hard-codes support for each agent framework's internal data shapes cannot scale to new or custom frameworks, and forces every new framework integration to be built and maintained from scratch. Defining a stable, framework-agnostic contract instead — which span kinds exist, which attributes identify each kind, and where the content values live — lets the evaluator score any agent whose instrumentation matches that contract. This is what makes "generic framework support" possible: not a degraded fallback, but the exact same mechanism used for named frameworks like Strands and LangGraph.
- **Keywords**: span classification, generic framework support, OpenInference, OTel GenAI semantic conventions, field extraction
- **Related concepts**: [[model-agnostic-evaluation-provider-abstraction]], [[trace-aware-agent-evaluation]], [[genai-operation-span-taxonomy]], [[agentcore-insights-triage-loop]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: sources/papers/bedrock-agentcore-observability-evals/

## Summary

Imagine hiring a grader who can score essays written in any language, as long as each essay clearly labels its introduction, body, and conclusion — the grader does not need to know the language itself, only where to look for each part. AgentCore's evaluation field contract works the same way: instead of teaching the evaluator every agent framework's internal data structures, AWS defines a small, fixed vocabulary of span kinds (invoke-agent, execute-tool, inference) and says exactly which attributes identify each kind and where the actual content — the user's prompt, the agent's answer, a tool's inputs and outputs — should be found. Any framework whose instrumentation follows that labeling, whether it is a framework AWS has explicitly documented or one a team built themselves, gets scored the same way. This excludes spans that don't carry the recognized identifying attributes, and infrastructure-only spans that aren't evaluation-relevant at all.

The "recognized OpenTelemetry or OpenInference attributes" phrase covers two genuinely distinct conventions, not one, because the instrumentation ecosystem for agent frameworks grew out of two separate communities. The primary OpenTelemetry path classifies spans with `gen_ai.operation.name`, using values `invoke_agent`, `execute_tool`, and `chat` for the three span kinds. OpenInference classifies spans with `openinference.span.kind` instead, using values `AGENT` (or `CHAIN` for an outer wrapping span in a nested agent tree), `TOOL`, and `LLM`. AWS also documents other OpenTelemetry-adjacent fallback attributes, such as `traceloop.span.kind`, for instrumentation that doesn't follow either primary convention exactly. Several frameworks — LangGraph, OpenAI Agents, and LlamaIndex among them — support both OpenTelemetry and OpenInference as alternative instrumentation-library choices for the same framework, and the evaluation service extracts identical values from either one a team happens to have picked.

Separately from which convention identifies a span, the "documented span attributes or correlated event records" phrase in this concept's definition names two distinct, officially-supported telemetry delivery modes. In split telemetry, ADOT moves the larger conversation-content payloads into a separate event record and correlates it back to its span by trace and span ID. In unified telemetry, that same content stays with the span itself — but its exact representation there still varies by instrumentation library: most libraries carry it as span attributes, while some, such as Strands, carry it as inline span events attached to the span. In both modes, the span's identifying attribute (the `gen_ai.operation.name` or `openinference.span.kind` value that classifies it) stays on the span itself; only the location of the conversation *content* changes between modes.

## Example

A team builds a custom agent with a homegrown orchestration loop — no LangGraph, no Strands, nothing on AgentCore's named-framework list. Instead of giving up on automated evaluation, they instrument their code so the top-level agent call emits a span with the recognized "invoke-agent" attributes, each tool call emits a span with the recognized "execute-tool" attributes and puts the tool's input and output in the documented locations, and each model call emits an "inference" span with the prompt and response in the expected place. AgentCore Evaluations classifies and scores these spans exactly as it would for a named framework's traces, because it never needed to know the framework — only the contract.

A second example shows the contract tolerating a framework that legitimately emits fewer than three span kinds by design, not by broken instrumentation: the Claude Agent SDK emits only AGENT and TOOL spans — no separate inference span at all — folding the model's metadata (model name, token usage) and the agent's response directly onto the AGENT span instead. The contract still classifies and scores this correctly, because it recognizes whichever kinds of spans are actually present and knows where each kind's content lives, rather than requiring a fixed one-span-per-kind shape on every trace.

## Relationship to existing concepts

- [[model-agnostic-evaluation-provider-abstraction]]: That concept abstracts over which model *provider* answers a call during evaluation; this concept abstracts over which agent *framework* produced the trace being evaluated — a different axis of the same generic-support philosophy.
- [[trace-aware-agent-evaluation]]: Uses recorded trajectories as evaluation input in general; this concept is the specific mechanism AgentCore uses to turn a raw trace into the structured fields an evaluator can act on.
- [[genai-operation-span-taxonomy]]: Supplies the underlying operation-boundary vocabulary (inference, tool call, retrieval) that this contract's span classification is built from — but that taxonomy doesn't itself map the two concrete, non-identical attribute schemes (OpenTelemetry's `gen_ai.operation.name` and OpenInference's `openinference.span.kind`) that different instrumentation libraries actually use to express it, which is the specific gap this contract's classification logic fills.
- [[agentcore-insights-triage-loop]]: Insights' failure analysis and root-cause tracing depend on this contract to reliably identify which span, and which extracted field, is implicated in a given failure.

## Open questions

- A framework that *deliberately* omits a span kind (like Claude Agent SDK's lack of a separate inference span) is handled cleanly, as the second example shows — but what happens to evaluation quality when instrumentation is merely *broken* or *incomplete* rather than intentionally collapsed? Does the contract distinguish "this framework never emits inference spans" from "this trace is missing an inference span it should have had," or does the latter silently produce an incomplete score?
- How often does AWS need to revise this contract as new span kinds (e.g., retrieval, multi-agent handoff) become common enough to need their own classification?
