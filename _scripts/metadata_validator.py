"""Validation helpers for YAML metadata and quiz entries."""

from __future__ import annotations

from pathlib import Path

import yaml


SOURCE_REQUIRED_FIELDS = (
    "type",
    "title",
    "language",
    "date_consumed",
    "date_added",
    "status",
)

CONCEPT_REQUIRED_FIELDS = (
    "id",
    "title",
    "depth",
    "review_due",
    "sources",
)

QUIZ_REQUIRED_FIELDS = (
    "id",
    "concept_id",
    "type",
    "difficulty",
    "question",
    "answer",
    "explanation",
    "created_at",
    "next_review",
    "interval_days",
    "ease_factor",
    "history",
)


def _missing_field_errors(payload: dict, required_fields: tuple[str, ...]) -> list[str]:
    return [f"Missing required field: {field}" for field in required_fields if field not in payload]


def _load_yaml_file(path: str | Path) -> dict:
    content = Path(path).read_text(encoding="utf-8")
    data = yaml.safe_load(content) or {}
    if not isinstance(data, dict):
        raise ValueError("Expected YAML document to be a mapping")
    return data


def _load_frontmatter(path: str | Path) -> dict:
    content = Path(path).read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        return {}

    lines = content.splitlines()
    if not lines or lines[0] != "---":
        return {}

    try:
        closing_index = lines[1:].index("---") + 1
    except ValueError:
        return {}

    frontmatter_text = "\n".join(lines[1:closing_index])
    data = yaml.safe_load(frontmatter_text) or {}
    if not isinstance(data, dict):
        raise ValueError("Expected frontmatter to be a mapping")
    return data


def validate_source_meta(meta_path: str) -> list[str]:
    """Validate source meta.yaml required fields."""

    return _missing_field_errors(_load_yaml_file(meta_path), SOURCE_REQUIRED_FIELDS)


def validate_concept_frontmatter(concept_path: str) -> list[str]:
    """Validate concept frontmatter required fields."""

    return _missing_field_errors(_load_frontmatter(concept_path), CONCEPT_REQUIRED_FIELDS)


def validate_quiz_entry(entry: dict) -> list[str]:
    """Validate quiz entry required fields."""

    return _missing_field_errors(entry, QUIZ_REQUIRED_FIELDS)
