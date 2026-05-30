# Exobrain Usage Cheatsheet

Ready-to-paste prompts and commands for everyday use. For the conceptual workflow, see `guide.md`.

---

## 1. Knowledge Ingest

### Repository (via DeepWiki)

```bash
# Step 1 — ingest the repo (creates sources/repos/<owner>-<repo>/)
./_scripts/ingest-deepwiki.sh <owner>/<repo>

# Steps 2-5 — pipeline spawns codex/claude to process, review, promote, topics
.venv/bin/python3 _scripts/pipeline.py sources/repos/<owner>-<repo>
```

Example:

```bash
./_scripts/ingest-deepwiki.sh nousresearch/hermes-agent
.venv/bin/python3 _scripts/pipeline.py sources/repos/nousresearch-hermes-agent
```

> Note: repo sources live under `sources/repos/<owner>-<repo>` (not `sources/videos/`).

### YouTube (English learning) — unattended background run

Codex runs ingest + pipeline for one or more episodes in the background:

```bash
nohup codex exec --yolo --skip-git-repo-check --model gpt-5.5 resume --last \
  'Handle these YouTube episodes end-to-end (ingest + full pipeline).
   https://www.youtube.com/watch?v=<id1>
   https://www.youtube.com/watch?v=<id2>
   Follow _scripts/prompts/guide.md. Write all output in English.' &
```

After it finishes, the slug is `sources/videos/<auto-slug>`. If you need to re-run a single step:

```bash
.venv/bin/python3 _scripts/pipeline.py sources/videos/<slug> --step topics
```

---

## 2. Review & Quiz a Topic

Diagram-first review, then one quiz question at a time:

```
Read _scripts/prompts/prompt-review-then-quiz.md and start with <topic>.
```

Shortcuts: `langfuse`, `dspy`, `system design`, `ai backend reliability`.

Example:

```
Read _scripts/prompts/prompt-review-then-quiz.md and start with langfuse topic.
```

Variant (visual + Feynman + applied): `_scripts/prompts/prompt-review-visual-feynman-apply.md`.

---

## 3. Hands-on Labs (Phase B: depth >= 2 concepts)

### Generate a fading-scaffold lab (autonomous setup)

```bash
.venv/bin/python3 _scripts/pipeline.py concepts/<category>/<concept-id>.md --step lab
```

Or in chat:

```
Read _scripts/prompts/lab-design.md then design a fading-scaffold lab for <concept>.
```

Then, manually:
1. Fill `labs/<concept-id>/predictions.md` **before** running.
2. Implement the stubbed core (`TODO: YOUR CORE`).
3. Diff your result against `labs/<concept-id>/expected.md`.

### Grade your attempt (interactive — run AFTER filling predictions + core)

```
Read _scripts/prompts/lab-review.md then review my labs/<concept-id>/ attempt.
```

The AI corrects mistakes, emits `application` quiz cards (due tomorrow), and updates `lab_status`.

### Lighter fallback (single-shot tiny lab, no grading loop)

```
Read _scripts/prompts/labs-tiny-from-concept.md then make a tiny lab for <concept>.
```

Use this when the full prediction → fill-core → review loop feels too heavy for a concept.

---

## 4. Spaced-Repetition Quiz (CLI)

```bash
.venv/bin/python3 -m _scripts.quiz_cli --count 10
```

---

## 5. Weekly Maintenance

```
Read _scripts/prompts/weekly-refine.md then execute.
```

---

## Quick map: which prompt for what

| I want to… | Use |
|---|---|
| Ingest a GitHub repo | `ingest-deepwiki.sh` + `pipeline.py …/repos/<slug>` |
| Ingest a YouTube video | `nohup codex … guide.md` (background) |
| Review + quiz a topic | `prompt-review-then-quiz.md` |
| Practice a concept hands-on | `pipeline.py <concept> --step lab` → `lab-review.md` |
| Quick hands-on, no grading | `labs-tiny-from-concept.md` |
| Daily spaced repetition | `quiz_cli` |
| Weekly cleanup | `weekly-refine.md` |
