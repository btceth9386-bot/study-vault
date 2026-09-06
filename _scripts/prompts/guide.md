# Exobrain Workflow Guide

A step-by-step guide for using AI agents to build your personal knowledge base.

> For ready-to-paste prompts and commands, see `_scripts/prompts/usage.md` (cheatsheet).

## Step 1 — Ingest a source

Run an ingest script to bring a source into the knowledge base:

```bash
# YouTube video
./_scripts/ingest-youtube.sh https://youtube.com/watch?v=...

# PDF document
./_scripts/ingest-pdf.sh /path/to/document.pdf

# GitHub repo (via DeepWiki)
./_scripts/ingest-deepwiki.sh https://github.com/owner/repo

# Or use DeepWiki / owner-repo form directly
./_scripts/ingest-deepwiki.sh https://deepwiki.com/owner/repo
./_scripts/ingest-deepwiki.sh owner/repo

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
https://deepwiki.com/<owner>/<repo> and process it as a new source in English.
```

The agent will:
- Organize the source into `sources/<type>/<slug>/`
- Generate candidate concept drafts in `_drafts/`
- Update `_index/`

## Step 3 — Review drafts

Ask an AI agent to review the drafts against the original source:

```
Review all files in _drafts/ against the source material. For each draft:

1. Use the DeepWiki MCP server to read https://deepwiki.com/<owner>/<repo> and verify the draft's accuracy
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

## Step 5 — Generate learning paths (topics)

After promoting concepts, ask the AI agent to create cross-concept learning paths:

```
Look at all concepts in concepts/ and suggest 2-3 learning paths that group related concepts into a logical study order. Create the topic files in topics/ and update _index/topics.md. Write in English.
```

Each topic file should include prerequisites, a recommended learning order, and links to the relevant concept files.

## Step 6 — Take a quiz

Test your understanding with spaced-repetition quizzing:

```bash
.venv/bin/python3 -m _scripts.quiz_cli --count 10
```

## Step 6.5 — Learn-by-building labs

Start once the learner recognizes the main term and can state its problem or expected input/output. If needed, the agent gives a short primer and continues with a heavier scaffold. Labs may combine multiple concepts and named tools around one practical scenario.

```bash
# One concept:
.venv/bin/python3 _scripts/pipeline.py concepts/<category>/<concept-id>.md --step lab

# A composed integration request:
.venv/bin/python3 _scripts/pipeline.py "Kiro CLI + Langfuse for evaluation" --step lab
```

The lab agent creates the complete lab under `~/orb_pods_share/<lab-id>/`, uses `web-artifacts-builder` to produce a human-readable review HTML, then uses the Wrangler skill to create a dedicated `<lab-id>-review` Cloudflare Pages application and publish the sanitized page. It keeps only `labs/<lab-id>/{manifest.yaml,spec.md}` in study-vault as a recovery capsule. Secrets, learner predictions, private answer keys, and completed core solutions must never be published.

Then (manually, in order):
1. Review the published architecture and acceptance criteria.
2. Fill `~/orb_pods_share/<lab-id>/predictions.md` BEFORE running.
3. Implement the stubbed core (`TODO: YOUR CORE`).
4. Diff your result against `~/orb_pods_share/<lab-id>/expected.md`.
5. Ask an AI agent to grade your attempt — it corrects mistakes and feeds them into the quiz bank:

```
Read _scripts/prompts/lab-review.md then review my ~/orb_pods_share/<lab-id>/ attempt.
```

Lighter fallback (single-shot, no grading loop): `Read _scripts/prompts/labs-tiny-from-concept.md then make a tiny lab for <concept>`.


## Step 7 — Weekly maintenance (`weekly-refine.md`)

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

## Automated pipeline

Instead of running steps 2-5 manually, use the pipeline script. **The "full pipeline" means steps 2-5 only (ingest → review → promote → topics). It does NOT include Step 6 (quiz), Step 6.5 (labs), or Step 7 (weekly-refine)** — those are separate, per-concept or periodic, and run manually.

```bash
# Full pipeline (steps 2-5) for an ingested source:
.venv/bin/python3 _scripts/pipeline.py sources/videos/my-video
.venv/bin/python3 _scripts/pipeline.py sources/repos/<owner>-<repo>

# Single step:
.venv/bin/python3 _scripts/pipeline.py sources/repos/<owner>-<repo> --step ingest
.venv/bin/python3 _scripts/pipeline.py --step review
.venv/bin/python3 _scripts/pipeline.py --step promote
.venv/bin/python3 _scripts/pipeline.py --step topics

# Preview commands without executing:
.venv/bin/python3 _scripts/pipeline.py sources/repos/<owner>-<repo> --dry-run
```

Configure which AI agent handles each step in `_scripts/pipeline.yml`.
