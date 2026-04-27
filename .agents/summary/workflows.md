# Workflows: Exobrain Knowledge Base System

## 1. Knowledge Base Initialization

```mermaid
flowchart TD
    A["Run init-kb.sh [target-dir]"] --> B[Create directory skeleton]
    B --> C["Generate README.md"]
    B --> D["Generate .gitignore"]
    B --> E["Generate example files"]
    B --> F["Generate index files"]
    E --> E1["Example source (meta.yaml + notes.md)"]
    E --> E2["Example concept (full frontmatter)"]
    E --> E3["Example quiz (bank.json with 1 question)"]
    F --> F1["_index/concepts.md"]
    F --> F2["_index/topics.md"]
    F --> F3["_index/tags.md"]
```

## 2. Source Ingestion (General Flow)

```mermaid
flowchart TD
    A[User provides source URL/path] --> B{Source type?}
    B -->|YouTube| C[ingest-youtube.sh]
    B -->|PDF| D[ingest-pdf.sh]
    B -->|GitHub repo| E[ingest-deepwiki.sh]
    B -->|Web article| F[ingest-article.js]
    B -->|Podcast| G[ingest-podcast.sh]
    B -->|epub| H[ingest-book.py]

    C --> I[sources/videos/slug/]
    D --> J[sources/type/slug/]
    E --> K[sources/repos/slug/]
    F --> L[sources/articles/slug/]
    G --> M[sources/podcasts/slug/]
    H --> N[sources/books/slug/]

    I & J & K & L & M & N --> O[Run new-source prompt]
    O --> P[_drafts/ candidates created]
    O --> Q[_index/ updated]
```

## 3. YouTube Ingestion (Detailed)

```mermaid
flowchart TD
    A[YouTube URL] --> B[yt-dlp: try CC subtitles]
    B --> C{Subtitles found?}
    C -->|Yes| D[srt_to_markdown]
    C -->|No| E[yt-dlp: try auto-generated]
    E --> F{Auto subs found?}
    F -->|Yes| D
    F -->|No| G[yt-dlp: download audio]
    G --> H[whisper_transcribe.py → Whisper API]
    H --> D
    D --> I["Create sources/videos/slug/"]
    I --> I1[meta.yaml]
    I --> I2[transcript.md]
    I --> I3[highlights.md]
    I --> J[Audio file → .gitignore]
```

## 4. DeepWiki Ingestion (Detailed)

```mermaid
flowchart TD
    A[GitHub repo URL] --> B[Convert to DeepWiki URL]
    B --> C[deepwiki-to-md CLI download]
    C --> D{Success?}
    D -->|Yes| E[Save to deepwiki-snapshot/]
    E --> F[Generate notes.md summary]
    F --> G[Create meta.yaml]
    G --> H[Prompt: run new-source]
    D -->|No - wiki not built| I["Prompt user: visit deepwiki.com<br/>to trigger wiki build"]
    D -->|No - private repo| J["Error: DeepWiki only supports<br/>public repos"]
```

## 5. Draft-to-Concept Promotion

```mermaid
flowchart TD
    A["_drafts/concept.md exists"] --> B[User reviews draft]
    B --> C{Approve?}
    C -->|No| D[Delete draft]
    C -->|Yes| E[Run promote-concept prompt]
    E --> F["Create concepts/category/concept-id.md"]
    F --> F1["Feynman-style summary"]
    F --> F2["≥1 concrete example"]
    F --> F3["depth=2, review_due=today+3d"]
    E --> G["Add ≥2 quiz questions to bank.json"]
    E --> H["Update bidirectional links"]
    E --> I["Update _index/concepts.md<br/>(draft → active)"]
    E --> J["Remove from _drafts/"]
```

## 6. Weekly Refine

```mermaid
flowchart TD
    A[Trigger weekly-refine] --> B[Scan entire KB state]
    B --> C["Identify overdue concepts<br/>(review_due < today)"]
    B --> D["Detect contradictions<br/>across concept files"]
    B --> E["Find stale drafts<br/>(>7 days in _drafts/)"]
    B --> F["Collect open questions<br/>(我的疑問 sections)"]
    B --> G["Select 5-10 review questions<br/>from bank.json"]

    C & D & E & F & G --> H["Generate _inbox/refine-report-date.md"]
    H --> I["Update quiz/bank.json schedules"]
    H --> J["Regenerate all _index/ files"]
    H --> K["Log to _index/refine-log.md"]
```

## 7. Quiz Session

```mermaid
flowchart TD
    A["User runs quiz_cli.py"] --> B["start_session()"]
    B --> C["Load due questions from bank.json"]
    C --> D["Extract concept summaries<br/>as review materials"]
    D --> E["Display review materials"]
    E --> F["get_next_question()"]
    F --> G{Question type?}
    G -->|Multiple choice| H["Display options A/B/C/D"]
    G -->|Short answer| I["Open text input"]
    G -->|Application| I
    H & I --> J["User submits answer"]
    J --> K["submit_answer()"]
    K --> L{Correct?}
    L -->|Yes| M["interval *= ease_factor"]
    L -->|No| N["interval = 1<br/>ease_factor = max(1.3, ef-0.2)"]
    M & N --> O["Show explanation + next_review"]
    O --> P{More questions?}
    P -->|Yes| F
    P -->|No| Q["get_session_summary()"]
    Q --> R["Display statistics"]
```

## 8. SM-2 Spaced Repetition Cycle

```mermaid
flowchart LR
    A["New question<br/>interval=1, ef=2.5"] --> B["Due for review<br/>(next_review ≤ today)"]
    B --> C{Answer}
    C -->|Correct| D["interval *= ef<br/>ef unchanged"]
    C -->|Incorrect| E["interval = 1<br/>ef = max(1.3, ef-0.2)"]
    D --> F["next_review = today + interval"]
    E --> F
    F --> B
```
