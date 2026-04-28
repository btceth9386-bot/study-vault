"""Tests for ingest-book.py."""

from __future__ import annotations

import importlib.util
import io
import tempfile
import zipfile
from pathlib import Path

import yaml

# ingest-book.py has a hyphen so it cannot be imported via normal import machinery.
_SCRIPT = Path(__file__).resolve().parents[1] / "ingest-book.py"
_spec = importlib.util.spec_from_file_location("ingest_book", _SCRIPT)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

_html_to_markdown = _mod._html_to_markdown
_slugify = _mod._slugify
ingest_book = _mod.ingest_book


# ---------------------------------------------------------------------------
# Helpers to build minimal epub fixtures
# ---------------------------------------------------------------------------

def _make_epub(
    title: str = "Test Book",
    authors: list[str] | None = None,
    language: str = "en",
    chapters: list[tuple[str, str]] | None = None,
) -> bytes:
    """Return raw bytes of a minimal valid epub (zip-based)."""
    if authors is None:
        authors = ["Author One"]
    if chapters is None:
        chapters = [("<h1>Chapter 1</h1><p>Hello world.</p>", "ch1")]

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("mimetype", "application/epub+zip")
        zf.writestr("META-INF/container.xml", (
            '<?xml version="1.0"?>'
            '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
            '<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>'
            "</rootfiles></container>"
        ))

        author_elements = "".join(f'<dc:creator>{a}</dc:creator>' for a in authors)
        spine_items = "".join(
            f'<item id="{cid}" href="{cid}.xhtml" media-type="application/xhtml+xml"/>'
            for _, cid in chapters
        )
        spine_refs = "".join(f'<itemref idref="{cid}"/>' for _, cid in chapters)

        opf = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="uid">'
            "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\">"
            f"<dc:identifier id=\"uid\">test-uid</dc:identifier>"
            f"<dc:title>{title}</dc:title>"
            f"{author_elements}"
            f"<dc:language>{language}</dc:language>"
            "</metadata>"
            f"<manifest>{spine_items}</manifest>"
            f"<spine>{spine_refs}</spine>"
            "</package>"
        )
        zf.writestr("OEBPS/content.opf", opf)

        for html, cid in chapters:
            xhtml = (
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" '
                '"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">'
                '<html xmlns="http://www.w3.org/1999/xhtml"><body>'
                f"{html}"
                "</body></html>"
            )
            zf.writestr(f"OEBPS/{cid}.xhtml", xhtml)

    return buf.getvalue()


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

def test_slugify_basic() -> None:
    assert _slugify("Hello World") == "hello-world"


def test_slugify_special_chars() -> None:
    assert _slugify("C++ Primer, 5th Ed.") == "c-primer-5th-ed"


def test_html_to_markdown_heading() -> None:
    result = _html_to_markdown("<h1>Title</h1><p>Body text.</p>")
    assert "# Title" in result
    assert "Body text." in result


def test_html_to_markdown_strips_script() -> None:
    result = _html_to_markdown("<script>alert(1)</script><p>Keep this.</p>")
    assert "alert" not in result
    assert "Keep this." in result


def test_ingest_book_creates_output_structure() -> None:
    epub_bytes = _make_epub(title="My Book", authors=["Alice"])
    with tempfile.TemporaryDirectory() as tmp:
        epub_path = Path(tmp) / "my-book.epub"
        epub_path.write_bytes(epub_bytes)

        out_dir = ingest_book(epub_path, kb_root=tmp)

        assert out_dir.is_dir()
        assert (out_dir / "meta.yaml").exists()
        chapter_files = list(out_dir.glob("chapter-*.md"))
        assert len(chapter_files) >= 1


def test_ingest_book_meta_yaml_fields() -> None:
    epub_bytes = _make_epub(title="Deep Learning", authors=["Goodfellow"], language="en")
    with tempfile.TemporaryDirectory() as tmp:
        epub_path = Path(tmp) / "dl.epub"
        epub_path.write_bytes(epub_bytes)

        out_dir = ingest_book(epub_path, kb_root=tmp)

        meta = yaml.safe_load((out_dir / "meta.yaml").read_text(encoding="utf-8"))
        assert meta["type"] == "book"
        assert meta["title"] == "Deep Learning"
        assert meta["authors"] == ["Goodfellow"]
        assert meta["language"] == "en"
        assert meta["status"] == "ingesting"
        for field in ("date_consumed", "date_added"):
            assert field in meta


def test_ingest_book_chapter_content() -> None:
    epub_bytes = _make_epub(chapters=[("<h1>Intro</h1><p>First paragraph.</p>", "ch1")])
    with tempfile.TemporaryDirectory() as tmp:
        epub_path = Path(tmp) / "book.epub"
        epub_path.write_bytes(epub_bytes)

        out_dir = ingest_book(epub_path, kb_root=tmp)

        chapter_text = (out_dir / "chapter-01.md").read_text(encoding="utf-8")
        assert "First paragraph." in chapter_text


def test_ingest_book_multiple_chapters() -> None:
    chapters = [
        ("<h1>Chapter 1</h1><p>Content one.</p>", "ch1"),
        ("<h1>Chapter 2</h1><p>Content two.</p>", "ch2"),
    ]
    epub_bytes = _make_epub(chapters=chapters)
    with tempfile.TemporaryDirectory() as tmp:
        epub_path = Path(tmp) / "book.epub"
        epub_path.write_bytes(epub_bytes)

        out_dir = ingest_book(epub_path, kb_root=tmp)

        assert (out_dir / "chapter-01.md").exists()
        assert (out_dir / "chapter-02.md").exists()


def test_ingest_book_adds_epub_to_gitignore_when_missing() -> None:
    epub_bytes = _make_epub()
    with tempfile.TemporaryDirectory() as tmp:
        epub_path = Path(tmp) / "book.epub"
        epub_path.write_bytes(epub_bytes)

        ingest_book(epub_path, kb_root=tmp)

        gitignore = (Path(tmp) / ".gitignore").read_text(encoding="utf-8")
        assert "*.epub" in gitignore


def test_ingest_book_appends_epub_to_existing_gitignore() -> None:
    epub_bytes = _make_epub()
    with tempfile.TemporaryDirectory() as tmp:
        gitignore = Path(tmp) / ".gitignore"
        gitignore.write_text("*.pyc\n", encoding="utf-8")

        epub_path = Path(tmp) / "book.epub"
        epub_path.write_bytes(epub_bytes)

        ingest_book(epub_path, kb_root=tmp)

        content = gitignore.read_text(encoding="utf-8")
        assert "*.pyc" in content
        assert "*.epub" in content


def test_ingest_book_does_not_duplicate_epub_in_gitignore() -> None:
    epub_bytes = _make_epub()
    with tempfile.TemporaryDirectory() as tmp:
        gitignore = Path(tmp) / ".gitignore"
        gitignore.write_text("*.epub\n", encoding="utf-8")

        epub_path = Path(tmp) / "book.epub"
        epub_path.write_bytes(epub_bytes)

        ingest_book(epub_path, kb_root=tmp)

        content = gitignore.read_text(encoding="utf-8")
        assert content.count("*.epub") == 1


def test_ingest_book_raises_for_missing_file() -> None:
    import pytest
    with tempfile.TemporaryDirectory() as tmp:
        with pytest.raises(FileNotFoundError):
            ingest_book(Path(tmp) / "nonexistent.epub", kb_root=tmp)


def test_ingest_book_large_chapter_splits() -> None:
    """A chapter exceeding 1 MB should be split into multiple part files."""
    big_paragraph = "word " * 50_000  # ~250 KB per paragraph, 5 paragraphs = ~1.25 MB
    html = "<p>" + "</p><p>".join([big_paragraph] * 5) + "</p>"
    epub_bytes = _make_epub(chapters=[(html, "bigch")])

    with tempfile.TemporaryDirectory() as tmp:
        epub_path = Path(tmp) / "big.epub"
        epub_path.write_bytes(epub_bytes)

        out_dir = ingest_book(epub_path, kb_root=tmp)

        part_files = sorted(out_dir.glob("chapter-01-part-*.md"))
        assert len(part_files) >= 2
        for pf in part_files:
            assert len(pf.read_bytes()) <= 1_000_000
