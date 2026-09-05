# Study Vault OpenWiki brief

Build a persistent, interlinked orientation layer over this repository's approved knowledge. Help a reader form a mental model and find the canonical material; do not reproduce every source or concept as another document dump.

## Canonical inputs

- `concepts/`: approved atomic knowledge. Treat frontmatter `related` links as explicit relationships.
- `topics/`: curated learning paths and recommended concept order.
- `_index/`: generated discovery indexes; useful for inventory, not authority over the files they index.
- `labs/*/spec.diataxis.md`: primary human learning narrative when present.
- `labs/*/spec.md`: lab source specification and fallback when no Diátaxis version exists.
- `_scripts/prompts/` and current scripts/tests: workflow behavior and write-boundary evidence.

Prefer current implementation and tests over stale prose. Never infer approved knowledge from `_drafts/`, `_inbox/`, raw `sources/`, quiz history, learner predictions, private answer keys, or generated review HTML; these paths are excluded by `.openwikiignore`.

## Wiki shape

Keep the wiki small and navigable:

1. Start with a quickstart that explains the source → draft → promote → topic → lab → review loop.
2. Create domain maps only where they connect multiple approved concepts.
3. Explain cross-domain relationships and unresolved questions instead of duplicating concept pages.
4. Provide a lab catalog that links concepts to hands-on practice and distinguishes `spec.diataxis.md` from the canonical lab spec.
5. Link every material claim to repository evidence through OpenWiki Claims.

Use concise English, progressive disclosure, and Mermaid only when it clarifies a relationship or workflow. Preserve the draft-then-promote boundary: this wiki is derived navigation, never a new source of truth and never authorization to modify `concepts/`, `topics/`, `quiz/`, or lab content.

Keep updates manual during this pilot. Do not create or document a scheduled OpenWiki workflow; automated runs require a separate cost and review decision.
