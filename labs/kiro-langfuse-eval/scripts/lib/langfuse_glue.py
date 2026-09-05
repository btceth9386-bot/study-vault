"""Glue between Kiro CLI and Langfuse's native dataset-experiment API.

Everything here is GIVEN and should run as-is, except `judge_score()` —
that function is `TODO: YOUR CORE` (see spec.md "Your core task").
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

from langfuse import Evaluation, Langfuse

from kiro_client import call_kiro
from judge_client import call_judge

LAB_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = LAB_DIR / "dataset" / "eval-items.jsonl"
DATASET_NAME = "kiro-support-faq-eval"
USAGE_LOG_PATH = Path(os.environ.get("KIRO_USAGE_LOG", str(LAB_DIR / "usage-log.jsonl")))

SYSTEM_PROMPTS = {
    "baseline": "You are a support assistant. Answer the user's question.",
    "improved": (
        "You are a support assistant for a SaaS product. Answer in one or two "
        "sentences, state the concrete policy or steps directly, and do not "
        "hedge or add disclaimers unless the question is genuinely ambiguous. "
        "If the question depends on information you were not given, say what "
        "is missing instead of guessing."
    ),
}


def load_local_items() -> list[dict[str, Any]]:
    items = []
    with DATASET_PATH.open() as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def seed_dataset(client: Langfuse) -> None:
    """Idempotent upsert of the local JSONL into a Langfuse dataset.

    Safe to call at the start of every run: dataset names are unique per
    project (create is a no-op if it already exists) and
    create_dataset_item() upserts by id, so re-running this never creates
    duplicate items.
    """
    try:
        client.create_dataset(
            name=DATASET_NAME,
            description="Sanitized support-FAQ items for the kiro-langfuse-eval lab",
        )
    except Exception:
        pass  # dataset already exists
    for item in load_local_items():
        client.create_dataset_item(
            dataset_name=DATASET_NAME,
            id=item["id"],
            input=item["input"],
            expected_output=item["expected_output"],
            metadata={"category": item["category"]},
        )


def make_kiro_task(*, system_prompt: str, model: Optional[str] = None):
    """Build a task(*, item, **kwargs) function bound to one variant/model.

    dataset.run_experiment() calls this once per dataset item. Each call is
    its own Kiro CLI invocation and becomes its own Langfuse trace.
    """

    def task(*, item, **kwargs) -> str:
        prompt = f"{system_prompt}\n\nUser question: {item.input}"
        result = call_kiro(prompt, model=model)
        return result.output

    return task


def judge_score(*, input, output, expected_output=None, metadata=None, **kwargs):
    """TODO: YOUR CORE.

    Implement LLM-as-judge scoring for one (input, output, expected_output)
    triple. Background: concepts/llm-engineering/llm-as-judge-evaluation.md.

    Requirements:
    1. Build a rubric prompt that gives the judge the question, the answer
       to grade, and the expected answer. Do not just string-compare —
       a correct answer can be worded differently from expected_output.
    2. Handle expected_output starting with "AMBIGUOUS_BY_DESIGN:" as its
       own case: score on whether the answer *acknowledges* the ambiguity
       or missing policy context, not on whether it matches a "right"
       answer — none exists for that item by design (see item-07).
    3. Call `call_judge(...)` (from judge_client.py) with your rubric
       prompt — never `call_kiro(...)`. The judge must run on a distinct
       provider from the task, both so its cost isn't attributed to the
       task's Kiro credit usage and to avoid self-preference bias from
       judging output produced by the same model family (see spec.md
       "Why the task model and the judge model must not be the same
       provider or model family").
    4. Parse a 1-5 score and a short reason out of the judge's free-text
       reply. Be tolerant of formatting (e.g. a regex for the first digit
       1-5); on a parse failure return value=-1 with the raw judge reply in
       `comment` instead of raising, so one bad judge reply does not crash
       the whole dataset run.
    5. Return an `Evaluation` (or a list of them). You do not need to call
       `langfuse.create_score()` yourself — returning it from an evaluator
       passed to `run_experiment()` is what attaches the score in Langfuse.

    Returns:
        Evaluation(name="judge_correctness", value=<1-5 or -1>, comment=<reason>)
    """
    raise NotImplementedError(
        "TODO: YOUR CORE — implement judge_score() in scripts/lib/langfuse_glue.py"
    )


def credit_usage_run_evaluator(*, item_results, **kwargs):
    """GIVEN. Aggregate credit usage logged by the Kiro `Stop` hook during
    this run into one run-level score.

    Reads USAGE_LOG_PATH, which scripts/log_usage.sh appends to every time
    the Stop hook fires. The hook only fires on Kiro CLI responses — judge
    calls go through judge_client.call_judge() and never touch Kiro CLI, so
    this count reflects task-side credit usage only, never evaluation cost.
    For an 8-item dataset, a healthy run therefore logs exactly 8 snapshots.
    If the hook never fired at all (wrong trigger name, wrong path,
    disabled), this reports 0 snapshots for a run that clearly made Kiro CLI
    calls — that gap is failure case 2 (see spec.md). If you see 16 instead
    of 8, judge_score() is still (incorrectly) calling call_kiro() instead
    of call_judge().
    """
    if not USAGE_LOG_PATH.exists():
        return Evaluation(
            name="credits_logged",
            value=0,
            comment=f"No usage log found at {USAGE_LOG_PATH} — Stop hook likely did not fire.",
        )

    snapshots = []
    with USAGE_LOG_PATH.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                snapshots.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    total_credits = sum(s.get("credits_used") or 0 for s in snapshots)
    return Evaluation(
        name="credits_logged",
        value=len(snapshots),
        comment=f"{len(snapshots)} usage snapshot(s), ~{total_credits:g} credits logged during this run.",
        metadata={"total_credits_used": total_credits},
    )
