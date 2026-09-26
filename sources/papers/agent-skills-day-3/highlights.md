# Highlights

- `p. 7` Agent Skills address context overload, missing procedural memory, excessive multi-agent complexity, and portability across runtimes.
- `p. 9` A skill can originate either from existing domain knowledge or from a successful workflow that an agent and reviewer crystallize for reuse.
- `p. 10` Progressive disclosure has three layers: always-visible metadata, a conditionally loaded `SKILL.md` body, and resources loaded or executed only as needed.
- `p. 11` The description field acts as the routing algorithm and should state concrete triggers as well as explicit non-triggers.
- `p. 14` MCP provides reach into external systems, while a skill provides the know-how for using that reach; project instructions remain always loaded.
- `p. 18` Skill failures fall into four groups: trigger, execution, token-budget, and regression failures.
- `pp. 21-24` Evaluation must assess both the final answer and the tool trajectory, because a plausible result can hide an unsafe or incorrect sequence of actions.
- `pp. 24-27` Isolation can conceal context and interaction failures, so tests must include realistic co-loading and cover all four failure groups.
- `pp. 30-34` Skills are conditional, composable, owned units of improvement that reduce the active-context cost of expanding an agent's capabilities.
- `pp. 35-37` Meta-skills can author and improve skills, but evaluation gates and early human review are necessary to prevent metric gaming and regressions.
- `pp. 38-41` Reliable composition externalizes structured state instead of using the model's context window as a database or message bus.
- `pp. 41-43` Skill adoption should prefer first-party sources, pin versions, and audit third-party packages as supply-chain dependencies.
- `pp. 55-57` Skill ownership belongs with the teams that own the underlying expertise, while deployment authority should progress from read-only to draft-only to action-allowed.
