# Highlights

- `Section: 1. What Is an Agent` An agent differs from a pipeline because the model dynamically chooses the application's next action and tool use.
- `Section: 6. Loop Termination` Reliable loops combine model-declared completion with hard step, token, cost, or goal-verification boundaries.
- `Section: 14. Compaction Strategies` Structured incremental summaries preserve goals, decisions, modified artifacts, resolved errors, and next steps better than truncation or a fixed sliding window.
- `Section: 18. What Is Context Rot` Context can lose practical usefulness well before reaching the model's maximum window because relevant information becomes harder to attend to.
- `Section: 22. The 12 Defenses Against Context Rot` High-signal context requires active pruning, instruction reinjection, scoped retrieval, recoverable references, phase handoffs, and isolated exploration.
- `Section: 24. Agent Cognitive Compressor (ACC)` A bounded, schema-constrained cognitive state offers an alternative to retaining and repeatedly summarizing an ever-growing conversation.
- `Section: 18. The Memory Hierarchy` Working, session, long-term, episodic, and observational memory serve different lifetimes and should not be collapsed into one store.
- `Section: 28. Code-as-Action` Executable code gives an agent variables, loops, and multi-tool composition in one action, but reduces auditability and demands a robust sandbox.
- `Section: 31. The Tool Sprawl Crisis` Large always-loaded tool catalogs consume context and impair selection; compressed descriptions, small toolsets, search, and progressive disclosure reduce that burden.
- `Section: 32. Why Multi-Agent` A single agent should remain the default until specialization, separate authority, quality control, or parallel work provides a concrete benefit.
- `Section: 34. State Passing Between Agents` Shared state, typed artifacts, and messages are distinct handoff mechanisms with different coupling and auditability.
- `Section: 44. Checkpointing` Persisting state transitions enables crash recovery, replay, branching, debugging, and audit trails for long-running work.
- `Section: 47. Prompt Injection Defense` Untrusted tool content must remain subordinate to system instructions and pass isolation, policy validation, sandbox, and approval controls before causing side effects.
- `Section: 51. Evals in Production` Completion rate alone is insufficient; turns, tool success, interventions, cost, latency, errors, and compaction behavior expose operational quality.
