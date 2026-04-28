#!/usr/bin/env bash

set -euo pipefail

target_root="${1:-.}"

mkdir -p "$target_root"
target_root="$(cd "$target_root" && pwd)"

write_if_missing() {
  local path="$1"
  if [[ -e "$path" ]]; then
    return
  fi

  mkdir -p "$(dirname "$path")"
  cat >"$path"
}

mkdir -p \
  "$target_root/_inbox" \
  "$target_root/_drafts" \
  "$target_root/concepts/examples" \
  "$target_root/sources/repos" \
  "$target_root/sources/videos" \
  "$target_root/sources/books" \
  "$target_root/sources/articles/example-article" \
  "$target_root/sources/podcasts" \
  "$target_root/sources/papers" \
  "$target_root/quiz" \
  "$target_root/_index" \
  "$target_root/topics" \
  "$target_root/_scripts/prompts"

write_if_missing "$target_root/README.md" <<'EOF'
# Study Vault

This directory is an initialized Exobrain knowledge base.

## Usage

1. Drop new raw materials into `_inbox/`.
2. Run the appropriate ingest script from `_scripts/` to normalize the source into `sources/`.
3. Generate draft concepts into `_drafts/` and review them before promotion.
4. Promote approved concepts into `concepts/`, then update `quiz/bank.json` and `_index/`.
5. Regenerate indexes whenever concepts or topics change.

## Structure

- `_inbox/` stores new materials waiting for ingestion.
- `_drafts/` stores AI-generated drafts that still require review.
- `concepts/` stores approved concept notes.
- `sources/` stores normalized source material grouped by type.
- `quiz/bank.json` stores spaced-repetition questions.
- `_index/` stores generated concept, topic, and tag indexes.
- `topics/` stores curated learning paths.
- `_scripts/prompts/` stores agent prompt templates.
EOF

write_if_missing "$target_root/sources/articles/example-article/meta.yaml" <<'EOF'
type: article
title: "Example Article: Active Recall Basics"
url: https://example.com/active-recall-basics
authors:
  - Example Author
language: en
date_consumed: 2026-04-28
date_added: 2026-04-28
estimated_time: 15min
status: processed
related_concepts:
  - active-recall
tags:
  - learning
  - fundamentals
EOF

write_if_missing "$target_root/sources/articles/example-article/notes.md" <<'EOF'
# Example Article Notes

## Summary

Active recall improves retention by forcing you to retrieve ideas from memory instead of re-reading them passively.

## Key Takeaways

- Turn reading highlights into questions.
- Keep prompts concrete and easy to review later.
- Review at increasing intervals to reinforce recall.
EOF

write_if_missing "$target_root/concepts/examples/active-recall.md" <<'EOF'
---
id: active-recall
title: Active Recall
depth: 2
review_due: 2026-05-01
sources:
  - sources/articles/example-article
related:
  - spaced-repetition
tags:
  - learning
  - fundamentals
---

# Active Recall

- **一句話定義**：主動從記憶中提取資訊，而不是被動重讀。
- **為什麼存在 / 解決什麼問題**：降低熟悉感錯覺，讓學習更接近真實提取場景。
- **關鍵字**：retrieval practice, memory, testing effect
- **相關概念**：[[spaced-repetition]]
- **深度等級**：2
- **最後更新**：2026-04-28
- **來源**：sources/articles/example-article

## 摘要

Active recall asks you to answer from memory before checking notes. This reveals gaps quickly and creates stronger retrieval cues for later reviews.

## 範例

After reading a chapter, close the book and write down the three main claims from memory, then compare your answer with the notes.

## 我的疑問

- Which prompt formats make recall easiest to maintain for long-term study?
EOF

write_if_missing "$target_root/quiz/bank.json" <<'EOF'
{
  "questions": [
    {
      "id": "q-active-recall-001",
      "concept_id": "active-recall",
      "type": "short_answer",
      "difficulty": 1,
      "question": "What is the main goal of active recall?",
      "answer": "To retrieve knowledge from memory instead of passively re-reading it.",
      "explanation": "The retrieval step strengthens memory and exposes gaps in understanding.",
      "created_at": "2026-04-28",
      "next_review": "2026-04-29",
      "interval_days": 1,
      "ease_factor": 2.5,
      "history": []
    }
  ]
}
EOF

write_if_missing "$target_root/_index/concepts.md" <<'EOF'
# Concepts Index

Knowledge base initialized. Run `_scripts/index_generator.py` after adding or promoting concepts.
EOF

write_if_missing "$target_root/_index/topics.md" <<'EOF'
# Topics Index

Knowledge base initialized. Add topic files under `topics/` and regenerate indexes when ready.
EOF

write_if_missing "$target_root/_index/tags.md" <<'EOF'
# Tags Index

Knowledge base initialized. Tags will appear here after concepts are added and indexes are regenerated.
EOF

write_if_missing "$target_root/.gitignore" <<'EOF'
# Audio and video artifacts
*.mp3
*.m4a
*.wav
*.mp4
*.mkv
*.mov
*.webm

# Large document artifacts
*.pdf
*.epub

# Cloned repositories or nested VCS data
sources/repos/**/repo/
sources/repos/**/.git/
EOF
