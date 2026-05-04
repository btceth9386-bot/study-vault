agent = create_agent(
    model="openai:gpt-4o",
    checkpointer=MemorySaver()
)