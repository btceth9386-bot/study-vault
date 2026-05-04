---
id: llm-program-optimization-dspy
title: "LLM Program Optimization with DSPy"
description: A focused path for building multi-step LLM programs that improve automatically — covering DSPy's core abstractions, the bootstrapping and compilation workflow, and agentic tool use, all grounded in metric-driven optimization rather than hand-tuned prompts.
---

## Overview

Most LLM developers write prompts by hand and improve them by feel. DSPy replaces that with a programming model: declare task structure with Signatures, compose programs from Modules, define a success metric, and let an optimizer compile better prompts and few-shot examples automatically. This path moves from "understanding how DSPy structures a program" to "running an optimizer and reading the compiled result" — and ends with observing that result in production.

This path is a focused companion to the broader [Production LLM Engineering](../topics/production-llm-engineering.md) path. Where that path covers the full LLM application stack (monitoring, databases, pipelines), this one stays tightly inside the DSPy workflow.

**Estimated study time:** 3–5 hours  
**Prerequisites:** Comfortable calling LLM APIs (OpenAI / Anthropic). No prior DSPy experience needed. Familiarity with [LLM Observability](../concepts/llm-engineering/llm-observability.md) is helpful for the final step.

---

## Concepts in Order

### 1. [DSPy Signatures — Declarative LLM Task Specification](../concepts/llm-engineering/dspy-signatures.md)
The entry point to DSPy. A Signature names the inputs and outputs of an LLM task and attaches a natural-language instruction — separating *what* the task is from *how* it gets prompted. Start here because every other concept in this path operates on Signatures: modules wrap them, optimizers tune the instruction inside them, and adapters format them for different providers.

### 2. [DSPy Module Composition](../concepts/llm-engineering/dspy-module-composition.md)
Modules are composable units that hold Signatures and predictors. A `dspy.Module` subclass can contain other modules as attributes, and `optimizer.compile()` discovers and tunes all of them in one pass via `named_predictors()`. Study second because you need to understand the program tree structure before optimization — the optimizer traverses and modifies it in-place. The save/load state mechanism (`dump_state()` / `load_state()`) introduced here is how a compiled program becomes a deployable artifact.

### 3. [LLM-as-Judge Evaluation](../concepts/llm-engineering/llm-as-judge-evaluation.md)
Before you can optimize, you need a metric — a function that scores whether a program's output is good. LLM-as-judge is the most common technique: a judge model scores each output against a rubric and returns a float. Study before bootstrapping and optimization because the metric function is the input to both — without a reliable metric, the optimizer is optimizing noise. This is also where DSPy and Langfuse overlap: Langfuse's evaluation system runs the same judge pattern at production monitoring time.

### 4. [Few-Shot Bootstrapping](../concepts/llm-engineering/few-shot-bootstrapping.md)
The concrete mechanism behind most DSPy optimization: run a teacher program on training examples, capture successful traces, filter by the metric, and assign the passing traces as demonstrations to the student program's predictors. Study after the metric concept because the filter step is the metric in action at training time. The key insight: bootstrapped demos are metric-validated, not hand-picked — the optimizer trusts what the metric says is good.

### 5. [Metric-Driven LLM Optimization](../concepts/llm-engineering/metric-driven-llm-optimization.md)
The top-level DSPy paradigm: define success as code, then compile. Covers the full optimizer landscape — `BootstrapFewShot` for demonstrations, `MIPROv2` for joint Bayesian instruction + demo search, `SIMBA` for stochastic rule generation. Study here (after bootstrapping) because it shows how bootstrapping fits inside a larger optimization loop that also searches the instruction space. MIPROv2's auto-run modes ("light", "medium", "heavy") give a practical starting point before tuning optimizer hyperparameters.

### 6. [ReAct Agentic Loop](../concepts/llm-engineering/react-agentic-loop.md)
The pattern for building tool-using agents: Thought (reason about what to do) → Action (call a tool) → Observation (receive the result) → repeat. Study after optimization because `dspy.ReAct` is itself a module with a signature — it benefits from few-shot bootstrapping (the optimizer can learn good tool-calling sequences from traces) and from a metric that evaluates end-to-end task completion, not just individual steps. Understanding the agentic loop also makes module composition concrete: ReAct is a module whose forward pass runs other sub-modules in a loop.

### 7. [LLM Observability](../concepts/llm-engineering/llm-observability.md)
The final step: how to inspect a compiled program running in production. The trace/observation/score model gives you a structured record of every step — which module ran, what prompt it used, how many tokens it consumed, what score it received. Study last because at this point you have a compiled DSPy program (from steps 1–6) and want to verify it is behaving well, compare it to a previous version, and catch regressions. The compiled program's prompt versions appear in traces, closing the loop between optimization and monitoring.

---

## What You'll Be Able to Do

- Write a DSPy Signature for any LLM task and understand how it differs from a raw prompt string
- Compose a multi-step program from `Predict`, `ChainOfThought`, and `ReAct` modules
- Write a metric function and use it to run `BootstrapFewShot` or `MIPROv2` on a training set
- Save a compiled program as a JSON artifact and load it into a different model configuration
- Build a tool-using ReAct agent and optimize its tool-calling behavior via bootstrapped traces
- Connect a compiled DSPy program to an observability platform to monitor its production behavior
