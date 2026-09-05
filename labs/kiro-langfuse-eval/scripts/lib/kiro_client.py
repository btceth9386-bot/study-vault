"""Thin wrapper around `kiro-cli chat --no-interactive`.

GIVEN — you should not need to change this file. It exists so the rest of
the harness talks to a plain Python object instead of shelling out and
scraping ANSI text everywhere.

Kiro CLI is the ACP agent backend documented at
https://github.com/openabdev/openab/blob/main/docs/kiro.md — it prints the
first response to STDOUT and exits when called with `--no-interactive`.
Model switching works the same way `/model claude-sonnet-4` does inside an
interactive session: send it as a slash-command line before the task text
in the same piped input.
"""
from __future__ import annotations

import re
import subprocess
import time
from dataclasses import dataclass

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[mGKHFABCDJsuhl?]")


def strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


@dataclass
class KiroResult:
    output: str
    raw: str
    latency_ms: float
    model: str | None
    exit_code: int


def call_kiro(prompt: str, *, model: str | None = None, agent: str | None = None,
               timeout_s: int = 120) -> KiroResult:
    """Send one task to Kiro CLI and return its first response.

    If `model` is given, a `/model <id>` line is sent ahead of the prompt in
    the same stdin blob — this mirrors the pattern in the credit-usage
    snippet (`echo "/usage" | kiro-cli chat --no-interactive`), which is the
    one invocation shape verified to work in this environment. Confirm with
    `kiro-cli chat --help` before relying on this in a different Kiro
    version; docs for --model at the `chat` subcommand level were unclear
    at write time (see spec.md "Setup / verify Kiro CLI" step).
    """
    stdin_lines = []
    if model:
        stdin_lines.append(f"/model {model}")
    stdin_lines.append(prompt)
    stdin_payload = "\n".join(stdin_lines)

    cmd = ["kiro-cli", "chat", "--no-interactive"]
    if agent:
        cmd = ["kiro-cli", "chat", "--agent", agent, "--no-interactive"]

    start = time.monotonic()
    proc = subprocess.run(
        cmd,
        input=stdin_payload,
        capture_output=True,
        text=True,
        timeout=timeout_s,
    )
    latency_ms = (time.monotonic() - start) * 1000

    raw = strip_ansi(proc.stdout + proc.stderr)
    return KiroResult(
        output=raw.strip(),
        raw=raw,
        latency_ms=latency_ms,
        model=model,
        exit_code=proc.returncode,
    )


def get_usage_snapshot(timeout_s: int = 30) -> str:
    """Run `/usage` and return the stripped 'Estimated Usage' block.

    Adapted from the working snippet:

        echo "/usage" | kiro-cli chat --no-interactive 2>&1 \\
          | sed 's/\\x1b\\[[0-9;]*[mGKHFABCDJsuhl?]//g' \\
          | grep -A 20 "Estimated Usage"

    Returns the raw text block; scripts/lib/usage_parser.py turns it into
    structured JSON. Kept separate from call_kiro() because a usage check
    is its own zero-argument call, not a dataset task.
    """
    proc = subprocess.run(
        ["kiro-cli", "chat", "--no-interactive"],
        input="/usage",
        capture_output=True,
        text=True,
        timeout=timeout_s,
    )
    text = strip_ansi(proc.stdout + proc.stderr)
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "Estimated Usage" in line:
            return "\n".join(lines[i : i + 21])
    return text
