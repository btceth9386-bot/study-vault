

# Connecting Grafana
<a name="connecting-telemetry-sources-connecting-grafana"></a>

Grafana integration enables AWS DevOps Agent to query metrics, dashboards, and alerting data from your Grafana instance during incident investigations. This integration follows a two-step process: account-level registration of Grafana, followed by connecting it to individual Agent Spaces.

To improve security, the Grafana integration only enables read-only tools. Write tools are disabled and cannot be enabled. This means the agent can query and read data from your Grafana instance but cannot create, modify, or delete any Grafana resources such as dashboards, alerts, or annotations. For more information, see [Security in AWS DevOps Agent](https://docs.aws.amazon.com/devopsagent/latest/userguide/aws-devops-agent-security.html).

## Grafana requirements
<a name="grafana-requirements"></a>

Before connecting Grafana, ensure you have:
+ Grafana version 9.0 or later. Some features, particularly datasource-related operations, may not work correctly with earlier versions due to missing API endpoints.
+ A Grafana instance accessible over HTTPS. Both public and private network endpoints are supported. With private network connectivity, your Grafana instance can be hosted inside a VPC with no public internet access. For details, see [Connecting to privately hosted tools](configuring-integrations-and-knowledge-connecting-to-privately-hosted-tools.md).
+ A Grafana service account with an access token that has appropriate read permissions

## Registering Grafana (account-level)
<a name="registering-grafana-account-level"></a>

Grafana is registered at the AWS account level and shared among all Agent Spaces in that account.

### Step 1: Configure Grafana
<a name="step-1-configure-grafana"></a>

1. Sign in to the AWS Management Console

1. Navigate to the AWS DevOps Agent console

1. Go to the **Capability Providers** page (accessible from the side navigation)

1. Find **Grafana** in the **Available** providers section under **Telemetry** and choose **Register**

1. On the **Configure Grafana** page, enter the following information:
   + **Service Name** (required) – Enter a descriptive name for your Grafana server using alphanumeric characters, hyphens, and underscores only. For example, `my-grafana-server`.
   + **Grafana URL** (required) – Enter the full HTTPS URL of your Grafana instance. For example, `https://myinstance.grafana.net`.
   + **Service Account Access Token** (required) – Enter a Grafana service account access token. Tokens typically start with `glsa_`. To create a service account token, navigate to your Grafana instance, go to **Administration > Service accounts**, create a service account with Viewer role, and generate a token.
   + **Description** (optional) – Add a description to help identify the server's purpose. For example, `Production Grafana server for monitoring`.

1. (Optional) Add AWS tags to the registration for organizational purposes.

1. Choose **Next**

### Step 2: Review and submit Grafana registration
<a name="step-2-review-and-submit-grafana-registration"></a>

1. Review all the Grafana configuration details

1. Choose **Submit** to complete the registration

1. Upon successful registration, Grafana appears in the **Currently registered** section of the Capability Providers page

## Adding Grafana to an Agent Space
<a name="adding-grafana-to-an-agent-space"></a>

After registering Grafana at the account level, you can connect it to individual Agent Spaces:

1. In the AWS DevOps Agent console, select your Agent Space

1. Go to the **Capabilities** tab

1. In the **Telemetry** section, choose **Add**

1. Select **Grafana** from the list of available providers

1. Choose **Save**

## Configuring Grafana alert webhooks
<a name="configuring-grafana-alert-webhooks"></a>

You can configure Grafana to automatically trigger AWS DevOps Agent investigations when alerts fire by sending webhooks through Grafana contact points. For details on webhook authentication methods and credential management, see [Invoking DevOps Agent through Webhook](configuring-integrations-and-knowledge-invoking-devops-agent-through-webhook.md).

### Step 1: Create a custom notification template
<a name="step-1-create-a-custom-notification-template"></a>

In your Grafana instance, navigate to **Alerting > Contact points > Notification templates** and create a new template with the following content:

```
{{ define "devops-agent-payload" }}
{
  "eventType": "incident",
  "incidentId": "{{ (index .Alerts 0).Labels.alertname }}-{{ (index .Alerts 0).Fingerprint }}",
  "action": "{{ if eq .Status "resolved" }}resolved{{ else }}created{{ end }}",
  "priority": "{{ if eq .Status "resolved" }}MEDIUM{{ else }}HIGH{{ end }}",
  "title": "{{ (index .Alerts 0).Labels.alertname }}",
  "description": "{{ (index .Alerts 0).Annotations.summary }}",
  "service": "{{ if (index .Alerts 0).Labels.job }}{{ (index .Alerts 0).Labels.job }}{{ else }}grafana{{ end }}",
  "timestamp": "{{ (index .Alerts 0).StartsAt }}",
  "data": {
    "metadata": {
      {{ range $k, $v := (index .Alerts 0).Labels }}
      "{{ $k }}": "{{ $v }}",
      {{ end }}
      "_source": "grafana"
    }
  }
}
{{ end }}
```

This template formats Grafana alerts into the webhook payload structure expected by AWS DevOps Agent. It maps alert labels, annotations, and status into the appropriate fields, and includes all alert labels as metadata.

**Note:** This template processes only the first alert in a group. Grafana groups multiple firing alerts into a single notification by default. To ensure each alert is sent individually, configure your notification policies to group by `alertname`. Additionally, this template does not escape special JSON characters in label values or annotations. Ensure that alert labels and the `summary` annotation do not contain characters such as double quotes or newlines, which would produce invalid JSON.

### Step 2: Create a webhook contact point
<a name="step-2-create-a-webhook-contact-point"></a>

1. In Grafana, navigate to **Alerting > Contact points** and choose **Add contact point**

1. Select **Webhook** as the integration type

1. Set the **URL** to your AWS DevOps Agent webhook endpoint

1. Under **Optional Webhook settings**, configure the authentication headers based on your webhook type. See [Webhook authentication methods](configuring-integrations-and-knowledge-invoking-devops-agent-through-webhook.md) for details.

1. Set the **Custom Payload** field to use your custom template: `{{ template "devops-agent-payload" . }}`

1. Choose **Save contact point**

### Step 3: Assign the contact point to a notification policy
<a name="step-3-assign-the-contact-point-to-a-notification-policy"></a>

1. Navigate to **Alerting > Notification policies**

1. Edit an existing policy or create a new one

1. Set the contact point to the webhook contact point you created

1. Choose **Save policy**

When a matching alert fires, Grafana will send the formatted payload to AWS DevOps Agent, which will start an investigation automatically.

## Limitations
<a name="limitations"></a>
+ **ClickHouse data source tools** – ClickHouse data source tools are not currently supported.
+ **Proactive incident prevention** – [Proactive incident prevention](production-operations-proactive-incident-prevention.md) does not currently use Grafana tools. Support is planned for a future release.

### Amazon Managed Grafana considerations
<a name="amazon-managed-grafana-considerations"></a>

If you are using [Amazon Managed Grafana](https://aws.amazon.com/grafana/) (AMG), be aware of the following limitations:
+ **Webhook contact points are not supported** – AMG does not currently support webhook contact points in its alerting configuration. You cannot use AMG to send alert webhooks directly to AWS DevOps Agent. For details, see [Alerting contact points in Amazon Managed Grafana](https://docs.aws.amazon.com/grafana/latest/userguide/v9-alerting-explore-contacts.html).
+ **Service account token expiration** – AMG service account tokens have a maximum expiration of 30 days. You will need to rotate tokens and update your Grafana registration in AWS DevOps Agent before they expire. See [Managing Grafana connections](#managing-grafana-connections) for how to update credentials. For details on AMG token limits, see [Service accounts in Amazon Managed Grafana](https://docs.aws.amazon.com/grafana/latest/userguide/service-accounts.html).

## Managing Grafana connections
<a name="managing-grafana-connections"></a>
+ **Updating credentials** – If your service account token expires or needs to be updated, deregister Grafana from the Capability Providers page and re-register with the new token.
+ **Viewing connected instances** – In the AWS DevOps Agent console, select your Agent Space and go to the Capabilities tab to view connected telemetry sources.
+ **Removing Grafana** – To disconnect Grafana from an Agent Space, select it in the Telemetry section and choose **Remove**. To completely remove the registration, remove it from all Agent Spaces first, then deregister from the Capability Providers page.