---
type: quickstart
title: Study Vault Quickstart
description: Start with approved learning paths, choose a domain route, add a hands-on lab when ready, and use review to retain knowledge. This page distinguishes canonical learning material from derived discovery and navigation.
tags: [quickstart, learning-paths, knowledge-governance, retention, labs]
verified:
  - by: openwiki/0.5.0
    at: 2026-09-05T08:40:09.738Z
sources:
  - id: openwiki-source-f9899ad835a2972666763144
    resource: repo://_index/topics.md
  - id: openwiki-source-f03c94ce5e7172928498691c
    resource: repo://_scripts/pipeline.py
  - id: openwiki-source-15abb03857bbe9acd0500e5e
    resource: repo://_scripts/prompts/new-source.md
  - id: openwiki-source-792d9b4fab22e29d325c1a72
    resource: repo://_scripts/prompts/promote-concept.md
  - id: openwiki-source-6f5839457ae5477b69a31a0c
    resource: repo://_scripts/prompts/weekly-refine.md
  - id: openwiki-source-faf78437a2e3fd3a1c2aa841
    resource: repo://_scripts/quiz_cli.py
  - id: openwiki-source-a849d3412f6dec7d48ad2424
    resource: repo://_scripts/quiz_session.py
  - id: openwiki-source-3157dd7558008dcc412dd11c
    resource: repo://labs/kiro-langfuse-eval/spec.md
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-5edd4864bd096c5be05523df
    resource: repo://topics/aws-devops-agent-operations.md
  - id: openwiki-source-62e8f8fd6f022a12af96e356
    resource: repo://topics/langgraph-application-development.md
  - id: openwiki-source-c33d884f1c1d6f98ee076703
    resource: repo://topics/llm-program-optimization-dspy.md
  - id: openwiki-source-633e63ec0f859dab1762db6b
    resource: repo://topics/llm-quality-evaluation-pipeline.md
  - id: openwiki-source-c9cc5872812918ea0caedf5a
    resource: repo://topics/mcp-record-replay-testing.md
  - id: openwiki-source-52965091ff4dbe494abea436
    resource: repo://topics/production-agent-runtime.md
generated: { by: "openwiki/0.5.0", at: "2026-09-05T08:40:09.738Z" }
---

# Study Vault Quickstart

This is a **routing page**, not a lesson or a publication workflow. Read canonical files for the knowledge itself: `concepts/` holds approved atomic material, and `topics/` holds curated sequences and prerequisites. Use OpenWiki pages and `_index/` to find those files, then follow the canonical links. A generated index can list drafts, so visibility in `_index/` is not approval.

> **Keep the authority boundary:** OpenWiki is derived navigation. It does not replace canonical material and does not authorize edits to `concepts/`, `topics/`, `quiz/`, or lab content. For the full boundary and change process, see [Approved Knowledge and Write Boundaries](architecture/knowledge-governance.md).

## The shortest useful loop

1. **Choose a curated topic** below and work through its canonical order rather than collecting isolated pages.
2. **Read concepts as needed** for the approved explanation, relationships, and examples behind that sequence.
3. **Practice with a lab** when you can state the problem and expected input/output; labs are optional and manual, not a required pipeline stage.
4. **Quiz and revisit** using the spaced-review entrypoint. Results update review scheduling; they do not publish or revise concepts.
5. **Maintain deliberately:** source intake, draft review, and human-approved promotion are the route for new knowledge. Periodic refinement can report issues and maintain quiz/index state, but cannot promote or edit concepts.

For the complete source-to-retention flow, including the human approval gate, use [From Source to Learning Path](workflows/knowledge-lifecycle.md). For the review-session lifecycle and scheduling behavior, use [Review, Quiz, and Maintenance Loop](workflows/review-and-retention.md).

### When you are adding knowledge rather than studying it

The repository supports video, PDF, repository, web-article, podcast, and EPUB ingestion. Ingested material is normalized under `sources/`; an agent can create candidates in `_drafts/`; a person reviews and explicitly approves a candidate before promotion creates or changes an approved concept. Topics then organize approved concepts into a learning order. Do not treat normalized sources, drafts, quiz state, or generated indexes as canonical knowledge.

The workflow guide has the source-specific commands and the full pipeline options. The important safety rule is that the configured pipeline dispatches agents but does not itself record human approval or enforce prompt write restrictions; review the verdict and diff before promotion.

## Choose a domain route

| Goal | Start with the canonical learning path | Use this map for orientation |
| --- | --- | --- |
| Build a broad foundation in scaling, data access, failure handling, consistency, and async work | [System Design Fundamentals](../topics/system-design-fundamentals.md) | [System Design Foundations Map](concepts/system-design-map.md) |
| Instrument distributed systems, operate telemetry delivery, or understand GenAI tracing | [OpenTelemetry Foundations](../topics/opentelemetry-foundations.md) | [Observability and Telemetry Domain Map](concepts/observability-map.md) |
| Make LLM behavior observable, evaluate it, build stateful agents, optimize programs, or work with MCP | [Production LLM Engineering](../topics/production-llm-engineering.md) | [LLM Engineering Domain Map](concepts/llm-engineering-map.md) |
| Learn workplace and everyday English vocabulary and idioms in a deliberate concrete-to-abstract order | [English: Workplace Vocabulary & Idioms](../topics/english-workplace-vocabulary.md) | [English Learning Contexts Map](concepts/english-learning-map.md) |

### Pick the focused LLM path when the broad route is too large

- Need a production feedback loop for quality, latency, and cost? Start with [LLM Quality and Evaluation Pipeline](../topics/llm-quality-evaluation-pipeline.md) or the broader [Production LLM Engineering](../topics/production-llm-engineering.md) path.
- Need durable, tool-using workflow execution and review pauses? Use [LangGraph Application Development](../topics/langgraph-application-development.md) or [Building Stateful Agents with LangGraph](../topics/langgraph-stateful-agents.md).
- Need systematic prompt/program improvement? Use [LLM Program Optimization with DSPy](../topics/llm-program-optimization-dspy.md).
- Need an interoperable agent-tool protocol and safe regression tests? Start with [MCP Protocol Foundations](../topics/mcp-protocol-foundations.md), then [MCP Record-Replay Testing](../topics/mcp-record-replay-testing.md).
- Need an operational agent context? Use [Production Agent Runtime](../topics/production-agent-runtime.md) or [AWS DevOps Agent Operations](../topics/aws-devops-agent-operations.md).

The maps explain handoffs: system-design foundations support reliable LLM and telemetry pipelines, while the observability route supplies the portable instrumentation and delivery layer beneath LLM-specific tracing and evaluation. They are navigational overlays—return to the linked topic or concept for the canonical material.

## Add hands-on practice

The current approved practice entrypoint is [Kiro CLI + Langfuse for Evaluation](../labs/kiro-langfuse-eval/spec.md), cataloged in [Hands-On Lab Catalog](labs/catalog.md). It is a 90–120 minute real-tool exercise that surrounds non-interactive Kiro CLI task calls with Langfuse dataset experiments, compares baseline and improved variants, and keeps rubric judging on a separately configured provider.

Read its canonical `spec.md` before running anything. The lab has no `spec.diataxis.md`, no mock fallback, and version-sensitive CLI behavior, so its setup script is an operational gate rather than a formality. Make predictions before execution, implement the intentionally stubbed evaluator, run the prescribed variants, investigate the deliberately inert usage-hook case, and only then trust the comparison. Keep credentials, predictions, expected answers, completed work, run outputs, and usage logs private and out of navigation content.

## Retain what you learned

Run a focused review session with:

```bash
.venv/bin/python3 -m _scripts.quiz_cli --count 10
```

The quiz adapter selects due questions before future questions, presents approved concept context, and persists each result’s updated schedule to the quiz bank. It intentionally does not turn quiz performance into a canonical content update. Use [Review, Quiz, and Maintenance Loop](workflows/review-and-retention.md) if you need concept filtering, session limits, SM-2 behavior, or the privacy and concurrency boundaries.

Weekly refinement is separate from the normal source pipeline. It can identify stale or contradictory material, write a report, update quiz scheduling from real results, and regenerate indexes; a needed concept correction remains a recommendation for human review. This separation keeps retention signals useful without letting them bypass draft-then-promote governance.

## Navigation checklist

- **Want to learn now?** Open a topic in the table and follow its order.
- **Need a cross-domain decision?** Use the matching map, then open its canonical links.
- **Want to build skill?** Check the [lab catalog](labs/catalog.md), then read the lab specification.
- **Want durable recall?** Run the quiz command and revisit the associated concepts.
- **Want to add or correct knowledge?** Follow the [knowledge lifecycle](workflows/knowledge-lifecycle.md), preserve human approval before promotion, and regenerate derived indexes instead of treating them as authority.
