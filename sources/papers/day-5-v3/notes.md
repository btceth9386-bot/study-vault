# Spec-Driven Production Grade Development in the Age of Vibe Coding

## Summary

This paper argues that AI-assisted software development becomes production-grade only when fast code generation is surrounded by explicit specifications, verification, integration practices, and enforceable safety boundaries. A repository-held specification acts as an architectural source of truth for both people and agents. It should combine technical design, contracts, diagrams, versioned dependencies, rationale, and behavior-oriented scenarios so the agent has less room to guess. Instructions should also be placed according to their scope: transient orchestration in chat, task-specific designs in a versioned `specs/` directory, reusable procedures in skills, and stable identity or project conventions in hierarchical configuration files.

The paper recommends changing prompts with the job. Project generation begins with an agreed architecture; feature work follows local conventions and exposes diffs; bug fixing starts from evidence and a failing reproduction; documentation remains synchronized with code; and data work shows the exact query used. MCP is presented as a reusable boundary through which compatible agents can discover and invoke tools.

Because AI increases change volume, the bottleneck shifts from writing code to reviewing and integrating it. Suggested responses include risk-oriented PR summaries, automated style checks, conditional merges after tests, clearer file ownership, continuous review agents, and choosing the least elaborate review runtime that catches the team's actual risks. Teams must also manage approval fatigue so human checkpoints remain meaningful.

Production safety requires controls outside the model prompt. Sandboxes contain execution, human checkpoints guard high-impact actions, deterministic tests catch repeatable regressions, and behavioral evaluations detect probabilistic drift. A hybrid policy server combines fast role/environment rules with semantic inspection of proposed tool use, while context hygiene reduces the chance that stale or sensitive strings become accidental action parameters. Overall, the developer's role shifts toward specifying intent, designing controls, and integrating verified output.

## Knowledge Map

- Versioned specifications as shared implementation and verification contracts
- Instruction placement by lifetime, scope, and reuse
- Prompt modes for architecture, features, diagnosis, documentation, and data
- Risk-focused review and tiered continuous review runtimes
- Sandboxing, human checkpoints, tests, evaluations, and policy enforcement
- Sustainable oversight under high AI-generated change volume

## Key Takeaways

- Treat the specification, not generated code, as the durable source of truth.
- Put each instruction where its scope and lifetime justify its context cost.
- Start bug fixes with evidence and a failing reproduction, then make one root-cause change.
- Automate mechanical review and reserve human attention for architecture and material risk.
- Enforce safety outside prompts through sandboxes, policy checks, scoped approval, tests, and evaluations.
- Use the lowest-complexity review runtime that reliably catches the risks that matter.
