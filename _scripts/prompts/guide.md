# Exobrain Workflow Guide

A step-by-step guide for using AI agents to build your personal knowledge base.

## Step 1 — Ingest a source

Run an ingest script to bring a source into the knowledge base:

```bash
# YouTube video
./_scripts/ingest-youtube.sh https://youtube.com/watch?v=...

# PDF document
./_scripts/ingest-pdf.sh /path/to/document.pdf

# GitHub repo (via DeepWiki)
./_scripts/ingest-deepwiki.sh https://github.com/owner/repo

# Web article
node _scripts/ingest-article.js https://example.com/article

# Podcast
./_scripts/ingest-podcast.sh /path/to/episode.mp3

# epub book
.venv/bin/python3 _scripts/ingest-book.py /path/to/book.epub
```

## Step 2 — Process the source into drafts (`new-source.md`)

Ask an AI agent to read the source and generate concept drafts:

```
Read _scripts/prompts/new-source.md then process the new source in _inbox/
```

For GitHub repos, use the DeepWiki MCP server to read the full wiki content directly:

```
Read _scripts/prompts/new-source.md, then use the DeepWiki MCP server to read
https://deepwiki.com/donnemartin/system-design-primer and process it as a new source in English.
```

The agent will:
- Organize the source into `sources/<type>/<slug>/`
- Generate candidate concept drafts in `_drafts/`
- Update `_index/`

## Step 3 — Review drafts

Ask an AI agent to review the drafts against the original source:

```
Review all files in _drafts/ against the source material. For each draft:

1. Use the DeepWiki MCP server to read https://deepwiki.com/donnemartin/system-design-primer and verify the draft's accuracy
2. Check: Is the one-sentence definition correct? Is "why it matters" accurate? Are relationships to other concepts valid?
3. Flag any factual errors, missing key points, or misleading simplifications
4. Rate each draft: APPROVE (ready to promote), REVISE (needs changes — list what), or REJECT (too inaccurate)

Output a summary table with your verdict for each draft.
```

After the review, fix any REVISE items manually or ask the agent to fix them.

## Step 4 — Promote approved drafts to concepts (`promote-concept.md`)

Promote all approved drafts at once:

```
Read _scripts/prompts/promote-concept.md then promote all approved drafts in _drafts/ to concepts. Write all output in English.
```

Or promote a specific batch if the agent runs out of context:

```
Read _scripts/prompts/promote-concept.md then promote these drafts to concepts in English:
_drafts/load-balancing.md
_drafts/cap-theorem.md
_drafts/horizontal-scaling.md
```

The agent will:
- Create `concepts/<category>/<concept-id>.md` (Feynman-style)
- Add quiz questions to `quiz/bank.json`
- Update `_index/`

Repeat for each approved draft.

## Step 5 — Take a quiz

Test your understanding with spaced-repetition quizzing:

```bash
.venv/bin/python3 _scripts/quiz_cli.py --count 10
```

## Step 6 — Weekly maintenance (`weekly-refine.md`)

Run periodically (e.g. weekly) to maintain the knowledge base:

```
Read _scripts/prompts/weekly-refine.md then execute
```

The agent will:
- Generate a refine report in `_inbox/refine-report-<date>.md`
- Flag stale concepts, contradictions, expired drafts
- Update `quiz/bank.json` and `_index/`

## Key constraint

AI never writes directly to `concepts/`. All AI output goes to `_drafts/` first. You review, then promote.
