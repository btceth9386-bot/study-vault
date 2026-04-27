"""Validation helpers for YAML metadata and quiz entries."""

from __future__ import annotations

from pathlib import Path
from typing import Any

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


def _missing_field_errors(payload: dict[str, Any], required_fields: tuple[str, ...]) -> list[str]:
    return [f"Missing required field: {field}" for field in required_fields if field not in payload]


def _load_yaml_file(path: str | Path) -> tuple[dict[str, Any], list[str]]:
    try:
        content = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        return {}, [f"Unable to read file: {exc}"]

    try:
        data = yaml.safe_load(content) or {}
    except yaml.YAMLError as exc:
        return {}, [f"Invalid YAML: {exc}"]

    if not isinstance(data, dict):
        return {}, ["YAML content must be a mapping"]

    return data, []


def _load_frontmatter(path: str | Path) -> tuple[dict[str, Any], list[str]]:
    try:
        content = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        return {}, [f"Unable to read file: {exc}"]

    if not content.startswith("---\n"):
        return {}, ["Concept file is missing YAML frontmatter"]

    parts = content.split("---\n", 2)
    if len(parts) < 3:
        return {}, ["Concept file has incomplete YAML frontmatter"]

    frontmatter_text = parts[1]

    try:
        data = yaml.safe_load(frontmatter_text) or {}
    except yaml.YAMLError as exc:
        return {}, [f"Invalid YAML frontmatter: {exc}"]

    if not isinstance(data, dict):
        return {}, ["Concept frontmatter must be a mapping"]

    return data, []


def validate_source_meta(meta_path: str | Path) -> list[str]:
    """Validate source meta.yaml required fields."""

    data, errors = _load_yaml_file(meta_path)
    if errors:
        return errors

    return _missing_field_errors(data, SOURCE_REQUIRED_FIELDS)


def validate_concept_frontmatter(concept_path: str | Path) -> list[str]:
    """Validate concept frontmatter required fields."""

    data, errors = _load_frontmatter(concept_path)
    if errors:
        return errors

    return _missing_field_errors(data, CONCEPT_REQUIRED_FIELDS)


def validate_quiz_entry(entry: dict[str, Any]) -> list[str]:
    """Validate quiz entry required fields."""

    if not isinstance(entry, dict):
        return ["Quiz entry must be a mapping"]

    return _missing_field_errors(entry, QUIZ_REQUIRED_FIELDS)
