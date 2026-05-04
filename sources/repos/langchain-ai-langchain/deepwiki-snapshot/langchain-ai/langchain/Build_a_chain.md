prompt = PromptTemplate.from_template("Hello, {name}!")
chain = prompt | model | StrOutputParser()