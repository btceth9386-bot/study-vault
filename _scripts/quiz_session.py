"""Pure quiz-session logic without terminal or network I/O."""

from __future__ import annotations

import json
import uuid
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import yaml

from _scripts import sm2_scheduler
from _scripts.quiz_manager import get_review_pack


SESSION_STORE: dict[str, dict[str, Any]] = {}
_SESSIONS = SESSION_STORE


def _today_value(today: str | None) -> str:
    return today or date.today().isoformat()


def _normalize_bank_payload(data: Any) -> tuple[str, list[dict[str, Any]]]:
    if isinstance(data, list):
        entries = data
        payload_kind = "list"
    elif isinstance(data, dict):
        entries = data.get("questions")
        payload_kind = "dict"
    else:
        raise ValueError("Quiz bank must be a JSON array or an object with a questions list")

    if not isinstance(entries, list):
        raise ValueError("Quiz bank questions must be a list")

    normalized: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Quiz bank entries must be objects")
        normalized.append(deepcopy(entry))

    return payload_kind, normalized


def _load_bank_entries(bank_path: str | Path) -> tuple[str, list[dict[str, Any]]]:
    path = Path(bank_path)
    if not path.exists():
        raise FileNotFoundError(f"Quiz bank not found: {bank_path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    return _normalize_bank_payload(data)


def _write_bank_entries(bank_path: str | Path, payload_kind: str, entries: list[dict[str, Any]]) -> None:
    payload: list[dict[str, Any]] | dict[str, list[dict[str, Any]]]
    if payload_kind == "dict":
        payload = {"questions": entries}
    else:
        payload = entries

    Path(bank_path).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _select_questions(
    bank_path: str | Path,
    count: int,
    today: str,
    concept_id: str | None,
) -> tuple[str, list[dict[str, Any]]]:
    payload_kind, all_entries = _load_bank_entries(bank_path)
    if concept_id is None:
        try:
            return payload_kind, get_review_pack(bank_path, count=count, today=today)
        except ValueError:
            pass

    filtered_entries = all_entries
    if concept_id is not None:
        filtered_entries = [
            entry for entry in all_entries if entry.get("concept_id") == concept_id
        ]

    due_entries = [entry for entry in filtered_entries if entry.get("next_review", "") <= today]
    future_entries = [entry for entry in filtered_entries if entry.get("next_review", "") > today]

    due_entries.sort(key=lambda entry: (entry.get("next_review", ""), entry.get("id", "")))
    future_entries.sort(key=lambda entry: (entry.get("next_review", ""), entry.get("id", "")))

    return payload_kind, due_entries[:count] + future_entries[: max(0, count - len(due_entries))]


def _parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    if not content.startswith("---\n"):
        return {}, content

    parts = content.split("---\n", 2)
    if len(parts) < 3:
        return {}, content

    frontmatter = yaml.safe_load(parts[1]) or {}
    if not isinstance(frontmatter, dict):
        frontmatter = {}

    return frontmatter, parts[2]


def _extract_summary(body: str) -> str:
    lines = body.splitlines()
    capture = False
    collected: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            heading_text = stripped.lstrip("#").strip().lower()
            if heading_text in {"摘要", "summary"}:
                capture = True
                continue
            if capture:
                break

        if capture:
            if stripped:
                collected.append(stripped)
            elif collected:
                break

    if collected:
        return " ".join(collected)

    paragraphs = [paragraph.strip() for paragraph in body.split("\n\n") if paragraph.strip()]
    for paragraph in paragraphs:
        if not paragraph.startswith("#"):
            return " ".join(paragraph.splitlines()).strip()

    return ""


def _find_concept_file(kb_root: str | Path, concept_id: str) -> Path:
    concepts_root = Path(kb_root) / "concepts"
    if not concepts_root.exists():
        return concepts_root / f"{concept_id}.md"

    direct_match = concepts_root / f"{concept_id}.md"
    if direct_match.exists():
        return direct_match

    for candidate in concepts_root.rglob("*.md"):
        frontmatter, _ = _parse_frontmatter(candidate.read_text(encoding="utf-8"))
        if frontmatter.get("id") == concept_id:
            return candidate

    return direct_match


def _load_review_material(kb_root: str | Path, concept_id: str) -> dict[str, Any]:
    concept_path = _find_concept_file(kb_root, concept_id)
    if not concept_path.exists():
        return {
            "concept_id": concept_id,
            "title": concept_id,
            "summary": "",
            "related_concepts": [],
            "source_refs": [],
        }

    frontmatter, body = _parse_frontmatter(concept_path.read_text(encoding="utf-8"))

    related_concepts = frontmatter.get("related_concepts", [])
    if not isinstance(related_concepts, list):
        related_concepts = []

    source_refs = frontmatter.get("sources", [])
    if not isinstance(source_refs, list):
        source_refs = []

    return {
        "concept_id": concept_id,
        "title": frontmatter.get("title", concept_id),
        "summary": _extract_summary(body),
        "related_concepts": related_concepts,
        "source_refs": source_refs,
    }


def _question_preview(question: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": question["id"],
        "concept_id": question["concept_id"],
        "type": question["type"],
        "difficulty": question["difficulty"],
    }


def _public_question(question: dict[str, Any], question_number: int, total: int) -> dict[str, Any]:
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


def _get_session(session_id: str) -> dict[str, Any]:
    try:
        return SESSION_STORE[session_id]
    except KeyError as exc:
        raise KeyError(f"Unknown session_id: {session_id}") from exc


def _question_is_correct(question: dict[str, Any], answer: str, self_eval: bool | None) -> bool:
    if question["type"] == "multiple_choice":
        return answer.strip().lower() == str(question["answer"]).strip().lower()

    if self_eval is None:
        raise ValueError("self_eval is required for short-answer and application questions")

    return self_eval


def _apply_review_update(question: dict[str, Any], correct: bool, today_value: str) -> dict[str, Any]:
    review_date = date.fromisoformat(today_value)
    updated = sm2_scheduler._apply_result(question, correct=correct, review_date=review_date)
    interval_days = max(1, int(round(float(updated["interval_days"]))))
    updated["interval_days"] = interval_days
    updated["next_review"] = (review_date + timedelta(days=interval_days)).isoformat()
    return updated


def start_session(
    bank_path: str,
    kb_root: str,
    count: int = 10,
    concept_id: str | None = None,
    today: str | None = None,
) -> dict[str, Any]:
    """Create a session and return review materials plus question preview."""

    today_value = _today_value(today)
    payload_kind, questions = _select_questions(
        bank_path,
        count=count,
        today=today_value,
        concept_id=concept_id,
    )

    session_id = uuid.uuid4().hex
    concept_ids = list(dict.fromkeys(question["concept_id"] for question in questions))
    review_materials = [_load_review_material(kb_root, current_concept_id) for current_concept_id in concept_ids]

    SESSION_STORE[session_id] = {
        "bank_path": bank_path,
        "bank_payload_kind": payload_kind,
        "kb_root": kb_root,
        "today": today_value,
        "questions": [deepcopy(question) for question in questions],
        "cursor": 0,
        "results": {},
        "review_materials": review_materials,
    }

    return {
        "session_id": session_id,
        "review_materials": review_materials,
        "total_questions": len(questions),
        "questions_preview": [_question_preview(question) for question in questions],
    }


def get_next_question(session_id: str) -> dict[str, Any] | None:
    """Return the next unanswered question without its answer."""

    session = _get_session(session_id)
    cursor = session["cursor"]
    questions = session["questions"]

    if cursor >= len(questions):
        return None

    question = questions[cursor]
    return _public_question(question, question_number=cursor + 1, total=len(questions))


def submit_answer(
    session_id: str,
    question_id: str,
    answer: str,
    self_eval: bool | None = None,
) -> dict[str, Any]:
    """Score one answer, update scheduling fields, and persist bank changes."""

    session = _get_session(session_id)
    cursor = session["cursor"]
    questions = session["questions"]

    if cursor >= len(questions):
        raise ValueError("Session is already complete")

    question = questions[cursor]
    if question["id"] != question_id:
        raise ValueError("question_id does not match the next pending question")

    correct = _question_is_correct(question, answer, self_eval)
    updated_question = _apply_review_update(question, correct, session["today"])

    session["questions"][cursor] = updated_question
    session["results"][question_id] = {
        "correct": correct,
        "concept_id": updated_question["concept_id"],
        "next_review": updated_question["next_review"],
    }
    session["cursor"] += 1

    payload_kind, bank_entries = _load_bank_entries(session["bank_path"])
    for index, entry in enumerate(bank_entries):
        if entry.get("id") == question_id:
            bank_entries[index] = deepcopy(updated_question)
            break
    else:
        raise ValueError(f"Question not found in bank: {question_id}")

    _write_bank_entries(session["bank_path"], payload_kind, bank_entries)

    return {
        "correct": correct,
        "correct_answer": str(question["answer"]),
        "explanation": question["explanation"],
        "new_interval_days": updated_question["interval_days"],
        "new_ease_factor": updated_question["ease_factor"],
        "next_review": updated_question["next_review"],
    }


def get_session_summary(session_id: str) -> dict[str, Any]:
    """Return aggregate session stats."""

    session = _get_session(session_id)
    results = list(session["results"].items())
    total = len(session["questions"])
    correct = sum(1 for _, result in results if result["correct"])
    incorrect = len(results) - correct
    concepts_reviewed = list(dict.fromkeys(question["concept_id"] for question in session["questions"]))

    return {
        "total": total,
        "correct": correct,
        "incorrect": incorrect,
        "accuracy": (correct / total) if total else 0.0,
        "concepts_reviewed": concepts_reviewed,
        "next_reviews": [
            {"question_id": question_id, "next_review": result["next_review"]}
            for question_id, result in results
        ],
    }
