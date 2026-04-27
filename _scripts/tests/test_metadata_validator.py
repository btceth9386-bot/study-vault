from __future__ import annotations

from pathlib import Path
import sys
import tempfile

import yaml
from hypothesis import given
from hypothesis import strategies as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _scripts.metadata_validator import (
    CONCEPT_REQUIRED_FIELDS,
    QUIZ_REQUIRED_FIELDS,
    SOURCE_REQUIRED_FIELDS,
    validate_concept_frontmatter,
    validate_quiz_entry,
    validate_source_meta,
)


DATE_STRATEGY = st.dates().map(lambda value: value.isoformat())
TEXT_STRATEGY = st.text(
    alphabet=st.characters(
        blacklist_categories=("Cc", "Cs"),
        blacklist_characters="\x00",
    ),
    min_size=1,
    max_size=40,
)


@st.composite
def source_meta_payloads(draw):
    return {
        "type": draw(TEXT_STRATEGY),
        "title": draw(TEXT_STRATEGY),
        "language": draw(TEXT_STRATEGY),
        "date_consumed": draw(DATE_STRATEGY),
        "date_added": draw(DATE_STRATEGY),
        "status": draw(TEXT_STRATEGY),
    }


@st.composite
def concept_frontmatter_payloads(draw):
    return {
        "id": draw(TEXT_STRATEGY),
        "title": draw(TEXT_STRATEGY),
        "depth": draw(st.integers(min_value=1, max_value=4)),
        "review_due": draw(DATE_STRATEGY),
        "sources": draw(st.lists(TEXT_STRATEGY, min_size=1, max_size=5)),
    }


@st.composite
def quiz_entry_payloads(draw):
    return {
        "id": draw(TEXT_STRATEGY),
        "concept_id": draw(TEXT_STRATEGY),
        "type": draw(TEXT_STRATEGY),
        "difficulty": draw(st.integers(min_value=1, max_value=5)),
        "question": draw(TEXT_STRATEGY),
        "answer": draw(TEXT_STRATEGY),
        "explanation": draw(TEXT_STRATEGY),
        "created_at": draw(DATE_STRATEGY),
        "next_review": draw(DATE_STRATEGY),
        "interval_days": draw(st.integers(min_value=1, max_value=3650)),
        "ease_factor": draw(st.floats(min_value=1.3, max_value=5.0, allow_nan=False, allow_infinity=False)),
        "history": draw(
            st.lists(
                st.fixed_dictionaries(
                    {
                        "date": DATE_STRATEGY,
                        "result": st.sampled_from(["correct", "incorrect"]),
                    }
                ),
                max_size=5,
            )
        ),
    }


def _write_yaml(path: Path, payload: dict) -> None:
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def _write_concept(path: Path, frontmatter: dict) -> None:
    content = f"---\n{yaml.safe_dump(frontmatter, sort_keys=False)}---\n\n# Concept\n"
    path.write_text(content, encoding="utf-8")


@given(source_meta_payloads())
def test_validate_source_meta_accepts_complete_payloads(payload: dict) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        meta_path = Path(temp_dir) / "meta.yaml"
        _write_yaml(meta_path, payload)

        assert validate_source_meta(str(meta_path)) == []


@given(source_meta_payloads(), st.sampled_from(SOURCE_REQUIRED_FIELDS))
def test_validate_source_meta_reports_missing_fields(payload: dict, missing_field: str) -> None:
    payload.pop(missing_field)
    with tempfile.TemporaryDirectory() as temp_dir:
        meta_path = Path(temp_dir) / "meta.yaml"
        _write_yaml(meta_path, payload)

        errors = validate_source_meta(str(meta_path))

        assert any(missing_field in error for error in errors)


@given(concept_frontmatter_payloads())
def test_validate_concept_frontmatter_accepts_complete_payloads(payload: dict) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        concept_path = Path(temp_dir) / "concept.md"
        _write_concept(concept_path, payload)

        assert validate_concept_frontmatter(str(concept_path)) == []


@given(concept_frontmatter_payloads(), st.sampled_from(CONCEPT_REQUIRED_FIELDS))
def test_validate_concept_frontmatter_reports_missing_fields(payload: dict, missing_field: str) -> None:
    payload.pop(missing_field)
    with tempfile.TemporaryDirectory() as temp_dir:
        concept_path = Path(temp_dir) / "concept.md"
        _write_concept(concept_path, payload)

        errors = validate_concept_frontmatter(str(concept_path))

        assert any(missing_field in error for error in errors)


@given(quiz_entry_payloads())
def test_validate_quiz_entry_accepts_complete_payloads(payload: dict) -> None:
    assert validate_quiz_entry(payload) == []


@given(quiz_entry_payloads(), st.sampled_from(QUIZ_REQUIRED_FIELDS))
def test_validate_quiz_entry_reports_missing_fields(payload: dict, missing_field: str) -> None:
    payload.pop(missing_field)

    errors = validate_quiz_entry(payload)

    assert any(missing_field in error for error in errors)
