agent = create_agent(
    model="openai:gpt-4o",
    checkpointer=PostgresSaver.from_conn_string("postgresql://...")
)