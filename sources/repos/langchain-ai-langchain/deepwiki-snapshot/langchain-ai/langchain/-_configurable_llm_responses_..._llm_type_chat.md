```

Sources: [libs/core/tests/unit_tests/runnables/test_runnable.py:742-869]()

### Integration with RunnableWithMessageHistory

Configuration plays a crucial role in session management for conversational applications:

```python
chain_with_history = RunnableWithMessageHistory(
    runnable=chain,
    get_session_history=get_session_history_func,
    input_messages_key="question",
    history_messages_key="history",
    history_factory_config=[
        ConfigurableFieldSpec(
            id="session_id",
            annotation=str,
            name="Session ID",
            is_shared=True
        ),
        ConfigurableFieldSpec(
            id="user_id",
            annotation=str,
            name="User ID",
            is_shared=True
        )
    ]
)

# Invoke with session configuration
chain_with_history.invoke(
    {"question": "Hello"},
    config={"configurable": {"session_id": "123", "user_id": "user-1"}}
)
```

The `history_factory_config` specifies which configurable fields should be passed to the session history factory function.

Sources: [libs/core/langchain_core/runnables/history.py:169-222](), [libs/core/tests/unit_tests/runnables/test_history.py:169-196]()