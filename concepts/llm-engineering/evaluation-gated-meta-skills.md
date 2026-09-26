---
id: evaluation-gated-meta-skills
title: Evaluation-Gated Meta-Skills
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/agent-skills-day-3
related:
  - self-improving-agent-skill-memory-loop
  - agent-skill-evaluation-coverage
tags:
  - agent-skills
  - llm-engineering
  - evaluation
  - governance
---

# Evaluation-Gated Meta-Skills

- **One-sentence definition**: Evaluation-gated meta-skills create or revise skills from workflows, traces, and failures, but promote the change only after tests and review pass.
- **Why it exists / what problem it solves**: Agents can preserve useful procedures and repair repeated failures, but uncontrolled self-editing can game metrics, break routing, or grow a low-quality library.
- **Keywords**: meta-skills, draft tier, human review, promotion gate, traces, library evolution
- **Related concepts**: [[self-improving-agent-skill-memory-loop]], [[agent-skill-evaluation-coverage]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: Agent Skills

## Summary

A meta-skill is a skill that helps make other skills. It can extract a procedure from a successful trace, propose a repair after a failed evaluation, or maintain a library. Its proposal starts as a draft regardless of confidence; it must clear ordinary tests and human review before gaining more authority. This turns improvement into a controlled release process rather than automatic self-modification.

## Example

An agent notices that several support traces need the same account-verification step. A meta-skill drafts a support-verification skill and its tests. The draft stays inactive until routing, execution, regression, and budget evaluations pass and a reviewer approves it.

## Relationship to existing concepts

- [[self-improving-agent-skill-memory-loop]]: This supplies concrete gates for the broader capture-and-reuse feedback loop.
- [[agent-skill-evaluation-coverage]]: The coverage conditions provide the evidence a generated change needs before promotion.

## My questions

- Which failed evaluations are strong enough evidence to justify drafting a new skill?
- When can review requirements be reduced without inviting metric gaming?
