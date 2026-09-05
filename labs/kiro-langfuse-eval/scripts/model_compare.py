#!/usr/bin/env python3
"""Medium-complexity task: run the SAME prompts through two Kiro CLI models
and compare judge score, latency, and credits.

GIVEN — no TODOs here. This is meant to be read and run, not implemented.
It reuses judge_score() from langfuse_glue, so fill that in first.

Model ids and cost multipliers come from https://kiro.dev/docs/models/
(cost is relative to "auto" = 1.0x). Cheap vs. expensive is a real trade,
not a hypothetical one: Haiku 4.5 is ~0.4x, Sonnet 5 is ~1.3x.

Usage:
    python scripts/model_compare.py --models auto haiku-4.5 sonnet-5
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from langfuse import Langfuse  # noqa: E402
from langfuse_glue import SYSTEM_PROMPTS, judge_score, load_local_items  # noqa: E402
from kiro_client import call_kiro  # noqa: E402

RUNS_DIR = Path(__file__).resolve().parent.parent / "runs"
SUBSET_IDS = {"item-01", "item-04", "item-07"}  # policy, billing, adversarial — kept small on purpose


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=["auto", "haiku-4.5", "sonnet-5"])
    args = parser.parse_args()

    client = Langfuse()
    items = [i for i in load_local_items() if i["id"] in SUBSET_IDS]
    system_prompt = SYSTEM_PROMPTS["improved"]

    table = []
    for model in args.models:
        for item in items:
            prompt = f"{system_prompt}\n\nUser question: {item['input']}"
            start = time.monotonic()
            with client.start_as_current_observation(
                name="model-compare-answer",
                as_type="generation",
                model=model,
                input=prompt,
                metadata={"item_id": item["id"], "task": "model_compare"},
            ) as generation:
                kiro_result = call_kiro(prompt, model=model)
                latency_ms = (time.monotonic() - start) * 1000
                generation.update(output=kiro_result.output)

                evaluation = judge_score(
                    input=item["input"],
                    output=kiro_result.output,
                    expected_output=item["expected_output"],
                    metadata={"category": item["category"]},
                )
                evaluation = evaluation[0] if isinstance(evaluation, list) else evaluation

                generation.score(
                    name="judge_correctness",
                    value=evaluation.value,
                    comment=f"[{model}] {evaluation.comment}",
                )

            table.append(
                {
                    "model": model,
                    "item_id": item["id"],
                    "score": evaluation.value,
                    "latency_ms": round(latency_ms, 1),
                }
            )

    RUNS_DIR.mkdir(exist_ok=True)
    out_path = RUNS_DIR / "model-compare.json"
    out_path.write_text(json.dumps(table, indent=2))

    print(f"{'model':<12}{'item_id':<12}{'score':<8}{'latency_ms':<12}")
    for row in table:
        print(f"{row['model']:<12}{row['item_id']:<12}{row['score']!s:<8}{row['latency_ms']:<12}")
    print(f"\nRaw results written to {out_path}")
    print(
        "Cross-reference with credit multipliers (kiro.dev/docs/models/) to judge "
        "whether the more expensive model's score gain is worth its cost."
    )


if __name__ == "__main__":
    main()
