llm.with_config(configurable={"llm": "fast"}).invoke("...")
```

Sources: [libs/core/langchain_core/runnables/configurable.py:49-350](), [libs/core/langchain_core/runnables/utils.py:450-600]()

---

## Module Map

**Files and types in the LCEL implementation**

```mermaid
graph TD
    base["langchain_core/runnables/base.py\n────────────────────────\nRunnable\nRunnableSerializable\nRunnableSequence\nRunnableParallel  (RunnableMap)\nRunnableLambda\nRunnableBindingBase\nRunnableBinding\nRunnableEach\ncoerce_to_runnable\nchain decorator"]
    cfg["langchain_core/runnables/config.py\n────────────────────────\nRunnableConfig\nvar_child_runnable_config\nensure_config\nmerge_configs\npatch_config\nget_config_list\nContextThreadPoolExecutor\nDEFAULT_RECURSION_LIMIT=25"]
    passthrough["langchain_core/runnables/passthrough.py\n────────────────────────\nRunnablePassthrough\nRunnableAssign\nRunnablePick"]
    branch["langchain_core/runnables/branch.py\n────────────────────────\nRunnableBranch"]
    fallbacks["langchain_core/runnables/fallbacks.py\n────────────────────────\nRunnableWithFallbacks"]
    history["langchain_core/runnables/history.py\n────────────────────────\nRunnableWithMessageHistory\nGetSessionHistoryCallable"]
    configurable["langchain_core/runnables/configurable.py\n────────────────────────\nDynamicRunnable\nRunnableConfigurableFields\nRunnableConfigurableAlternatives"]
    utils["langchain_core/runnables/utils.py\n────────────────────────\nConfigurableField\nConfigurableFieldSpec\nConfigurableFieldSingleOption\nConfigurableFieldMultiOption\nAddableDict\nInput, Output"]
    schema["langchain_core/runnables/schema.py\n────────────────────────\nStreamEvent\nEventData\nStandardStreamEvent\nCustomStreamEvent"]
    log_stream["langchain_core/tracers/log_stream.py\n────────────────────────\nRunLog\nRunLogPatch\nRunState\nLogEntry\nLogStreamCallbackHandler"]
    event_stream["langchain_core/tracers/event_stream.py\n────────────────────────\n_AstreamEventsCallbackHandler\nRunInfo"]

    base --> cfg
    base --> utils
    base --> log_stream
    base --> event_stream
    passthrough --> base
    branch --> base
    fallbacks --> base
    history --> base
    configurable --> base
    event_stream --> schema
    event_stream --> log_stream
```

Sources: [libs/core/langchain_core/runnables/base.py:1-100](), [libs/core/langchain_core/runnables/config.py:1-50](), [libs/core/langchain_core/runnables/passthrough.py:1-50](), [libs/core/langchain_core/runnables/branch.py:1-40](), [libs/core/langchain_core/runnables/fallbacks.py:1-35](), [libs/core/langchain_core/runnables/history.py:1-40](), [libs/core/langchain_core/runnables/configurable.py:1-48](), [libs/core/langchain_core/runnables/utils.py:1-50](), [libs/core/langchain_core/runnables/schema.py:1-120](), [libs/core/langchain_core/tracers/log_stream.py:1-40](), [libs/core/langchain_core/tracers/event_stream.py:1-56]()