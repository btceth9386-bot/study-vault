"""Stateless-friendly quiz session helpers built around in-memory session state."""

from __future__ import annotations

from copy import deepcopy
from datetime import date, timedelta
import json
from pathlib import Path
import uuid

from _scripts.sm2_scheduler import update_on_correct, update_on_incorrect


_SESSIONS: dict[str, dict] = {}


def _parse_today(today: str | None) -> date:
    return date.fromisoformat(today) if today is not None else date.today()


def _load_questions(bank_path: str, concept_id: str | None, today: date, count: int) -> list[dict]:
    payload = json.loads(Path(bank_path).read_text(encoding="utf-8"))
    questions = payload.get("questions", [])

    filtered_questions = []
    for question in questions:
        if concept_id is not None and question.get("concept_id") != concept_id:
            continue
        next_review = question.get("next_review")
        if next_review is None or next_review <= today.isoformat():
            filtered_questions.append(deepcopy(question))

    return filtered_questions[:count]


def _build_review_materials(questions: list[dict]) -> list[dict]:
    concept_ids = []
    for question in questions:
        concept_id = question.get("concept_id")
        if concept_id not in concept_ids:
            concept_ids.append(concept_id)

    return [
        {
            "concept_id": concept_id,
            "title": concept_id,
            "summary": "",
            "related_concepts": [],
            "source_refs": [],
        }
        for concept_id in concept_ids
    ]


def _question_preview(question: dict) -> dict:
    return {
        "id": question["id"],
        "concept_id": question["concept_id"],
        "type": question["type"],
        "difficulty": question["difficulty"],
    }


def _public_question(question: dict, question_number: int, total: int) -> dict:
    return {
        "question_number": question_number,
        "total": total,
        "id": question["id"],
        "concept_id": question["concept_id"],
        "type": question["type"],
        "difficulty": question["difficulty"],
        "question": question["question"],
        "options": question.get("options"),
    }


def _normalize_interval_days(value: float | int) -> int:
    return max(1, int(round(value)))


def _grade_answer(question: dict, answer: str, self_eval: bool | None) -> bool:
    question_type = question["type"]
    if question_type == "multiple_choice":
        return answer.strip() == question["answer"]
    if self_eval is None:
        raise ValueError("self_eval is required for non-multiple-choice questions")
    return self_eval


def start_session(
    bank_path: str,
    kb_root: str,
    count: int = 10,
    concept_id: str | None = None,
    today: str | None = None,
) -> dict:
    """Create a quiz session from due questions in the quiz bank."""

    review_date = _parse_today(today)
    questions = _load_questions(bank_path, concept_id, review_date, count)
    session_id = str(uuid.uuid4())

    _SESSIONS[session_id] = {
        "bank_path": bank_path,
        "kb_root": kb_root,
        "today": review_date,
        "questions": questions,
        "answers": {},
    }

    return {
        "session_id": session_id,
        "review_materials": _build_review_materials(questions),
        "total_questions": len(questions),
        "questions_preview": [_question_preview(question) for question in questions],
    }


def get_next_question(session_id: str) -> dict | None:
    """Return the next unanswered question without revealing its answer."""

    session = _SESSIONS[session_id]
    total = len(session["questions"])
    for index, question in enumerate(session["questions"], start=1):
        if question["id"] not in session["answers"]:
            return _public_question(question, question_number=index, total=total)
    return None


def submit_answer(
    session_id: str,
    question_id: str,
    answer: str,
    self_eval: bool | None = None,
) -> dict:
    """Submit an answer, update SM-2 scheduling fields, and record the result."""

    session = _SESSIONS[session_id]
    review_date = session["today"]
    question = next(
        (item for item in session["questions"] if item["id"] == question_id),
        None,
    )
    if question is None:
        raise KeyError(f"Unknown question_id: {question_id}")
    if question_id in session["answers"]:
        raise ValueError(f"Question already answered: {question_id}")

    is_correct = _grade_answer(question, answer, self_eval)
    updated_question = (
        update_on_correct(question, review_date=review_date)
        if is_correct
        else update_on_incorrect(question, review_date=review_date)
    )

    normalized_interval = _normalize_interval_days(updated_question["interval_days"])
    updated_question["interval_days"] = normalized_interval
    updated_question["next_review"] = (
        review_date + timedelta(days=normalized_interval)
    ).isoformat()

    question_index = session["questions"].index(question)
    session["questions"][question_index] = updated_question
    session["answers"][question_id] = is_correct

    return {
        "correct": is_correct,
        "correct_answer": question["answer"],
        "explanation": question["explanation"],
        "new_interval_days": updated_question["interval_days"],
        "new_ease_factor": updated_question["ease_factor"],
        "next_review": updated_question["next_review"],
    }


def get_session_summary(session_id: str) -> dict:
    """Return aggregate statistics for a completed or in-progress session."""

    session = _SESSIONS[session_id]
    total = len(session["questions"])
    correct = sum(1 for result in session["answers"].values() if result)
    incorrect = sum(1 for result in session["answers"].values() if not result)
    concepts_reviewed = list(dict.fromkeys(question["concept_id"] for question in session["questions"]))

    return {
        "total": total,
        "correct": correct,
        "incorrect": incorrect,
        "accuracy": (correct / total) if total else 0.0,
        "concepts_reviewed": concepts_reviewed,
        "next_reviews": [
            {
                "question_id": question["id"],
                "next_review": question.get("next_review"),
            }
            for question in session["questions"]
            if question["id"] in session["answers"]
        ],
    }
