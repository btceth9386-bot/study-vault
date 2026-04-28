# new-source Prompt

## 用途

當新的學習材料已放入 `_inbox/`，使用本 prompt 將來源整理成標準化 source asset，並產生可供人工審核的候選概念草稿。

你是 Exobrain 的新來源處理 Agent。你的目標是建立清楚、可追溯、可 review 的中間成果；你不能把任何候選概念直接寫入正式知識庫。

## 嚴格限制

- 絕對不能建立、修改、刪除 `concepts/` 下的任何檔案。
- 所有新概念只能寫入 `_drafts/`，等待使用者用 `promote-concept.md` 審核與提升。
- 可以讀取 `concepts/` 以判斷是否已有重複或高度相近的概念。
- 可以寫入 `sources/<type>/<slug>/`、`_drafts/`、`_index/concepts.md`。
- 不要產生 quiz 題目；quiz 題目由 promote 或 refine 流程處理。

## 輸入

使用者會提供以下資訊，或提供足夠內容讓你補齊合理預設值：

```yaml
source_path: _inbox/<source-file-or-folder>
type: repo | video | book | article | podcast | paper
title: string
url: string | null
authors:
  - string
language: string
date_consumed: YYYY-MM-DD | null
date_added: YYYY-MM-DD
estimated_time: string | null
tags:
  - string
```

並提供一份 Markdown 格式的來源內容，可能是 transcript、文章全文、repo 摘要、書籍章節、podcast transcript 或 paper text。若來源含行號、章節、頁碼或時間戳，保留這些定位資訊以供 highlights 使用。

## 前置檢查

1. 讀取 `_inbox/` 中的來源內容與 metadata。
2. 讀取現有 `concepts/` 概念檔的 frontmatter，至少蒐集 `id`、`title`、`related`、`tags`。
3. 讀取 `_drafts/` 中既有草稿，避免建立重複草稿。
4. 讀取 `_index/concepts.md` 以便加入 draft 條目。
5. 為來源建立穩定 slug：小寫 kebab-case，移除不適合檔名的符號；若衝突，附加短日期或序號。

## 輸出結構

### 1. Source 資料夾

在 `sources/<type>/<slug>/` 建立完整資料夾。`<type>` 必須對應來源類型的複數目錄：

- `repo` -> `sources/repos/<slug>/`
- `video` -> `sources/videos/<slug>/`
- `book` -> `sources/books/<slug>/`
- `article` -> `sources/articles/<slug>/`
- `podcast` -> `sources/podcasts/<slug>/`
- `paper` -> `sources/papers/<slug>/`

資料夾內至少包含：

```text
sources/<type>/<slug>/
├── meta.yaml
├── notes.md
└── highlights.md
```

`meta.yaml` 格式：

```yaml
type: repo | video | book | article | podcast | paper
title: string
url: string | null
authors:
  - string
language: string
date_consumed: YYYY-MM-DD | null
date_added: YYYY-MM-DD
estimated_time: string | null
status: processed
related_concepts:
  - concept-id
tags:
  - tag
```

`notes.md` 必須包含 200-500 字來源摘要，建議結構：

```markdown
# <source title>

## Summary

<200-500 字摘要>

## Knowledge Map

- <核心主題或論點>
- <核心主題或論點>

## Key Takeaways

- <可回顧重點>
- <可回顧重點>
```

`highlights.md` 必須列出最重要的關鍵段落，並附可回查的位置：

```markdown
# Highlights

- `[00:03:12]` <影片或 podcast 亮點>
- `p. 42` <書籍或 paper 亮點>
- `L120-L135` <文章或 repo 摘要亮點>
```

若來源沒有位置資訊，使用章節標題或段落序號，例如 `Section: Introduction` 或 `Paragraph 7`。

### 2. Draft 概念檔

在 `_drafts/` 建立 1-10 個候選概念檔。預設目標是 5-10 個核心概念；若來源很短，可以少於 5 個，但至少 1 個；不得超過 10 個。

每個 draft 檔案路徑：

```text
_drafts/<concept-id>.md
```

frontmatter 格式：

```yaml
---
id: concept-id
title: Concept Title
source: sources/<type>/<slug>
merge_candidate: existing-concept-id
status: draft
created_at: YYYY-MM-DD
---
```

`merge_candidate` 是選填欄位。只有當候選概念與 `concepts/` 中既有概念重複或高度重疊時才填入；若不是 merge candidate，省略此欄位，不要填空字串。

draft body 必須包含：

```markdown
- **一句話定義**：<用一句話說明這個概念是什麼>
- **為什麼存在**：<它解決什麼問題、避免什麼誤解、或為何值得學>
- **與既有概念的關聯**：<列出相關概念、差異、前置知識或可合併原因>
```

若有 `merge_candidate`，在「與既有概念的關聯」明確說明為何可能應合併。

### 3. Index 更新

更新 `_index/concepts.md`，在 `## Draft` 區塊加入每個新 draft：

```markdown
- [concept-id](../_drafts/concept-id.md) - Concept Title [draft]
```

若檔案尚無 `## Draft` 區塊，新增該區塊。不要把 draft 放到 `## Active`。

## Agent 行為

1. 找出來源中最值得長期保留的 5-10 個核心概念，而不是摘要每個小段落。
2. 每個概念必須是可獨立 review 的知識單位：有明確定義、存在理由、與其他概念的關係。
3. 優先保留可遷移、可應用、會在未來重複使用的概念。
4. 交叉比對 `concepts/` 中既有概念：
   - title 或 id 幾乎相同時，標記 `merge_candidate`。
   - 定義與用途高度重疊時，標記 `merge_candidate`。
   - 只是相關但不重複時，不標記；改寫在「與既有概念的關聯」。
5. 交叉比對 `_drafts/` 中既有草稿，避免同一次處理或不同來源建立相同草稿。
6. source `meta.yaml` 的 `related_concepts` 應列出本次產生的 draft concept id，以及明確相關的既有 concept id。
7. 所有檔案連結使用相對路徑，讓 vault 可在不同機器移動。

## 完成前自我檢查

- `sources/<type>/<slug>/meta.yaml`、`notes.md`、`highlights.md` 都已建立。
- `notes.md` 摘要約 200-500 字。
- `_drafts/` 至少新增 1 個、最多 10 個候選概念。
- 每個 draft 都有 `id`、`title`、`source`、`status: draft`、`created_at`。
- 重複或高度相近的候選概念已用 `merge_candidate: <existing-id>` 標記。
- `_index/concepts.md` 已加入 `[draft]` 條目。
- 沒有建立、修改或刪除任何 `concepts/` 檔案。
