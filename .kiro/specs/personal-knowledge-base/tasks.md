# 實作計畫：個人知識庫系統（Exobrain）

## 概覽

依據設計文件，將系統分為：初始化腳本、核心 Python 模組、Ingest Pipeline 腳本、Node.js 文章匯入、Prompt 檔案五大區塊，逐步實作並整合。每個步驟建立在前一步之上，確保無孤立程式碼。

## 任務

- [ ] 1. 建立專案結構與核心介面
  - [ ] 1.1 建立 `_scripts/` 目錄結構與 Python 套件設定
    - 建立 `_scripts/` 目錄
    - 建立 `requirements.txt`（openai, pyyaml, ebooklib, hypothesis, pytest）
    - 建立 `package.json`（@mozilla/readability, turndown, fast-check, vitest）
    - _Requirements: 1.1, 17.1_

  - [ ] 1.2 實作 `metadata_validator.py`
    - 實作 `validate_source_meta(meta_path)` — 驗證 source meta.yaml 必填欄位（type, title, language, date_consumed, date_added, status）
    - 實作 `validate_concept_frontmatter(concept_path)` — 驗證 concept frontmatter 必填欄位（id, title, depth, review_due, sources）
    - 實作 `validate_quiz_entry(entry)` — 驗證 quiz 題目必填欄位（id, concept_id, type, difficulty, question, answer, explanation, created_at, next_review, interval_days, ease_factor, history）
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 14.1, 14.2_

  - [ ]* 1.3 撰寫 `metadata_validator.py` 的屬性測試
    - **Property 3: Metadata Schema 驗證**
    - 使用 Hypothesis 產生隨機 meta.yaml / frontmatter / quiz entry，隨機移除欄位
    - 驗證：完整欄位 → 空錯誤清單；缺欄位 → 錯誤清單包含該欄位名稱
    - **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 14.1, 14.2**

- [ ] 2. 實作 SM-2 排程器與檔案拆分器
  - [ ] 2.1 實作 `sm2_scheduler.py`
    - 實作 `update_on_correct(question)` — interval_days *= ease_factor，ease_factor 不變
    - 實作 `update_on_incorrect(question)` — interval_days = 1，ease_factor = max(1.3, ease_factor - 0.2)
    - 實作 `get_due_questions(bank_path, today)` — 取得 next_review <= today 的題目
    - 實作 `update_bank(bank_path, question_id, correct)` — 更新 bank.json 中指定題目
    - 預設 ease_factor = 2.5，確保 ease_factor >= 1.3 下限
    - _Requirements: 13.1, 13.2, 13.3, 13.4_

  - [ ]* 2.2 撰寫 `sm2_scheduler.py` 的屬性測試
    - **Property 9: SM-2 排程計算正確性**
    - 使用 Hypothesis 產生隨機 interval_days（正數）和 ease_factor（>= 1.3）
    - 驗證：答對時 interval 正確計算、答錯時重設為 1、ease_factor 永遠 >= 1.3、history 新增一筆
    - **Validates: Requirements 13.1, 13.2, 13.3, 13.4, 15.4**

  - [ ] 2.3 實作 `file_splitter.py`
    - 實作 `split_markdown(content, max_bytes=1_000_000)` — 以標題或段落為邊界拆分
    - 每個片段加上 part 編號
    - 若段落仍超過 max_bytes，以句子為邊界再拆分
    - _Requirements: 2.3, 2.4, 4.4_

  - [ ]* 2.4 撰寫 `file_splitter.py` 的屬性測試
    - **Property 1: 檔案拆分大小不變量**
    - 使用 Hypothesis 產生隨機長度的 Markdown 字串（含標題、段落）
    - 驗證：每個片段 <= max_bytes，所有片段串接後文字內容與原始一致
    - **Validates: Requirements 2.4, 4.4**

- [ ] 3. 實作 Quiz 系統
  - [ ] 3.1 實作 `quiz_manager.py`
    - 實作 `add_questions(bank_path, questions)` — 新增題目到 bank.json
    - 實作 `get_review_pack(bank_path, count=10, today=None)` — 取得複習題包，優先 next_review <= today，若超過 count 題到期則選最早的
    - _Requirements: 12.6, 15.4_

  - [ ]* 3.2 撰寫 `quiz_manager.py` 的屬性測試
    - **Property 8: 複習題包優先排序與數量**
    - 使用 Hypothesis 產生隨機 quiz bank（不同 next_review 日期）
    - 驗證：回傳數量 5-10（不足 5 題回傳全部）、優先包含到期題目、超過 10 題取最早的
    - **Validates: Requirements 12.6**

  - [ ] 3.3 實作 `quiz_session.py`（純邏輯層）
    - 實作 `start_session(bank_path, kb_root, count, concept_id, today)` — 建立 session，回傳 review_materials + questions_preview
    - 實作 `get_next_question(session_id)` — 取得下一題（不含答案）
    - 實作 `submit_answer(session_id, question_id, answer, self_eval)` — 提交答案，MC 自動判斷，SA/App 使用者自評
    - 實作 `get_session_summary(session_id)` — 回傳統計（total, correct, incorrect, accuracy, concepts_reviewed, next_reviews）
    - 所有函式輸入輸出皆為 dict/JSON，不含任何 I/O
    - _Requirements: 22.1, 22.2, 22.3, 22.4, 22.5, 22.6_

  - [ ]* 3.4 撰寫 `quiz_session.py` 的屬性測試
    - **Property 13: Quiz Runner 答題後排程更新一致性**
    - 使用 Hypothesis 產生隨機答題序列（多題、隨機對錯）
    - 驗證：每題 history 長度增加 1、最後一筆 result 與作答一致、correct + incorrect == total
    - **Validates: Requirements 22.4, 22.5**

  - [ ] 3.5 實作 `quiz_cli.py`（CLI 介面層）
    - 解析 CLI 參數：`--count`、`--concept`、`--bank`
    - 呼叫 quiz_session.py API 驅動互動流程
    - 顯示複習材料 → 逐題出題 → 顯示對錯與解釋 → 顯示統計
    - _Requirements: 22.1, 22.7_

- [ ] 4. 檢查點 — 確認核心模組測試通過
  - 確保所有測試通過，如有疑問請詢問使用者。

- [ ] 5. 實作 Whisper 轉錄與索引產生器
  - [ ] 5.1 實作 `whisper_transcribe.py`
    - 實作 `transcribe(audio_path, language="auto")` — 呼叫 OpenAI Whisper API
    - 實作 `srt_to_markdown(srt_path)` — 將 SRT 轉為清理後的 Markdown（移除時間戳、合併段落）
    - 透過 `OPENAI_API_KEY` 環境變數取得 API key，未設定時報錯退出
    - _Requirements: 3.2, 3.3, 19.1, 19.2, 19.3, 19.4_

  - [ ]* 5.2 撰寫 `srt_to_markdown` 的屬性測試
    - **Property 2: SRT 轉 Markdown 內容保留**
    - 使用 Hypothesis 產生隨機 SRT 內容（隨機編號、時間戳、文字）
    - 驗證：原始 SRT 中所有文字段落都出現在產出的 Markdown 中
    - **Validates: Requirements 3.2**

  - [ ] 5.3 實作 `index_generator.py`
    - 實作 `generate_concepts_index(kb_root)` — 掃描 concepts/ 和 _drafts/，產生 concepts.md
    - 實作 `generate_topics_index(kb_root)` — 掃描 topics/，產生 topics.md
    - 實作 `generate_tags_index(kb_root)` — 掃描所有 concept frontmatter 的 tags，產生 tags.md
    - _Requirements: 1.4, 12.9, 20.3_

- [ ] 6. 實作初始化腳本
  - [ ] 6.1 實作 `init-kb.sh`
    - 建立所有必要目錄（_inbox/, _drafts/, concepts/, sources/ 含子目錄, quiz/, _index/, topics/, _scripts/prompts/）
    - 產生 README.md（使用說明）
    - 產生範例 source（含 meta.yaml + notes.md）
    - 產生範例 concept（含完整 frontmatter + 內文結構）
    - 產生範例 quiz（bank.json 含至少 1 題）
    - 產生三個索引檔（concepts.md, topics.md, tags.md）
    - 產生 .gitignore（排除音訊、影片、大型 PDF、cloned repo、epub）
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.5_

  - [ ]* 6.2 撰寫 `init-kb.sh` 的整合測試（bats-core）
    - 驗證目錄結構完整性
    - 驗證範例檔案內容正確
    - 驗證 .gitignore 包含所有必要排除規則
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 7. 實作 Ingest Pipeline 腳本
  - [ ] 7.1 實作 `ingest-youtube.sh`
    - 使用 yt-dlp 嘗試下載字幕（優先人工 CC → 自動生成）
    - 若無字幕 → 下載音訊 → 呼叫 whisper_transcribe.py
    - 呼叫 srt_to_markdown 轉換 SRT
    - 建立 sources/videos/<slug>/（meta.yaml, transcript.md, highlights.md）
    - 確保音訊檔列入 .gitignore
    - 啟動時檢查 yt-dlp 與 OPENAI_API_KEY
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 17.2, 19.1_

  - [ ] 7.2 實作 `ingest-pdf.sh`
    - 使用 pdftotext 或 Marker 將 PDF 轉為 Markdown
    - 若超過 1 MB → 呼叫 file_splitter.py
    - 建立 sources/<type>/<slug>/（meta.yaml, notes.md）
    - 原始 PDF 列入 .gitignore
    - 啟動時檢查 pdftotext/Marker 是否安裝
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 17.3_

  - [ ] 7.3 實作 `ingest-deepwiki.sh`
    - 接受 GitHub repo URL 或 DeepWiki URL
    - 自動轉換 GitHub URL 為 DeepWiki URL
    - 使用 deepwiki-to-md CLI 下載
    - 成功：建立 sources/repos/<slug>/（meta.yaml, notes.md, deepwiki-snapshot/）
    - 失敗（未建立 wiki）：提示使用者前往 deepwiki.com 觸發建立
    - 失敗（private repo）：報錯提示僅支援 public repo
    - 啟動時檢查 deepwiki-to-md 是否安裝
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 16.1, 16.2, 17.4_

  - [ ] 7.4 實作 `ingest-article.js`（Node.js）
    - 使用 @mozilla/readability 擷取文章內容
    - 使用 turndown 將 HTML 轉為 Markdown
    - 建立 sources/articles/<slug>/（meta.yaml, notes.md）
    - _Requirements: 6.1, 6.2_

  - [ ] 7.5 實作 `ingest-podcast.sh`
    - 接受音訊檔案路徑或 URL
    - 呼叫 whisper_transcribe.py 產生逐字稿
    - 建立 sources/podcasts/<slug>/（meta.yaml, transcript.md, highlights.md）
    - 音訊檔列入 .gitignore
    - _Requirements: 7.1, 7.2, 7.3_

  - [ ] 7.6 實作 `ingest-book.py`
    - 使用 ebooklib 解析 epub
    - 拆分為逐章 Markdown 檔案
    - 建立 sources/books/<slug>/（meta.yaml, chapter-01.md, chapter-02.md, ...）
    - 原始 epub 列入 .gitignore
    - _Requirements: 8.1, 8.2, 8.3_

  - [ ]* 7.7 撰寫 Ingest Pipeline 整合測試（bats-core）
    - 使用 mock/stub 替代外部服務（yt-dlp, Whisper API, DeepWiki CLI）
    - 驗證 ingest-youtube.sh 完整流程（字幕路徑 + Whisper fallback 路徑）
    - 驗證 ingest-pdf.sh 完整流程（含大檔拆分）
    - 驗證 ingest-deepwiki.sh 完整流程（成功 + 失敗路徑）
    - _Requirements: 3.1-3.6, 4.1-4.4, 5.1-5.4, 17.2, 17.3, 17.4_

- [ ] 8. 檢查點 — 確認 Ingest Pipeline 測試通過
  - 確保所有測試通過，如有疑問請詢問使用者。

- [ ] 9. 實作 Prompt 檔案與 MCP 設定
  - [ ] 9.1 撰寫 `_scripts/prompts/new-source.md`
    - 定義輸入：_inbox/ 中的來源內容 + 基本 metadata
    - 定義輸出：sources/<type>/<slug>/ 完整結構 + _drafts/ 候選概念 + _index 更新
    - 定義約束：不能直接寫入 concepts/
    - 定義 Agent 行為：識別 5-10 個核心概念、跨參照既有概念、標記 merge_candidate
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 18.2_

  - [ ] 9.2 撰寫 `_scripts/prompts/promote-concept.md`
    - 定義輸入：_drafts/<concept>.md + 對應來源 + 既有 concepts/ 結構
    - 定義輸出：concepts/<category>/<concept-id>.md + quiz/bank.json 新題 + _index 更新
    - 定義約束：Feynman 風格、至少 1 範例、depth=2 預設、反向連結、review_due = today + 3 天
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 18.3_

  - [ ] 9.3 撰寫 `_scripts/prompts/weekly-refine.md`
    - 定義輸入：整個知識庫狀態 + 上次執行時間戳
    - 定義輸出：_inbox/refine-report-<date>.md（過期概念、矛盾偵測、過期草稿、疑問彙整、複習題包）
    - 定義約束：不能修改 concepts/、可更新 quiz/bank.json 與 _index/
    - 定義 SM-2 更新邏輯與 refine-log.md 記錄
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8, 12.9, 12.10, 18.4_

  - [ ] 9.4 建立 `.mcp.json`（DeepWiki MCP server 設定）
    - 設定 deepwiki MCP server URL
    - _Requirements: 16.3_

- [ ] 10. 整合與連接
  - [ ] 10.1 確保所有 Ingest 腳本正確呼叫核心 Python 模組
    - ingest-youtube.sh 呼叫 whisper_transcribe.py 與 metadata_validator.py
    - ingest-pdf.sh 呼叫 file_splitter.py 與 metadata_validator.py
    - ingest-podcast.sh 呼叫 whisper_transcribe.py
    - ingest-book.py 呼叫 file_splitter.py
    - 所有腳本產出的 meta.yaml 通過 metadata_validator 驗證
    - _Requirements: 9.4, 17.2, 17.3, 17.4_

  - [ ] 10.2 確保 quiz_session.py 正確整合 sm2_scheduler.py 與 quiz_manager.py
    - submit_answer 呼叫 SM-2 更新
    - start_session 呼叫 get_review_pack
    - 驗證端到端流程：啟動 session → 答題 → 更新排程 → 取得統計
    - _Requirements: 22.2, 22.5, 22.6_

  - [ ]* 10.3 撰寫端到端整合測試
    - 測試完整流程：init-kb → ingest → quiz session
    - 驗證檔案結構、metadata 完整性、SM-2 排程更新
    - _Requirements: 1.1-1.5, 9.1-9.4, 13.1-13.4, 22.1-22.7_

- [ ] 11. 最終檢查點 — 確認所有測試通過
  - 確保所有測試通過，如有疑問請詢問使用者。

## 備註

- 標記 `*` 的任務為選填，可跳過以加速 MVP 開發
- 每個任務都引用對應的需求編號以確保可追溯性
- 檢查點確保漸進式驗證
- 屬性測試驗證通用正確性屬性，單元測試驗證具體範例與邊界條件
- 所有 Python 模組放在 `_scripts/` 目錄下
- Bash 腳本使用 `set -euo pipefail` 確保錯誤處理
