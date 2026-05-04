GEPA (Genetic-Pareto) is a framework for optimizing textual system components—prompts, code, agent architectures, configurations—using LLM-based reflection and Pareto-efficient evolutionary search. Unlike reinforcement learning or gradient-based methods, GEPA leverages language models to read full execution traces (error messages, profiling data, reasoning logs) and diagnose *why* candidates fail, enabling targeted improvements with 100–500 evaluations instead of 5,000–25,000+.

**Scope of this document:** This page provides a high-level architectural overview of GEPA's core systems, their interactions, and how they map to code entities. For specific subsystems, see:
- User-facing APIs and quick start examples: [Quick Start](#2)
- Detailed optimization concepts: [Core Concepts](#3)
- Internal architecture deep dive: [Architecture Deep Dive](#4)
- Adapter development: [Adapter System](#5)

---

## System Architecture

GEPA's architecture separates concerns through a layered design: user-facing APIs invoke the core engine, which orchestrates proposers, adapters, and strategies while maintaining persistent state.

```mermaid
graph TB
    subgraph "User APIs"
        OPTIMIZE["gepa.optimize()<br/>(src/gepa/api.py:43-96)"]
        OPTIMIZE_ANY["optimize_anything()<br/>(gepa.optimize_anything)"]
        DSPY["dspy.GEPA<br/>(DSPy integration)"]
    end
    
    subgraph "Core Engine"
        ENGINE["GEPAEngine<br/>(src/gepa/core/engine.py:51)"]
        STATE["GEPAState<br/>(src/gepa/core/state.py:142)"]
        RESULT["GEPAResult<br/>(src/gepa/api.py:20)"]
    end
    
    subgraph "Proposers"
        REFLECTIVE["ReflectiveMutationProposer<br/>(src/gepa/proposer/reflective_mutation/reflective_mutation.py:66)"]
        MERGE["MergeProposer<br/>(src/gepa/proposer/merge.py:20)"]
    end
    
    subgraph "Adapters"
        ADAPTER["GEPAAdapter protocol<br/>(src/gepa/api.py:17)"]
        DEFAULT["DefaultAdapter<br/>(src/gepa/api.py:14)"]
        DSPY_ADAPTER["DSPyAdapter"]
        MCP_ADAPTER["MCPAdapter"]
        OA_ADAPTER["OptimizeAnythingAdapter"]
    end
    
    subgraph "Strategies"
        CAND_SEL["CandidateSelector<br/>(src/gepa/api.py:25)"]
        BATCH_SAMP["BatchSampler<br/>(src/gepa/api.py:28)"]
        STOP["StopperProtocol<br/>(src/gepa/api.py:40)"]
        EVAL_POL["EvaluationPolicy<br/>(src/gepa/api.py:39)"]
    end
    
    subgraph "Storage & Logging"
        CACHE["EvaluationCache<br/>(src/gepa/core/state.py:46)"]
        TRACKER["ExperimentTracker<br/>(src/gepa/core/engine.py:31)"]
        CALLBACKS["GEPACallback<br/>(src/gepa/core/engine.py:11)"]
    end
    
    OPTIMIZE --> ENGINE
    OPTIMIZE_ANY --> ENGINE
    DSPY --> ENGINE
    
    ENGINE --> STATE
    ENGINE --> REFLECTIVE
    ENGINE --> MERGE
    ENGINE --> RESULT
    
    ENGINE --> ADAPTER
    ADAPTER --> DEFAULT
    ADAPTER --> DSPY_ADAPTER
    ADAPTER --> MCP_ADAPTER
    ADAPTER --> OA_ADAPTER
    
    REFLECTIVE --> CAND_SEL
    REFLECTIVE --> BATCH_SAMP
    ENGINE --> STOP
    ENGINE --> EVAL_POL
    
    STATE --> CACHE
    ENGINE --> TRACKER
    ENGINE --> CALLBACKS
```

**Sources:** [src/gepa/api.py:1-96](), [src/gepa/core/engine.py:1-134](), [src/gepa/core/state.py:1-176](), [README.md:135-156]()

---

## Core Optimization Loop

Each iteration follows a dual-path strategy: either **reflective mutation** (LLM-driven improvement) or **merge** (combining Pareto-optimal candidates).

```mermaid
graph TD
    START["Iteration i+1<br/>state.i += 1"]
    
    DECIDE{"Merge<br/>scheduled?"}
    
    MERGE_PATH["MergeProposer.propose()<br/>(src/gepa/proposer/merge.py)"]
    MERGE_EVAL["Evaluate on<br/>stratified subsample"]
    MERGE_CHECK{"Score >=<br/>max(parents)?"}
    
    REFLECT_PATH["ReflectiveMutationProposer.execute_proposal()<br/>(src/gepa/proposer/reflective_mutation/reflective_mutation.py:66)"]
    SELECT_CAND["CandidateSelector.select_candidate_idx()<br/>(src/gepa/proposer/reflective_mutation/reflective_mutation.py:26)"]
    SELECT_BATCH["BatchSampler.sample_batch()<br/>(src/gepa/proposer/reflective_mutation/reflective_mutation.py:30)"]
    EVAL_TRACE["adapter.evaluate()<br/>capture_traces=True"]
    BUILD_REFLECT["adapter.make_reflective_dataset()<br/>(src/gepa/proposer/reflective_mutation/reflective_mutation.py:9)"]
    PROPOSE_LM["reflection_lm<br/>analyzes traces"]
    EVAL_NEW["Evaluate new candidate<br/>on same batch"]
    IMPROVE_CHECK{"Score ><br/>old score?"}
    
    FULL_EVAL["engine._run_full_eval_and_add()<br/>(src/gepa/core/engine.py:175)"]
    UPDATE_STATE["state.update_state_with_new_program()<br/>(src/gepa/core/state.py)"]
    PARETO_UPDATE["Update Pareto frontiers<br/>fire callbacks"]
    
    REJECT["Reject<br/>Continue to next iteration"]
    
    START --> DECIDE
    
    DECIDE -->|Yes| MERGE_PATH
    MERGE_PATH --> MERGE_EVAL
    MERGE_EVAL --> MERGE_CHECK
    MERGE_CHECK -->|No| REJECT
    MERGE_CHECK -->|Yes| FULL_EVAL
    
    DECIDE -->|No| REFLECT_PATH
    REFLECT_PATH --> SELECT_CAND
    SELECT_CAND --> SELECT_BATCH
    SELECT_BATCH --> EVAL_TRACE
    EVAL_TRACE --> BUILD_REFLECT
    BUILD_REFLECT --> PROPOSE_LM
    PROPOSE_LM --> EVAL_NEW
    EVAL_NEW --> IMPROVE_CHECK
    IMPROVE_CHECK -->|No| REJECT
    IMPROVE_CHECK -->|Yes| FULL_EVAL
    
    FULL_EVAL --> UPDATE_STATE
    UPDATE_STATE --> PARETO_UPDATE
```

**Sources:** [src/gepa/core/engine.py:154-181](), [src/gepa/proposer/merge.py:118-177](), [src/gepa/proposer/reflective_mutation/reflective_mutation.py:66-170]()

---

## Key Data Structures

GEPA's core data types define how candidates, evaluations, and state are represented throughout the system.

| Type | Location | Purpose |
|------|----------|---------|
| `Candidate` | [src/gepa/proposer/merge.py:9]() | Maps component names to text values (e.g., `{"system_prompt": "..."}`) |
| `GEPAState` | [src/gepa/core/state.py:142]() | Persistent optimization state: candidates, scores, Pareto fronts, budget |
| `EvaluationBatch` | [src/gepa/core/adapter.py]() | Container for evaluation results: `outputs`, `scores`, `trajectories`, `objective_scores` |
| `ValsetEvaluation` | [src/gepa/core/state.py:134]() | Validation results indexed by `DataId`: `outputs_by_val_id`, `scores_by_val_id` |
| `GEPAResult` | [src/gepa/api.py:20]() | Immutable snapshot returned to user: best candidate, lineage, Pareto fronts |
| `CandidateProposal` | [src/gepa/proposer/base.py:24]() | Proposed candidate with parent IDs and subsample scores |
| `EvaluationCache` | [src/gepa/core/state.py:46]() | Memoization for `(candidate, example_id)` pairs to avoid redundant evals |

**Sources:** [src/gepa/core/state.py:46-176](), [src/gepa/proposer/merge.py:9-24](), [src/gepa/api.py:12-40]()

---

## User-Facing Entry Points

Three APIs provide different levels of abstraction:

```mermaid
graph LR
    subgraph "API Entry Points"
        OPT["gepa.optimize()<br/>Simple prompt optimization<br/>(src/gepa/api.py:43)"]
        OPT_ANY["optimize_anything()<br/>Universal text optimization<br/>(README.md:116)"]
        DSPY_API["dspy.GEPA<br/>DSPy compiler integration<br/>(README.md:103)"]
    end
    
    subgraph "Initialization Flow"
        VALIDATE["Validate seed_candidate<br/>normalize datasets"]
        CREATE_ADAPTER["Create adapter:<br/>DefaultAdapter if none provided"]
        CREATE_PROPOSERS["Create proposers:<br/>ReflectiveMutationProposer<br/>MergeProposer (optional)"]
        CREATE_ENGINE["Create GEPAEngine<br/>(src/gepa/core/engine.py:51)"]
    end
    
    subgraph "Execution"
        ENGINE_RUN["engine.run()<br/>(src/gepa/core/engine.py)"]
        MAIN_LOOP["Main optimization loop<br/>until stop condition"]
        SAVE_STATE["state.save()<br/>(src/gepa/core/state.py)"]
        RETURN_RESULT["GEPAResult.from_state()"]
    end
    
    OPT --> VALIDATE
    OPT_ANY --> VALIDATE
    DSPY_API --> VALIDATE
    
    VALIDATE --> CREATE_ADAPTER
    CREATE_ADAPTER --> CREATE_PROPOSERS
    CREATE_PROPOSERS --> CREATE_ENGINE
    
    CREATE_ENGINE --> ENGINE_RUN
    ENGINE_RUN --> MAIN_LOOP
    MAIN_LOOP --> SAVE_STATE
    SAVE_STATE --> RETURN_RESULT
```

**Configuration mapping:**
- `gepa.optimize()`: Assembles `GEPAEngine` with user-specified strategies ([src/gepa/api.py:43-96]())
- `max_metric_calls`: Budget limit used by the engine ([src/gepa/api.py:69]())
- `run_dir`: Directory for persistence and logging ([src/gepa/api.py:74]())
- `candidate_selection_strategy`: Strategy for choosing candidates to mutate ([src/gepa/api.py:53]())
- `reflection_lm`: LLM used for analyzing traces and proposing fixes ([src/gepa/api.py:51]())

**Sources:** [src/gepa/api.py:43-96](), [src/gepa/core/engine.py:51-134](), [README.md:68-130]()

---

## Adapter Protocol

The `GEPAAdapter` protocol separates domain-specific evaluation logic from the core optimization engine.

```mermaid
graph TB
    subgraph "Adapter Interface"
        PROTOCOL["GEPAAdapter[DataInst, Trajectory, RolloutOutput]<br/>(src/gepa/api.py:17)"]
        EVALUATE["evaluate(batch, candidate, capture_traces)<br/>→ EvaluationBatch"]
        MAKE_REFLECT["make_reflective_dataset(candidate, eval_batch, components)<br/>→ dict[component → examples]"]
        PROPOSE["propose_new_texts (optional)"]
    end
    
    subgraph "Built-in Adapters"
        DEFAULT_A["DefaultAdapter<br/>(src/gepa/api.py:14)"]
        
        DSPY_A["DSPyAdapter<br/>(README.md:156)"]
        
        MCP_A["MCPAdapter<br/>(README.md:156)"]
        
        OA_A["OptimizeAnythingAdapter<br/>(README.md:156)"]
    end
    
    PROTOCOL --> EVALUATE
    PROTOCOL --> MAKE_REFLECT
    PROTOCOL --> PROPOSE
    
    PROTOCOL --> DEFAULT_A
    PROTOCOL --> DSPY_A
    PROTOCOL --> MCP_A
    PROTOCOL --> OA_A
```

**Required methods:**
1. `evaluate()`: Execute candidate on batch, return `EvaluationBatch` with scores, outputs, and optionally trajectories ([src/gepa/api.py:113-118]())
2. `make_reflective_dataset()`: Transform trajectories into structured feedback for the reflection LLM ([src/gepa/api.py:119-123]())

**Optional method:**
3. `propose_new_texts()`: Custom proposal logic, overriding default LLM-based reflection ([src/gepa/proposer/reflective_mutation/reflective_mutation.py:120-135]())

**Sources:** [src/gepa/api.py:113-123](), [src/gepa/proposer/reflective_mutation/reflective_mutation.py:120-135](), [README.md:151-166]()

---

## State Management and Persistence

`GEPAState` maintains all optimization artifacts and supports resumption from disk.

```mermaid
graph TB
    subgraph "GEPAState Fields"
        CANDS["program_candidates:<br/>list[dict[str, str]]"]
        PARENTS["parent_program_for_candidate:<br/>list[list[ProgramIdx | None]]"]
        VAL_SCORES["prog_candidate_val_subscores:<br/>list[dict[DataId, float]]"]
        OBJ_SCORES["prog_candidate_objective_scores:<br/>list[ObjectiveScores]"]
        
        PARETO_INST["pareto_front_valset:<br/>dict[DataId, float]"]
        PARETO_PROG["program_at_pareto_front_valset:<br/>dict[DataId, set[ProgramIdx]]"]
        PARETO_OBJ["objective_pareto_front:<br/>ObjectiveScores"]
        
        BUDGET["total_num_evals: int"]
        ITER["i: int"]
        CACHE_OPT["evaluation_cache:<br/>EvaluationCache | None"]
    end
    
    subgraph "Persistence Operations"
        SAVE["state.save(run_dir)"]
        PICKLE["Pickle serialization"]
        JSON_OUT["JSON export"]
        
        LOAD["GEPAState.load(run_dir)"]
    end
    
    subgraph "State Updates"
        UPDATE["update_state_with_new_program()"]
        INCREMENT["increment_evals(count)<br/>(src/gepa/core/state.py:167)"]
    end
    
    CANDS --> SAVE
    PARENTS --> SAVE
    VAL_SCORES --> SAVE
    BUDGET --> SAVE
    CACHE_OPT --> SAVE
    
    SAVE --> PICKLE
    SAVE --> JSON_OUT
    
    PICKLE --> LOAD
    
    INCREMENT --> BUDGET
```

**Key features:**
- **Caching:** Optional `EvaluationCache` memoizes `(candidate_hash, example_id)` pairs to avoid redundant evaluations ([src/gepa/core/state.py:46-131]()).
- **Budget Tracking:** Tracks total evaluations and metric calls to enforce limits ([src/gepa/core/state.py:175-177]()).
- **Pareto Frontiers:** Maintains sets of non-dominated candidates across instances and objectives ([src/gepa/core/state.py:162-167]()).

**Sources:** [src/gepa/core/state.py:1-177](), [src/gepa/core/engine.py:135-153]()

---

## Pareto Frontier Management

GEPA tracks four frontier types to support multi-objective optimization:

| Frontier Type | Key Type | Purpose |
|---------------|----------|---------|
| `instance` | `DataId` | Per validation example performance ([src/gepa/core/state.py:22]()) |
| `objective` | `str` | Per objective metric performance ([src/gepa/core/state.py:22]()) |
| `hybrid` | `tuple` | Both instance and objective ([src/gepa/core/state.py:22]()) |
| `cartesian` | `tuple` | Per (example, objective) pair ([src/gepa/core/state.py:22]()) |

**Frontier type configured via:** `frontier_type` parameter in `optimize` ([src/gepa/api.py:55]()).

**Sources:** [src/gepa/core/state.py:21-25](), [src/gepa/api.py:55]()

---

## Stopping Conditions

Multiple stopping strategies can be composed via the `StopperProtocol`:

```mermaid
graph LR
    subgraph "Stopper Implementations"
        MAX_CALLS["MaxMetricCallsStopper<br/>max_metric_calls"]
        MAX_COST["MaxReflectionCostStopper<br/>max_reflection_cost"]
        FILE["FileStopper<br/>gepa.stop file"]
    end
    
    subgraph "Composition"
        PROTOCOL["StopperProtocol<br/>(src/gepa/api.py:40)"]
    end
    
    MAX_CALLS --> PROTOCOL
    MAX_COST --> PROTOCOL
    FILE --> PROTOCOL
    
    ENGINE["GEPAEngine<br/>(src/gepa/core/engine.py:78)"]
    PROTOCOL --> ENGINE
```

**Auto-creation:** 
- `max_metric_calls` parameter provided to `optimize` ([src/gepa/api.py:69]()).
- `max_reflection_cost` parameter provided to `optimize` ([src/gepa/api.py:70]()).
- `FileStopper` used for graceful shutdown via a signal file ([src/gepa/api.py:40]()).

**Sources:** [src/gepa/api.py:40-78](), [src/gepa/core/engine.py:78-95]()

---

## Strategy Layer

Pluggable strategies control optimization behavior:

| Strategy Type | Interface | Implementations | Configuration |
|---------------|-----------|----------------|---------------|
| Candidate Selection | `CandidateSelector` | `Pareto`, `CurrentBest`, `EpsilonGreedy`, `TopKPareto` | [src/gepa/api.py:53-54]() |
| Batch Sampling | `BatchSampler` | `EpochShuffledBatchSampler` | [src/gepa/api.py:57]() |
| Component Selection | `ReflectionComponentSelector` | `RoundRobin`, `All` | [src/gepa/api.py:63]() |
| Evaluation Policy | `EvaluationPolicy` | `FullEvaluationPolicy` | [src/gepa/api.py:93]() |

**Sources:** [src/gepa/api.py:25-39](), [src/gepa/api.py:53-93]()