#!/usr/bin/env bash
# GIVEN. One-time environment setup + smoke tests. Run from the lab root:
#   ./scripts/setup.sh
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$LAB_DIR"

echo "== 1. Prerequisite binaries =="
command -v kiro-cli >/dev/null || {
  echo "FAIL: kiro-cli not on PATH. This lab is real-tool: install/authenticate"
  echo "      Kiro CLI per https://github.com/openabdev/openab/blob/main/docs/kiro.md"
  echo "      (KIRO_API_KEY env var, or OAuth device flow) before continuing."
  exit 1
}
echo "OK: kiro-cli found at $(command -v kiro-cli)"

echo
echo "== 2. Python env =="
python3 -m venv .venv 2>/dev/null || true
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt
echo "OK: dependencies installed"

echo
echo "== 3. Env vars =="
if [ ! -f .env ]; then
  echo "No .env found — copy .env.example to .env and fill in KIRO_API_KEY / LANGFUSE_* first."
  exit 1
fi
set -a; source .env; set +a
for var in KIRO_API_KEY JUDGE_PROVIDER JUDGE_API_KEY LANGFUSE_PUBLIC_KEY LANGFUSE_SECRET_KEY LANGFUSE_BASE_URL; do
  [ -n "${!var:-}" ] || { echo "FAIL: $var is empty in .env"; exit 1; }
done
case "$JUDGE_PROVIDER" in
  anthropic|openai|gemini) ;;
  *) echo "FAIL: JUDGE_PROVIDER='$JUDGE_PROVIDER' is not one of anthropic|openai|gemini (see scripts/lib/judge_client.py)"; exit 1 ;;
esac
echo "OK: required env vars are set (including JUDGE_PROVIDER=$JUDGE_PROVIDER — confirm yourself it doesn't share a model family with your Kiro CLI task --model, see spec.md)"

echo
echo "== 4. Langfuse reachability =="
curl -sS -m 5 "${LANGFUSE_BASE_URL%/}/api/public/health" || {
  echo "FAIL: could not reach Langfuse at $LANGFUSE_BASE_URL"
  exit 1
}
echo
echo "OK: Langfuse health check passed"

echo
echo "== 5. Kiro CLI smoke test (this is the invocation shape the whole lab depends on) =="
echo "Sending: /model auto + a 1-line prompt via stdin to 'kiro-cli chat --no-interactive'"
printf '/model auto\nReply with exactly the word: pong\n' | kiro-cli chat --no-interactive
echo
echo "If the line above did not look like a single short reply (e.g. it echoed"
echo "back multiple turns, or /model was treated as literal text), open"
echo "'kiro-cli chat --help' and adjust scripts/lib/kiro_client.py's call_kiro()"
echo "before running the rest of the lab — see spec.md 'Setup / verify Kiro CLI'."

echo
echo "== 6. Usage snapshot smoke test =="
./scripts/log_usage.sh
tail -n 1 "${KIRO_USAGE_LOG:-$LAB_DIR/usage-log.jsonl}"
echo
echo "Setup checks complete."
