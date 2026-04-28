"""SM-2 scheduling helpers for quiz bank entries."""

from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, timedelta
import json
from pathlib import Path
from typing import Any


DEFAULT_EASE_FACTOR = 2.5
MIN_EASE_FACTOR = 1.3
DEFAULT_INTERVAL_DAYS = 1


def _today() -> date:
    return date.today()


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _load_bank(bank_path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(bank_path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("bank.json must contain a JSON object")

    questions = payload.get("questions")
    if not isinstance(questions, list):
        raise ValueError("bank.json must contain a questions list")

    return payload


def _write_bank(bank_path: str | Path, payload: dict[str, Any]) -> None:
    Path(bank_path).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _normalize_question(question: dict[str, Any]) -> dict[str, Any]:
    updated = deepcopy(question)
    updated["interval_days"] = float(updated.get("interval_days", DEFAULT_INTERVAL_DAYS))
    updated["ease_factor"] = max(float(updated.get("ease_factor", DEFAULT_EASE_FACTOR)), MIN_EASE_FACTOR)
    history = updated.get("history", [])
    if not isinstance(history, list):
        raise ValueError("question history must be a list")
    updated["history"] = deepcopy(history)
    return updated


def _next_review_for(interval_days: float, review_date: date) -> str:
    next_review = datetime.combine(review_date, datetime.min.time()) + timedelta(days=interval_days)
    return next_review.date().isoformat()


def _apply_result(question: dict[str, Any], *, correct: bool, review_date: date | None = None) -> dict[str, Any]:
    updated = _normalize_question(question)
    review_date = review_date or _today()

    if correct:
        updated["interval_days"] *= updated["ease_factor"]
        result = "correct"
    else:
        updated["interval_days"] = DEFAULT_INTERVAL_DAYS
        updated["ease_factor"] = max(MIN_EASE_FACTOR, updated["ease_factor"] - 0.2)
        result = "incorrect"

    review_date_str = review_date.isoformat()
    updated["last_attempted"] = review_date_str
    updated["next_review"] = _next_review_for(updated["interval_days"], review_date)
    updated["history"].append({"date": review_date_str, "result": result})
    return updated


def update_on_correct(question: dict) -> dict:
    """Correct answer: multiply interval by ease factor and keep ease factor unchanged."""

    return _apply_result(question, correct=True)


def update_on_incorrect(question: dict) -> dict:
    """Incorrect answer: reset interval and reduce ease factor with a floor."""

    return _apply_result(question, correct=False)


def get_due_questions(bank_path: str, today: str = None) -> list:
    """Return questions where next_review is on or before today."""

    payload = _load_bank(bank_path)
    review_date = _parse_date(today) if today else _today()

    due_questions: list[dict[str, Any]] = []
    for question in payload["questions"]:
        next_review = question.get("next_review")
        if next_review is None:
            continue
        if _parse_date(next_review) <= review_date:
            due_questions.append(deepcopy(question))

    return due_questions


def update_bank(bank_path: str, question_id: str, correct: bool) -> None:
    """Update SM-2 scheduling fields for the specified question in bank.json."""

    payload = _load_bank(bank_path)

    for index, question in enumerate(payload["questions"]):
        if question.get("id") != question_id:
            continue

        payload["questions"][index] = _apply_result(question, correct=correct)
        _write_bank(bank_path, payload)
        return

    raise ValueError(f"Question not found: {question_id}")
