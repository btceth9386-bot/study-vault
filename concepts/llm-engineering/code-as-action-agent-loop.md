---
id: code-as-action-agent-loop
title: Code-as-Action Agent Loop
depth: 2
lab_status: not-started
last_reviewed: 2026-09-26
review_due: 2026-09-29
sources:
  - sources/papers/comprehensive-agent-engineering-guide-2026
related:
  - react-agentic-loop
  - ephemeral-agent-execution-sandbox
  - zero-ambient-authority-for-agents
tags:
  - llm-engineering
  - agents
  - tool-use
---

# Code-as-Action Agent Loop

- **One-sentence definition**: A code-as-action agent loop lets the model express an action as executable code that composes tools, variables, branching, and iteration inside one sandboxed step.
- **Why it exists / what problem it solves**: Typed tool calls are easy to audit but can require many model round trips. Executable code can describe a compact multi-step workflow in one action.
- **Keywords**: code agent, tool composition, sandbox, control flow, auditability
- **Related concepts**: [[react-agentic-loop]], [[ephemeral-agent-execution-sandbox]], [[zero-ambient-authority-for-agents]]
- **Depth**: 2/4
- **Last updated**: 2026-09-26
- **Source**: The Comprehensive Guide to AI Agent Engineering

## Summary

Instead of choosing one tool call at a time, an agent can write a small program that calls several tools, stores results in variables, and branches on what it finds. This gives the model the control flow ordinary code already has, often with fewer calls back to the model. The trade-off is that the program is broader and harder to inspect than a single typed call. It therefore belongs in a sandbox with narrow, task-specific authority.

## Example

For a research task, an agent writes code that searches a repository catalog, filters results by date, summarizes the remaining entries, and calls `final_answer`. The runtime executes the code in an isolated container with only the search tool and no host credentials; it returns the output to the model for the next decision.

## Relationship to existing concepts

- [[react-agentic-loop]]: Code-as-action is an alternative way to express the action part of a reasoning-and-acting loop.
- [[ephemeral-agent-execution-sandbox]]: Generated code needs isolation because it can compose broad control flow and tool use.
- [[zero-ambient-authority-for-agents]]: The sandboxed program should receive only narrowly scoped credentials for its task.

## My questions

- Which code actions are safe enough to run automatically, and which should require review?
- How can the runtime make generated code easier to audit without losing its composability?
