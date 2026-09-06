from pathlib import Path

from _scripts.pipeline import reviewed_drafts


def _draft(path: Path, source: str, review_status: str | None) -> None:
    status_line = f"review_status: {review_status}\n" if review_status else ""
    path.write_text(
        "---\n"
        f"id: {path.stem}\n"
        f"title: {path.stem}\n"
        f"source: {source}\n"
        "status: draft\n"
        f"{status_line}"
        "---\n",
        encoding="utf-8",
    )


def test_reviewed_drafts_scopes_source_and_keeps_unverified_out(tmp_path: Path) -> None:
    drafts = tmp_path / "_drafts"
    drafts.mkdir()
    source = "sources/repos/example"

    _draft(drafts / "verified.md", source, "verified")
    _draft(drafts / "pending.md", f"{source}/", None)
    _draft(drafts / "unknown.md", source, "maybe")
    _draft(drafts / "unrelated.md", "sources/repos/other", "verified")

    grouped = reviewed_drafts(tmp_path, str(tmp_path / source))

    assert grouped["verified"] == ["_drafts/verified.md"]
    assert grouped["pending"] == ["_drafts/pending.md"]
    assert grouped["needs-decision"] == ["_drafts/unknown.md"]
    assert grouped["rejected"] == []
