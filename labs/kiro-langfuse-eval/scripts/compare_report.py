#!/usr/bin/env python3
"""The lab's one runnable check.

Reads the local summaries written by run_variant.py for both variants and
prints a pass/fail comparison. Run this after both `run_variant.py
--variant baseline` and `run_variant.py --variant improved` have completed.

Exit code 0 means the acceptance criteria in spec.md were met; exit code 1
means something is missing or the improved variant did not actually improve
on the baseline — read the printed reasons either way.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from statistics import mean

RUNS_DIR = Path(__file__).resolve().parent.parent / "runs"


def load_summary(variant: str) -> dict | None:
    path = RUNS_DIR / f"{variant}-summary.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def judge_scores(summary: dict) -> list[float]:
    scores = []
    for item in summary["items"]:
        for ev in item["evaluations"]:
            if ev["name"] == "judge_correctness" and isinstance(ev["value"], (int, float)):
                scores.append(ev["value"])
    return scores


def credits_logged(summary: dict) -> int:
    for ev in summary["run_evaluations"]:
        if ev["name"] == "credits_logged":
            return ev["value"]
    return 0


def main() -> int:
    baseline = load_summary("baseline")
    improved = load_summary("improved")

    ok = True

    if baseline is None or improved is None:
        missing = "baseline" if baseline is None else "improved"
        print(f"FAIL: missing runs/{missing}-summary.json — run scripts/run_variant.py --variant {missing} first.")
        return 1

    base_scores = judge_scores(baseline)
    impr_scores = judge_scores(improved)

    if not base_scores or not impr_scores:
        print(
            "FAIL: no judge_correctness evaluations found in one or both runs. "
            "Most likely judge_score() in scripts/lib/langfuse_glue.py is still "
            "the TODO stub (it raises NotImplementedError) — implement it, then "
            "re-run both scripts/run_variant.py invocations."
        )
        return 1

    print(f"{'':<24}{'baseline':<14}{'improved':<14}")
    print(f"{'mean judge score':<24}{mean(base_scores):<14.2f}{mean(impr_scores):<14.2f}")
    print(f"{'items scored':<24}{len(base_scores):<14}{len(impr_scores):<14}")
    print(f"{'credits_logged':<24}{credits_logged(baseline):<14}{credits_logged(improved):<14}")

    if mean(impr_scores) < mean(base_scores):
        print(
            "\nWARN: improved variant did not score higher than baseline. "
            "That is a valid lab outcome (see spec.md Acceptance criteria) — "
            "inspect item-07 (the adversarial item) and your rubric before assuming a bug."
        )

    if credits_logged(baseline) > 0 and credits_logged(improved) == 0:
        print(
            "\nFAIL: baseline run logged credit usage but improved run logged none. "
            "This is failure case 2 — check .kiro/hooks/log-usage-on-stop.json's "
            "`trigger` field against https://kiro.dev/docs/hooks/#available-triggers."
        )
        ok = False

    print(f"\nBaseline run: {baseline['dataset_run_url']}")
    print(f"Improved run: {improved['dataset_run_url']}")
    print("Open both in Langfuse and use the dataset run comparison view for the side-by-side.")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
