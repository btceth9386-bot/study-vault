---
id: genai-operation-span-taxonomy
title: GenAI Operation Span Taxonomy
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-semantic-conventions-genai/
related:
  - llm-observability
  - semantic-conventions-as-telemetry-schema
tags:
  - observability
  - opentelemetry
  - generative-ai
  - tracing
---

# GenAI Operation Span Taxonomy

- **One-sentence definition**: A GenAI operation span taxonomy gives inference, embeddings, retrieval, memory, and tool execution their own trace spans.
- **Why it exists / what problem it solves**: One large "AI request" span cannot show which step caused a delay, cost, or error.
- **Keywords**: spans, inference, retrieval, memory, tools, tracing
- **Related concepts**: [[llm-observability]], [[semantic-conventions-as-telemetry-schema]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: OpenTelemetry Semantic Conventions for Generative AI

## Summary

A trace is a timeline of work. This taxonomy labels the important stops on that timeline instead of calling all of them a model call. An inference span covers the request to a model; retrieval, memory, embeddings, and tool execution get spans of their own.

That separation makes a slow or failed answer explainable. It also gives dashboards a portable vocabulary, so the same query can work across model providers and frameworks.

## Example

A support agent retrieves a policy document, asks a model to draft an answer, then calls a CRM tool. Its trace has a retrieval span, an inference span, and a tool-execution span. If the response is slow, the trace can show whether document search, the model, or the CRM caused it.

## Relationship to existing concepts

- [[llm-observability]]: The taxonomy supplies the detailed steps that LLM observability records.
- [[semantic-conventions-as-telemetry-schema]]: Stable span names and attributes make these steps comparable across tools.

## My questions

- Which application-specific operations deserve their own span rather than an event?
- How should nested tool calls be represented without making traces hard to read?
