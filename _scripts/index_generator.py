"""Generate Markdown indexes for concepts, topics, and tags."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml


def _load_frontmatter(markdown_path: Path) -> dict[str, Any]:
    content = markdown_path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        return {}

    parts = content.split("---\n", 2)
    if len(parts) < 3:
        return {}

    data = yaml.safe_load(parts[1]) or {}
    if not isinstance(data, dict):
        return {}

    return data


def _iter_markdown_files(root: Path) -> list[Path]:
    if not root.exists():
        return []

    return sorted(path for path in root.rglob("*.md") if path.is_file())


def _write_index(index_path: Path, lines: list[str]) -> None:
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _display_title(path: Path, frontmatter: dict[str, Any]) -> str:
    title = frontmatter.get("title")
    if title:
        return str(title)

    content = path.read_text(encoding="utf-8")
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()

    return path.stem.replace("-", " ").replace("_", " ").title()


def _concept_records(root: Path, status: str) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for path in _iter_markdown_files(root):
        frontmatter = _load_frontmatter(path)
        records.append(
            {
                "title": _display_title(path, frontmatter),
                "id": str(frontmatter.get("id", path.stem)),
                "status": status,
                "link": path.relative_to(root.parent).as_posix(),
            }
        )

    return sorted(records, key=lambda record: (record["title"].casefold(), record["id"].casefold()))


def generate_concepts_index(kb_root: str | Path) -> Path:
    """Generate `_index/concepts.md` from `concepts/` and `_drafts/`."""

    root = Path(kb_root)
    active_records = _concept_records(root / "concepts", "active")
    draft_records = _concept_records(root / "_drafts", "draft")

    lines = [
        "# Concepts Index",
        "",
        "| Title | ID | Status | Path |",
        "| --- | --- | --- | --- |",
    ]

    for record in active_records + draft_records:
        lines.append(
            f"| {record['title']} | `{record['id']}` | {record['status']} | "
            f"[{record['link']}](../{record['link']}) |"
        )

    if not active_records and not draft_records:
        lines.append("| _No concepts yet_ |  |  |  |")

    index_path = root / "_index" / "concepts.md"
    _write_index(index_path, lines)
    return index_path


def generate_topics_index(kb_root: str | Path) -> Path:
    """Generate `_index/topics.md` from `topics/`."""

    root = Path(kb_root)
    topic_paths = _iter_markdown_files(root / "topics")

    lines = [
        "# Topics Index",
        "",
    ]

    if not topic_paths:
        lines.append("- _No topics yet_")
    else:
        for path in topic_paths:
            frontmatter = _load_frontmatter(path)
            title = _display_title(path, frontmatter)
            link = path.relative_to(root).as_posix()
            lines.append(f"- [{title}](../{link})")

    index_path = root / "_index" / "topics.md"
    _write_index(index_path, lines)
    return index_path


def generate_tags_index(kb_root: str | Path) -> Path:
    """Generate `_index/tags.md` from concept frontmatter tags."""

    root = Path(kb_root)
    tag_map: dict[str, list[tuple[str, str]]] = defaultdict(list)

    for concept_root in (root / "concepts", root / "_drafts"):
        for path in _iter_markdown_files(concept_root):
            frontmatter = _load_frontmatter(path)
            tags = frontmatter.get("tags", [])
            if not isinstance(tags, list):
                continue

            title = _display_title(path, frontmatter)
            link = path.relative_to(root).as_posix()
            for tag in tags:
                if isinstance(tag, str) and tag:
                    tag_map[tag].append((title, link))

    lines = [
        "# Tags Index",
        "",
    ]

    if not tag_map:
        lines.append("- _No tags yet_")
    else:
        for tag in sorted(tag_map, key=str.casefold):
            lines.append(f"## {tag}")
            lines.append("")
            for title, link in sorted(tag_map[tag], key=lambda item: (item[0].casefold(), item[1])):
                lines.append(f"- [{title}](../{link})")
            lines.append("")

    index_path = root / "_index" / "tags.md"
    _write_index(index_path, lines)
    return index_path
