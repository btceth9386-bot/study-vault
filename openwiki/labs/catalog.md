---
type: lab catalog
title: Hands-On Lab Catalog
description: Catalog of the three repository-resident lab recovery capsules, their approved concept links, and canonical specifications. Use it to select or recover a lab while keeping runnable work and review artifacts in the external workspace.
tags: [labs, hands-on-learning, recovery-capsules, llm-engineering, observability]
verified:
  - by: openwiki/0.5.0
    at: 2026-09-06T04:14:39.619Z
sources:
  - id: openwiki-source-e11325fe5026a3874a69376f
    resource: repo://_scripts/prompts/lab-design.md
  - id: openwiki-source-92eab7e5213be05201442af4
    resource: repo://_scripts/prompts/lab-review.md
  - id: openwiki-source-e119253b3c3737247dc63f2a
    resource: repo://.openwikiignore
  - id: openwiki-source-48472eed2b7d05affcbff47f
    resource: repo://labs/kiro-langfuse-eval/manifest.yaml
  - id: openwiki-source-3157dd7558008dcc412dd11c
    resource: repo://labs/kiro-langfuse-eval/spec.md
  - id: openwiki-source-51f5b3747f7658cbaf70609f
    resource: repo://labs/langgraph-state-flow/manifest.yaml
  - id: openwiki-source-2483947c0005a39ae355f8fb
    resource: repo://labs/langgraph-state-flow/spec.md
  - id: openwiki-source-ff244e76d1b895b26904dcf6
    resource: repo://labs/otel-collector-positioning/manifest.yaml
  - id: openwiki-source-86239438e8660e4bbacd1c6a
    resource: repo://labs/otel-collector-positioning/spec.md
  - id: openwiki-source-c2819cde93975d4de977b166
    resource: repo://labs/README.md
generated: { by: "openwiki/0.5.0", at: "2026-09-06T04:14:39.619Z" }
---

# Hands-On Lab Catalog

This is a navigation page for the repository's **three recovery capsules**. A capsule preserves a lab's identity, approved concept links, recovery location, and canonical learning contract; it is not the runnable lab. Read the linked `spec.md` to understand a lab's goal, core task, intentional failure or comparison, prerequisites, and acceptance criteria. OpenWiki is derived navigation: it neither replaces those canonical files nor authorizes edits to the capsules, concepts, or external lab workspace.

## Catalog

| Lab | Setup and time box | Approved concepts | Canonical specification |
| --- | --- | --- | --- |
| **Kiro CLI + Langfuse for Evaluation** | `real-tool`; 90–120 min | [LLM Observability](../../concepts/llm-engineering/llm-observability.md); [LLM-as-Judge Evaluation](../../concepts/llm-engineering/llm-as-judge-evaluation.md); `acp-agent-backend-for-ides` | [`labs/kiro-langfuse-eval/spec.md`](../../labs/kiro-langfuse-eval/spec.md) |
| **LangGraph State Flow — Reducer vs. Overwrite** | `local-mock`; 20–30 min | [LangGraph StateGraph State Schema](../../concepts/llm-engineering/langgraph-stategraph-state-schema.md); [LangGraph Channels and Reducers](../../concepts/llm-engineering/langgraph-channels-and-reducers.md) | [`labs/langgraph-state-flow/spec.md`](../../labs/langgraph-state-flow/spec.md) |
| **OpenTelemetry Positioning — Where the Collector Sits** | `local-mock`; 45–75 min | [Telemetry Signal Model](../../concepts/observability/telemetry-signal-model.md); [OpenTelemetry Collector Pipeline Architecture](../../concepts/observability/collector-pipeline-architecture.md); `otlp-vendor-neutral-telemetry-protocol`; `opentelemetry-api-sdk-separation` | [`labs/otel-collector-positioning/spec.md`](../../labs/otel-collector-positioning/spec.md) |

The concept links above are the approved starting points for theory. The canonical specification is the entrypoint for the corresponding exercise; it is not a completed implementation or a record of any learner run.

## What the repository preserves

Each lab directory contains two recovery-contract files:

- **`manifest.yaml`** identifies the capsule, its `status`, concept IDs, external `workspace_path`, canonical-spec filename, generator prompt, review URLs, and the artifact categories to regenerate. Its `spec_sha256` records the canonical specification's SHA-256 value for damage detection.
- **`spec.md`** is the repository-resident canonical learning contract. It defines the learning intent and the behavior a recovered lab must preserve, including the scaffold boundary, learner-owned core, failure or comparison case, prerequisites, and acceptance criteria.

The current manifests mark all three capsules `scaffolded`. Their `canonical_spec` is `spec.md`, and their recovery workspace is under `~/orb_pods_share/<lab-id>/`.

```mermaid
flowchart LR
    Capsule["Repository recovery capsule"] --> Manifest["manifest.yaml identity and recovery metadata"]
    Capsule --> Spec["spec.md canonical learning contract"]
    Manifest --> Workspace["External orb_pods_share workspace"]
    Spec --> Workspace
    Workspace --> Scaffold["Runnable scaffold and learner work"]
    Workspace --> Narrative["Diataxis narrative and review artifacts"]
```

*The repository retains the recovery contract; the external workspace holds reconstructed runnable and presentation artifacts.*

## Recovery and ownership boundary

To recover a lost lab, provide its `manifest.yaml` and `spec.md` to an agent and follow [`_scripts/prompts/lab-design.md`](../../_scripts/prompts/lab-design.md). Recovery targets equivalent learning behavior and acceptance criteria, not byte-for-byte reproduction. The design workflow places the complete lab in the external workspace and only then creates the minimal repository capsule.

The follow-on review workflow is also external and happens after a learner attempt. [`lab-review.md`](../../_scripts/prompts/lab-review.md) reads the external specification, learner predictions, learner-owned core, and private answer key; it must stop rather than grade when the attempt is empty. It is feedback and retention support, not catalog content.

### Deliberately outside this repository

Do not treat a manifest's regeneration list or review URLs as proof that these files are present here. Runnable scaffolds and fixtures, learner work, `predictions.md`, answer keys, Diátaxis narratives, review sites and pages, deployment material, generated runs, usage logs, and credentials belong outside this repository. The repository ignore policy also excludes private learner state and generated lab artifacts from its canonical knowledge surface.

This boundary prevents a catalog from exposing solutions, predictions, credentials, operational output, or review evidence. It also preserves the draft-then-promote rule: discovering a lab through OpenWiki does not authorize a change to canonical knowledge or lab content.

## Choosing a lab

- Choose **Kiro CLI + Langfuse for Evaluation** to practice a real-tool evaluation and observability integration, including a separately configured judge provider and real operational prerequisites. Read the specification before deciding whether its cost and access requirements are appropriate.
- Choose **LangGraph State Flow — Reducer vs. Overwrite** for a compact local exercise on how a `StateGraph` state schema and reducer semantics affect accumulated versus replaced state.
- Choose **OpenTelemetry Positioning — Where the Collector Sits** for a local exercise on separating telemetry signal types and routing them through Collector pipelines to appropriate backends.

For broader orientation before selecting a capsule, use the [LLM Engineering Domain Map](../concepts/llm-engineering-map.md) or the [Observability and Telemetry Domain Map](../concepts/observability-map.md). The [Study Vault Quickstart](../quickstart.md) and [From Source to Learning Path](../workflows/knowledge-lifecycle.md) explain the repository's authority and learning lifecycle boundaries.
