# Lab recovery capsules

Complete, runnable labs live outside this repository under
`~/orb_pods_share/<lab-id>/`. This directory keeps only the minimum material
needed to recreate one after data loss:

- `manifest.yaml` — identity, concept links, workspace path, review URLs, and
  the regeneration contract.
- `spec.md` — the canonical learning intent, scaffold description, failure
  cases, and acceptance criteria.

To recover a lab, give an AI agent its manifest and spec, then ask it to follow
`_scripts/prompts/lab-design.md`. Generated code, `spec.diataxis.md`, learner
files, answer keys, and review HTML belong in `orb_pods_share`, not here.

Recovery aims for equivalent learning behavior and acceptance criteria, not
byte-for-byte reproduction. The SHA-256 value in each manifest detects damage
to the canonical spec.
