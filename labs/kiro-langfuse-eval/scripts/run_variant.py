#!/usr/bin/env python3
"""Run one dataset-run variant (baseline or improved) through Kiro CLI and
score it in Langfuse. GIVEN — run this after filling judge_score().

Usage:
    python scripts/run_variant.py --variant baseline
    python scripts/run_variant.py --variant improved
    python scripts/run_variant.py --variant improved --model haiku-4.5
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from langfuse import Langfuse  # noqa: E402
from langfuse_glue import (  # noqa: E402
    DATASET_NAME,
    SYSTEM_PROMPTS,
    credit_usage_run_evaluator,
    judge_score,
    make_kiro_task,
    seed_dataset,
)

RUNS_DIR = Path(__file__).resolve().parent.parent / "runs"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=sorted(SYSTEM_PROMPTS), required=True)
    parser.add_argument(
        "--model", default=None, help="Kiro CLI model id, e.g. auto, haiku-4.5, sonnet-5"
    )
    args = parser.parse_args()

    client = Langfuse()
    seed_dataset(client)
    dataset = client.get_dataset(DATASET_NAME)

    task = make_kiro_task(system_prompt=SYSTEM_PROMPTS[args.variant], model=args.model)

    result = dataset.run_experiment(
        name=f"{args.variant} — {args.model or 'default'}",
        run_name=f"{args.variant}-v1",
        description=(
            f"Kiro CLI ({args.model or 'default model'}) answering the support-FAQ "
            f"dataset with the {args.variant} system prompt."
        ),
        task=task,
        evaluators=[judge_score],
        run_evaluators=[credit_usage_run_evaluator],
        metadata={"variant": args.variant, "model": args.model or "default"},
    )

    print(result.format(include_item_results=True))
    print(f"\nDataset run URL: {result.dataset_run_url}")

    RUNS_DIR.mkdir(exist_ok=True)
    summary = {
        "variant": args.variant,
        "model": args.model or "default",
        "run_name": result.run_name,
        "dataset_run_url": result.dataset_run_url,
        "items": [
            {
                "input": ir.item.input if hasattr(ir.item, "input") else ir.item.get("input"),
                "output": ir.output,
                "evaluations": [
                    {"name": e.name, "value": e.value, "comment": e.comment}
                    for e in ir.evaluations
                ],
            }
            for ir in result.item_results
        ],
        "run_evaluations": [
            {"name": e.name, "value": e.value, "comment": e.comment}
            for e in result.run_evaluations
        ],
    }
    out_path = RUNS_DIR / f"{args.variant}-summary.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"Local summary written to {out_path}")


if __name__ == "__main__":
    main()
