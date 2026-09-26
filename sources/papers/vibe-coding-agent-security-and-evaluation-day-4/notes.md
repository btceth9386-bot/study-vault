# Vibe Coding Agent Security and Evaluation

## Summary

This paper argues that production-grade coding agents require two separate forms of assurance: security determines whether an agent stayed within its permitted boundary, while evaluation determines whether the work inside that boundary was useful and worth shipping. A raw model becomes an agent only through a harness that supplies state, tools, execution, feedback, identity, and enforceable constraints. Because autonomous behavior is non-deterministic, trust must be continuously recomputed from runtime context instead of granted once through a static credential.

The proposed security architecture combines isolated execution, governed network egress, supply-chain verification, protected prompts and data, contextual tool authorization, dedicated agent identities, short-lived least-privilege credentials, behavioral monitoring, and auditable governance. Particular risks include hallucinated package names exploited through slopsquatting, spoofed MCP servers, prompt injection hidden in repositories, denial-of-wallet loops, excessive browser-side trust, and agents acting as confused deputies. High-risk actions should require a plain-language “Vibe Diff” and strong human authorization. Runtime traces, an Agent Bill of Materials, checkpoints, and stateful quarantine make drift visible and contain failures without destroying forensic state.

Evaluation must compensate for underspecified user intent, limited human ability to inspect generated code, and sessions that progressively mutate a real codebase. The paper recommends measuring intent satisfaction, functional and visual correctness, cost, convention fit, trajectory quality, and self-repair. No single method covers all dimensions, so teams should combine deterministic tests, security scans, model judges, browser testing, trace inspection, calibrated human review, and risk-biased online sampling. Session-level convergence, rendered artifacts, and clusters of user corrections provide stronger product signals than isolated turn accuracy or benchmark scores alone.

## Knowledge Map

- Continuous effective trust enforced by the agent harness
- Sandboxing, dependency provenance, and governed egress
- Agent identity, contextual authorization, and human approval
- Runtime behavior analytics, quarantine, and rollback
- Multidimensional, trace-aware, session-level evaluation

## Key Takeaways

- Security and evaluation answer different questions; passing one does not imply passing the other.
- Generated code should execute with ephemeral state, narrow credentials, and deterministic CI gates.
- Agent activity needs runtime inventories and end-to-end traces, not static asset lists alone.
- Evaluate the delivered artifact and full session against inferred intent, not only tests or final text.
- Use standardized benchmarks for calibration, then validate against real project conventions and user behavior.
