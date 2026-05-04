def route_tools_output(state: AgentState) -> str:
    if jump_to := state.get("jump_to"):
        return jump_to
    
    # Check if any tool has return_direct=True
    if should_return_direct(state):
        return "__end__"
    
    return "model"  # Loop back to model
```

| Routing Point | Condition | Destination | Priority |
|---------------|-----------|-------------|----------|
| After model | `state["jump_to"]` set | Value of `jump_to` | Highest |
| After model | `AIMessage.tool_calls` present | `"tools"` node | Medium |
| After model | No tool calls | `"__end__"` | Lowest |
| After tools | `state["jump_to"]` set | Value of `jump_to` | Highest |
| After tools | `return_direct=True` on any tool | `"__end__"` | Medium |
| After tools | Default | `"model"` (loop) | Lowest |

**Sources:** [libs/langchain_v1/langchain/agents/factory.py:1151-1200](), [libs/langchain_v1/langchain/agents/factory.py:1202-1246]()

### Control Flow with jump_to

Middleware can override default routing via `jump_to`:

| Jump Destination | Effect |
|-----------------|--------|
| `"model"` | Return to model node (retry model call) |
| `"tools"` | Force tool execution even without tool_calls |
| `"end"` | Skip remaining execution and return |

Example: Early exit based on condition:

```python
@after_model(can_jump_to=["end"])
def early_exit(state: AgentState, runtime: Runtime) -> dict | None:
    if should_stop(state):
        return {"jump_to": "end"}
    return None
```

**Sources:** [libs/langchain_v1/langchain/agents/middleware/types.py:67-68](), [libs/langchain_v1/langchain/agents/factory.py:329-361]()

## Example: Complete Middleware Implementation

### Context Editing Middleware

This middleware demonstrates `wrap_model_call` usage:

```python
class ContextEditingMiddleware(AgentMiddleware):
    """Prune tool results to manage context size."""
    
    edits: list[ContextEdit]
    token_count_method: Literal["approximate", "model"]
    
    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelCallResult:
        """Apply context edits before invoking model."""
        if not request.messages:
            return handler(request)
        
        # Define token counter
        if self.token_count_method == "approximate":
            count_tokens = count_tokens_approximately
        else:
            system_msg = [request.system_message] if request.system_message else []
            def count_tokens(messages):
                return request.model.get_num_tokens_from_messages(
                    system_msg + list(messages), request.tools
                )
        
        # Apply edits to copy of messages
        edited_messages = deepcopy(list(request.messages))
        for edit in self.edits:
            edit.apply(edited_messages, count_tokens=count_tokens)
        
        return handler(request.override(messages=edited_messages))
```

**Sources:** [libs/langchain_v1/langchain/agents/middleware/context_editing.py:185-244]()

### Human-in-the-Loop Middleware

Demonstrates `after_model` hook with interrupt:

```python
class HumanInTheLoopMiddleware(AgentMiddleware):
    """Request human approval for specific tool calls."""
    
    interrupt_on: dict[str, InterruptOnConfig]
    
    def after_model(self, state: AgentState, runtime: Runtime) -> dict | None:
        """Trigger interrupts for configured tools."""
        last_ai_msg = state["messages"][-1]
        if not isinstance(last_ai_msg, AIMessage) or not last_ai_msg.tool_calls:
            return None
        
        # Build interrupt requests
        action_requests = []
        review_configs = []
        for tool_call in last_ai_msg.tool_calls:
            if config := self.interrupt_on.get(tool_call["name"]):
                action_request, review_config = self._create_action_and_config(
                    tool_call, config, state, runtime
                )
                action_requests.append(action_request)
                review_configs.append(review_config)
        
        if not action_requests:
            return None
        
        # Send interrupt and get decisions
        decisions = interrupt(
            HITLRequest(
                action_requests=action_requests,
                review_configs=review_configs
            )
        )["decisions"]
        
        # Process decisions and update tool calls
        revised_tool_calls = self._process_decisions(decisions, last_ai_msg.tool_calls)
        last_ai_msg.tool_calls = revised_tool_calls
        
        return {"messages": [last_ai_msg, *artificial_tool_messages]}
```

**Sources:** [libs/langchain_v1/langchain/agents/middleware/human_in_the_loop.py:159-358]()

## State Schema Resolution

Middleware can extend `AgentState` with custom fields:

```python
class TodoState(AgentState):
    """Extended state with todos field."""
    todos: Annotated[NotRequired[list[Todo]], OmitFromInput]

class TodoListMiddleware(AgentMiddleware):
    state_schema = TodoState  # Declares state extension
```

The factory merges all middleware state schemas:

```python
def _resolve_schema(schemas: set[type], schema_name: str, omit_flag: str | None) -> type:
    """Merge schemas and respect OmitFromSchema annotations."""
    all_annotations = {}
    for schema in schemas:
        hints = get_type_hints(schema, include_extras=True)
        for field_name, field_type in hints.items():
            # Check OmitFromSchema metadata
            if should_omit_field(field_type, omit_flag):
                continue
            all_annotations[field_name] = field_type
    
    return TypedDict(schema_name, all_annotations)
```

| Schema Type | Purpose |
|-------------|---------|
| `resolved_state_schema` | Internal state (all fields) |
| `input_schema` | External input (respects `OmitFromInput`) |
| `output_schema` | External output (respects `OmitFromOutput`) |

**Sources:** [libs/langchain_v1/langchain/agents/factory.py:283-327](), [libs/langchain_v1/langchain/agents/factory.py:852-869](), [libs/langchain_v1/langchain/agents/middleware/types.py:283-301]()