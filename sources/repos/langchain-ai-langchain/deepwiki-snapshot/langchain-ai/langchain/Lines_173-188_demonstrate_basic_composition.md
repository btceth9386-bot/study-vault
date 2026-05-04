chain = RunnableLambda(lambda x: x + 1) | RunnableLambda(lambda x: x * 2)
chain.invoke(1)  # Returns 4