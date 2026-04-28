#!/usr/bin/env bats

setup() {
  export REPO_ROOT="${BATS_TEST_DIRNAME}/../.."
  export SCRIPT_PATH="${REPO_ROOT}/_scripts/ingest-pdf.sh"
  export TEST_TMPDIR
  TEST_TMPDIR="$(mktemp -d)"

  # Minimal KB structure
  mkdir -p "${TEST_TMPDIR}/kb/_scripts"
  mkdir -p "${TEST_TMPDIR}/kb/sources/papers"
  mkdir -p "${TEST_TMPDIR}/kb/sources/books"
  mkdir -p "${TEST_TMPDIR}/kb/sources/articles"
  touch "${TEST_TMPDIR}/kb/.gitignore"

  # Stub venv python that delegates to real python3
  mkdir -p "${TEST_TMPDIR}/kb/.venv/bin"
  cat > "${TEST_TMPDIR}/kb/.venv/bin/python3" <<'PYSHIM'
#!/usr/bin/env bash
exec python3 "$@"
PYSHIM
  chmod +x "${TEST_TMPDIR}/kb/.venv/bin/python3"

  # Copy file_splitter so the script can import it
  cp "${REPO_ROOT}/_scripts/file_splitter.py" "${TEST_TMPDIR}/kb/_scripts/file_splitter.py"

  # Create a small sample PDF text (we mock pdftotext, so just need the file)
  echo "sample pdf content" > "${TEST_TMPDIR}/sample.pdf"

  # Mock pdftotext: writes fixed content to the output file
  mkdir -p "${TEST_TMPDIR}/bin"
  cat > "${TEST_TMPDIR}/bin/pdftotext" <<'MOCK'
#!/usr/bin/env bash
# args: <input.pdf> <output.txt>
echo "This is the extracted PDF text." > "$2"
MOCK
  chmod +x "${TEST_TMPDIR}/bin/pdftotext"

  export PATH="${TEST_TMPDIR}/bin:${PATH}"
}

teardown() {
  rm -rf "${TEST_TMPDIR}"
}

# Helper: run the script with KB_ROOT overridden via symlink trick
run_ingest() {
  # Temporarily symlink _scripts inside the test KB so SCRIPT_DIR resolves correctly
  ln -sf "${REPO_ROOT}/_scripts/file_splitter.py" "${TEST_TMPDIR}/kb/_scripts/file_splitter.py" 2>/dev/null || true

  # We need the script to treat TEST_TMPDIR/kb as KB_ROOT.
  # Copy the script into the test KB _scripts dir so SCRIPT_DIR points there.
  cp "${SCRIPT_PATH}" "${TEST_TMPDIR}/kb/_scripts/ingest-pdf.sh"
  chmod +x "${TEST_TMPDIR}/kb/_scripts/ingest-pdf.sh"

  run "${TEST_TMPDIR}/kb/_scripts/ingest-pdf.sh" "$@"
}

@test "ingest-pdf creates sources/<type>/<slug>/ directory" {
  run_ingest "${TEST_TMPDIR}/sample.pdf" papers
  [ "${status}" -eq 0 ]
  [ -d "${TEST_TMPDIR}/kb/sources/papers/sample" ]
}

@test "ingest-pdf writes meta.yaml with required fields" {
  run_ingest "${TEST_TMPDIR}/sample.pdf" papers
  [ "${status}" -eq 0 ]

  META="${TEST_TMPDIR}/kb/sources/papers/sample/meta.yaml"
  [ -f "${META}" ]

  run grep -F "type: paper" "${META}"
  [ "${status}" -eq 0 ]

  run grep -F "title: sample" "${META}"
  [ "${status}" -eq 0 ]

  run grep -F "status: processed" "${META}"
  [ "${status}" -eq 0 ]

  run grep -E "^date_added: [0-9]{4}-[0-9]{2}-[0-9]{2}" "${META}"
  [ "${status}" -eq 0 ]
}

@test "ingest-pdf meta.yaml passes metadata_validator" {
  run_ingest "${TEST_TMPDIR}/sample.pdf" papers
  [ "${status}" -eq 0 ]

  META="${TEST_TMPDIR}/kb/sources/papers/sample/meta.yaml"
  run python3 - <<PYEOF
import sys
sys.path.insert(0, "${REPO_ROOT}/_scripts")
from metadata_validator import validate_source_meta
errors = validate_source_meta("${META}")
if errors:
    print("Validation errors:", errors)
    sys.exit(1)
PYEOF
  [ "${status}" -eq 0 ]
}

@test "ingest-pdf writes notes.md with converted content" {
  run_ingest "${TEST_TMPDIR}/sample.pdf" papers
  [ "${status}" -eq 0 ]

  NOTES="${TEST_TMPDIR}/kb/sources/papers/sample/notes.md"
  [ -f "${NOTES}" ]

  run grep -F "extracted PDF text" "${NOTES}"
  [ "${status}" -eq 0 ]
}

@test "ingest-pdf supports books type" {
  run_ingest "${TEST_TMPDIR}/sample.pdf" books
  [ "${status}" -eq 0 ]
  [ -d "${TEST_TMPDIR}/kb/sources/books/sample" ]

  META="${TEST_TMPDIR}/kb/sources/books/sample/meta.yaml"
  run grep -F "type: book" "${META}"
  [ "${status}" -eq 0 ]
}

@test "ingest-pdf supports articles type" {
  run_ingest "${TEST_TMPDIR}/sample.pdf" articles
  [ "${status}" -eq 0 ]
  [ -d "${TEST_TMPDIR}/kb/sources/articles/sample" ]

  META="${TEST_TMPDIR}/kb/sources/articles/sample/meta.yaml"
  run grep -F "type: article" "${META}"
  [ "${status}" -eq 0 ]
}

@test "ingest-pdf adds PDF path to .gitignore when not already excluded" {
  # Remove the blanket *.pdf rule so the specific path gets added
  echo "" > "${TEST_TMPDIR}/kb/.gitignore"

  run_ingest "${TEST_TMPDIR}/sample.pdf" papers
  [ "${status}" -eq 0 ]

  run grep -F "sample.pdf" "${TEST_TMPDIR}/kb/.gitignore"
  [ "${status}" -eq 0 ]
}

@test "ingest-pdf does not duplicate gitignore entry when *.pdf already present" {
  echo "*.pdf" > "${TEST_TMPDIR}/kb/.gitignore"

  run_ingest "${TEST_TMPDIR}/sample.pdf" papers
  [ "${status}" -eq 0 ]

  # Count lines containing sample.pdf — should be 0 (covered by *.pdf glob)
  count="$(grep -c "sample.pdf" "${TEST_TMPDIR}/kb/.gitignore" || true)"
  [ "${count}" -eq 0 ]
}

@test "ingest-pdf splits content over 1 MB into multiple part files" {
  # Mock pdftotext to produce >1 MiB of text (1048576 bytes)
  cat > "${TEST_TMPDIR}/bin/pdftotext" <<'MOCK'
#!/usr/bin/env bash
python3 -c "print('# Section\n\n' + 'word ' * 220000)" > "$2"
MOCK
  chmod +x "${TEST_TMPDIR}/bin/pdftotext"

  run_ingest "${TEST_TMPDIR}/sample.pdf" papers
  [ "${status}" -eq 0 ]

  # At least two part files should exist
  part_count="$(ls "${TEST_TMPDIR}/kb/sources/papers/sample/notes-part"*.md 2>/dev/null | wc -l | tr -d ' ')"
  [ "${part_count}" -ge 2 ]
}

@test "ingest-pdf exits non-zero when PDF file does not exist" {
  run_ingest "${TEST_TMPDIR}/nonexistent.pdf" papers
  [ "${status}" -ne 0 ]
}

@test "ingest-pdf exits non-zero when type is invalid" {
  run_ingest "${TEST_TMPDIR}/sample.pdf" videos
  [ "${status}" -ne 0 ]
}

@test "ingest-pdf exits non-zero when no converter is available" {
  # Remove pdftotext from PATH
  rm "${TEST_TMPDIR}/bin/pdftotext"

  run_ingest "${TEST_TMPDIR}/sample.pdf" papers
  [ "${status}" -ne 0 ]
  [[ "${output}" == *"pdftotext"* ]] || [[ "${output}" == *"marker"* ]]
}
