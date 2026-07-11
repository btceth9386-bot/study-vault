

# DevOps Agent Memories
<a name="about-aws-devops-agent-devops-agent-memories"></a>

Memories are informational knowledge items that AWS DevOps Agent builds and maintains to supplement its capabilities with synthesized, high-signal context specific to your Agent Space. Unlike [DevOps Agent Skills](about-aws-devops-agent-devops-agent-skills.md), which encode procedural knowledge and extend agent capabilities, memories encode informational knowledge that helps agents make faster and more accurate decisions during investigations.

## What are memories
<a name="what-are-memories"></a>

A *memory* is a single markdown file that captures synthesized information relevant to your Agent Space. Examples include recurring root causes for a specific alarm, known environmental quirks, or user-specific preferences. Memories do not extend agent capabilities; they provide context the agent uses to make better decisions.

A *memory store* is a collection of related memory files. Each memory store has a name and description that agents use to decide whether to browse its contents. Memory stores are the organizational containers that group memories by topic.

Memories differ from other knowledge item types in key ways:


| Aspect | Skill | Agent instructions | Memory | 
| --- | --- | --- | --- | 
| Knowledge type | Procedural (instructions) | Procedural (always-on instructions) | Informational (synthesized context) | 
| Content format | Markdown or ZIP bundle | Markdown only | Markdown only | 
| Context injection | On demand (agent decides via description matching) | Always (every session) | On demand (agent decides via description matching) | 
| Created by | User (UI, CLI), DevOps Agent | User (UI, CLI) | User (via Chat), DevOps Agent (Learning agent) | 

## Why use memories
<a name="why-use-memories"></a>

Memories give agents access to historical patterns and environmental knowledge that would otherwise be lost between sessions.

**Key benefits:**
+ **Faster investigations** - Agents recall recent root causes for specific monitors, avoiding redundant diagnostic steps when a recurring issue fires again.
+ **Environmental awareness** - Memories capture environment-specific details such as known noisy alarms, infrastructure quirks, or component relationships that are difficult to re-discover each session.
+ **Continuous improvement** - As the DevOps Agent resolves more incidents, it automatically builds a richer knowledge base of patterns and root causes specific to your infrastructure.
+ **User preferences** - Memories record communication preferences and directives so the agent consistently behaves according to your expectations.

## How memories work
<a name="how-memories-work"></a>

When an agent session starts, the agent receives a list of memory stores with their names and descriptions. During an investigation, the agent evaluates whether a memory store is relevant to the current task. If it is, the agent lists the memories within that store and reads the specific memory files it needs. This progressive-disclosure pattern keeps context consumption low while making all relevant knowledge accessible.

Each memory is versioned. Every update creates a new immutable version, enabling audit trails and rollback to previous content.

## Managed memory stores
<a name="managed-memory-stores"></a>

DevOps Agent creates and maintains the following managed memory stores automatically as it learns from sessions in your Agent Space:

### monitors
<a name="monitors"></a>

Per-monitor recurring root cause history. Each memory file corresponds to a specific monitor (alarm or metric) and lists the cause categories that have produced incidents for that alarm, with per-investigation evidence. Agents read the entry matching the firing alarm before triaging to quickly identify whether the current incident matches a known pattern.

When there are investigations in the past 2 weeks in the Agent Space, a Learning agent runs once per day to analyze recent investigations, then extract and store memories in this store. Memory items in this store are deleted when they have no updates for 2 weeks. If the store becomes full, the oldest memory item is deleted to make room.

### directives
<a name="directives"></a>

User-authored directives that steer agent behavior. Use this store to record standing instructions the agent should follow, such as infrastructure conventions or naming preferences.

Examples:
+ "Lambdas are no longer used. The service uses Fargate."
+ "The storage service is called Orders Storage Service."

## Viewing memories
<a name="viewing-memories"></a>

You can view all memory stores and their contents from the **Knowledge** page in your Agent Space Operator Web App.

**To view memory stores:**

1. Navigate to the **Knowledge** page in your Agent Space Operator Web App.

1. Choose the **Memories** tab.

1. Browse the list of managed memory stores, each showing its name, description, and agent type scope.

**To view memories within a store:**

1. On the **Memories** tab, choose **View** next to the memory store you want to explore.

1. The store detail page lists all memories with their name, description, version number, and last modified date, sorted newest first.

**To view a specific memory:**

1. From the store detail page, choose **View** next to the memory you want to read.

1. The memory detail page displays the rendered markdown content along with creation date, last modified date, and a version selector.

**To view a previous version:**

1. On the memory detail page, use the version selector dropdown to choose an older version.

1. The content updates to display the selected version.

## Activating and deactivating memories
<a name="activating-and-deactivating-memories"></a>

You can toggle individual memory stores or individual memories active or inactive without deleting them.

**To toggle a memory store:**

1. On the **Memories** tab, use the toggle switch next to the memory store.

1. When inactive, agents do not access any memories within that store.

**To toggle an individual memory:**

1. Navigate into a memory store to see its list of memories.

1. Use the toggle switch next to the memory you want to activate or deactivate.

1. When inactive, agents skip that specific memory during investigations.

## Editing memories with Chat
<a name="editing-memories-with-chat"></a>

You can create, update, or delete memories by chatting with the DevOps Agent in the Chat interface. The Chat agent can write directly to memory stores.

**Examples of Chat commands:**
+ "Remember that the storage service is called Orders Storage Service" - Creates or updates a memory in the directives store.
+ "Update the memory for the canary alarm to note that it is flaky during deployments" - Updates a specific memory in the monitors store.
+ "Delete the memory about the old database connection string" - Removes a memory that is no longer relevant.

The Chat agent writes directly to memory stores on your behalf.

## Memory limits
<a name="memory-limits"></a>

The following limits apply to memories:


| Resource | Limit | 
| --- | --- | 
| Memory stores per Agent Space | 50 | 
| Memories per memory store | 200 | 
| Individual memory content size | 100 KB | 