---
id: authority-tiered-agent-skills
title: Authority-Tiered Agent Skills
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/agent-skills-day-3
related:
  - agent-space-access-boundary
  - trace-aware-agent-evaluation
tags:
  - agent-skills
  - llm-engineering
  - governance
  - risk-management
---

# Authority-Tiered Agent Skills

- **One-sentence definition**: Authority-tiered skills move from read-only to draft-only to action-allowed only as their evidence and review requirements become stronger.
- **Why it exists / what problem it solves**: Looking up information, preparing a reviewable artifact, and changing a real system have different failure costs and need different release thresholds.
- **Keywords**: read-only, draft-only, action-allowed, evidence, approvals, reliability
- **Related concepts**: [[agent-space-access-boundary]], [[trace-aware-agent-evaluation]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: Agent Skills

## Summary

An agent should earn permission in small steps. A read-only skill may retrieve information; a draft-only skill may prepare work for a human to approve; an action-allowed skill may make a real change. Each step raises the potential harm, so it also raises the required reliability evidence and reviewer sign-off.

## Example

A refund helper first reads an order and summarizes eligibility. The next tier drafts a refund request for a support agent. Only after stronger testing, security review, and accountable approval may it submit the refund itself.

## Relationship to existing concepts

- [[agent-space-access-boundary]]: The access boundary controls what systems a skill can reach at each authority tier.
- [[trace-aware-agent-evaluation]]: Trace evidence helps establish that an action-capable skill follows safe sequences.

## My questions

- Which actions should remain draft-only even after a skill has strong test evidence?
- How should authority be reduced quickly when a newly promoted skill misbehaves?
