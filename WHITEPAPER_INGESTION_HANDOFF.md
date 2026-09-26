# Whitepaper Ingestion Handoff

## Objective

Ingest the PDF whitepapers under `/Users/9icloud/projects/ai-agent-whitepaper/` into this knowledge base. Follow `_scripts/prompts/usage.md` and use `_scripts/pipeline.py` for the normal source flow. All generated knowledge content is in English.

Do **not** run quiz sessions, labs, `weekly-refine`, or an OpenWiki refresh as part of this work.

## Current Git State

- Branch: `codex/ingest-ai-whitepapers`
- The branch has **not** been pushed.
- Provider-separated commits:

  | Provider | Commit | Contents |
  | --- | --- | --- |
  | Google | `5804c50` | Five Google whitepapers: source materials, verified concepts, and learning paths |
  | Google | `550da2c` | Three Google concepts missed initially because their YAML list indentation differed |
  | Anthropic | `6c2ffe3` | Enterprise transformation guide and State of AI Agents Report |
  | OpenAI | `846194f` | Comprehensive Agent Engineering Guide |
  | Shared generated data | `61120cc` | Reciprocal links, indexes, topic counts, and quiz-bank records |

## Completed Sources

| Provider | Source directory | Result |
| --- | --- | --- |
| Google | `sources/papers/google-day-1-v3/` | Complete |
| Google | `sources/papers/agent-tools---interoperability-day-2/` | Complete |
| Google | `sources/papers/agent-skills-day-3/` | Complete |
| Google | `sources/papers/vibe-coding-agent-security-and-evaluation-day-4/` | Complete |
| Google | `sources/papers/day-5-v3/` | Complete |
| Anthropic | `sources/papers/6a05227a9465cf77dba4c51a-the-enterprise-ai-transformation-guide-101425/` | Complete |
| Anthropic | `sources/papers/the-2026-state-of-ai-agents-report/` | Complete |
| OpenAI | `sources/papers/comprehensive-agent-engineering-guide-2026/` | Complete |

Every completed source passed the draft-then-review gate before promotion. The OpenAI State of AI Agents Report run reported 53 passing targeted tests; other pipeline runs also validated frontmatter, links, indexes, and quiz JSON. OpenWiki was intentionally not refreshed.

## AWS Source — Completed as Filtered Subsets

`sources/papers/bedrock-agentcore-dg/` holds the raw extraction of the 3,428-page AWS Bedrock AgentCore Developer Guide (reference only; not run through the pipeline). It was filtered by PDF page range (focus: agent observability, multi-agent, DevOps/SRE) into four bounded sources, each run through the full pipeline (ingest → review → promote → topics):

| Source directory | Pages | New concepts |
| --- | --- | --- |
| `sources/papers/bedrock-agentcore-observability-evals/` | 96 | 8 |
| `sources/papers/bedrock-agentcore-multi-agent/` | 84 | 9 |
| `sources/papers/bedrock-agentcore-agentops/` | 136 | 9 |
| `sources/papers/bedrock-agentcore-eval-framework-examples/` | 104 | 0 (enriched 2 existing) |

Each `notes.md` lists its page ranges in section headings. Subprocess `claude` agents need `CLAUDE_CODE_OAUTH_TOKEN` in the Claude Code settings `env` when the pipeline is run from a Claude desktop sandbox shell.

## Uncommitted Change Requiring Confirmation

`_scripts/pipeline.yml` is modified but not committed. Its agent commands were changed from the earlier mixed Codex/Claude configuration to Claude commands for ingest, promote, topics, and lab, and Codex for review.

This change was not included in the ingestion commits. Confirm its intended owner and behavior before committing, reverting, or relying on it. Do not overwrite it casually.

## Suggested Next Actions

1. Review the uncommitted pipeline configuration change separately.
2. When the user authorizes it, push `codex/ingest-ai-whitepapers` and open a PR to `main`.

## Useful Commands

```bash
# Complete normal source pipeline
.venv/bin/python3 _scripts/pipeline.py sources/papers/<source-slug>

# Resume one safe missing stage only
.venv/bin/python3 _scripts/pipeline.py sources/papers/<source-slug> --step topics

# Validate Python scripts
.venv/bin/python3 -m pytest _scripts/tests/ -v
```
