"""Simplified SM-2 scheduling helpers for quiz review updates."""

from __future__ import annotations

from copy import deepcopy
from datetime import date
from typing import Any


EASE_FACTOR_FLOOR = 1.3
INCORRECT_EASE_FACTOR_PENALTY = 0.2


def _review_date_value(review_date: date | None) -> str:
    return (review_date or date.today()).isoformat()


def _append_history(entry: dict[str, Any], result: str, review_date: date | None) -> None:
    history = list(entry.get("history", []))
    history.append({"date": _review_date_value(review_date), "result": result})
    entry["history"] = history


def update_on_correct(entry: dict[str, Any], review_date: date | None = None) -> dict[str, Any]:
    """Return an updated quiz entry after a correct answer."""

    updated_entry = deepcopy(entry)
    updated_entry["interval_days"] = updated_entry["interval_days"] * updated_entry["ease_factor"]
    updated_entry["ease_factor"] = max(EASE_FACTOR_FLOOR, updated_entry["ease_factor"])
    _append_history(updated_entry, "correct", review_date)
    return updated_entry


def update_on_incorrect(entry: dict[str, Any], review_date: date | None = None) -> dict[str, Any]:
    """Return an updated quiz entry after an incorrect answer."""

    updated_entry = deepcopy(entry)
    updated_entry["interval_days"] = 1
    updated_entry["ease_factor"] = max(
        EASE_FACTOR_FLOOR,
        updated_entry["ease_factor"] - INCORRECT_EASE_FACTOR_PENALTY,
    )
    _append_history(updated_entry, "incorrect", review_date)
    return updated_entry
