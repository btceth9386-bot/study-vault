

# Connecting Splunk
<a name="connecting-telemetry-sources-connecting-splunk"></a>

## Built-in, 1 way integration
<a name="built-in-1-way-integration"></a>

Currently, AWS DevOps Agent supports Splunk users with built-in, 1 way integration, enabling the following:
+ **Automated Investigation triggering** - Splunk events can be configured to trigger AWS DevOps Agent incident resolution Investigations via AWS DevOps Agent webhooks.
+ **Telemetry introspection** - AWS DevOps Agent can introspect Splunk telemetry as it investigates an issue via each provider's remote MCP server.

## Prerequisites
<a name="prerequisites"></a>

### Getting a Splunk API token
<a name="getting-a-splunk-api-token"></a>

You will need an MCP URL and token to connect Splunk.

### Splunk Administrator steps
<a name="splunk-administrator-steps"></a>

Your Splunk Administrator needs to perform the following steps:
+ enable [REST API access ](https://docs.splunk.com/Documentation/SplunkCloud/latest/RESTTUT/RESTandCloud)
+ [enable token authentication ](https://help.splunk.com/en/splunk-cloud-platform/administer/manage-users-and-security/9.2.2406/authenticate-into-the-splunk-platform-with-tokens/enable-or-disable-token-authentication) on the deployment.
+ create a new role 'mcp\_user', the new role does not need to have any capabilities.
+ assign the role 'mcp\_user' to any users on the deployment who are authorized to use the MCP server.
+ create the token for the authorized users with audience as 'mcp' and set the appropriate expiration, if the user does not have the permission to create tokens themselves.

### Splunk User steps
<a name="splunk-user-steps"></a>

A Splunk user needs to perform the following steps:
+ Get an appropriate token from the Splunk Administrator or create one themselves, if they have the permission. The audience for the token must be 'mcp'.

## Onboarding
<a name="onboarding"></a>

### Step 1: Connect
<a name="step-1-connect"></a>

Establish connection to your Splunk remote MCP endpoint with account access credentials

#### Configuration
<a name="configuration"></a>

1. Go to the **Capability Providers** page (accessible from the side navigation)

1. Find **Splunk** in the **Available** providers section under **Telemetry** and choose **Register**

1. Enter your Splunk MCP server details:
   + **Server Name** - Unique identifier (e.g., my-splunk-server)
   + **Endpoint URL** - Your Splunk MCP server endpoint:

`https://<YOUR_SPLUNK_DEPLOYMENT_NAME>.api.scs.splunk.com/<YOUR_SPLUNK_DEPLOYMENT_NAME>/mcp/v1/`
+ **Description** - Optional server description
+ **Token Name** - The name of the bearer token for authentication: `my-splunk-token`
+ **Token Value** The bearer token value for authentication

### Step 2: Enable
<a name="step-2-enable"></a>

Activate Splunk in a specific Agent space and configure appropriate scoping

#### Configuration
<a name="configuration"></a>

1. From the agent spaces page, select an agent space and press view details (if you have not yet created an agent space see [Creating an Agent Space](getting-started-with-aws-devops-agent-creating-an-agent-space.md))

1. Select the Capabilities tab

1. Scroll down to the Telemetry section

1. Press Add

1. Select Splunk

1. Next

1. Review and press Save

1. Copy the Webhook URL and API Key

### Step 3: Configure webhooks
<a name="step-3-configure-webhooks"></a>

Using the Webhook URL and API Key you can configure Splunk to send events to trigger an investigation, for example from an alarm.

Splunk webhooks use bearer token authentication. For the complete webhook request format, payload schema, and example code, see [Invoking DevOps Agent through Webhook](configuring-integrations-and-knowledge-invoking-devops-agent-through-webhook.md). Use the Version 2 (Bearer token authentication) examples, setting the `Authorization: Bearer <Token>` header with the API Key from Step 2.

Send webhooks with Splunk [https://help.splunk.com/en/splunk-enterprise/alert-and-respond/alerting-manual/9.4/configure-alert-actions/use-a-webhook-alert-action](https://help.splunk.com/en/splunk-enterprise/alert-and-respond/alerting-manual/9.4/configure-alert-actions/use-a-webhook-alert-action) (note select no authorization and instead use the custom header option)

### Learn more:
<a name="learn-more"></a>
+ Splunk's MCP Server Documentation: [https://help.splunk.com/en/splunk-cloud-platform/mcp-server-for-splunk-platform/about-mcp-server-for-splunk-platform ](https://help.splunk.com/en/splunk-cloud-platform/mcp-server-for-splunk-platform/about-mcp-server-for-splunk-platform)
+ Access requirements and limitations for the Splunk Cloud Platform REST API: [https://docs.splunk.com/Documentation/SplunkCloud/latest/RESTTUT/RESTandCloud ](https://docs.splunk.com/Documentation/SplunkCloud/latest/RESTTUT/RESTandCloud)
+ Manage authentication tokens in Splunk Cloud Platform: [https://help.splunk.com/en/splunk-cloud-platform/administer/manage-users-and-security/9.3.2411/authenticate-into-the-splunk-platform-with-tokens/manage-or-delete-authentication-tokens ](https://help.splunk.com/en/splunk-cloud-platform/administer/manage-users-and-security/9.3.2411/authenticate-into-the-splunk-platform-with-tokens/manage-or-delete-authentication-tokens)
+ Create and manage roles with Splunk Web: [https://docs.splunk.com/Documentation/SplunkCloud/latest/Security/Addandeditroles ](https://docs.splunk.com/Documentation/SplunkCloud/latest/Security/Addandeditroles)

## Removal
<a name="removal"></a>

The telemetry source is connected at two levels at the agent space level and at account level. To completely remove it you must first remove it from all agent spaces where it is used and then it can be unregistered.

### Step 1: Remove from agent space
<a name="step-1-remove-from-agent-space"></a>

1. From the agent spaces page, select an agent space and press view details

1. Select the Capabilities tab

1. Scroll down to the Telemetry section

1. Select Splunk

1. Press remove

### Step 2: Deregister from account
<a name="step-2-deregister-from-account"></a>

1. Go to the **Capability Providers** page (accessible from the side navigation)

1. Scroll to the **Currently registered** section. 

1. Check the agent space count is zero (if not repeat Step 1 above in your other agent spaces) 

1. Press Deregister next to Splunk