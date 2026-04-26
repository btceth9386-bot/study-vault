# 個人知識庫設計規格 v2:用 AI Agent 持續 refine 的 Exobrain

> 一份從零開始、不綁定任何主題、能持續成長的個人知識庫設計規格。
> 核心理念:**多種來源輸入 → 統一 markdown 格式 → AI Agent 持續 refine → 變成可複習可考試的個人資產**。
>
> **本文件為規格書**,後續會交給實作 Agent 開發。所有具體 prompt、script、目錄結構都已定義清楚。

---

## 目錄

1. [學習方法的理論基礎](#1-學習方法的理論基礎)
2. [四階段學習流程](#2-四階段學習流程)
3. [產出格式與檔案結構](#3-產出格式與檔案結構)
4. [維護策略](#4-維護策略)
5. [AI Agent 如何持續 refine](#5-ai-agent-如何持續-refine)
6. [影片與語音的處理](#6-影片與語音的處理)
7. [Whisper 本機 vs 線上選擇](#7-whisper-本機-vs-線上選擇)
8. [通用知識庫架構(最終版)](#8-通用知識庫架構最終版)
9. [統一 metadata 規格](#9-統一-metadata-規格)
10. [來源 Ingest Pipeline 對照表](#10-來源-ingest-pipeline-對照表)
11. [外部工具整合](#11-外部工具整合)
12. [三個核心 Prompt 規格](#12-三個核心-prompt-規格)
13. [起手式 Checklist](#13-起手式-checklist)
14. [命名建議](#14-命名建議)

---

## 1. 學習方法的理論基礎

這套設計對應到幾個既有的學習方法,把它們串起來:

- **T 型學習(T-shaped learning)**:橫向廣度先鋪開,遇到需要的點再往下挖深。
- **Feynman Technique**:學完一個概念用自己的話講出來,講不清楚就是還沒懂。AI 出題能逼你做這件事。
- **Spaced Repetition(間隔重複)**:Anki 那套。配合考題效果最好,遺忘曲線會壓下來。
- **Active Recall**:主動回憶比重讀有效好幾倍。出題就是 active recall 的形式。
- **Just-in-Time Learning**:需要時才深入。對工程師專案導向的學習特別適合。

整體策略:**T 型 + Active Recall + Spaced Repetition** 串起來。

---

## 2. 四階段學習流程

針對任何一個新主題(GitHub repo / 書 / 課程 / Podcast),都跑這四個階段:

### 第一階段:地圖建立
- 讓 AI Agent 讀來源,產出「知識地圖」
- 包含:核心概念 5-10 個、進階主題、依賴的前置知識
- 這階段只要廣度,不深入

### 第二階段:廣度掃描
- 每個核心概念給 3-5 句的摘要 + 1-2 題選擇題或簡答題
- 目標是讓你對整體有感覺
- 不求深入

### 第三階段:深度按需
- 你挑出有興趣或工作需要的點
- Agent 抓對應的程式碼、issue、PR、相關文件,深入講解
- 配合比較難的應用題

### 第四階段:複習排程
- 答錯的題目進入間隔重複佇列
- 隔天、三天、一週後再考

---

## 3. 產出格式與檔案結構

### 為什麼用 Markdown

- 純文字、Git 友善
- 所有 AI Agent 都能讀寫
- 未來可匯出到 Obsidian / Logseq / Notion
- 影片/語音必須先轉成文字才能進入 refine 循環

### 概念檔模板(每個概念固定格式)

```markdown
---
id: cap-theorem
title: CAP Theorem
depth: 2          # 1=表面, 2=能解釋, 3=能應用, 4=能教
last_reviewed: 2026-04-20
review_due: 2026-04-27
sources:
  - sources/repos/donnemartin-system-design-primer
  - sources/videos/2024-harvard-scalability-lecture#L420-L455
related: [consistency-patterns, eventual-consistency]
tags: [distributed-systems, fundamentals]
---

# CAP Theorem

- **一句話定義**:
- **為什麼存在 / 解決什麼問題**:
- **關鍵字**:
- **相關概念**: [[consistency-patterns]]
- **深度等級**: 1/2/3/4
- **最後更新**: 2026-04-25
- **來源**: repo/file.py:L120

## 摘要
(3-5 句)

## 範例
(程式碼或場景)

## 我的疑問
(自己補,Agent 下次來深入)
```

---

## 4. 維護策略

**要持續維護,但要分層**。沒有維護的知識庫會變墳場。

| 層級 | 更新頻率 | 說明 |
|---|---|---|
| 核心概念層 | 半年一次 | 穩定知識 |
| 深度筆記層 | 工作上用到才補 | Just-in-time |
| 題庫層 | 持續累積 | 最有複利的部分 |
| 疑問清單 | 每次學習新增 | 定期清空 |

**重要原則**:不要追求「全都寫滿」,留白比填滿重要。

---

## 5. AI Agent 如何持續 refine

由淺到深四種做法:

### 方法 1:固定 prompt + 排程
寫一個 refine prompt,每週丟給 Agent:
- 檢查過期內容
- 補充新範例
- 標記內部矛盾
- 產生本週複習題

### 方法 2:用 Claude Code / Cursor 開在 repo 上
- 整個知識庫當 Git repo
- Agent 直接 edit markdown
- 你 review commit
- **這是最實用的做法**

### 方法 3:雙向同步機制
- 聊天時學到的東西,丟一句「把這段加進 knowledge-base/projects/xxx/」
- Agent 直接更新對應檔案

### 方法 4:版本化的 refine workflow
- 每個檔案末尾加 changelog
- Agent 每次修改都附理由
- 半年後能看到自己理解的演進

### 三個核心 prompt(寫好就重複用)

詳細規格見第 12 節。

1. **`new-source.md`**:給定 transcript / repo / 文章,產出來源摘要 + 抽取候選概念到 `_drafts/`
2. **`promote-concept.md`**:把 `_drafts/` 概念提煉成正式概念檔(Feynman 風格摘要 + 範例 + 關聯)
3. **`weekly-refine.md`**:掃 `_inbox/` 和 `_drafts/`、檢查過期概念、生成本週複習題、更新 review_due

---

## 6. 影片與語音的處理

### 為什麼必須轉文字

知識庫核心是「可被搜尋、可被 diff、可被 AI 重讀」。影片做不到:

- **搜尋**:三個月後想找某段內容,看影片要拉時間軸,文字直接 grep
- **Diff / 版本控制**:Git 看不懂 mp4 改了什麼
- **AI refine**:Agent 沒辦法「讀」影片去更新筆記,但能讀 transcript

**原則:影片是來源,transcript 是中間層,筆記是產出**。三層都留著,只有後兩層進 Git。

### SRT 是什麼

純文字字幕格式,每段有編號、時間戳、文字:

```
1
00:00:05,200 --> 00:00:08,500
Welcome to today's lecture on scalability.

2
00:00:08,500 --> 00:00:12,300
We'll start with vertical vs horizontal scaling.
```

對知識庫超友善,因為它就是文字。

### YouTube 影片處理流程

```bash
# 一條指令:先試人工字幕,沒有就抓自動字幕
yt-dlp --write-sub --write-auto-sub --sub-lang en \
  --skip-download --convert-subs srt \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

字幕分三種情況:

| 情況 | 結果 | 處理方式 |
|---|---|---|
| 有人工 CC 字幕 | 品質最好(有標點) | 直接用 |
| 只有自動生成字幕 | 英文堪用,中文/口音重會爛 | 視情況決定要不要 Whisper 重跑 |
| 完全沒字幕 | yt-dlp 抓不到 | 下載音訊 + Whisper |

### 決策流程

```
影片 URL
   ↓
yt-dlp 試抓字幕
   ↓
   ├─ 抓到 CC 字幕 → 直接用 ✅
   ├─ 抓到自動字幕 → 看內容
   │   ├─ 英文清楚 → 直接用 ✅
   │   └─ 中文/混雜/品質差 → 下載音訊 + Whisper
   └─ 沒字幕 → 下載音訊 + Whisper
```

下載音訊餵 Whisper 的指令:

```bash
yt-dlp -x --audio-format mp3 "VIDEO_URL"
whisper audio.mp3 --model medium --output_format srt
```

---

## 7. Whisper 本機 vs 線上選擇

### 本機方案(免費,但要設備)

| 工具 | 特點 |
|---|---|
| `openai/whisper` | 原版,PyTorch,GPU 最爽 |
| `faster-whisper` | **速度快 4 倍、記憶體少一半**,社群主推 |
| `whisper.cpp` | C++ 實作,Mac M 系列特別快 |
| `WhisperX` | 加上精準時間戳、講者分離(diarization),長影片很有用 |

模型大小:`tiny` / `base` / `small` / `medium` / `large-v3`
- 中文或混雜語言 → 一定要 `large-v3`
- 英文 → `medium` 就夠

### 線上服務(付費,省事)

| 服務 | 特點 |
|---|---|
| OpenAI Whisper API | $0.006/分鐘,60 分鐘約 $0.36 |
| Deepgram | 更快、有 streaming、$0.0043/分鐘,企業級 |
| AssemblyAI | 附帶摘要、章節、講者分離 |
| NotebookLM | Google 出的,丟 YouTube 連結直接生筆記和 Q&A |

### 推薦混搭策略

| 情境 | 用什麼 |
|---|---|
| YouTube 教育影片 | yt-dlp 抓字幕,免錢 |
| < 1 小時、英文、不敏感 | OpenAI Whisper API |
| 中文 / 混雜 / 專業術語多 | 本機 faster-whisper + large-v3 |
| 私密內容(會議、自己錄音) | 一律本機跑,不上雲 |
| 想要附加摘要、章節 | NotebookLM 或 AssemblyAI |

實務:筆電裝 `faster-whisper` 當預設,雲端 API 當備援。

---

## 8. 通用知識庫架構(最終版)

### 核心設計原則

1. **來源層 vs 概念層分離**:原始材料和提煉的知識分開
2. **概念是第一公民**:所有東西最終要能變成可複習、可考試的概念
3. **反向連結**:概念知道從哪些來源來,來源知道貢獻了哪些概念
4. **格式統一為 markdown**:影片→transcript、PDF→md、網頁→md、語音→md

### 推薦目錄結構

```
my-kb/
├── README.md                       # 全庫導覽
├── _index/                         # 全庫索引
│   ├── concepts.md                 # 所有概念清單
│   ├── topics.md                   # 主題分類
│   └── tags.md                     # 標籤索引
│
├── concepts/                       # 【概念層】核心資產
│   ├── distributed-systems/
│   │   ├── cap-theorem.md
│   │   └── consistency-patterns.md
│   ├── machine-learning/
│   └── ...
│
├── topics/                         # 【主題層】跨概念的學習路徑
│   ├── system-design-interview.md
│   └── llm-fundamentals.md
│
├── sources/                        # 【來源層】原始材料的處理結果
│   ├── repos/
│   │   └── donnemartin-system-design-primer/
│   │       ├── meta.yaml
│   │       ├── notes.md
│   │       ├── deepwiki-snapshot/  # DeepWiki 下載的 markdown
│   │       └── extracted/
│   ├── videos/
│   │   └── 2024-harvard-scalability-lecture/
│   │       ├── meta.yaml
│   │       ├── transcript.md       # 清理後的全文
│   │       └── highlights.md       # AI 摘要 + 時間戳
│   ├── books/
│   ├── articles/
│   ├── podcasts/
│   └── papers/
│
├── quiz/                           # 【測驗層】
│   ├── bank.json                   # 題庫(結構化)
│   └── review-log.md               # 答題紀錄、間隔重複狀態
│
├── _inbox/                         # 暫存區,還沒分類的筆記
├── _drafts/                        # AI 產的草稿,等你 review
└── _scripts/                       # 自動化工具
    ├── ingest-youtube.sh
    ├── ingest-pdf.sh
    ├── ingest-deepwiki.sh
    └── prompts/
        ├── new-source.md           # 見第 12 節
        ├── promote-concept.md      # 見第 12 節
        └── weekly-refine.md        # 見第 12 節
```

---

## 9. 統一 metadata 規格

### Source 的 meta.yaml

```yaml
type: video | repo | book | article | podcast | paper
title: ...
url: ...
authors: [...]
language: en
date_consumed: 2026-04-26
date_added: 2026-04-26
estimated_time: 90min
quality: 1-5      # 你給的評分
status: ingesting | processed | refined | archived
related_concepts:
  - distributed-systems/cap-theorem
  - databases/sharding
tags: [system-design, interview-prep]
```

### Concept 的 frontmatter

```yaml
---
id: cap-theorem
title: CAP Theorem
depth: 2          # 1=表面, 2=能解釋, 3=能應用, 4=能教
last_reviewed: 2026-04-20
review_due: 2026-04-27
sources:
  - sources/repos/donnemartin-system-design-primer
  - sources/videos/2024-harvard-scalability-lecture#L420-L455
related: [consistency-patterns, eventual-consistency]
tags: [distributed-systems, fundamentals]
---
```

### Quiz Bank 的 JSON 格式

```json
{
  "questions": [
    {
      "id": "q-cap-001",
      "concept_id": "cap-theorem",
      "type": "multiple_choice | short_answer | application",
      "difficulty": 1-5,
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "answer": "...",
      "explanation": "...",
      "created_at": "2026-04-26",
      "last_attempted": "2026-04-27",
      "next_review": "2026-04-30",
      "interval_days": 3,
      "ease_factor": 2.5,
      "history": [
        {"date": "2026-04-26", "result": "correct"},
        {"date": "2026-04-27", "result": "incorrect"}
      ]
    }
  ]
}
```

---

## 10. 來源 Ingest Pipeline 對照表

不管來源是什麼,**最後都產出 markdown + frontmatter**,下游處理就能完全統一。

| 來源類型 | Pipeline |
|---|---|
| GitHub repo | clone → 讀 README/docs → AI 產知識地圖 + 概念草稿 |
| GitHub repo (替代) | DeepWiki 抓現成 wiki → 轉 markdown → 進 sources/repos |
| YouTube | yt-dlp 抓字幕(必要時 Whisper)→ 清理 → AI 摘要 + 概念抽取 |
| PDF / 論文 | pdftotext / Marker → 清理 → AI 摘要 |
| 網頁文章 | 抓 HTML → 轉 markdown(Readability + Turndown)→ 摘要 |
| Podcast | 下載 mp3 → Whisper → 清理 → 摘要 |
| 書(epub) | epub → 章節 markdown → 逐章摘要 |
| 會議錄音 | Whisper + WhisperX(講者分離)→ 清理 → 摘要 |

---

## 11. 外部工具整合

### DeepWiki 整合方案

DeepWiki(deepwiki.com)由 Devin 出品,自動把任何 public GitHub repo 變成可問答的 wiki。

**定位**:DeepWiki 不取代本知識庫,而是當作 GitHub repo 類型的 ingest 工具。

**官網沒有原生下載按鈕**,但有四種方式取得內容:

| 方法 | 適合情境 | 自動化 |
|---|---|---|
| Chrome 擴充「DeepWiki to Markdown」 | 偶爾手動下載 | ❌ |
| `deepwiki-to-md` CLI(PyPI) | 命令列、可 script | ✅ |
| 官方 MCP server | 接 Claude Code / Cursor | ✅ |
| 直接 web fetch | 簡單一兩頁 | 半自動 |

**推薦組合用法**:

- **首次整批下載 repo wiki** → 用 CLI 或瀏覽器擴充
- **AI Agent 即時查詢** → 用 MCP server
- **臨時看一頁** → 直接 fetch

**MCP server 設定範例**(Claude Code 的 `.mcp.json`):

```json
{
  "mcpServers": {
    "deepwiki": {
      "url": "https://mcp.deepwiki.com/mcp"
    }
  }
}
```

MCP server 提供三個工具:
- `ask_question`:對 wiki 問問題
- `read_wiki_structure`:讀 wiki 目錄
- `read_wiki_contents`:讀 wiki 內容

**CLI 用法範例**:

```bash
pip install deepwiki-to-md

deepwiki-to-md https://deepwiki.com/donnemartin/system-design-primer \
  --path ./sources/repos/donnemartin-system-design-primer/deepwiki-snapshot
```

### 其他可整合工具

| 工具 | 整合方式 | 用途 |
|---|---|---|
| NotebookLM | 手動丟連結 | 快速生 Q&A、章節摘要 |
| Anki | 從 quiz/bank.json 匯出 .apkg | 間隔重複實踐 |
| Obsidian | 直接打開 my-kb 資料夾 | 雙向連結視覺化 |
| Readwise | API | 同步電子書畫線、文章摘錄 |

---

## 12. 三個核心 Prompt 規格

這三個 prompt 是知識庫運作的核心引擎。實作 Agent 應該依照下列規格寫成 markdown 檔,放在 `_scripts/prompts/` 目錄下。

### 12.1 `new-source.md` 規格

**用途**:任何新來源(transcript / repo / PDF / 文章)進入 `_inbox/` 後,觸發此 prompt 做初步處理。

**輸入**:
- 一份 markdown 格式的來源內容(可能是 transcript、文章、repo 摘要等)
- 來源的基本 metadata(類型、URL、語言)

**輸出**:
1. 在 `sources/<type>/<slug>/` 建立資料夾,包含:
   - `meta.yaml`(填好所有欄位)
   - `notes.md`(來源整體摘要,200-500 字)
   - `highlights.md`(關鍵段落 + 行號/時間戳)
2. 在 `_drafts/` 建立候選概念檔,每個概念一個 .md,含 frontmatter
3. 在 `_index/concepts.md` 加入新概念條目(標記為 draft)

**Agent 行為要求**:
- 識別 5-10 個核心概念,不超過 10 個(避免過度切割)
- 每個候選概念至少寫:一句話定義、為什麼存在、跟既有概念的關聯
- 跨參照:檢查 `concepts/` 已存在的概念,如果重複,在 draft 標記 `merge_candidate: <existing-id>`
- 不要提煉成正式概念,留給 `promote-concept.md` 處理

**驗收標準**:
- meta.yaml 所有欄位完整
- _drafts/ 至少有 1 個候選概念
- 不能直接寫入 concepts/(只能寫 _drafts/)

---

### 12.2 `promote-concept.md` 規格

**用途**:把 `_drafts/` 的候選概念,提煉成正式概念檔,移到 `concepts/`。

**輸入**:
- 一個 `_drafts/<concept>.md` 檔案
- 該概念對應的所有來源(從 frontmatter 反查)
- 既有的 `concepts/` 結構(用於決定分類資料夾)

**輸出**:
1. 在 `concepts/<category>/<concept-id>.md` 建立正式概念檔(格式見第 9 節 frontmatter)
2. 概念內容要符合 Feynman Technique:能讓「不熟此領域的人」讀懂
3. 在 `quiz/bank.json` 自動產生 2-3 題(含選擇題、簡答題、應用題各至少一題)
4. 更新 `_index/concepts.md`,從 draft 改為 active
5. 從 `_drafts/` 移除該檔案

**Agent 行為要求**:
- **Feynman 風格摘要**(必填):用日常語言解釋,避免術語堆疊。如果用了術語,要附簡短說明。
- **至少一個具體範例**:程式碼、現實場景、或類比
- **明確標記 depth**:首次提煉預設 depth=2(能解釋)
- **建立反向連結**:檢查 related concepts,在它們的檔案裡也加上反向連結
- **設定首次 review_due**:預設為今天 + 3 天

**驗收標準**:
- 概念檔通過 markdown lint
- 至少 1 個範例
- quiz/bank.json 至少新增 2 題,且包含正確答案與解釋
- 反向連結雙向一致

---

### 12.3 `weekly-refine.md` 規格

**用途**:每週(或使用者觸發)執行的維護任務,讓知識庫持續健康成長。

**輸入**:
- 整個知識庫狀態
- 上次執行 weekly-refine 的時間戳(從 `_index/refine-log.md` 讀取)

**輸出**:一份 `_inbox/refine-report-<date>.md` 報告,包含以下章節:

1. **過期概念清單**:`review_due` 已過的概念,並針對每個產生 1 題複習題
2. **內部矛盾偵測**:同一概念在不同檔案說法不一致的地方
3. **草稿待處理清單**:`_drafts/` 裡超過 7 天還沒 promote 的概念
4. **疑問清單彙整**:從各概念檔的「我的疑問」段落彙整,附上建議處理方式
5. **本週複習題包**:5-10 題,優先取自 `quiz/bank.json` 中 `next_review <= today` 的題目
6. **新增概念建議**:從 `sources/` 中可能還沒抽出的概念

**Agent 行為要求**:
- **不要主動修改 concepts/**,只在報告中提建議,等使用者 review
- **可以更新 quiz/bank.json**:依答題紀錄計算下次 `next_review`(SM-2 演算法或簡化版)
- **可以更新 `_index/`**:重新產生 concepts.md / topics.md / tags.md
- **記錄本次執行**:在 `_index/refine-log.md` 加一行(時間、處理數量、報告路徑)

**SM-2 演算法簡化版**(用於 next_review 計算):
- 答對:`interval_days = interval_days * ease_factor`,`ease_factor` 維持
- 答錯:`interval_days = 1`,`ease_factor = max(1.3, ease_factor - 0.2)`
- 預設 `ease_factor = 2.5`

**驗收標準**:
- 報告檔案產生在 `_inbox/refine-report-YYYY-MM-DD.md`
- 不應修改 `concepts/` 任何檔案內容
- `quiz/bank.json` 的 `next_review` 欄位有更新
- `_index/refine-log.md` 有新一行記錄

---

### 12.4 三個 Prompt 的呼叫時機

```
新來源進來 → new-source.md → _drafts/ 出現候選概念
                                      ↓
                          (使用者 review draft)
                                      ↓
                         promote-concept.md → concepts/ 正式概念
                                      ↓
                         (持續累積一段時間)
                                      ↓
                         weekly-refine.md → 報告 + 複習題
                                      ↓
                              (使用者答題、refine)
                                      ↓
                              循環回到任何階段
```

---

## 13. 起手式 Checklist

依序執行(交給實作 Agent):

- [ ] 1. 開 GitHub private repo(命名見下節)
- [ ] 2. 建立目錄骨架(複製第 8 節結構)
- [ ] 3. 產生範例檔案:1 個範例 source、1 個範例 concept、1 個範例 quiz
- [ ] 4. 產生 `_scripts/prompts/` 下三個 prompt 檔(依第 12 節規格)
- [ ] 5. 寫 ingest scripts:`ingest-youtube.sh`、`ingest-pdf.sh`、`ingest-deepwiki.sh`
- [ ] 6. 設定 DeepWiki MCP server(`.mcp.json`)
- [ ] 7. 寫 README.md,說明知識庫使用方式
- [ ] 8. 建立 GitHub Actions(可選):每週日自動執行 weekly-refine
- [ ] 9. 跑一個完整 pipeline 驗收(從一個 YouTube 影片開始,跑到出現複習題)

---

## 14. 命名建議

### 候選名字分類

**直白型**
- `knowledge-base` / `my-kb` / `personal-kb`
- `learning-notes` / `study-vault`

**第二大腦型**
- `second-brain` / `exobrain` / `brain-dump`

**Digital Garden 型**(很適合 refine 概念)
- `digital-garden` / `knowledge-garden`

**個人風格型**
- `<handle>/notes` / `<handle>/wiki` / `<handle>/codex`

**有點玩味的**
- `recall`(對應 active recall)
- `compendium`(知識彙編)
- `lighthouse`(給未來自己照路)

### Exobrain 是什麼

- **exo-** = 希臘文「外部的」(exoskeleton 外骨骼、exoplanet 系外行星)
- **exobrain = 外部大腦 / 外掛大腦**
- 把知識、想法、記憶外包給外部系統,肉身大腦負責思考和創造,exobrain 負責儲存和檢索
- 跟 Second Brain 概念一樣,但更工程師、更 hacker 文化

### Digital Garden vs Exobrain 差別

- **digital-garden** 強調「過程」(持續培育知識)
- **exobrain** 強調「定位」(這是我大腦的延伸)

### 命名實用建議

repo 名字不用太花俏,因為:
- `git clone` 會打很多次
- 編輯器顯示就是這名字
- 太可愛的名字三年後會尷尬

**實用 > 浪漫**。前三推薦:
1. `digital-garden` — 契合持續 refine 的設計
2. `<handle>/kb` — 簡潔、私人、實用
3. `exobrain` — 有個性,技術圈會心一笑

---

## 附錄:核心心法

1. **影片 / 語音必須轉文字**才能進入 refine 循環
2. **格式統一為 markdown + frontmatter**,下游處理才能自動化
3. **概念是第一公民**,來源只是供應商
4. **留白比填滿重要**,別追求「全都寫滿」
5. **持續 refine 比一次寫好重要**,知識會生長
6. **三個 prompt 寫好就重複用**:new-source / promote-concept / weekly-refine
7. **DeepWiki 是 ingest 工具,不是替代品**

---

## 附錄:給實作 Agent 的注意事項

- 本規格書定義了**what**和**why**,具體**how**(技術選型、語言、framework)由實作 Agent 決定
- 三個 prompt 的文字內容由實作 Agent 撰寫,但必須符合第 12 節定義的輸入/輸出/行為/驗收標準
- 優先使用既有開源工具(yt-dlp、Whisper、deepwiki-to-md 等),不要重造輪子
- 所有寫入操作必須是「先進 _drafts/ 或 _inbox/,使用者 review 後才進正式區」,避免 AI 自動寫壞知識庫
- weekly-refine 永遠不能直接修改 concepts/,只能產出建議報告
