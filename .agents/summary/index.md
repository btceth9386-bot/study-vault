# Exobrain Documentation Index

> **For AI Assistants**: This file is the primary entry point for understanding the Exobrain (study-vault) project. Read this file first to determine which detailed documentation files to consult for specific questions.

## Project Summary

Exobrain is a **design-phase** personal knowledge base system. No implementation code exists yet — the repository contains specification documents (requirements, design, tasks) written in Traditional Chinese. The system will ingest learning materials from 6 source types, convert them to Markdown, use AI agents to refine content, and provide spaced-repetition quizzing.

**Tech stack**: Bash + Python + Node.js | Markdown + YAML + JSON | OpenAI Whisper API | Git

## Documentation Map

### How to Use This Documentation

1. **Start here** (index.md) to understand what exists and where to find details
2. **For architecture questions** → architecture.md
3. **For "what does X do?"** → components.md
4. **For "how do I call X?"** → interfaces.md
5. **For data schemas** → data_models.md
6. **For process flows** → workflows.md
7. **For tool/package info** → dependencies.md
8. **For raw analysis** → codebase_info.md

### File Descriptions

| File | Content | When to Consult |
|------|---------|-----------------|
| [codebase_info.md](codebase_info.md) | Project overview, tech stack, file inventory, full architecture diagrams | General project understanding, tech stack questions |
| [architecture.md](architecture.md) | System architecture, design decisions, layer separation, four-stage learning flow | Architecture decisions, system design, layer constraints |
| [components.md](components.md) | All components: init script, 6 ingest pipelines, 8 Python modules, 3 prompts | Understanding what each component does, responsibilities |
| [interfaces.md](interfaces.md) | CLI interfaces, Python function signatures, prompt I/O contracts, quiz session sequence | How to call scripts/functions, API contracts |
| [data_models.md](data_models.md) | Source meta.yaml, concept frontmatter, quiz bank JSON, draft/topic/index schemas, ER diagram | Data structure questions, schema validation, field definitions |
| [workflows.md](workflows.md) | 8 workflow diagrams: init, ingestion, YouTube/DeepWiki detail, promotion, weekly refine, quiz session, SM-2 cycle | Process flow questions, "what happens when...?" |
| [dependencies.md](dependencies.md) | External tools, Python/Node.js packages, APIs, env vars, dependency graph | Dependency questions, setup requirements, tool versions |

### Cross-Reference Guide

| Topic | Primary File | Related Files |
|-------|-------------|---------------|
| Ingest pipeline | components.md | interfaces.md (CLI args), workflows.md (flow diagrams), dependencies.md (external tools) |
| Quiz system | components.md (SM-2, quiz_manager, quiz_session) | interfaces.md (function signatures), data_models.md (bank.json schema), workflows.md (quiz session flow) |
| Layer separation | architecture.md | workflows.md (promotion flow), components.md (prompt write constraints) |
| Data schemas | data_models.md | interfaces.md (validator functions), components.md (metadata_validator) |
| Prompt engine | components.md | interfaces.md (prompt I/O), workflows.md (new-source, promote, weekly-refine flows) |
| DeepWiki integration | components.md (ingest-deepwiki) | workflows.md (DeepWiki flow), dependencies.md (MCP config) |

## Key Concepts for AI Assistants

- **This is a design-phase project** — all docs describe planned behavior, not existing code
- **Spec language is Traditional Chinese** — requirements, design, and tasks are in zh-TW
- **Draft-then-promote pattern** — AI never writes directly to `concepts/`; everything goes through `_drafts/` first
- **Strict layer separation** — each prompt has explicit write-access constraints
- **SM-2 algorithm** — standard spaced repetition with ease_factor ≥ 1.3 floor
- **Stateless quiz logic** — `quiz_session.py` has no I/O, enabling multi-platform reuse

## Source Specification Files

| File | Location | Content |
|------|----------|---------|
| Design v2 | `personal-knowledge-base-design-v2.md` | Original comprehensive design spec |
| Requirements | `.kiro/specs/personal-knowledge-base/requirements.md` | 22 formal requirements with acceptance criteria |
| Design | `.kiro/specs/personal-knowledge-base/design.md` | Detailed architecture, components, interfaces, data models |
| Tasks | `.kiro/specs/personal-knowledge-base/tasks.md` | 11 task groups with implementation plan |
