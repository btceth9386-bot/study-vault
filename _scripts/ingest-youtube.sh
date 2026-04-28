#!/usr/bin/env bash
# ingest-youtube.sh - Ingest a YouTube video into the knowledge base.
# Usage: ./_scripts/ingest-youtube.sh <youtube-url> [kb-root]
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <youtube-url> [kb-root]" >&2
  exit 1
fi

YOUTUBE_URL="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KB_ROOT="${2:-$(dirname "${SCRIPT_DIR}")}"
PYTHON="${KB_ROOT}/.venv/bin/python3"
PYTHON_SCRIPTS_DIR="${_INGEST_SCRIPTS_DIR:-${SCRIPT_DIR}}"

if ! command -v yt-dlp >/dev/null 2>&1; then
  echo "Error: yt-dlp is not installed or not in PATH." >&2
  exit 1
fi

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "Error: OPENAI_API_KEY is not set." >&2
  exit 1
fi

echo "Fetching video metadata..."
VIDEO_TITLE="$(yt-dlp --get-title --no-playlist "${YOUTUBE_URL}" 2>/dev/null || true)"
if [[ -z "${VIDEO_TITLE}" ]]; then
  VIDEO_TITLE="$(printf '%s' "${YOUTUBE_URL}" | sed 's|.*[=/]||; s|[^a-zA-Z0-9_-]|-|g')"
fi

SLUG="$(printf '%s' "${VIDEO_TITLE}" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g; s/-\{1,\}/-/g; s/^-//; s/-$//')"
if [[ -z "${SLUG}" ]]; then
  SLUG="video-$(date +%Y%m%d%H%M%S)"
fi

TODAY="$(date +%Y-%m-%d)"
OUT_DIR="${KB_ROOT}/sources/videos/${SLUG}"
mkdir -p "${OUT_DIR}"

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "${WORK_DIR}"' EXIT

echo "Attempting to download subtitles..."
SRT_FILE=""

if yt-dlp \
    --write-subs \
    --sub-langs "en,zh-TW,zh-Hans,zh" \
    --sub-format srt \
    --convert-subs srt \
    --skip-download \
    --no-playlist \
    -o "${WORK_DIR}/%(id)s" \
    --output "${WORK_DIR}/%(id)s" \
    "${YOUTUBE_URL}" >/dev/null 2>&1; then
  SRT_FILE="$(find "${WORK_DIR}" -type f -name "*.srt" | head -1)"
fi

if [[ -z "${SRT_FILE}" ]]; then
  if yt-dlp \
      --write-auto-subs \
      --sub-langs "en,zh-TW,zh-Hans,zh" \
      --sub-format srt \
      --convert-subs srt \
      --skip-download \
      --no-playlist \
      -o "${WORK_DIR}/%(id)s" \
      --output "${WORK_DIR}/%(id)s" \
      "${YOUTUBE_URL}" >/dev/null 2>&1; then
    SRT_FILE="$(find "${WORK_DIR}" -type f -name "*.srt" | head -1)"
  fi
fi

if [[ -z "${SRT_FILE}" ]]; then
  echo "No subtitles found. Downloading audio for Whisper transcription..."
  yt-dlp \
    --extract-audio \
    --audio-format mp3 \
    --no-playlist \
    -o "${WORK_DIR}/audio.%(ext)s" \
    --output "${WORK_DIR}/audio.%(ext)s" \
    "${YOUTUBE_URL}"

  AUDIO_FILE="$(find "${WORK_DIR}" -type f -name "audio.*" | head -1)"
  if [[ -z "${AUDIO_FILE}" ]]; then
    echo "Error: Audio download failed." >&2
    exit 1
  fi

  echo "Transcribing with Whisper API..."
  SRT_FILE="${WORK_DIR}/transcript.srt"
  if [[ -n "${_INGEST_SCRIPTS_DIR:-}" ]]; then
    "${PYTHON}" - "${PYTHON_SCRIPTS_DIR}" "${AUDIO_FILE}" > "${SRT_FILE}" <<'PY'
import sys

scripts_dir, audio_path = sys.argv[1:3]
sys.path.insert(0, scripts_dir)

from whisper_transcribe import transcribe

print(transcribe(audio_path))
PY
  else
    "${PYTHON}" "${SCRIPT_DIR}/whisper_transcribe.py" transcribe "${AUDIO_FILE}" > "${SRT_FILE}"
  fi
fi

echo "Converting SRT to Markdown..."
if [[ -n "${_INGEST_SCRIPTS_DIR:-}" ]]; then
  TRANSCRIPT_MD="$("${PYTHON}" - "${PYTHON_SCRIPTS_DIR}" "${SRT_FILE}" <<'PY'
import sys

scripts_dir, srt_path = sys.argv[1:3]
sys.path.insert(0, scripts_dir)

from whisper_transcribe import srt_to_markdown

print(srt_to_markdown(srt_path))
PY
)"
else
  TRANSCRIPT_MD="$("${PYTHON}" "${SCRIPT_DIR}/whisper_transcribe.py" srt-to-md "${SRT_FILE}")"
fi

cat > "${OUT_DIR}/transcript.md" <<MD
# ${VIDEO_TITLE}

${TRANSCRIPT_MD}
MD

cat > "${OUT_DIR}/highlights.md" <<MD
# ${VIDEO_TITLE} - Highlights

<!-- Fill in key highlights after reviewing the transcript. -->
MD

"${PYTHON}" - "${OUT_DIR}/meta.yaml" "${VIDEO_TITLE}" "${YOUTUBE_URL}" "${TODAY}" <<'PY'
import sys

import yaml

meta_path, title, url, today = sys.argv[1:5]
metadata = {
    "type": "video",
    "title": title,
    "url": url,
    "language": "en",
    "date_consumed": today,
    "date_added": today,
    "status": "processed",
}

with open(meta_path, "w", encoding="utf-8") as handle:
    yaml.safe_dump(metadata, handle, allow_unicode=True, sort_keys=False)
    handle.write(f'# url: "{url}"\n')
PY

ERRORS="$("${PYTHON}" - "${PYTHON_SCRIPTS_DIR}" "${OUT_DIR}/meta.yaml" <<'PY'
import sys

scripts_dir, meta_path = sys.argv[1:3]
sys.path.insert(0, scripts_dir)

from metadata_validator import validate_source_meta

for error in validate_source_meta(meta_path):
    print(error)
PY
)"
if [[ -n "${ERRORS}" ]]; then
  echo "Error: meta.yaml validation failed:" >&2
  echo "${ERRORS}" >&2
  exit 1
fi

GITIGNORE="${KB_ROOT}/.gitignore"
for pattern in "*.mp3" "*.wav" "*.m4a" "*.ogg" "*.flac"; do
  if [[ ! -f "${GITIGNORE}" ]] || ! grep -qxF "${pattern}" "${GITIGNORE}"; then
    echo "${pattern}" >> "${GITIGNORE}"
  fi
done

echo "Done. Output written to ${OUT_DIR}"
