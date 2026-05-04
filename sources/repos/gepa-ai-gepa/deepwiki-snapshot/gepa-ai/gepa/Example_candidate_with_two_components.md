seed_candidate = {
    "system_prompt": "You are a helpful assistant...",
    "query_rewriter": "Reformulate the query to be more specific..."
}
```

**Component** refers to an individual named text parameter within a candidate (e.g., `"system_prompt"`). The `seed_candidate` provided by the user defines the initial components and their starting values. In "seedless mode" via `optimize_anything`, GEPA can bootstrap the initial candidate from a natural language objective.

**Sources:** [src/gepa/api.py:44-44](), [src/gepa/api.py:103-105](), [README.md:102-105]()

For detailed information about candidate structure and component handling, see [Candidates and Text Components](#3.4).

---

### Adapters: The Integration Interface

The `GEPAAdapter` protocol defines how GEPA connects to arbitrary systems. Adapters implement two required methods:

| Method | Purpose | Returns |
|--------|---------|---------|
| `evaluate(batch, candidate, capture_traces)` | Execute candidate on input batch | `EvaluationBatch` with scores, outputs, and optional trajectories |
| `make_reflective_dataset(candidate, eval_batch, components)` | Transform execution traces into LLM-readable feedback | `dict[component_name, list[examples]]` |

```mermaid
graph TB
    User["User System"]
    Adapter["GEPAAdapter Implementation"]
    Engine["GEPAEngine"]
    
    User -->|"implements"| Adapter
    Adapter -->|"evaluate()"| Engine
    Adapter -->|"make_reflective_dataset()"| Engine
    Engine -->|"calls with candidate"| Adapter
    
    subgraph "Adapter Responsibilities"
        Eval["execute candidate on inputs"]
        Extract["extract execution traces (Trajectory)"]
        Format["format traces for LLM reflection (Reflective Dataset)"]
    end
    
    Adapter --> Eval
    Adapter --> Extract
    Adapter --> Format
```

**Diagram: GEPAAdapter Protocol Interface**

**Sources:** [src/gepa/core/adapter.py:11-40](), [src/gepa/api.py:113-124]()

See [Adapters and System Integration](#3.3) for implementation details and built-in adapter examples.

---

### State: Persistent Optimization History

`GEPAState` maintains the complete optimization history and is automatically persisted to disk when `run_dir` is specified. Key state components:

| State Component | Type | Purpose |
|----------------|------|---------|
| `program_candidates` | `list[dict[str, str]]` | All explored candidates |
| `parent_program_for_candidate` | `list[list[int \| None]]` | Lineage tracking |
| `prog_candidate_val_subscores` | `list[dict[DataId, float]]` | Per-example scores |
| `pareto_front_valset` | `dict[DataId, float]` | Best score per validation example |
| `total_num_evals` | `int` | Cumulative metric call count |

```mermaid
graph LR
    State["GEPAState"]
    
    subgraph "Candidate Pool"
        Cands["program_candidates"]
        Parents["parent_program_for_candidate"]
        Scores["prog_candidate_val_subscores"]
    end
    
    subgraph "Pareto Frontiers"
        InstFront["pareto_front_valset"]
        InstProgs["program_at_pareto_front_valset"]
        ObjFront["objective_pareto_front"]
        ObjProgs["program_at_pareto_front_objectives"]
    end
    
    subgraph "Budget Tracking"
        Evals["total_num_evals"]
        Discovery["num_metric_calls_by_discovery"]
    end
    
    State --> Cands
    State --> Parents
    State --> Scores
    State --> InstFront
    State --> InstProgs
    State --> ObjFront
    State --> ObjProgs
    State --> Evals
    State --> Discovery
```

**Diagram: GEPAState Structure**

The state implements persistence, enabling GEPA to resume optimization from a directory:

```python
# Resumption from disk happens automatically via engine initialization
result = gepa.optimize(
    run_dir="./optimization_run",  # Resumes if directory exists
    seed_candidate=seed,
    ...
)
```

**Sources:** [src/gepa/core/state.py:142-200](), [src/gepa/core/engine.py:135-153]()

See [State Management and Persistence](#4.2) for details on state evolution and migration.

---

### Results: Immutable Optimization Snapshot

`GEPAResult` is the immutable object returned by `optimize()` and `optimize_anything()`, containing the best found candidate and full lineage information.

```mermaid
graph TB
    Opt["optimize() / optimize_anything()"]
    State["GEPAState"]
    Result["GEPAResult"]
    
    Opt -->|"runs optimization"| State
    State -->|"GEPAResult.from_state()"| Result
    
    subgraph "GEPAResult Contents"
        Best["best_candidate: dict[str, str] | str"]
        AllCands["candidates: list[dict[str, str]]"]
        Scores["val_aggregate_scores: list[float]"]
        Pareto["per_val_instance_best_candidates"]
        Lineage["parents: list[list[int | None]]"]
    end
    
    Result --> Best
    Result --> AllCands
    Result --> Scores
    Result --> Pareto
    Result --> Lineage
```

**Diagram: GEPAResult Structure**

**Sources:** [src/gepa/core/result.py:15-50](), [src/gepa/api.py:96-96]()

See [Results and Lineage Tracking](#4.3) for details on analyzing optimization results.

---

## The Optimization Loop

At each iteration, `GEPAEngine` coordinates three main steps:

### 1. Proposal Generation

Two proposer mechanisms generate new candidates:

**Reflective Mutation** (`ReflectiveMutationProposer`):
1. Select candidate from pool via `CandidateSelector` (e.g., Pareto selection).
2. Select component(s) to modify via `ReflectionComponentSelector`.
3. Sample minibatch via `BatchSampler`.
4. Execute candidate and capture trajectories.
5. Build reflective dataset (ASI) via adapter.
6. `reflection_lm` analyzes ASI and proposes new component text.

**Merge** (`MergeProposer`):
1. Find two Pareto-optimal candidates with a common ancestor.
2. Combine components where descendants diverged.
3. Evaluate on a stratified subsample to ensure the merge is effective.

```mermaid
graph TB
    Start["Iteration Start"]
    Merge{"Merge\nscheduled?"}
    MergePath["MergeProposer.propose()"]
    ReflectPath["ReflectiveMutationProposer.propose()"]
    
    Start --> Merge
    Merge -->|"Yes"| MergePath
    Merge -->|"No"| ReflectPath
    
    subgraph "Reflective Mutation Steps"
        SelectCand["CandidateSelector.select_candidate_idx()"]
        SelectComp["ComponentSelector.select_components()"]
        SampleBatch["BatchSampler.sample_batch()"]
        Eval["adapter.evaluate(capture_traces=True)"]
        BuildDataset["adapter.make_reflective_dataset()"]
        Propose["reflection_lm generates new text"]
    end
    
    ReflectPath --> SelectCand
    SelectCand --> SelectComp
    SelectComp --> SampleBatch
    SampleBatch --> Eval
    Eval --> BuildDataset
    BuildDataset --> Propose
    
    subgraph "Merge Steps"
        FindPair["find_common_ancestor_pair()"]
        MergeComps["Combine diverged components"]
        SubsampleEval["Evaluate on stratified subsample"]
    end
    
    MergePath --> FindPair
    FindPair --> MergeComps
    MergeComps --> SubsampleEval
```

**Diagram: Proposal Generation Paths**

**Sources:** [src/gepa/core/engine.py:429-588](), [src/gepa/proposer/reflective_mutation/reflective_mutation.py:66-120](), [src/gepa/proposer/merge.py:128-180]()

See [Proposer System](#4.4) for detailed proposer architecture.

### 2. Subsample Acceptance

New candidates must improve on their training subsample before full validation:
- **Reflective mutation**: Uses `AcceptanceCriterion` (default: `StrictImprovementAcceptance`).
- **Merge**: Evaluated against the performance of both parents to ensure hybrid improvement.

**Sources:** [src/gepa/core/engine.py:124-128](), [src/gepa/strategies/acceptance.py:1-40]()

### 3. Full Validation and Pareto Update

Accepted candidates undergo full validation evaluation:
1. Evaluate on validation set (controlled by `EvaluationPolicy`).
2. Update Pareto frontier(s) based on `frontier_type`.
3. Persist updated state to disk via `GEPAState.save()`.

**Sources:** [src/gepa/core/engine.py:154-174](), [src/gepa/core/state.py:220-250]()

---

## Strategic Configuration Points

GEPA's behavior is controlled by pluggable strategy objects:

### Candidate Selection
Controls which candidate to evolve from the pool.
- `ParetoCandidateSelector`: Sample uniformly from the Pareto front.
- `CurrentBestCandidateSelector`: Always select the highest-scoring candidate.

**Sources:** [src/gepa/strategies/candidate_selector.py:1-50](), [src/gepa/api.py:53-54]()

### Component Selection
Controls which component(s) to modify in a candidate.
- `RoundRobinReflectionComponentSelector`: Cycle through components.
- `AllReflectionComponentSelector`: Modify all components at once.

**Sources:** [src/gepa/strategies/component_selector.py:1-30](), [src/gepa/api.py:63-63]()

### Batch Sampling
Controls training data selection for the reflection step.
- `EpochShuffledBatchSampler`: Shuffles and batches examples into epochs.

**Sources:** [src/gepa/strategies/batch_sampler.py:1-20](), [src/gepa/api.py:57-57]()

### Frontier Type
Controls Pareto frontier tracking strategy.
- `"instance"`: Tracks best performance per validation example.
- `"objective"`: Tracks Pareto front across multiple competing objectives (e.g., accuracy vs. latency).

**Sources:** [src/gepa/core/state.py:22-23](), [src/gepa/api.py:55-55]()

### Stopping Conditions
Controls when optimization terminates. Multiple stoppers can be combined via `CompositeStopper`.

| Stopper | Termination Condition |
|---------|-----------------------|
| `MaxMetricCallsStopper` | Cumulative metric calls reach a limit |
| `MaxReflectionCostStopper` | Total USD cost of reflection LM calls reaches a budget |
| `TimeoutStopCondition` | Specified time elapsed |
| `ScoreThresholdStopper` | Validation score reaches a target |

**Sources:** [src/gepa/utils/stop_condition.py:34-210](), [src/gepa/api.py:69-71]()

See [Stopping Conditions](#3.5) for complete documentation.

---

## Data Flow Through the System

```mermaid
graph TB
    User["User Code"]
    OptFunc["optimize() / optimize_anything()"]
    Engine["GEPAEngine"]
    State["GEPAState"]
    Adapter["GEPAAdapter"]
    Proposer["ReflectiveMutationProposer / MergeProposer"]
    LM["reflection_lm"]
    
    User -->|"provides seed_candidate, datasets, config"| OptFunc
    OptFunc -->|"initializes"| Engine
    Engine -->|"loads or creates"| State
    
    Engine -->|"iteration loop"| Proposer
    Proposer -->|"select_candidate_idx()"| State
    Proposer -->|"evaluate(capture_traces=True)"| Adapter
    Adapter -->|"EvaluationBatch with Trajectory"| Proposer
    Proposer -->|"make_reflective_dataset()"| Adapter
    Adapter -->|"formatted examples (ASI)"| Proposer
    Proposer -->|"analyze traces, propose fix"| LM
    LM -->|"new component text"| Proposer
    Proposer -->|"CandidateProposal"| Engine
    
    Engine -->|"evaluate on valset"| Adapter
    Adapter -->|"scores, outputs"| Engine
    Engine -->|"update state"| State
    State -->|"save(run_dir)"| Disk["Disk (gepa_state.bin)"]
    
    Engine -->|"optimization complete"| OptFunc
    OptFunc -->|"GEPAResult.from_state()"| Result["GEPAResult"]
    Result -->|"returned to"| User
```

**Diagram: End-to-End Data Flow**

**Sources:** [src/gepa/api.py:42-407](), [src/gepa/core/engine.py:429-653](), [src/gepa/optimize_anything.py:53-131]()

---

## Evaluation and Caching

### Evaluation Batches
Adapters return `EvaluationBatch` objects containing outputs, scores, and trajectories. This structured output allows GEPA to handle multi-objective scores and complex execution traces.

### Evaluation Caching
When `cache_evaluation=True`, GEPA uses `EvaluationCache` to memoize `(candidate, example_id)` pairs, significantly reducing costs for validation steps.

**Sources:** [src/gepa/core/state.py:45-131](), [src/gepa/api.py:89-89]()

See [Evaluation Caching](#4.7) for implementation details.

---

## Configuration Hierarchy

GEPA uses a structured configuration system to manage complexity. In `optimize_anything`, this is exposed via `GEPAConfig`, which nests `EngineConfig`, `ReflectionConfig`, and others.

**Sources:** [src/gepa/optimize_anything.py:124-130](), [src/gepa/api.py:43-96]()

See [Configuration System](#3.8) for detailed parameter documentation.

# The optimize Function




This document covers the `gepa.optimize` function, which serves as the main API entry point for the GEPA framework. The `optimize` function orchestrates the entire evolutionary optimization process, from initialization to result generation.

For information about the internal optimization engine mechanics, see [Optimization Engine](4.1). For details about adapter implementation requirements, see [GEPAAdapter Interface](5.1). For specific optimization strategies and component selection, see [Optimization Strategies](3.3).

## Purpose and Scope

The `optimize` function provides a high-level interface that configures and executes GEPA's evolutionary text optimization algorithm. It handles parameter validation, component initialization, and orchestration of the optimization loop while abstracting away the internal complexity from end users.

**Sources:** [src/gepa/api.py:43-132]()

## Function Signature and Parameters

The `optimize` function accepts a comprehensive set of parameters organized into logical groups:

| Parameter Group | Key Parameters | Description |
|---|---|---|
| **Core Requirements** | `seed_candidate`, `trainset`, `valset` | Initial candidate (`dict[str, str]`) and training/validation datasets (lists or `DataLoader` instances). [src/gepa/api.py:44-46]() |
| **System Integration** | `adapter`, `task_lm`, `evaluator` | `GEPAAdapter` instance or `task_lm` string for `DefaultAdapter`. Optional custom `Evaluator`. [src/gepa/api.py:47-49]() |
| **Reflection Configuration** | `reflection_lm`, `candidate_selection_strategy`, `frontier_type`, `reflection_minibatch_size` | LLM for reflection, selection strategy (`"pareto"`, `"current_best"`, etc.), frontier strategy (`"instance"`, `"objective"`, etc.), minibatch size. [src/gepa/api.py:51-58]() |
| **Component Selection** | `module_selector`, `reflection_prompt_template`, `custom_candidate_proposer` | Component selector (`"round_robin"`, `"all"`), optional custom prompt templates, optional custom proposal function. [src/gepa/api.py:60-63]() |
| **Merge Strategy** | `use_merge`, `max_merge_invocations`, `merge_val_overlap_floor` | Enable merge (`bool`), max merge attempts, minimum validation overlap. [src/gepa/api.py:65-67]() |
| **Budget & Stopping** | `max_metric_calls`, `max_reflection_cost`, `stop_callbacks`, `perfect_score`, `skip_perfect_score` | Maximum evaluation calls, reflection cost budget, custom stoppers, perfect score threshold. [src/gepa/api.py:59-71]() |
| **Evaluation** | `val_evaluation_policy`, `cache_evaluation`, `batch_sampler`, `acceptance_criterion` | Validation policy, enable caching (`bool`), batch sampling strategy, acceptance logic. [src/gepa/api.py:89-95]() |
| **Logging & Callbacks** | `logger`, `run_dir`, `callbacks`, `use_wandb`, `use_mlflow`, `track_best_outputs`, `display_progress_bar` | Logger instance, save directory, callback list, experiment trackers, output tracking, progress display. [src/gepa/api.py:73-86]() |
| **Reproducibility** | `seed`, `raise_on_exception`, `use_cloudpickle` | Random seed, exception handling mode, use cloudpickle for serialization. [src/gepa/api.py:91-92]() |

**Sources:** [src/gepa/api.py:43-96]()

## Component Initialization and Orchestration

The `optimize` function serves as a factory that instantiates and wires together the core GEPA components. It creates the `GEPAEngine` which manages the optimization loop [src/gepa/core/engine.py:51-54]().

### GEPA Component Initialization Flow

```mermaid
graph TD
    OPTIMIZE["gepa.optimize()"] --> ADAPTER_INIT["Adapter Initialization"]
    ADAPTER_INIT --> DEFAULT_CHECK{"adapter is None?"}
    DEFAULT_CHECK -->|Yes| DEFAULT_ADAPTER["DefaultAdapter(model=task_lm, evaluator=evaluator)"]
    DEFAULT_CHECK -->|No| PROVIDED_ADAPTER["active_adapter = adapter"]
    
    DEFAULT_ADAPTER --> DATA_LOADERS["Data Loader Setup"]
    PROVIDED_ADAPTER --> DATA_LOADERS
    
    DATA_LOADERS --> TRAIN_LOADER["train_loader = ensure_loader(trainset)"]
    DATA_LOADERS --> VAL_LOADER["val_loader = ensure_loader(valset) or train_loader"]
    
    TRAIN_LOADER --> STOP_SETUP["Stopping Condition Setup"]
    VAL_LOADER --> STOP_SETUP
    
    STOP_SETUP --> COMPOSITE_STOP["CompositeStopper or single StopperProtocol"]
    
    COMPOSITE_STOP --> LM_SETUP["Language Model Setup"]
    LM_SETUP --> LM_CHECK{"reflection_lm is str?"}
    LM_CHECK -->|Yes| LITELLM_WRAP["litellm.completion wrapper"]
    LM_CHECK -->|No| DIRECT_LM["reflection_lm_callable = reflection_lm"]
    
    LITELLM_WRAP --> SELECTOR_INIT["Selector Initialization"]
    DIRECT_LM --> SELECTOR_INIT
    
    SELECTOR_INIT --> CAND_SEL["candidate_selector (Pareto/CurrentBest/...)"]
    SELECTOR_INIT --> MOD_SEL["module_selector_instance (RoundRobin/All)"]
    SELECTOR_INIT --> VAL_POLICY["val_evaluation_policy (FullEvaluationPolicy/...)"]
    
    CAND_SEL --> TRACKER_INIT["Tracker Initialization"]
    MOD_SEL --> TRACKER_INIT
    VAL_POLICY --> TRACKER_INIT
    
    TRACKER_INIT --> CREATE_TRACKER["create_experiment_tracker(wandb, mlflow)"]
    
    CREATE_TRACKER --> PROPOSER_INIT["Proposer Initialization"]
    
    PROPOSER_INIT --> REFL_PROP["ReflectiveMutationProposer"]
    REFL_PROP --> MERGE_INIT{"use_merge == True?"}
    MERGE_INIT -->|Yes| MERGE_PROP["MergeProposer"]
    MERGE_INIT -->|No| NO_MERGE["merge_proposer = None"]
    
    MERGE_PROP --> ENGINE_CREATE["GEPAEngine Creation"]
    NO_MERGE --> ENGINE_CREATE
    
    ENGINE_CREATE --> ENGINE["GEPAEngine"]
    ENGINE --> ENGINE_RUN["state = engine.run()"]
    ENGINE_RUN --> BUILD_RESULT["GEPAResult.from_state(state)"]
```

**Sources:** [src/gepa/api.py:180-408](), [src/gepa/core/engine.py:54-134]()

## Parameter Validation and Default Handling

The function performs several validation checks and applies defaults:

### Adapter Configuration Logic

```mermaid
graph TB
    START["optimize() invoked"] --> VALIDATE_SEED{"seed_candidate not empty?"}
    VALIDATE_SEED -->|No| ERROR1["ValueError: seed_candidate required"]
    VALIDATE_SEED -->|Yes| ADAPTER_CHECK{"adapter parameter"}
    
    ADAPTER_CHECK -->|None| TASK_LM_REQ{"task_lm provided?"}
    TASK_LM_REQ -->|No| ERROR2["AssertionError: task_lm required"]
    TASK_LM_REQ -->|Yes| DEFAULT_INIT["DefaultAdapter"]
    
    ADAPTER_CHECK -->|Provided| TASK_LM_CHECK{"task_lm is None?"}
    TASK_LM_CHECK -->|No| ERROR3["AssertionError: task_lm must be None"]
    TASK_LM_CHECK -->|Yes| EVAL_CHECK{"evaluator is None?"}
    EVAL_CHECK -->|No| ERROR4["AssertionError: evaluator must be None"]
    EVAL_CHECK -->|Yes| USE_PROVIDED["Use provided adapter"]
    
    DEFAULT_INIT --> PROPOSE_CHECK["Check proposal method"]
    USE_PROVIDED --> PROPOSE_CHECK
    
    PROPOSE_CHECK --> HAS_ADAPTER_PROPOSE{"adapter.propose_new_texts exists?"}
    HAS_ADAPTER_PROPOSE -->|Yes| HAS_CUSTOM{"custom_candidate_proposer provided?"}
    HAS_CUSTOM -->|Yes| ERROR5["ValueError: Cannot provide both"]
    HAS_CUSTOM -->|No| CONTINUE1["Continue"]
    
    HAS_ADAPTER_PROPOSE -->|No| CUSTOM_CHECK{"custom_candidate_proposer provided?"}
    CUSTOM_CHECK -->|Yes| CONTINUE2["Continue"]
    CUSTOM_CHECK -->|No| REFL_LM_CHECK{"reflection_lm provided?"}
    REFL_LM_CHECK -->|No| ERROR6["AssertionError: reflection_lm required"]
```

This validation ensures that:
1. A non-empty `seed_candidate` is provided.
2. Either `adapter` OR `task_lm` is specified, but not both.
3. When using a custom adapter, `task_lm` and `evaluator` must be `None`.
4. Either the adapter provides `propose_new_texts`, OR `custom_candidate_proposer` is provided, OR `reflection_lm` is specified.

**Sources:** [src/gepa/api.py:176-252]()

## Data Loader Normalization

The function normalizes dataset inputs to `DataLoader` instances using `ensure_loader` [src/gepa/core/data_loader.py:18-18]():

```python
train_loader = ensure_loader(trainset)
val_loader = ensure_loader(valset) if valset is not None else train_loader
```

**Sources:** [src/gepa/api.py:198-199]()

## Stopping Conditions Construction

The function constructs a composite stopping condition from multiple sources:

```mermaid
graph TB
    START["optimize() called"] --> INIT_LIST["stop_callbacks_list = []"]
    
    CHECK_RUN_DIR --> RUN_DIR_PARAM{"run_dir provided?"}
    RUN_DIR_PARAM -->|Yes| ADD_FILE["FileStopper(run_dir/gepa.stop)"]
    
    ADD_FILE --> CHECK_MAX{"max_metric_calls provided?"}
    CHECK_MAX -->|Yes| ADD_MAX["MaxMetricCallsStopper(max_metric_calls)"]
    
    ADD_MAX --> CHECK_COST{"max_reflection_cost provided?"}
    CHECK_COST -->|Yes| ADD_COST["MaxReflectionCostStopper(max_reflection_cost)"]
    
    ADD_COST --> VALIDATE_LIST{"stop_callbacks_list empty?"}
    VALIDATE_LIST -->|Yes| ERROR["ValueError: Stopping condition required"]
    VALIDATE_LIST -->|No| CREATE_COMPOSITE["CompositeStopper or single Stopper"]
```

The function requires at least one stopping condition. Multiple stoppers are combined using `CompositeStopper`.

**Sources:** [src/gepa/api.py:201-236]()

## Strategy Configuration Patterns

The function supports flexible strategy configuration through string-based selectors:

### Strategy Mapping

| Category | String Value | Implementation Class |
|---|---|---|
| **Component Selector** | `"round_robin"` | `RoundRobinReflectionComponentSelector` [src/gepa/strategies/component_selector.py:35-37]() |
| **Component Selector** | `"all"` | `AllReflectionComponentSelector` [src/gepa/strategies/component_selector.py:35-37]() |
| **Candidate Selector** | `"pareto"` | `ParetoCandidateSelector` [src/gepa/strategies/candidate_selector.py:32-32]() |
| **Candidate Selector** | `"current_best"` | `CurrentBestCandidateSelector` [src/gepa/strategies/candidate_selector.py:30-30]() |
| **Batch Sampler** | `"epoch_shuffled"` | `EpochShuffledBatchSampler` [src/gepa/strategies/batch_sampler.py:28-28]() |

**Sources:** [src/gepa/api.py:278-326]()

## Return Value and Result Generation

The function returns a `GEPAResult` object constructed from the final `GEPAState` produced by the engine [src/gepa/core/result.py:20-20](). This result contains the best candidate found, performance metrics, and lineage tracking.

**Sources:** [src/gepa/api.py:407-408]()

# The optimize_anything API




## Purpose and Scope

The `optimize_anything` API is GEPA's universal interface for optimizing arbitrary text artifacts: code, prompts, agent architectures, configurations, vector graphics, scheduling policies, and any other text-representable parameter [src/gepa/optimize_anything.py:1-15](). Unlike the standard `gepa.optimize()` function which is designed specifically for LLM prompt optimization with DSPy integration, `optimize_anything` provides a declarative API that abstracts over three distinct optimization paradigms and works with any domain where quality can be measured [src/gepa/optimize_anything.py:22-26]().

The key insight is that many problems can be formulated as text optimization: speeding up a CUDA kernel, tuning a scheduling policy, or redesigning an agent architecture [src/gepa/optimize_anything.py:10-14]().

---

## Core API Components

The `optimize_anything` API revolves around three user-facing concepts: **candidates** (text parameters to optimize), **evaluators** (functions that score candidates), and **ASI** (diagnostic feedback that guides LLM reflection) [src/gepa/optimize_anything.py:77-95]().

```mermaid
graph TB
    User["User Code"]
    OA["optimize_anything()"]
    Evaluator["User-Defined<br/>Evaluator"]
    Wrapper["EvaluatorWrapper"]
    Adapter["OptimizeAnythingAdapter"]
    Engine["GEPAEngine"]
    State["GEPAState"]
    Result["GEPAResult"]
    
    User -->|"seed_candidate<br/>evaluator<br/>dataset/valset<br/>objective"| OA
    OA -->|wraps| Evaluator
    Evaluator -->|wrapped by| Wrapper
    Wrapper -->|used by| Adapter
    OA -->|creates| Adapter
    OA -->|creates| Engine
    Engine -->|orchestrate| Adapter
    Engine -->|update| State
    Engine -->|return| State
    OA -->|convert| State
    State -->|to| Result
    Result -->|return to| User
    
    Wrapper -.->|capture| ASI["ASI:<br/>oa.log()<br/>stdio<br/>side_info"]
    Wrapper -.->|inject| OptState["OptimizationState<br/>(historical context)"]
```

**API Entry Point Flow**
Sources: [src/gepa/optimize_anything.py:153-406](), [src/gepa/adapters/optimize_anything_adapter/optimize_anything_adapter.py:233-296]()

---

## API Signature

The `optimize_anything` function is defined in `src/gepa/optimize_anything.py` and provides a unified interface for all three optimization modes:

```python
def optimize_anything(
    seed_candidate: str | dict[str, str] | None = None,
    evaluator: Evaluator,
    dataset: list | None = None,
    valset: list | None = None,
    objective: str | None = None,
    background: str | None = None,
    config: GEPAConfig | None = None,
) -> GEPAResult
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `seed_candidate` | `str \| dict[str, str] \| None` | Initial artifact to optimize. `None` triggers seedless mode where the LLM generates the first candidate from `objective` [src/gepa/optimize_anything.py:44-49](). |
| `evaluator` | `Evaluator` | Function that scores candidates: `(candidate, example?, **kwargs) -> float \| tuple[float, SideInfo]` [src/gepa/optimize_anything.py:171-230](). |
| `dataset` | `list \| None` | Training examples for multi-task search or generalization modes [src/gepa/optimize_anything.py:31-42](). |
| `valset` | `list \| None` | Validation examples (enables generalization mode when provided) [src/gepa/optimize_anything.py:38-42](). |
| `objective` | `str \| None` | Natural language description of optimization goal (required for seedless mode) [src/gepa/optimize_anything.py:93-95](). |
| `background` | `str \| None` | Domain knowledge, constraints, and context for the reflection LLM [src/gepa/optimize_anything.py:93-95](). |
| `config` | `GEPAConfig \| None` | Engine, reflection, tracking, merge, and refiner configuration [src/gepa/optimize_anything.py:654-811](). |

**Return Value**: `GEPAResult` containing `best_candidate`, `candidates`, Pareto frontiers, and lineage tracking [src/gepa/optimize_anything.py:808-815]().

Sources: [src/gepa/optimize_anything.py:153-166](), [src/gepa/optimize_anything.py:385-408]()

---

## Three Optimization Modes

The presence or absence of `dataset` and `valset` determines which optimization mode is activated [src/gepa/optimize_anything.py:22-43]():

```mermaid
graph TB
    Start{"`optimize_anything() called`"}
    CheckDataset{"`dataset provided?`"}
    CheckValset{"`valset provided?`"}
    
    SingleTask["`**Single-Task Search**<br/>dataset=None, valset=None<br/>Evaluator signature:<br/>evaluator(candidate) -> score`"]
    MultiTask["`**Multi-Task Search**<br/>dataset=list, valset=None<br/>Evaluator signature:<br/>evaluator(candidate, example) -> score`"]
    Generalization["`**Generalization**<br/>dataset=list, valset=list<br/>Evaluator signature:<br/>evaluator(candidate, example) -> score`"]
    
    SingleTaskImpl["SingleInstanceDataLoader<br/>(_SINGLE_INSTANCE_SENTINEL)"]
    DatasetImpl["ListDataLoader(dataset)"]
    ValsetImpl["ListDataLoader(valset)"]
    
    Start --> CheckDataset
    CheckDataset -->|No| SingleTask
    CheckDataset -->|Yes| CheckValset
    CheckValset -->|No| MultiTask
    CheckValset -->|Yes| Generalization
    
    SingleTask --> SingleTaskImpl
    MultiTask --> DatasetImpl
    Generalization --> DatasetImpl
    Generalization --> ValsetImpl
    
    SingleTaskImpl -.->|"all_ids() = [sentinel]"| Engine["GEPAEngine.run()"]
    DatasetImpl -.->|"all_ids() = range(len(dataset))"| Engine
    ValsetImpl -.->|"all_ids() = range(len(valset))"| Engine
```

**Optimization Mode Selection Logic**

### Mode 1: Single-Task Search

**Use case**: Solve one hard problem where the candidate *is* the solution (e.g., circle packing, blackbox optimization) [src/gepa/optimize_anything.py:27-30]().

**Characteristics**:
- No `dataset` or `valset` provided.
- Evaluator receives only `candidate` (no `example` parameter) [src/gepa/optimize_anything.py:548-566]().
- Internally uses `SingleInstanceDataLoader` with a sentinel value [src/gepa/optimize_anything.py:161-164]().

### Mode 2: Multi-Task Search

**Use case**: Solve a batch of related problems with cross-task transfer (e.g., CUDA kernels for multiple operations) [src/gepa/optimize_anything.py:33-36]().

**Characteristics**:
- `dataset` provided, `valset=None`.
- Evaluator receives `candidate` and `example` from dataset [src/gepa/optimize_anything.py:567-584]().
- Pareto frontier tracks per-example scores [src/gepa/optimize_anything.py:89-92]().

### Mode 3: Generalization

**Use case**: Build a skill/prompt that generalizes to unseen problems (e.g., prompt optimization for AIME) [src/gepa/optimize_anything.py:38-42]().

**Characteristics**:
- Both `dataset` (train) and `valset` (validation) provided.
- Final ranking uses validation set scores [src/gepa/optimize_anything.py:585-608]().

Sources: [src/gepa/optimize_anything.py:22-43](), [src/gepa/optimize_anything.py:548-608]()

---

## Evaluator Contract

The evaluator is a user-defined function that scores candidates. Its signature adapts to the optimization mode [src/gepa/optimize_anything.py:171-230]():

```python