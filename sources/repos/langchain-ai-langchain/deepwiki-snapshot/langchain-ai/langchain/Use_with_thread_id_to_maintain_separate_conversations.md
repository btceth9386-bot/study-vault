thread_config = {"configurable": {"thread_id": "conversation-123"}}

agent.invoke({"messages": [{"role": "user", "content": "My name is Alice"}]}, config=thread_config)
agent.invoke({"messages": [{"role": "user", "content": "What's my name?"}]}, config=thread_config)