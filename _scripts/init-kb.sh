#!/usr/bin/env bash
set -euo pipefail

target_dir="${1:-.}"

mkdir -p \
  "${target_dir}/_inbox" \
  "${target_dir}/_drafts" \
  "${target_dir}/concepts/examples" \
  "${target_dir}/sources/repos" \
  "${target_dir}/sources/videos" \
  "${target_dir}/sources/books" \
  "${target_dir}/sources/articles/example-article" \
  "${target_dir}/sources/podcasts" \
  "${target_dir}/sources/papers" \
  "${target_dir}/quiz" \
  "${target_dir}/_index" \
  "${target_dir}/topics" \
  "${target_dir}/_scripts/prompts"

cat > "${target_dir}/README.md" <<'EOF'
# Study Vault

This knowledge base stores refined text assets in Git and keeps large raw media files out of version control.

## Structure

- `_inbox/`: staging area for newly captured materials
- `_drafts/`: AI-generated concept drafts pending review
- `concepts/`: promoted concepts with frontmatter and examples
- `sources/`: processed source materials by type
- `quiz/bank.json`: spaced-repetition question bank
- `_index/`: generated concept, topic, and tag indexes

## Git Tracking

Commit Markdown, YAML, JSON, and scripts. Do not commit raw audio, video, large PDFs, cloned repositories, or other large binaries.

## First Steps

1. Add a new source under `_inbox/` or `sources/`.
2. Generate drafts in `_drafts/`.
3. Review and promote approved concepts into `concepts/`.
4. Study from `quiz/bank.json`.
EOF

cat > "${target_dir}/sources/articles/example-article/meta.yaml" <<'EOF'
type: article
title: Example Article
language: en
date_consumed: 2026-04-28
date_added: 2026-04-28
status: processed
url: https://example.com/article
EOF

cat > "${target_dir}/sources/articles/example-article/notes.md" <<'EOF'
# Example Article Notes

## Knowledge Map

- Core concept: deliberate practice
- Supporting concept: feedback loops

## Summary

This sample source shows the expected structure for processed article notes.
EOF

cat > "${target_dir}/concepts/examples/deliberate-practice.md" <<'EOF'
---
id: deliberate-practice
title: Deliberate Practice
depth: 2
review_due: 2026-05-01
last_updated: 2026-04-28
sources:
  - sources/articles/example-article
tags:
  - learning
  - skill-building
---

# 一句話定義

刻意練習是針對明確弱點進行高回饋、可調整的訓練方式。

# 為什麼存在

它幫助學習者避免只靠重複次數，改以有目標的修正提升能力。

# 關鍵字

- feedback loop
- repetition
- coaching

# 相關概念

- [[active-recall]]

# 摘要

刻意練習要求拆解技能、針對瓶頸練習，並盡快取得回饋。這比單純累積時間更有效率。

# 範例

工程師在每次 code review 後整理錯誤模式，下一輪只針對該模式設計練習題。

# 我的疑問

- 如何替抽象技能定義可量測回饋？
EOF

cat > "${target_dir}/quiz/bank.json" <<'EOF'
[
  {
    "id": "q-deliberate-practice-1",
    "concept_id": "deliberate-practice",
    "type": "short_answer",
    "difficulty": 2,
    "question": "What makes deliberate practice different from passive repetition?",
    "answer": "It targets specific weaknesses and relies on fast feedback plus adjustment.",
    "explanation": "The key distinction is focused correction rather than mindless repetition.",
    "created_at": "2026-04-28",
    "last_attempted": null,
    "next_review": "2026-04-28",
    "interval_days": 1,
    "ease_factor": 2.5,
    "history": []
  }
]
EOF

cat > "${target_dir}/_index/concepts.md" <<'EOF'
# Concepts Index

- deliberate-practice (active)
EOF

cat > "${target_dir}/_index/topics.md" <<'EOF'
# Topics Index

- learning-systems
EOF

cat > "${target_dir}/_index/tags.md" <<'EOF'
# Tags Index

- learning
- skill-building
EOF

cat > "${target_dir}/.gitignore" <<'EOF'
# Audio files
*.mp3
*.wav
*.m4a
*.ogg
*.flac

# Video files
*.mp4
*.mkv
*.webm
*.avi

# Large raw files
*.pdf
*.epub

# Cloned repositories
sources/repos/*/clone/

# Large binaries
*.bin
EOF
