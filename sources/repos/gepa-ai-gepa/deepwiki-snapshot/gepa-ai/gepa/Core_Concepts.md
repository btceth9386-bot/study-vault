This page introduces the fundamental abstractions, data structures, and mechanisms that underpin GEPA's optimization approach. Understanding these concepts is essential for effectively using GEPA, configuring optimization runs, and integrating GEPA with custom systems.

For detailed API documentation of the primary user-facing functions, see [The optimize Function](#3.1) and [The optimize_anything API](#3.2). For system integration patterns, see [Adapters and System Integration](#3.3).

---

## Overview: The Optimization Problem

GEPA (Genetic-Pareto) is a framework for optimizing any system with textual parameters against any evaluation metric. Unlike reinforcement learning or gradient-based methods that collapse execution traces into a single scalar reward, GEPA treats the system as a black box that:

1. Accepts text parameters (e.g., prompts, code, configurations, architectures) as input.
2. Produces outputs on a dataset.
3. Returns scalar scores and optional execution traces.

GEPA's core mechanism is the use of **Actionable Side Information (ASI)**—execution traces like error messages, logs, or intermediate reasoning—as textual feedback that an LLM can analyze to diagnose failures and propose targeted fixes.

**Key files:**
- [src/gepa/api.py:43-96]() - Main `optimize()` entry point
- [src/gepa/optimize_anything.py:53-131]() - Universal `optimize_anything()` API
- [src/gepa/core/engine.py:51-134]() - `GEPAEngine` orchestration logic

---

## Core Abstractions

### Candidates and Text Components

A **candidate** is a mapping from component names to component texts, represented as `dict[str, str]`. Each candidate defines a complete instantiation of the system being optimized.

```python