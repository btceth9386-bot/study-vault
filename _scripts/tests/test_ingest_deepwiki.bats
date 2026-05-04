#!/usr/bin/env bats

setup() {
  export REPO_ROOT="${BATS_TEST_DIRNAME}/../.."
  export SCRIPT_PATH="${REPO_ROOT}/_scripts/ingest-deepwiki.sh"
  export TEST_TMPDIR
  TEST_TMPDIR="$(mktemp -d)"

  # Create a mock deepwiki-to-md on PATH that succeeds by default
  export MOCK_BIN="${TEST_TMPDIR}/bin"
  mkdir -p "${MOCK_BIN}"
  cat > "${MOCK_BIN}/deepwiki-to-md" <<'MOCK'
#!/usr/bin/env bash
# Mock: write a sample markdown file to --path dir
if [[ "$*" == *"--help"* ]]; then
  exit 0
fi
OUTPUT_DIR=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --path) OUTPUT_DIR="$2"; shift 2 ;;
    *) shift ;;
  esac
done
mkdir -p "${OUTPUT_DIR}"
echo "# Overview" > "${OUTPUT_DIR}/overview.md"
echo "Sample wiki content." >> "${OUTPUT_DIR}/overview.md"
MOCK
  chmod +x "${MOCK_BIN}/deepwiki-to-md"
  export DEEPWIKI_TO_MD="${MOCK_BIN}/deepwiki-to-md"
  export PATH="${MOCK_BIN}:${PATH}"
}

teardown() {
  rm -rf "${TEST_TMPDIR}"
}

# ── GitHub URL conversion ──────────────────────────────────────────────────────

@test "accepts GitHub URL and converts to DeepWiki URL" {
  run "${SCRIPT_PATH}" "https://github.com/donnemartin/system-design-primer" "${TEST_TMPDIR}/kb"
  [ "${status}" -eq 0 ]
  [ -d "${TEST_TMPDIR}/kb/sources/repos/donnemartin-system-design-primer" ]
}

@test "accepts DeepWiki URL directly" {
  run "${SCRIPT_PATH}" "https://deepwiki.com/donnemartin/system-design-primer" "${TEST_TMPDIR}/kb"
  [ "${status}" -eq 0 ]
  [ -d "${TEST_TMPDIR}/kb/sources/repos/donnemartin-system-design-primer" ]
}

@test "accepts owner/repo path directly" {
  run "${SCRIPT_PATH}" "donnemartin/system-design-primer" "${TEST_TMPDIR}/kb"
  [ "${status}" -eq 0 ]
  [ -d "${TEST_TMPDIR}/kb/sources/repos/donnemartin-system-design-primer" ]
}

@test "rejects invalid URL" {
  run "${SCRIPT_PATH}" "https://example.com/foo/bar" "${TEST_TMPDIR}/kb"
  [ "${status}" -ne 0 ]
  [[ "${output}" == *"URL must be"* ]]
}

# ── Success path: directory structure ─────────────────────────────────────────

@test "success path creates meta.yaml" {
  run "${SCRIPT_PATH}" "https://github.com/donnemartin/system-design-primer" "${TEST_TMPDIR}/kb"
  [ "${status}" -eq 0 ]
  [ -f "${TEST_TMPDIR}/kb/sources/repos/donnemartin-system-design-primer/meta.yaml" ]
}

@test "success path creates notes.md" {
  run "${SCRIPT_PATH}" "https://github.com/donnemartin/system-design-primer" "${TEST_TMPDIR}/kb"
  [ "${status}" -eq 0 ]
  [ -f "${TEST_TMPDIR}/kb/sources/repos/donnemartin-system-design-primer/notes.md" ]
}

@test "success path creates deepwiki-snapshot directory" {
  run "${SCRIPT_PATH}" "https://github.com/donnemartin/system-design-primer" "${TEST_TMPDIR}/kb"
  [ "${status}" -eq 0 ]
  [ -d "${TEST_TMPDIR}/kb/sources/repos/donnemartin-system-design-primer/deepwiki-snapshot" ]
}

@test "meta.yaml contains required fields" {
  run "${SCRIPT_PATH}" "https://github.com/donnemartin/system-design-primer" "${TEST_TMPDIR}/kb"
  [ "${status}" -eq 0 ]
  META="${TEST_TMPDIR}/kb/sources/repos/donnemartin-system-design-primer/meta.yaml"
  run grep -F "type: repo" "${META}"
  [ "${status}" -eq 0 ]
  run grep -F "url: https://github.com/donnemartin/system-design-primer" "${META}"
  [ "${status}" -eq 0 ]
  run grep -F "status: processed" "${META}"
  [ "${status}" -eq 0 ]
  run grep -F "language: en" "${META}"
  [ "${status}" -eq 0 ]
}

@test "notes.md includes repo name and DeepWiki source link" {
  run "${SCRIPT_PATH}" "https://github.com/donnemartin/system-design-primer" "${TEST_TMPDIR}/kb"
  [ "${status}" -eq 0 ]
  NOTES="${TEST_TMPDIR}/kb/sources/repos/donnemartin-system-design-primer/notes.md"
  run grep -F "donnemartin/system-design-primer" "${NOTES}"
  [ "${status}" -eq 0 ]
  run grep -F "https://deepwiki.com/donnemartin/system-design-primer" "${NOTES}"
  [ "${status}" -eq 0 ]
}

# ── Failure: wiki not built ────────────────────────────────────────────────────

@test "failure when wiki not built shows prompt to visit deepwiki.com" {
  # Override mock to fail without 'private' in stderr
  cat > "${MOCK_BIN}/deepwiki-to-md" <<'MOCK'
#!/usr/bin/env bash
if [[ "$*" == *"--help"* ]]; then
  exit 0
fi
echo "wiki not found" >&2
exit 1
MOCK
  chmod +x "${MOCK_BIN}/deepwiki-to-md"

  run "${SCRIPT_PATH}" "https://github.com/some/repo" "${TEST_TMPDIR}/kb"
  [ "${status}" -ne 0 ]
  [[ "${output}" == *"deepwiki.com"* ]]
}

@test "failure when wiki not built cleans up output directory" {
  cat > "${MOCK_BIN}/deepwiki-to-md" <<'MOCK'
#!/usr/bin/env bash
if [[ "$*" == *"--help"* ]]; then
  exit 0
fi
echo "not found" >&2
exit 1
MOCK
  chmod +x "${MOCK_BIN}/deepwiki-to-md"

  run "${SCRIPT_PATH}" "https://github.com/some/repo" "${TEST_TMPDIR}/kb"
  [ "${status}" -ne 0 ]
  [ ! -d "${TEST_TMPDIR}/kb/sources/repos/some-repo" ]
}

# ── Failure: private repo ──────────────────────────────────────────────────────

@test "failure for private repo shows clear error message" {
  cat > "${MOCK_BIN}/deepwiki-to-md" <<'MOCK'
#!/usr/bin/env bash
if [[ "$*" == *"--help"* ]]; then
  exit 0
fi
echo "Error: private repository not supported" >&2
exit 1
MOCK
  chmod +x "${MOCK_BIN}/deepwiki-to-md"

  run "${SCRIPT_PATH}" "https://github.com/private/repo" "${TEST_TMPDIR}/kb"
  [ "${status}" -ne 0 ]
  [[ "${output}" == *"public"* ]]
}

# ── Dependency check ──────────────────────────────────────────────────────────

@test "exits with error when deepwiki-to-md is not installed" {
  rm "${MOCK_BIN}/deepwiki-to-md"

  run "${SCRIPT_PATH}" "https://github.com/some/repo" "${TEST_TMPDIR}/kb"
  [ "${status}" -ne 0 ]
  [[ "${output}" == *"deepwiki-to-md"* ]]
}
