#!/usr/bin/env bats
bats_require_minimum_version 1.5.0

setup() {
  export REPO_ROOT="${BATS_TEST_DIRNAME}/../.."
  export SCRIPT_PATH="${REPO_ROOT}/_scripts/ingest-youtube.sh"
  export TEST_TMPDIR
  TEST_TMPDIR="$(mktemp -d)"

  # Create a minimal KB structure
  mkdir -p "${TEST_TMPDIR}/kb/_scripts"
  mkdir -p "${TEST_TMPDIR}/kb/sources/videos"

  # Create a mock venv python that delegates to the repo's real venv python
  mkdir -p "${TEST_TMPDIR}/kb/.venv/bin"
  REAL_PYTHON="${REPO_ROOT}/.venv/bin/python3"
  cat > "${TEST_TMPDIR}/kb/.venv/bin/python3" <<PYEOF
#!/usr/bin/env bash
exec "${REAL_PYTHON}" "\$@"
PYEOF
  chmod +x "${TEST_TMPDIR}/kb/.venv/bin/python3"

  # Stub yt-dlp in a local bin dir that takes priority
  mkdir -p "${TEST_TMPDIR}/bin"
  export PATH="${TEST_TMPDIR}/bin:${PATH}"

  export OPENAI_API_KEY="test-key"
}

teardown() {
  rm -rf "${TEST_TMPDIR}"
}

# Helper: create a stub yt-dlp that writes a fake SRT when --write-subs is used
_stub_ytdlp_with_subs() {
  cat > "${TEST_TMPDIR}/bin/yt-dlp" <<'STUB'
#!/usr/bin/env bash
# Minimal yt-dlp stub
if [[ "$*" == *"--get-title"* ]]; then
  echo "Test Video Title"
  exit 0
fi
if [[ "$*" == *"--write-subs"* ]]; then
  # Find the -o argument and derive the output path
  output_template=""
  for i in "$@"; do
    if [[ "${prev}" == "-o" ]]; then output_template="${i}"; fi
    prev="${i}"
  done
  # Write a fake SRT next to the template
  dir="$(dirname "${output_template}")"
  cat > "${dir}/video.en.srt" <<SRT
1
00:00:00,000 --> 00:00:02,000
Hello from subtitle

2
00:00:03,000 --> 00:00:05,000
Second line

SRT
  exit 0
fi
exit 0
STUB
  chmod +x "${TEST_TMPDIR}/bin/yt-dlp"
}

# Helper: create a stub yt-dlp that has NO subtitles, but downloads audio
_stub_ytdlp_no_subs() {
  cat > "${TEST_TMPDIR}/bin/yt-dlp" <<'STUB'
#!/usr/bin/env bash
if [[ "$*" == *"--get-title"* ]]; then
  echo "Whisper Video"
  exit 0
fi
if [[ "$*" == *"--write-subs"* ]] || [[ "$*" == *"--write-auto-subs"* ]]; then
  # No subtitles — exit 0 but write nothing
  exit 0
fi
if [[ "$*" == *"--extract-audio"* ]]; then
  # Find output template
  output_template=""
  for i in "$@"; do
    if [[ "${prev}" == "-o" ]]; then output_template="${i}"; fi
    prev="${i}"
  done
  dir="$(dirname "${output_template}")"
  # Write a tiny fake mp3
  echo "fake-audio" > "${dir}/audio.mp3"
  exit 0
fi
exit 0
STUB
  chmod +x "${TEST_TMPDIR}/bin/yt-dlp"
}

# ── Dependency checks ────────────────────────────────────────────────────────

@test "exits with error when yt-dlp is not installed" {
  run env PATH="/usr/bin:/bin" bash "${SCRIPT_PATH}" "https://youtu.be/test" "${TEST_TMPDIR}/kb"
  [ "${status}" -eq 1 ]
  [[ "${output}" == *"yt-dlp is not installed"* ]]
}

@test "exits with error when OPENAI_API_KEY is not set" {
  _stub_ytdlp_with_subs
  run env OPENAI_API_KEY="" bash "${SCRIPT_PATH}" "https://youtu.be/test" "${TEST_TMPDIR}/kb"
  [ "${status}" -ne 0 ]
  [[ "${output}" == *"OPENAI_API_KEY"* ]]
}

@test "exits with error when no URL argument is provided" {
  run bash "${SCRIPT_PATH}"
  [ "${status}" -ne 0 ]
  [[ "${output}" == *"Usage"* ]]
}

# ── Subtitle path ────────────────────────────────────────────────────────────

@test "subtitle path: creates meta.yaml transcript.md highlights.md" {
  _stub_ytdlp_with_subs

  run bash "${SCRIPT_PATH}" "https://youtu.be/test" "${TEST_TMPDIR}/kb"
  [ "${status}" -eq 0 ]

  # Slug derived from "Test Video Title" → "test-video-title"
  SLUG="test-video-title"
  [ -f "${TEST_TMPDIR}/kb/sources/videos/${SLUG}/meta.yaml" ]
  [ -f "${TEST_TMPDIR}/kb/sources/videos/${SLUG}/transcript.md" ]
  [ -f "${TEST_TMPDIR}/kb/sources/videos/${SLUG}/highlights.md" ]
}

@test "subtitle path: meta.yaml contains required fields" {
  _stub_ytdlp_with_subs

  run bash "${SCRIPT_PATH}" "https://youtu.be/test" "${TEST_TMPDIR}/kb"
  [ "${status}" -eq 0 ]

  META="${TEST_TMPDIR}/kb/sources/videos/test-video-title/meta.yaml"
  run grep -F "type: video" "${META}"
  [ "${status}" -eq 0 ]
  run grep -F "url: https://youtu.be/test" "${META}"
  [ "${status}" -eq 0 ]
  run grep -F "status: processed" "${META}"
  [ "${status}" -eq 0 ]
}

@test "subtitle path: transcript.md contains subtitle text" {
  _stub_ytdlp_with_subs

  run bash "${SCRIPT_PATH}" "https://youtu.be/test" "${TEST_TMPDIR}/kb"
  [ "${status}" -eq 0 ]

  TRANSCRIPT="${TEST_TMPDIR}/kb/sources/videos/test-video-title/transcript.md"
  run grep -F "Hello from subtitle" "${TRANSCRIPT}"
  [ "${status}" -eq 0 ]
}

# ── Whisper fallback path ────────────────────────────────────────────────────

@test "whisper fallback: creates output files when no subtitles available" {
  _stub_ytdlp_no_subs

  # Create a stub scripts dir with whisper_transcribe stub + real metadata_validator
  mkdir -p "${TEST_TMPDIR}/stub_scripts"
  ln -sf "${REPO_ROOT}/_scripts/metadata_validator.py" "${TEST_TMPDIR}/stub_scripts/metadata_validator.py"
  cat > "${TEST_TMPDIR}/stub_scripts/whisper_transcribe.py" <<'PYSTUB'
def transcribe(audio_path, language="auto"):
    return "1\n00:00:00,000 --> 00:00:02,000\nWhisper transcribed text\n\n"

def srt_to_markdown(srt_path):
    from pathlib import Path
    import re
    TIMESTAMP_PATTERN = re.compile(r"^\s*\d{2}:\d{2}:\d{2},\d{3}\s+-->\s+\d{2}:\d{2}:\d{2},\d{3}\s*$")
    content = Path(srt_path).read_text(encoding="utf-8")
    paragraphs = []
    current = []
    expect_sequence = True
    for raw_line in content.splitlines():
        line = raw_line.rstrip("\r\n")
        normalized = line.strip()
        if not normalized:
            if current:
                paragraphs.append(" ".join(current))
                current = []
            expect_sequence = True
            continue
        if expect_sequence and normalized.isdigit():
            expect_sequence = False
            continue
        expect_sequence = False
        if TIMESTAMP_PATTERN.match(normalized):
            continue
        current.append(line)
    if current:
        paragraphs.append(" ".join(current))
    return "\n\n".join(paragraphs)
PYSTUB

  run env _INGEST_SCRIPTS_DIR="${TEST_TMPDIR}/stub_scripts" \
      bash "${SCRIPT_PATH}" "https://youtu.be/test" "${TEST_TMPDIR}/kb"
  [ "${status}" -eq 0 ]

  SLUG="whisper-video"
  [ -f "${TEST_TMPDIR}/kb/sources/videos/${SLUG}/meta.yaml" ]
  [ -f "${TEST_TMPDIR}/kb/sources/videos/${SLUG}/transcript.md" ]
  [ -f "${TEST_TMPDIR}/kb/sources/videos/${SLUG}/highlights.md" ]
}

# ── .gitignore ───────────────────────────────────────────────────────────────

@test "adds audio patterns to .gitignore if not present" {
  _stub_ytdlp_with_subs

  run bash "${SCRIPT_PATH}" "https://youtu.be/test" "${TEST_TMPDIR}/kb"
  [ "${status}" -eq 0 ]

  for pattern in "*.mp3" "*.wav" "*.m4a"; do
    run grep -xF "${pattern}" "${TEST_TMPDIR}/kb/.gitignore"
    [ "${status}" -eq 0 ]
  done
}

@test "does not duplicate audio patterns in .gitignore" {
  _stub_ytdlp_with_subs

  # Pre-populate .gitignore with the patterns
  printf "*.mp3\n*.wav\n*.m4a\n*.ogg\n*.flac\n" > "${TEST_TMPDIR}/kb/.gitignore"

  run bash "${SCRIPT_PATH}" "https://youtu.be/test" "${TEST_TMPDIR}/kb"
  [ "${status}" -eq 0 ]

  count="$(grep -c "^\*\.mp3$" "${TEST_TMPDIR}/kb/.gitignore")"
  [ "${count}" -eq 1 ]
}
