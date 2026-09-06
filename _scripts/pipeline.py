#!/usr/bin/env python3
"""Exobrain Pipeline — orchestrate AI agents through the knowledge base workflow.

Usage:
    # Process, independently verify, and promote a source's concepts:
    .venv/bin/python3 _scripts/pipeline.py sources/videos/my-video

    # Run a single step:
    .venv/bin/python3 _scripts/pipeline.py sources/repos/my-repo --step ingest
    .venv/bin/python3 _scripts/pipeline.py sources/repos/my-repo --step review
    .venv/bin/python3 _scripts/pipeline.py _drafts/my-concept.md --step promote
    .venv/bin/python3 _scripts/pipeline.py sources/repos/my-repo --step topics

    # Use a custom config:
    .venv/bin/python3 _scripts/pipeline.py sources/repos/my-repo --config my-pipeline.yml
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

STEPS = ["ingest", "review", "promote", "topics"]
# `lab` is a manual-only step (per-concept, interactive setup) — not part of the
# default per-source pipeline run, but available via --step.
STEP_CHOICES = STEPS + ["lab"]
DEFAULT_CONFIG = Path(__file__).parent / "pipeline.yml"
REVIEW_STATUSES = ("pending", "verified", "needs-decision", "rejected")


def load_config(path: Path) -> dict:
    with open(path) as f:
        raw = yaml.safe_load(f)

    # Expand env vars in strings
    def expand(value):
        if isinstance(value, str):
            return re.sub(
                r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}",
                lambda m: os.environ.get(m.group(1), m.group(0)),
                value,
            )
        if isinstance(value, dict):
            return {k: expand(v) for k, v in value.items()}
        if isinstance(value, list):
            return [expand(i) for i in value]
        return value

    return expand(raw)


def pick_agent(config: dict, role: str) -> dict | None:
    candidates = [a for a in config.get("agents", []) if a["role"] == role]
    return candidates[0] if candidates else None


def _frontmatter(path: Path) -> dict:
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        return {}
    parts = content.split("---\n", 2)
    if len(parts) < 3:
        return {}
    data = yaml.safe_load(parts[1]) or {}
    return data if isinstance(data, dict) else {}


def _normalized_source(value: str, kb_root: Path) -> str:
    path = Path(value)
    if path.is_absolute():
        try:
            path = path.resolve().relative_to(kb_root.resolve())
        except ValueError:
            pass
    return path.as_posix().rstrip("/")


def reviewed_drafts(kb_root: str | Path, source_dir: str) -> dict[str, list[str]]:
    """Group drafts for one source by the reviewer's persisted verdict."""

    root = Path(kb_root)
    source = _normalized_source(source_dir, root)
    grouped = {status: [] for status in REVIEW_STATUSES}
    for path in sorted((root / "_drafts").glob("*.md")):
        metadata = _frontmatter(path)
        if _normalized_source(str(metadata.get("source", "")), root) != source:
            continue
        status = str(metadata.get("review_status", "pending"))
        if status not in grouped:
            status = "needs-decision"
        grouped[status].append(path.relative_to(root).as_posix())
    return grouped


def run_agent(agent: dict, prompt: str, cwd: str) -> subprocess.CompletedProcess:
    command = agent["command"]
    env = {**os.environ, **agent.get("env", {})}

    # Append prompt as the last argument
    full_command = f"{command} {shlex.quote(prompt)}"
    log.info("Running agent '%s' (role=%s)", agent["name"], agent["role"])
    log.info("Command: %s", full_command[:200])

    result = subprocess.run(
        full_command,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True,
        env=env,
    )
    return result


def run_step(
    config: dict,
    step: str,
    source_dir: str | None = None,
    prompt_vars: dict[str, str] | None = None,
) -> bool:
    kb_root = config.get("kb_root", ".")
    agent = pick_agent(config, step)
    if not agent:
        log.error("No agent configured for role '%s'", step)
        return False

    prompts = config.get("prompts", {})
    prompt_template = prompts.get(step)
    if not prompt_template:
        log.error("No prompt configured for step '%s'", step)
        return False

    # Fill template variables
    values = {"source_dir": source_dir or "", "kb_root": kb_root, **(prompt_vars or {})}
    prompt = prompt_template
    for key, value in values.items():
        prompt = prompt.replace(f"{{{key}}}", value)

    # Validate step prerequisites
    if step in STEP_CHOICES and not source_dir:
        log.error("Step '%s' requires a target path or request", step)
        return False

    log.info("=== Step: %s ===", step)
    result = run_agent(agent, prompt, cwd=kb_root)

    if result.returncode != 0:
        log.error("Agent '%s' failed (exit %d)", agent["name"], result.returncode)
        if result.stderr:
            log.error("stderr: %s", result.stderr[:500])
        return False

    log.info("Agent '%s' completed successfully", agent["name"])
    if result.stdout:
        # Print last 500 chars of output as summary
        log.info("Output (tail): %s", result.stdout[-500:])
    return True


def main():
    parser = argparse.ArgumentParser(description="Exobrain Pipeline")
    parser.add_argument(
        "source_dir",
        nargs="?",
        help="Path to ingested source (required for 'ingest' step and full pipeline)",
    )
    parser.add_argument(
        "--step",
        choices=STEP_CHOICES,
        help="Run a single step instead of the full pipeline",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help=f"Pipeline config file (default: {DEFAULT_CONFIG})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without executing",
    )
    args = parser.parse_args()

    config = load_config(args.config)

    if args.step:
        # Single step mode
        if args.dry_run:
            agent = pick_agent(config, args.step)
            prompt = config.get("prompts", {}).get(args.step, "")
            prompt = prompt.replace("{source_dir}", args.source_dir or "").replace(
                "{kb_root}", config.get("kb_root", ".")
            ).replace("{verified_drafts}", args.source_dir or "")
            print(f"Agent: {agent['name'] if agent else 'NONE'}")
            print(f"Command: {agent['command'] if agent else 'NONE'}")
            print(f"Prompt: {prompt}")
            return

        prompt_vars = None
        if args.step == "promote":
            prompt_vars = {"verified_drafts": args.source_dir or ""}
        success = run_step(config, args.step, args.source_dir, prompt_vars)
        sys.exit(0 if success else 1)

    # Full pipeline mode (steps 2-5)
    if not args.source_dir:
        parser.error("source_dir is required for full pipeline mode")

    if args.dry_run:
        for step in STEPS:
            agent = pick_agent(config, step)
            print(f"[{step}] Agent: {agent['name'] if agent else 'NONE'}")
        print("[promote] Conditional: only drafts persisted as review_status=verified")
        return

    for step in ("ingest", "review"):
        if not run_step(config, step, args.source_dir):
            log.error("Pipeline stopped at step '%s'", step)
            sys.exit(1)

    verdicts = reviewed_drafts(config.get("kb_root", "."), args.source_dir)
    verified = verdicts["verified"]
    exceptions = verdicts["pending"] + verdicts["needs-decision"]

    if verified:
        if not run_step(
            config,
            "promote",
            args.source_dir,
            {"verified_drafts": "\n".join(f"- {path}" for path in verified)},
        ):
            log.error("Pipeline stopped at step 'promote'")
            sys.exit(1)
        if not run_step(config, "topics", args.source_dir):
            log.error("Pipeline stopped at step 'topics'")
            sys.exit(1)
    else:
        log.info("No verified drafts for %s; skipping promote and topics", args.source_dir)

    if exceptions:
        log.warning("Drafts need a decision: %s", ", ".join(exceptions))
    if verdicts["rejected"]:
        log.info("Rejected drafts retained with review notes: %s", ", ".join(verdicts["rejected"]))

    if not args.dry_run:
        log.info("Pipeline completed; refresh OpenWiki manually if canonical content changed")


if __name__ == "__main__":
    main()
