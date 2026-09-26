---
id: immutable-versioned-endpoints-for-agent-config
title: Immutable Versioned Endpoints for Agent Config
depth: 2
lab_status: not-started
last_reviewed: 2026-09-26
review_due: 2026-09-29
sources:
  - sources/papers/bedrock-agentcore-agentops
related:
  - config-bundle-ab-testing-for-agent-behavior
tags:
  - aws
  - agentcore
  - deployment
  - reliability
---

# Immutable Versioned Endpoints for Agent Config

- **One-sentence definition**: Every update to an AgentCore harness or Runtime automatically creates a new, complete, immutable configuration version, and named endpoints — plus an auto-updating `DEFAULT` endpoint — let different environments point at different versions independently, so promoting a change to production is a separate, explicit act from creating the change.
- **Why it exists / what problem it solves**: Deploying a new agent configuration straight into the only environment that exists is risky: there's no way to try a change against staging traffic while production keeps running the previous, known-good behavior, and no fast way to undo a mistake once it's live. Making every version immutable and self-contained — model, system prompt, tools, memory, limits, and environment all captured together in one version — guarantees a version can never be silently altered after the fact. An endpoint is just a named pointer at one specific version: `DEFAULT` always tracks the latest version automatically, which is convenient while iterating, but any other named endpoint (such as `production-endpoint`) only moves when someone explicitly updates it. That separation means production stays pinned to a known version until a person deliberately repoints it, and "rolling back" is nothing more than repointing an endpoint to the previous version number — no redeploy required.
- **Keywords**: immutable versioning, named endpoints, DEFAULT endpoint, rollback, environment pinning
- **Related concepts**: [[config-bundle-ab-testing-for-agent-behavior]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: Amazon Bedrock AgentCore Developer Guide — Operations, reliability, and governance

## Summary

Think of each version as a sealed, dated snapshot — once it exists, nothing about it can change, ever. An endpoint is a labeled sticky note that says "production points at snapshot #7." Updating the agent doesn't erase snapshot #7 or edit it; it creates snapshot #8 and leaves the production sticky note exactly where it was, still pointing at #7, until someone deliberately moves it. This is what makes a rollback trivial and safe: moving a sticky note back to #7 is instant and can't fail halfway through the way a redeploy can.

## Example

A team updates their harness's system prompt, creating version 5 from version 4. The `DEFAULT` endpoint automatically now points at version 5, so ad hoc testing immediately sees the new prompt. Their `production-endpoint`, however, still points at version 4 — real users see no change. After confirming version 5 behaves correctly, the team runs `update-harness-endpoint` to repoint `production-endpoint` to version 5. A week later, a subtle regression surfaces; they repoint `production-endpoint` back to version 4 in seconds, without touching version 5 or redeploying anything.

## Relationship to existing concepts

- [[config-bundle-ab-testing-for-agent-behavior]]: A related but more specialized immutable-snapshot mechanism, applied specifically to prompt, model-ID, and tool-description changes for the purpose of running a statistically validated A/B test. This concept's version-and-endpoint mechanism is the more general deployment-safety pattern that underlies agent configuration management as a whole, independent of whether an A/B test is involved.

## My questions

- How does a team decide when a change is significant enough to warrant its own version versus being folded into ongoing iteration on `DEFAULT`?
- Is there a limit on how many versions can accumulate, and does an old, unreferenced version ever get cleaned up automatically?
