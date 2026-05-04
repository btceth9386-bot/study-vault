model = ChatOpenAI(model="gpt-4o-mini")
for chunk in model.stream("Hello"):
    if chunk.usage_metadata:
        # Last chunk contains cumulative usage
        print(f"Total tokens: {chunk.usage_metadata['total_tokens']}")