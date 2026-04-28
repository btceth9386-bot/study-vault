from __future__ import annotations

from datetime import date, timedelta
import json
from pathlib import Path
import sys
import tempfile

from hypothesis import given
from hypothesis import strategies as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _scripts import quiz_manager


DATE_STRATEGY = st.dates(min_value=date(2024, 1, 1), max_value=date(2035, 12, 31))


@st.composite
def quiz_banks(draw):
    today = draw(DATE_STRATEGY)
    entries = draw(
        st.lists(
            st.integers(min_value=-30, max_value=30),
            min_size=1,
            max_size=40,
            unique=True,
        )
    )
    count = draw(st.integers(min_value=1, max_value=20))

    questions = []
    for index, offset in enumerate(entries):
        next_review = (today + timedelta(days=offset)).isoformat()
        questions.append(
            {
                "id": f"q-{index:02d}",
                "concept_id": f"concept-{index:02d}",
                "type": "short_answer",
                "difficulty": (index % 5) + 1,
                "question": f"Question {index}",
                "answer": f"Answer {index}",
                "explanation": f"Explanation {index}",
                "created_at": today.isoformat(),
                "next_review": next_review,
                "interval_days": 1,
                "ease_factor": 2.5,
                "history": [],
            }
        )

    return today, questions, count


def _write_bank(path: Path, questions: list[dict]) -> None:
    path.write_text(
        json.dumps({"questions": questions}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _review_pack(questions: list[dict], today: date, count: int) -> list[dict]:
    with tempfile.TemporaryDirectory() as temp_dir:
        bank_path = Path(temp_dir) / "bank.json"
        _write_bank(bank_path, questions)
        return quiz_manager.get_review_pack(str(bank_path), count=count, today=today.isoformat())


@given(quiz_banks())
def test_get_review_pack_never_exceeds_requested_count(payload: tuple[date, list[dict], int]) -> None:
    today, questions, count = payload

    review_pack = _review_pack(questions, today, count)

    assert len(review_pack) <= count
    assert len(review_pack) <= len(questions)


@given(quiz_banks())
def test_get_review_pack_places_due_questions_before_future_questions(payload: tuple[date, list[dict], int]) -> None:
    today, questions, count = payload

    review_pack = _review_pack(questions, today, count)
    observed_is_due = [entry["next_review"] <= today.isoformat() for entry in review_pack]

    assert observed_is_due == sorted(observed_is_due, reverse=True)


@given(quiz_banks())
def test_get_review_pack_selects_earliest_due_questions_when_truncated(payload: tuple[date, list[dict], int]) -> None:
    today, questions, count = payload

    due_questions = [question for question in questions if question["next_review"] <= today.isoformat()]
    if len(due_questions) <= count:
        return

    review_pack = _review_pack(questions, today, count)
    expected_ids = [
        question["id"]
        for question in sorted(due_questions, key=lambda question: (question["next_review"], question["id"]))[:count]
    ]

    assert [question["id"] for question in review_pack] == expected_ids


def test_add_questions_appends_entries_to_existing_bank() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        bank_path = Path(temp_dir) / "bank.json"
        _write_bank(
            bank_path,
            [
                {
                    "id": "q-1",
                    "concept_id": "concept-1",
                    "type": "short_answer",
                    "difficulty": 1,
                    "question": "Question 1",
                    "answer": "Answer 1",
                    "explanation": "Explanation 1",
                    "created_at": "2026-04-28",
                    "next_review": "2026-04-28",
                    "interval_days": 1,
                    "ease_factor": 2.5,
                    "history": [],
                }
            ],
        )

        quiz_manager.add_questions(
            str(bank_path),
            [
                {
                    "id": "q-2",
                    "concept_id": "concept-2",
                    "type": "short_answer",
                    "difficulty": 2,
                    "question": "Question 2",
                    "answer": "Answer 2",
                    "explanation": "Explanation 2",
                    "created_at": "2026-04-28",
                    "next_review": "2026-04-29",
                    "interval_days": 1,
                    "ease_factor": 2.5,
                    "history": [],
                }
            ],
        )

        payload = json.loads(bank_path.read_text(encoding="utf-8"))

    assert [question["id"] for question in payload["questions"]] == ["q-1", "q-2"]
