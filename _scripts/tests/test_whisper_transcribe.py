from __future__ import annotations

from pathlib import Path
import re
import sys
import tempfile

from hypothesis import given
from hypothesis import strategies as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _scripts.whisper_transcribe import srt_to_markdown


TIMESTAMP_PATTERN = re.compile(r"\d{2}:\d{2}:\d{2},\d{3}\s+-->\s+\d{2}:\d{2}:\d{2},\d{3}")
TEXT_STRATEGY = st.text(
    alphabet=st.characters(
        blacklist_categories=("Cc", "Cs"),
        blacklist_characters="\x00\r\n",
    ),
    min_size=1,
    max_size=40,
).filter(lambda text: text.strip() != "")


@st.composite
def srt_payloads(draw):
    block_count = draw(st.integers(min_value=1, max_value=12))
    blocks = []

    for _ in range(block_count):
        sequence = draw(st.integers(min_value=1, max_value=9999))
        start_hour = draw(st.integers(min_value=0, max_value=22))
        start_minute = draw(st.integers(min_value=0, max_value=59))
        start_second = draw(st.integers(min_value=0, max_value=58))
        start_millisecond = draw(st.integers(min_value=0, max_value=998))
        end_hour = draw(st.integers(min_value=start_hour, max_value=23))
        end_minute = draw(st.integers(min_value=0, max_value=59))
        end_second = draw(st.integers(min_value=0, max_value=59))
        end_millisecond = draw(st.integers(min_value=0, max_value=999))
        text_lines = draw(st.lists(TEXT_STRATEGY, min_size=1, max_size=4))
        timestamp = (
            f"{start_hour:02d}:{start_minute:02d}:{start_second:02d},{start_millisecond:03d} --> "
            f"{end_hour:02d}:{end_minute:02d}:{end_second:02d},{end_millisecond:03d}"
        )
        blocks.append((sequence, timestamp, text_lines))

    parts = []
    expected_segments = []
    for sequence, timestamp, text_lines in blocks:
        parts.append(str(sequence))
        parts.append(timestamp)
        parts.extend(text_lines)
        parts.append("")
        expected_segments.extend(text_lines)

    return "\n".join(parts), expected_segments


@given(srt_payloads())
def test_srt_to_markdown_preserves_all_text_segments(payload: tuple[str, list[str]]) -> None:
    srt_content, expected_segments = payload

    with tempfile.TemporaryDirectory() as temp_dir:
        srt_path = Path(temp_dir) / "sample.srt"
        srt_path.write_text(srt_content, encoding="utf-8")

        markdown = srt_to_markdown(str(srt_path))

    for segment in expected_segments:
        assert segment in markdown

    assert not TIMESTAMP_PATTERN.search(markdown)


def test_srt_to_markdown_merges_multiline_blocks_and_removes_sequence_numbers(tmp_path: Path) -> None:
    srt_path = tmp_path / "sample.srt"
    srt_path.write_text(
        "1\n"
        "00:00:01,000 --> 00:00:02,000\n"
        "hello\n"
        "world\n"
        "\n"
        "2\n"
        "00:00:03,000 --> 00:00:04,000\n"
        "second block\n",
        encoding="utf-8",
    )

    markdown = srt_to_markdown(str(srt_path))

    assert markdown == "hello world\n\nsecond block"
    assert "00:00:01,000 --> 00:00:02,000" not in markdown
    assert "\n1\n" not in f"\n{markdown}\n"
