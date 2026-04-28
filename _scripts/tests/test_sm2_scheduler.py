from __future__ import annotations

from datetime import date
from pathlib import Path
import sys

from hypothesis import given
from hypothesis import strategies as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _scripts.sm2_scheduler import (
    EASE_FACTOR_FLOOR,
    INCORRECT_EASE_FACTOR_PENALTY,
    update_on_correct,
    update_on_incorrect,
)


REVIEW_DATE = date(2026, 4, 28)
RESULT_STRATEGY = st.sampled_from(["correct", "incorrect"])


@st.composite
def quiz_entries(draw):
    return {
        "interval_days": draw(st.integers(min_value=1, max_value=3650)),
        "ease_factor": draw(
            st.floats(
                min_value=EASE_FACTOR_FLOOR,
                max_value=5.0,
                allow_nan=False,
                allow_infinity=False,
            )
        ),
        "history": draw(
            st.lists(
                st.fixed_dictionaries(
                    {
                        "date": st.dates().map(lambda value: value.isoformat()),
                        "result": RESULT_STRATEGY,
                    }
                ),
                max_size=20,
            )
        ),
    }


@given(quiz_entries())
def test_update_on_correct_multiplies_interval_and_appends_history(entry: dict) -> None:
    updated_entry = update_on_correct(entry, review_date=REVIEW_DATE)

    assert updated_entry["interval_days"] == entry["interval_days"] * entry["ease_factor"]
    assert updated_entry["ease_factor"] >= EASE_FACTOR_FLOOR
    assert len(updated_entry["history"]) == len(entry["history"]) + 1
    assert updated_entry["history"][-1] == {"date": REVIEW_DATE.isoformat(), "result": "correct"}


@given(quiz_entries())
def test_update_on_incorrect_resets_interval_and_enforces_ease_factor_floor(entry: dict) -> None:
    updated_entry = update_on_incorrect(entry, review_date=REVIEW_DATE)

    assert updated_entry["interval_days"] == 1
    assert updated_entry["ease_factor"] == max(
        EASE_FACTOR_FLOOR,
        entry["ease_factor"] - INCORRECT_EASE_FACTOR_PENALTY,
    )
    assert updated_entry["ease_factor"] >= EASE_FACTOR_FLOOR
    assert len(updated_entry["history"]) == len(entry["history"]) + 1
    assert updated_entry["history"][-1] == {"date": REVIEW_DATE.isoformat(), "result": "incorrect"}
