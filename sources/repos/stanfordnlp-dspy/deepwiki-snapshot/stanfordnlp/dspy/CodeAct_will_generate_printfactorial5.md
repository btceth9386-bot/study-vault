res = act(n=5) 
```
[dspy/predict/code_act.py:31-37]()

### Manual Tool Handling
For granular control, tools can be defined as `InputField` types in a signature:
```python
class ManualToolSig(dspy.Signature):
    question: str = dspy.InputField()
    tools: list[dspy.Tool] = dspy.InputField()
    outputs: dspy.ToolCalls = dspy.OutputField()
```
[docs/docs/learn/programming/tools.md:77-81]()

Sources: [dspy/predict/react.py:30-38](), [dspy/predict/code_act.py:28-38](), [docs/docs/learn/programming/tools.md:74-118]()