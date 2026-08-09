#!/usr/bin/env bash
# GIVEN. Invoked by the Kiro `Stop` hook (.kiro/hooks/log-usage-on-stop.json)
# after every agent response. Appends one JSON line with a credit-usage
# snapshot to usage-log.jsonl, so a whole dataset run's cost can be summed
# without asking the learner to babysit `/usage` by hand.
#
# Adapted from:
#   echo "/usage" | kiro-cli chat --no-interactive 2>&1 \
#     | sed 's/\x1b\[[0-9;]*[mGKHFABCDJsuhl?]//g' | grep -A 20 "Estimated Usage"
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="${KIRO_USAGE_LOG:-$LAB_DIR/usage-log.jsonl}"

strip_ansi() { sed 's/\x1b\[[0-9;]*[mGKHFABCDJsuhl?]//g'; }

raw_block="$(echo "/usage" | kiro-cli chat --no-interactive 2>&1 | strip_ansi | grep -A 20 "Estimated Usage" || true)"

# First two numbers in the block are treated as (used, limit). If your Kiro
# CLI version prints a different shape, this is the line to adjust — see
# scripts/lib/usage_parser.py for the same extraction in Python.
mapfile -t numbers < <(echo "$raw_block" | grep -oE '[0-9]+(\.[0-9]+)?')
used="${numbers[0]:-null}"
limit="${numbers[1]:-null}"
ts="$(date -u +%FT%TZ)"

escaped_raw="$(python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))' <<<"$raw_block" 2>/dev/null || printf '"%s"' "${raw_block//\"/\\\"}")"

printf '{"timestamp":"%s","credits_used":%s,"credits_limit":%s,"raw":%s}\n' \
  "$ts" "$used" "$limit" "$escaped_raw" >> "$LOG_FILE"
