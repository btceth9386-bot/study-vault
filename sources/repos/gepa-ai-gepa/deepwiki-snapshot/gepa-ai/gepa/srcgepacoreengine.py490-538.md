with ThreadPoolExecutor(max_workers=self.num_parallel_proposals) as executor:
    contexts = [self.reflective_proposer.prepare_proposal(state) for _ in range(self.num_parallel_proposals)]
    futures = [executor.submit(self.reflective_proposer.execute_proposal, ctx) for ctx in contexts]
    
    for future in as_completed(futures):
        output = future.result()
        # Apply acceptance criterion and update state...
```

**Acceptance criterion**: The engine uses the configured `AcceptanceCriterion` (default: `StrictImprovementAcceptance`) to gate promotion [src/gepa/core/engine.py:124]().

**Sources**: [src/gepa/core/engine.py:484-538](), [src/gepa/proposer/reflective_mutation/reflective_mutation.py:66-260]()

---

### 4. Error Handling

```python
# src/gepa/core/engine.py:540-556
except Exception as e:
    self.logger.log(f"Iteration {state.i + 1}: Exception: {e}")
    notify_callbacks(self.callbacks, "on_error", ...)
    if self.raise_on_exception:
        raise e
    else:
        continue  # graceful continuation
```

**Behavior**:
- **`raise_on_exception=True`**: Propagates exception, halting optimization.
- **`raise_on_exception=False`**: Logs error, notifies callbacks, continues to next iteration.

**Sources**: [src/gepa/core/engine.py:540-556]()

---

## Evaluation and Acceptance

### Full Valset Evaluation

The `_run_full_eval_and_add()` method ([src/gepa/core/engine.py:145-233]()) handles:

1. **Selects validation IDs** via `val_evaluation_policy.get_eval_batch()`.
2. **Evaluates candidate** on selected IDs using cached evaluation ([src/gepa/core/state.py:30]()).
3. **Updates state** with new candidate, scores, and Pareto frontiers via `update_state_with_new_program` [src/gepa/core/state.py:30]().
4. **Emits callbacks**: `on_valset_evaluated`, `on_pareto_front_updated`.
5. **Logs metrics** to experiment tracker.

**Sources**: [src/gepa/core/engine.py:145-233]()

---

### Evaluation Caching

If `cache_evaluation=True` in `optimize()`, the engine uses `EvaluationCache` ([src/gepa/core/state.py:10-131]()) to avoid redundant metric calls.

```python