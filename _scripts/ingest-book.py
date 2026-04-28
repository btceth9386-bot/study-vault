"""Ingest an epub book into sources/books/<slug>/."""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

import ebooklib
import yaml
from ebooklib import epub
from html.parser import HTMLParser

sys.path.insert(0, str(Path(__file__).resolve().parent))
from file_splitter import split_markdown


# ---------------------------------------------------------------------------
# HTML → plain Markdown conversion (no external deps beyond stdlib)
# ---------------------------------------------------------------------------

class _HTMLToMarkdown(HTMLParser):
    """Minimal HTML-to-Markdown converter for epub chapter content."""

    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []
        self._skip = False

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in ("script", "style"):
            self._skip = True
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(tag[1])
            self._parts.append("\n" + "#" * level + " ")
        elif tag == "p":
            self._parts.append("\n\n")
        elif tag == "br":
            self._parts.append("\n")
        elif tag == "li":
            self._parts.append("\n- ")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style"):
            self._skip = False

    def handle_data(self, data: str) -> None:
        if not self._skip:
            self._parts.append(data)

    def result(self) -> str:
        text = "".join(self._parts)
        # Collapse excessive blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def _html_to_markdown(html: str) -> str:
    parser = _HTMLToMarkdown()
    parser.feed(html)
    return parser.result()


# ---------------------------------------------------------------------------
# Slug helpers
# ---------------------------------------------------------------------------

def _slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-") or "book"


# ---------------------------------------------------------------------------
# Core ingest logic
# ---------------------------------------------------------------------------

def ingest_book(epub_path: str | Path, kb_root: str | Path = ".") -> Path:
    """Parse *epub_path* and write sources/books/<slug>/ under *kb_root*.

    Returns the created source directory.
    """
    epub_path = Path(epub_path)
    if not epub_path.exists():
        raise FileNotFoundError(f"epub not found: {epub_path}")

    book = epub.read_epub(str(epub_path))

    title: str = book.get_metadata("DC", "title")[0][0] if book.get_metadata("DC", "title") else epub_path.stem
    authors: list[str] = [a[0] for a in book.get_metadata("DC", "creator")] if book.get_metadata("DC", "creator") else []
    language: str = book.get_metadata("DC", "language")[0][0] if book.get_metadata("DC", "language") else "en"

    slug = _slugify(title)
    out_dir = Path(kb_root) / "sources" / "books" / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    # Collect document items in spine order
    spine_ids = {item_id for item_id, _ in book.spine}
    chapters = [
        item for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
        if item.get_id() in spine_ids
    ]

    chapter_num = 0
    for item in chapters:
        content = _html_to_markdown(item.get_content().decode("utf-8", errors="replace"))
        if not content.strip():
            continue

        chapter_num += 1
        chunks = split_markdown(content)

        if len(chunks) <= 1:
            out_file = out_dir / f"chapter-{chapter_num:02d}.md"
            out_file.write_text(content, encoding="utf-8")
        else:
            for chunk in chunks:
                part_file = out_dir / f"chapter-{chapter_num:02d}-part-{chunk.part_number:02d}.md"
                part_file.write_text(str(chunk), encoding="utf-8")

    today = date.today().isoformat()
    meta = {
        "type": "book",
        "title": title,
        "authors": authors,
        "language": language,
        "date_consumed": today,
        "date_added": today,
        "status": "ingesting",
        "related_concepts": [],
        "tags": [],
    }
    (out_dir / "meta.yaml").write_text(yaml.safe_dump(meta, allow_unicode=True, sort_keys=False), encoding="utf-8")

    # Ensure epub is gitignored at kb_root level
    gitignore = Path(kb_root) / ".gitignore"
    if gitignore.exists():
        existing = gitignore.read_text(encoding="utf-8")
        if "*.epub" not in existing:
            gitignore_path = gitignore
            with gitignore_path.open("a", encoding="utf-8") as fh:
                fh.write("\n# epub books\n*.epub\n")
    else:
        gitignore.write_text("# epub books\n*.epub\n", encoding="utf-8")

    return out_dir


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: ingest-book.py <epub-path> [kb-root]", file=sys.stderr)
        sys.exit(1)

    epub_path = sys.argv[1]
    kb_root = sys.argv[2] if len(sys.argv) > 2 else "."

    try:
        out_dir = ingest_book(epub_path, kb_root)
        print(f"Ingested: {out_dir}")
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
