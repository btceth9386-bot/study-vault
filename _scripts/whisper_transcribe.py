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


MAX_WHISPER_BYTES = 24 * 1024 * 1024  # 24 MB (conservative, Whisper limit is ~25 MB)


def _split_audio(audio_path: str, max_bytes: int = MAX_WHISPER_BYTES) -> list[str]:
    """Split audio into chunks under max_bytes using ffmpeg. Returns list of chunk paths."""
    import subprocess, tempfile, math

    path = Path(audio_path)
    file_size = path.stat().st_size
    if file_size <= max_bytes:
        return [audio_path]

    # Get duration in seconds
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
        capture_output=True, text=True,
    )
    try:
        duration = float(result.stdout.strip())
    except ValueError:
        # ffprobe failed — fall back to size-based estimate (128kbps)
        duration = file_size / (128 * 1024 / 8)

    # Calculate chunk duration to stay under limit
    num_chunks = math.ceil(file_size / (max_bytes * 0.85))  # 15% safety margin
    chunk_duration = duration / num_chunks

    tmp_dir = tempfile.mkdtemp(prefix="whisper-chunks-")
    chunks = []
    for i in range(num_chunks):
        start = i * chunk_duration
        chunk_path = f"{tmp_dir}/chunk-{i:03d}.mp3"
        subprocess.run(
            ["ffmpeg", "-y", "-i", audio_path, "-ss", str(start),
             "-t", str(chunk_duration), "-b:a", "64k", chunk_path],
            capture_output=True,
        )
        if Path(chunk_path).exists() and Path(chunk_path).stat().st_size > 0:
            chunks.append(chunk_path)

    return chunks if chunks else [audio_path]


def transcribe(audio_path: str, language: str = "auto") -> str:
    """Call the OpenAI Whisper API and return SRT subtitle content.

    Automatically splits audio files exceeding the 25 MB API limit.
    """

    client = OpenAI(api_key=_get_api_key())
    chunks = _split_audio(audio_path)
    all_srt = []

    for chunk_path in chunks:
        try:
            with Path(chunk_path).open("rb") as audio_file:
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
            all_srt.append(transcript)
        elif hasattr(transcript, "text"):
            all_srt.append(transcript.text)
        else:
            all_srt.append(str(transcript))

    # Clean up temp chunks
    if len(chunks) > 1:
        import shutil
        shutil.rmtree(Path(chunks[0]).parent, ignore_errors=True)

    return "\n\n".join(all_srt)


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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    t = subparsers.add_parser("transcribe")
    t.add_argument("audio_path")
    t.add_argument("--language", default="auto")

    s = subparsers.add_parser("srt-to-md")
    s.add_argument("srt_path")

    args = parser.parse_args()
    if args.command == "transcribe":
        print(transcribe(args.audio_path, args.language))
    else:
        print(srt_to_markdown(args.srt_path))
