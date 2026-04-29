from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _scripts.metadata_validator import (
    validate_concept_frontmatter,
    validate_quiz_entry,
    validate_source_meta,
)
from _scripts.quiz_session import (
    SESSION_STORE,
    get_next_question,
    get_session_summary,
    start_session,
    submit_answer,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
INIT_SCRIPT = REPO_ROOT / "_scripts" / "init-kb.sh"
INGEST_PDF_SCRIPT = REPO_ROOT / "_scripts" / "ingest-pdf.sh"


def _run_init(kb_root: Path) -> None:
    subprocess.run(["bash", str(INIT_SCRIPT), str(kb_root)], check=True)


def _install_temp_scripts(kb_root: Path) -> None:
    scripts_dir = kb_root / "_scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    (scripts_dir / "ingest-pdf.sh").symlink_to(INGEST_PDF_SCRIPT)
    (scripts_dir / "file_splitter.py").symlink_to(REPO_ROOT / "_scripts" / "file_splitter.py")


def _install_mock_pdftotext(mock_bin: Path) -> None:
    mock_bin.mkdir(parents=True, exist_ok=True)
    pdftotext = mock_bin / "pdftotext"
    pdftotext.write_text(
        "#!/usr/bin/env bash\n"
        "cat > \"$2\" <<'EOF'\n"
        "# Retrieval Practice Paper\n\n"
        "Retrieval practice improves retention by asking learners to answer from memory.\n"
        "EOF\n",
        encoding="utf-8",
    )
    pdftotext.chmod(0o755)


def _write_promoted_concept(kb_root: Path) -> Path:
    concept_path = kb_root / "concepts" / "learning" / "retrieval-practice.md"
    concept_path.parent.mkdir(parents=True, exist_ok=True)
    concept_path.write_text(
        "---\n"
        "id: retrieval-practice\n"
        "title: Retrieval Practice\n"
        "depth: 2\n"
        "review_due: 2026-05-01\n"
        "sources:\n"
        "  - sources/papers/retrieval-practice-paper\n"
        "related:\n"
        "  - active-recall\n"
        "tags:\n"
        "  - learning\n"
        "  - memory\n"
        "---\n\n"
        "# Retrieval Practice\n\n"
        "## 摘要\n\n"
        "Retrieval practice strengthens memory by requiring answers before reviewing notes.\n\n"
        "## Example\n\n"
        "Read a section, close the source, answer a concrete question, then compare.\n",
        encoding="utf-8",
    )
    return concept_path


def _write_quiz_bank(kb_root: Path) -> Path:
    bank_path = kb_root / "quiz" / "bank.json"
    payload = {
        "questions": [
            {
                "id": "q-retrieval-practice-001",
                "concept_id": "retrieval-practice",
                "type": "multiple_choice",
                "difficulty": 2,
                "question": "What does retrieval practice require before reviewing notes?",
                "options": ["Highlighting", "Answering from memory", "Rereading", "Summarizing only"],
                "answer": "B",
                "explanation": "The key behavior is attempting recall before checking the material.",
                "created_at": "2026-04-28",
                "next_review": "2026-04-28",
                "interval_days": 2,
                "ease_factor": 2.5,
                "history": [],
            },
            {
                "id": "q-retrieval-practice-002",
                "concept_id": "retrieval-practice",
                "type": "short_answer",
                "difficulty": 3,
                "question": "Why is rereading weaker than retrieval practice?",
                "answer": "Rereading can feel familiar without proving recall.",
                "explanation": "Retrieval exposes memory gaps that passive review can hide.",
                "created_at": "2026-04-28",
                "next_review": "2026-04-28",
                "interval_days": 4,
                "ease_factor": 1.4,
                "history": [],
            },
        ]
    }
    bank_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return bank_path


def test_init_ingest_quiz_flow_updates_valid_kb_state(tmp_path: Path, monkeypatch) -> None:
    SESSION_STORE.clear()
    kb_root = tmp_path / "kb"
    _run_init(kb_root)
    _install_temp_scripts(kb_root)

    expected_directories = [
        "_inbox",
        "_drafts",
        "concepts",
        "sources",
        "sources/papers",
        "quiz",
        "_index",
        "topics",
        "_scripts",
        "_scripts/prompts",
    ]
    for relative_path in expected_directories:
        assert (kb_root / relative_path).is_dir(), relative_path

    mock_bin = tmp_path / "bin"
    _install_mock_pdftotext(mock_bin)
    monkeypatch.setenv("PATH", f"{mock_bin}{os.pathsep}{os.environ['PATH']}")

    pdf_path = kb_root / "_inbox" / "retrieval-practice-paper.pdf"
    pdf_path.write_text("%PDF-1.4 test fixture\n", encoding="utf-8")

    subprocess.run(
        ["bash", str(kb_root / "_scripts" / "ingest-pdf.sh"), str(pdf_path), "papers"],
        cwd=kb_root,
        check=True,
    )

    source_dir = kb_root / "sources" / "papers" / "retrieval-practice-paper"
    assert (source_dir / "notes.md").read_text(encoding="utf-8").startswith("# Retrieval Practice Paper")
    assert validate_source_meta(source_dir / "meta.yaml") == []

    concept_path = _write_promoted_concept(kb_root)
    bank_path = _write_quiz_bank(kb_root)

    assert validate_concept_frontmatter(concept_path) == []
    bank_payload = json.loads(bank_path.read_text(encoding="utf-8"))
    assert [validate_quiz_entry(question) for question in bank_payload["questions"]] == [[], []]

    session = start_session(
        bank_path=str(bank_path),
        kb_root=str(kb_root),
        count=2,
        concept_id="retrieval-practice",
        today="2026-04-29",
    )

    assert session["total_questions"] == 2
    assert session["review_materials"] == [
        {
            "concept_id": "retrieval-practice",
            "title": "Retrieval Practice",
            "summary": "Retrieval practice strengthens memory by requiring answers before reviewing notes.",
            "related_concepts": ["active-recall"],
            "source_refs": ["sources/papers/retrieval-practice-paper"],
        }
    ]

    first_question = get_next_question(session["session_id"])
    assert first_question is not None
    assert first_question["id"] == "q-retrieval-practice-001"
    assert "answer" not in first_question

    correct_result = submit_answer(session["session_id"], first_question["id"], "B")
    assert correct_result["correct"] is True
    assert correct_result["new_interval_days"] == 5
    assert correct_result["new_ease_factor"] == 2.5
    assert correct_result["next_review"] == "2026-05-04"

    second_question = get_next_question(session["session_id"])
    assert second_question is not None
    assert second_question["id"] == "q-retrieval-practice-002"

    incorrect_result = submit_answer(
        session["session_id"],
        second_question["id"],
        "It is always slower.",
        self_eval=False,
    )
    assert incorrect_result["correct"] is False
    assert incorrect_result["new_interval_days"] == 1
    assert incorrect_result["new_ease_factor"] == 1.3
    assert incorrect_result["next_review"] == "2026-04-30"

    assert get_next_question(session["session_id"]) is None
    assert get_session_summary(session["session_id"]) == {
        "total": 2,
        "correct": 1,
        "incorrect": 1,
        "accuracy": 0.5,
        "concepts_reviewed": ["retrieval-practice"],
        "next_reviews": [
            {"question_id": "q-retrieval-practice-001", "next_review": "2026-05-04"},
            {"question_id": "q-retrieval-practice-002", "next_review": "2026-04-30"},
        ],
    }

    updated_bank = json.loads(bank_path.read_text(encoding="utf-8"))
    updated_questions = {question["id"]: question for question in updated_bank["questions"]}
    assert updated_questions["q-retrieval-practice-001"]["history"] == [
        {"date": "2026-04-29", "result": "correct"}
    ]
    assert updated_questions["q-retrieval-practice-001"]["interval_days"] == 5
    assert updated_questions["q-retrieval-practice-001"]["next_review"] == "2026-05-04"
    assert updated_questions["q-retrieval-practice-002"]["history"] == [
        {"date": "2026-04-29", "result": "incorrect"}
    ]
    assert updated_questions["q-retrieval-practice-002"]["interval_days"] == 1
    assert updated_questions["q-retrieval-practice-002"]["ease_factor"] == 1.3
    assert updated_questions["q-retrieval-practice-002"]["next_review"] == "2026-04-30"
