

# Executing custom agents
<a name="custom-agents-executing-custom-agents"></a>

You can execute a custom agent on demand or configure triggers to run it automatically.

## Running a custom agent on demand
<a name="running-a-custom-agent-on-demand"></a>

You can run a custom agent immediately from the agent detail page or through Chat.

**To run a custom agent from the detail page:**

1. Navigate to the **Agents** page in your DevOps Agent web app.

1. Choose the custom agent you want to run.

1. Choose **Run Now** to execute the agent with its configured instructions.

To provide additional context for a specific run, choose the dropdown arrow next to **Run Now**, enter a prompt describing what the agent should focus on in this invocation, and choose **Run with prompt**. The prompt is passed to the agent as additional context alongside its system prompt.

After the run starts, the new invocation appears in the **History** tab with a status of "Pending start". Choose the invocation to view its trajectory in real time.

**To run a custom agent using Chat:**

Ask Chat to run the agent by name. For example:

```
Run my weekly-investigation-report agent.
```

```
Run certificate-checker and focus on certificates expiring in the next 7 days.
```

When you provide additional context in the chat message, Chat passes it as the prompt for that run. If you don't provide additional context, the agent runs with its configured system prompt only.

A custom agent can only run one invocation at a time. If the agent is already running, you must wait for the current invocation to complete, time out, or be canceled before starting another.

## Scheduling custom agents
<a name="scheduling-custom-agents"></a>

Triggers let you run a custom agent automatically based on defined conditions. AWS DevOps Agent currently supports schedule-based triggers, which execute the agent at recurring intervals using EventBridge-compatible cron or rate expressions.

**To create a schedule trigger:**

1. Navigate to the **Agents** page in your DevOps Agent web app.

1. Choose the custom agent you want to schedule.

1. Choose the **Triggers** tab.

1. Choose the **\+** (create) button.

1. In the dialog, enter a schedule expression in the input field. The expression must be one of the following formats:
   + **Rate expression** – Runs at a fixed interval. Format: `rate(value unit)`. Examples:
     + `rate(1 hour)` – Every hour
     + `rate(30 minutes)` – Every 30 minutes
     + `rate(7 days)` – Every 7 days
   + **Cron expression** – Runs on a specific schedule. Format: `cron(minutes hours day-of-month month day-of-week year)`. Examples:
     + `cron(0 9 ? * MON-FRI *)` – Every weekday at 9:00 AM UTC
     + `cron(0 0 1 * ? *)` – First day of every month at midnight UTC
     + `cron(0 */6 ? * * *)` – Every 6 hours

A green confirmation message appears when the expression is valid.

1. Choose **Create**.

For cron expressions, exactly one of day-of-month or day-of-week must be `?` (question mark). For more information about schedule expression syntax, see [Schedule types](https://docs.aws.amazon.com/scheduler/latest/UserGuide/schedule-types.html) in the *Amazon EventBridge Scheduler User Guide*.

After creation, the trigger appears in the list showing its expression, creation date, and next scheduled run time.

## Managing triggers
<a name="managing-triggers"></a>

The **Triggers** tab displays all triggers configured for the custom agent. For each trigger, you can see the schedule expression, when it was created, and when it will next run.

**Pausing a trigger:**

To temporarily stop a trigger from invoking the agent without deleting it, turn off the toggle switch next to the trigger. The trigger status changes to "Paused" and no longer fires until re-enabled. Turn the toggle back on to resume the schedule.

**Deleting a trigger:**

To permanently remove a trigger, choose the delete icon (trash can) next to the trigger you want to remove. Confirm the deletion in the dialog that appears. Deleted triggers cannot be recovered.

## Canceling an invocation
<a name="canceling-an-invocation"></a>

You can cancel a running invocation from the invocation trajectory view or through Chat.

**To cancel a running invocation from the trajectory view:**

1. From the **History** tab, choose the running invocation.

1. Choose **Cancel** at the top of the trajectory view.

**To cancel a running invocation using Chat:**

```
Cancel the running invocation of weekly-health-report.
```

The invocation status changes to "Canceled". Any work completed before cancellation is preserved in the trajectory. Tool calls that were in progress when the cancellation occurred may still complete.

## Tool call results
<a name="tool-call-results"></a>

During invocation, the custom agent invokes MCP tools to gather data, perform actions, and produce outputs. Each tool call and its result are recorded in the invocation trajectory.

Tool call results provide transparency into what the agent did during invocation:
+ **Successful tool calls** – The tool returned data that the agent uses to continue its work. For example, `query_cloudwatch_logs` returns log entries, or `use_aws` returns API responses.
+ **Failed tool calls** – The tool returned an error. The agent may retry, try an alternative approach, or report the failure in its output.

You can inspect individual tool calls and their results in the invocation trajectory to understand the agent's behavior, verify it accessed the correct resources, and troubleshoot unexpected results. For more information about viewing trajectories, see [Viewing an invocation trajectory](custom-agents-managing-custom-agents.md).