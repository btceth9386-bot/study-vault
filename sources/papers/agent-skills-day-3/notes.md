# Agent Skills

## Summary

This paper presents Agent Skills as portable, on-demand packages of procedural knowledge for general-purpose AI agents. A skill is anchored by a `SKILL.md` file and may include scripts, references, and assets. Its central design principle is progressive disclosure: compact metadata is always visible for routing, the instruction body loads only when the skill matches the task, and supporting resources load only when needed. This keeps active context smaller than a monolithic system prompt while allowing a large library of specialized capabilities.

The paper treats a skill's description as a routing interface rather than documentation. A useful description states what the skill does, includes concrete positive triggers, and defines negative boundaries. Skills complement rather than replace tools, MCP servers, or project-wide instructions: tools provide access, project instructions provide persistent conventions, and skills provide task-specific know-how.

Production readiness depends on evaluation across four failure surfaces: triggering, execution, regression, and token budget. Tests should inspect both final outputs and tool trajectories, use positive and negative trigger cases, exercise skills alongside the wider library, and require stronger evidence as authority increases. The proposed read-only, draft-only, and action-allowed tiers connect evaluation rigor to operational risk.

Skills also provide a small, versioned unit for improving an agent without changing the model or enlarging a global prompt. Meta-skills can draft or revise skills from successful traces and failed evaluations, but every generated change should enter a gated review process. For multi-skill workflows, state should live in structured files or message buses rather than accumulating in model context. Finally, skill libraries require ordinary dependency discipline: clear ownership, version pinning, audits, tests, and stricter review for community packages.

## Knowledge Map

- Skills as portable procedural memory for agents
- Progressive disclosure and active-context budgeting
- Descriptions as routing interfaces
- Output, trajectory, regression, and token-budget evaluation
- Risk-based authority tiers for deployment
- Evaluation-gated meta-skills and library evolution
- Externalized state for multi-skill composition
- Ownership and supply-chain governance

## Key Takeaways

- Keep one skill focused on one reusable job.
- Put deterministic work in scripts and load reference material only when needed.
- Test when a skill should and should not trigger before trusting its output.
- Evaluate the full agent-and-library system under realistic context load.
- Match deployment authority to evidence: read, draft, then act.
- Treat every installed skill as executable, versioned supply-chain material.
