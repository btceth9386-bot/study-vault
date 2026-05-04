```

### get_config_jsonschema Method

The `get_config_jsonschema` method produces a JSON Schema representation for API documentation and validation:

```python
json_schema = runnable.get_config_jsonschema(include=["tags", "metadata"])
# Returns: {"properties": {"tags": {...}, "metadata": {...}}, ...}
```

Sources: [libs/core/langchain_core/runnables/base.py:520-582](), [libs/core/langchain_core/runnables/utils.py:448-620]()

## Configuration in Practice

### Combining Multiple Configuration Techniques

Configuration techniques can be combined for sophisticated runtime control:

```python
from langchain_core.runnables import RunnableLambda, ConfigurableField