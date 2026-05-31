This document describes the communication infrastructure for the Model Context Protocol project, including where community discussions happen, how decisions are documented, and the policies governing transparency. For governance structure and decision-making processes, see [Governance Structure](#7.1). For the SEP proposal process, see [Specification Enhancement Process](#6.2).

## Overview

The MCP project maintains four primary communication channels, each serving distinct purposes in the project lifecycle:

| Channel | Purpose | Formality | Persistence |
|---------|---------|-----------|-------------|
| Discord | Real-time contributor discussions, working group coordination | Informal | Transient |
| GitHub Discussions | Long-form proposals, community consensus-building | Semi-formal | Permanent |
| GitHub Issues | Actionable tasks, bug reports, feature tracking | Formal | Permanent |
| Security Reporting | Private vulnerability disclosure | Formal | Private |

The project serves approximately 2,900+ Discord members with 100+ new contributors joining weekly as of November 2025.

**Sources:** [docs/community/communication.mdx:1-107](), [blog/content/posts/2025-11-25-first-mcp-anniversary.md:122-123]()

## Communication Channel Architecture

```mermaid
graph TB
    subgraph "Real-time Communication"
        Discord[Discord Server<br/>2,900+ members<br/>100+ new weekly]
        
        subgraph "Public Discord Channels"
            PublicSDK["SDK Development<br/>#typescript-sdk-dev<br/>#python-sdk-dev"]
            PublicWG["Working Groups<br/>Per WG/IG channels<br/>Tagged in calendar"]
            PublicTools["Tooling Development<br/>#inspector-dev<br/>#registry-dev"]
            PublicOffice["Community Onboarding<br/>Office hours<br/>Contribution guidance"]
        end
        
        subgraph "Private Discord Channels"
            PrivateSec["Security Incidents<br/>CVE handling<br/>Protocol vulnerabilities"]
            PrivatePeople["People Matters<br/>Maintainer discussions<br/>Code of conduct"]
            PrivateDecision["Decision Coordination<br/>Read-only archives<br/>Maintainer consensus"]
        end
        
        Discord --> PublicSDK
        Discord --> PublicWG
        Discord --> PublicTools
        Discord --> PublicOffice
        Discord --> PrivateSec
        Discord --> PrivatePeople
        Discord --> PrivateDecision
    end
    
    subgraph "Asynchronous Communication"
        GHDiscussions["GitHub Discussions<br/>Long-form proposals<br/>Roadmap planning"]
        GHIssues["GitHub Issues<br/>Bug reports<br/>Feature tracking"]
        SEPs["SEP Pull Requests<br/>seps/ directory<br/>Specification changes"]
    end
    
    subgraph "Decision Records"
        GHIssuesRecord["GitHub Issues<br/>Technical decisions<br/>notes label"]
        SEPsRecord["SEPs<br/>seps/ directory<br/>Specification changes"]
        ChangelogRecord["Changelog<br/>specification/draft/changelog<br/>Version history"]
        DocsRecord["Community Docs<br/>community/governance<br/>Process changes"]
    end
    
    PublicSDK -.must document in.-> GHDiscussions
    PublicWG -.must document in.-> GHIssues
    PrivateDecision -.must document in.-> GHIssuesRecord
    
    GHDiscussions --> SEPs
    GHIssues --> SEPs
    SEPs --> SEPsRecord
    SEPsRecord --> ChangelogRecord
    
    style Discord fill:#f9f9f9
    style PrivateSec fill:#ffe0e0
    style PrivatePeople fill:#ffe0e0
    style PrivateDecision fill:#ffe0e0
```

**Sources:** [docs/community/communication.mdx:8-107](), [docs/community/governance.mdx:32-34]()

## Discord Server Structure

### Access and Membership

The Discord server is designed for MCP contributors, not general MCP support. Contributors access the server at `https://discord.gg/6CSzBmMkjX` (referenced as `discord-join` link).

### Public Channel Categories

Public channels follow a default-open policy for transparency:

**SDK and Tooling Development:**
- Channels named `#<sdk-name>-sdk-dev` (e.g., `#typescript-sdk-dev`, `#python-sdk-dev`)
- Channels named `#<tool-name>-dev` (e.g., `#inspector-dev`, `#registry-dev`)
- Development occurs entirely in public from ideation through release planning

**Working and Interest Groups:**
- Each WG/IG has a dedicated channel
- Channel names tagged in the public MCP community calendar at `meet.modelcontextprotocol.io`
- Meeting notes published as GitHub Issues with links in respective channels

**Community Onboarding:**
- Office hours coordination
- Contribution guidance
- New contributor onboarding

### Private Channel Policies

Private channels exist only for specific exceptions, with strict transparency requirements:

```mermaid
graph LR
    PrivateChannel[Private Discord Channel]
    
    subgraph "Allowed Private Use Cases"
        Security["Security Incidents<br/>CVEs<br/>Protocol vulnerabilities"]
        People["People Matters<br/>Maintainer-related<br/>Code of conduct"]
        ReadOnly["Read-only Channels<br/>Maintainer decisions<br/>Limited audience coordination"]
        Urgent["Urgent Coordination<br/>Immediate response<br/>Focused audience"]
    end
    
    subgraph "Required Public Documentation"
        GHIssues["GitHub Issues<br/>notes label"]
        GHDiscussions["GitHub Discussions<br/>Context preservation"]
        Exception["Personal matters<br/>may remain private"]
    end
    
    PrivateChannel --> Security
    PrivateChannel --> People
    PrivateChannel --> ReadOnly
    PrivateChannel --> Urgent
    
    Security -.must document.-> GHIssues
    ReadOnly -.must document.-> GHIssues
    Urgent -.must document.-> GHDiscussions
    People -.may document.-> Exception
    
    style PrivateChannel fill:#ffe0e0
    style Exception fill:#fff0e0
```

All technical and governance decisions affecting the community must be documented in GitHub Discussions or Issues, labeled with `notes`. Personal matters related to individual contributors may remain private when appropriate (e.g., personal circumstances, disciplinary actions).

**Sources:** [docs/community/communication.mdx:19-53](), [docs/community/governance.mdx:32-34]()

## GitHub Discussions

### Purpose and Use Cases

GitHub Discussions serves as the structured, long-form discussion forum for project direction and feature proposals:

| Use Case | Description | Example Labels |
|----------|-------------|----------------|
| Roadmap Planning | Project direction, milestone discussions | `roadmap`, `planning` |
| Announcements | Release communications, community updates | `announcement` |
| Consensus Building | Community polls, voting on approaches | `consensus`, `poll` |
| Feature Requests | Proposals with context and rationale | `feature-request` |

Discussions accessed at `https://github.com/modelcontextprotocol/modelcontextprotocol/discussions`.

### Relationship to SEP Process

Significant Discord discussions that lead to potential decisions or proposals must be moved to GitHub Discussions to create a persistent, searchable record. Discussions then promote to SEP pull requests as they mature:

```mermaid
graph TD
    Discord["Discord Discussion<br/>Real-time exploration<br/>Working Group brainstorm"]
    GHDiscussion["GitHub Discussion<br/>Structured proposal<br/>Community feedback"]
    SEPDraft["SEP Draft PR<br/>seps/0000-feature.md<br/>Sponsor search"]
    SEPReview["SEP In-Review<br/>seps/####-feature.md<br/>Core Maintainer review"]
    SEPFinal["SEP Final<br/>Merged to seps/<br/>Reference implementation"]
    
    Discord -.must move to.-> GHDiscussion
    GHDiscussion --> SEPDraft
    SEPDraft --> SEPReview
    SEPReview --> SEPFinal
    
    GHDiscussion -.optional for.-> SEPDraft
    
    Note1["Note: Moving from Discord<br/>to Discussion preserves<br/>searchable context"]
    Note2["Note: SEPs can start<br/>without prior Discussion<br/>but IG input encouraged"]
    
    Discord -.-> Note1
    GHDiscussion -.-> Note2
```

**Sources:** [docs/community/communication.mdx:54-66](), [docs/community/sep-guidelines.mdx:41-42](), [seps/1850-pr-based-sep-workflow.md:13-31]()

## GitHub Issues

### Issue Types and Workflows

GitHub Issues handle actionable development tasks across all MCP repositories:

| Issue Type | Purpose | Labels | Assignment |
|------------|---------|--------|------------|
| Bug Report | Reproducible defects with steps | `bug` | Maintainer triages |
| Documentation | Improvements with specific scope | `docs` | Open contribution |
| CI/CD | Infrastructure, pipeline failures | `ci`, `infrastructure` | Maintainer handles |
| Release Task | Milestone tracking items | `release`, `milestone` | Maintainer coordinates |

### SEP vs Issue Distinction

SEPs are **not** submitted as GitHub Issues. The PR-based SEP workflow introduced in November 2025 (SEP-1850) requires proposals as pull requests to the `seps/` directory:

```