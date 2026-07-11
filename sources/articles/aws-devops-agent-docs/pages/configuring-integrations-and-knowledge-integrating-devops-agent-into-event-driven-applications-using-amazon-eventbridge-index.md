

# Integrating AWS DevOps Agent with Amazon EventBridge
<a name="configuring-integrations-and-knowledge-integrating-devops-agent-into-event-driven-applications-using-amazon-eventbridge-index"></a>

You can integrate AWS DevOps Agent with your event-driven applications by using events that occur during investigation and mitigation lifecycles. AWS DevOps Agent sends events to Amazon EventBridge when the state of an investigation or mitigation changes. You can then create EventBridge rules that take action based on these events.

For example, you can create rules that perform the following actions:
+ Invoke an AWS Lambda function to process investigation results when an investigation completes.
+ Send an Amazon SNS notification when an investigation fails or times out.
+ Update a ticketing system when a new investigation is created.
+ Start an AWS Step Functions workflow when a mitigation action completes.

## How EventBridge routes AWS DevOps Agent events
<a name="how-eventbridge-routes-aws-devops-agent-events"></a>

AWS DevOps Agent sends events to the EventBridge default event bus. EventBridge then evaluates the events against the rules that you create. When an event matches a rule's event pattern, EventBridge sends the event to the specified targets.

The following diagram shows how EventBridge routes AWS DevOps Agent events.

![Amazon EventBridge routing events from AWS source through rules to targets such as AWS services.](http://docs.aws.amazon.com/devopsagent/latest/userguide/images/eventbridge-integration-how-it-works.png)


1. AWS DevOps Agent sends an event to the EventBridge default event bus when an investigation or mitigation lifecycle state changes.

1. EventBridge evaluates the event against the rules that you created.

1. If the event matches a rule's event pattern, EventBridge sends the event to the targets specified in the rule.

## AWS DevOps Agent events
<a name="aws-devops-agent-events"></a>

AWS DevOps Agent sends the following events to EventBridge. All events use the source `aws.aidevops`.

### Supported investigation events
<a name="supported-investigation-events"></a>


| detail-type | Description | 
| --- | --- | 
| Investigation Created | An investigation was created in the agent space. | 
| Investigation Priority Updated | The priority of an investigation was changed. | 
| Investigation In Progress | An investigation started active analysis. | 
| Investigation Completed | An investigation finished successfully with findings. | 
| Investigation Failed | An investigation encountered an error and could not complete. | 
| Investigation Timed Out | An investigation exceeded the maximum allowed duration. | 
| Investigation Cancelled | An investigation was canceled before completion. | 
| Investigation Pending Triage | An investigation is awaiting triage before active analysis begins. | 
| Investigation Linked | An investigation was linked to a related incident or ticket. | 
| Investigation Skipped | An investigation was skipped because it matched skip criteria defined in a skill. | 

### Supported mitigation events
<a name="supported-mitigation-events"></a>


| detail-type | Description | 
| --- | --- | 
| Mitigation In Progress | A mitigation action started. | 
| Mitigation Completed | A mitigation action finished successfully. | 
| Mitigation Failed | A mitigation action encountered an error and could not complete. | 
| Mitigation Timed Out | A mitigation action exceeded the maximum allowed duration. | 
| Mitigation Cancelled | A mitigation action was canceled before completion. | 

For detailed field descriptions and example events, see [AWS DevOps Agent events detail reference](integrating-devops-agent-into-event-driven-applications-using-amazon-eventbridge-devops-agent-events-detail-reference.md).

## Creating event patterns that match AWS DevOps Agent events
<a name="creating-event-patterns-that-match-aws-devops-agent-events"></a>

EventBridge rules use event patterns to select events and route them to targets. An event pattern matches the structure of the events that it handles. You create event patterns to filter AWS DevOps Agent events based on the event fields.

The following examples show event patterns for common use cases.

**Match all AWS DevOps Agent events**

The following event pattern matches all events from AWS DevOps Agent.

```
{
  "source": ["aws.aidevops"]
}
```

**Match only investigation events**

The following event pattern uses a prefix match to select only investigation lifecycle events.

```
{
  "source": ["aws.aidevops"],
  "detail-type": [{"prefix": "Investigation"}]
}
```

**Match only completion and failure events**

The following event pattern matches events for completed or failed investigations and mitigations.

```
{
  "source": ["aws.aidevops"],
  "detail-type": [
    "Investigation Completed",
    "Investigation Failed",
    "Mitigation Completed",
    "Mitigation Failed"
  ]
}
```

**Match events for a specific agent space**

The following event pattern matches events from a specific agent space.

```
{
  "source": ["aws.aidevops"],
  "detail": {
    "metadata": {
      "agent_space_id": ["your-agent-space-id"]
    }
  }
}
```

For more information about event patterns, see [Amazon EventBridge event patterns](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-event-patterns.html) in the *Amazon EventBridge User Guide*.

## Amazon EventBridge permissions
<a name="amazon-eventbridge-permissions"></a>

AWS DevOps Agent doesn't require additional permissions to deliver events to EventBridge. The events are sent to the default event bus automatically.

Depending on the targets that you configure for your EventBridge rules, you might need to add specific permissions. For more information about the permissions required for targets, see [Using resource-based policies for Amazon EventBridge](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-use-resource-based.html) in the *Amazon EventBridge User Guide*.

## Additional EventBridge resources
<a name="additional-eventbridge-resources"></a>

For more information about EventBridge concepts and configuration, see the following topics in the *Amazon EventBridge User Guide*:
+ [EventBridge event buses](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-event-bus.html)
+ [EventBridge events](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-events.html)
+ [EventBridge event patterns](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-event-patterns.html)
+ [EventBridge rules](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-rules.html)
+ [EventBridge targets](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-targets.html)