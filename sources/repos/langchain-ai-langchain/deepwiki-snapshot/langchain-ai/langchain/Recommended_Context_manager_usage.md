with FileCallbackHandler("output.txt") as handler:
    chain.invoke(input, config={"callbacks": [handler]})