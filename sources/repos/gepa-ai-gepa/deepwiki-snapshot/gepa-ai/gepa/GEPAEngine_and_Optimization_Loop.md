**Purpose**: This page documents the `GEPAEngine` class and the core optimization loop that drives GEPA's evolutionary search. It explains how the engine orchestrates candidate proposal, evaluation, acceptance, and state updates across iterations until stopping conditions are met.

**Scope**: Covers the engine's initialization, the main `run()` method, iteration structure, proposal scheduling (merge vs reflective mutation), acceptance criteria, and integration with callbacks, stopping conditions, and progress tracking. For details on state persistence and Pareto frontier management, see [State Management and Persistence](4.2). For proposer implementations, see [Proposer System](4.4).

---

## Overview

The `GEPAEngine` class in [src/gepa/core/engine.py:51-624]() is the orchestrator of GEPA's optimization process. It manages:

- **Iteration control**: Incrementing iterations and checking stop conditions.
- **Proposal coordination**: Scheduling merge and reflective mutation proposals.
- **Evaluation orchestration**: Calling adapters to evaluate candidates on validation sets.
- **Acceptance logic**: Determining whether to add new candidates to the population based on `AcceptanceCriterion` [src/gepa/core/engine.py:124]().
- **State updates**: Maintaining candidate pool, scores, and Pareto frontiers in `GEPAState`.
- **Callback notifications**: Emitting events for logging and monitoring via `notify_callbacks`.
- **Persistence**: Saving state snapshots for resumability.

The engine is instantiated by the `optimize()` function in [src/gepa/api.py:383-403]() and runs until stopping conditions are satisfied.

**Sources**: [src/gepa/core/engine.py:51-624](), [src/gepa/api.py:383-403]()

---

## GEPAEngine Initialization

### Constructor Parameters

The `GEPAEngine.__init__` method ([src/gepa/core/engine.py:54-134]()) accepts:

| Parameter | Type | Purpose |
|-----------|------|---------|
| `adapter` | `GEPAAdapter` | Evaluates candidates and creates reflective datasets. |
| `run_dir` | `str \| None` | Directory for saving state and outputs. |
| `valset` | `DataLoader` | Validation data for scoring candidates. |
| `seed_candidate` | `dict[str, str]` | Initial candidate to bootstrap optimization. |
| `reflective_proposer` | `ReflectiveMutationProposer` | Handles LLM-based reflection and mutation. |
| `merge_proposer` | `MergeProposer \| None` | Combines Pareto-optimal candidates (optional). |
| `frontier_type` | `FrontierType` | Strategy for tracking Pareto frontiers. |
| `stop_callback` | `StopperProtocol` | Determines when to halt optimization. |
| `val_evaluation_policy` | `EvaluationPolicy` | Controls which validation examples to evaluate. |
| `evaluation_cache` | `EvaluationCache \| None` | Caches (candidate, example) evaluations. |
| `perfect_score` | `float \| None` | Score threshold considered optimal. |
| `track_best_outputs` | `bool` | Whether to save best outputs per validation example. |
| `display_progress_bar` | `bool` | Show tqdm progress bar. |
| `raise_on_exception` | `bool` | Propagate exceptions vs. graceful stopping. |
| `num_parallel_proposals` | `int` | Number of concurrent proposals to generate. |

**Sources**: [src/gepa/core/engine.py:54-134]()

---

### Dependency Graph

```mermaid
graph TB
    API["optimize()<br/>src/gepa/api.py"]
    Engine["GEPAEngine<br/>src/gepa/core/engine.py"]
    RefProposer["ReflectiveMutationProposer<br/>src/gepa/proposer/reflective_mutation/"]
    MergeProposer["MergeProposer<br/>src/gepa/proposer/merge.py"]
    Adapter["GEPAAdapter<br/>src/gepa/core/adapter.py"]
    State["GEPAState<br/>src/gepa/core/state.py"]
    ValLoader["DataLoader valset<br/>src/gepa/core/data_loader.py"]
    EvalPolicy["EvaluationPolicy<br/>src/gepa/strategies/eval_policy.py"]
    Stopper["StopperProtocol<br/>src/gepa/utils/stop_condition.py"]
    Cache["EvaluationCache<br/>src/gepa/core/state.py"]
    
    API -->|"instantiates"| RefProposer
    API -->|"instantiates"| MergeProposer
    API -->|"instantiates"| Engine
    
    Engine -->|"uses for reflection"| RefProposer
    Engine -->|"uses for merging"| MergeProposer
    Engine -->|"evaluates via"| Adapter
    Engine -->|"initializes & updates"| State
    Engine -->|"fetches data from"| ValLoader
    Engine -->|"checks with"| Stopper
    Engine -->|"selects ids via"| EvalPolicy
    
    State -->|"optionally uses"| Cache
```

**Caption**: Dependency graph showing how `GEPAEngine` integrates with proposers, adapters, state, and supporting components.

**Sources**: [src/gepa/api.py:383-403](), [src/gepa/core/engine.py:54-134]()

---

## The Main Optimization Loop

The `run()` method ([src/gepa/core/engine.py:235-590]()) executes the optimization loop. It:

1. **Initializes state**: Loads from disk if `run_dir` exists, otherwise creates new state with seed candidate via `initialize_gepa_state` [src/gepa/core/state.py:30]().
2. **Evaluates seed**: Scores the initial candidate on the full validation set.
3. **Iterates**: Proposes, evaluates, and accepts/rejects candidates until stop conditions trigger.
4. **Persists state**: Saves snapshots to disk after each iteration.
5. **Returns final state**: Contains all explored candidates and their scores.

---

### High-Level Loop Structure

```mermaid
flowchart TD
    Start["Start run()"]
    InitState["Initialize or load GEPAState<br/>initialize_gepa_state()"]
    EvalSeed["Evaluate seed candidate<br/>on full valset"]
    LogBaseline["Log baseline metrics"]
    NotifyStart["Notify on_optimization_start"]
    
    CheckStop{"_should_stop(state)?"}
    
    IncrIter["state.i += 1"]
    SaveState["state.save(run_dir)"]
    NotifyIterStart["Notify on_iteration_start"]
    
    AttemptMerge["Attempt merge proposal<br/>(if scheduled)"]
    MergeAccepted{"Merge accepted?"}
    EvalMerge["_run_full_eval_and_add()"]
    NotifyMergeAccept["Notify on_merge_accepted"]
    SkipReflective["Skip reflective this iteration"]
    
    ProposeReflective["ReflectiveMutationProposer.propose()"]
    ReflectiveSuccess{"Proposal returned?"}
    SubsampleBetter{"AcceptanceCriterion.check()?"}
    EvalReflective["_run_full_eval_and_add()"]
    NotifyAccept["Notify on_candidate_accepted"]
    ScheduleMerge["Schedule merge attempts<br/>if enabled"]
    NotifyReject["Notify on_candidate_rejected"]
    
    NotifyIterEnd["Notify on_iteration_end"]
    
    FinalSave["state.save(run_dir)"]
    NotifyEnd["Notify on_optimization_end"]
    Return["Return GEPAState"]
    
    Start --> InitState
    InitState --> EvalSeed
    EvalSeed --> LogBaseline
    LogBaseline --> NotifyStart
    NotifyStart --> CheckStop
    
    CheckStop -->|"No"| IncrIter
    CheckStop -->|"Yes"| FinalSave
    
    IncrIter --> SaveState
    SaveState --> NotifyIterStart
    NotifyIterStart --> AttemptMerge
    
    AttemptMerge --> MergeAccepted
    MergeAccepted -->|"Yes"| EvalMerge
    EvalMerge --> NotifyMergeAccept
    NotifyMergeAccept --> SkipReflective
    
    MergeAccepted -->|"No or not attempted"| ProposeReflective
    ProposeReflective --> ReflectiveSuccess
    
    ReflectiveSuccess -->|"No"| NotifyIterEnd
    ReflectiveSuccess -->|"Yes"| SubsampleBetter
    
    SubsampleBetter -->|"No"| NotifyReject
    NotifyReject --> NotifyIterEnd
    
    SubsampleBetter -->|"Yes"| EvalReflective
    EvalReflective --> NotifyAccept
    NotifyAccept --> ScheduleMerge
    ScheduleMerge --> NotifyIterEnd
    
    SkipReflective --> NotifyIterEnd
    NotifyIterEnd --> CheckStop
    
    FinalSave --> NotifyEnd
    NotifyEnd --> Return
```

**Caption**: Main optimization loop flowchart showing iteration lifecycle, merge/reflective proposal sequencing, and callback notifications.

**Sources**: [src/gepa/core/engine.py:235-590]()

---

## Iteration Structure

Each iteration ([src/gepa/core/engine.py:372-570]()) follows this sequence:

### 1. State Persistence and Iteration Start

```python