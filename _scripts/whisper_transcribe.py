"""Helpers for OpenAI Whisper transcription and SRT cleanup."""

from __future__ import annotations

import os
from pathlib import Path
import re
import sys

from openai import OpenAI


TIMESTAMP_PATTERN = re.compile(
    r"^\s*\d{2}:\d{2}:\d{2},\d{3}\s+-->\s+\d{2}:\d{2}:\d{2},\d{3}\s*$"
)


def _exit_with_error(message: str) -> "NoReturn":
    print(message, file=sys.stderr)
    raise SystemExit(1)


def _get_api_key() -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        _exit_with_error("OPENAI_API_KEY is not set")
    return api_key


def transcribe(audio_path: str, language: str = "auto") -> str:
    """Call the OpenAI Whisper API and return SRT subtitle content."""

    client = OpenAI(api_key=_get_api_key())

    try:
        with Path(audio_path).open("rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=None if language == "auto" else language,
                response_format="srt",
            )
    except Exception as exc:
        _exit_with_error(
            f"OpenAI Whisper API transcription failed: {exc}. "
            "Check OPENAI_API_KEY or network connectivity."
        )

    if isinstance(transcript, str):
        return transcript

    text = getattr(transcript, "text", None)
    if isinstance(text, str):
        return text

    return str(transcript)


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
