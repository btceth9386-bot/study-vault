---
id: chain-of-thought-reasoning
title: Chain-of-Thought Reasoning
depth: 2
lab_status: not-started
last_reviewed: '2026-05-13'
review_due: '2026-05-16'
sources:
- sources/repos/stanfordnlp-dspy/
related:
- llm-program-distillation
tags:
- llm-engineering
- llm
- prompt-optimization
- agents
- few-shot-learning
- chain-of-thought
- python
---

# Chain-of-Thought Reasoning

- **一句話定義**：Chain-of-thought (CoT) prompting adds an intermediate natural-language reasoning step before the final answer, letting the model externalize its thinking and dramatically improving accuracy on multi-step or complex tasks.
- **為什麼存在 / 解決什麼問題**：LLMs produce more accurate answers when forced to reason step-by-step before committing to an output. A model asked directly "What is 17 × 24?" may err; the same model asked to "think step by step" first produces a verifiable intermediate chain that catches errors before the final answer. This works because the reasoning text becomes additional context in the model's own forward pass — each reasoning token informs the next token, effectively giving the model more computation per question. In DSPy, `dspy.ChainOfThought(signature)` automatically prepends a `reasoning: str` field to the Signature's output fields, and this field is tunable — optimizers can include demonstrations where the reasoning was especially good, teaching the model to produce structured, effective reasoning chains. The pattern generalizes: `dspy.ProgramOfThought` extends CoT by generating executable Python code as the reasoning step, then running it to get a deterministic answer. The core trade-off is cost: CoT produces more output tokens (typically 2–5× longer responses), which increases latency and API cost but often reduces the number of retries needed for correct outputs.
- **關鍵字**：llm-engineering, llm, prompt-optimization, agents, few-shot-learning, chain-of-thought, python
- **相關概念**：[[llm-program-distillation]]
- **深度等級**：2/4
- **最後更新**：2026-05-13
- **來源**：stanfordnlp/dspy

## 摘要

Think of Chain-of-Thought Reasoning as a design pattern for making agent or backend systems easier to operate. Chain-of-thought (CoT) prompting adds an intermediate natural-language reasoning step before the final answer, letting the model externalize its thinking and dramatically improving accuracy on multi-step or complex tasks. It matters because the simple version of the system usually works only in demos; production systems need state, boundaries, recovery, and observability. LLMs produce more accurate answers when forced to reason step-by-step before committing to an output.

## 範例

Suppose an engineering team is turning an agent prototype into a service used every day. Instead of treating Chain-of-Thought Reasoning as theory, they ask: what breaks if this piece is missing? The answer is visible in the source, **stanfordnlp/dspy**: LLMs produce more accurate answers when forced to reason step-by-step before committing to an output. That makes the concept a design check the team can apply before the system reaches production.

## 與既有概念的關聯

- [[llm-program-distillation]]: chain-of-thought-reasoning connects to llm-program-distillation because both describe a nearby part of the same learning path or system design problem.

## 我的疑問

- What examples would make this concept easier to recognize in future sources?
- When would this concept be misleading or too broad?
