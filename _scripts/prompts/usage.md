# Exobrain Usage Cheatsheet

> **How you use this:** You talk to an AI agent through **Discord (openAB)**. You don't run scripts yourself — you paste a request, the agent executes the scripts in the repo and reports back. Each section below gives **what to say in Discord** as the primary form; the shell commands shown in `(agent runs: …)` are just reference for what the agent will execute on your behalf.
>
> For the conceptual workflow, see `guide.md`.

---

## 1. Knowledge Ingest

### Repository (via DeepWiki)

**Say in Discord:**

```
Ingest the repo https://deepwiki.com/<owner>/<repo> following _scripts/prompts/guide.md.
Run step 1 (ingest-deepwiki.sh), then run the source pipeline
(_scripts/pipeline.py): extract drafts, independently verify them, auto-promote
only verified drafts, and update topics. Leave needs-decision/rejected drafts
for the report. Do NOT run quiz / labs / weekly-refine / OpenWiki refresh.
Write all output in English.
```

*(agent runs: `./_scripts/ingest-deepwiki.sh <owner>/<repo>` then `.venv/bin/python3 _scripts/pipeline.py sources/repos/<owner>-<repo>`)*

> Repo sources land in `sources/repos/<owner>-<repo>/`.

### YouTube (English learning)

**Say in Discord:**

```
Ingest these YouTube episodes for English learning, following _scripts/prompts/guide.md.
Run step 1 (ingest-youtube.sh) per video, then the source pipeline
(_scripts/pipeline.py): extract drafts, independently verify them, auto-promote
only verified drafts, and update topics. Leave needs-decision/rejected drafts
for the report. Do NOT run quiz / labs / weekly-refine / OpenWiki refresh.
Output in English:
https://www.youtube.com/watch?v=<id1>
https://www.youtube.com/watch?v=<id2>
```

*(agent runs: `./_scripts/ingest-youtube.sh <url>` for each, then `.venv/bin/python3 _scripts/pipeline.py sources/videos/<slug>`. For many episodes the agent may background it with `nohup codex exec … &`.)*

> Video sources land in `sources/videos/<auto-slug>/`. To re-run one step:
> "re-run the topics step for sources/videos/<slug>" → *(agent runs: `pipeline.py sources/videos/<slug> --step topics`)*

---

## 2. Review & Quiz a Topic

Two modes, matched to your learning phase (see `_inbox/learning-method-upgrade.md`).
Self-check: "Without notes, can I explain this topic?" No → Phase A. Yes → Phase B.

**Phase A — still building the schema** (agent explains → quizzes you, recall-first). Say in Discord:

```
Read _scripts/prompts/prompt-review-then-quiz.md and start with <topic>.
```

**Phase B — you can already explain it** (you explain it back → recall + application). Say in Discord:

```
Read _scripts/prompts/prompt-review-visual-feynman-apply.md and start with <topic>.
```

Both are diagram-first, one question at a time, conducted in the Discord chat. Shortcuts: `langfuse`, `dspy`, `system design`, `ai backend reliability`.

---

## 3. Learn-by-Building Labs

> Start as soon as you recognize the main term and can state its problem or expected input/output. If that foundation is missing, the agent gives a 2–5 minute primer and continues with more scaffold. Quiz scores and explain-back calibrate difficulty; they do not block the lab. A lab may combine multiple concepts and named tools around one coherent scenario.

### Generate a fading-scaffold lab

**Say in Discord:**

```
Read _scripts/prompts/lab-design.md then design a learn-by-building lab for <concepts or integration request>.
```

Examples:

```text
Read _scripts/prompts/lab-design.md then design a learn-by-building lab for concepts/observability/llm-observability.md.
Read _scripts/prompts/lab-design.md then design a lab combining Kiro CLI and Langfuse for evaluation.
```

### Advanced integration example

```text
Read _scripts/prompts/lab-design.md then design an advanced integration lab
combining Kiro CLI and Langfuse for evaluation.

Complexity: advanced
Time box: 90-120 minutes
Setup mode: real-tool
Include:
- An end-to-end evaluation dataset and scoring workflow.
- Kiro CLI execution traced into Langfuse.
- A baseline-versus-improved comparison.
- Two intentional failure cases.
- Observable traces, metrics, and acceptance criteria.
```

The prompt above is sufficient; you do not need to name each skill again. The agent follows this workflow:

```text
~/orb_pods_share/<lab-id>/spec.md
  -> doc-restructure -> ~/orb_pods_share/<lab-id>/spec.diataxis.md
  -> web-artifacts-builder -> ~/orb_pods_share/<lab-id>/pages/index.html
  -> wrangler -> https://<lab-id>-review.pages.dev
  -> study-vault recovery capsule: labs/<lab-id>/{manifest.yaml,spec.md}
```

`spec.md` remains the complete source specification. `spec.diataxis.md` is a second-pass, human-first version with separated tutorial, explanation, reference, and checkpoint material; it becomes the primary source for the review HTML. The agent then creates or reuses the dedicated Cloudflare Pages application `<lab-id>-review` and deploys only the sanitized `pages/` directory. It never publishes `expected.md`, learner predictions, secrets, private URLs, or a completed core solution. If deployment is unavailable, the local HTML and exact retry commands remain in the lab folder.

Then **you** do the hands-on part:
1. Open the review URL and confirm the architecture and learning goal.
2. Fill `~/orb_pods_share/<lab-id>/predictions.md` **before** running.
3. Implement the stubbed core (`TODO: YOUR CORE`).
4. Diff your result against `~/orb_pods_share/<lab-id>/expected.md`.

### Grade your attempt (run AFTER filling predictions + core)

**Say in Discord:**

```
Read _scripts/prompts/lab-review.md then review my ~/orb_pods_share/<lab-id>/ attempt.
```

The agent corrects mistakes, adds `application` quiz cards (due tomorrow), and updates `lab_status`.

### Lighter fallback (single-shot tiny lab, no grading loop)

**Say in Discord:**

```
Read _scripts/prompts/labs-tiny-from-concept.md then make a tiny lab for <concept>.
```

Use when the full predict → fill-core → review loop feels too heavy for a concept.

---

## 4. Spaced-Repetition Quiz

**Say in Discord:** "Quiz me on due cards" — the agent pulls due questions from `quiz/bank.json` and runs the quiz conversationally in Discord, one at a time.

*(At a terminal you can instead run the interactive CLI: `.venv/bin/python3 -m _scripts.quiz_cli --count 10`)*

---

## 5. Weekly Maintenance

**Say in Discord:**

```
Read _scripts/prompts/weekly-refine.md then execute.
```

The agent generates a refine report in `_inbox/`, flags stale concepts/expired drafts, and updates `quiz/bank.json` + `_index/`.

---

## Quick map: what to say in Discord

| I want to… | Say in Discord |
|---|---|
| Ingest a GitHub repo | "ingest the repo `<deepwiki-url>` following guide.md" |
| Ingest YouTube videos | "ingest these episodes for English learning following guide.md: `<urls>`" |
| Review + quiz (still learning it) | "review-then-quiz `<topic>`" (Phase A) |
| Review + quiz (already know it) | "visual-feynman-apply review `<topic>`" (Phase B) |
| Practice concepts/tools hands-on | "design a lab combining `<concepts/tools>` for `<goal>`" → later "review my lab attempt" |
| Quick hands-on, no grading | "make a tiny lab for `<concept>`" |
| Daily spaced repetition | "quiz me on due cards" |
| Weekly cleanup | "run weekly-refine" |
| Refresh knowledge map | "review canonical changes, then manually update and republish OpenWiki" |
| Commit & push results | "commit and push with message `<msg>`" |
