state.save(self.run_dir, use_cloudpickle=self.use_cloudpickle)
notify_callbacks(self.callbacks, "on_state_saved", ...)

state.i += 1
state.full_program_trace.append({"i": state.i})

notify_callbacks(self.callbacks, "on_iteration_start", ...)
```

- **Saves current state** to `{run_dir}/gepa_state.bin` for resumability [src/gepa/core/state.py:30]().
- **Increments iteration counter** `state.i`.
- **Emits `on_iteration_start`** callback event.

**Sources**: [src/gepa/core/engine.py:382-404]()

---

### 2. Merge Attempt (if scheduled)

```python
# src/gepa/core/engine.py:407-479
if self.merge_proposer is not None and self.merge_proposer.use_merge:
    if self.merge_proposer.merges_due > 0 and self.merge_proposer.last_iter_found_new_program:
        proposal = self.merge_proposer.propose(state)
        # ... evaluate subsample, check acceptance
```

**Merge is attempted when**:
- `use_merge=True` in configuration.
- `merges_due > 0` (scheduled attempts remaining).
- `last_iter_found_new_program=True` (reflective mutation succeeded last iteration).

**Acceptance criterion**: Merged candidate's subsample score must be `>= max(parent_scores)` [src/gepa/core/engine.py:431]().

If accepted:
- Full valset evaluation via `_run_full_eval_and_add()`.
- `merges_due` counter decremented.
- `total_merges_tested` incremented.
- **Skip reflective mutation this iteration** (continues to next iteration).

**Sources**: [src/gepa/core/engine.py:407-479](), [src/gepa/proposer/merge.py:35-132]()

---

### 3. Reflective Mutation Proposal

The engine supports parallel proposal generation using a `ThreadPoolExecutor` [src/gepa/core/engine.py:484-538](). The `ReflectiveMutationProposer` splits the work into three phases:
1. `prepare_proposal`: Sequential context sampling.
2. `execute_proposal`: Parallel LLM reflection and evaluation.
3. `apply_proposal_output`: Sequential state updates.

```python