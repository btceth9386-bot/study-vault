# Architecture: Exobrain Knowledge Base System

## System Architecture

Exobrain follows a **pipeline architecture** with strict layer separation. External learning materials flow through an ingest pipeline, get refined by AI agents, and become quizzable knowledge assets.

### High-Level Architecture

```mermaid
graph TB
    subgraph Input["Input Sources (6 types)"]
        YT[YouTube Video]
        PDF[PDF Document]
        GH[GitHub Repo]
        WEB[Web Article]
        POD[Podcast]
        EPUB[epub Book]
    end

    subgraph Pipeline["Ingest Pipeline Layer"]
        direction LR
        IY["ingest-youtube.sh"]
        IP["ingest-pdf.sh"]
        ID["ingest-deepwiki.sh"]
        IA["ingest-article.js"]
        IPO["ingest-podcast.sh"]
        IB["ingest-book.py"]
    end

    subgraph KB["Knowledge Base (4 Layers)"]
        SRC["sources/ (append-only)"]
        DRAFTS["_drafts/ (AI candidates)"]
        CONCEPTS["concepts/ (promoted assets)"]
        QUIZ["quiz/ (SM-2 scheduled)"]
    end

    subgraph Engine["Prompt Engine"]
        NS["new-source.md"]
        PC["promote-concept.md"]
        WR["weekly-refine.md"]
    end

    Input --> Pipeline
    Pipeline --> SRC
    SRC -->|new-source| DRAFTS
    DRAFTS -->|promote-concept| CONCEPTS
    CONCEPTS --> QUIZ
    WR -.->|weekly report| KB
```

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Speech-to-text | OpenAI Whisper API only | No local GPU dependency; $0.006/min cost |
| Version control | Git + GitHub Free | Only refined text tracked; large files excluded via .gitignore |
| Script languages | Bash + Python + Node.js | Bash for pipeline orchestration, Python for complex logic, Node.js for HTML conversion |
| Data format | Markdown + YAML + JSON | Git-friendly, AI-readable, exportable to Obsidian/Logseq |
| Concept management | Draft-then-promote | User retains final review authority; AI never writes directly to concepts/ |

## Layer Separation

The system enforces four strict layers with controlled write access:

```mermaid
flowchart LR
    L1["Source Layer<br/>sources/<br/><i>append-only</i>"]
    L2["Draft Layer<br/>_drafts/<br/><i>AI candidates</i>"]
    L3["Concept Layer<br/>concepts/<br/><i>promoted only</i>"]
    L4["Quiz Layer<br/>quiz/<br/><i>SM-2 state</i>"]

    L1 -->|"new-source prompt<br/>(can write)"| L2
    L2 -->|"promote-concept prompt<br/>(can write)"| L3
    L3 -->|"quiz generation"| L4

    style L1 fill:#e1f5fe
    style L2 fill:#fff3e0
    style L3 fill:#e8f5e9
    style L4 fill:#f3e5f5
```

**Write access constraints:**
- `new-source` → writes to `sources/` and `_drafts/` only
- `promote-concept` → writes to `concepts/`, `quiz/`, `_index/`
- `weekly-refine` → writes to `_inbox/` (reports), `quiz/`, `_index/`; **cannot modify `concepts/`**

## Four-Stage Learning Flow

Every new topic follows this progression:

```mermaid
flowchart TD
    S1["Stage 1: Map Building<br/>AI reads source → produces knowledge map<br/>5-10 core concepts, prerequisites"]
    S2["Stage 2: Breadth Scan<br/>3-5 sentence summary per concept<br/>1-2 quiz questions each"]
    S3["Stage 3: Depth on Demand<br/>User picks topics of interest<br/>Deep dive with application questions"]
    S4["Stage 4: Review Schedule<br/>Wrong answers enter SM-2 queue<br/>Spaced repetition: 1d → 3d → 1w"]

    S1 --> S2 --> S3 --> S4
    S4 -->|"Incorrect answers"| S4
```

## External Service Integration

```mermaid
graph LR
    subgraph Tools["External Tools"]
        YTDLP[yt-dlp]
        WHISPER[OpenAI Whisper API]
        DW[deepwiki-to-md CLI]
        READ["Readability + Turndown"]
        PDFT["pdftotext / Marker"]
        EBOOK[ebooklib / pandoc]
    end

    subgraph Scripts["Ingest Scripts"]
        IY[ingest-youtube.sh] --> YTDLP
        IY --> WHISPER
        IP[ingest-pdf.sh] --> PDFT
        ID[ingest-deepwiki.sh] --> DW
        IA[ingest-article.js] --> READ
        IPO[ingest-podcast.sh] --> WHISPER
        IB[ingest-book.py] --> EBOOK
    end
```
