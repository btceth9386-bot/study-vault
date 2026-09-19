# Highlights

- [`notes.md` — Section: What is promptfoo?](notes.md#what-is-promptfoo) Promptfoo unifies structured LLM evaluation, provider comparison, adversarial testing, CI integration, and model-oriented code scanning.
- [`notes.md` — Section: Core Evaluation System / Evaluation Pipeline](notes.md#core-evaluation-system) A test suite expands into prompt × provider × test cells, each flowing through rendering, provider execution, transformation, assertions, and persistence.
- [`notes.md` — Section: Assertions and Grading / Assertion Types](notes.md#assertion-types) Deterministic, model-graded, and trace-aware assertions provide complementary evidence instead of relying on one scoring method.
- [`notes.md` — Section: Provider Abstractions](notes.md#provider-abstractions) The `ApiProvider` contract and registry isolate evaluation orchestration from vendor-specific authentication, requests, and response parsing.
- [`notes.md` — Section: Red Team System / System Architecture](notes.md#red-team-system) Red-team plugins generate risk-specific probes while strategies independently transform their delivery, enabling reusable combinations.
- [`notes.md` — Section: Attack Providers / The Attack Loop](notes.md#attack-providers) Stateful attacks alternate between an attacker, target, and judge, using scores and history to refine or branch subsequent attempts.
- [`notes.md` — Section: OpenTelemetry Tracing / Trajectory and Trace-Aware Assertions](notes.md#trajectory-and-trace-aware-assertions) Stored spans are normalized into tool-use trajectories that assertions can check for tools, arguments, sequence, and goal completion.
- [`notes.md` — Section: Core Evaluation System / Concurrency and Rate Limiting](notes.md#core-evaluation-system) Queues and adaptive rate controls make large evaluation matrices practical without coupling tests to provider limits.
