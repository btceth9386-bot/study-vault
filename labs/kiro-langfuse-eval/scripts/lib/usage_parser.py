"""Turn the raw '/usage' text block into structured JSON.

GIVEN. The exact wording of the "Estimated Usage" block can vary by Kiro CLI
version, so this parser is deliberately forgiving: it pulls the first two
numbers it finds (used, limit) and always keeps the raw text so nothing is
silently lost. If your Kiro CLI version prints a shape this regex misses,
adjust the two regexes below — that is a parsing detail, not the lab's core
task, but you may need to fix it once during Setup step 1's smoke test.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

_NUMBER_RE = re.compile(r"(\d+(?:\.\d+)?)")


@dataclass
class UsageSnapshot:
    timestamp: str
    credits_used: float | None
    credits_limit: float | None
    raw: str

    def to_dict(self) -> dict:
        return asdict(self)


def parse_usage_block(raw_block: str) -> UsageSnapshot:
    numbers = _NUMBER_RE.findall(raw_block)
    credits_used = float(numbers[0]) if len(numbers) >= 1 else None
    credits_limit = float(numbers[1]) if len(numbers) >= 2 else None
    return UsageSnapshot(
        timestamp=datetime.now(timezone.utc).isoformat(),
        credits_used=credits_used,
        credits_limit=credits_limit,
        raw=raw_block,
    )
