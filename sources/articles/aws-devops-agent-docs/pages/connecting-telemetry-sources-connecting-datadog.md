

# Connecting DataDog
<a name="connecting-telemetry-sources-connecting-datadog"></a>

## Built-in, 1 way integration
<a name="built-in-1-way-integration"></a>

Currently, AWS DevOps Agent supports Datadog users with built-in, 1 way integration, enabling the following:
+ **Automated Investigation triggering** - Datadog events can be configured to trigger AWS DevOps Agent incident resolution Investigations via AWS DevOps Agent webhooks.
+ **Telemetry introspection** - AWS DevOps Agent can introspect Datadog telemetry as it investigates an issue via each provider's remote MCP server.

## Onboarding
<a name="onboarding"></a>

### Step 1: Connect
<a name="step-1-connect"></a>

Establish connection to your Datadog remote MCP endpoint with account access credentials

#### Configuration
<a name="configuration"></a>

1. Go to the **Capability Providers** page (accessible from the side navigation)

1. Find **Datadog** in the **Available** providers section under **Telemetry** and choose **Register**

1. Enter your Datadog MCP server details:
   + **Server Name** - Unique identifier (e.g., my-datadog-server)
   + **Endpoint URL** - Your Datadog MCP server endpoint. The endpoint URL varies depending on your Datadog site. See the Datadog site endpoint table below.
   + **Description** - Optional server description

1. Choose Next

1. Review and submit

#### Datadog site endpoints
<a name="datadog-site-endpoints"></a>

The MCP endpoint URL varies depending on your Datadog site. To identify your site, check the URL in your browser when logged into Datadog, or see [Access the Datadog site](https://docs.datadoghq.com/getting_started/site/#access-the-datadog-site).


| Datadog Site | Site Domain | MCP Endpoint URL | 
| --- | --- | --- | 
| US1 (default) | datadoghq.com | https://mcp.datadoghq.com/api/unstable/mcp-server/mcp | 
| US3 | us3.datadoghq.com | https://mcp.us3.datadoghq.com/api/unstable/mcp-server/mcp | 
| US5 | us5.datadoghq.com | https://mcp.us5.datadoghq.com/api/unstable/mcp-server/mcp | 
| EU1 | datadoghq.eu | https://mcp.datadoghq.eu/api/unstable/mcp-server/mcp | 
| AP1 | ap1.datadoghq.com | https://mcp.ap1.datadoghq.com/api/unstable/mcp-server/mcp | 
| AP2 | ap2.datadoghq.com | https://mcp.ap2.datadoghq.com/api/unstable/mcp-server/mcp | 

#### Authorization
<a name="authorization"></a>

Complete OAuth authorization by:
+ Authorizing as your user on the Datadog OAuth page
+ If not logged in, choose Allow, login, then authorize

Once configured, Datadog becomes available across all Agent spaces.

### Step 2: Enable
<a name="step-2-enable"></a>

Activate DataDog in a specific Agent space and configure appropriate scoping

#### Configuration
<a name="configuration"></a>

1. From the agent spaces page, select an agent space and press view details (if you have not yet created an agent space see [Creating an Agent Space](getting-started-with-aws-devops-agent-creating-an-agent-space.md))

1. Select the Capabilities tab

1. Scroll down to the Telemetry section

1. Press Add

1. Select Datadog

1. Next

1. Review and press Save

1. Copy the Webhook URL and API Key

### Step 3: Configure webhooks
<a name="step-3-configure-webhooks"></a>

Using the Webhook URL and API Key you can configure Datadog to send events to trigger an investigation, for example from an alarm.

Datadog webhooks use bearer token authentication. For the complete webhook request format, payload schema, and example code, see [Invoking DevOps Agent through Webhook](configuring-integrations-and-knowledge-invoking-devops-agent-through-webhook.md). Use the Version 2 (Bearer token authentication) examples, setting the `Authorization: Bearer <Token>` header with the API Key from Step 2.

Send webhooks with Datadog [https://docs.datadoghq.com/integrations/webhooks/](https://docs.datadoghq.com/integrations/webhooks/) (note select no authorization and instead use the custom header option).

Learn more: [Datadog Remote MCP Server](https://www.datadoghq.com/blog/datadog-remote-mcp-server/)

## Removal
<a name="removal"></a>

The telemetry source is connected at two levels at the agent space level and at account level. To completely remove it you must first remove from all agent spaces where it is used and then it can be unregistered.

### Step 1: Remove from agent space
<a name="step-1-remove-from-agent-space"></a>

1. From the agent spaces page, select an agent space and press view details

1. Select the Capabilities tab

1. Scroll down to the Telemetry section

1. Select Datadog

1. Press remove

### Step 2: Deregister from account
<a name="step-2-deregister-from-account"></a>

1. Go to the **Capability Providers** page (accessible from the side navigation)

1. Scroll to the **Currently registered** section.

1. Check the agent space count is zero (if not repeat Step 1 above in your other agent spaces)

1. Press Deregister next to Datadog