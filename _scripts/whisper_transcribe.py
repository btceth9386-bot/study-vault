from __future__ import annotations

from pathlib import Path
import os
import re


TIMESTAMP_PATTERN = re.compile(
    r"^\s*\d{2}:\d{2}:\d{2},\d{3}\s+-->\s+\d{2}:\d{2}:\d{2},\d{3}\s*$"
)


def transcribe(audio_path: str, language: str = "auto") -> str:
    """Call the OpenAI Whisper API and return the transcript text."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required")

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    with Path(audio_path).open("rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=None if language == "auto" else language,
            response_format="text",
        )

    return transcript if isinstance(transcript, str) else str(transcript)


def srt_to_markdown(srt_path: str) -> str:
    """Convert SRT subtitles to clean Markdown."""
    content = Path(srt_path).read_text(encoding="utf-8")
    paragraphs = []
    current = []
    expect_sequence = True

    for raw_line in content.splitlines():
        line = raw_line.rstrip("\r\n")
        normalized = line.strip()
        if not normalized:
            if current:
                paragraphs.append(" ".join(current))
                current = []
            expect_sequence = True
            continue
        if expect_sequence and normalized.isdigit():
            expect_sequence = False
            continue
        expect_sequence = False
        if TIMESTAMP_PATTERN.match(normalized):
            continue
        current.append(line)

    if current:
        paragraphs.append(" ".join(current))

    return "\n\n".join(paragraphs)
