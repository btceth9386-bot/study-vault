

# Creating a custom agent
<a name="custom-agents-creating-a-custom-agent"></a>

You can create a custom agent in two ways: using the form in the DevOps Agent web app, or through a guided conversation in Chat. Both methods result in the same custom agent configuration stored in your Agent Space.

Before creating a custom agent, you must have an Agent Space with at least one connected integration. For more information, see [Creating an Agent Space](getting-started-with-aws-devops-agent-creating-an-agent-space.md).

## Creating a custom agent using the form
<a name="creating-a-custom-agent-using-the-form"></a>

The form lets you quickly create a custom agent by specifying a name, system prompt, and optional skills. To assign MCP tools to the agent, use Chat after creating the agent.

**To create a custom agent using the form:**

1. Navigate to the **Agents** page in your DevOps Agent web app.

1. In the **Custom Agents** section, choose **Create agent**.

1. In the dialog, choose **Form**.

1. Fill out the form:
   + **Name** – A unique identifier for your agent. Use lowercase letters, numbers, and hyphens only (maximum 64 characters). Must not start or end with a hyphen. Example: `weekly-health-report`
   + **System prompt** – Instructions that define what the agent does and how it operates, written in Markdown (minimum 10 characters, maximum 50,000 characters). For guidance on writing effective prompts, see [Writing a system prompt](#writing-a-system-prompt).
   + **Skills** (optional) – Select skills from your Agent Space that provide additional domain knowledge or capabilities to the agent. Use the search field to find skills by name.

1. Choose **Create agent**.

After creation, you are redirected to the agent's detail page where you can view the configuration, run the agent, or set up triggers.

## Creating a custom agent using Chat
<a name="creating-a-custom-agent-using-chat"></a>

Chat provides a guided, conversational experience for creating custom agents. This method is recommended when you want to assign MCP tools to the agent, or when you want assistance writing the system prompt.

**To create a custom agent using Chat:**

1. Navigate to the **Agents** page in your DevOps Agent web app.

1. In the **Custom Agents** section, choose **Create agent**.

1. In the dialog, choose **Chat**. The dialog closes and a new conversation opens in the Chat panel with a pre-composed message.

1. Chat guides you through a collaborative process:
   + **Intent clarification** – Confirms the purpose and scope of your agent.
   + **Duplicate check** – Verifies no similar agent already exists in your Agent Space.
   + **Tool and skill selection** – Proposes which MCP tools and skills the agent needs, and asks you to confirm.
   + **Output type** – Determines whether the agent should produce text responses, artifacts, or recommendations.
   + **System prompt draft** – Writes a system prompt and presents it for your review. You can iterate until you are satisfied.
   + **Confirmation** – Suggests a name and confirms all settings before creating the agent.

You can also create a custom agent by asking Chat directly at any time. For example:

```
Create an agent that generates a weekly report of all investigations from the past week.
```

```
Create a custom agent for checking certificate expiration across all accounts.
```

```
Make me an agent that audits DynamoDB table configurations daily.
```

## Writing a system prompt
<a name="writing-a-system-prompt"></a>

The system prompt is the most important part of your custom agent. It defines the agent's purpose, approach, constraints, and expected output. A well-written prompt produces consistent, reliable results.

**Structure your system prompt with these sections:**
+ **Goal** – What the agent should accomplish in a single sentence or short paragraph.
+ **Approach** – Step-by-step procedures the agent should follow, referencing specific tool names it should call and in what order.
+ **Constraints** – Boundaries on what the agent should and should not do. For example, read-only access, time ranges to consider, or services to exclude.
+ **Output** – What the agent should produce and in what format. Specify whether it should generate text, create an artifact, or create a recommendation.

**Example system prompt:**

```
You are a DevOps reporting agent specializing in summarizing investigation activity.

## Goal
Generate a concise weekly report of all investigations from the past 7 days.

## Approach
1. Call `list_investigations` to fetch investigations from the last 7 days.
2. For each investigation, retrieve its title, status, root cause, and resolution time.
3. Group investigations by status and root cause category.
4. Identify trends: services most affected, average resolution time, recurring root causes.

## Constraints
- Only include investigations from the past 7 days.
- Read-only access — do not modify, close, or reassign investigations.

## Output
Produce a single artifact titled "Weekly Investigation Report" containing:
- A table listing each investigation with title, status, and resolution time.
- A chart showing investigation counts by root cause category.
- A summary paragraph with key trends and recommendations.
```

**Tips for effective system prompts:**
+ **Be specific about tools** – Reference tool names directly (for example, `list_investigations`, `use_aws`, `query_cloudwatch_logs`) so the agent knows which tools to call.
+ **Define success criteria** – Describe what a good output looks like so the agent knows when it is done.
+ **Set boundaries** – Explicitly state what the agent should not do to prevent unintended actions.
+ **Use Markdown formatting** – Headers, lists, and code blocks make the prompt easier for the agent to parse and follow.

## Configuring tools
<a name="configuring-tools"></a>

MCP tools determine what actions your custom agent can perform during invocation. You select tools from the full set available in your Agent Space, including tools from connected AWS accounts, observability platforms, CI/CD pipelines, ticketing systems, and custom MCP servers.

Tools can only be configured through Chat. To assign tools when creating an agent, use the Chat creation method. To add or change tools on an existing agent, ask Chat to update the agent. For example:

```
Add the query_cloudwatch_logs and use_aws tools to my weekly-health-report agent.
```

```
Update certificate-checker to also use the list_resources tool.
```

```
Remove the use_kubectl tool from cluster-audit-agent.
```

When selecting tools, follow the principle of least privilege — assign only the tools the agent needs to accomplish its task. This reduces the risk of unintended actions and keeps the agent focused.

## Configuring skills
<a name="configuring-skills"></a>

Skills provide your custom agent with additional domain knowledge, investigation procedures, or specialized capabilities. When a custom agent runs, it loads its assigned skills and can reference their instructions during invocation.

You can assign skills during creation (using either the form or Chat) or add them later by editing the agent. Skills assigned to a custom agent must already exist in your Agent Space. For more information about creating skills, see [DevOps Agent Skills](about-aws-devops-agent-devops-agent-skills.md).

Custom agents also have built-in capabilities for creating artifacts and recommendations that do not require skill assignment. For more information, see [Custom agent outputs](custom-agents-custom-agent-outputs.md).

You can assign up to 200 skills per custom agent. Choose skills that are relevant to the agent's purpose to reduce context consumption and improve agent focus.