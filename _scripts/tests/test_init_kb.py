from __future__ import annotations

import json
from pathlib import Path
import stat
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _scripts.metadata_validator import (
    validate_concept_frontmatter,
    validate_quiz_entry,
    validate_source_meta,
)


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "init-kb.sh"


def run_init(target_root: Path) -> None:
    subprocess.run(["bash", str(SCRIPT_PATH), str(target_root)], check=True)


def test_init_kb_bootstraps_structure_and_example_content(tmp_path: Path) -> None:
    run_init(tmp_path)

    expected_directories = [
        "_inbox",
        "_drafts",
        "concepts",
        "concepts/examples",
        "sources",
        "sources/repos",
        "sources/videos",
        "sources/books",
        "sources/articles",
        "sources/articles/example-article",
        "sources/podcasts",
        "sources/papers",
        "quiz",
        "_index",
        "topics",
        "_scripts",
        "_scripts/prompts",
    ]

    for relative_path in expected_directories:
        assert (tmp_path / relative_path).is_dir(), relative_path

    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert "## Usage" in readme
    assert "_drafts/" in readme
    assert "quiz/bank.json" in readme

    meta_path = tmp_path / "sources" / "articles" / "example-article" / "meta.yaml"
    concept_path = tmp_path / "concepts" / "examples" / "active-recall.md"
    bank_path = tmp_path / "quiz" / "bank.json"

    assert validate_source_meta(meta_path) == []
    assert validate_concept_frontmatter(concept_path) == []

    bank_payload = json.loads(bank_path.read_text(encoding="utf-8"))
    assert "questions" in bank_payload
    assert len(bank_payload["questions"]) >= 1
    assert validate_quiz_entry(bank_payload["questions"][0]) == []

    concepts_index = (tmp_path / "_index" / "concepts.md").read_text(encoding="utf-8")
    topics_index = (tmp_path / "_index" / "topics.md").read_text(encoding="utf-8")
    tags_index = (tmp_path / "_index" / "tags.md").read_text(encoding="utf-8")
    new_source_prompt = (tmp_path / "_scripts" / "prompts" / "new-source.md").read_text(encoding="utf-8")

    assert "Knowledge base initialized." in concepts_index
    assert "Knowledge base initialized." in topics_index
    assert "Knowledge base initialized." in tags_index
    assert "sources/<type>/<slug>/" in new_source_prompt
    assert "絕對不能建立、修改、刪除 `concepts/`" in new_source_prompt
    assert "merge_candidate" in new_source_prompt

    gitignore = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    for pattern in ("*.mp3", "*.mp4", "*.pdf", "*.epub", "sources/repos/**/repo/"):
        assert pattern in gitignore


def test_init_kb_is_idempotent_and_preserves_existing_files(tmp_path: Path) -> None:
    readme_path = tmp_path / "README.md"
    readme_path.write_text("custom readme\n", encoding="utf-8")

    gitignore_path = tmp_path / ".gitignore"
    gitignore_path.write_text("custom-ignore\n", encoding="utf-8")

    run_init(tmp_path)
    first_snapshot = {
        "readme": readme_path.read_text(encoding="utf-8"),
        "gitignore": gitignore_path.read_text(encoding="utf-8"),
        "concept_mode": stat.S_IMODE((tmp_path / "concepts" / "examples" / "active-recall.md").stat().st_mode),
    }

    run_init(tmp_path)

    assert readme_path.read_text(encoding="utf-8") == first_snapshot["readme"]
    assert gitignore_path.read_text(encoding="utf-8") == first_snapshot["gitignore"]
    assert stat.S_IMODE((tmp_path / "concepts" / "examples" / "active-recall.md").stat().st_mode) == first_snapshot[
        "concept_mode"
    ]
