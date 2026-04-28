"""Quiz bank helpers for loading, updating, and selecting review questions."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from _scripts.metadata_validator import validate_quiz_entry


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
        normalized.append(entry)

    return payload_kind, normalized


def _load_bank(bank_path: str | Path) -> tuple[str, list[dict[str, Any]]]:
    path = Path(bank_path)
    if not path.exists():
        return "list", []

    data = json.loads(path.read_text(encoding="utf-8"))
    return _normalize_bank_payload(data)


def _write_bank(bank_path: str | Path, payload_kind: str, entries: list[dict[str, Any]]) -> None:
    path = Path(bank_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: list[dict[str, Any]] | dict[str, list[dict[str, Any]]]
    if payload_kind == "dict":
        payload = {"questions": entries}
    else:
        payload = entries
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def add_questions(bank_path: str | Path, questions: list[dict[str, Any]]) -> None:
    """Append validated questions to bank.json."""

    payload_kind, existing = _load_bank(bank_path)

    for question in questions:
        errors = validate_quiz_entry(question)
        if errors:
            raise ValueError("; ".join(errors))

    existing.extend(questions)
    _write_bank(bank_path, payload_kind, existing)


def get_review_pack(
    bank_path: str | Path,
    count: int = 10,
    today: str | None = None,
) -> list[dict[str, Any]]:
    """Return up to count review questions, prioritizing due entries."""

    if count <= 0:
        return []

    _, entries = _load_bank(bank_path)
    today_value = _today_value(today)

    due_entries = [entry for entry in entries if entry.get("next_review", "") <= today_value]
    future_entries = [entry for entry in entries if entry.get("next_review", "") > today_value]

    due_entries.sort(key=lambda entry: (entry.get("next_review", ""), entry.get("id", "")))
    future_entries.sort(key=lambda entry: (entry.get("next_review", ""), entry.get("id", "")))

    return due_entries[:count] + future_entries[: max(0, count - len(due_entries))]
