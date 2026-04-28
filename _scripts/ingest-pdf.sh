#!/usr/bin/env bash
# ingest-pdf.sh — Ingest a PDF into the knowledge base.
#
# Usage: ingest-pdf.sh <pdf-path> [type]
#   type: papers | books | articles  (default: papers)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KB_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# ── argument validation ────────────────────────────────────────────────────────
if [[ $# -lt 1 ]]; then
  echo "Usage: ingest-pdf.sh <pdf-path> [papers|books|articles]" >&2
  exit 1
fi

PDF_PATH="$1"
SOURCE_TYPE="${2:-papers}"

if [[ ! -f "${PDF_PATH}" ]]; then
  echo "Error: file not found: ${PDF_PATH}" >&2
  exit 1
fi

case "${SOURCE_TYPE}" in
  papers|books|articles) ;;
  *)
    echo "Error: type must be papers, books, or articles (got: ${SOURCE_TYPE})" >&2
    exit 1
    ;;
esac

# ── dependency check ───────────────────────────────────────────────────────────
CONVERTER=""
if command -v pdftotext &>/dev/null; then
  CONVERTER="pdftotext"
elif command -v marker &>/dev/null; then
  CONVERTER="marker"
else
  echo "Error: neither pdftotext nor marker is installed." >&2
  echo "  Install pdftotext: brew install poppler  (macOS) / apt install poppler-utils (Debian)" >&2
  echo "  Install marker:    pip install marker-pdf" >&2
  exit 1
fi

# ── derive slug from filename ──────────────────────────────────────────────────
BASENAME="$(basename "${PDF_PATH}" .pdf)"
SLUG="$(echo "${BASENAME}" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//;s/-$//')"
TODAY="$(date +%Y-%m-%d)"

DEST_DIR="${KB_ROOT}/sources/${SOURCE_TYPE}/${SLUG}"
mkdir -p "${DEST_DIR}"

# ── convert PDF → plain text ───────────────────────────────────────────────────
TMP_TXT="$(mktemp /tmp/ingest-pdf-XXXXXX.txt)"
trap 'rm -f "${TMP_TXT}"' EXIT

if [[ "${CONVERTER}" == "pdftotext" ]]; then
  pdftotext "${PDF_PATH}" "${TMP_TXT}"
else
  # marker outputs to a directory; capture stdout instead
  marker "${PDF_PATH}" --output_format markdown 2>/dev/null > "${TMP_TXT}" \
    || { echo "Error: marker failed to convert ${PDF_PATH}" >&2; exit 1; }
fi

CONTENT="$(cat "${TMP_TXT}")"

if [[ -z "${CONTENT}" ]]; then
  echo "Error: PDF conversion produced empty output. Check that the PDF is not scanned-only." >&2
  exit 1
fi

# ── split if > 1 MB ────────────────────────────────────────────────────────────
BYTE_SIZE="$(echo -n "${CONTENT}" | wc -c | tr -d ' ')"
ONE_MB=1048576

if [[ "${BYTE_SIZE}" -gt "${ONE_MB}" ]]; then
  echo "Content exceeds 1 MB (${BYTE_SIZE} bytes) — splitting…"
  "${KB_ROOT}/.venv/bin/python3" - <<PYEOF
import sys
sys.path.insert(0, "${SCRIPT_DIR}")
from file_splitter import split_markdown

content = open("${TMP_TXT}", encoding="utf-8").read()
chunks = split_markdown(content)
for chunk in chunks:
    part_path = "${DEST_DIR}/notes-part{:02d}.md".format(chunk.part_number)
    with open(part_path, "w", encoding="utf-8") as f:
        f.write(chunk)
    print(f"  wrote {part_path}")
PYEOF
  NOTES_FILE="${DEST_DIR}/notes-part01.md"
else
  NOTES_FILE="${DEST_DIR}/notes.md"
  printf '%s\n' "${CONTENT}" > "${NOTES_FILE}"
fi

# ── write meta.yaml ────────────────────────────────────────────────────────────
META_FILE="${DEST_DIR}/meta.yaml"
cat > "${META_FILE}" <<YAML
type: ${SOURCE_TYPE%s}
title: ${BASENAME}
language: en
date_consumed: ${TODAY}
date_added: ${TODAY}
status: processed
tags: []
related_concepts: []
YAML

# Strip trailing 's' for type field (papers→paper, books→book, articles→article)
YAML_TYPE="${SOURCE_TYPE%s}"
sed -i.bak "s/^type: .*/type: ${YAML_TYPE}/" "${META_FILE}" && rm -f "${META_FILE}.bak"

# ── add original PDF to .gitignore ─────────────────────────────────────────────
GITIGNORE="${KB_ROOT}/.gitignore"
ABS_PDF="$(cd "$(dirname "${PDF_PATH}")" && pwd)/$(basename "${PDF_PATH}")"
REL_PDF="${ABS_PDF#${KB_ROOT}/}"

if [[ -f "${GITIGNORE}" ]]; then
  if ! grep -qxF "${REL_PDF}" "${GITIGNORE}" && ! grep -qxF "*.pdf" "${GITIGNORE}"; then
    echo "${REL_PDF}" >> "${GITIGNORE}"
    echo "Added ${REL_PDF} to .gitignore"
  fi
fi

# ── done ───────────────────────────────────────────────────────────────────────
echo "Ingested: ${DEST_DIR}"
echo "  meta.yaml : ${META_FILE}"
echo "  notes     : ${NOTES_FILE}"
echo ""
echo "Next step: run the new-source prompt against ${DEST_DIR}"
