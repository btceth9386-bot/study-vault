# Prompt Usage Examples

## 1. Process a new source (`new-source.md`)

After ingesting a source into `_inbox/`, ask the AI agent to process it:

```
Read _scripts/prompts/new-source.md then process the new source in _inbox/
```

The agent will:
- Organize the source into `sources/<type>/<slug>/`
- Generate candidate concept drafts in `_drafts/`
- Update `_index/`

## 2. Promote a draft to a formal concept (`promote-concept.md`)

After reviewing a draft in `_drafts/`, ask the AI agent to promote it:

```
Read _scripts/prompts/promote-concept.md then promote _drafts/<concept-name>.md
```

The agent will:
- Create `concepts/<category>/<concept-id>.md` (Feynman-style)
- Add quiz questions to `quiz/bank.json`
- Update `_index/`

## 3. Weekly knowledge base maintenance (`weekly-refine.md`)

Run periodically (e.g. weekly) to maintain the knowledge base:

```
Read _scripts/prompts/weekly-refine.md then execute
```

The agent will:
- Generate a refine report in `_inbox/refine-report-<date>.md`
- Flag stale concepts, contradictions, expired drafts
- Update `quiz/bank.json` and `_index/`

## Key constraint

AI never writes directly to `concepts/`. All AI output goes to `_drafts/` first. You review, then promote.
