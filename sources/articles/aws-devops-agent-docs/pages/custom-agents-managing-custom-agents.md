

# Managing custom agents
<a name="custom-agents-managing-custom-agents"></a>

After creating a custom agent, you can edit its configuration, view its invocation history, and delete it when it is no longer needed.

## Editing a custom agent
<a name="editing-a-custom-agent"></a>

You can edit a custom agent using the form or through Chat. The form lets you update the name, system prompt, and skills. To modify the agent's tools, use Chat.

**To edit a custom agent using the form:**

1. Navigate to the **Agents** page in your DevOps Agent web app.

1. Choose the custom agent you want to edit.

1. On the agent detail page, choose **Edit**.

1. In the dialog, choose **Form**.

1. Modify the fields you want to update:
   + **Name** – Update the agent's identifier (same constraints as creation: lowercase, hyphens, maximum 64 characters).
   + **System prompt** – Revise the agent's instructions (minimum 10 characters, maximum 50,000 characters).
   + **Skills** – Add or remove skills using the search field.

1. Choose **Save**.

Fields you do not modify retain their current values. The agent's assigned tools are preserved when editing through the form.

**To edit a custom agent using Chat:**

You can update any field — including tools — by asking Chat. For example:

```
Update weekly-health-report to also check for Lambda function errors.
```

```
Add the use_kubectl tool to my cluster-audit-agent.
```

```
Change the system prompt of certificate-checker to also report certificates expiring within 30 days.
```

Chat retrieves the current agent configuration, applies your requested changes, and confirms before saving. Fields you do not mention remain unchanged.

## Viewing invocation history
<a name="viewing-invocation-history"></a>

The agent detail page shows a complete history of all invocations for a custom agent, including status, trigger source, and timestamps.

**To view invocation history:**

1. Navigate to the **Agents** page in your DevOps Agent web app.

1. Choose the custom agent you want to inspect.

1. Choose the **History** tab.

The invocations table displays the following information:


| Column | Description | 
| --- | --- | 
| Invocation | The task title or description provided when the agent was invoked. | 
| Status | Current invocation status (see below). | 
| Triggered By | How the invocation was started — the trigger name for scheduled runs, or "Manual" for on-demand invocations. | 
| Started | Date and time the invocation began. | 
| Last Updated | Date and time of the most recent status change. | 

You can filter invocations by status or search by title. The table refreshes automatically every 10 seconds to show updated statuses for running invocations.

**Invocation statuses:**


| Status | Description | 
| --- | --- | 
| Pending start | The invocation is queued and waiting to be scheduled. | 
| Running | The agent is actively executing. | 
| Succeeded | The invocation completed successfully. | 
| Failed | The invocation encountered an error and stopped. | 
| Timed out | The invocation exceeded the 1-hour timeout limit. | 
| Canceled | The invocation was manually canceled before completion. | 

## Viewing an invocation trajectory
<a name="viewing-an-invocation-trajectory"></a>

The invocation trajectory shows the complete trace of an agent's work — every tool call, result, and text output the agent produced during a single invocation.

**To view an invocation trajectory:**

1. From the **History** tab, choose the invocation you want to inspect.

1. Review the trajectory timeline.

The timeline displays the following step types:
+ **Tool calls** – Which tools the agent invoked and with what parameters.
+ **Tool results** – The responses returned by each tool.
+ **Text outputs** – Messages the agent produced during invocation.
+ **Generated outputs** – Any artifacts or recommendations the agent produced, shown as links at the end of the timeline.

For running invocations, the trajectory updates in real time. You can cancel a running invocation by choosing **Cancel** at the top of the trajectory view.

## Deleting a custom agent
<a name="deleting-a-custom-agent"></a>

**Important**  
** Deleting a custom agent does not affect invocations that are already in progress. Running invocations continue until they complete, time out, or are canceled. However, the agent cannot be invoked again after deletion.

You can delete a custom agent using Chat. Deletion is permanent and cannot be undone.

**To delete a custom agent:**

Ask Chat to delete the agent by name. For example:

```
Delete the custom agent weekly-health-report.
```

Chat confirms the agent name and type before deleting. If the agent has active triggers, they are removed along with the agent.