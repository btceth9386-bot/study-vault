#!/usr/bin/env python3
"""Exobrain Pipeline — orchestrate AI agents through the knowledge base workflow.

Usage:
    # Run full pipeline (steps 2-5) for a source that was already ingested:
    .venv/bin/python3 _scripts/pipeline.py sources/videos/my-video

    # Run a single step:
    .venv/bin/python3 _scripts/pipeline.py sources/repos/my-repo --step ingest
    .venv/bin/python3 _scripts/pipeline.py --step review
    .venv/bin/python3 _scripts/pipeline.py --step promote
    .venv/bin/python3 _scripts/pipeline.py --step topics

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
DEFAULT_CONFIG = Path(__file__).parent / "pipeline.yml"


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


def run_step(config: dict, step: str, source_dir: str | None = None) -> bool:
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
    prompt = prompt_template.replace("{source_dir}", source_dir or "").replace(
        "{kb_root}", kb_root
    )

    # Validate step prerequisites
    if step == "ingest" and not source_dir:
        log.error("Step 'ingest' requires a source_dir argument")
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
        choices=STEPS,
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
            )
            print(f"Agent: {agent['name'] if agent else 'NONE'}")
            print(f"Command: {agent['command'] if agent else 'NONE'}")
            print(f"Prompt: {prompt}")
            return

        success = run_step(config, args.step, args.source_dir)
        sys.exit(0 if success else 1)

    # Full pipeline mode (steps 2-5)
    if not args.source_dir:
        parser.error("source_dir is required for full pipeline mode")

    steps_to_run = STEPS  # ingest, review, promote, topics

    for step in steps_to_run:
        if args.dry_run:
            agent = pick_agent(config, step)
            prompt = config.get("prompts", {}).get(step, "")
            prompt = prompt.replace("{source_dir}", args.source_dir or "").replace(
                "{kb_root}", config.get("kb_root", ".")
            )
            print(f"[{step}] Agent: {agent['name'] if agent else 'NONE'}")
            print(f"[{step}] Prompt: {prompt[:100]}...")
            print()
            continue

        success = run_step(config, step, args.source_dir)
        if not success:
            log.error("Pipeline stopped at step '%s'", step)
            sys.exit(1)

    if not args.dry_run:
        log.info("Pipeline completed successfully!")


if __name__ == "__main__":
    main()
