"""Terminal interface for interactive quiz sessions."""

from __future__ import annotations

import argparse
from pathlib import Path

from _scripts import quiz_session


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for a quiz run."""

    parser = argparse.ArgumentParser(description="Run an interactive quiz session.")
    parser.add_argument("--count", type=int, default=10, help="Number of questions to review.")
    parser.add_argument("--concept", help="Limit the quiz to one concept ID.")
    parser.add_argument("--bank", default="quiz/bank.json", help="Path to quiz bank JSON.")
    parser.add_argument(
        "--kb-root",
        default=str(Path(__file__).resolve().parents[1]),
        help="Knowledge-base root that contains concepts/.",
    )
    return parser.parse_args()


def _print_review_materials(review_materials: list[dict]) -> None:
    print("本次考試涵蓋以下概念：")
    if not review_materials:
        print("目前沒有可複習的概念。")
        return

    for index, material in enumerate(review_materials, start=1):
        title = material.get("title", material["concept_id"])
        summary = material.get("summary", "").strip() or "無摘要可供顯示。"
        print(f"{index}. {title} ({material['concept_id']})")
        print(f"   {summary}")


def _prompt_answer(question: dict) -> tuple[str, bool | None]:
    if question["type"] == "multiple_choice":
        options = question.get("options") or []
        for index, option in enumerate(options):
            label = chr(ord("A") + index)
            print(f"  {label}. {option}")
        return input("你的答案：").strip(), None

    answer = input("你的作答：").strip()
    self_eval = input("你覺得自己答對了嗎？(y/n)：").strip().lower() == "y"
    return answer, self_eval


def _print_feedback(result: dict) -> None:
    status = "答對了" if result["correct"] else "答錯了"
    print(status)
    print(f"正確答案：{result['correct_answer']}")
    print(f"解釋：{result['explanation']}")
    print(
        "下次複習："
        f" {result['next_review']} (interval={result['new_interval_days']} days,"
        f" ease_factor={result['new_ease_factor']:.2f})"
    )


def _print_summary(summary: dict) -> None:
    print("\n本次統計")
    print(f"總題數：{summary['total']}")
    print(f"答對：{summary['correct']}")
    print(f"答錯：{summary['incorrect']}")
    print(f"答對率：{summary['accuracy']:.0%}")
    concepts = ", ".join(summary["concepts_reviewed"]) or "無"
    print(f"涵蓋概念：{concepts}")

    if summary["next_reviews"]:
        print("下次複習日期：")
        for item in summary["next_reviews"]:
            print(f"  - {item['question_id']}: {item['next_review']}")


def main() -> int:
    """CLI entry point that drives quiz_session functions."""

    args = parse_args()
    session = quiz_session.start_session(
        bank_path=args.bank,
        kb_root=args.kb_root,
        count=args.count,
        concept_id=args.concept,
    )

    _print_review_materials(session["review_materials"])
    if session["total_questions"] == 0:
        print("目前沒有符合條件的題目。")
        return 0

    input("\n按 Enter 開始答題...")

    while True:
        question = quiz_session.get_next_question(session["session_id"])
        if question is None:
            break

        print(
            f"\n第 {question['question_number']}/{question['total']} 題"
            f" [{question['type']}] ({question['concept_id']})"
        )
        print(question["question"])
        answer, self_eval = _prompt_answer(question)
        result = quiz_session.submit_answer(
            session["session_id"],
            question["id"],
            answer,
            self_eval=self_eval,
        )
        _print_feedback(result)

    summary = quiz_session.get_session_summary(session["session_id"])
    _print_summary(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
