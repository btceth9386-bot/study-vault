# Codebase Information: Exobrain (study-vault)

## Project Status

**Phase: Design / Pre-implementation**
No implementation code exists yet. The repository contains specification documents only.

## Project Description

Exobrain is a personal knowledge base system that ingests learning materials from multiple sources (YouTube, PDF, GitHub repos, web articles, podcasts, epub books), converts them to unified Markdown format, and uses AI Agents to continuously refine the content into reviewable, quizzable personal knowledge assets.

Core flow: **Multiple sources → Ingest Pipeline → Unified Markdown → AI Agent refine → Reviewable & quizzable assets**

## Language

All specification documents are written in **Traditional Chinese (zh-TW)**.

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Pipeline orchestration | Bash | Simple ingest pipeline scripts |
| Core logic | Python | Whisper API, SM-2 scheduling, quiz management, metadata validation, PDF conversion |
| Web content | Node.js | HTML → Markdown conversion (Readability + Turndown) |
| Data format | Markdown + YAML frontmatter + JSON | Git-friendly, AI-readable, exportable to Obsidian/Logseq |
| Speech-to-text | OpenAI Whisper API | Audio/video transcription ($0.006/min) |
| Video tools | yt-dlp | Subtitle/audio download |
| PDF tools | pdftotext / Marker | PDF to text conversion |
| Repo knowledge | DeepWiki (deepwiki-to-md CLI) | GitHub repo wiki generation |
| Version control | Git + GitHub Free | Only refined text files tracked |

## File Inventory

| File | Purpose |
|------|---------|
| `personal-knowledge-base-design-v2.md` | Original design spec v2 (standalone, comprehensive) |
| `.kiro/specs/personal-knowledge-base/requirements.md` | Formal requirements (22 requirements with acceptance criteria) |
| `.kiro/specs/personal-knowledge-base/design.md` | Detailed design document (architecture, components, interfaces, data models) |
| `.kiro/specs/personal-knowledge-base/tasks.md` | Implementation plan (11 task groups with sub-tasks) |
| `.gitignore` | Excludes `.kiro`, `.claude`, `.codex`, `.copilot`, `.gemini` directories |

## Planned Directory Structure

```
my-kb/
├── _inbox/          # Staging area for new sources
├── _drafts/         # AI-generated draft concepts awaiting review
├── concepts/        # Promoted knowledge assets (by category)
├── sources/         # Processed source materials
│   ├── repos/       # GitHub repositories
│   ├── videos/      # YouTube videos
│   ├── books/       # epub books
│   ├── articles/    # Web articles
│   ├── podcasts/    # Podcast episodes
│   └── papers/      # Academic papers
├── quiz/            # Quiz bank (bank.json)
├── _index/          # Auto-generated indexes
├── topics/          # Cross-concept learning paths
└── _scripts/        # All automation scripts + prompts
    └── prompts/     # 3 core AI prompts
```

## Architecture Overview

```mermaid
graph TB
    subgraph Sources["Input Sources"]
        YT[YouTube]
        PDF[PDF]
        GH[GitHub Repo]
        WEB[Web Article]
        POD[Podcast]
        EPUB[epub Book]
    end

    subgraph Ingest["Ingest Pipeline Layer"]
        IY["ingest-youtube.sh<br/>(Bash+Python)"]
        IP["ingest-pdf.sh<br/>(Bash+Python)"]
        ID["ingest-deepwiki.sh<br/>(Bash)"]
        IA["ingest-article.js<br/>(Node.js)"]
        IPO["ingest-podcast.sh<br/>(Bash+Python)"]
        IB["ingest-book.py<br/>(Python)"]
    end

    subgraph External["External Services"]
        YTDLP[yt-dlp]
        WHISPER[OpenAI Whisper API]
        DW[DeepWiki CLI/MCP]
        READ[Readability + Turndown]
        PDFT[pdftotext / Marker]
    end

    subgraph KB["Knowledge Base File System"]
        INBOX[_inbox/]
        SRC[sources/]
        DRAFTS[_drafts/]
        CONCEPTS[concepts/]
        QUIZ[quiz/bank.json]
        INDEX[_index/]
        TOPICS[topics/]
    end

    subgraph Prompts["Prompt Engine"]
        NS[new-source.md]
        PC[promote-concept.md]
        WR[weekly-refine.md]
    end

    subgraph Core["Core Logic (Python)"]
        SM2[SM-2 Scheduler]
        QM[Quiz Manager]
        QS[Quiz Session]
        MV[Metadata Validator]
        FS[File Splitter]
        IG[Index Generator]
    end

    YT --> IY
    PDF --> IP
    GH --> ID
    WEB --> IA
    POD --> IPO
    EPUB --> IB

    IY --> YTDLP
    IY --> WHISPER
    IP --> PDFT
    ID --> DW
    IA --> READ
    IPO --> WHISPER

    IY --> SRC
    IP --> SRC
    ID --> SRC
    IA --> SRC
    IPO --> SRC
    IB --> SRC

    INBOX -->|new-source| NS
    NS --> SRC
    NS --> DRAFTS
    DRAFTS -->|user review + promote| PC
    PC --> CONCEPTS
    PC --> QUIZ
    WR --> INDEX
    WR --> QUIZ

    QUIZ --> SM2
    QUIZ --> QM
    QM --> QS
    SM2 --> QS
    CONCEPTS --> IG
    IG --> INDEX
```

## Data Flow

```mermaid
flowchart TD
    A[External Source] --> B[Ingest Pipeline]
    B --> C[sources/]
    C -->|new-source prompt| D[_drafts/]
    D --> E{User Review}
    E -->|Approve| F[promote-concept prompt]
    E -->|Reject| G[Delete draft]
    F --> H[concepts/]
    F --> I[quiz/bank.json]
    H --> J[weekly-refine prompt]
    J --> K[refine-report]
    I --> L[Quiz Session + SM-2]
    L -->|Update schedule| I
```

## Layer Separation Principle

The system enforces strict layer separation:

```mermaid
graph LR
    subgraph Layer1["Source Layer (sources/)"]
        S1[Append-only processed materials]
    end
    subgraph Layer2["Draft Layer (_drafts/)"]
        S2[AI-generated candidates awaiting review]
    end
    subgraph Layer3["Concept Layer (concepts/)"]
        S3[Promoted knowledge assets]
    end
    subgraph Layer4["Quiz Layer (quiz/)"]
        S4[Structured quiz bank + SM-2 state]
    end

    Layer1 -->|new-source prompt| Layer2
    Layer2 -->|promote-concept prompt| Layer3
    Layer3 -->|weekly-refine prompt| Layer4

    style Layer1 fill:#e1f5fe
    style Layer2 fill:#fff3e0
    style Layer3 fill:#e8f5e9
    style Layer4 fill:#f3e5f5
```

Key constraints:
- `new-source` prompt can only write to `sources/` and `_drafts/`, never directly to `concepts/`
- `weekly-refine` prompt cannot modify any files in `concepts/`
- All writes to `concepts/` must go through `promote-concept` prompt

## Planned Scripts

### Bash Scripts
- `init-kb.sh` — Initialize knowledge base directory skeleton
- `ingest-youtube.sh` — YouTube video ingestion (yt-dlp + Whisper fallback)
- `ingest-pdf.sh` — PDF document ingestion (pdftotext/Marker)
- `ingest-deepwiki.sh` — GitHub repo ingestion via DeepWiki
- `ingest-podcast.sh` — Podcast audio ingestion (Whisper API)

### Python Modules
- `whisper_transcribe.py` — OpenAI Whisper API wrapper + SRT→Markdown conversion
- `sm2_scheduler.py` — SM-2 spaced repetition algorithm
- `metadata_validator.py` — YAML/JSON schema validation
- `quiz_manager.py` — Quiz bank CRUD operations
- `quiz_session.py` — Stateless quiz session logic (no I/O)
- `quiz_cli.py` — Terminal-based quiz interface
- `file_splitter.py` — Markdown file splitting (≤1MB per chunk)
- `index_generator.py` — Auto-generate concept/topic/tag indexes

### Node.js
- `ingest-article.js` — Web article ingestion (Readability + Turndown)

### Prompt Files
- `_scripts/prompts/new-source.md` — Process new source → drafts
- `_scripts/prompts/promote-concept.md` — Draft → formal concept + quiz
- `_scripts/prompts/weekly-refine.md` — Weekly maintenance report

## Design Patterns

- **Draft-then-promote**: AI never writes directly to `concepts/`; all AI output goes to `_drafts/` first for human review
- **Stateless quiz logic**: `quiz_session.py` has no I/O, enabling reuse across CLI, Discord, Telegram
- **SM-2 spaced repetition**: Standard algorithm with ease_factor ≥ 1.3 floor
- **Bidirectional linking**: Concepts link to sources and vice versa via frontmatter fields
- **Feynman Technique**: Concept summaries written in plain language with examples
