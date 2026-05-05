cron = await client.crons.create(
    assistant_id="asst_123",
    schedule="0 12 * * *",
    input={"query": "Daily summary"},
    end_time=datetime(2025, 1, 1, tzinfo=timezone.utc),
    timezone="America/Los_Angeles"
)
```
**Sources**: [libs/sdk-py/tests/test_crons_client.py:100-128](), [libs/sdk-py/tests/test_crons_client.py:131-161]()

#### Create Cron for Thread
Creates a cron job specifically for a thread (stateful).
```python
# Sync
cron = client.crons.create_for_thread(
    thread_id="thread_123",
    assistant_id="asst_123",
    schedule="0 0 * * *",
    multitask_strategy="enqueue"
)
```
**Sources**: [libs/sdk-py/tests/test_crons_client.py:163-190](), [libs/sdk-py/tests/test_crons_client.py:34-62]()

#### Search and List
Filter and sort existing cron jobs.
- **`order_by`**: Field to sort by (e.g., `"next_run_date"`, `"created_at"`).
- **`order`**: `"asc"` or `"desc"`.

**Sources**: [libs/sdk-py/langgraph_sdk/schema.py:166-182](), [libs/sdk-py/langgraph_sdk/schema.py:489-504]()

---

## Payload and Execution Control

The `payload` of a cron job contains the execution parameters used for every triggered run.

- **`input`**: The initial state or message for the graph.
- **`config`**: `recursion_limit`, `tags`, and `configurable` parameters. [libs/sdk-py/langgraph_sdk/schema.py:185-206]()
- **`context`**: Static context to add to the assistant (Added in version 0.6.0). [libs/sdk-py/langgraph_sdk/_async/cron.py:93-94]()
- **`durability`**: Level for the run (`'sync'`, `'async'`, or `'exit'`), replacing the deprecated `checkpoint_during`. [libs/sdk-py/langgraph_sdk/_async/cron.py:109-113]()
- **`multitask_strategy`**: Defines how to handle multiple tasks (`'reject'`, `'interrupt'`, `'rollback'`, or `'enqueue'`). [libs/sdk-py/langgraph_sdk/schema.py:81-88]()

The `end_time` parameter ensures that the cron job automatically stops triggering after a certain date.

**Sources**: [libs/sdk-py/langgraph_sdk/schema.py:185-206](), [libs/sdk-py/tests/test_crons_client.py:66-96](), [libs/sdk-py/langgraph_sdk/_async/cron.py:138-143]()