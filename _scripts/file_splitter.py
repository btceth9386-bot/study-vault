"""Utilities for splitting Markdown into Git-friendly chunks."""

from __future__ import annotations

import re


def _byte_length(text: str) -> int:
    return len(text.encode("utf-8"))


def _split_markdown_blocks(content: str) -> list[str]:
    if not content:
        return []

    pieces = re.split(r"(\n\s*\n)", content)
    blocks: list[str] = []

    for index in range(0, len(pieces), 2):
        block = pieces[index]
        separator = pieces[index + 1] if index + 1 < len(pieces) else ""
        combined = block + separator
        if combined:
            blocks.append(combined)

    return blocks


def _largest_prefix_within_limit(text: str, max_bytes: int) -> int:
    total = 0

    for index, char in enumerate(text):
        total += len(char.encode("utf-8"))
        if total > max_bytes:
            return index

    return len(text)


def _find_preferred_split(text: str, max_bytes: int) -> int:
    prefix_end = _largest_prefix_within_limit(text, max_bytes)
    if prefix_end == len(text):
        return prefix_end

    prefix = text[:prefix_end]

    for pattern in (r"\n\s*\n", r"\n", r"(?<=[.!?。！？])\s+"):
        matches = list(re.finditer(pattern, prefix))
        if matches:
            return matches[-1].end()

    return prefix_end


def _split_oversized_block(block: str, max_bytes: int) -> list[str]:
    parts: list[str] = []
    remaining = block

    while remaining:
        split_at = _find_preferred_split(remaining, max_bytes)
        if split_at <= 0:
            split_at = _largest_prefix_within_limit(remaining, max_bytes)
        if split_at <= 0:
            raise ValueError("Unable to split content within max_bytes")

        parts.append(remaining[:split_at])
        remaining = remaining[split_at:]

    return parts


def split_markdown(content: str, max_bytes: int = 1_000_000) -> list[str]:
    """Split Markdown at heading or paragraph boundaries with byte-sized chunks."""

    if max_bytes <= 0:
        raise ValueError("max_bytes must be greater than zero")
    if not content:
        return []

    chunks: list[str] = []
    current = ""

    for block in _split_markdown_blocks(content):
        if _byte_length(block) > max_bytes:
            if current:
                chunks.append(current)
                current = ""

            chunks.extend(_split_oversized_block(block, max_bytes))
            continue

        candidate = current + block
        if current and _byte_length(candidate) > max_bytes:
            chunks.append(current)
            current = block
            continue

        current = candidate

    if current:
        chunks.append(current)

    return chunks
