#!/usr/bin/env bash
set -euo pipefail

# Usage: ingest-youtube.sh <youtube-url> [kb-root]
URL="${1:?Usage: ingest-youtube.sh <youtube-url> [kb-root]}"
KB_ROOT="${2:-.}"
SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"

# Dependency checks
if ! command -v yt-dlp &>/dev/null; then
  echo "Error: yt-dlp is not installed. Install with: pip install yt-dlp" >&2
  exit 1
fi
if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "Error: OPENAI_API_KEY is not set" >&2
  exit 1
fi

# Derive slug from URL
SLUG="$(echo "$URL" | sed 's|.*[=/]||; s|[^a-zA-Z0-9_-]|-|g' | tr '[:upper:]' '[:lower:]')"
OUT_DIR="${KB_ROOT}/sources/videos/${SLUG}"
mkdir -p "${OUT_DIR}"

TRANSCRIPT_MD="${OUT_DIR}/transcript.md"
SRT_FILE="${OUT_DIR}/transcript.srt"
AUDIO_FILE="${OUT_DIR}/audio.m4a"

# Ensure audio files are gitignored
GITIGNORE="${KB_ROOT}/.gitignore"
if [[ -f "$GITIGNORE" ]] && ! grep -qF "*.m4a" "$GITIGNORE"; then
  echo "*.m4a" >> "$GITIGNORE"
fi

# Step 1: Try to download subtitles
if yt-dlp --write-sub --write-auto-sub --sub-lang en --skip-download \
    --output "${OUT_DIR}/transcript" "$URL" 2>/dev/null \
    && ls "${OUT_DIR}"/transcript*.srt 2>/dev/null | head -1 | xargs -I{} cp {} "$SRT_FILE" 2>/dev/null \
    && [[ -s "$SRT_FILE" ]]; then
  # Convert SRT to Markdown
  .venv/bin/python3 "${SCRIPTS_DIR}/whisper_transcribe.py" srt-to-md "$SRT_FILE" > "$TRANSCRIPT_MD"
else
  # Step 2: Fallback — download audio and use Whisper API
  rm -f "$SRT_FILE"
  if ! yt-dlp --extract-audio --audio-format m4a --output "$AUDIO_FILE" "$URL" 2>/dev/null; then
    echo "Error: yt-dlp failed to download audio from $URL. Check the URL is valid." >&2
    exit 1
  fi
  SRT_OUT="${OUT_DIR}/transcript_whisper.srt"
  .venv/bin/python3 "${SCRIPTS_DIR}/whisper_transcribe.py" transcribe "$AUDIO_FILE" > "$SRT_OUT"
  .venv/bin/python3 "${SCRIPTS_DIR}/whisper_transcribe.py" srt-to-md "$SRT_OUT" > "$TRANSCRIPT_MD"
fi

# Create highlights.md template
cat > "${OUT_DIR}/highlights.md" <<'EOF'
# Highlights

<!-- Fill in key takeaways after running the new-source prompt -->
EOF

# Create meta.yaml
TODAY="$(date +%Y-%m-%d)"
cat > "${OUT_DIR}/meta.yaml" <<EOF
type: video
title: "${SLUG}"
url: "${URL}"
language: en
date_consumed: ${TODAY}
date_added: ${TODAY}
status: ingesting
related_concepts: []
tags: []
EOF

echo "Done: ${OUT_DIR}"
