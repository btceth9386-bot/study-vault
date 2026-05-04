#!/usr/bin/env bats

# Integration tests for the Ingest Pipeline scripts.
# External services (yt-dlp, Whisper API, pdftotext, deepwiki-to-md) are replaced
# with mock executables placed on PATH before each test.

setup() {
  export REPO_ROOT="${BATS_TEST_DIRNAME}/../.."
  export YOUTUBE_SCRIPT="${REPO_ROOT}/_scripts/ingest-youtube.sh"
  export PDF_SCRIPT="${REPO_ROOT}/_scripts/ingest-pdf.sh"
  export DEEPWIKI_SCRIPT="${REPO_ROOT}/_scripts/ingest-deepwiki.sh"

  export TEST_TMPDIR
  TEST_TMPDIR="$(mktemp -d)"

  # Mock bin directory — prepended to PATH so mocks shadow real tools
  export MOCK_BIN="${TEST_TMPDIR}/bin"
  mkdir -p "${MOCK_BIN}"
  export PATH="${MOCK_BIN}:${PATH}"
  export DEEPWIKI_TO_MD="${MOCK_BIN}/deepwiki-to-md"

  # Fake venv python that delegates to real python3 for file_splitter
  mkdir -p "${TEST_TMPDIR}/.venv/bin"
  cat > "${TEST_TMPDIR}/.venv/bin/python3" <<'PYSHIM'
#!/usr/bin/env bash
exec python3 "$@"
PYSHIM
  chmod +x "${TEST_TMPDIR}/.venv/bin/python3"

  # Symlink _scripts into the tmp KB so relative imports work
  ln -s "${REPO_ROOT}/_scripts" "${TEST_TMPDIR}/_scripts"

  export OPENAI_API_KEY="test-key"
}

teardown() {
  rm -rf "${TEST_TMPDIR}"
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

make_mock() {
  # make_mock <name> <exit-code> [stdout-content]
  local name="$1" code="$2" body="${3:-}"
  cat > "${MOCK_BIN}/${name}" <<MOCK
#!/usr/bin/env bash
echo "${body}"
exit ${code}
MOCK
  chmod +x "${MOCK_BIN}/${name}"
}

# ---------------------------------------------------------------------------
# ingest-youtube.sh — subtitle path
# ---------------------------------------------------------------------------

@test "ingest-youtube: subtitle path creates expected output files" {
  # yt-dlp succeeds and writes a stub SRT file
  cat > "${MOCK_BIN}/yt-dlp" <<'MOCK'
#!/usr/bin/env bash
# Detect subtitle download invocation and write a stub SRT
if [[ "$*" == *"--write-sub"* ]]; then
  OUTPUT_PATTERN=""
  for arg in "$@"; do
    if [[ "$prev" == "--output" ]]; then OUTPUT_PATTERN="$arg"; fi
    prev="$arg"
  done
  echo "1
00:00:01,000 --> 00:00:03,000
Hello world

" > "${OUTPUT_PATTERN}.en.srt"
fi
exit 0
MOCK
  chmod +x "${MOCK_BIN}/yt-dlp"

  # Mock whisper_transcribe.py CLI (srt-to-md subcommand)
  cat > "${MOCK_BIN}/whisper_transcribe_mock" <<'MOCK'
#!/usr/bin/env bash
echo "Hello world"
MOCK

  # Patch the script to use our mock python for whisper_transcribe
  # by providing a fake .venv/bin/python3 that handles the srt-to-md call
  cat > "${TEST_TMPDIR}/.venv/bin/python3" <<'PYSHIM'
#!/usr/bin/env bash
# If called as whisper_transcribe.py srt-to-md <file>, output mock transcript
if [[ "$*" == *"srt-to-md"* ]]; then
  echo "Hello world"
  exit 0
fi
exec python3 "$@"
PYSHIM
  chmod +x "${TEST_TMPDIR}/.venv/bin/python3"

  run bash -c "cd '${TEST_TMPDIR}' && bash '${YOUTUBE_SCRIPT}' 'https://youtube.com/watch?v=abc123' '${TEST_TMPDIR}'"
  [ "${status}" -eq 0 ]

  SLUG="abc123"
  OUT="${TEST_TMPDIR}/sources/videos/${SLUG}"
  [ -f "${OUT}/transcript.md" ]
  [ -f "${OUT}/meta.yaml" ]
  [ -f "${OUT}/highlights.md" ]

  run grep "type: video" "${OUT}/meta.yaml"
  [ "${status}" -eq 0 ]

  run grep "url: \"https://youtube.com/watch?v=abc123\"" "${OUT}/meta.yaml"
  [ "${status}" -eq 0 ]
}

@test "ingest-youtube: Whisper fallback path when no subtitles available" {
  # yt-dlp: subtitle download produces no SRT; audio download succeeds
  cat > "${MOCK_BIN}/yt-dlp" <<'MOCK'
#!/usr/bin/env bash
if [[ "$*" == *"--write-sub"* ]]; then
  # No subtitle files written — simulate unavailable subtitles
  exit 0
fi
# Audio download: create a stub audio file
for arg in "$@"; do
  if [[ "$prev" == "--output" ]]; then
    touch "$arg"
  fi
  prev="$arg"
done
exit 0
MOCK
  chmod +x "${MOCK_BIN}/yt-dlp"

  # Mock python3 for both transcribe and srt-to-md
  cat > "${TEST_TMPDIR}/.venv/bin/python3" <<'PYSHIM'
#!/usr/bin/env bash
if [[ "$*" == *"transcribe"* ]]; then
  echo "1
00:00:01,000 --> 00:00:02,000
Whisper transcript"
  exit 0
fi
if [[ "$*" == *"srt-to-md"* ]]; then
  echo "Whisper transcript"
  exit 0
fi
exec python3 "$@"
PYSHIM
  chmod +x "${TEST_TMPDIR}/.venv/bin/python3"

  run bash -c "cd '${TEST_TMPDIR}' && bash '${YOUTUBE_SCRIPT}' 'https://youtube.com/watch?v=whisper1' '${TEST_TMPDIR}'"
  [ "${status}" -eq 0 ]

  SLUG="whisper1"
  OUT="${TEST_TMPDIR}/sources/videos/${SLUG}"
  [ -f "${OUT}/transcript.md" ]
  [ -f "${OUT}/meta.yaml" ]
  [ -f "${OUT}/highlights.md" ]
}

@test "ingest-youtube: fails when OPENAI_API_KEY is unset" {
  make_mock yt-dlp 0 ""
  unset OPENAI_API_KEY
  run bash -c "cd '${TEST_TMPDIR}' && bash '${YOUTUBE_SCRIPT}' 'https://youtube.com/watch?v=x' '${TEST_TMPDIR}'"
  [ "${status}" -ne 0 ]
  [[ "${output}" == *"OPENAI_API_KEY"* ]]
}

@test "ingest-youtube: fails when yt-dlp is not installed" {
  # No yt-dlp mock created — if real yt-dlp is present, skip this test
  if command -v yt-dlp &>/dev/null && [[ "$(command -v yt-dlp)" != "${MOCK_BIN}/yt-dlp" ]]; then
    skip "real yt-dlp is installed; cannot test missing-tool path"
  fi

  run bash -c "cd '${TEST_TMPDIR}' && bash '${YOUTUBE_SCRIPT}' 'https://youtube.com/watch?v=x' '${TEST_TMPDIR}'"
  [ "${status}" -ne 0 ]
  [[ "${output}" == *"yt-dlp"* ]]
}

# ---------------------------------------------------------------------------
# ingest-pdf.sh — conversion and large file splitting
# ---------------------------------------------------------------------------

@test "ingest-pdf: small PDF creates notes.md and meta.yaml" {
  STUB_PDF="${TEST_TMPDIR}/test-paper.pdf"
  echo "%PDF-1.4 stub" > "$STUB_PDF"

  # pdftotext is called as: pdftotext <input> <output-file>
  cat > "${MOCK_BIN}/pdftotext" <<'MOCK'
#!/usr/bin/env bash
echo "# Test Paper

This is the extracted text." > "$2"
exit 0
MOCK
  chmod +x "${MOCK_BIN}/pdftotext"

  run bash -c "cd '${REPO_ROOT}' && bash '${PDF_SCRIPT}' '${STUB_PDF}' papers"
  [ "${status}" -eq 0 ]

  SLUG="test-paper"
  OUT="${REPO_ROOT}/sources/papers/${SLUG}"
  [ -f "${OUT}/notes.md" ]
  [ -f "${OUT}/meta.yaml" ]

  run grep "type: paper" "${OUT}/meta.yaml"
  [ "${status}" -eq 0 ]

  # Cleanup
  rm -rf "${OUT}"
}

@test "ingest-pdf: large PDF is split into multiple part files" {
  STUB_PDF="${TEST_TMPDIR}/big-paper.pdf"
  echo "%PDF-1.4 stub" > "$STUB_PDF"

  # pdftotext writes ~1.1 MB of text to the output file
  cat > "${MOCK_BIN}/pdftotext" <<'MOCK'
#!/usr/bin/env bash
python3 -c "print('# Section\n\n' + ('word ' * 200 + '\n\n') * 1100)" > "$2"
exit 0
MOCK
  chmod +x "${MOCK_BIN}/pdftotext"

  run bash -c "cd '${REPO_ROOT}' && bash '${PDF_SCRIPT}' '${STUB_PDF}' papers"
  [ "${status}" -eq 0 ]

  SLUG="big-paper"
  OUT="${REPO_ROOT}/sources/papers/${SLUG}"
  [ ! -f "${OUT}/notes.md" ]
  run ls "${OUT}"/notes-part*.md
  [ "${status}" -eq 0 ]

  # Cleanup
  rm -rf "${OUT}"
}

@test "ingest-pdf: fails when neither pdftotext nor marker is installed" {
  STUB_PDF="${TEST_TMPDIR}/test.pdf"
  echo "%PDF stub" > "$STUB_PDF"

  if command -v pdftotext &>/dev/null || command -v marker &>/dev/null; then
    skip "pdftotext or marker is installed; cannot test missing-tool path"
  fi

  run bash -c "bash '${PDF_SCRIPT}' '${STUB_PDF}' papers"
  [ "${status}" -ne 0 ]
  [[ "${output}" == *"pdftotext"* ]] || [[ "${output}" == *"marker"* ]]
}

@test "ingest-pdf: fails when PDF file does not exist" {
  make_mock pdftotext 0 "text"
  run bash -c "bash '${PDF_SCRIPT}' '/nonexistent/file.pdf' papers"
  [ "${status}" -ne 0 ]
  [[ "${output}" == *"not found"* ]]
}

# ---------------------------------------------------------------------------
# ingest-deepwiki.sh — success and failure paths
# ---------------------------------------------------------------------------

@test "ingest-deepwiki: success path creates expected output structure" {
  # Mock deepwiki-to-md to create a stub snapshot file
  cat > "${MOCK_BIN}/deepwiki-to-md" <<'MOCK'
#!/usr/bin/env bash
# Find --path argument and create a stub markdown file there
if [[ "$*" == *"--help"* ]]; then
  exit 0
fi
prev=""
for arg in "$@"; do
  if [[ "$prev" == "--path" ]]; then
    mkdir -p "$arg"
    echo "# Repo Wiki\n\nThis is the wiki content." > "${arg}/index.md"
  fi
  prev="$arg"
done
exit 0
MOCK
  chmod +x "${MOCK_BIN}/deepwiki-to-md"

  run bash -c "cd '${TEST_TMPDIR}' && bash '${DEEPWIKI_SCRIPT}' 'https://github.com/user/myrepo' '${TEST_TMPDIR}'"
  [ "${status}" -eq 0 ]

  OUT="${TEST_TMPDIR}/sources/repos/user-myrepo"
  [ -d "${OUT}/deepwiki-snapshot" ]
  [ -f "${OUT}/notes.md" ]
  [ -f "${OUT}/meta.yaml" ]

  run grep "type: repo" "${OUT}/meta.yaml"
  [ "${status}" -eq 0 ]

  run grep "url: https://github.com/user/myrepo" "${OUT}/meta.yaml"
  [ "${status}" -eq 0 ]
}

@test "ingest-deepwiki: accepts deepwiki.com URL directly" {
  cat > "${MOCK_BIN}/deepwiki-to-md" <<'MOCK'
#!/usr/bin/env bash
if [[ "$*" == *"--help"* ]]; then
  exit 0
fi
prev=""
for arg in "$@"; do
  if [[ "$prev" == "--path" ]]; then
    mkdir -p "$arg"
    echo "# Wiki" > "${arg}/index.md"
  fi
  prev="$arg"
done
exit 0
MOCK
  chmod +x "${MOCK_BIN}/deepwiki-to-md"

  run bash -c "cd '${TEST_TMPDIR}' && bash '${DEEPWIKI_SCRIPT}' 'https://deepwiki.com/user/myrepo' '${TEST_TMPDIR}'"
  [ "${status}" -eq 0 ]

  OUT="${TEST_TMPDIR}/sources/repos/user-myrepo"
  [ -f "${OUT}/meta.yaml" ]
}

@test "ingest-deepwiki: failure path prompts user to trigger wiki creation" {
  # deepwiki-to-md fails with a generic error (wiki not yet built)
  cat > "${MOCK_BIN}/deepwiki-to-md" <<'MOCK'
#!/usr/bin/env bash
if [[ "$*" == *"--help"* ]]; then
  exit 0
fi
echo "wiki not found" >&2
exit 1
MOCK
  chmod +x "${MOCK_BIN}/deepwiki-to-md"

  run bash -c "cd '${TEST_TMPDIR}' && bash '${DEEPWIKI_SCRIPT}' 'https://github.com/user/newrepo' '${TEST_TMPDIR}'"
  [ "${status}" -ne 0 ]
  [[ "${output}" == *"deepwiki.com"* ]]
}

@test "ingest-deepwiki: failure path reports private repo error" {
  cat > "${MOCK_BIN}/deepwiki-to-md" <<'MOCK'
#!/usr/bin/env bash
if [[ "$*" == *"--help"* ]]; then
  exit 0
fi
echo "private repository not supported" >&2
exit 1
MOCK
  chmod +x "${MOCK_BIN}/deepwiki-to-md"

  run bash -c "cd '${TEST_TMPDIR}' && bash '${DEEPWIKI_SCRIPT}' 'https://github.com/user/privaterepo' '${TEST_TMPDIR}'"
  [ "${status}" -ne 0 ]
  [[ "${output}" == *"private"* ]]
}

@test "ingest-deepwiki: fails when deepwiki-to-md is not installed" {
  # Skip if deepwiki-to-md is actually installed
  if command -v deepwiki-to-md &>/dev/null; then
    skip "deepwiki-to-md is installed; cannot test missing-tool path"
  fi

  run bash -c "cd '${TEST_TMPDIR}' && bash '${DEEPWIKI_SCRIPT}' 'https://github.com/user/repo' '${TEST_TMPDIR}'"
  [ "${status}" -ne 0 ]
  [[ "${output}" == *"deepwiki-to-md"* ]]
}
