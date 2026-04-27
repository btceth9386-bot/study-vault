# 需求文件：個人知識庫系統（Exobrain）

## 簡介

本系統為一套以 Markdown 為核心的個人知識庫（Exobrain），支援多種來源輸入（YouTube 影片、PDF、GitHub repo、文章、Podcast、書籍），透過 AI Agent 持續 refine，將原始材料轉化為可搜尋、可複習、可考試的個人知識資產。

核心流程：**多種來源輸入 → 統一 Markdown 格式 → AI Agent 持續 refine → 可複習可考試的個人資產**

### 設計決策

- **Whisper 策略**：僅使用 OpenAI Whisper API（$0.006/分鐘），不需要本機 Whisper 方案。
- **Git 策略**：僅將 refined/processed 的 Markdown 檔案納入 Git。原始音訊/影片檔、大型 PDF、cloned repo 等大型檔案透過 `.gitignore` 排除。目標相容 GitHub Free 帳號（單一 repo 建議 < 10 GB、單一檔案建議 < 1 MB、強制上限 100 MB）。

## 詞彙表

- **Knowledge_Base（知識庫）**：整個 Exobrain 系統，包含所有目錄、檔案、腳本與索引
- **Ingest_Pipeline（匯入管線）**：將外部來源轉換為統一 Markdown 格式的自動化流程
- **Source（來源）**：原始學習材料（影片、文章、repo、PDF、Podcast、書籍等）
- **Concept（概念）**：從來源中提煉出的核心知識單元，為知識庫的第一公民
- **Draft（草稿）**：AI 產出但尚未經使用者 review 的候選概念檔
- **Prompt_Engine（提示引擎）**：三個核心 Prompt（new-source、promote-concept、weekly-refine）的統稱
- **Quiz_Bank（題庫）**：結構化的測驗題目集合，支援間隔重複複習
- **SM2_Scheduler（SM-2 排程器）**：基於 SM-2 演算法計算下次複習時間的排程邏輯
- **Transcript（逐字稿）**：影片或語音轉換後的文字內容
- **Frontmatter**：Markdown 檔案開頭的 YAML metadata 區塊
- **DeepWiki**：由 Devin 出品的工具，可將 public GitHub repo 自動轉為可問答的 wiki
- **Refine_Report（精煉報告）**：weekly-refine 產出的維護報告

## 需求

### 需求 1：目錄結構初始化

**使用者故事：** 身為使用者，我希望能一鍵建立完整的知識庫目錄骨架，以便立即開始使用知識庫。

#### 驗收標準

1. WHEN 使用者執行初始化指令，THE Knowledge_Base SHALL 建立以下目錄結構：`_inbox/`、`_drafts/`、`concepts/`、`sources/`（含 `repos/`、`videos/`、`books/`、`articles/`、`podcasts/`、`papers/` 子目錄）、`quiz/`、`_index/`、`topics/`、`_scripts/`（含 `prompts/` 子目錄）
2. WHEN 初始化完成，THE Knowledge_Base SHALL 產生 `README.md` 說明知識庫使用方式
3. WHEN 初始化完成，THE Knowledge_Base SHALL 產生範例檔案：1 個範例 source（含 `meta.yaml` 與 `notes.md`）、1 個範例 concept（含完整 frontmatter）、1 個範例 quiz（`quiz/bank.json` 含至少 1 題）
4. WHEN 初始化完成，THE Knowledge_Base SHALL 產生 `_index/concepts.md`、`_index/topics.md`、`_index/tags.md` 三個索引檔
5. WHEN 初始化完成，THE Knowledge_Base SHALL 產生 `.gitignore` 檔案，排除以下類型的檔案：音訊檔（`*.mp3`、`*.wav`、`*.m4a`）、影片檔（`*.mp4`、`*.mkv`、`*.webm`）、大型 PDF 原始檔、cloned repo 原始碼、以及任何超過 1 MB 的二進位檔案

### 需求 2：Git 儲存庫大小管理

**使用者故事：** 身為使用者，我希望知識庫能安全地 commit 到 GitHub Free 帳號，不會因為檔案過大而被拒絕。

#### 驗收標準

1. THE Knowledge_Base SHALL 確保所有納入 Git 追蹤的檔案為純文字格式（Markdown、YAML、JSON、shell script）
2. THE Knowledge_Base SHALL 透過 `.gitignore` 排除所有未經 refine 的原始來源檔案（音訊、影片、大型 PDF、cloned repo 原始碼）
3. THE Knowledge_Base SHALL 確保單一 Markdown 檔案大小不超過 1 MB
4. IF 單一 transcript 檔案超過 1 MB，THEN THE Ingest_Pipeline SHALL 將該 transcript 拆分為多個檔案，每個檔案不超過 1 MB
5. THE Knowledge_Base SHALL 在 `README.md` 中說明哪些檔案類型納入 Git、哪些應排除

### 需求 3：YouTube 影片匯入

**使用者故事：** 身為使用者，我希望能將 YouTube 影片轉換為 Markdown 筆記，以便納入知識庫進行 refine。

#### 驗收標準

1. WHEN 使用者提供 YouTube 影片 URL，THE Ingest_Pipeline SHALL 使用 yt-dlp 嘗試下載字幕（優先人工 CC 字幕，其次自動生成字幕）
2. WHEN yt-dlp 成功取得字幕，THE Ingest_Pipeline SHALL 將 SRT 字幕轉換為清理後的 Markdown transcript
3. WHEN yt-dlp 無法取得字幕或字幕品質不佳，THE Ingest_Pipeline SHALL 使用 yt-dlp 下載音訊並呼叫 OpenAI Whisper API 產生逐字稿
4. WHEN transcript 產生完成，THE Ingest_Pipeline SHALL 在 `sources/videos/<slug>/` 建立 `meta.yaml`、`transcript.md`、`highlights.md`
5. THE Ingest_Pipeline SHALL 在 `meta.yaml` 中填入所有必要欄位（type、title、url、language、date_consumed、date_added、status）
6. WHEN 影片處理完成，THE Ingest_Pipeline SHALL 將下載的音訊檔排除於 Git 追蹤之外（音訊檔保留在本機但列入 `.gitignore`）

### 需求 4：PDF 文件匯入

**使用者故事：** 身為使用者，我希望能將 PDF 文件轉換為 Markdown 筆記，以便納入知識庫。

#### 驗收標準

1. WHEN 使用者提供 PDF 檔案路徑，THE Ingest_Pipeline SHALL 使用文字擷取工具（如 pdftotext 或 Marker）將 PDF 轉換為 Markdown
2. WHEN 轉換完成，THE Ingest_Pipeline SHALL 在 `sources/<適當類型>/<slug>/` 建立 `meta.yaml` 與 `notes.md`
3. THE Ingest_Pipeline SHALL 將原始 PDF 檔案排除於 Git 追蹤之外
4. IF PDF 轉換後的 Markdown 超過 1 MB，THEN THE Ingest_Pipeline SHALL 將內容拆分為多個檔案

### 需求 5：GitHub Repo 匯入

**使用者故事：** 身為使用者，我希望能提供 GitHub repo URL 就能透過 DeepWiki 自動匯入該 repo 的知識，以便學習 repo 的架構與核心概念。

#### 驗收標準

1. WHEN 使用者提供 GitHub repo URL，THE Ingest_Pipeline SHALL 自動轉換為對應的 DeepWiki URL 並使用 `deepwiki-to-md` CLI 下載 wiki 內容
2. IF DeepWiki 尚未建立該 repo 的 wiki，THEN THE Ingest_Pipeline SHALL 提示使用者前往 deepwiki.com 貼上 repo URL 觸發建立，並於建立完成後重新執行腳本
3. IF repo 為 private，THEN THE Ingest_Pipeline SHALL 報錯提示 DeepWiki 僅支援 public repo
4. WHEN 匯入完成，THE Ingest_Pipeline SHALL 在 `sources/repos/<slug>/` 建立 `meta.yaml`、`notes.md`、`deepwiki-snapshot/` 目錄

### 需求 6：網頁文章匯入

**使用者故事：** 身為使用者，我希望能將網頁文章轉換為 Markdown 筆記，以便納入知識庫。

#### 驗收標準

1. WHEN 使用者提供網頁 URL，THE Ingest_Pipeline SHALL 擷取 HTML 內容並轉換為 Markdown（使用 Readability + Turndown 或同等工具）
2. WHEN 轉換完成，THE Ingest_Pipeline SHALL 在 `sources/articles/<slug>/` 建立 `meta.yaml` 與 `notes.md`

### 需求 7：Podcast 匯入

**使用者故事：** 身為使用者，我希望能將 Podcast 音訊轉換為 Markdown 筆記，以便納入知識庫。

#### 驗收標準

1. WHEN 使用者提供 Podcast 音訊檔案或 URL，THE Ingest_Pipeline SHALL 下載音訊並呼叫 OpenAI Whisper API 產生逐字稿
2. WHEN 逐字稿產生完成，THE Ingest_Pipeline SHALL 在 `sources/podcasts/<slug>/` 建立 `meta.yaml`、`transcript.md`、`highlights.md`
3. THE Ingest_Pipeline SHALL 將下載的音訊檔排除於 Git 追蹤之外

### 需求 8：書籍（epub）匯入

**使用者故事：** 身為使用者，我希望能將 epub 書籍轉換為 Markdown 筆記，以便逐章學習。

#### 驗收標準

1. WHEN 使用者提供 epub 檔案路徑，THE Ingest_Pipeline SHALL 將 epub 拆分為逐章 Markdown 檔案
2. WHEN 轉換完成，THE Ingest_Pipeline SHALL 在 `sources/books/<slug>/` 建立 `meta.yaml` 與各章節的 Markdown 檔案
3. THE Ingest_Pipeline SHALL 將原始 epub 檔案排除於 Git 追蹤之外


### 需求 9：統一 Metadata 規格

**使用者故事：** 身為使用者，我希望所有來源與概念都有統一的 metadata 格式，以便 AI Agent 自動化處理與索引。

#### 驗收標準

1. THE Knowledge_Base SHALL 要求每個 Source 目錄包含 `meta.yaml`，欄位包含：type、title、url、authors、language、date_consumed、date_added、estimated_time、quality、status、related_concepts、tags
2. THE Knowledge_Base SHALL 要求每個 Concept 檔案包含 YAML frontmatter，欄位包含：id、title、depth（1-4）、last_reviewed、review_due、sources、related、tags
3. THE Knowledge_Base SHALL 要求 `quiz/bank.json` 中每個題目包含：id、concept_id、type、difficulty、question、answer、explanation、created_at、last_attempted、next_review、interval_days、ease_factor、history
4. WHEN 任何 Ingest_Pipeline 產出檔案，THE Ingest_Pipeline SHALL 確保 metadata 欄位完整且符合上述規格

### 需求 10：new-source Prompt 執行

**使用者故事：** 身為使用者，我希望新來源進入知識庫時，AI Agent 能自動產出摘要並抽取候選概念，以便我後續 review。

#### 驗收標準

1. WHEN 新來源內容進入 `_inbox/`，THE Prompt_Engine SHALL 執行 `new-source` prompt 進行初步處理
2. WHEN `new-source` 執行完成，THE Prompt_Engine SHALL 在 `sources/<type>/<slug>/` 建立 `meta.yaml`（所有欄位完整）、`notes.md`（200-500 字摘要）、`highlights.md`（關鍵段落含行號或時間戳）
3. WHEN `new-source` 執行完成，THE Prompt_Engine SHALL 在 `_drafts/` 建立 1-10 個候選概念檔，每個概念包含：一句話定義、為什麼存在、與既有概念的關聯
4. WHEN `_drafts/` 中的候選概念與 `concepts/` 中已存在的概念重複，THE Prompt_Engine SHALL 在 draft 的 frontmatter 中標記 `merge_candidate: <existing-id>`
5. THE Prompt_Engine SHALL 在 `_index/concepts.md` 中加入新概念條目並標記為 draft
6. THE Prompt_Engine SHALL 不直接寫入 `concepts/` 目錄，僅寫入 `_drafts/`

### 需求 11：promote-concept Prompt 執行

**使用者故事：** 身為使用者，我希望能將 AI 產出的草稿概念提煉為正式概念，並自動產生測驗題目。

#### 驗收標準

1. WHEN 使用者選定一個 `_drafts/<concept>.md` 進行 promote，THE Prompt_Engine SHALL 在 `concepts/<category>/<concept-id>.md` 建立正式概念檔
2. THE Prompt_Engine SHALL 以 Feynman Technique 風格撰寫概念摘要：使用日常語言解釋，術語附簡短說明
3. THE Prompt_Engine SHALL 在概念檔中包含至少 1 個具體範例（程式碼、現實場景或類比）
4. WHEN 概念檔建立完成，THE Prompt_Engine SHALL 在 `quiz/bank.json` 新增至少 2 題測驗題（包含選擇題、簡答題、應用題中至少兩種類型），每題含正確答案與解釋
5. WHEN 概念檔建立完成，THE Prompt_Engine SHALL 設定 `depth=2`（能解釋）作為預設深度，並設定 `review_due` 為建立日期 + 3 天
6. WHEN 概念檔建立完成，THE Prompt_Engine SHALL 檢查 related concepts 並在相關概念檔中加入反向連結
7. WHEN promote 完成，THE Prompt_Engine SHALL 更新 `_index/concepts.md` 將該概念從 draft 改為 active，並從 `_drafts/` 移除該檔案

### 需求 12：weekly-refine Prompt 執行

**使用者故事：** 身為使用者，我希望每週有一份維護報告，讓我知道哪些概念需要複習、哪些草稿待處理。

#### 驗收標準

1. WHEN 使用者觸發 weekly-refine（手動或排程），THE Prompt_Engine SHALL 產生 `_inbox/refine-report-<YYYY-MM-DD>.md` 報告
2. THE Prompt_Engine SHALL 在報告中列出所有 `review_due` 已過期的概念，並為每個過期概念產生 1 題複習題
3. THE Prompt_Engine SHALL 在報告中偵測並列出同一概念在不同檔案中說法不一致的地方
4. THE Prompt_Engine SHALL 在報告中列出 `_drafts/` 中超過 7 天未 promote 的概念
5. THE Prompt_Engine SHALL 在報告中彙整各概念檔「我的疑問」段落的內容，並附上建議處理方式
6. THE Prompt_Engine SHALL 在報告中產生 5-10 題本週複習題包，優先取自 `quiz/bank.json` 中 `next_review <= today` 的題目
7. THE Prompt_Engine SHALL 不直接修改 `concepts/` 目錄中的任何檔案內容
8. WHEN weekly-refine 執行完成，THE Prompt_Engine SHALL 更新 `quiz/bank.json` 中的 `next_review` 欄位（依據 SM-2 演算法）
9. WHEN weekly-refine 執行完成，THE Prompt_Engine SHALL 重新產生 `_index/concepts.md`、`_index/topics.md`、`_index/tags.md`
10. WHEN weekly-refine 執行完成，THE Prompt_Engine SHALL 在 `_index/refine-log.md` 記錄本次執行（時間、處理數量、報告路徑）

### 需求 13：SM-2 間隔重複排程

**使用者故事：** 身為使用者，我希望題庫能根據我的答題表現自動調整複習間隔，以便有效對抗遺忘曲線。

#### 驗收標準

1. WHEN 使用者答對一題，THE SM2_Scheduler SHALL 計算新的 `interval_days = interval_days * ease_factor`，並維持 `ease_factor` 不變
2. WHEN 使用者答錯一題，THE SM2_Scheduler SHALL 將 `interval_days` 重設為 1，並將 `ease_factor` 調整為 `max(1.3, ease_factor - 0.2)`
3. THE SM2_Scheduler SHALL 使用 `ease_factor = 2.5` 作為每題的預設值
4. WHEN 排程計算完成，THE SM2_Scheduler SHALL 更新 `quiz/bank.json` 中對應題目的 `next_review`、`interval_days`、`ease_factor` 與 `history` 欄位

### 需求 14：概念檔格式規範

**使用者故事：** 身為使用者，我希望所有概念檔遵循統一格式，以便 AI Agent 能一致地讀取與更新。

#### 驗收標準

1. THE Knowledge_Base SHALL 要求每個概念檔包含以下段落：一句話定義、為什麼存在/解決什麼問題、關鍵字、相關概念（使用 `[[concept-id]]` 格式的雙向連結）、深度等級、最後更新、來源、摘要（3-5 句）、範例（程式碼或場景）、我的疑問
2. THE Knowledge_Base SHALL 要求概念檔的 depth 欄位使用 1-4 的整數（1=表面、2=能解釋、3=能應用、4=能教）
3. WHEN 概念檔的 `review_due` 日期已過，THE Knowledge_Base SHALL 在 weekly-refine 報告中標記該概念為待複習

### 需求 15：四階段學習流程支援

**使用者故事：** 身為使用者，我希望對任何新主題都能依循「地圖建立 → 廣度掃描 → 深度按需 → 複習排程」的四階段流程學習。

#### 驗收標準

1. WHEN 新來源匯入完成，THE Prompt_Engine SHALL 在 `notes.md` 中產出知識地圖，包含 5-10 個核心概念、進階主題、依賴的前置知識（第一階段：地圖建立）
2. WHEN 知識地圖產出完成，THE Prompt_Engine SHALL 為每個核心概念提供 3-5 句摘要與 1-2 題選擇題或簡答題（第二階段：廣度掃描）
3. WHEN 使用者選定特定概念進行深入學習，THE Prompt_Engine SHALL 抓取對應的程式碼、文件或相關資料進行深入講解，並配合應用題（第三階段：深度按需）
4. WHEN 使用者完成答題，THE SM2_Scheduler SHALL 將答錯的題目排入間隔重複佇列（第四階段：複習排程）

### 需求 16：DeepWiki 整合

**使用者故事：** 身為使用者，我希望能透過 DeepWiki 快速取得 GitHub repo 的結構化知識，以便加速 repo 類型來源的匯入。

#### 驗收標準

1. THE Knowledge_Base SHALL 在 `_scripts/` 中提供 `ingest-deepwiki.sh` 腳本，支援使用 `deepwiki-to-md` CLI 下載 DeepWiki wiki 內容
2. WHEN 使用 DeepWiki 匯入，THE Ingest_Pipeline SHALL 將下載的 wiki 內容存放於 `sources/repos/<slug>/deepwiki-snapshot/` 目錄
3. THE Knowledge_Base SHALL 支援透過 MCP server 設定（`.mcp.json`）讓 AI Agent 即時查詢 DeepWiki

### 需求 17：Ingest 腳本提供

**使用者故事：** 身為使用者，我希望有現成的自動化腳本處理各類來源匯入，以便減少手動操作。

#### 驗收標準

1. THE Knowledge_Base SHALL 在 `_scripts/` 目錄中提供以下腳本：`ingest-youtube.sh`、`ingest-pdf.sh`、`ingest-deepwiki.sh`
2. WHEN 執行 `ingest-youtube.sh` 並提供 YouTube URL，THE Ingest_Pipeline SHALL 完成字幕下載（或 Whisper API 轉錄）、Markdown 轉換、meta.yaml 建立的完整流程
3. WHEN 執行 `ingest-pdf.sh` 並提供 PDF 檔案路徑，THE Ingest_Pipeline SHALL 完成文字擷取、Markdown 轉換、meta.yaml 建立的完整流程
4. WHEN 執行 `ingest-deepwiki.sh` 並提供 DeepWiki URL，THE Ingest_Pipeline SHALL 完成 wiki 下載、Markdown 轉換、meta.yaml 建立的完整流程

### 需求 18：三個核心 Prompt 檔案

**使用者故事：** 身為使用者，我希望知識庫內建三個核心 Prompt 檔案，以便 AI Agent 能重複使用標準化的處理流程。

#### 驗收標準

1. THE Knowledge_Base SHALL 在 `_scripts/prompts/` 目錄中提供 `new-source.md`、`promote-concept.md`、`weekly-refine.md` 三個 Prompt 檔案
2. THE Knowledge_Base SHALL 確保 `new-source.md` 的內容符合需求 10 定義的輸入、輸出與行為規範
3. THE Knowledge_Base SHALL 確保 `promote-concept.md` 的內容符合需求 11 定義的輸入、輸出與行為規範
4. THE Knowledge_Base SHALL 確保 `weekly-refine.md` 的內容符合需求 12 定義的輸入、輸出與行為規範

### 需求 19：OpenAI Whisper API 整合

**使用者故事：** 身為使用者，我希望在需要語音轉文字時統一使用 OpenAI Whisper API，以便簡化設定並避免本機環境依賴。

#### 驗收標準

1. WHEN 需要將音訊轉為逐字稿，THE Ingest_Pipeline SHALL 呼叫 OpenAI Whisper API 進行轉錄
2. THE Ingest_Pipeline SHALL 支援設定 OpenAI API key（透過環境變數 `OPENAI_API_KEY`）
3. IF OpenAI Whisper API 呼叫失敗，THEN THE Ingest_Pipeline SHALL 記錄錯誤訊息並提示使用者檢查 API key 或網路連線
4. WHEN Whisper API 回傳逐字稿，THE Ingest_Pipeline SHALL 將結果轉換為 SRT 或 Markdown 格式並存入對應的 source 目錄

### 需求 20：主題層（Topics）管理

**使用者故事：** 身為使用者，我希望能建立跨概念的學習路徑（主題），以便組織相關概念進行系統性學習。

#### 驗收標準

1. THE Knowledge_Base SHALL 支援在 `topics/` 目錄中建立主題檔案，每個主題為一個 Markdown 檔案
2. THE Knowledge_Base SHALL 要求主題檔案包含：主題名稱、涵蓋的概念清單（連結至 `concepts/`）、建議學習順序
3. WHEN weekly-refine 執行時，THE Prompt_Engine SHALL 更新 `_index/topics.md` 以反映最新的主題與概念對應關係

### 需求 21：來源層與概念層分離

**使用者故事：** 身為使用者，我希望原始材料（來源）與提煉的知識（概念）嚴格分離，以便獨立管理與更新。

#### 驗收標準

1. THE Knowledge_Base SHALL 將所有原始材料的處理結果存放於 `sources/` 目錄，將所有提煉的知識存放於 `concepts/` 目錄
2. THE Knowledge_Base SHALL 透過 concept frontmatter 的 `sources` 欄位建立概念到來源的正向連結
3. THE Knowledge_Base SHALL 透過 source 的 `meta.yaml` 中 `related_concepts` 欄位建立來源到概念的反向連結
4. THE Prompt_Engine SHALL 確保正向連結與反向連結雙向一致

### 需求 22：互動式答題（Quiz Session + CLI）

**使用者故事：** 身為使用者，我希望能在終端機中進行互動式答題，出題前先看相關概念的摘要複習，系統根據我的作答結果即時更新 SM-2 排程。同時希望答題邏輯與介面分離，以便未來透過 AI Agent 在 Discord/Telegram 等平台進行問答。

#### 驗收標準

1. THE Knowledge_Base SHALL 在 `_scripts/` 目錄中提供 `quiz_session.py`（純邏輯層，無 I/O）與 `quiz_cli.py`（CLI 介面層）
2. WHEN 使用者啟動答題 session，THE Quiz_Session SHALL 從 `quiz/bank.json` 中選取到期題目，並從對應的 concept 檔中擷取摘要段落作為複習材料（`review_materials`），一次只給本次考試涵蓋的概念摘要
3. THE Quiz_Session SHALL 所有函式的輸入輸出皆為 dict/JSON 格式，不包含任何 I/O 操作（不呼叫 `input()`/`print()`），以便 AI Agent 或外部 bot 直接呼叫
4. THE Quiz_Session SHALL 根據題型呈現不同的互動方式：選擇題自動比對答案、簡答題與應用題由使用者自評對錯
5. WHEN 使用者完成一題作答，THE Quiz_Session SHALL 立即呼叫 SM2_Scheduler 更新該題的 `interval_days`、`ease_factor`、`next_review` 與 `history`
6. WHEN 所有題目作答完成，THE Quiz_Session SHALL 回傳本次答題統計（總題數、答對數、答錯數、答對率、涵蓋的概念清單）
7. THE Quiz_CLI SHALL 支援以下 CLI 參數：`--count`（題數，預設 10）、`--concept`（指定概念 ID）、`--bank`（指定 bank.json 路徑）
