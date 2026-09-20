# AI Agent 知識理解與長篇 Markdown 閱讀體驗整理

## 背景

目前的 AI Agent 使用體感有一個很明顯的問題：

> **產生資訊變得非常廉價，但人類理解資訊的成本仍然很高。**

目前已經使用 `web-artifacts-builder`，把 AI Agent 整理出的長篇 Markdown 轉換成較友善的 HTML，閱讀體驗確實比純 Markdown 好，但仍然存在：

- 資訊量太大
- 長文閱讀容易疲勞
- Background、Architecture、Workflow、How-to、Lab 混在一起
- 一次需要在腦中維持太多概念
- 即使內容完整，仍不容易快速建立 mental model
- AI 很容易產出更多文件，但不一定幫助真正理解

目前已有三個實驗頁面：

- https://kiro-langfuse-eval-review.pages.dev/
- https://otel-collector-positioning-review.pages.dev/
- https://langgraph-state-flow-review.pages.dev/

以及目前使用的 Anthropic Skill：

- https://github.com/anthropics/skills/blob/main/skills/web-artifacts-builder/SKILL.md

---

# 一、第一層問題：知識越來越多，如何避免變成文件堆積

這一層是比較大的 knowledge architecture 問題。

目前的模式容易變成：

```text
Topic
  ↓
AI Research
  ↓
Markdown
  ↓
HTML
  ↓
下一個 Topic
  ↓
另一份 Markdown
  ↓
另一份 HTML
```

久了會變成：

```text
Document
Document
Document
Document
Document
```

問題不是文件不存在，而是：

> 新知識沒有被整合進既有 mental model。

比較好的方向是讓 AI 從：

> Documentation Generator

轉成：

> Knowledge Compiler + Tutor

也就是：

```text
Sources / Docs / Repo
        ↓
AI Knowledge Compiler
        ↓
Knowledge Model
   ↙      ↓      ↘
 Map   Concepts   Labs
```

---

## 1. OpenWiki

推薦優先研究：

- https://github.com/langchain-ai/openwiki

OpenWiki 的價值不是「再產一份文件」，而是維護一套：

- Persistent
- Interlinked
- Incrementally updated

的 Wiki。

理想上，知識應從：

```text
otel.html
langfuse.html
langgraph.html
```

慢慢變成：

```text
AI-Agent-Knowledge/

index.md

concepts/
  observability.md
  evaluation.md
  tracing.md
  state-management.md
  agent-runtime.md

tools/
  kiro-cli.md
  langfuse.md
  opentelemetry.md
  langgraph.md

relationships/
  otel-vs-langfuse.md
  langgraph-vs-kiro.md
  tracing-vs-evaluation.md

labs/
  kiro-langfuse-eval.md
  otel-collector.md
  langgraph-state.md
```

新的知識進來時，不是問：

> 要不要再產一份 HTML？

而是問：

1. 這是新的 concept 嗎？
2. 它跟既有 concept 的關係是什麼？
3. 它應該更新哪個 mental model？
4. 是否存在 contradiction / unresolved question？
5. 是否真的值得做成一個 Lab？

---

## 2. LikeC4

推薦：

- https://github.com/likec4/likec4
- https://c4model.com/

LikeC4 的價值是：

> 不要每次產一張互相沒有關係的 Mermaid，而是維護一個 architecture model。

同一套 architecture model 可以有不同視角：

```text
Level 1
AI Agent Platform

Level 2
Observability / Runtime / MCP / Evaluation

Level 3
OTel Collector / Langfuse / LangGraph / Kiro
```

適合做成 zoomable architecture。

例如：

```text
                  AI Agent Platform

                       Slack
                         │
                         ▼
                    ChatOps Agent
                         │
                ┌────────┴────────┐
                ▼                 ▼
           Agent Runtime      MCP / Tools
          Kiro / LangGraph
                │
        ┌───────┴────────┐
        ▼                ▼
 Observability        Evaluation
 OTel / Langfuse    Dataset / Judge
```

再往下點 Observability：

```text
Application
    │
    ├── OTel SDK
    │
    ▼
OTel Collector
    │
    ├── Metrics → Prometheus
    ├── Traces  → Tempo
    └── AI telemetry → Langfuse
```

這比「一張超完整架構圖」更適合建立 mental model。

---

## 3. Kiro Skills + Knowledge Base

Kiro Skill 可以拿來做自己的：

```text
architecture-tutor
```

核心不是一次回答很多，而是使用 Progressive Disclosure。

可以設定類似規則：

```text
Goal:
Help me build a mental model, not generate documentation.

Rules:
1. Start with at most 3 concepts.
2. Explain relationships before implementation.
3. Never introduce more than one new architectural layer at once.
4. Default answer < 300 words.
5. Explain "Why should I care?" before implementation details.
6. Hide implementation details unless requested.
7. Link new concepts to concepts I already know.
8. Ask me to predict before revealing details.
```

例如學 OTel 時，不要一開始丟：

- SDK
- OTLP
- Collector
- Receiver
- Processor
- Exporter
- Trace
- Metric
- Log

而是先：

```text
You already know:

Prometheus → metrics storage/query
Grafana    → visualization

Now add ONE new thing:

OpenTelemetry
     ↓
collect / transport telemetry
     ↓
Prometheus / Tempo / other backend
```

再依照問題逐步展開。

---

## 4. GitNexus / Understand Anything

如果問題不是學一個概念，而是：

> 我要快速理解一個陌生 GitHub Repository。

可以研究：

### GitNexus

- https://github.com/abhigyanpatwari/GitNexus

適合理解：

- AST
- import relations
- function call paths
- execution flow
- code knowledge graph

### Understand Anything

- https://github.com/Egonex-AI/Understand-Anything

比較偏：

- repo structural graph
- domain / business flow
- guided tour
- semantic exploration

這兩者的重點不是「幫你寫更多 docs」，而是：

> 幫你探索程式碼的結構。

---

## 5. Diátaxis

推薦：

- https://diataxis.fr/

Diátaxis 把技術文件拆成四種類型：

```text
Tutorial
How-to
Reference
Explanation
```

很多 AI 長文難讀，是因為四種內容全部混在一起。

例如：

```text
OpenTelemetry 是什麼？        → Explanation
Collector 位在哪？           → Explanation
Collector config 怎麼寫？     → How-to
OTLP 是什麼？                 → Reference
Docker Compose Lab            → Tutorial
```

如果全部塞在同一條線性文章裡，讀者會一直切換 cognition mode。

---

# 二、真正要 Zoom In 的問題：如何讓「一份很長的 Markdown」更容易理解

這是本次討論後半段真正聚焦的問題。

假設現在已經有一份非常完整的 Markdown，裡面包含：

- Background
- Architecture Diagram
- Workflow Diagram
- Concepts
- How it works
- How to use
- Config
- Lab
- Troubleshooting

問題不是內容不夠，而是：

> 怎麼把同樣的內容轉換成「人腦更容易吸收」的形式？

---

# 三、不要只做「Markdown → Better HTML」

目前的做法大概是：

```text
Markdown paragraph
      ↓
HTML paragraph
```

雖然 HTML 排版漂亮很多，但 cognition model 其實沒有變。

更好的方向應該是：

```text
Markdown Knowledge
      ↓
Semantic Analysis
      ↓
Choose the best UI for each concept
```

例如 Architecture 本來是 500 字。

不要只是：

> 500 字 + Card + Header + Better Typography

而是轉成：

```text
┌──────────────────────────────────┐
│ Architecture                     │
│                                  │
│ Kiro → Hook → OTel → Langfuse    │
│              ↓                   │
│           Collector              │
│                                  │
│ [What's Collector?]              │
│ [Why do we need it?]             │
│ [Show implementation details]    │
└──────────────────────────────────┘
```

---

# 四、推薦把一份長 Markdown 拆成 4 種閱讀模式

## Mode 1 — Overview

目標：

> 3 分鐘知道這個東西在幹嘛。

不是 Executive Summary 長文，而是：

```text
OpenTelemetry Collector
────────────────────────────

What problem does it solve?

Application
    │
    ▼
Telemetry
    │
    ▼
[ OTel Collector ]
   │      │      │
   ▼      ▼      ▼
Prom   Tempo   Langfuse


3 things to remember

① Collector ≠ storage
② It receives / processes / exports telemetry
③ It sits between producers and backends


You already know:
Prometheus / Grafana

New concepts:
OTLP / Processor / Exporter
```

可以直接給讀者選擇：

```text
Choose your depth

[ 3-minute overview ]
[ 15-minute guided tour ]
[ Full deep dive ]
[ Jump to lab ]
```

核心概念：

> 讀者控制資訊量，而不是文件控制讀者。

---

## Mode 2 — Guided Tour

這是最值得實驗的模式之一。

把長文改成「一步一畫面」。

例如：

```text
Step 2 of 8

Where does OTel Collector sit?

Application
     │
     ▼
OTel SDK
     │
     ▼
┌───────────────┐
│ OTel Collector│  ← focus here
└───────────────┘
     │
     ▼
Backend


Collector has 3 jobs:

receive → process → export


[← Previous] [Next →]
```

下一步：

```text
Step 3 of 8

What enters the Collector?

           OTLP
            │
            ▼
      ┌───────────┐
      │ Receiver  │
      └───────────┘

OTLP = OpenTelemetry Protocol

[ Why OTLP? ]
[ Show config example ]
```

再下一步：

```text
Step 4 of 8

What happens inside?

Receiver → Processor → Exporter
```

Guided Tour 的價值是：

> 控制 working context。

一次只讓大腦處理一個主要概念。

---

# 五、Slidev：把長文變成 Developer Story

推薦：

- https://github.com/slidevjs/slidev

Slidev 是 Markdown-based developer presentation framework。

可以把：

```text
original.md
    ↓
AI restructuring
    ↓
slides.md
    ↓
Slidev
```

原本：

```text
# Architecture

500 words...

# Workflow

800 words...

# Configuration

600 words...
```

重構成：

```text
---
# What problem are we solving?

---
# Where does Collector sit?

[diagram]

---
# One thing to remember

Collector is not storage.

---
# Data flow

Receiver → Processor → Exporter

---
# Now let's see the config
```

它會強迫 AI 做一件非常有價值的事情：

> 決定「什麼值得獨佔一個畫面」。

這跟單純 summary 不同。

---

# 六、Explore Mode：先看 Map，不要先看文章

一份長文件的入口，可以先變成：

```text
                  OTel
                   │
       ┌───────────┼────────────┐
       │           │            │
      SDK       Collector      OTLP
                   │
          ┌────────┼────────┐
          │        │        │
       Receiver Processor Exporter
                            │
                      ┌─────┼─────┐
                    Prom   Tempo Langfuse
```

每個 Node 可以點：

```text
[Collector]

What?
A telemetry pipeline.

Why?
Decouples applications from telemetry backends.

How?
Receiver → Processor → Exporter

[Learn more →]
```

Map 的主要功能不是取代教材，而是：

> 幫助讀者隨時知道「我現在在哪裡」。

---

# 七、Markmap

推薦：

- https://github.com/dundalek/markmap

Markmap 可以把 Markdown 轉成 interactive mind map。

適合：

- 展開 / 收合 branch
- 快速看整份文件的層級
- 作為 Concept Map
- 作為「You are here」導航

不一定適合當完整教材，但非常適合作為：

```text
Overview
│
├── 🗺 Concept Map
├── 🎓 Guided Tour
├── 📖 Full Reading
└── 🧪 Lab
```

其中的 Concept Map。

---

# 八、Learn Mode 和 Lab Mode 要分開

不要：

```text
What is Collector?
↓
Architecture
↓
OTLP
↓
Docker command
↓
Config
↓
Exporter concept
↓
kubectl
↓
Debug
```

這樣讀者會一直 context switch。

比較好的 UI：

```text
[ Learn ] [ Lab ]
```

Learn：

```text
What is it?
Architecture
Workflow
Key concepts
Tradeoffs
```

Lab：

```text
Prerequisites
Step 1
Step 2
Step 3
Verification
Troubleshooting
```

不是把 Lab 放在文章最下面，而是把它視為：

> 不同 cognition mode。

---

# 九、Checkpoint：不要讓 AI 教材只剩「順順看完」

AI 很容易把內容寫得太順。

讀起來：

```text
嗯
懂
合理
下一段
懂
```

但半小時後可能什麼都沒留下。

所以 Guided Tour 裡可以加入小型 Checkpoint。

例如：

```text
Receiver → Processor → Exporter
```

接著：

```text
Before continuing:

Where would filtering happen?

○ Receiver
○ Processor
○ Exporter

[Check answer]
```

回答後：

```text
✓ Processor

Processors transform or filter
telemetry before export.
```

閱讀模式從：

```text
read
read
read
read
```

變成：

```text
read
 ↓
predict
 ↓
reveal
 ↓
continue
```

這種 Active Recall 對建立記憶非常有幫助。

---

# 十、NotebookLM：不要只用「閱讀」學習

NotebookLM 是另一種值得 A/B Test 的方式。

同一份 Markdown 可以轉成：

- Mind Map
- Audio Overview
- Video Overview
- Slide Deck
- Flashcards
- Quiz
- Study Guide
- Infographic

核心概念：

```text
Reading ≠ learning 的唯一入口
```

例如：

```text
otel-collector-positioning-review.md
        ↓
NotebookLM
        ↓
Mind Map
        ↓
Audio Overview
        ↓
回頭看 Architecture
        ↓
最後看 Config / Lab
```

甚至可以給 NotebookLM 一個 Persona：

```text
Explain this to a senior DevOps engineer
who already knows Prometheus and Grafana
but is new to OpenTelemetry.
```

這可能比從頭閱讀長文省力很多。

---

# 十一、Quarto

推薦：

- https://quarto.org/

Quarto 適合做 structured technical document。

支援：

- Tabs
- Callouts
- Code folding
- Sidebar
- Interactive widgets
- Observable JS
- Jupyter widgets

例如：

```text
Architecture

[ Overview ] [ Data flow ] [ Detailed components ]

                 ↓

             diagram
```

但目前的情境下：

> web-artifacts-builder 的自由度還是更高。

所以 Quarto 值得知道，但不一定要優先切換。

---

# 十二、重新定義 web-artifacts-builder 的角色

目前 web-artifacts-builder 很可能只是被當成：

```text
Markdown
   ↓
Pretty HTML
```

但它本身其實已經提供：

- React
- TypeScript
- State
- Routing
- Tailwind
- shadcn/ui
- Interactive Components

所以它其實足夠做：

```text
Long Markdown
      ↓
Learning Artifact
```

不需要先換工具。

真正需要改的是 Prompt。

不要：

```text
Convert this Markdown into a beautiful interactive HTML.
```

而應該改成：

```text
Transform this long technical document into
an interactive learning experience.

Do not preserve the document structure blindly.

Optimize for human comprehension,
not information completeness per screen.
```

---

# 十三、建議的 Learning Artifact UI

推薦：

```text
┌────────────────────────────────────┐
│ 3 min │ Guided │ Explore │ Lab     │
├────────────────────────────────────┤
│                                    │
│           Current concept          │
│                                    │
│           Diagram                  │
│                                    │
│  Key idea                          │
│                                    │
│ [Why?] [Details] [Example]         │
│                                    │
├────────────────────────────────────┤
│       ← Previous     Next →        │
└────────────────────────────────────┘
```

四個 Mode：

### 3 min

快速建立 mental model。

### Guided

一步一步學，每次只引入一個主要概念。

### Explore

Concept Map / Architecture Map / Clickable Nodes。

### Lab

Hands-on implementation。

---

# 十四、目前推薦的實驗優先順序

## 第一名：改造現有 web-artifacts-builder

保留：

```text
Markdown
   ↓
web-artifacts-builder
```

但是從：

```text
Readable HTML
```

升級成：

```text
Learning Artifact
```

重點是：

- Progressive Disclosure
- Guided Tour
- Map First
- Learn / Lab Separation
- Checkpoint
- Reader-selected depth

這應該是目前最值得做的改動。

---

## 第二名：Slidev

拿同一份 Markdown A/B Test：

```text
Long HTML
vs
20–30 screen Guided Story
```

看看哪一種吸收速度更快。

---

## 第三名：NotebookLM

用不同 modality：

```text
Markdown
 ├─ Mind Map
 ├─ Audio
 ├─ Quiz
 └─ Slide
```

測試是否能降低閱讀疲勞。

---

## 第四名：Markmap

作為：

```text
You are here map
```

不要當主要教材，而是當 navigation / concept map。

---

# 十五、這次討論最重要的觀念

第一階段已經做到：

```text
Markdown
   ↓
Readable HTML
```

下一階段不是：

```text
Better HTML
```

而是：

```text
                    ┌─ Map
                    │
Long Markdown ──────┼─ Guided Story
                    │
                    ├─ Interactive Explanation
                    │
                    ├─ Lab
                    │
                    └─ Quiz / Audio
```

也就是從：

> **Document Formatting**

進化到：

> **Instructional Design**

---

# 十六、最終建議

如果下一步只做一件事：

> 拿 `otel-collector-positioning-review.md` 做一版 **Learning Artifact v2**。

不要先改內容，而是重新設計 UI 與資訊節奏：

```text
Home
 ├─ 3-minute Overview
 ├─ Guided Tour
 ├─ Explore Architecture
 ├─ Deep Dive
 └─ Lab
```

並加入：

```text
Progressive Disclosure
Concept Map
One-concept-per-screen
Learn / Lab separation
Small checkpoints
Reader-selected depth
```

這應該會比單純繼續優化 HTML 排版，更接近真正降低「人類理解成本」的目標。

---

# 相關工具與連結

## Knowledge Architecture

- OpenWiki  
  https://github.com/langchain-ai/openwiki

- LikeC4  
  https://github.com/likec4/likec4

- C4 Model  
  https://c4model.com/

- GitNexus  
  https://github.com/abhigyanpatwari/GitNexus

- Understand Anything  
  https://github.com/Egonex-AI/Understand-Anything

- Diátaxis  
  https://diataxis.fr/

## Single-document Learning Experience

- Anthropic Web Artifacts Builder  
  https://github.com/anthropics/skills/blob/main/skills/web-artifacts-builder/SKILL.md

- Slidev  
  https://github.com/slidevjs/slidev

- Markmap  
  https://github.com/dundalek/markmap

- Quarto  
  https://quarto.org/

- NotebookLM  
  https://notebooklm.google.com/

---

# 一句話總結

> **AI 時代真正稀缺的不是資訊，而是能讓人快速形成 mental model 的「理解介面」。**

下一步最值得做的，不是再產生更多內容，而是把同一份內容轉成：

> **可控制深度、可探索、可逐步理解、可互動驗證的 Learning Artifact。**
