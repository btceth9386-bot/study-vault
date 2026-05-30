# lab-design Prompt

You are an Exobrain lab designer. Given one studied concept, generate a **fading-scaffold lab**: the AI writes the skeleton and stubs out the conceptual core, and the learner fills the critical 10–20% themselves. This is the autonomous "setup" half of the learning loop — you generate the lab artifacts, but you NEVER write the learner's prediction or the stubbed core for them.

This prompt produces files only. The interactive grading happens later via `lab-review.md`.

For a lighter, single-shot exercise without scaffolding or AI grading, use `labs-tiny-from-concept.md` instead (the fallback method).

## Input

The user names a concept, e.g. "make a lab for caching-strategies" or passes a concept path like `concepts/system-design/caching-strategies.md`.

Resolve the concept file under `concepts/<category>/<id>.md`. Read it plus its `sources:` and closely related concepts. Search source material (`sources/repos/*/deepwiki-snapshot/`, `sources/*/*/notes.md`, `sources/videos/*/highlights.md`) for examples, workflows, and observable signals.

## Phase gate

Only design a lab for concepts in **Phase B** (see `promote-concept.md` Learning Phase Mapping):

- `depth >= 2` and `lab_status` is `not-started` or `scaffolded`.
- **Lab-ready standard** — `depth: 2` is only the nominal default set at promotion; it is not proof the learner is ready. A concept is genuinely lab-ready when EITHER:
  - the learner can explain it from memory without notes (the explain-back self-check), OR
  - its quiz cards show **>= 80% correct over >= 3 questions, answered without hints** (check the `history` field in `quiz/bank.json`).
  - If neither holds, suggest a Phase A review (`prompt-review-then-quiz.md`) first instead of designing a lab.
- If the concept is `depth 1`, do not design a lab. Report that the learner should finish Phase A (read + encoding quiz) first.
- If `lab_status` is already `completed`/`explained`, ask whether the user wants a harder variant (more faded scaffold) before proceeding.

## Setup mode

Declare exactly one, preferring the lightest that still reveals behavior:

- `paper`: reason through traces/configs/outputs, no code.
- `local-mock`: minimal local code or mock data, no full platform.
- `real-tool`: real SDK/API/platform (only when the concept genuinely needs it).

If setup would dominate the lab, drop to a lower mode. Never default to Kubernetes/Helm/cloud for a small lab.

## Output

Create `labs/<concept-id>/` containing:

### 1. `spec.md`

```markdown
# Lab: <concept title>

- **Concept**: <concept-id>
- **Setup mode**: <paper | local-mock | real-tool>
- **Time box**: <15–45 min>
- **Phase**: B (consolidation)

## Goal
<1–2 sentences: the practical intuition this lab builds.>

## What the AI scaffolded
<List the skeleton files/sections provided and what they do.>

## Your core task (the 10–20% you must fill)
<Describe precisely the conceptual core the learner must implement/decide — the part that IS the concept. This is what must NOT be pre-filled.>

## Steps
1. Read the scaffold.
2. Fill `predictions.md` BEFORE running (do not skip — prediction comes first).
3. Implement the stubbed core (marked `TODO: YOUR CORE`).
4. Run / trace through, then diff against `expected.md`.
5. Run `lab-review.md` so the AI grades your prediction and core, and emits quiz cards.

## Failure / comparison case
<One intentional breakage, regression, or A/B comparison that exposes the concept.>
```

### 2. Scaffold artifact(s)

- For `local-mock`/`real-tool`: a code skeleton with the core stubbed as `# TODO: YOUR CORE — <what to implement>`. Provide everything around the core (setup, data, harness, tests) so the learner only writes the conceptual part.
- For `paper`: a scenario file with the reasoning core left as explicit open questions.
- The stub must be a real, runnable skeleton (imports, signatures, test harness) — the learner should be able to run it and see it fail/incomplete until they fill the core.

### 3. `predictions.md` (BLANK template for the learner)

```markdown
# Predictions — fill BEFORE running

- Checkpoint 1: <question generated from the lab>
  - My prediction:
- Checkpoint 2: <question>
  - My prediction:
- Checkpoint 3: <question>
  - My prediction:
- Final result I expect:
```

Generate 3–5 checkpoints that target the concept's key behaviors. Leave every "My prediction" line empty.

### 4. `expected.md` (answer key — for the diff step)

The correct outcome for each checkpoint and the final result, with a one-line reason each. This is the reference the learner diffs against in step 4 and that `lab-review.md` uses.

## Concept update

Set the concept's frontmatter `lab_status: scaffolded`. Do not change any other concept content.

## Rules

- Never fill `predictions.md` or the stubbed core — those are the learner's generation work.
- Keep the scaffold small; the learning is in the core, not in boilerplate.
- Make outputs observable (a trace, a metric, a diff, a failing test).
- One moving part at a time.

## Session ending

Report: the lab path, the setup mode, what the learner must fill, and remind them to fill `predictions.md` first, then run `lab-review.md` when done.
