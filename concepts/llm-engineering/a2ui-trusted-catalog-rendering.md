---
id: a2ui-trusted-catalog-rendering
title: A2UI Trusted Catalog Rendering
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/agent-tools---interoperability-day-2/
related:
  - standardized-message-content-blocks
  - multi-platform-agent-gateway
  - a2ui-layout-ownership-patterns
tags:
  - llm-engineering
  - a2ui
  - security
---

# A2UI Trusted Catalog Rendering

- **One-sentence definition**: A2UI lets an agent describe a UI with approved component types while the client renders those declarations with its own native component library.
- **Why it exists / what problem it solves**: Raw data makes people build the interface by hand, while model-generated frontend code lets untrusted output cross a security boundary. A trusted catalog keeps the UI interactive without running arbitrary code.
- **Keywords**: A2UI, declarative UI, trusted catalog, renderer, native components, security
- **Related concepts**: [[standardized-message-content-blocks]], [[multi-platform-agent-gateway]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: Agent Tools & Interoperability — Day 2

## Summary

Think of the component catalog as a menu, not a blank check. The agent can ask for approved pieces such as a chart, card, or form and arrange them to express its intent. The client decides how each piece looks and behaves on that device. Because the agent never sends executable JavaScript, the renderer can reject anything outside its trusted catalog.

## Example

An analytics agent returns a declaration for a `line-chart` and a `date-filter`. The web client maps those names to its own accessible React components, while a mobile client maps them to native controls. Neither client executes code supplied by the agent.

## Relationship to existing concepts

- [[standardized-message-content-blocks]]: Both use typed structures, but content blocks carry message payloads while A2UI declarations describe an interactive interface.
- [[multi-platform-agent-gateway]]: A gateway can send the same UI intent to clients whose catalog renderers implement it natively.
- [[a2ui-layout-ownership-patterns]]: Both LLM-owned and template-owned layouts render through the same trusted catalog.

## My questions

- Which component properties should be expressive enough for useful interfaces but still safe to expose to an agent?
- How should a client report an unsupported catalog component without breaking the rest of the response?
