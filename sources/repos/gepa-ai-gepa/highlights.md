# Highlights

- `Overview.md Section: Overview` GEPA optimizes textual system components with LLM-based reflection and Pareto-efficient evolutionary search, using execution traces to make targeted improvements with far fewer evaluations than reward-only search.
- `Core_Concepts.md Section: Overview: The Optimization Problem` GEPA treats the target system as a black box that accepts text parameters, produces outputs on a dataset, and returns scores plus optional execution traces.
- `Candidates_and_Text_Components.md Section: What is a Candidate` A candidate is a dictionary mapping component names to text values; it represents one complete instantiation of the optimized system.
- `Reflective_Mutation_Proposer.md Section: Reflective Mutation Workflow` The proposer selects a candidate, evaluates it with trace capture, builds a reflective dataset, asks a reflection model for new text, and evaluates the mutated candidate.
- `Reflective_Mutation_Proposer.md Section: Merge Proposer` Merge combines successful descendants of a common ancestor so improvements that solve different weaknesses can be recombined.
- `Adapter_System.md Section: GEPAAdapter Protocol Definition` The adapter protocol requires evaluation and reflective dataset construction, keeping domain-specific execution outside the core engine.
- `Evaluation_Policies.md Section: RoundRobinSampleEvaluationPolicy` Incremental evaluation can prioritize under-evaluated validation examples, making validation coverage more balanced under a limited budget.
- `Evaluation_Caching.md Section: Purpose and Scope` Caching avoids redundant candidate-example evaluations, especially when proposers or validation policies revisit overlapping examples.
- `OptimizeAnythingAdapter.md Section: Key Implementation Details` `optimize_anything()` instruments user evaluators to capture `oa.log()`, stdio, and returned side information as feedback for reflection.
- `Production_Use_Cases.md Section: Performance and Efficiency Metrics` Reported production patterns emphasize low-data, budgeted optimization with fewer evaluations than traditional RL-style methods.

## Recommended follow-up ingestions

| Type | URL | Description |
|------|-----|-------------|
| Repository | https://github.com/gepa-ai/gepa | Primary GitHub repository behind the DeepWiki snapshot. |
| Website | https://dspy.ai/ | DSPy documentation, useful because GEPA has a first-class DSPy integration. |
| Repository | https://github.com/BerriAI/litellm | LiteLLM integration context for GEPA's model abstraction and provider support. |
