

# AWS DevOps Agent events detail reference
<a name="integrating-devops-agent-into-event-driven-applications-using-amazon-eventbridge-devops-agent-events-detail-reference"></a>

Events from AWS services have common metadata fields, including `source`, `detail-type`, `account`, `region`, and `time`. These events also contain a `detail` field with data specific to the service. For AWS DevOps Agent events, the `source` is always `aws.aidevops` and the `detail-type` identifies the specific event.

## Investigation events
<a name="investigation-events"></a>

The following `detail-type` values identify investigation events:
+ `Investigation Created`
+ `Investigation Priority Updated`
+ `Investigation In Progress`
+ `Investigation Completed`
+ `Investigation Failed`
+ `Investigation Timed Out`
+ `Investigation Cancelled`
+ `Investigation Pending Triage`
+ `Investigation Linked`
+ `Investigation Skipped`

The `source` and `detail-type` fields are included below because they contain specific values for AWS DevOps Agent events. For definitions of the other metadata fields that are included in all events, see [Event structure](https://docs.aws.amazon.com/eventbridge/latest/ref/overiew-event-structure.html) in the *Amazon EventBridge Events Reference*.

The following is the JSON structure for investigation events.

```
{
  . . .,
  "detail-type" : "string",
  "source" : "aws.aidevops",
  . . .,
  "detail" : {
    "version" : "string",
    "metadata" : {
      "agent_space_id" : "string",
      "task_id" : "string",
      "execution_id" : "string"
    },
    "data" : {
      "task_type" : "string",
      "priority" : "string",
      "status" : "string",
      "created_at" : "string",
      "updated_at" : "string",
      "summary_record_id" : "string"
    }
  }
}
```

**`detail-type`** Identifies the type of event. For investigation events, this is one of the event names listed previously.

**`source`** Identifies the service that generated the event. For AWS DevOps Agent events, this value is `aws.aidevops`.

**`detail`** A JSON object that contains event-specific data. The `detail` object includes the following fields:
+ `version` (string) – The schema version of the event detail. Currently `1.0.0`.
+ `metadata.agent_space_id` (string) – The unique identifier of the agent space where the event originated.
+ `metadata.task_id` (string) – The unique identifier of the task.
+ `metadata.execution_id` (string) – The unique identifier of the execution run. Present when an execution has been assigned to the investigation.
+ `data.task_type` (string) – The type of task. Value: `INVESTIGATION`.
+ `data.priority` (string) – The priority level. Values: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `MINIMAL`.
+ `data.status` (string) – The current status. Values: `PENDING_START`, `IN_PROGRESS`, `COMPLETED`, `FAILED`, `TIMED_OUT`, `CANCELLED`, `PENDING_TRIAGE`, `LINKED`, `SKIPPED`.
+ `data.created_at` (string) – ISO 8601 timestamp when the task was created.
+ `data.updated_at` (string) – ISO 8601 timestamp when the task was last updated.
+ `data.summary_record_id` (string) – The identifier of the summary record containing investigation findings. Included when a summary is generated for the completed investigation. You can retrieve the summary content through the AWS DevOps Agent API by using this identifier to look up the journal record with a record type of `investigation_summary_md`.

**Example: Investigation Completed event**

```
{
  "version": "0",
  "id": "12345678-1234-1234-1234-123456789015",
  "detail-type": "Investigation Completed",
  "source": "aws.aidevops",
  "account": "123456789012",
  "time": "2026-03-12T18:10:00Z",
  "region": "us-east-1",
  "resources": [
    "arn:aws:aidevops:us-east-1:123456789012:agentspace/8f6187a7-0388-4926-8217-3a0fe32f757c"
  ],
  "detail": {
    "version": "1.0.0",
    "metadata": {
      "agent_space_id": "8f6187a7-0388-4926-8217-3a0fe32f757c",
      "task_id": "a1b2c3d4-5678-90ab-cdef-example11111",
      "execution_id": "b2c3d4e5-6789-01ab-cdef-example22222"
    },
    "data": {
      "task_type": "INVESTIGATION",
      "priority": "CRITICAL",
      "status": "COMPLETED",
      "created_at": "2026-03-12T18:00:00Z",
      "updated_at": "2026-03-12T18:10:00Z",
      "summary_record_id": "d4e5f6g7-6789-01ab-cdef-example44444"
    }
  }
}
```

**Example: Investigation Failed event**

```
{
  "version": "0",
  "id": "12345678-1234-1234-1234-123456789016",
  "detail-type": "Investigation Failed",
  "source": "aws.aidevops",
  "account": "123456789012",
  "time": "2026-03-12T18:10:00Z",
  "region": "us-east-1",
  "resources": [
    "arn:aws:aidevops:us-east-1:123456789012:agentspace/8f6187a7-0388-4926-8217-3a0fe32f757c"
  ],
  "detail": {
    "version": "1.0.0",
    "metadata": {
      "agent_space_id": "8f6187a7-0388-4926-8217-3a0fe32f757c",
      "task_id": "a1b2c3d4-5678-90ab-cdef-example11111",
      "execution_id": "b2c3d4e5-6789-01ab-cdef-example22222"
    },
    "data": {
      "task_type": "INVESTIGATION",
      "priority": "CRITICAL",
      "status": "FAILED",
      "created_at": "2026-03-12T18:00:00Z",
      "updated_at": "2026-03-12T18:10:00Z"
    }
  }
}
```

## Mitigation events
<a name="mitigation-events"></a>

The following `detail-type` values identify mitigation events:
+ `Mitigation In Progress`
+ `Mitigation Completed`
+ `Mitigation Failed`
+ `Mitigation Timed Out`
+ `Mitigation Cancelled`

The `source` and `detail-type` fields are included below because they contain specific values for AWS DevOps Agent events. For definitions of the other metadata fields that are included in all events, see [Event structure](https://docs.aws.amazon.com/eventbridge/latest/ref/overiew-event-structure.html) in the *Amazon EventBridge Events Reference*.

The following is the JSON structure for mitigation events.

```
{
  . . .,
  "detail-type" : "string",
  "source" : "aws.aidevops",
  . . .,
  "detail" : {
    "version" : "string",
    "metadata" : {
      "agent_space_id" : "string",
      "task_id" : "string",
      "execution_id" : "string"
    },
    "data" : {
      "task_type" : "string",
      "priority" : "string",
      "status" : "string",
      "created_at" : "string",
      "updated_at" : "string",
      "summary_record_id" : "string"
    }
  }
}
```

**`detail-type`** Identifies the type of event. For mitigation events, this is one of the event names listed previously.

**`source`** Identifies the service that generated the event. For AWS DevOps Agent events, this value is `aws.aidevops`.

**`detail`** A JSON object that contains event-specific data. The `detail` object includes the following fields:
+ `version` (string) – The schema version of the event detail. Currently `1.0.0`.
+ `metadata.agent_space_id` (string) – The unique identifier of the agent space where the event originated.
+ `metadata.task_id` (string) – The unique identifier of the task.
+ `metadata.execution_id` (string) – The unique identifier of the execution run. Present when an execution has been assigned to the mitigation.
+ `data.task_type` (string) – The type of task. Value: `INVESTIGATION`.
+ `data.priority` (string) – The priority level. Values: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `MINIMAL`.
+ `data.status` (string) – The current status. Values: `IN_PROGRESS`, `COMPLETED`, `FAILED`, `TIMED_OUT`, `CANCELLED`.
+ `data.created_at` (string) – ISO 8601 timestamp when the task was created.
+ `data.updated_at` (string) – ISO 8601 timestamp when the task was last updated.
+ `data.summary_record_id` (string) – The identifier of the summary record containing mitigation findings. Included when a summary is generated for the completed mitigation. You can retrieve the summary content through the AWS DevOps Agent API by using this identifier to look up the journal record with a record type of `mitigation_summary_md`.

**Example: Mitigation Completed event**

```
{
  "version": "0",
  "id": "12345678-1234-1234-1234-12345678901c",
  "detail-type": "Mitigation Completed",
  "source": "aws.aidevops",
  "account": "123456789012",
  "time": "2026-03-12T18:20:00Z",
  "region": "us-east-1",
  "resources": [
    "arn:aws:aidevops:us-east-1:123456789012:agentspace/8f6187a7-0388-4926-8217-3a0fe32f757c"
  ],
  "detail": {
    "version": "1.0.0",
    "metadata": {
      "agent_space_id": "8f6187a7-0388-4926-8217-3a0fe32f757c",
      "task_id": "a1b2c3d4-5678-90ab-cdef-example11111",
      "execution_id": "c3d4e5f6-7890-12ab-cdef-example33333"
    },
    "data": {
      "task_type": "INVESTIGATION",
      "priority": "CRITICAL",
      "status": "COMPLETED",
      "created_at": "2026-03-12T18:00:00Z",
      "updated_at": "2026-03-12T18:20:00Z",
      "summary_record_id": "e5f6g7h8-7890-12ab-cdef-example55555"
    }
  }
}
```

**Example: Mitigation Failed event**

```
{
  "version": "0",
  "id": "12345678-1234-1234-1234-12345678901d",
  "detail-type": "Mitigation Failed",
  "source": "aws.aidevops",
  "account": "123456789012",
  "time": "2026-03-12T18:20:00Z",
  "region": "us-east-1",
  "resources": [
    "arn:aws:aidevops:us-east-1:123456789012:agentspace/8f6187a7-0388-4926-8217-3a0fe32f757c"
  ],
  "detail": {
    "version": "1.0.0",
    "metadata": {
      "agent_space_id": "8f6187a7-0388-4926-8217-3a0fe32f757c",
      "task_id": "a1b2c3d4-5678-90ab-cdef-example11111",
      "execution_id": "c3d4e5f6-7890-12ab-cdef-example33333"
    },
    "data": {
      "task_type": "INVESTIGATION",
      "priority": "CRITICAL",
      "status": "FAILED",
      "created_at": "2026-03-12T18:00:00Z",
      "updated_at": "2026-03-12T18:20:00Z"
    }
  }
}
```