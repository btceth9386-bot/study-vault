# Learning Method Upgrade: From "Watching AI Do Labs" to "Active Completion"

> Overall analysis and improvement plan for the "quiz Q&A + small lab" study method, including how it merges with the existing concept-first approach.

## Diagnosis: The problem isn't "labs are slow" — it's "the wrong role"

In the current loop, the AI does the lab and you watch the result. In learning science, **watching someone else do the work has the lowest retention of any method**. It feels slow not because labs take time, but because passive observation has low retention — you have to re-encounter a concept many times before it sticks, so it feels like endless grinding.

Two core ideas:

- **Generation effect**: you remember best what you generate yourself.
- **Desirable difficulty**: appropriate struggle is what produces learning.

When the AI removes all the friction, it removes the learning along with it. "I want to know the process and results" is a signal — you're trying to recover the skipped learning through observation, but observation can't recover it.

## The core reframe: change your role from "observer" to "director / verifier / completer"

Let the AI do the "two ends" and you do the "hard core in the middle." Three modes (shallow to deep):

### 1. Prediction-first (highest leverage, most time-efficient)
Before running the lab, write down what you expect each step to do and what the final result will look like. Then let the AI run it, and diff your prediction against the actual outcome.
- Directly answers "I want to know the process and results" — but as an **active** version.
- Where your prediction is wrong = a hole in your mental model = automatically becomes the next quiz card.
- Adds almost no time.

### 2. Fading scaffolding (completion problems)
The AI gives the skeleton and stubs out the "conceptual core" (stub + TODO); you fill only the critical 10–20%.
- Example: learning caching — the AI writes the server/DB/tests, leaving only `cache_get_or_load()` for you.
- As your fluency grows, the stubbed-out portion gets larger (fade out).

### 3. Reverse lab / debugging (advanced)
The AI deliberately writes a version with a bug or design flaw; you find and fix it.
- Debugging is closer to real work than writing from scratch, and forces you to actually read and understand.

## The AI's role: a feedback layer AFTER your attempt, never a replacement

This addresses the key risk: **what if your prediction (B3) or your core fill-in (B4) is weak or wrong?**

The rule: **you always generate first; the AI then corrects and reinforces.** The AI never writes the prediction or the core for you. After your attempt:

- **On the prediction (B3)** — the AI reviews it and flags gaps or misconceptions *without handing you the full answer*. If your prediction is too vague, it asks targeted questions to push your thinking (e.g., "what happens to the second request — cache hit or miss, and why?").
- **On the core fill-in (B4)** — the AI reviews your code/answer:
  - If correct: confirm it and explain *why* it's correct (reinforces the schema).
  - If wrong or weak: correct it with a clear explanation of the gap, and turn that gap into an `application` quiz card.
- **Calibration** — if your attempt was strong, the AI fades more scaffolding next time; if you struggled, it adds more guidance. This keeps you in the "desirable difficulty" zone.

This preserves the generation effect (you struggle first) while guaranteeing no wrong mental model survives (the AI catches it immediately, when feedback is most valuable).

## Two reinforcing dimensions

- **Interleaving**: mix quizzes from different concepts in one session (caching + sharding + CAP together). Harder in the moment, far better long-term transfer. `quiz_cli` already supports this — just mix deliberately.
- **Feynman wrap-up**: after each lab, explain in 3–4 sentences, to a layperson, what you just did and why you designed it that way. Where you get stuck is where you didn't actually understand.

## Learn by building from the first useful mental model

Concept-first review and prediction-first labs are not mutually exclusive. A novice can begin with a small lab as soon as they recognize the problem or expected input/output; the amount of scaffold then fades as understanding grows.

| Phase | State | Method | Maps to |
|-------|-------|--------|---------|
| **A — Guided acquisition** | zero / low prior knowledge | short primer → orientation question → heavily scaffolded lab | learn while building |
| **B — Consolidation** | can roughly explain it | prediction + fading-scaffold lab + application questions | less guidance |
| **C — Retention** | mastered | interleaved SM-2 review, reverse labs, teach-back | shared |

### How to decide which phase a concept is in

No new machinery is needed. Use `depth` and `lab_status` to calibrate support, not as a hard gate:

- `depth 1` (just encountered) → **Phase A**: short primer + highly guided lab with one small learner-owned decision.
- `depth 2` (can explain) + `lab_status: not-started|scaffolded` → **Phase B**: prediction + lab.
- `depth 3-4` or `lab_status: completed|explained` → **Phase C**: interleaved review, reverse labs, teaching.

Minimum starting check: **"Can I name the problem this addresses or its expected input/output?"** If not, the lab begins with a 2–5 minute primer and one orientation question. Explain-back and quiz history decide how much scaffold to remove; they do not prevent the lab.

## The merged loop

```
[Phase A — first exposure, guided building]
A1. Read a focused primer and answer one orientation question ~5 min
A2. Review the lab architecture and observable outcome        ~5 min
A3. Predict one behavior and fill one small scaffolded core   ~15 min
    -> AI reviews the attempt and turns gaps into quiz cards

[Phase B — familiar concept, fading scaffold]
B1. Use quiz history and explain-back to calibrate support
B3. Prediction: write your expected lab result              ~5 min
    -> AI reviews: flags gaps/misconceptions, pushes with
       targeted questions; never gives the full answer
B4. AI generates the fading-scaffold lab; you fill the core ~15-20 min
    -> AI reviews your fill-in: confirm+explain if right;
       correct+explain if wrong; weak spots become quiz cards
B5. Diff prediction vs actual -> wrong points become quiz cards ~5 min
B6. Feynman wrap-up: explain in 3 sentences to a layperson  ~3 min

[Phase C — shared]
C. Enter SM-2, review across concepts (interleaved)
```

The key difference is that assessment calibrates the scaffold instead of blocking hands-on work. The learner always owns at least one meaningful prediction or implementation decision.

## Where this lives in Exobrain

- `_scripts/prompts/promote-concept.md` — defines the `lab_status` frontmatter field and the depth→phase mapping (already updated).
- `concepts/<category>/<id>.md` — each concept now carries `lab_status` so you can see at a glance which concepts you've actually practiced vs. only read.
- `_scripts/prompts/lab-design.md` accepts one or more concepts or a concrete tool-integration request, then produces a fading-scaffold lab and human review site.

## Implementation status & the lightweight fallback

This is now wired into Exobrain:

- `_scripts/prompts/lab-design.md` — autonomous: generates artifacts under `labs/<lab-id>/`, builds an English human-review HTML with `web-artifacts-builder`, uses Wrangler to create a dedicated `<lab-id>-review` Cloudflare Pages application and publish the sanitized page, and sets included concepts to `lab_status: scaffolded`.
- `_scripts/prompts/lab-review.md` — interactive: run AFTER you fill the predictions and core. The AI grades, corrects, emits `application` quiz cards for your mistakes (due tomorrow), and updates `lab_status` to `completed`/`explained`. Deliberately NOT automated — automating it would recreate the "AI does it for you" problem.

**Fallback method:** `_scripts/prompts/labs-tiny-from-concept.md` is a lighter, single-shot lab generator (15–45 min, no scaffolding fade, no AI grading, no quiz feedback). Keep it as a fallback: if the full prediction → fill-core → review loop ever feels too slow or heavy for a given concept, drop back to a tiny lab for quick hands-on intuition.
