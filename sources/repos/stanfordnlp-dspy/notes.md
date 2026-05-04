# stanfordnlp/dspy

## Summary

DSPy (Declarative Self-improving Python) is a framework from Stanford NLP that replaces hand-crafted prompt strings with **composable Python programs that are automatically optimized**. The central claim: prompts are implementation details, not the thing you should be writing by hand. You declare what a task needs (a `Signature`), compose modules to build a program, define a metric for success, and let an optimizer figure out the best prompts and few-shot examples.

The framework has three core abstractions. A **Signature** declaratively specifies the input and output fields for an LLM task — written as either a string (`"question -> answer"`) or a Python class with typed fields and a docstring instruction. This separates *what* the LLM should accomplish from *how* it is prompted. A **Module** is a composable program component: `dspy.Predict` is the basic unit (wraps a Signature into an LLM call); `dspy.ChainOfThought` adds a `reasoning` field before the answer; `dspy.ReAct` implements an agentic loop of thought-action-observation steps; `dspy.ProgramOfThought` generates Python code for execution. Modules nest freely — a `dspy.Module` subclass can contain other modules and is jointly optimizable. An **Optimizer** (formerly "teleprompter") tunes the program's parameters given training examples and a metric. The three main families are: **Few-Shot** (`BootstrapFewShot`, `BootstrapFewShotWithRandomSearch`) which automatically synthesizes demonstrations by running a teacher program; **Instruction** (`MIPROv2`, `COPRO`) which uses Bayesian optimization over instruction candidates; and **Weight** (`BootstrapFinetune`) which distills the full program into a fine-tuned smaller model.

The bootstrapping process is central: given labeled examples, a teacher program is run, successful traces are filtered by a metric threshold, and the resulting demonstrations are assigned to the student program's predictors. `MIPROv2` extends this by also searching the instruction space using Optuna's Tree-Parzen Estimator (Bayesian optimization), jointly tuning both instructions and demo sets. `SIMBA` goes further — it identifies "challenging" examples across mini-batches and generates natural-language improvement rules, not just demonstrations.

State is fully serializable: `dump_state()` / `load_state()` captures all optimized parameters (instructions, demonstrations) and can be versioned like a model checkpoint. A two-tier LRU + disk cache (keyed by SHA-256 of the request) makes repeated calls fast; `rollout_id` bypasses the cache during optimization runs. DSPy integrates with 40+ LLM providers via LiteLLM, supports streaming, async/parallel execution, and typed outputs via `JSONAdapter` or Pydantic schemas. Production users include Shopify (550× cost reduction on extraction tasks via GEPA), Databricks, Dropbox, and AWS.

## Knowledge Map

- Signatures: declarative input/output spec for LLM tasks; typed fields with constraints
- Modules: Predict, ChainOfThought, ReAct, ProgramOfThought, RLM — composable building blocks
- Optimizers: BootstrapFewShot, MIPROv2, SIMBA, GEPA, BootstrapFinetune
- Compile-then-run model: write → optimize → serialize → deploy
- Bootstrapping: teacher-student execution to auto-generate few-shot demonstrations
- Bayesian instruction optimization: Optuna TPE over (instruction, demo_set) index space
- LLM distillation: bootstrap training data from large model, fine-tune small model
- Two-tier caching: memory LRU + disk FanoutCache; rollout_id for stochastic experiments
- Adapter system: ChatAdapter, JSONAdapter, XMLAdapter, TwoStepAdapter for structured outputs
- Streaming and async execution: streamify, asyncify, dspy.Parallel

## Key Takeaways

- The core insight: treat LLM programs like ML models — compile them with an optimizer and a metric, don't hand-tune them
- Signatures make programs portable across models: the same program can run on GPT-4o, Llama-3, Gemini by recompiling — no model-specific prompt rewrites
- ChainOfThought is one of the highest-leverage single changes in LLM programming — adding a `reasoning` field before the answer consistently improves accuracy across tasks
- BootstrapFewShot generates better few-shot examples than hand-curation because it filters by the actual success metric, not human intuition
- MIPROv2's Bayesian search makes instruction tuning tractable: it evaluates ~100 combinations systematically rather than relying on trial-and-error
- BootstrapFinetune closes the distillation loop: a GPT-4o-optimized program can train a Llama-3.2-1B replacement that's 550× cheaper at similar quality
- Save/load state means an optimized DSPy program is a versioned artifact, not a prompt string — it's closer to a trained model than a prompt template
