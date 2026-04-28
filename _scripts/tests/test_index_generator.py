from __future__ import annotations

from pathlib import Path
import sys
import tempfile

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _scripts.index_generator import (
    generate_concepts_index,
    generate_tags_index,
    generate_topics_index,
)


def _write_markdown(path: Path, frontmatter: dict | None = None, body: str = "# Title\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if frontmatter is None:
        path.write_text(body, encoding="utf-8")
        return

    content = f"---\n{yaml.safe_dump(frontmatter, sort_keys=False)}---\n\n{body}"
    path.write_text(content, encoding="utf-8")


def test_generate_concepts_index_includes_concepts_and_drafts() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        kb_root = Path(temp_dir)
        _write_markdown(
            kb_root / "concepts" / "distributed-systems" / "cap-theorem.md",
            {
                "id": "cap-theorem",
                "title": "CAP Theorem",
                "depth": 2,
                "review_due": "2026-05-01",
                "sources": ["sources/repos/system-design-primer"],
                "tags": ["distributed-systems"],
            },
        )
        _write_markdown(
            kb_root / "_drafts" / "raft-consensus.md",
            {
                "id": "raft-consensus",
                "title": "Raft Consensus",
                "depth": 1,
                "review_due": "2026-05-02",
                "sources": ["sources/books/ddia"],
                "tags": ["distributed-systems", "draft"],
            },
        )

        index_path = generate_concepts_index(kb_root)
        content = index_path.read_text(encoding="utf-8")

    assert index_path == kb_root / "_index" / "concepts.md"
    assert "| CAP Theorem | `cap-theorem` | active | [concepts/distributed-systems/cap-theorem.md](../concepts/distributed-systems/cap-theorem.md) |" in content
    assert "| Raft Consensus | `raft-consensus` | draft | [_drafts/raft-consensus.md](../_drafts/raft-consensus.md) |" in content


def test_generate_topics_index_lists_topic_files() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        kb_root = Path(temp_dir)
        _write_markdown(
            kb_root / "topics" / "system-design-interview.md",
            {"title": "System Design Interview"},
        )
        _write_markdown(kb_root / "topics" / "llm-fundamentals.md", None, "# LLM Fundamentals\n")

        index_path = generate_topics_index(kb_root)
        content = index_path.read_text(encoding="utf-8")

    assert index_path == kb_root / "_index" / "topics.md"
    assert "- [LLM Fundamentals](../topics/llm-fundamentals.md)" in content
    assert "- [System Design Interview](../topics/system-design-interview.md)" in content


def test_generate_tags_index_groups_concepts_by_tag() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        kb_root = Path(temp_dir)
        _write_markdown(
            kb_root / "concepts" / "distributed-systems" / "cap-theorem.md",
            {
                "id": "cap-theorem",
                "title": "CAP Theorem",
                "depth": 2,
                "review_due": "2026-05-01",
                "sources": ["sources/repos/system-design-primer"],
                "tags": ["distributed-systems", "fundamentals"],
            },
        )
        _write_markdown(
            kb_root / "_drafts" / "raft-consensus.md",
            {
                "id": "raft-consensus",
                "title": "Raft Consensus",
                "depth": 1,
                "review_due": "2026-05-02",
                "sources": ["sources/books/ddia"],
                "tags": ["distributed-systems"],
            },
        )

        index_path = generate_tags_index(kb_root)
        content = index_path.read_text(encoding="utf-8")

    assert index_path == kb_root / "_index" / "tags.md"
    assert "## distributed-systems" in content
    assert "- [CAP Theorem](../concepts/distributed-systems/cap-theorem.md)" in content
    assert "- [Raft Consensus](../_drafts/raft-consensus.md)" in content
    assert "## fundamentals" in content
