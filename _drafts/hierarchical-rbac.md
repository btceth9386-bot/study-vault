---
id: hierarchical-rbac
title: Hierarchical RBAC
source: sources/repos/langfuse-langfuse
status: draft
created_at: 2026-05-04
---

- **One-sentence definition**: A role-based access control design where roles are defined at a parent scope (organization) and can be selectively overridden at a child scope (project), with the effective permission being the maximum of both roles — enabling uniform defaults with targeted exceptions.
- **Why it matters**: Flat RBAC forces a choice between simplicity (one role per user, hard to customize) and flexibility (role per resource, requires managing N×M assignments). Hierarchical RBAC achieves both: an organization MEMBER gets standard access to all projects by default, but a specific project can override that user to VIEWER or OWNER. The `max(org_role, project_role)` rule means project overrides can only grant additional access, never restrict below the org baseline — which is intentional: org OWNER always wins. This prevents the accidental lockout scenarios that arise when project restrictions can override org admin access. Fine-grained scopes (`resource:action`, e.g., `prompts:CUD`, `auditLogs:read`) decouple what roles can do from the role hierarchy itself, enabling easy extension.
- **Relationship to other concepts**: Hierarchical RBAC is the access layer over multi-tenancy, which is a prerequisite for SaaS products. The entitlement system (plan-gated features) sits above RBAC — some scopes require a specific billing plan regardless of role. Server-side enforcement via tRPC middleware (`throwIfNoProjectAccess`) pairs with client-side hooks (`useHasProjectAccess`) for defense in depth, a principle from SSL-termination and firewall design: check at multiple layers, not just one.
