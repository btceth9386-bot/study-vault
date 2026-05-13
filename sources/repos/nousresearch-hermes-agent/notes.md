# nousresearch/hermes-agent

## Summary

Hermes Agent is a general-purpose AI agent platform built by Nous Research around a persistent, self-improving agent loop. At the product level, it combines a terminal interface, messaging gateway, scheduled automations, memory systems, subagent delegation, multiple terminal backends, and support for many model providers. At the architecture level, the documentation emphasizes a few core patterns: the agent can run as an ACP server for IDEs, it persists and restores sessions across processes, it compresses long conversations instead of failing on context limits, and it exposes capabilities through a structured tool and toolset system that can also absorb MCP servers.

The repo is notable because it is not just a chat wrapper. It treats the agent as a portable runtime that can live in CLI, IDE, and messaging environments while keeping shared memory, session history, and tool access. The DeepWiki export also shows production-oriented details: session recovery, queued prompts, JSON-RPC transport for ACP and the TUI gateway, cron-based unattended execution, delivery routing to multiple platforms, and probabilistic toolset distributions for evaluation workloads. The most reusable ideas for long-term knowledge are the ACP-backed IDE integration model, surgical context compression, unified built-in plus MCP tool registration, isolated cron job execution, and the design of a self-improving memory and skill loop.

## Knowledge Map

- Agent product surface: CLI, TUI, IDE backend, messaging gateway, dashboard.
- Core runtime patterns: persistent sessions, toolsets, MCP integration, context compression.
- Automation patterns: cron jobs, delivery routing, background execution.
- Learning patterns: memory, skills, self-improvement, session search.
- Evaluation patterns: toolset distributions and research-oriented trajectory generation.

## Key Takeaways

- Hermes is designed as an agent runtime, not just a single chat interface.
- ACP support turns the agent into a backend for AI-native editors and IDEs.
- Session persistence and context compression are first-class infrastructure concerns.
- Toolsets unify built-in tools and MCP-provided tools behind one surface.
- Scheduled jobs and multi-platform delivery make the agent useful outside interactive chat.

## Recommended follow-up ingestions

| Type | URL | Description |
|------|-----|-------------|
