#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KB_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PYTHON="${KB_ROOT}/.venv/bin/python3"

usage() {
  echo "Usage: $0 <audio-file-or-url> [language]" >&2
  echo "  language: ISO code (e.g. en, zh) or 'auto' (default)" >&2
  exit 1
}

[ $# -lt 1 ] && usage

INPUT="$1"
LANGUAGE="${2:-auto}"

if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "Error: OPENAI_API_KEY is not set." >&2
  exit 1
fi

# Derive slug from input basename
BASENAME="$(basename "${INPUT}")"
SLUG="${BASENAME%.*}"
SLUG="$(echo "${SLUG}" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//;s/-$//')"

OUT_DIR="${KB_ROOT}/sources/podcasts/${SLUG}"

if [ -d "${OUT_DIR}" ]; then
  echo "Error: Output directory already exists: ${OUT_DIR}" >&2
  exit 1
fi

mkdir -p "${OUT_DIR}"

# Download if URL
AUDIO_PATH="${INPUT}"
if echo "${INPUT}" | grep -qE '^https?://'; then
  AUDIO_PATH="${OUT_DIR}/${SLUG}.mp3"
  echo "Downloading audio from ${INPUT} ..."
  if command -v yt-dlp &>/dev/null; then
    yt-dlp -x --audio-format mp3 -o "${AUDIO_PATH}" "${INPUT}"
  elif command -v curl &>/dev/null; then
    curl -fsSL -o "${AUDIO_PATH}" "${INPUT}"
  else
    echo "Error: No download tool found (yt-dlp or curl required)." >&2
    rm -rf "${OUT_DIR}"
    exit 1
  fi
fi

# Transcribe via Whisper API and convert SRT → Markdown
echo "Transcribing ${AUDIO_PATH} ..."
"${PYTHON}" -c "
import sys, tempfile, os
sys.path.insert(0, '${KB_ROOT}')
from _scripts.whisper_transcribe import transcribe, srt_to_markdown
srt = transcribe(sys.argv[1], sys.argv[2])
with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False, encoding='utf-8') as f:
    f.write(srt); tmp = f.name
try:
    md = srt_to_markdown(tmp)
finally:
    os.unlink(tmp)
open(sys.argv[3], 'w', encoding='utf-8').write(md)
" "${AUDIO_PATH}" "${LANGUAGE}" "${OUT_DIR}/transcript.md"

# Write highlights template
cat > "${OUT_DIR}/highlights.md" <<'EOF'
# Highlights

<!-- Key insights from this podcast episode. Fill in after review. -->
EOF

# Write meta.yaml
TODAY="$(date +%Y-%m-%d)"
TITLE="$(echo "${SLUG}" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2); print}')"

cat > "${OUT_DIR}/meta.yaml" <<EOF
type: podcast
title: ${TITLE}
language: ${LANGUAGE}
date_consumed: ${TODAY}
date_added: ${TODAY}
status: processed
related_concepts: []
tags: []
EOF

# Validate meta.yaml
ERRORS="$("${PYTHON}" -c "
import sys
sys.path.insert(0, '${KB_ROOT}')
from _scripts.metadata_validator import validate_source_meta
errors = validate_source_meta('${OUT_DIR}/meta.yaml')
for e in errors: print(e)
")"
if [ -n "${ERRORS}" ]; then
  echo "Warning: meta.yaml validation errors:" >&2
  echo "${ERRORS}" >&2
fi

# Ensure audio file patterns are in .gitignore
GITIGNORE="${KB_ROOT}/.gitignore"
for pattern in "*.mp3" "*.wav" "*.m4a" "*.ogg" "*.flac"; do
  if ! grep -qxF "${pattern}" "${GITIGNORE}" 2>/dev/null; then
    echo "${pattern}" >> "${GITIGNORE}"
  fi
done

echo "Done. Output: ${OUT_DIR}"
echo "Next: run the new-source prompt on ${OUT_DIR}"
