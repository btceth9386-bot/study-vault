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

## Two methods are not in conflict — they are phases of the same concept's lifecycle

Your previous approach (concept-first → reinforcing quiz) and this prediction-first loop are **not either/or — they are sequential phases** keyed to how much prior knowledge you have. This follows the **expertise reversal effect / guidance fading** principle: high guidance for novices, faded guidance as expertise grows.

| Phase | State | Method | Maps to |
|-------|-------|--------|---------|
| **A — Acquisition** | zero / low prior knowledge | read concept first → light quiz (multiple-choice / recall) to encode the schema | your previous approach |
| **B — Consolidation** | can roughly explain it | prediction + fading-scaffold lab + application questions (with AI feedback) | the 7-step loop |
| **C — Retention** | mastered | interleaved SM-2 review, reverse labs, teach-back | shared |

### How to decide which phase a concept is in

No new machinery needed — use the existing `depth` field plus the new `lab_status` field:

- `depth 1` (just encountered) → **Phase A**: concept-first + encoding quiz.
- `depth 2` (can explain) + `lab_status: not-started|scaffolded` → **Phase B**: prediction + lab.
- `depth 3-4` or `lab_status: completed|explained` → **Phase C**: interleaved review, reverse labs, teaching.

Simple self-check: **"Without notes, can I explain this concept in my own words?"**
- No → Phase A (old approach)
- Yes → Phase B (new approach)

## The merged loop (old approach slots in as Phase A)

```
[Phase A — new concept, build the schema first]
A1. Read the concept (in full, not patching holes)        ~10 min
A2. Encoding quiz: mostly multiple-choice + recall          ~5 min
    Goal: "remember + initial understanding," not application
    On pass, the concept's depth rises to 2

[Phase B — depth >= 2, hands-on consolidation]   <- the 7-step loop
B1. Breadth quiz as a ROUTER:
    pass -> go to B3;  still stuck -> fall back to A1 to patch
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

The key difference: **step B1's breadth quiz changes from a "fixed start" into a "router"** — its job is to decide whether you start at Phase A or jump straight to Phase B, not to re-test from scratch every time.

This way the old approach isn't replaced — it becomes Phase A of the new loop, and the two connect naturally.

## Where this lives in Exobrain

- `_scripts/prompts/promote-concept.md` — defines the `lab_status` frontmatter field and the depth→phase mapping (already updated).
- `concepts/<category>/<id>.md` — each concept now carries `lab_status` so you can see at a glance which concepts you've actually practiced vs. only read.
- Suggested next step: a `_scripts/prompts/lab-design.md` prompt that, given a concept, produces a fading-scaffold lab spec + prediction checkpoints + expected results, with the AI acting as the feedback layer (review prediction → review fill-in → emit quiz cards), and updates `lab_status` accordingly.

## Implementation status & the lightweight fallback

This is now wired into Exobrain:

- `_scripts/prompts/lab-design.md` — autonomous: generates the fading-scaffold lab artifacts under `labs/<concept-id>/` (spec, stubbed core, blank predictions, expected answer key) and sets `lab_status: scaffolded`. Available as a manual pipeline step: `pipeline.py concepts/<cat>/<id>.md --step lab`.
- `_scripts/prompts/lab-review.md` — interactive: run AFTER you fill the predictions and core. The AI grades, corrects, emits `application` quiz cards for your mistakes (due tomorrow), and updates `lab_status` to `completed`/`explained`. Deliberately NOT automated — automating it would recreate the "AI does it for you" problem.

**Fallback method:** `_scripts/prompts/labs-tiny-from-concept.md` is a lighter, single-shot lab generator (15–45 min, no scaffolding fade, no AI grading, no quiz feedback). Keep it as a fallback: if the full prediction → fill-core → review loop ever feels too slow or heavy for a given concept, drop back to a tiny lab for quick hands-on intuition.
