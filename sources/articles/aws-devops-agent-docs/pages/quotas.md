

# Quotas
<a name="quotas"></a>

AWS DevOps Agent quotas include number of agent spaces, concurrent investigations and more. You can request increases for some quotas, but not all quotas can be increased. These increases are not granted immediately, so it may take a couple of hours to days for your increase to become effective. Unless otherwise noted, each quota is Region-specific.

The following table describes the quotas for AWS DevOps Agent.


| Name | Default | Adjustable | Description | 
| --- | --- | --- | --- | 
| Agent spaces per account per Region | 100 | Yes | The maximum number of agent spaces that you can create per account in each AWS Region. | 
| Concurrent investigations per agent space | 3 | Yes | The maximum number of incident resolution investigations that can run concurrently in a single agent space. | 
| Concurrent evaluations per agent space | 1 | No | The maximum number of incident prevention evaluations that can run concurrently in a single agent space. | 
| Concurrent on-demand invocations per agent space | 10 | Yes | The maximum number of on-demand DevOps invocations that can run concurrently in a single agent space. | 
| Concurrent release readiness reviews per agent space | 4 | Yes | The maximum number of release readiness code reviews that can run concurrently in a single agent space. | 
| Concurrent automated release tests per agent space | 4 | Yes | The maximum number of release testing tests that can run concurrently in a single agent space. | 
| MCP tools per agent space | 500 | No | The maximum number of MCP tools that can be allowlisted across all MCP servers in a single agent space. | 
| Custom agents per agent space | 200 | No | The maximum number of custom agents you can create in a single agent space. | 
| Concurrent custom agent invocations per agent space | 5 | No | The maximum number of custom agent invocations that can run concurrently in a single agent space. | 
| Concurrent invocations per custom agent | 1 | No | The maximum number of concurrent invocations for the same custom agent. A custom agent must complete its current invocation before it can be invoked again. | 
| Custom agent system prompt length | 50,000 characters | No | The maximum length of the system prompt (Markdown content) for a custom agent. | 
| Skills per custom agent | 200 | No | The maximum number of skills you can assign to a single custom agent. | 
| Custom agent invocation timeout | 1 hour | No | The maximum duration for a single custom agent invocation. | 
| Memory stores per agent space | 50 | No | The maximum number of memory stores that can exist in a single agent space. | 
| Memories per memory store | 200 | No | The maximum number of individual memory files within a single memory store. | 

## Requesting a quota increase
<a name="requesting-a-quota-increase"></a>

You can request a quota increase by using one of the following options:
+ **From the AWS Management Console** – Open the [Service Quotas console](https://console.aws.amazon.com/servicequotas/). In the navigation pane, choose **AWS services**. Select **DevOps Agent**, select a quota, and follow the directions to request a quota increase. For more information, see [Requesting a quota increase](https://docs.aws.amazon.com/servicequotas/latest/userguide/request-quota-increase.html) in the *Service Quotas User Guide*.
+ **From the AWS CLI** – Use the [request-service-quota-increase](https://docs.aws.amazon.com/cli/latest/reference/service-quotas/request-service-quota-increase.html) AWS CLI command. For more information, see [Requesting a quota increase](https://docs.aws.amazon.com/servicequotas/latest/userguide/request-quota-increase.html) in the *Service Quotas User Guide*.