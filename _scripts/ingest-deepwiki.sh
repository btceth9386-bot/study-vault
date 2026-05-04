#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 <github-url|deepwiki-url> [kb-root]" >&2
  exit 1
}

[ $# -lt 1 ] && usage

INPUT_URL="$1"
KB_ROOT="${2:-.}"
VENV_BIN="${KB_ROOT}/.venv/bin"
DEEPWIKI_BIN="${DEEPWIKI_TO_MD:-${VENV_BIN}/deepwiki-to-md}"

# Check dependency
if ! "${DEEPWIKI_BIN}" --help &>/dev/null; then
  echo "Error: deepwiki-to-md is not installed. Run: .venv/bin/pip install deepwiki-to-md" >&2
  exit 1
fi

# Convert GitHub URL to DeepWiki URL
if [[ "$INPUT_URL" =~ ^https://github\.com/([^/]+/[^/]+) ]]; then
  REPO_PATH="${BASH_REMATCH[1]}"
  DEEPWIKI_URL="https://deepwiki.com/${REPO_PATH}"
  GITHUB_URL="$INPUT_URL"
elif [[ "$INPUT_URL" =~ ^https://deepwiki\.com/([^/]+/[^/]+) ]]; then
  REPO_PATH="${BASH_REMATCH[1]}"
  DEEPWIKI_URL="$INPUT_URL"
  GITHUB_URL="https://github.com/${REPO_PATH}"
elif [[ "$INPUT_URL" =~ ^([^/[:space:]]+/[^/[:space:]]+)$ ]]; then
  REPO_PATH="${BASH_REMATCH[1]}"
  DEEPWIKI_URL="https://deepwiki.com/${REPO_PATH}"
  GITHUB_URL="https://github.com/${REPO_PATH}"
else
  echo "Error: URL must be a GitHub URL, DeepWiki URL, or owner/repo path." >&2
  exit 1
fi

SLUG="${REPO_PATH//\//-}"
OUT_DIR="${KB_ROOT}/sources/repos/${SLUG}"
SNAPSHOT_DIR="${OUT_DIR}/deepwiki-snapshot"
TODAY="$(date +%Y-%m-%d)"

mkdir -p "${SNAPSHOT_DIR}"

# Attempt download
DEEPWIKI_ERR="$(mktemp)"
trap 'rm -f "${DEEPWIKI_ERR}"' EXIT

echo "Downloading DeepWiki for ${REPO_PATH}..."
if ! "${DEEPWIKI_BIN}" "${REPO_PATH}" --path "${SNAPSHOT_DIR}" 2>"${DEEPWIKI_ERR}"; then
  ERR="$(cat "${DEEPWIKI_ERR}")"
  if echo "$ERR" | grep -qi "private"; then
    echo "Error: DeepWiki only supports public repositories. '${REPO_PATH}' appears to be private." >&2
    rm -rf "${OUT_DIR}"
    exit 1
  else
    echo "Error: DeepWiki has not built a wiki for '${REPO_PATH}' yet." >&2
    echo "  1. Visit https://deepwiki.com and paste the repo URL to trigger a build." >&2
    echo "  2. Wait a few minutes, then re-run this script." >&2
    rm -rf "${OUT_DIR}"
    exit 1
  fi
fi

# Build notes.md from snapshot (concatenate all downloaded md files as summary)
NOTES_FILE="${OUT_DIR}/notes.md"
{
  echo "# ${REPO_PATH} — DeepWiki Notes"
  echo ""
  echo "Source: ${DEEPWIKI_URL}"
  echo ""
  find "${SNAPSHOT_DIR}" -name "*.md" | sort | while read -r f; do
    echo ""
    cat "$f"
  done
} > "${NOTES_FILE}"

# Write meta.yaml
cat > "${OUT_DIR}/meta.yaml" <<EOF
type: repo
title: ${REPO_PATH}
url: ${GITHUB_URL}
language: en
date_consumed: ${TODAY}
date_added: ${TODAY}
status: processed
tags: []
related_concepts: []
EOF

echo "Done. Source saved to: ${OUT_DIR}"
echo "Next: run the new-source prompt on ${OUT_DIR} to generate draft concepts."
