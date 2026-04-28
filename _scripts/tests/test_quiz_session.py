from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import sys
import tempfile

from hypothesis import given
from hypothesis import strategies as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _scripts.quiz_session import (
    SESSION_STORE,
    _SESSIONS,
    get_next_question,
    get_session_summary,
    start_session,
    submit_answer,
)


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


def _write_concept(path: Path, concept_id: str, title: str, summary: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        f"id: {concept_id}\n"
        f"title: {title}\n"
        "depth: 2\n"
        "review_due: 2026-04-28\n"
        "sources:\n"
        "  - sources/articles/example.md\n"
        "related_concepts:\n"
        "  - sibling-concept\n"
        "---\n\n"
        "## 摘要\n"
        f"{summary}\n\n"
        "## 內容\n"
        "details\n",
        encoding="utf-8",
    )


def _write_bank_list(path: Path, entries: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_bank_dict(path: Path, questions: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"questions": questions}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def draw_answer_text(question: dict, should_be_correct: bool) -> str:
    if should_be_correct:
        return question["answer"]
    return f"{question['answer']} (incorrect)"


@given(quiz_question_sets())
def test_quiz_session_property_updates_history_and_counts(question_set: tuple[list[dict], list[bool]]) -> None:
    _SESSIONS.clear()
    questions, outcomes = question_set

    with tempfile.TemporaryDirectory() as temp_dir:
        bank_path = Path(temp_dir) / "bank.json"
        _write_bank_dict(bank_path, questions)

        session_payload = start_session(
            bank_path=str(bank_path),
            kb_root=temp_dir,
            count=len(questions),
            today=REVIEW_DATE.isoformat(),
        )
        session_id = session_payload["session_id"]

        original_history_lengths = {question["id"]: len(question["history"]) for question in questions}

        for question, should_be_correct in zip(questions, outcomes):
            answer = question["answer"] if should_be_correct else "__wrong__"
            self_eval = None
            if question["type"] != "multiple_choice":
                self_eval = should_be_correct
                answer = draw_answer_text(question, should_be_correct)

            result = submit_answer(session_id, question["id"], answer, self_eval=self_eval)
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


def test_quiz_session_runs_end_to_end_and_updates_bank(tmp_path: Path) -> None:
    SESSION_STORE.clear()
    kb_root = tmp_path
    _write_concept(kb_root / "concepts" / "cap-theorem.md", "cap-theorem", "CAP Theorem", "CAP summary.")
    _write_concept(
        kb_root / "concepts" / "consistency-patterns.md",
        "consistency-patterns",
        "Consistency Patterns",
        "Consistency summary.",
    )

    bank_path = kb_root / "quiz" / "bank.json"
    _write_bank_list(
        bank_path,
        [
            {
                "id": "q1",
                "concept_id": "cap-theorem",
                "type": "multiple_choice",
                "difficulty": 2,
                "question": "Which letter stands for partition tolerance?",
                "options": ["Consistency", "Availability", "Partition tolerance"],
                "answer": "C",
                "explanation": "P stands for partition tolerance.",
                "created_at": "2026-04-01",
                "next_review": "2026-04-20",
                "interval_days": 3,
                "ease_factor": 2.5,
                "history": [],
            },
            {
                "id": "q2",
                "concept_id": "consistency-patterns",
                "type": "short_answer",
                "difficulty": 3,
                "question": "Describe eventual consistency.",
                "answer": "Replicas converge over time.",
                "explanation": "Eventual consistency tolerates temporary divergence.",
                "created_at": "2026-04-05",
                "next_review": "2026-04-21",
                "interval_days": 2,
                "ease_factor": 2.2,
                "history": [],
            },
        ],
    )

    session = start_session(str(bank_path), str(kb_root), count=2, today="2026-04-28")

    assert session["total_questions"] == 2
    assert [item["concept_id"] for item in session["review_materials"]] == [
        "cap-theorem",
        "consistency-patterns",
    ]
    assert session["review_materials"][0]["summary"] == "CAP summary."

    question_1 = get_next_question(session["session_id"])
    assert question_1 is not None
    assert question_1["id"] == "q1"
    assert "answer" not in question_1

    result_1 = submit_answer(session["session_id"], "q1", "C")
    assert result_1["correct"] is True
    assert result_1["next_review"] == "2026-05-06"

    question_2 = get_next_question(session["session_id"])
    assert question_2 is not None
    assert question_2["id"] == "q2"

    result_2 = submit_answer(session["session_id"], "q2", "close enough", self_eval=False)
    assert result_2["correct"] is False
    assert result_2["next_review"] == "2026-04-29"

    assert get_next_question(session["session_id"]) is None

    summary = get_session_summary(session["session_id"])
    assert summary == {
        "total": 2,
        "correct": 1,
        "incorrect": 1,
        "accuracy": 0.5,
        "concepts_reviewed": ["cap-theorem", "consistency-patterns"],
        "next_reviews": [
            {"question_id": "q1", "next_review": "2026-05-06"},
            {"question_id": "q2", "next_review": "2026-04-29"},
        ],
    }

    updated_bank = json.loads(bank_path.read_text(encoding="utf-8"))
    assert updated_bank[0]["history"][-1] == {"date": "2026-04-28", "result": "correct"}
    assert updated_bank[1]["history"][-1] == {"date": "2026-04-28", "result": "incorrect"}


def test_start_session_can_filter_to_one_concept(tmp_path: Path) -> None:
    SESSION_STORE.clear()
    _write_concept(tmp_path / "concepts" / "cap-theorem.md", "cap-theorem", "CAP Theorem", "CAP summary.")
    _write_bank_list(
        tmp_path / "quiz" / "bank.json",
        [
            {
                "id": "q1",
                "concept_id": "cap-theorem",
                "type": "application",
                "difficulty": 4,
                "question": "When does CAP matter?",
                "answer": "During partitions.",
                "explanation": "CAP is relevant when partitions occur.",
                "created_at": "2026-04-01",
                "next_review": "2026-04-20",
                "interval_days": 3,
                "ease_factor": 2.5,
                "history": [],
            },
            {
                "id": "q2",
                "concept_id": "other-concept",
                "type": "multiple_choice",
                "difficulty": 1,
                "question": "Other question",
                "options": ["A", "B"],
                "answer": "A",
                "explanation": "A",
                "created_at": "2026-04-01",
                "next_review": "2026-04-20",
                "interval_days": 1,
                "ease_factor": 2.5,
                "history": [],
            },
        ],
    )

    session = start_session(
        str(tmp_path / "quiz" / "bank.json"),
        str(tmp_path),
        count=10,
        concept_id="cap-theorem",
        today="2026-04-28",
    )

    assert session["total_questions"] == 1
    assert session["questions_preview"] == [
        {
            "id": "q1",
            "concept_id": "cap-theorem",
            "type": "application",
            "difficulty": 4,
        }
    ]


def test_start_session_filters_before_count_limit(tmp_path: Path) -> None:
    SESSION_STORE.clear()
    _write_concept(tmp_path / "concepts" / "cap-theorem.md", "cap-theorem", "CAP Theorem", "CAP summary.")
    _write_bank_list(
        tmp_path / "quiz" / "bank.json",
        [
            {
                "id": "q-other",
                "concept_id": "other-concept",
                "type": "multiple_choice",
                "difficulty": 1,
                "question": "Other question",
                "options": ["A", "B"],
                "answer": "A",
                "explanation": "A",
                "created_at": "2026-04-01",
                "next_review": "2026-04-01",
                "interval_days": 1,
                "ease_factor": 2.5,
                "history": [],
            },
            {
                "id": "q-cap",
                "concept_id": "cap-theorem",
                "type": "multiple_choice",
                "difficulty": 2,
                "question": "CAP question",
                "options": ["A", "B"],
                "answer": "A",
                "explanation": "A",
                "created_at": "2026-04-01",
                "next_review": "2026-04-02",
                "interval_days": 2,
                "ease_factor": 2.5,
                "history": [],
            },
        ],
    )

    session = start_session(
        str(tmp_path / "quiz" / "bank.json"),
        str(tmp_path),
        count=1,
        concept_id="cap-theorem",
        today="2026-04-28",
    )

    assert session["total_questions"] == 1
    assert session["questions_preview"][0]["id"] == "q-cap"
