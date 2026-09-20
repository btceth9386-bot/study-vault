# Lab: LangGraph State Flow — Reducer vs. Overwrite

- **Concepts**: langgraph-stategraph-state-schema, langgraph-channels-and-reducers
- **Tools**: none (pure `langgraph` StateGraph, no LLM calls, no external services)
- **Setup mode**: local-mock
- **Time box**: 20–30 min
- **Starting knowledge**: comfortable reading basic Python (functions, dicts, type hints). No prior LangGraph experience required.

## Quick primer

A LangGraph `StateGraph` is built from a state schema (a `TypedDict`). Every field in that
schema becomes a **channel** at compile time. When a node returns a partial update
(e.g. `{"results": ["a"]}`), LangGraph writes that update into the matching channel:

- A plain field (no reducer) uses **last-write-wins**: the new value replaces the old one.
- A field annotated with `Annotated[<type>, <reducer_fn>]` uses that **reducer** to merge the
  new value with the existing one instead of replacing it.

That single annotation is the entire difference between state that gets clobbered and state
that accumulates. This lab makes that difference visible by running both kinds of channel
side by side through the same three nodes.

## Goal

Build intuition for how state flows through a graph: watch one channel get overwritten on every
node and another channel accumulate, then write the one line of logic (the reducer) that causes
the accumulation.

## What the AI scaffolded

- `graph_lab.py` — a runnable 3-node linear `StateGraph` (`node_a → node_b → node_c`).
  - The graph, nodes, edges, and `stream`/`invoke` trace-printing are complete.
  - The state schema defines two channels on purpose:
    - `last_note: str` — **no reducer**, so it is expected to be overwritten each step.
    - `results: Annotated[list[str], accumulate_results]` — **has a reducer**, but the
      reducer body is stubbed as `TODO: YOUR CORE`.
  - Running the script as-is will raise `NotImplementedError` when `node_a` writes to
    `results` — that failure is intentional and is your starting point.
- `requirements.txt` — the one dependency (`langgraph`) needed to run it locally.

## Your core task

Implement `accumulate_results(existing, new)` in `graph_lab.py`. It receives the channel's
current value and a node's new partial update for that channel, and must return the merged
value that LangGraph should store. The goal behavior: after all three nodes run, `results`
must contain every node's contribution, in the order the nodes ran (`["a", "b", "c"]`), not
just the last one.

Do not touch `last_note`, the nodes, or the graph wiring — those exist specifically so you can
compare their behavior against the channel you fix.

## Steps

1. Read the scaffold (`graph_lab.py`) top to bottom before running anything.
2. Fill `predictions.md` BEFORE running (do not skip — prediction comes first).
3. Implement the stubbed core (marked `TODO: YOUR CORE`) in `graph_lab.py`.
4. Run it and trace through:
   ```bash
   pip install -r requirements.txt
   python graph_lab.py
   ```
   then diff what you see against `expected.md`.
5. Open `review-site/index.html` in a browser to inspect the architecture and acceptance
   criteria in a more visual form.
6. (Optional, if you're using the full Exobrain workflow) Run `lab-review.md` so the AI grades
   your prediction and core and emits quiz cards.

## Failure / comparison case

The script prints the full state dict after every node (`stream_mode="values"`), so both
channels are visible side by side on every line of output:

- **`last_note` (no reducer)** — each printed state shows only the note from the node that
  just ran. The two previous notes are gone. This is the classic LangGraph surprise:
  "I returned an update, why did my earlier data disappear?" Answer: no reducer means replace,
  not merge.
- **`results` (with reducer, once you implement it)** — each printed state shows the list
  growing by one entry per node, keeping everything from every prior step.

Comparing these two lines at each step is the whole lab: same graph, same three nodes, same
kind of partial-update return value — the only difference is one type annotation.

## Optional deepening (not required for this lab)

If 20–30 minutes wasn't enough and you want to go further without adding new setup:

- **langgraph-checkpoint-time-travel-forking**: add a checkpointer to `graph_lab.py` and replay
  state as of `node_b` to see the channel values at that point in history.
- **langgraph-human-in-the-loop-interrupts**: add an `interrupt()` before `node_c` and observe
  that `results` still holds `["a", "b"]` while the graph is paused, which is only meaningful
  once you've seen the reducer accumulate correctly.

Keep the base lab as-is if you attempt these — copy `graph_lab.py` to a second file rather than
modifying the original, so the reducer/overwrite comparison stays intact.
