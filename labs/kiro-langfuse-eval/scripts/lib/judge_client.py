"""Pluggable judge LLM client — deliberately decoupled from Kiro CLI.

GIVEN. This file supplies the wiring only; it does not pick a vendor for
you. Set JUDGE_PROVIDER to one of the keys in _PROVIDERS below (whichever
you actually hold credentials for), plus JUDGE_API_KEY for that provider.

The rule this lab enforces — that the judge must not share a model family
with whatever Kiro CLI is running the task with — is stated in spec.md
"Why the task model and the judge model must not be the same provider or
model family". This file cannot verify that rule for you: it dispatches to
whichever provider you configure, but *you* must confirm your choice of
JUDGE_PROVIDER doesn't overlap with whatever --model you're running on the
Kiro CLI task side (Kiro CLI's roster spans OpenAI, Anthropic, DeepSeek,
MiniMax, GLM, and Qwen per kiro.dev/docs/models — check against that).
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Callable


def _call_anthropic(prompt: str, model: str, api_key: str) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in response.content if block.type == "text")


def _call_openai(prompt: str, model: str, api_key: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content or ""


def _call_gemini(prompt: str, model: str, api_key: str) -> str:
    from google import genai

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text or ""


# provider key -> (call function, default model for that provider)
_PROVIDERS: dict[str, tuple[Callable[[str, str, str], str], str]] = {
    "anthropic": (_call_anthropic, "claude-haiku-4.5"),
    "openai": (_call_openai, "gpt-4o-mini"),
    "gemini": (_call_gemini, "gemini-2.5-flash"),
}


@dataclass
class JudgeResult:
    text: str
    latency_ms: float
    provider: str
    model: str


def call_judge(prompt: str, *, timeout_s: int = 60) -> JudgeResult:
    """Send one rubric prompt to whichever judge provider is configured.

    Raises RuntimeError if JUDGE_PROVIDER/JUDGE_API_KEY are unset, or if
    JUDGE_PROVIDER names a provider this file doesn't know how to call —
    fail loudly rather than silently falling back to kiro_client, since
    that fallback is exactly the bug this lab's judge/task provider
    separation exists to prevent.
    """
    provider = os.environ.get("JUDGE_PROVIDER")
    if not provider:
        raise RuntimeError(
            "JUDGE_PROVIDER is not set (pick one of: "
            + ", ".join(_PROVIDERS)
            + ") — use whichever provider you hold credentials for, as long "
            "as it's a different model family than the Kiro CLI task side. "
            "See spec.md Prerequisites."
        )
    if provider not in _PROVIDERS:
        raise RuntimeError(
            f"Unknown JUDGE_PROVIDER '{provider}'. Known providers: "
            + ", ".join(_PROVIDERS)
            + " — add a new _call_<provider> function above to support another one."
        )

    api_key = os.environ.get("JUDGE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "JUDGE_API_KEY is not set. The judge must call a distinct "
            "provider, never kiro-cli — see spec.md Prerequisites."
        )

    call_fn, default_model = _PROVIDERS[provider]
    model = os.environ.get("JUDGE_MODEL", default_model)

    start = time.monotonic()
    text = call_fn(prompt, model, api_key)
    latency_ms = (time.monotonic() - start) * 1000

    return JudgeResult(text=text.strip(), latency_ms=latency_ms, provider=provider, model=model)
