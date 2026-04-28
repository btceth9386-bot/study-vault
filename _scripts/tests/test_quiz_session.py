from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import sys
import tempfile

from hypothesis import given
from hypothesis import strategies as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _scripts.quiz_session import _SESSIONS, get_session_summary, start_session, submit_answer


REVIEW_DATE = date(2026, 4, 28)
QUESTION_TYPE_STRATEGY = st.sampled_from(["multiple_choice", "short_answer", "application"])
CHOICE_STRATEGY = st.sampled_from(["A", "B", "C", "D"])
TEXT_STRATEGY = st.text(
    alphabet=st.characters(
        blacklist_categories=("Cc", "Cs"),
        blacklist_characters="\x00",
    ),
    min_size=1,
    max_size=40,
)


@st.composite
def quiz_question_sets(draw):
    count = draw(st.integers(min_value=1, max_value=10))
    questions = []
    outcomes = []

    for index in range(count):
        question_type = draw(QUESTION_TYPE_STRATEGY)
        correct = draw(st.booleans())
        concept_id = draw(TEXT_STRATEGY)
        question = {
            "id": f"q-{index}",
            "concept_id": concept_id,
            "type": question_type,
            "difficulty": draw(st.integers(min_value=1, max_value=5)),
            "question": draw(TEXT_STRATEGY),
            "answer": draw(CHOICE_STRATEGY if question_type == "multiple_choice" else TEXT_STRATEGY),
            "explanation": draw(TEXT_STRATEGY),
            "created_at": REVIEW_DATE.isoformat(),
            "next_review": REVIEW_DATE.isoformat(),
            "interval_days": draw(st.integers(min_value=1, max_value=3650)),
            "ease_factor": draw(
                st.floats(
                    min_value=1.3,
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
                            "result": st.sampled_from(["correct", "incorrect"]),
                        }
                    ),
                    max_size=10,
                )
            ),
        }
        if question_type == "multiple_choice":
            question["options"] = ["A", "B", "C", "D"]

        questions.append(question)
        outcomes.append(correct)

    return questions, outcomes


def _write_bank(path: Path, questions: list[dict]) -> None:
    payload = {"questions": questions}
    path.write_text(json.dumps(payload), encoding="utf-8")


@given(quiz_question_sets())
def test_quiz_session_property_updates_history_and_counts(question_set: tuple[list[dict], list[bool]]) -> None:
    questions, outcomes = question_set

    with tempfile.TemporaryDirectory() as temp_dir:
        bank_path = Path(temp_dir) / "bank.json"
        _write_bank(bank_path, questions)

        session_payload = start_session(
            bank_path=str(bank_path),
            kb_root=temp_dir,
            count=len(questions),
            today=REVIEW_DATE.isoformat(),
        )
        session_id = session_payload["session_id"]

        original_history_lengths = {
            question["id"]: len(question["history"])
            for question in questions
        }

        for question, should_be_correct in zip(questions, outcomes):
            answer = question["answer"] if should_be_correct else "__wrong__"
            self_eval = None
            if question["type"] != "multiple_choice":
                self_eval = should_be_correct
                answer = draw_answer_text(question, should_be_correct)

            result = submit_answer(
                session_id,
                question["id"],
                answer,
                self_eval=self_eval,
            )
            updated_question = next(
                item for item in _SESSIONS[session_id]["questions"] if item["id"] == question["id"]
            )

            expected_result = "correct" if result["correct"] else "incorrect"
            assert len(updated_question["history"]) == original_history_lengths[question["id"]] + 1
            assert updated_question["history"][-1] == {
                "date": REVIEW_DATE.isoformat(),
                "result": expected_result,
            }

        summary = get_session_summary(session_id)

        assert summary["correct"] + summary["incorrect"] == summary["total"]


def draw_answer_text(question: dict, should_be_correct: bool) -> str:
    if should_be_correct:
        return question["answer"]
    return f"{question['answer']} (incorrect)"
