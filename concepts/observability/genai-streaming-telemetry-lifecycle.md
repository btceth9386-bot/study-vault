---
id: genai-streaming-telemetry-lifecycle
title: GenAI Streaming Telemetry Lifecycle
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-semantic-conventions-genai/
related:
  - llm-observability
  - telemetry-signal-model
tags:
  - observability
  - opentelemetry
  - generative-ai
  - streaming
  - tracing
---

# GenAI Streaming Telemetry Lifecycle

- **One-sentence definition**: Streaming telemetry keeps one inference span open from request start to the final chunk while recording responsiveness and final results.
- **Why it exists / what problem it solves**: Closing a span at the first chunk loses finish status and token usage, while recording only the end hides how quickly the user saw a response.
- **Keywords**: streaming, first chunk, span lifecycle, token usage, latency
- **Related concepts**: [[llm-observability]], [[telemetry-signal-model]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: OpenTelemetry Semantic Conventions for Generative AI

## Summary

A streaming answer has two meaningful moments: the first visible chunk and the completed response. Start the inference span before the request, record time to first chunk when output begins, add chunk events if they are useful, and close the same span only after the stream ends.

This keeps responsiveness, final token use, finish reason, and errors on one coherent operation.

## Example

A chat request starts at 12:00:00, emits its first token at 12:00:00.4, and finishes at 12:00:03.2. The inference span records a 0.4-second time to first chunk, a 3.2-second total duration, and the final input/output token counts.

## Relationship to existing concepts

- [[llm-observability]]: Streaming spans make perceived latency and final model outcomes inspectable together.
- [[telemetry-signal-model]]: Spans describe one stream, events capture chunk details, and metrics show fleet-wide responsiveness.

## My questions

- Which chunk details are worth retaining as events rather than summarized metrics?
- How should cancellation by the user differ from a provider-side stream failure?
