from __future__ import annotations

from pathlib import Path
import string
import sys

from hypothesis import given
from hypothesis import strategies as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _scripts.file_splitter import split_markdown


TEXT_ALPHABET = string.ascii_letters + string.digits + " .,;:-_/"
HEADING_TEXT = st.text(alphabet=TEXT_ALPHABET, min_size=1, max_size=40)
PARAGRAPH_TEXT = st.text(alphabet=TEXT_ALPHABET, min_size=1, max_size=200)


@st.composite
def markdown_documents(draw):
    blocks = draw(
        st.lists(
            st.one_of(
                HEADING_TEXT.map(lambda text: f"# {text}"),
                PARAGRAPH_TEXT,
            ),
            min_size=1,
            max_size=20,
        )
    )
    return "\n\n".join(blocks)


@given(markdown_documents(), st.integers(min_value=1, max_value=120))
def test_split_markdown_respects_max_bytes(content: str, max_bytes: int) -> None:
    chunks = split_markdown(content, max_bytes=max_bytes)

    assert chunks
    assert all(len(chunk.encode("utf-8")) <= max_bytes for chunk in chunks)
    assert [chunk.part_number for chunk in chunks] == list(range(1, len(chunks) + 1))
    assert all(chunk.total_parts == len(chunks) for chunk in chunks)


@given(markdown_documents(), st.integers(min_value=1, max_value=120))
def test_split_markdown_preserves_content(content: str, max_bytes: int) -> None:
    chunks = split_markdown(content, max_bytes=max_bytes)

    assert "".join(chunks) == content


def test_split_markdown_returns_empty_list_for_empty_content() -> None:
    assert split_markdown("") == []


def test_split_markdown_prefers_heading_boundaries() -> None:
    content = "# One\n\nalpha.\n\n# Two\n\nbeta.\n"
    max_bytes = len("# One\n\nalpha.\n\n".encode("utf-8"))

    chunks = split_markdown(content, max_bytes=max_bytes)

    assert len(chunks) == 2
    assert chunks[0] == "# One\n\nalpha.\n\n"
    assert chunks[1] == "# Two\n\nbeta.\n"
