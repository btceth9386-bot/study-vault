from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import sys
import tempfile

from hypothesis import given
from hypothesis import strategies as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _scripts import sm2_scheduler


DATE_STRATEGY = st.dates(min_value=date(2024, 1, 1), max_value=date(2035, 12, 31))
INTERVAL_STRATEGY = st.floats(min_value=0.1, max_value=365.0, allow_nan=False, allow_infinity=False)
EASE_FACTOR_STRATEGY = st.floats(min_value=1.3, max_value=5.0, allow_nan=False, allow_infinity=False)


@st.composite
def quiz_questions(draw):
    review_date = draw(DATE_STRATEGY)
    return {
        "id": draw(st.text(min_size=1, max_size=30)),
        "concept_id": draw(st.text(min_size=1, max_size=30)),
        "type": "short_answer",
        "difficulty": draw(st.integers(min_value=1, max_value=5)),
        "question": draw(st.text(min_size=1, max_size=100)),
        "answer": draw(st.text(min_size=1, max_size=100)),
        "explanation": draw(st.text(min_size=1, max_size=100)),
        "created_at": review_date.isoformat(),
        "next_review": review_date.isoformat(),
        "interval_days": draw(INTERVAL_STRATEGY),
        "ease_factor": draw(EASE_FACTOR_STRATEGY),
        "history": [],
    }


def _write_bank(path: Path, questions: list[dict]) -> None:
    path.write_text(
        json.dumps({"questions": questions}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


@given(quiz_questions(), DATE_STRATEGY)
def test_update_on_correct_multiplies_interval_and_appends_history(question: dict, today: date) -> None:
    original_interval = question["interval_days"]
    original_ease = question["ease_factor"]

    updated = sm2_scheduler._apply_result(question, correct=True, review_date=today)

    assert updated["interval_days"] == original_interval * original_ease
    assert updated["ease_factor"] == original_ease
    assert updated["last_attempted"] == today.isoformat()
    assert updated["history"][-1] == {"date": today.isoformat(), "result": "correct"}


@given(quiz_questions(), DATE_STRATEGY)
def test_update_on_incorrect_resets_interval_and_floors_ease_factor(question: dict, today: date) -> None:
    updated = sm2_scheduler._apply_result(question, correct=False, review_date=today)

    assert updated["interval_days"] == 1
    assert updated["ease_factor"] == max(1.3, question["ease_factor"] - 0.2)
    assert updated["last_attempted"] == today.isoformat()
    assert updated["history"][-1] == {"date": today.isoformat(), "result": "incorrect"}


@given(
    DATE_STRATEGY,
    st.lists(
        st.integers(min_value=-5, max_value=5),
        min_size=1,
        max_size=20,
    ),
)
def test_get_due_questions_filters_by_next_review(today: date, offsets: list[int]) -> None:
    questions = []
    expected_ids = []

    for index, offset in enumerate(offsets):
        next_review = today.fromordinal(today.toordinal() + offset).isoformat()
        question = {
            "id": f"q-{index}",
            "concept_id": "concept",
            "type": "short_answer",
            "difficulty": 1,
            "question": "Question",
            "answer": "Answer",
            "explanation": "Explanation",
            "created_at": today.isoformat(),
            "next_review": next_review,
            "interval_days": 1,
            "ease_factor": 2.5,
            "history": [],
        }
        questions.append(question)
        if offset <= 0:
            expected_ids.append(question["id"])

    with tempfile.TemporaryDirectory() as temp_dir:
        bank_path = Path(temp_dir) / "bank.json"
        _write_bank(bank_path, questions)

        due_ids = [question["id"] for question in sm2_scheduler.get_due_questions(str(bank_path), today.isoformat())]

    assert due_ids == expected_ids


def test_update_bank_persists_schedule_changes_and_history() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        bank_path = Path(temp_dir) / "bank.json"
        _write_bank(
            bank_path,
            [
                {
                    "id": "q-1",
                    "concept_id": "concept",
                    "type": "short_answer",
                    "difficulty": 2,
                    "question": "Question",
                    "answer": "Answer",
                    "explanation": "Explanation",
                    "created_at": "2026-04-20",
                    "next_review": "2026-04-28",
                    "interval_days": 2,
                    "ease_factor": 2.5,
                    "history": [],
                }
            ],
        )

        original_today = sm2_scheduler._today
        sm2_scheduler._today = lambda: date(2026, 4, 28)
        try:
            sm2_scheduler.update_bank(str(bank_path), "q-1", correct=True)
        finally:
            sm2_scheduler._today = original_today

        payload = json.loads(bank_path.read_text(encoding="utf-8"))
        updated = payload["questions"][0]

    assert updated["interval_days"] == 5.0
    assert updated["ease_factor"] == 2.5
    assert updated["last_attempted"] == "2026-04-28"
    assert updated["next_review"] == "2026-05-03"
    assert updated["history"] == [{"date": "2026-04-28", "result": "correct"}]


def test_update_bank_raises_for_unknown_question_id() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        bank_path = Path(temp_dir) / "bank.json"
        _write_bank(bank_path, [])

        try:
            sm2_scheduler.update_bank(str(bank_path), "missing", correct=False)
        except ValueError as exc:
            assert str(exc) == "Question not found: missing"
        else:
            raise AssertionError("Expected ValueError for unknown question id")
