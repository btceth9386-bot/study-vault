---
id: llm-program-distillation
title: LLM Program Distillation
depth: 2
lab_status: not-started
last_reviewed: '2026-05-13'
review_due: '2026-05-16'
sources:
- sources/repos/stanfordnlp-dspy/
related:
- chain-of-thought-reasoning
tags:
- llm-engineering
- llm
- prompt-optimization
- agents
- few-shot-learning
- chain-of-thought
- python
---

# LLM Program Distillation

- **一句話定義**：LLM program distillation uses a large, expensive model to generate high-quality (input, output) training pairs from a bootstrapped program, then fine-tunes a small, cheap model on those pairs — transferring the large model's task-specific behavior at a fraction of the inference cost.
- **為什麼存在 / 解決什麼問題**：The gap between frontier model quality and small model quality is often partially closable for narrow tasks. A GPT-4o-based DSPy program that has been optimized for a specific extraction or classification task generates reliable outputs on that task — those outputs become training data. Fine-tuning a Llama-3.2-1B on thousands of such examples teaches it to replicate the task-specific behavior, achieving similar quality at 100–1000× lower cost per inference call. Shopify used this approach (via GEPA + `BootstrapFinetune`) to achieve a 550× cost reduction on product attribute extraction. The mechanics in DSPy: (1) compile a teacher program with `BootstrapFewShot` using a capable LLM; (2) run it on a large dataset to collect `(input_fields, output_fields)` pairs; (3) call `BootstrapFinetune.compile(student, teacher, trainset)` which submits a fine-tuning job to a provider (`LocalProvider` via SGLang+TRL, `DatabricksProvider`, `OpenAIProvider`); (4) the returned student program uses the fine-tuned model and requires zero or fewer few-shot examples because the behavior is now encoded in the weights. The key constraint: distillation only works well for tasks where the large model is already reliable — if the teacher has low quality, the fine-tuned student inherits that noise.
- **關鍵字**：llm-engineering, llm, prompt-optimization, agents, few-shot-learning, chain-of-thought, python
- **相關概念**：[[chain-of-thought-reasoning]]
- **深度等級**：2/4
- **最後更新**：2026-05-13
- **來源**：stanfordnlp/dspy

## 摘要

Think of LLM Program Distillation as a design pattern for making agent or backend systems easier to operate. LLM program distillation uses a large, expensive model to generate high-quality (input, output) training pairs from a bootstrapped program, then fine-tunes a small, cheap model on those pairs — transferring the large model's task-specific behavior at a fraction of the inference cost. It matters because the simple version of the system usually works only in demos; production systems need state, boundaries, recovery, and observability. The gap between frontier model quality and small model quality is often partially closable for narrow tasks.

## 範例

Suppose an engineering team is turning an agent prototype into a service used every day. Instead of treating LLM Program Distillation as theory, they ask: what breaks if this piece is missing? The answer is visible in the source, **stanfordnlp/dspy**: The gap between frontier model quality and small model quality is often partially closable for narrow tasks. That makes the concept a design check the team can apply before the system reaches production.

## 與既有概念的關聯

- [[chain-of-thought-reasoning]]: llm-program-distillation connects to chain-of-thought-reasoning because both describe a nearby part of the same learning path or system design problem.

## 我的疑問

- What examples would make this concept easier to recognize in future sources?
- When would this concept be misleading or too broad?
