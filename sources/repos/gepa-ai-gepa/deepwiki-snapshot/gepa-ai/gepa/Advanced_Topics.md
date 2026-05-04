This page provides in-depth coverage of advanced features and optimization techniques within GEPA. It serves as a high-level map to specialized child pages that detail how to tune the engine, track costs, visualize candidate evolution, and handle complex multi-objective scenarios.

## 8.1 Experiment Tracking and Logging
GEPA integrates with standard experiment tracking frameworks to provide visibility into the optimization process. The `ExperimentTracker` class [src/gepa/logging/experiment_tracker.py:7-10]() handles communication with backends like **Weights & Biases (WandB)** and **MLflow**. It supports logging scalar metrics via `log_metrics()` [src/gepa/logging/experiment_tracker.py:236-258]() and structured data via `log_table()` [src/gepa/logging/experiment_tracker.py:260-291]().

For details, see [Experiment Tracking and Logging](#8.1).

Sources: [src/gepa/logging/experiment_tracker.py:7-291](), [src/gepa/logging/utils.py:11-131]()

## 8.2 Visualization
Understanding the lineage of candidates is crucial for debugging optimization runs. `GEPAResult` provides utilities to generate interactive HTML and DOT visualizations of the candidate tree via `candidate_tree_html()` [src/gepa/core/result.py:110-119]() and `candidate_tree_dot()` [src/gepa/core/result.py:99-108](). These tools help visualize the "family tree" of candidates, showing which mutations or merges led to performance breakthroughs.

For details, see [Visualization](#8.2).

Sources: [src/gepa/core/result.py:99-119]()

## 8.3 Batch Sampling Strategies
The `BatchSampler` protocol defines how data instances are selected from the training set during each iteration. Strategies like `EpochShuffledBatchSampler` ensure diverse data exposure. These samplers provide the `subsample_indices` [src/gepa/proposer/base.py:35]() used by proposers to gather feedback for reflection.

For details, see [Batch Sampling Strategies](#8.3).

Sources: [src/gepa/proposer/base.py:31-45]()

## 8.4 Component Selection Strategies
When a system has multiple optimizable text components (e.g., multiple prompts in a RAG pipeline), GEPA must decide which one to mutate. This is controlled by the `ReflectionComponentSelector` protocol [src/gepa/proposer/reflective_mutation/base.py:16-24](). Implementations allow for targeted mutation of specific modules based on performance or round-robin logic.

For details, see [Component Selection Strategies](#8.4).

Sources: [src/gepa/proposer/reflective_mutation/base.py:16-24]()

## 8.5 Dynamic Validation Sets
To balance evaluation speed and statistical significance, GEPA supports dynamic validation sets. The `BackfillValidationPolicy` allows the engine to evaluate candidates on a growing subset of the validation data, ensuring that promising candidates eventually receive full evaluation without wasting budget on poor ones.

For details, see [Dynamic Validation Sets](#8.5).

Sources: [src/gepa/logging/utils.py:20-28]()

## 8.6 Multi-Objective Optimization
GEPA natively supports optimizing for multiple competing objectives (e.g., accuracy vs. latency). It tracks an `objective_pareto_front` [src/gepa/core/result.py:49]() and `per_objective_best_candidates` [src/gepa/core/result.py:48](). This allows the engine to maintain a diverse set of candidates that excel in different dimensions.

For details, see [Multi-Objective Optimization](#8.6).

Sources: [src/gepa/core/result.py:41-50](), [src/gepa/logging/utils.py:112-131]()

## 8.7 Testing with LLM Mocking
Deterministic testing of stochastic LLM workflows is enabled via mocking utilities. This system supports a "record and replay" mode, allowing developers to verify engine logic without incurring API costs or dealing with non-deterministic model outputs by caching responses in structured files.

For details, see [Testing with LLM Mocking](#8.7).

Sources: [tests/test_experiment_tracking.py:129-143]()

## 8.8 Acceptance Criteria
Not every proposed candidate is worth keeping. The `CandidateProposal` [src/gepa/proposer/base.py:31-45]() structure carries the `eval_before` and `eval_after` data used by acceptance criteria to gate which candidates are added to the state. This prevents the engine from drifting into lower-performance regions of the search space.

For details, see [Acceptance Criteria](#8.8).

Sources: [src/gepa/proposer/base.py:31-45]()

## 8.9 Cost Tracking
Optimization can be expensive. GEPA provides built-in cost tracking to monitor resource usage during the reflection and evaluation phases. This is reflected in `total_metric_calls` [src/gepa/core/result.py:55]() and can be used with stoppers like `MaxReflectionCostStopper` to set hard USD budgets.

For details, see [Cost Tracking](#8.9).

Sources: [src/gepa/core/result.py:54-59](), [src/gepa/logging/utils.py:81]()

## System Integration Mapping

The following diagrams illustrate how advanced system components bridge the gap between high-level optimization concepts and the underlying code entities.

### Optimization Control Bridge
This diagram shows how user-facing configuration and strategies map to the internal `GEPAState` and the logging infrastructure.

```mermaid
graph LR
    subgraph "Natural Language / User Space"
        "Optimization Progress"
        "Mutation Selection"
        "Metric Tracking"
        "Candidate Acceptance"
    end

    subgraph "Code Entity Space"
        "Optimization Progress" --> GS["GEPAState"]
        "Mutation Selection" --> RCS["ReflectionComponentSelector"]
        "Metric Tracking" --> ET["ExperimentTracker"]
        "Candidate Acceptance" --> CP["CandidateProposal"]
        
        GS --> ET
        RCS --> RM["ReflectiveMutationProposer"]
        CP --> RM
        RM --> GS
    end
```
Sources: [src/gepa/core/state.py:7-12](), [src/gepa/logging/experiment_tracker.py:7-35](), [src/gepa/proposer/reflective_mutation/base.py:16-24](), [src/gepa/proposer/base.py:31-45]()

### Data and Evaluation Flow
This diagram maps the flow of data from raw inputs to the persistent results, highlighting the roles of the `Signature` and `GEPAResult`.

```mermaid
graph TD
    subgraph "Natural Language / Data Space"
        "Input Prompts"
        "LLM Responses"
        "Evaluation Scores"
        "Final Artifacts"
    end

    subgraph "Code Entity Space"
        "Input Prompts" --> SIG["Signature"]
        "LLM Responses" --> LM["LanguageModel"]
        "Evaluation Scores" --> SE["SubsampleEvaluation"]
        "Final Artifacts" --> RES["GEPAResult"]
        
        SIG --> LM
        LM --> SE
        SE --> RES
        RES --> HTML["candidate_tree_html"]
    end
```
Sources: [src/gepa/proposer/reflective_mutation/base.py:27-65](), [src/gepa/proposer/base.py:12-28](), [src/gepa/core/result.py:16-120]()