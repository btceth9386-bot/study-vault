from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _scripts import quiz_cli


def test_parse_args_supports_issue_flags(monkeypatch) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "quiz_cli.py",
            "--count",
            "5",
            "--concept",
            "cap-theorem",
            "--bank",
            "custom-bank.json",
        ],
    )

    args = quiz_cli.parse_args()

    assert args.count == 5
    assert args.concept == "cap-theorem"
    assert args.bank == "custom-bank.json"


def test_main_drives_interactive_flow_via_quiz_session(monkeypatch, capsys) -> None:
    calls: list[tuple] = []

    def fake_start_session(bank_path: str, kb_root: str, count: int, concept_id: str | None) -> dict:
        calls.append(("start_session", bank_path, kb_root, count, concept_id))
        return {
            "session_id": "session-1",
            "review_materials": [
                {
                    "concept_id": "cap-theorem",
                    "title": "CAP Theorem",
                    "summary": "CAP summary.",
                }
            ],
            "total_questions": 2,
            "questions_preview": [],
        }

    questions = iter(
        [
            {
                "question_number": 1,
                "total": 2,
                "id": "q1",
                "concept_id": "cap-theorem",
                "type": "multiple_choice",
                "difficulty": 2,
                "question": "Which letter means partition tolerance?",
                "options": ["Consistency", "Availability", "Partition tolerance"],
            },
            {
                "question_number": 2,
                "total": 2,
                "id": "q2",
                "concept_id": "cap-theorem",
                "type": "short_answer",
                "difficulty": 3,
                "question": "Explain eventual consistency.",
                "options": None,
            },
            None,
        ]
    )

    def fake_get_next_question(session_id: str):
        calls.append(("get_next_question", session_id))
        return next(questions)

    def fake_submit_answer(session_id: str, question_id: str, answer: str, self_eval: bool | None = None) -> dict:
        calls.append(("submit_answer", session_id, question_id, answer, self_eval))
        return {
            "correct": question_id == "q1",
            "correct_answer": "C" if question_id == "q1" else "Replicas converge.",
            "explanation": f"Explanation for {question_id}",
            "new_interval_days": 4 if question_id == "q1" else 1,
            "new_ease_factor": 2.5 if question_id == "q1" else 2.0,
            "next_review": "2026-05-02" if question_id == "q1" else "2026-04-29",
        }

    def fake_get_session_summary(session_id: str) -> dict:
        calls.append(("get_session_summary", session_id))
        return {
            "total": 2,
            "correct": 1,
            "incorrect": 1,
            "accuracy": 0.5,
            "concepts_reviewed": ["cap-theorem"],
            "next_reviews": [
                {"question_id": "q1", "next_review": "2026-05-02"},
                {"question_id": "q2", "next_review": "2026-04-29"},
            ],
        }

    inputs = iter(["", "C", "Replicas eventually converge.", "n"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
    monkeypatch.setattr(quiz_cli.quiz_session, "start_session", fake_start_session)
    monkeypatch.setattr(quiz_cli.quiz_session, "get_next_question", fake_get_next_question)
    monkeypatch.setattr(quiz_cli.quiz_session, "submit_answer", fake_submit_answer)
    monkeypatch.setattr(quiz_cli.quiz_session, "get_session_summary", fake_get_session_summary)
    monkeypatch.setattr(sys, "argv", ["quiz_cli.py", "--count", "2", "--concept", "cap-theorem"])

    exit_code = quiz_cli.main()
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "本次考試涵蓋以下概念：" in output
    assert "CAP summary." in output
    assert "第 1/2 題 [multiple_choice]" in output
    assert "第 2/2 題 [short_answer]" in output
    assert "答對了" in output
    assert "答錯了" in output
    assert "本次統計" in output
    assert calls == [
        ("start_session", "quiz/bank.json", str(Path(quiz_cli.__file__).resolve().parents[1]), 2, "cap-theorem"),
        ("get_next_question", "session-1"),
        ("submit_answer", "session-1", "q1", "C", None),
        ("get_next_question", "session-1"),
        ("submit_answer", "session-1", "q2", "Replicas eventually converge.", False),
        ("get_next_question", "session-1"),
        ("get_session_summary", "session-1"),
    ]
