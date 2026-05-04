@pytest.mark.compile
def test_placeholder() -> None:
    """Placeholder test to verify integration tests compile."""
    pass
```

**Sources**: [.github/workflows/_compile_integration_test.yml:9-53](), [libs/standard-tests/pyproject.toml:106-112]()

## VCR Testing for Deterministic HTTP Tests

The `langchain-tests` package provides VCR (Video Cassette Recorder) support via the `base_vcr_config()` fixture ([libs/standard-tests/langchain_tests/conftest.py:56-88]()) for recording HTTP interactions to cassette files, enabling deterministic tests without live API calls.

### VCR Configuration

Title: VCR Cassette Recording and Replay Flow

```mermaid
graph TB
    subgraph "Test Class Configuration"
        ENABLE["ChatModelIntegrationTests.enable_vcr_tests<br/>property returns True"]
        CONFTEST["tests/conftest.py:<br/>@pytest.fixture(scope='session')<br/>def vcr_config()"]
    end
    
    subgraph "base_vcr_config() from langchain_tests.conftest"
        BASE_CFG["config = {<br/>'record_mode': 'once',<br/>'match_on': ['method', 'uri', 'body'],<br/>'filter_headers': [...]<br/>}"]
        FILTER_HDR["filter_headers = [<br/>('authorization', 'PLACEHOLDER'),<br/>('x-api-key', 'PLACEHOLDER'),<br/>('api-key', 'PLACEHOLDER')]"]
    end
    
    subgraph "CustomSerializer and CustomPersister"
        SERIALIZER["CustomSerializer.serialize():<br/>cassette_dict['requests'] = [...]<br/>yml = yaml.safe_dump(cassette_dict)<br/>return gzip.compress(yml.encode())"]
        PERSISTER["CustomPersister.save_cassette():<br/>path.parent.mkdir(parents=True)<br/>path.write_bytes(data)"]
    end
    
    subgraph "Test Execution"
        FIRST["First run (no cassette):<br/>HTTP request to live API<br/>VCR records request/response"]
        SAVE["CustomSerializer.serialize()<br/>CustomPersister.save_cassette()<br/>→ tests/cassettes/TestClass_test.yaml.gz"]
        REPLAY["Subsequent runs:<br/>CustomPersister.load_cassette()<br/>CustomSerializer.deserialize()<br/>Mock responses from cassette"]
    end
    
    ENABLE --> CONFTEST
    CONFTEST --> BASE_CFG
    BASE_CFG --> FILTER_HDR
    FILTER_HDR --> SERIALIZER
    SERIALIZER --> PERSISTER
    
    PERSISTER --> FIRST
    FIRST --> SAVE
    SAVE --> REPLAY
```

**Sources**: [libs/standard-tests/langchain_tests/conftest.py:20-88](), [libs/standard-tests/langchain_tests/integration_tests/chat_models.py:222-229](), [libs/standard-tests/langchain_tests/integration_tests/chat_models.py:594-738]()

### Custom Serializer Implementation

The `CustomSerializer` class ([libs/standard-tests/langchain_tests/conftest.py:20-53]()) uses `yaml.safe_load` instead of `yaml.load` to prevent arbitrary code execution, and applies gzip compression:

```python