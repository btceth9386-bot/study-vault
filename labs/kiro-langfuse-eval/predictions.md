# Predictions — fill BEFORE running

- Checkpoint 1: Before implementing `judge_score()`, what will `python scripts/run_variant.py --variant baseline` do — will it fail immediately, or run to completion and produce a broken result?
  - My prediction:
- Checkpoint 2: After you implement `judge_score()` and run both variants, will `item-07` (the ambiguous double-charge item) score high, low, or inconsistently under your rubric? Why?
  - My prediction:
- Checkpoint 3: `.kiro/hooks/log-usage-on-stop.json` is wired to a trigger name. Before checking kiro.dev's docs, what do you expect happens if that name is wrong — does Kiro CLI error out, warn, or say nothing?
  - My prediction:
- Checkpoint 4: In `scripts/model_compare.py`, which of `auto`, `haiku-4.5`, `sonnet-5` do you predict will have the best judge-score-per-credit ratio on this support-FAQ task?
  - My prediction:
- Checkpoint 5: Will `scripts/compare_report.py` exit 0 on your first run of the full lab (both variants + hook wired as-shipped)?
  - My prediction:
- Final result I expect:
