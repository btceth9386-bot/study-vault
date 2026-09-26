---
id: a2ui-layout-ownership-patterns
title: A2UI Layout Ownership Patterns
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/agent-tools---interoperability-day-2/
related:
  - a2ui-trusted-catalog-rendering
  - hybrid-llm-output-assertions
tags:
  - llm-engineering
  - a2ui
  - architecture
---

# A2UI Layout Ownership Patterns

- **One-sentence definition**: A2UI layout ownership chooses whether an LLM composes the interface for changing user intent or a deterministic tool returns a fixed layout from known inputs.
- **Why it exists / what problem it solves**: Asking a model to recreate a stable dashboard wastes tokens and adds variation, but fixed templates cannot adapt well to an open-ended request. The layout owner should match what determines the layout.
- **Keywords**: A2UI, LLM-generated UI, templates, intent-driven, input-driven, determinism
- **Related concepts**: [[a2ui-trusted-catalog-rendering]], [[hybrid-llm-output-assertions]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: Agent Tools & Interoperability — Day 2

## Summary

The question is not whether A2UI is used; it is who makes the layout decision. Let the LLM own it when a user's intent changes the shape of the answer, such as “compare these options in the most useful way.” Let a tool own it when the inputs always imply the same screen, such as a shipment-status card. Both approaches still render through the same trusted catalog.

## Example

For “help me choose a laptop,” an LLM can arrange comparison cards around the user's priorities. For `get_order_status(order_id)`, the tool can always return the same order-status card, avoiding an LLM UI-generation step.

## Relationship to existing concepts

- [[a2ui-trusted-catalog-rendering]]: Both ownership patterns use the same catalog boundary; they differ only in who composes approved components.
- [[hybrid-llm-output-assertions]]: LLM-owned layouts benefit from schema and deterministic checks before a renderer receives them.

## My questions

- When does a frequently used LLM-owned layout become stable enough to replace with a template?
- Which layout errors should cause a fallback to a simpler deterministic UI?
