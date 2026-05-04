predict.load_state(state)
```

**Security note:** By default, `load_state()` blocks potentially unsafe LM configuration keys (`api_base`, `base_url`, `model_list`) defined in `UNSAFE_LM_STATE_KEYS` to prevent loading from untrusted files. Use `allow_unsafe_lm_state=True` only for trusted sources [dspy/predict/predict.py:22-40]().

**Sources:** [dspy/predict/predict.py:71-116](), [tests/predict/test_predict.py:43-68]()

### Demonstrations and Few-Shot Learning

Modules store few-shot examples in the `demos` attribute, which are automatically included in prompts by adapters [dspy/predict/predict.py:69]().

```python
predict.demos = [
    dspy.Example(question="What is 2+2?", answer="4").with_inputs("question"),
]
```

**Sources:** [dspy/predict/predict.py:69](), [tests/predict/test_predict.py:87-115]()

## Specialized Modules

Beyond basic `Predict`, DSPy provides specialized modules for common patterns.

### Reasoning Modules
For step-by-step reasoning, see [Reasoning Strategies](#3.2):
- `ChainOfThought`: Adds a `reasoning` field for intermediate steps [dspy/predict/chain_of_thought.py:12-35]()
- `ProgramOfThought`: Generates and executes code to produce answers.
- `ReAct`: Agent-based reasoning with tools.

### Tool Integration
For external tool use, see [Tool Integration & Function Calling](#3.3).

### Custom Types
For specialized data formats (Images, Audio, etc.), see [Custom Types & Multimodal Support](#3.4).

### Conversation History
For maintaining context across turns, see [History & Conversation Management](#3.6).

### Composition Modules
For module orchestration, see [Module Composition & Refinement](#3.5).

## Next Steps

For deeper understanding of specific topics:

- **[Predict Module](#3.1)**: Detailed API reference for `Predict` class
- **[Reasoning Strategies](#3.2)**: Chain-of-thought, ReAct, and other reasoning patterns
- **[Tool Integration & Function Calling](#3.3)**: Function calling and external tool use
- **[Custom Types & Multimodal Support](#3.4)**: Multimodal and specialized data types
- **[Module Composition & Refinement](#3.5)**: Advanced composition patterns and refinement
- **[History & Conversation Management](#3.6)**: Conversation state and context management
- **[Program Optimization](#4)**: Using optimizers to improve program performance