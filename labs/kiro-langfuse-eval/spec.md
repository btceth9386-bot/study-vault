# Lab: Kiro CLI + Langfuse for Evaluation

- **Concepts**: [[llm-observability]], [[llm-as-judge-evaluation]], [[acp-agent-backend-for-ides]]
- **Tools**: Kiro CLI (openab's ACP agent backend), Langfuse (in-cluster `langfuse` namespace)
- **Setup mode**: real-tool
- **Time box**: 90–120 min (advanced — explicitly scoped larger than the usual 15–45 min lab: dataset + scoring workflow, real tracing, a baseline/improved comparison, two failure cases, and a model-switch task)
- **Starting knowledge**: You can read a Langfuse trace (trace → observation → score) and you know what a rubric-based LLM judge does. You do not need prior Kiro CLI experience — the ACP backend shape is the same "agent exposes a session over a protocol" pattern as [[acp-agent-backend-for-ides]].

## Quick primer

Kiro CLI is the default ACP agent backend openab runs (`kiro-cli acp --trust-all-tools`, per [openab's kiro.md](https://github.com/openabdev/openab/blob/main/docs/kiro.md)). Called with `kiro-cli chat --no-interactive`, it reads stdin as one input and prints its first response to stdout, then exits — the same shape as the credit-usage check:

```bash
echo "/usage" | kiro-cli chat --no-interactive 2>&1 \
  | sed 's/\x1b\[[0-9;]*[mGKHFABCDJsuhl?]//g' | grep -A 20 "Estimated Usage"
```

Kiro CLI is **not** natively instrumented for Langfuse. Every trace in this lab exists because our harness code calls the Langfuse SDK around each `kiro-cli` subprocess call — that bridge is the integration seam this lab is about. Separately, Kiro supports **agent hooks**: JSON files under `.kiro/hooks/`, matched on named triggers (`Stop`, `PreToolUse`, `UserPromptSubmit`, `SessionStart`, `PostFileSave`, …; see [kiro.dev/docs/hooks](https://kiro.dev/docs/hooks/#available-triggers)). This lab uses the `Stop` trigger to auto-log credit usage after every response, instead of a human remembering to run `/usage`.

Langfuse models observability as **trace → observation → score** ([[llm-observability]]) and evaluation as an LLM judge applying a rubric to produce a score ([[llm-as-judge-evaluation]]). The Python SDK's `dataset.run_experiment(task=..., evaluators=[...])` does both in one call: it runs your task function over every dataset item, traces each call, runs your evaluators, and creates a named **dataset run** so two variants (baseline vs. improved) can be compared side by side in the Langfuse UI.

## Goal

Wire Kiro CLI's non-interactive output into Langfuse as scored, comparable traces — so that "did the improved prompt actually get better, and what did it cost in credits" is a question you can answer by looking at data, not by re-reading transcripts.

## Prerequisites, cost, and infrastructure

- **Kiro CLI**: installed and authenticated (`KIRO_API_KEY` env var — see openab's kiro.md). Not installed in a bare Claude/openab pod by default; this lab was scaffolded from a pod where it was absent, so **Setup step 5 (below) is unverified in this repo** — run it yourself before trusting `scripts/lib/kiro_client.py`'s exact invocation shape.
- **Langfuse**: this lab assumes an in-cluster instance. Reachability was confirmed from this pod at design time:
  ```
  $ curl http://langfuse-web.langfuse.svc.cluster.local:3000/api/public/health
  {"status":"OK","version":"3.173.0"}
  ```
  You still need your own project's `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` (Langfuse UI → Project Settings → API Keys) — not provided here. Outside this cluster, point `LANGFUSE_BASE_URL` at your own Langfuse instance instead.
- **Cost risk**: every dataset run makes ~8 Kiro CLI calls (task) + ~8 more (judge) = ~16 calls per variant; two variants + the model-compare task (3 items × up to 3 models) is on the order of 40–50 Kiro CLI calls total. Check `/usage` before and after if you're on a metered plan. The model-compare task is deliberately restricted to a 3-item subset to bound this.
- **Mock fallback**: none provided. This lab is `real-tool` because the whole point is observing real Kiro CLI output shapes and a real Langfuse UI — a mocked Kiro CLI would remove exactly what's being taught. If you don't have Kiro CLI access, read the code and `expected.md` instead of running it; the architecture and both failure cases are fully specified in this file.

## What the AI scaffolded

- `dataset/eval-items.jsonl` — 8 sanitized support-FAQ items, one deliberately ambiguous (`item-07`).
- `scripts/lib/kiro_client.py` — subprocess wrapper around `kiro-cli chat --no-interactive`, ANSI stripping, latency timing.
- `scripts/lib/usage_parser.py` — turns a raw `/usage` text block into `{credits_used, credits_limit, raw}`.
- `scripts/lib/langfuse_glue.py` — dataset seeding, per-variant system prompts, the `make_kiro_task()` builder, and `credit_usage_run_evaluator()`. **`judge_score()` in this file is your core task — see below.**
- `scripts/log_usage.sh` — the script the `Stop` hook is supposed to invoke; appends one JSON line per response to `usage-log.jsonl`.
- `.kiro/hooks/log-usage-on-stop.json` — a hook wired to the `Stop` trigger. **Shipped with a bug — see Failure case 2.**
- `scripts/run_variant.py` — runs one full dataset-run variant (`baseline` or `improved`) through `dataset.run_experiment()`, prints results, writes `runs/<variant>-summary.json`.
- `scripts/model_compare.py` — the medium-complexity task: runs a 3-item subset through 2–3 Kiro CLI models with the *same* (improved) prompt, scores each, writes `runs/model-compare.json`.
- `scripts/compare_report.py` — the one runnable check: reads both variant summaries and prints a pass/fail comparison (also where Failure case 2 becomes visible as a FAIL line).
- `scripts/setup.sh` — prerequisite + smoke-test script (kiro-cli present, Langfuse reachable, one live `/model` + prompt round trip, one usage-log line).

## Your core task

Implement `judge_score()` in `scripts/lib/langfuse_glue.py` (currently `raise NotImplementedError`). It is an item-level Langfuse evaluator: given `(input, output, expected_output, metadata)` for one dataset item, call Kiro CLI a **second, independent time** with a rubric prompt, and return an `Evaluation(name="judge_correctness", value=<1-5 or -1>, comment=<reason>)`.

The five numbered requirements are spelled out as a docstring directly above the `raise NotImplementedError` — including how to handle `item-07`'s `AMBIGUOUS_BY_DESIGN:` expected output, which is the seam that connects your rubric design to Failure case 1 below.

## Steps

1. Read the scaffold (`scripts/lib/langfuse_glue.py` and `scripts/lib/kiro_client.py` first).
2. Fill `predictions.md` BEFORE running (do not skip — prediction comes first).
3. `./scripts/setup.sh` — fixes/confirms your environment. **Setup / verify Kiro CLI**: step 5 of that script is a live smoke test of the exact stdin shape `call_kiro()` depends on (`/model <id>` line + prompt, piped together). If Kiro CLI treats that as two turns instead of one, or `--model` turns out to be a real top-level flag in your version, adjust `call_kiro()` before continuing — this detail could not be verified from documentation alone at scaffold time.
4. Implement the stubbed core (`judge_score()`, marked `TODO: YOUR CORE`).
5. Run `python scripts/run_variant.py --variant baseline`, then rename/clear `usage-log.jsonl`, then run `python scripts/run_variant.py --variant improved`. Watch for Failure case 2 between these two runs (see below — do not "fix" it before it happens once).
6. Run `python scripts/compare_report.py` — this is your runnable check.
7. Run `python scripts/model_compare.py` for the medium-complexity model-switch task.
8. Open both dataset run URLs (printed by `run_variant.py`) in the Langfuse UI; use its dataset-run comparison view for the side-by-side.
9. Open the published review site to inspect the architecture and acceptance criteria.
10. Run `lab-review.md` so the AI grades your prediction and core and emits quiz cards.

## Failure / comparison case

**Case 1 — judge miscalibration on an ambiguous item.** `item-07` describes a double-charge refund question entangled with an unrelated prior credit — reasonable people disagree on the right answer, and `expected_output` says so explicitly (`AMBIGUOUS_BY_DESIGN:`). A rubric that only checks "does this match the expected answer" will either score it arbitrarily or fail outright on this item, because there is no single correct answer to match. Run your judge on item-07 specifically and read its `comment`. This is not a bug to fix by tightening string matching — it's the concept: an LLM-as-judge rubric has to define what "good" means for ambiguous inputs, or its scores on those inputs are noise ([[llm-as-judge-evaluation]] open question: "which evaluation criteria are safe to automate?").

**Case 2 — the credit-usage hook silently doesn't fire.** `.kiro/hooks/log-usage-on-stop.json` uses `"trigger": "PostStop"`. The real Kiro trigger name (per [kiro.dev/docs/hooks](https://kiro.dev/docs/hooks/#available-triggers)) is `"Stop"` — `PostStop` matches nothing, so the hook is installed but inert. Symptom: after running the `improved` variant, `usage-log.jsonl` has zero new lines, `credit_usage_run_evaluator()` reports `credits_logged: 0` for that run in Langfuse, and `scripts/compare_report.py` prints an explicit `FAIL` line pointing at this file. This is deliberately the same class of failure real teams hit: a cost-tracking integration that looks configured but isn't wired to the trigger the tool actually emits, and nothing loud tells you until you go looking for the data that should be there and isn't.

## Acceptance criteria

- Both `baseline-v1` and `improved-v1` dataset runs exist in Langfuse with 8 scored items each.
- `scripts/compare_report.py` exits 0 (after you fix Failure case 2's hook trigger and re-run `improved`).
- The improved variant's mean `judge_correctness` is higher than baseline's on at least 6 of 8 items — item-07 is exempt from this bar by design (see Failure case 1).
- `runs/model-compare.json` has one row per (model × item) with a non-null `score` and `latency_ms`.
- You can explain, in one sentence each: (a) why item-07's score does not falsify your judge, and (b) what in the hook config caused Failure case 2 and how you found it (not just "I fixed it").
