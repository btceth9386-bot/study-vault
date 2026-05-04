The LangChain repository employs a comprehensive testing infrastructure that ensures consistency, quality, and compatibility across its modular package ecosystem. This infrastructure consists of three main components: (1) a standardized testing framework in the `langchain-tests` package that defines interface compliance tests for integrations, (2) an intelligent CI/CD pipeline that selectively runs tests based on changed files, and (3) multi-dimensional testing strategies that verify compatibility across Python versions, Pydantic versions, and dependency ranges.

This page documents the testing architecture, test execution workflows, and quality gates. For information about the release process that follows successful testing, see [Release Process and Workflows](#6.3).

## Standard Testing Framework

The `langchain-standard-tests` package ([libs/standard-tests/pyproject.toml:6]()) provides abstract base test classes in the `langchain_tests` module that integration packages inherit to verify compliance with LangChain's core abstractions. This ensures all implementations of `BaseChatModel`, `BaseTool`, `VectorStore`, and other abstractions expose consistent interfaces.

### Test Class Hierarchy

Title: Standard Test Class Inheritance Structure

```mermaid
graph TB
    subgraph "langchain_tests.base"
        BASE["BaseStandardTests<br/>test_no_overrides_DO_NOT_OVERRIDE()"]
    end
    
    subgraph "langchain_tests.unit_tests"
        CHAT_UNIT["ChatModelUnitTests<br/>chat_model_class property<br/>test_init()<br/>test_serialize()"]
        TOOL_UNIT["ToolsUnitTests<br/>tool_constructor property<br/>test_has_name()<br/>test_has_input_schema()"]
        EMB_UNIT["EmbeddingsUnitTests<br/>embeddings_class property<br/>test_init()<br/>test_embed_documents()"]
    end
    
    subgraph "langchain_tests.integration_tests"
        CHAT_INT["ChatModelIntegrationTests<br/>test_invoke()<br/>test_stream()<br/>test_invoke_with_tool_calling()<br/>test_structured_output()"]
        TOOL_INT["ToolsIntegrationTests<br/>test_invoke_matches_output_schema()<br/>test_async_invoke_matches_output_schema()"]
        VEC_INT["VectorStoreIntegrationTests<br/>vectorstore fixture<br/>test_add_documents()<br/>test_similarity_search()"]
        RET_INT["RetrieversIntegrationTests<br/>retriever_constructor property<br/>test_k_constructor_param()<br/>test_invoke_with_k_kwarg()"]
    end
    
    subgraph "Partner Package Tests"
        PKG_UNIT["TestChatOpenAIUnit<br/>TestChatAnthropicUnit<br/>TestChatMistralAIUnit"]
        PKG_INT["TestChatOpenAIIntegration<br/>TestChatAnthropicIntegration<br/>TestChatGroqIntegration"]
    end
    
    BASE --> CHAT_UNIT
    BASE --> TOOL_UNIT
    BASE --> EMB_UNIT
    
    CHAT_UNIT --> CHAT_INT
    TOOL_UNIT --> TOOL_INT
    
    CHAT_INT --> PKG_INT
    CHAT_UNIT --> PKG_UNIT
```

**Sources**: [libs/standard-tests/langchain_tests/base.py:1-63](), [libs/standard-tests/langchain_tests/unit_tests/chat_models.py:42-274](), [libs/standard-tests/langchain_tests/integration_tests/chat_models.py:173-739](), [libs/standard-tests/langchain_tests/unit_tests/tools.py:17-56](), [libs/standard-tests/langchain_tests/integration_tests/vectorstores.py:21-98](), [libs/standard-tests/langchain_tests/integration_tests/retrievers.py:13-144]()

### Test Override Protection

The `BaseStandardTests.test_no_overrides_DO_NOT_OVERRIDE` method ([libs/standard-tests/langchain_tests/base.py:7-62]()) prevents integration packages from silently overriding standard tests. If a test must be skipped, implementers must use `@pytest.mark.xfail(reason="...")`.

Title: Test Override Detection Algorithm

```mermaid
graph LR
    subgraph "BaseStandardTests"
        DISCOVER["test_no_overrides_DO_NOT_OVERRIDE()"]
    end
    
    subgraph "Validation Steps"
        FIND_BASE["explore_bases(cls)<br/>Find comparison_class<br/>from cls.__bases__"]
        GET_TESTS["dir(comparison_class)<br/>Filter test_* methods"]
        CHECK_DEL["base_tests - running_tests<br/>Detect deleted tests"]
        CHECK_OVER["getattr(self, test_name)<br/>== getattr(comparison_class, test_name)"]
        CHECK_XFAIL["hasattr(test_func, 'pytestmark')<br/>Check for xfail marker<br/>with reason kwarg"]
    end
    
    subgraph "Outcomes"
        PASS["✓ Pass validation"]
        FAIL_DEL["✗ ValueError:<br/>Standard tests deleted"]
        FAIL_OVER["✗ ValueError:<br/>Tests overridden<br/>without xfail"]
    end
    
    DISCOVER --> FIND_BASE
    FIND_BASE --> GET_TESTS
    GET_TESTS --> CHECK_DEL
    CHECK_DEL -->|"len(deleted_tests) > 0"| FAIL_DEL
    CHECK_DEL -->|"no deleted tests"| CHECK_OVER
    CHECK_OVER -->|"overridden_tests found"| CHECK_XFAIL
    CHECK_XFAIL -->|"has xfail + reason"| PASS
    CHECK_XFAIL -->|"missing xfail"| FAIL_OVER
    CHECK_OVER -->|"no overrides"| PASS
```

**Sources**: [libs/standard-tests/langchain_tests/base.py:7-62]()

### Configurable Test Properties

Integration test classes expose boolean properties that control which features are tested. For example, `ChatModelIntegrationTests` provides:

| Property | Default | Purpose |
|----------|---------|---------|
| `has_tool_calling` | Auto-detected | Whether `bind_tools` is implemented |
| `has_tool_choice` | Auto-detected | Whether `tool_choice` parameter is supported |
| `has_structured_output` | Auto-detected | Whether `with_structured_output` is implemented |
| `supports_json_mode` | `False` | Whether JSON mode is supported |
| `supports_image_inputs` | `False` | Whether image content blocks are supported |
| `supports_audio_inputs` | `False` | Whether audio content blocks are supported |
| `returns_usage_metadata` | `True` | Whether `usage_metadata` is populated |
| `enable_vcr_tests` | `False` | Whether to enable VCR cassette tests |

**Sources**: [libs/standard-tests/langchain_tests/unit_tests/chat_models.py:94-274](), [libs/standard-tests/langchain_tests/integration_tests/chat_models.py:226-739]()

### Example Test Implementation

The example below shows how partner packages implement the test base classes. The `ChatParrotLink` custom model ([libs/standard-tests/tests/unit_tests/custom_chat_model.py:18-149]()) demonstrates the pattern:

```python