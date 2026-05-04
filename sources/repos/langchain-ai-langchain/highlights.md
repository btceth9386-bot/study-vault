# Highlights

- `deepwiki-snapshot/langchain-ai/langchain/Messages_and_Content_Handling.md — Section: Message Class Hierarchy` `BaseMessage` is the serializable root for `HumanMessage`, `AIMessage`, `ToolMessage`, system messages, and streaming chunk variants.
- `deepwiki-snapshot/langchain-ai/langchain/Messages_and_Content_Handling.md — Section: BaseMessage` A message carries `content`, `type`, provider-specific `additional_kwargs`, response metadata, optional `name`, and optional `id`.
- `deepwiki-snapshot/langchain-ai/langchain/Messages_and_Content_Handling.md — Section: AIMessage` Chat model output is an `AIMessage` with parsed `tool_calls`, `invalid_tool_calls`, and usage metadata.
- `deepwiki-snapshot/langchain-ai/langchain/Messages_and_Content_Handling.md — Section: ToolMessage` Tool results carry a required `tool_call_id`, which links execution output back to the model's requested tool call.
- `deepwiki-snapshot/langchain-ai/langchain/Messages_and_Content_Handling.md — Section: Content Blocks` `content_blocks` normalizes raw content into typed blocks such as text, reasoning, image, audio, tool call, and server tool result.
- `deepwiki-snapshot/langchain-ai/langchain/OpenAI_and_Anthropic_Integrations.md — Section: Package Architecture` `langchain-openai` and `langchain-anthropic` ship separate provider packages that implement `langchain-core` chat model abstractions.
- `deepwiki-snapshot/langchain-ai/langchain/OpenAI_and_Anthropic_Integrations.md — Section: Message Format Conversion` Provider wrappers convert between LangChain messages and OpenAI/Anthropic wire formats while returning common message classes.
- `deepwiki-snapshot/langchain-ai/langchain/Tools_and_Function_Calling.md — Section: The @tool Decorator` `@tool` converts Python callables or Runnables into `BaseTool` instances with inferred or explicit schemas.
- `deepwiki-snapshot/langchain-ai/langchain/Tools_and_Function_Calling.md — Section: Function Calling Conversion Utilities` Tool conversion utilities turn `BaseTool`, callables, Pydantic models, TypedDicts, or schema dicts into provider-compatible function/tool definitions.
- `deepwiki-snapshot/langchain-ai/langchain/OpenAI_and_Anthropic_Integrations.md — Section: Using as a Retriever` `VectorStore.as_retriever()` wraps a vector store in a `VectorStoreRetriever` compatible with the retriever interface.
