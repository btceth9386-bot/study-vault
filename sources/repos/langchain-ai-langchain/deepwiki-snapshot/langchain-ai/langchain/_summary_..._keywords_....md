```

In LCEL, a plain `dict` literal used in a `|` expression is automatically coerced to `RunnableParallel`:

```python
chain = model | {"parsed": parser, "raw": RunnablePassthrough()}
```

Concurrent execution uses the same thread pool / `asyncio.gather` mechanism as `batch`, controlled by `RunnableConfig.max_concurrency`.

Sources: [libs/core/langchain_core/runnables/base.py:618-638](), [libs/core/langchain_core/runnables/passthrough.py:74-134]()

---

## RunnableBranch

`RunnableBranch` routes to one of several `Runnable` objects based on predicates evaluated against the input.

```python
branch = RunnableBranch(
    (lambda x: x["topic"] == "science", science_chain),
    (lambda x: x["topic"] == "math", math_chain),
    general_chain,  # default — must be last, no condition
)
```

Each condition is coerced to a `Runnable`. If no condition returns truthy, the final (default) branch runs. `RunnableBranch` requires at least two arguments: one `(condition, runnable)` pair and a default.

Sources: [libs/core/langchain_core/runnables/branch.py:42-180]()

---

## RunnableLambda

`RunnableLambda` wraps any Python callable into a `Runnable`. It is the primary mechanism for injecting custom logic into LCEL chains.

Constructor: `RunnableLambda(func, afunc=None)` where:
- `func` — sync callable or async callable (if async, treated as `afunc`)
- `afunc` — explicit async callable; if both are provided, `func` is used in sync paths and `afunc` in async paths

Input/output types are inferred from function annotations. For functions with no annotations, `RunnableLambda` inspects the function's source code via AST analysis (`get_function_first_arg_dict_keys` in `utils.py`) to infer the input schema from dict key accesses.

**Generator support:** if `func` is a generator function (`yield`-based), `RunnableLambda` becomes streamable. Async generators are supported via `afunc`.

The `@chain` decorator is a shorthand that creates a `RunnableLambda` from a generator function and makes it composable.

Sources: [libs/core/langchain_core/runnables/base.py:618-638](), [libs/core/langchain_core/runnables/utils.py:365-404]()

---

## RunnablePassthrough

`RunnablePassthrough` returns its input unchanged. It is useful inside `RunnableParallel` to forward the original input alongside computed values.

```python
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

chain = RunnableParallel(
    context=retriever,
    question=RunnablePassthrough(),
)
# Input "what is X?" → {"context": [doc1, doc2], "question": "what is X?"}
```

An optional `func` (or `afunc`) can be provided to run a side-effect on the input without changing the output.

### RunnablePassthrough.assign

`RunnablePassthrough.assign(**kwargs)` creates a `RunnableAssign` that merges new computed keys into an existing dict input, preserving all existing keys:

```python
chain = RunnablePassthrough.assign(
    context=lambda x: retriever.invoke(x["question"]),
)