#!/usr/bin/env bats

setup() {
  export REPO_ROOT="${BATS_TEST_DIRNAME}/../.."
  export SCRIPT_PATH="${REPO_ROOT}/_scripts/init-kb.sh"
  export TEST_TMPDIR
  TEST_TMPDIR="$(mktemp -d)"
}

teardown() {
  rm -rf "${TEST_TMPDIR}"
}

@test "init-kb creates the complete directory scaffold" {
  run "${SCRIPT_PATH}" "${TEST_TMPDIR}/kb"
  [ "${status}" -eq 0 ]

  required_paths=(
    "_inbox"
    "_drafts"
    "concepts"
    "concepts/examples"
    "sources"
    "sources/repos"
    "sources/videos"
    "sources/books"
    "sources/articles"
    "sources/podcasts"
    "sources/papers"
    "quiz"
    "_index"
    "topics"
    "_scripts"
    "_scripts/prompts"
  )

  for path in "${required_paths[@]}"; do
    [ -d "${TEST_TMPDIR}/kb/${path}" ]
  done
}

@test "init-kb writes example files with the expected structure" {
  run "${SCRIPT_PATH}" "${TEST_TMPDIR}/kb"
  [ "${status}" -eq 0 ]

  [ -f "${TEST_TMPDIR}/kb/README.md" ]
  [ -f "${TEST_TMPDIR}/kb/sources/articles/example-article/meta.yaml" ]
  [ -f "${TEST_TMPDIR}/kb/sources/articles/example-article/notes.md" ]
  [ -f "${TEST_TMPDIR}/kb/concepts/examples/deliberate-practice.md" ]
  [ -f "${TEST_TMPDIR}/kb/quiz/bank.json" ]
  [ -f "${TEST_TMPDIR}/kb/_index/concepts.md" ]
  [ -f "${TEST_TMPDIR}/kb/_index/topics.md" ]
  [ -f "${TEST_TMPDIR}/kb/_index/tags.md" ]
  [ -f "${TEST_TMPDIR}/kb/_scripts/prompts/new-source.md" ]

  run grep -F "Do not commit raw audio, video, large PDFs, cloned repositories" "${TEST_TMPDIR}/kb/README.md"
  [ "${status}" -eq 0 ]

  run grep -F "type: article" "${TEST_TMPDIR}/kb/sources/articles/example-article/meta.yaml"
  [ "${status}" -eq 0 ]

  run grep -F "status: processed" "${TEST_TMPDIR}/kb/sources/articles/example-article/meta.yaml"
  [ "${status}" -eq 0 ]

  run grep -F "## Knowledge Map" "${TEST_TMPDIR}/kb/sources/articles/example-article/notes.md"
  [ "${status}" -eq 0 ]

  run grep -F "id: deliberate-practice" "${TEST_TMPDIR}/kb/concepts/examples/deliberate-practice.md"
  [ "${status}" -eq 0 ]

  run grep -F "# 一句話定義" "${TEST_TMPDIR}/kb/concepts/examples/deliberate-practice.md"
  [ "${status}" -eq 0 ]

  run grep -F "\"concept_id\": \"deliberate-practice\"" "${TEST_TMPDIR}/kb/quiz/bank.json"
  [ "${status}" -eq 0 ]

  run grep -F "絕對不能建立、修改、刪除 \`concepts/\`" "${TEST_TMPDIR}/kb/_scripts/prompts/new-source.md"
  [ "${status}" -eq 0 ]

  run grep -F "merge_candidate" "${TEST_TMPDIR}/kb/_scripts/prompts/new-source.md"
  [ "${status}" -eq 0 ]
}

@test "init-kb writes the required gitignore exclusions" {
  run "${SCRIPT_PATH}" "${TEST_TMPDIR}/kb"
  [ "${status}" -eq 0 ]
  [ -f "${TEST_TMPDIR}/kb/.gitignore" ]

  required_rules=(
    "*.mp3"
    "*.wav"
    "*.m4a"
    "*.mp4"
    "*.mkv"
    "*.webm"
    "*.pdf"
    "*.epub"
    "sources/repos/*/clone/"
    "*.bin"
  )

  for rule in "${required_rules[@]}"; do
    run grep -Fx "${rule}" "${TEST_TMPDIR}/kb/.gitignore"
    [ "${status}" -eq 0 ]
  done
}
