full_message = None
for chunk in model.stream("Hello"):
    full_message = chunk if full_message is None else full_message + chunk