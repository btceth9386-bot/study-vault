

# Vended Logs and Metrics
<a name="configuring-integrations-and-knowledge-vended-logs-and-metrics"></a>

You can monitor your agent spaces and service operations by using vended Amazon CloudWatch metrics and logs. This topic describes the CloudWatch metrics that the AWS DevOps Agent automatically publishes to your account and the vended logs that you can configure for delivery to your preferred destinations.

## Vended CloudWatch metrics
<a name="vended-cloudwatch-metrics"></a>

AWS DevOps Agent automatically publishes metrics to Amazon CloudWatch in your account. These metrics are available without any configuration. You can use them to monitor usage, track operational activity, and create alarms.

### Service-Linked Role
<a name="service-linked-role"></a>

To have Amazon CloudWatch metrics published in your account for this service, AWS DevOps Agent will automatically create the [service-linked role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create-service-linked-role.html) **AWSServiceRoleForAIDevOps** Service-Linked Role for you. If the IAM role invoking the API do not have appropriate permission the resource creation will fail with an InvalidParameterException.

**Important**  
Customers who created their AgentSpace before March 13, 2026 will need to manually create the **AWSServiceRoleForAIDevOps** Service Linked Role to have CloudWatch metrics for AWS DevOps Agent published in their account.

### Manually Create Service-Linked Role (For existing customers)
<a name="manually-create-service-linked-role-for-existing-customers"></a>

Do one of the following:
+ In the IAM console, create the **AWSServiceRoleForAIDevOps** role under the **AWS DevOps Agent** service.
+ From the AWS CLI, run the following command:

```
aws iam create-service-linked-role --aws-service-name aidevops.amazonaws.com
```

### Namespace
<a name="namespace"></a>

All metrics are published under the `AWS/AIDevOps` namespace.

### Dimensions
<a name="dimensions"></a>

All metrics include the following dimension.


| Dimension | Description | 
| --- | --- | 
| AgentSpaceUUID | The unique identifier of the agent space. To aggregate metrics across all agent spaces in your account, use CloudWatch math expressions or omit the dimension filter. | 

### Metrics reference
<a name="metrics-reference"></a>


| Metric name | Description | Unit | Publishing frequency | Useful statistics | 
| --- | --- | --- | --- | --- | 
| ConsumedChatRequests | The number of chat requests that an agent space consumed. To get the total count for your account, use the SUM statistic across all AgentSpaceUUID dimensions. | Count | Every 5 minutes | Sum, Average | 
| ConsumedInvestigationTime | The time spent running investigations in an agent space. | Seconds | Every 5 minutes | Sum, Average, Maximum | 
| ConsumedEvaluationTime | The time spent running evaluations in an agent space. | Seconds | Every 5 minutes | Sum, Average, Maximum | 
| TopologyCompletionCount | The number of topology processing completions. AWS DevOps Agent emits this metric when a topology finishes processing, whether from initial creation during onboarding, a manual update, or a scheduled daily refresh. | Count | Event-driven (emitted on each completion) | Sum, SampleCount | 

### Viewing metrics in the CloudWatch console
<a name="viewing-metrics-in-the-cloudwatch-console"></a>

1. Open the [CloudWatch console](https://console.aws.amazon.com/cloudwatch/).

1. In the navigation pane, choose **Metrics**, and then choose **All metrics**.

1. Choose the **AWS/AIDevOps** namespace.

1. Choose **By AgentSpace** to view metrics for your agent spaces.

**Note**  
** You can create CloudWatch alarms on these metrics to receive notifications when usage exceeds a threshold. For example, create an alarm on `ConsumedChatRequests` to monitor chat request consumption.

## Prerequisites
<a name="prerequisites"></a>

Before you configure log delivery, make sure that you have the following:
+ An active AWS account with access to the AWS DevOps Agent console
+ An IAM principal with permissions for CloudWatch Logs delivery APIs
+ (Optional) An Amazon S3 bucket or Amazon Data Firehose delivery stream, if you plan to use those as log destinations

## Vended logs
<a name="vended-logs"></a>

AWS DevOps Agent supports vended logs that provide visibility into events that your agent spaces and service registrations process. Vended logs use the Amazon CloudWatch Logs infrastructure to deliver logs to your preferred destination.

To use vended logs, you must configure a delivery destination. The following destinations are supported:
+ **Amazon CloudWatch Logs** – A log group in your account
+ **Amazon S3** – An S3 bucket in your account
+ **Amazon Data Firehose** – A Firehose delivery stream in your account

### Supported log types
<a name="supported-log-types"></a>

A single log type is supported: `APPLICATION_LOGS`. This log type covers all operational events that the service emits.

### Log event types
<a name="log-event-types"></a>

The following table summarizes the events that AWS DevOps Agent logs.


| Event | Description | Log level | 
| --- | --- | --- | 
| Agent inbound event received | An agent is triggered by an integrated source and receives an inbound event (for example, a PagerDuty incident event). | INFO | 
| Agent inbound event dropped | An inbound event was dropped before the agent processed it. The log includes the reason (for example, malformed data). | TBD | 
| Agent outbound communication failure | An outbound communication to a third-party integration failed. The log includes the task ID and destination identifier (for example, an authentication error). | TBD | 
| Third-party provider call failed | An outbound call to a connected third-party provider failed because the provider returned an error or a network error occurred. The log includes the HTTP status code and the service type. | ERROR | 
| Association credential access denied | Access was denied or authorization failed while retrieving the stored credentials for an association — for example, insufficient permissions, or an encryption key that is disabled or unavailable. The log records the public AWS error code in optional\_details. | ERROR | 
| Topology creation queued | A topology creation job was queued for processing. | INFO | 
| Topology creation started | A topology creation job began processing. | INFO | 
| Topology creation finished | A topology creation job completed processing. This event applies to initial creation, updates, and daily refreshes. | INFO | 
| Resource discovery failed | Resource discovery during topology creation encountered a failure. | ERROR | 
| Service registration failed | Service registration encounters an unrecoverable failure | ERROR | 
| Webhook Validation fails | When webhook received by Devops agent doesn't match the expected schema | ERROR | 
| Association Validation status updates | When a Agent space association(typical primary/secondary account), validation status changes from valid to invalid and vice versa(for example, caused by malformed role, that is not assumable by the service). | ERROR/INFO | 

### Permissions
<a name="permissions"></a>

AWS DevOps Agent uses [CloudWatch vended logs (V2 permissions)](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AWS-vended-logs-permissions-V2.html) to deliver logs. To set up log delivery, the IAM role that configures the delivery must have the following permissions:
+ `aidevops:AllowVendedLogDeliveryForResource` – Required to allow log delivery for the agent space resource.
+ Permissions for the CloudWatch Logs delivery APIs (`logs:PutDeliverySource`, `logs:PutDeliveryDestination`, `logs:CreateDelivery`, and related operations).
+ Permissions specific to your chosen delivery destination.

For the full IAM policy that is required for each destination type, see the following topics in the *Amazon CloudWatch Logs User Guide*:
+ [Logs sent to CloudWatch Logs](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AWS-logs-infrastructure-V2-CloudWatchLogs.html)
+ [Logs sent to Amazon S3](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AWS-logs-infrastructure-V2-S3.html)
+ [Logs sent to Firehose](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AWS-logs-infrastructure-V2-Firehose.html)

### Configure log delivery (console)
<a name="configure-log-delivery-console"></a>

AWS DevOps Agent provides two locations in the AWS Management Console to configure log delivery:
+ **Service Registration settings page** – Configure log delivery for service-level events. These logs use the service ARN (`arn:aws:aidevops:<region>:<account-id>:service/<account-id>`) as the resource.
+ **Agent Space page** – Configure log delivery for events that are specific to an individual agent space. These logs use the agent space ARN (`arn:aws:aidevops:<region>:<account-id>:agentspace/<agent-space-id>`) as the resource.

#### To configure log delivery for a service registration
<a name="to-configure-log-delivery-for-a-service-registration"></a>

1. Open the AWS DevOps Agent console in the AWS Management Console.

1. In the navigation pane, choose **Settings**.

1. In the **Capability Providers** **>** **Logs** tab, choose **Configure**.

1. For **Destination type**, choose one of the following:

1. **CloudWatch Logs** – Select or create a log group.

1. **Amazon S3** – Enter the S3 bucket ARN.

1. **Amazon Data Firehose** – Select or create a Firehose delivery stream.

1. For **Additional settings** – *optional*, you can specify the following options:

   1. For **Field selection**, select the log field names that you want to deliver to your destination. You can select [access log fields](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/standard-logs-reference.html#BasicDistributionFileFormat) and a subset of [real-time access log fields](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/standard-logging.html#standard-logging-real-time-log-selection).

   1. (Amazon S3 only) For **Partitioning**, specify the path to partition your log file data.

   1. (Amazon S3 only) For **Hive-compatible file format**, you can select the checkbox to use Hive-compatible S3 paths. This helps simplify loading new data into your Hive-compatible tools.

   1. For **Output format**, specify your preferred format.

   1. For **Field delimiter**, specify how to separate log fields.

1. Choose **Save**.

1. Verify that the delivery status shows **Active**.

#### To configure log delivery for an agent space
<a name="to-configure-log-delivery-for-an-agent-space"></a>

1. Open the AWS DevOps Agent console in the AWS Management Console.

1. Choose the agent space that you want to configure.

1. In the **Configuration** tab, choose **Configure**.

1. For **[Destination type](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AWS-logs-and-resource-policy.html#AWS-vended-logs-permissions-V2:~:text=sts%3AAssumeRole%22%0A%20%20%20%20%7D%0A%20%20%5D%0A%7D-,Logging%20that%20requires%20additional%20permissions%20%5BV2%5D,-Some%20AWS%20services)**, choose one of the following:

1. **CloudWatch Logs** – Select or create a log group.

1. **Amazon S3** – Enter the S3 bucket ARN.

1. **Amazon Data Firehose** – Select or create a Firehose delivery stream.

1. For **Additional settings – \*optional** \*, you can specify the following options:

   1. For **Field selection**, select the log field names that you want to deliver to your destination. You can select [access log fields](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/standard-logs-reference.html#BasicDistributionFileFormat) and a subset of [real-time access log fields](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/standard-logging.html#standard-logging-real-time-log-selection).

   1. (Amazon S3 only) For **Partitioning**, specify the path to partition your log file data.

   1. (Amazon S3 only) For **Hive-compatible file format**, you can select the checkbox to use Hive-compatible S3 paths. This helps simplify loading new data into your Hive-compatible tools.

   1. For **Output format**, specify your preferred format.

   1. For **Field delimiter**, specify how to separate log fields.

1. Choose **Save**.

1. Verify that the delivery status shows **Active**.

### Configure log delivery (CloudWatch API)
<a name="configure-log-delivery-cloudwatch-api"></a>

You can also use the CloudWatch Logs API to configure log delivery programmatically. A working log delivery consists of three elements:
+ A **DeliverySource** – Represents the AWS DevOps Agent space resource that generates the logs.
+ A **DeliveryDestination** – Represents the destination where logs are written.
+ A **Delivery** – Connects a delivery source to a delivery destination.

#### Step 1: Create a delivery source
<a name="step-1-create-a-delivery-source"></a>

Use the [PutDeliverySource](https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_PutDeliverySource.html) operation to create a delivery source. Pass the ARN of your AWS DevOps Agent space resource and specify `APPLICATION_LOGS` as the log type.

The following example creates a delivery source for an agent space:

```
{
    "name": "my-agent-space-delivery-source",
    "resourceArn": "arn:aws:aidevops:us-east-1:123456789012:agentspace/my-agent-space-id",
    "logType": "APPLICATION_LOGS"
}
```

The following example creates a delivery source for the service:

```
{
    "name": "my-service-delivery-source",
    "resourceArn": "arn:aws:aidevops:us-east-1:123456789012:service",
    "logType": "APPLICATION_LOGS"
}
```

#### Step 2: Create a delivery destination
<a name="step-2-create-a-delivery-destination"></a>

Use the [PutDeliveryDestination](https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_PutDeliveryDestination.html) operation to configure where logs are stored. You can choose Amazon CloudWatch Logs, Amazon S3, or Amazon Data Firehose.

The following example creates a CloudWatch Logs destination:

```
{
    "name": "my-cwl-destination",
    "deliveryDestinationConfiguration": {
        "destinationResourceArn": "arn:aws:logs:us-east-1:123456789012:log-group:/aws/aidevops/my-agent-space"
    },
    "outputFormat": "json"
}
```

The following example creates an Amazon S3 destination:

```
{
    "name": "my-s3-destination",
    "deliveryDestinationConfiguration": {
        "destinationResourceArn": "arn:aws:s3:::my-aidevops-logs-bucket"
    },
    "outputFormat": "json"
}
```

The following example creates an Amazon Data Firehose destination:

```
{
    "name": "my-firehose-destination",
    "deliveryDestinationConfiguration": {
        "destinationResourceArn": "arn:aws:firehose:us-east-1:123456789012:deliverystream/my-aidevops-log-stream"
    },
    "outputFormat": "json"
}
```

**Note**  
** If you deliver logs cross-account, you must use [PutDeliveryDestinationPolicy](https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_PutDeliveryDestinationPolicy.html) in the destination account to authorize the delivery.

If you want to use CloudFormation, you can use the following:
+ [Delivery](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-delivery.html)
+ [DeliveryDestination](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-deliverydestination.html)
+ [DeliverySource](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-deliverysource.html)

The `ResourceArn` is the `AgentSpaceArn`, and `LogType` must be `APPLICATION_LOGS` as the supported log type.

#### Step 3: Create a delivery
<a name="step-3-create-a-delivery"></a>

Use the [CreateDelivery](https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_CreateDelivery.html) operation to link the delivery source to the delivery destination.

```
{
    "deliverySourceName": "my-agent-space-delivery-source",
    "deliveryDestinationArn": "arn:aws:logs:us-east-1:123456789012:delivery-destination:my-cwl-destination"
}
```

#### AWS CloudFormation
<a name="aws-cloudformation"></a>

You can also configure log delivery by using AWS CloudFormation with the following resources:
+ [AWS::Logs::DeliverySource](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-deliverysource.html)
+ [AWS::Logs::DeliveryDestination](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-deliverydestination.html)
+ [AWS::Logs::Delivery](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-delivery.html)

Set `ResourceArn` to the AWS DevOps Agent agent space or service ARN, and set `LogType` to `APPLICATION_LOGS`.

### Log schema reference
<a name="log-schema-reference"></a>

AWS DevOps Agent uses a shared log schema across all event types. Not every log event uses every field.

The following table describes the fields in the log schema.


| Field | Type | Description | 
| --- | --- | --- | 
| event\_timestamp | Long | Unix timestamp of when the event occurred | 
| resource\_arn | String | ARN of the resource that generated the event | 
| optional\_account\_id | String | AWS account ID associated with the log. | 
| optional\_level | String | Log level: INFO, WARN, ERROR | 
| optional\_agent\_space\_id | String | Identifier of the agent space. | 
| optional\_association\_id | String | Association identifier for the log. | 
| optional\_status | String | Status of the topology operation. | 
| optional\_webhook\_id | String | Webhook identifier. | 
| optional\_mcp\_endpoint\_url | String | MCP server endpoint URL | 
| optional\_service\_type | String | Type of the Service: DYNATRACE, DATADOG, GITHUB, SLACK, SERVICENOW. | 
| optional\_service\_endpoint\_url | String | Endpoint URL for third-party integrations. | 
| optional\_service\_id | String | Identifier of the source. | 
| request\_id | String | Request identifier for correlating with AWS CloudTrail or support tickets. | 
| optional\_operation | String | Name of the operation that was performed. | 
| optional\_task\_type | String | Agent backlog task type: INVESTIGATION or EVALUATION | 
| optional\_task\_id | String | Agent Backlog Task IDAgent backlog task identifier. | 
| optional\_reference | String | Reference from an agent task (for example, a Jira ticket). | 
| optional\_error\_type | String | Error type. For example, PROVIDER\_ERROR when a third-party provider call fails, or TOKEN\_ACCESS\_DENIED when access is denied while retrieving an association's credentials. | 
| optional\_error\_message | String | Error description when an operation fails. | 
| optional\_details | String (JSON) | Service-specific event payload that contains operation parameters and results. | 

### Manage and disable log delivery
<a name="manage-and-disable-log-delivery"></a>

You can modify or remove log delivery at any time from the AWS DevOps Agent console in the AWS Management Console or by using the CloudWatch Logs API.

#### Manage log delivery (console)
<a name="manage-log-delivery-console"></a>

1. Open the AWS DevOps Agent console in the AWS Management Console.

1. Navigate to the **Settings** page (for service-level logs) or the specific **Agent Space** page (for Agent Space-level logs).

1. In the **Configuration** tab (for Agent Space-level logs) or **Capability Providers** **>** **Logs** tab (for service-level logs), choose the delivery to modify.

1. Update the configuration as needed and choose **Save**.

**Note:** You can't change the destination type of an existing delivery. To change the destination type, delete the current delivery and create a new one.

#### Disable log delivery (console)
<a name="disable-log-delivery-console"></a>

1. Open the AWS DevOps Agent console in the AWS Management Console.

1. Navigate to the **Settings** page (for service-level logs) or the specific **Agent Space** page (for Agent Space-level logs).

1. In the **Configuration** tab (for Agent Space-level logs) or **Capability Providers** **>** **Logs** tab (for service-level logs),, select the delivery to remove.

1. Choose **Delete** and confirm.

#### Disable log delivery (API)
<a name="disable-log-delivery-api"></a>

To remove a log delivery by using the API, delete the resources in the following order:

1. Delete the delivery by using [DeleteDelivery](https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_DeleteDelivery.html).

1. Delete the delivery source by using [DeleteDeliverySource](https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_DeleteDeliverySource.html).

1. (Optional) If the delivery destination is no longer needed, delete it by using [DeleteDeliveryDestination](https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_DeleteDeliveryDestination.html).

**Important**  
** You are responsible for removing log delivery resources after you delete the agent space resource that generates the logs (for example, after you delete an agent space). If you don't remove these resources, orphaned delivery configurations might remain.

## Pricing
<a name="pricing"></a>

The AWS DevOps Agent does not charge for enabling vended logs. However, you can incur charges for the delivery, ingestion, storage or access, depending on the log delivery destination that you select. For pricing details, see **Vended Logs** on the **Logs** tab at [Amazon CloudWatch Pricing](https://aws.amazon.com/cloudwatch/pricing/).

For destination-specific pricing, see the following:
+ [Amazon CloudWatch Logs Pricing](https://aws.amazon.com/cloudwatch/pricing/)
+ [Amazon S3 Pricing](https://aws.amazon.com/s3/pricing/)
+ [Amazon Data Firehose Pricing](https://aws.amazon.com/kinesis/data-firehose/pricing/)