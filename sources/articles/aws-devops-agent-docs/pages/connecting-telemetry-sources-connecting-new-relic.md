

# Connecting New Relic
<a name="connecting-telemetry-sources-connecting-new-relic"></a>

## Built-in, 1 way integration
<a name="built-in-1-way-integration"></a>

Currently, AWS DevOps Agent supports New Relic users with built-in, 1 way integration, enabling the following:
+ **Automated Investigation triggering** - New Relic events can be configured to trigger AWS DevOps Agent incident resolution Investigations via AWS DevOps Agent webhooks.
+ **Telemetry introspection** - AWS DevOps Agent can introspect New Relic telemetry as it investigates an issue via each provider's remote MCP server.

## Onboarding
<a name="onboarding"></a>

### Step 1: Connect
<a name="step-1-connect"></a>

Establish connection to your New Relic remote MCP endpoint with account access credentials

Please use a Full Platform User (not Basic/Core) in New relic to enable New Relic MCP tools.

#### Configuration
<a name="configuration"></a>

1. Go to the **Capability Providers** page (accessible from the side navigation)

1. Find **New Relic** in the **Available** providers section under **Telemetry** and choose **Register**

1. Follow the instructions to obtain your New Relic API Key

1. Enter your New Relic MCP server API Key details:
   + **Account ID:** Enter your New Relic account ID obtained above
   + **API Key:** Enter the API Key obtained above
   + **Select US or EU region** based on where your New Relic account is.

1. Choose Add

### Step 2: Enable
<a name="step-2-enable"></a>

Activate New Relic in a specific Agent space and configure appropriate scoping

#### Configuration
<a name="configuration"></a>

1. From the agent spaces page, select an agent space and press view details (if you have not yet created an agent space see [Creating an Agent Space](getting-started-with-aws-devops-agent-creating-an-agent-space.md))

1. Select the Capabilities tab

1. Scroll down to the Telemetry section

1. Press Add

1. Select New Relic

1. Next

1. Review and press Save

1. Copy the Webhook URL and API Key

### Step 3: Configure webhooks
<a name="step-3-configure-webhooks"></a>

Using the Webhook URL and API Key you can configure New Relic to send events to trigger an investigation, for example from an alarm. For more details on setting up webhooks, see [Change tracking webhooks](https://docs.newrelic.com/docs/change-tracking/change-tracking-webhooks/).

New Relic webhooks use bearer token authentication. For the complete webhook request format, payload schema, and example code, see [Invoking DevOps Agent through Webhook](configuring-integrations-and-knowledge-invoking-devops-agent-through-webhook.md). Use the Version 2 (Bearer token authentication) examples, setting the `Authorization: Bearer <Token>` header with the API Key from Step 2.

Send webhooks with New Relic [https://newrelic.com/instant-observability/webhook-notifications](https://newrelic.com/instant-observability/webhook-notifications). You can either select Bearer token for the authorization type, or select no authorization and add the `Authorization: Bearer <Token>` as a custom header instead.

Learn more: [https://docs.newrelic.com/docs/agentic-ai/mcp/overview/](https://docs.newrelic.com/docs/agentic-ai/mcp/overview/)

## Removal
<a name="removal"></a>

The telemetry source is connected at two levels at the agent space level and at account level. To completely remove it you must first remove from all agent spaces where it is used and then it can be unregistered.

### Step 1: Remove from agent space
<a name="step-1-remove-from-agent-space"></a>

1. From the agent spaces page, select an agent space and press view details

1. Select the Capabilities tab

1. Scroll down to the Telemetry section

1. Select New Relic

1. Press remove

### Step 2: Deregister from account
<a name="step-2-deregister-from-account"></a>

1. Go to the **Capability Providers** page (accessible from the side navigation)

1. Scroll to the **Currently registered** section.

1. Check the agent space count is zero (if not repeat Step 1 above in your other agent spaces)

1. Press Deregister next to New Relic