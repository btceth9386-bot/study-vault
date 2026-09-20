---
type: quickstart
title: Study Vault Quickstart
description: Route study through canonical topics and concepts, then use optional labs and spaced review. For contributions, follow the source-scoped verified-draft lifecycle without confusing derived navigation with approval.
tags: [quickstart, learning-paths, knowledge-governance, retention, labs]
verified:
  - by: openwiki/0.5.0
    at: 2026-09-06T11:16:33.676Z
sources:
  - id: openwiki-source-f9899ad835a2972666763144
    resource: repo://_index/topics.md
  - id: openwiki-source-f03c94ce5e7172928498691c
    resource: repo://_scripts/pipeline.py
  - id: openwiki-source-15abb03857bbe9acd0500e5e
    resource: repo://_scripts/prompts/new-source.md
  - id: openwiki-source-792d9b4fab22e29d325c1a72
    resource: repo://_scripts/prompts/promote-concept.md
  - id: openwiki-source-1d05bd79aceb2c744ed29ee7
    resource: repo://_scripts/prompts/review-drafts.md
  - id: openwiki-source-faf78437a2e3fd3a1c2aa841
    resource: repo://_scripts/quiz_cli.py
  - id: openwiki-source-a849d3412f6dec7d48ad2424
    resource: repo://_scripts/quiz_session.py
  - id: openwiki-source-48472eed2b7d05affcbff47f
    resource: repo://labs/kiro-langfuse-eval/manifest.yaml
  - id: openwiki-source-c2819cde93975d4de977b166
    resource: repo://labs/README.md
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
generated: { by: "openwiki/0.5.0", at: "2026-09-06T11:16:33.676Z" }
---

# Study Vault Quickstart

This is a routing page, not a lesson or an approval workflow. **Canonical learning material lives in `concepts/` and `topics/`**: concepts explain reusable ideas, while topics provide a curated order and prerequisites. OpenWiki and `_index/` help discovery, but are derived navigation—not authority to edit concepts, topics, quiz data, or labs. An index can expose a draft, so an entry is not proof of approval. See [Approved Knowledge and Write Boundaries](architecture/knowledge-governance.md) for the ownership model.

## Take the shortest route

| If you want to… | Go here | Then |
| --- | --- | --- |
| **Study a subject now** | Choose a canonical topic in [the domain routes](#choose-a-domain-route). | Follow its listed order and open its linked concepts as needed. |
| **Add material from a source** | Use [the verified contribution route](#add-knowledge-through-verification). | Normalize the source, independently review its drafts, promote only verified work, then curate topics. |
| **Practice an approved idea** | Open the [Hands-On Lab Catalog](labs/catalog.md). | Read a capsule's canonical `spec.md`; labs are an optional, explicit branch. |
| **Retain what you learned** | Run the [review command](#retain-what-you-learned). | Use [Review, Quiz, and Maintenance Loop](workflows/review-and-retention.md) for session and scheduling details. |

## Choose a domain route

| Goal | Canonical learning path | Orientation map |
| --- | --- | --- |
| Build foundations in scaling, data access, failure handling, consistency, and asynchronous work | [System Design Fundamentals](../topics/system-design-fundamentals.md) | [System Design Foundations Map](concepts/system-design-map.md) |
| Instrument distributed systems or operate telemetry delivery | [OpenTelemetry Foundations](../topics/opentelemetry-foundations.md) | [Observability and Telemetry Domain Map](concepts/observability-map.md) |
| Build observable, evaluated, stateful, and durable LLM applications | [Production LLM Engineering](../topics/production-llm-engineering.md) | [LLM Engineering Domain Map](concepts/llm-engineering-map.md) |
| Learn workplace and everyday English vocabulary and idioms | [Workplace Vocabulary & Idioms](../topics/english-workplace-vocabulary.md) | [English Learning Contexts Map](concepts/english-learning-map.md) |

Use a map to orient across domains, then return to the linked topic or concept for canonical material. System-design foundations support reliable LLM and telemetry systems; the observability route provides the instrumentation and delivery foundation beneath LLM-specific tracing and evaluation.

### Focus an LLM route

- For quality, latency, and cost feedback loops, start with [LLM Quality and Evaluation Pipeline](../topics/llm-quality-evaluation-pipeline.md).
- For stateful application work, choose [LangGraph Application Development](../topics/langgraph-application-development.md).
- For program or prompt optimization, use [LLM Program Optimization with DSPy](../topics/llm-program-optimization-dspy.md).
- For protocol foundations and regression protection, take [MCP Protocol Foundations](../topics/mcp-protocol-foundations.md), then [MCP Record-Replay Testing](../topics/mcp-record-replay-testing.md).
- For deployment and operating context, use [Production Agent Runtime](../topics/production-agent-runtime.md) or [AWS DevOps Agent Operations](../topics/aws-devops-agent-operations.md).

## Add knowledge through verification

Start by normalizing an input with the appropriate ingest tool (video, PDF, repository, article, podcast, or EPUB). Then run the per-source dispatcher against the resulting `sources/<type>/<slug>` directory:

```bash
.venv/bin/python3 _scripts/pipeline.py sources/repos/<owner>-<repo>
```

The full route is deliberately gated:

1. The ingest role completes the normalized source asset and creates candidate drafts in `_drafts/`; it cannot write `concepts/` or create quiz questions.
2. An **independent** reviewer handles only drafts associated with that source and persists `verified`, `needs-decision`, or `rejected` with evidence. A learner resolves only material merge, scope, contradiction, or learning-priority exceptions.
3. The dispatcher groups the source's persisted verdicts. It passes only `verified` drafts to promotion and runs topic generation only after promotion succeeds. With no verified drafts, both promotion and topics are skipped; pending, exceptional, and rejected drafts remain records.
4. After a learner resolves an exception, select one draft explicitly for manual promotion rather than treating an entire batch as approved:

```bash
.venv/bin/python3 _scripts/pipeline.py _drafts/<concept-id>.md --step promote
```

Promotion is the route that creates or updates canonical concepts and their quiz/index outputs; topics organize the promoted concepts into learning paths. The runner dispatches configured agent commands and uses their exit status to decide whether a step succeeded—it does not sandbox agent writes, inspect a diff, or record a learner decision. Preview a dispatch and inspect the resulting changes:

```bash
.venv/bin/python3 _scripts/pipeline.py sources/repos/<owner>-<repo> --dry-run
```

For the full lifecycle, decision meanings, and focused pipeline test, see [From Source to Learning Path](workflows/knowledge-lifecycle.md) and [Automation, Validation, and Safe Change Surfaces](operations/automation-and-validation.md).

## Practice with a lab

Labs are outside the default source pipeline and require the explicit `lab` step. The repository keeps recovery capsules: `manifest.yaml` identifies a lab, its linked concepts, external workspace, and recovery contract, while `spec.md` is the canonical learning contract. Runnable scaffolds, learner work, answer keys, generated review artifacts, outputs, and credentials remain outside the repository. Select an appropriate capsule from the [Hands-On Lab Catalog](labs/catalog.md), use its linked concepts for theory, and read its `spec.md` before acting.

## Retain what you learned

Run a focused spaced-review session:

```bash
.venv/bin/python3 -m _scripts.quiz_cli --count 10
```

Review results update scheduling; they do not publish or revise canonical concepts. Use [Review, Quiz, and Maintenance Loop](workflows/review-and-retention.md) for filters, session behavior, scheduling, and privacy limits.

## Refresh this navigation deliberately

OpenWiki remains a derived navigation layer. During the pilot, refresh it manually only after a reviewed canonical batch is ready; do not make it a scheduled workflow. Refreshing OpenWiki neither approves content nor authorizes edits to canonical concepts, topics, quiz data, or labs.
