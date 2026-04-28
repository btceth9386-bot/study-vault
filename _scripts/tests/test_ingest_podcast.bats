#!/usr/bin/env bats

setup() {
  export REPO_ROOT="${BATS_TEST_DIRNAME}/../.."
  export TEST_TMPDIR
  TEST_TMPDIR="$(mktemp -d)"

  mkdir -p "${TEST_TMPDIR}/sources/podcasts" "${TEST_TMPDIR}/_scripts"
  touch "${TEST_TMPDIR}/.gitignore"
  cp -r "${REPO_ROOT}/_scripts/." "${TEST_TMPDIR}/_scripts/"

  # Stub whisper_transcribe so no real API call is made
  cat > "${TEST_TMPDIR}/_scripts/whisper_transcribe.py" <<'PYSTUB'
def transcribe(audio_path, language="auto"):
    return "1\n00:00:00,000 --> 00:00:01,000\nHello podcast world\n\n"

def srt_to_markdown(srt_path):
    return "Hello podcast world"
PYSTUB

  # Patch KB_ROOT and PYTHON in the script for test isolation
  export PATCHED_SCRIPT="${TEST_TMPDIR}/_scripts/ingest-podcast.sh"
  sed \
    -e "s|KB_ROOT=\"\$(cd \"\${SCRIPT_DIR}/..\" && pwd)\"|KB_ROOT=\"${TEST_TMPDIR}\"|" \
    -e "s|PYTHON=\"\${KB_ROOT}/.venv/bin/python3\"|PYTHON=\"python3\"|" \
    "${REPO_ROOT}/_scripts/ingest-podcast.sh" > "${PATCHED_SCRIPT}"
  chmod +x "${PATCHED_SCRIPT}"

  export OPENAI_API_KEY="test-key"
}

teardown() {
  rm -rf "${TEST_TMPDIR}"
}

@test "ingest-podcast exits 1 when no arguments given" {
  run bash "${PATCHED_SCRIPT}"
  [ "${status}" -eq 1 ]
}

@test "ingest-podcast exits 1 when OPENAI_API_KEY is not set" {
  local audio="${TEST_TMPDIR}/episode.mp3"
  touch "${audio}"
  run env -u OPENAI_API_KEY bash "${PATCHED_SCRIPT}" "${audio}"
  [ "${status}" -eq 1 ]
  echo "${output}" | grep -qi "OPENAI_API_KEY"
}

@test "ingest-podcast creates output directory structure" {
  local audio="${TEST_TMPDIR}/my-episode.mp3"
  touch "${audio}"
  run bash "${PATCHED_SCRIPT}" "${audio}"
  [ "${status}" -eq 0 ]
  [ -d "${TEST_TMPDIR}/sources/podcasts/my-episode" ]
  [ -f "${TEST_TMPDIR}/sources/podcasts/my-episode/meta.yaml" ]
  [ -f "${TEST_TMPDIR}/sources/podcasts/my-episode/transcript.md" ]
  [ -f "${TEST_TMPDIR}/sources/podcasts/my-episode/highlights.md" ]
}

@test "ingest-podcast meta.yaml passes metadata_validator" {
  local audio="${TEST_TMPDIR}/test-show.mp3"
  touch "${audio}"
  run bash "${PATCHED_SCRIPT}" "${audio}"
  [ "${status}" -eq 0 ]

  run "${REPO_ROOT}/.venv/bin/python3" -c "
import sys
sys.path.insert(0, '${REPO_ROOT}')
from _scripts.metadata_validator import validate_source_meta
errors = validate_source_meta('${TEST_TMPDIR}/sources/podcasts/test-show/meta.yaml')
assert errors == [], errors
"
  [ "${status}" -eq 0 ]
}

@test "ingest-podcast transcript.md contains transcribed text" {
  local audio="${TEST_TMPDIR}/my-podcast.mp3"
  touch "${audio}"
  run bash "${PATCHED_SCRIPT}" "${audio}"
  [ "${status}" -eq 0 ]
  run grep -F "Hello podcast world" "${TEST_TMPDIR}/sources/podcasts/my-podcast/transcript.md"
  [ "${status}" -eq 0 ]
}

@test "ingest-podcast adds audio patterns to .gitignore" {
  local audio="${TEST_TMPDIR}/episode2.mp3"
  touch "${audio}"
  run bash "${PATCHED_SCRIPT}" "${audio}"
  [ "${status}" -eq 0 ]
  for pattern in "*.mp3" "*.wav" "*.m4a" "*.ogg" "*.flac"; do
    run grep -xF "${pattern}" "${TEST_TMPDIR}/.gitignore"
    [ "${status}" -eq 0 ]
  done
}

@test "ingest-podcast exits 1 if output directory already exists" {
  local audio="${TEST_TMPDIR}/duplicate.mp3"
  touch "${audio}"
  mkdir -p "${TEST_TMPDIR}/sources/podcasts/duplicate"
  run bash "${PATCHED_SCRIPT}" "${audio}"
  [ "${status}" -eq 1 ]
  echo "${output}" | grep -qi "already exists"
}

@test "ingest-podcast does not add duplicate audio patterns to .gitignore" {
  local audio="${TEST_TMPDIR}/ep3.mp3"
  touch "${audio}"
  echo "*.mp3" >> "${TEST_TMPDIR}/.gitignore"
  run bash "${PATCHED_SCRIPT}" "${audio}"
  [ "${status}" -eq 0 ]
  count="$(grep -cxF "*.mp3" "${TEST_TMPDIR}/.gitignore")"
  [ "${count}" -eq 1 ]
}
