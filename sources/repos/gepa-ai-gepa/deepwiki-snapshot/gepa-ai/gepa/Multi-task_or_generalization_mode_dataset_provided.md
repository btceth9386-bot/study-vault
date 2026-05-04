def evaluator(
    candidate: str | dict[str, str],
    example: Any,
    opt_state: OptimizationState = None  # optional injection
) -> float | tuple[float, SideInfo]:
    ...
```

### Return Values

| Return Type | Description |
|-------------|-------------|
| `float` | Score only (higher is better). |
| `tuple[float, dict]` | Score and side information (ASI). |

### Optional Parameter Injection

The evaluator may declare optional keyword parameters that GEPA injects automatically, such as `opt_state` for historical context [src/gepa/optimize_anything.py:233-256]().

Sources: [src/gepa/optimize_anything.py:385-408](), [src/gepa/adapters/optimize_anything_adapter/optimize_anything_adapter.py:233-296]()

---

## Actionable Side Information (ASI)

ASI is the text-optimization analogue of gradients. Where gradients tell an optimizer *which direction to move*, ASI tells the LLM proposer *why a candidate failed* and *how to fix it* [src/gepa/optimize_anything.py:83-88]().

```mermaid
graph LR
    Evaluator["Evaluator Execution"]
    Log["oa.log() calls"]
    Stdio["stdout/stderr<br/>(if capture_stdio=True)"]
    Return["return (score, side_info)"]
    
    Wrapper["EvaluatorWrapper"]
    Merge["ASI Merging"]
    Dataset["Reflective Dataset"]
    Proposer["ReflectiveMutationProposer"]
    
    Evaluator --> Log
    Evaluator --> Stdio
    Evaluator --> Return
    
    Log -->|"capture in<br/>LogContext"| Wrapper
    Stdio -->|"capture in<br/>ThreadLocalStreamCapture"| Wrapper
    Return -->|"user-provided dict"| Wrapper
    
    Wrapper --> Merge
    Merge -->|"merged dict:<br/>{'log': ..., 'stdout': ..., ...}"| Dataset
    Dataset -->|"format examples"| Proposer
    Proposer -->|"LLM reflection prompt"| LLM["Reflection LM"]
```

**ASI Flow: Evaluator → Wrapper → Reflective Dataset → LLM Proposer**

### ASI Structure

ASI is a `dict[str, Any]` with conventional keys like `"log"`, `"stdout"`, and `"scores"` [src/gepa/optimize_anything.py:171-230]().

### Image Support

ASI supports including images for VLM reflection via the `gepa.Image` class [src/gepa/optimize_anything.py:131](), [src/gepa/image.py:1-10]().

Sources: [src/gepa/optimize_anything.py:83-88](), [src/gepa/adapters/optimize_anything_adapter/optimize_anything_adapter.py:76-147]()

---

## Logging and Diagnostics

### 1. `oa.log()` — In-Evaluator Logging

Thread-safe print-like function that captures output into the `"log"` key of side_info [src/gepa/optimize_anything.py:260-377]().

### 2. Stdout/Stderr Capture

When `capture_stdio=True` in `EngineConfig`, `sys.stdout` and `sys.stderr` are redirected into side_info [src/gepa/optimize_anything.py:611-650](). Uses `ThreadLocalStreamCapture` [src/gepa/utils/stdio_capture.py:1-20]().

Sources: [src/gepa/optimize_anything.py:260-377](), [src/gepa/utils/stdio_capture.py:1-237]()

---

## EvaluatorWrapper Architecture

The `EvaluatorWrapper` class bridges user-defined evaluators to GEPA's internal `GEPAAdapter` protocol [src/gepa/optimize_anything.py:419-425]().

```mermaid
graph TB
    UserEval["User Evaluator<br/>def eval(candidate, example?):<br/>  oa.log(...)<br/>  print(...)<br/>  return score, side_info"]
    
    Wrapper["EvaluatorWrapper"]
    
    LogCtx["LogContext<br/>(thread-local buffer)"]
    StdioCapture["ThreadLocalStreamCapture<br/>(stdout/stderr redirection)"]
    OptStateBuilder["OptimizationState builder<br/>(best_example_evals)"]
    
    NormalizedCall["Normalized Call:<br/>- Inject opt_state if needed<br/>- Unwrap str candidates if needed<br/>- Handle single-instance mode"]
    
    Merge["Merge ASI:<br/>{'log': ..., 'stdout': ..., **user_side_info}"]
    
    Return["Return:<br/>(score, candidate, side_info)"]
    
    UserEval -.->|wrapped by| Wrapper
    
    Wrapper -->|1. Create & activate| LogCtx
    Wrapper -->|2. Create & activate| StdioCapture
    Wrapper -->|3. Build if param exists| OptStateBuilder
    Wrapper -->|4. Call user function| NormalizedCall
    
    LogCtx -->|"drain() -> 'log' key"| Merge
    StdioCapture -->|"drain() -> 'stdout'/'stderr' keys"| Merge
    NormalizedCall -->|"return (score, user_side_info)"| Merge
    
    Merge --> Return
```

**EvaluatorWrapper Lifecycle**
Sources: [src/gepa/optimize_anything.py:419-545](), [src/gepa/adapters/optimize_anything_adapter/optimize_anything_adapter.py:233-296]()

---

## Stopping Conditions and Cost Tracking

The `optimize_anything` API supports various stopping conditions to manage budgets and execution time.

### Stopper Protocol
Stoppers are callables that return `True` when optimization should terminate [src/gepa/utils/stop_condition.py:14-31](). Common implementations include:
- `MaxMetricCallsStopper`: Stops after N evaluator calls [src/gepa/utils/stop_condition.py:163-174]().
- `TimeoutStopCondition`: Stops after a time limit [src/gepa/utils/stop_condition.py:34-43]().
- `MaxReflectionCostStopper`: Stops once the reflection LM cumulative cost reaches a USD budget [src/gepa/utils/stop_condition.py:176-191]().

### LM Cost Tracking
The `LM` wrapper tracks cumulative USD cost and token counts (input/output) across all calls [src/gepa/lm.py:60-87](). For custom callables, `TrackingLM` estimates usage based on string length (~4 chars/token) but reports zero cost [src/gepa/lm.py:190-210]().

Sources: [src/gepa/utils/stop_condition.py:1-210](), [src/gepa/lm.py:30-210]()

---

## Configuration Hierarchy

The `optimize_anything` API accepts a `GEPAConfig` object composing specialized sub-configs [src/gepa/optimize_anything.py:654-811]():

| Config Class | Purpose |
|--------------|---------|
| `EngineConfig` | Loop control (`max_metric_calls`, `seed`) [src/gepa/optimize_anything.py:611-650](). |
| `ReflectionConfig` | LLM settings (`reflection_lm`, `batch_sampler`) [src/gepa/optimize_anything.py:654-665](). |
| `TrackingConfig` | Experiment logging (`use_wandb`) [src/gepa/optimize_anything.py:675-688](). |

Sources: [src/gepa/optimize_anything.py:654-811]()

---

## Internal Execution Flow

```mermaid
graph TB
    Call["optimize_anything(...)<br/>called"]
    
    NormalizeSeed["Normalize seed_candidate:<br/>str → {_STR_CANDIDATE_KEY: str}<br/>None → seedless mode"]
    
    CreateLoader["Create DataLoaders:<br/>- dataset → ListDataLoader or SingleInstanceDataLoader<br/>- valset → ListDataLoader or same as dataset"]
    
    CreateWrapper["Create EvaluatorWrapper:<br/>- wrap user evaluator<br/>- handle oa.log(), stdio, opt_state"]
    
    CreateAdapter["Create OptimizeAnythingAdapter:<br/>- use EvaluatorWrapper<br/>- implement GEPAAdapter protocol"]
    
    CreateProposer["Create ReflectiveMutationProposer:<br/>- use OptimizeAnythingAdapter.propose_new_texts<br/>- format reflection prompts with objective/background"]
    
    CreateEngine["Create GEPAEngine:<br/>- orchestrate optimization loop<br/>- manage GEPAState<br/>- coordinate proposer & adapter"]
    
    RunEngine["engine.run():<br/>- iterate until stopper fires<br/>- evaluate → reflect → propose → accept/reject<br/>- track Pareto fronts"]
    
    ConvertResult["GEPAResult.from_state(state):<br/>- unwrap str candidates if needed<br/>- compute best_idx<br/>- expose Pareto fronts"]
    
    Return["return GEPAResult"]
    
    Call --> NormalizeSeed
    NormalizeSeed --> CreateLoader
    CreateLoader --> CreateWrapper
    CreateWrapper --> CreateAdapter
    CreateAdapter --> CreateProposer
    CreateProposer --> CreateEngine
    CreateEngine --> RunEngine
    RunEngine --> ConvertResult
    ConvertResult --> Return
```

**optimize_anything Execution Pipeline**
Sources: [src/gepa/optimize_anything.py:610-815](), [src/gepa/core/engine.py:254-653]()