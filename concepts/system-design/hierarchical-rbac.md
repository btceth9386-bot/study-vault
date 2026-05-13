---
id: hierarchical-rbac
title: Hierarchical RBAC
depth: 2
last_reviewed: '2026-05-13'
review_due: '2026-05-16'
sources:
- sources/repos/langfuse-langfuse/
related:
- event-sourcing-staging-propagation
tags:
- system-design
- llm
- observability
- tracing
- evaluation
- prompt-management
- open-source
---

# Hierarchical RBAC

- **一句話定義**：A role-based access control design where roles are defined at a parent scope (organization) and can be selectively overridden at a child scope (project), with the effective permission being the maximum of both roles — enabling uniform defaults with targeted exceptions.
- **為什麼存在 / 解決什麼問題**：Flat RBAC forces a choice between simplicity (one role per user, hard to customize) and flexibility (role per resource, requires managing N×M assignments). Hierarchical RBAC achieves both: an organization MEMBER gets standard access to all projects by default, but a specific project can override that user to VIEWER or OWNER. The `max(org_role, project_role)` rule means project overrides can only grant additional access, never restrict below the org baseline — which is intentional: org OWNER always wins. This prevents the accidental lockout scenarios that arise when project restrictions can override org admin access. Fine-grained scopes (`resource:action`, e.g., `prompts:CUD`, `auditLogs:read`) decouple what roles can do from the role hierarchy itself, enabling easy extension.
- **關鍵字**：system-design, llm, observability, tracing, evaluation, prompt-management, open-source
- **相關概念**：[[event-sourcing-staging-propagation]]
- **深度等級**：2/4
- **最後更新**：2026-05-13
- **來源**：langfuse/langfuse

## 摘要

Think of Hierarchical RBAC as a design pattern for making agent or backend systems easier to operate. A role-based access control design where roles are defined at a parent scope (organization) and can be selectively overridden at a child scope (project), with the effective permission being the maximum of both roles — enabling uniform defaults with targeted exceptions. It matters because the simple version of the system usually works only in demos; production systems need state, boundaries, recovery, and observability. Flat RBAC forces a choice between simplicity (one role per user, hard to customize) and flexibility (role per resource, requires managing N×M assignments).

## 範例

Suppose an engineering team is turning an agent prototype into a service used every day. Instead of treating Hierarchical RBAC as theory, they ask: what breaks if this piece is missing? The answer is visible in the source, **langfuse/langfuse**: Flat RBAC forces a choice between simplicity (one role per user, hard to customize) and flexibility (role per resource, requires managing N×M assignments). That makes the concept a design check the team can apply before the system reaches production.

## 與既有概念的關聯

- [[event-sourcing-staging-propagation]]: hierarchical-rbac connects to event-sourcing-staging-propagation because both describe a nearby part of the same learning path or system design problem.

## 我的疑問

- What examples would make this concept easier to recognize in future sources?
- When would this concept be misleading or too broad?
