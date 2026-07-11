

# Setting Up External Identity Provider (IdP) Authentication
<a name="aws-devops-agent-security-setting-up-external-identity-provider-idp-authentication"></a>

External identity provider (IdP) authentication allows your organization to use an existing OIDC-compatible identity provider, such as Okta or Microsoft Entra ID, to manage user access to the AWS DevOps Agent Space web application. Users sign in with their corporate credentials directly through your IdP, without requiring AWS IAM Identity Center.

## Prerequisites
<a name="prerequisites"></a>

Before setting up external IdP authentication, ensure you have:
+ An OIDC-compatible identity provider (Okta or Microsoft Entra ID)
+ Administrator access to your identity provider
+ Administrator permissions to access AWS DevOps Agent console
+ An Agent Space configured or ready to create

## How it works
<a name="how-it-works"></a>

When you configure external IdP authentication:
+ Users navigate to the Agent Space web app URL
+ They are redirected to your identity provider's login page
+ After authenticating with their corporate credentials, they are redirected back to the web app
+ The web app exchanges the authentication token for short-lived AWS credentials scoped to the Agent Space

Sessions are valid for up to 8 hours. Credentials are automatically refreshed using OIDC refresh tokens without requiring users to re-authenticate.

## Configuring external IdP authentication
<a name="configuring-external-idp-authentication"></a>

### Step 1: Register an application in your identity provider
<a name="step-1-register-an-application-in-your-identity-provider"></a>

Choose your identity provider and follow the corresponding setup instructions.

#### Option A: Okta
<a name="option-a-okta"></a>

1. In the Okta Admin Console, navigate to **Applications** > **Applications** and choose **Create App Integration**

1. Select **OIDC - OpenID Connect** as the sign-in method and **Web Application** as the application type. Choose **Next**

1. Set a descriptive name for the application (for example, `AWS DevOps Agent`)

1. Under **Grant type**, ensure the following are checked:
   + **Authorization Code** (default)
   + **Refresh Token** — This is required for session refresh. If not enabled, users will be unable to maintain sessions.

**Note**  
** Okta does not enable the Refresh Token grant type by default. You must explicitly enable it.

1. Leave the **Sign-in redirect URIs** as the default value for now — you will update it after configuring the Agent Space

1. Under **Assignments**, assign the users or groups that should have access

1. Choose **Save**

1. On the application's **General** tab, note the following values:
   + **Client ID**
   + **Client secret** — Choose **Copy** to save this value securely

1. Note your **Okta domain** — this is your Issuer URL (for example, `https://dev-12345678.okta.com`).

**Note**  
** On the ** Sign On ** tab, verify the ** Issuer ** is set to ** Okta URL ** (not Dynamic). This ensures a stable issuer URL.

**Note**  
** Do not add a ** groups ** claim to the ID token in your authorization server's Claims tab. AWS DevOps Agent does not use group membership from your IdP.

#### Option B: Microsoft Entra ID
<a name="option-b-microsoft-entra-id"></a>

1. In the Azure portal, navigate to **Microsoft Entra ID** > **App registrations** > **New registration**

1. Set a descriptive name (for example, `AWS DevOps Agent`)

1. Under **Supported account types**, select the option appropriate for your organization (typically **Accounts in this organizational directory only**)

1. Leave the **Redirect URI** blank for now. Choose **Register**

1. On the application **Overview** page, note the following values:
   + **Application (client) ID** — used as the Client ID when configuring the Agent Space
   + **Directory (tenant) ID** — used to construct the Issuer URL

1. Navigate to **Certificates & secrets** > **New client secret**
   + Set a description and expiration period
   + Choose **Add** and copy the secret **Value** immediately — it will not be shown again

1. The Issuer URL for Entra ID follows this format. Replace `{tenant-id}` with your Directory (tenant) ID from step 5:
   + `https://login.microsoftonline.com/{tenant-id}/v2.0`

**Note**  
** Do not enable the ** groups ** optional claim in ** Token configuration **. AWS DevOps Agent does not use group membership from your IdP.

### Step 2: Enable the Operator App with IdP authentication
<a name="step-2-enable-the-operator-app-with-idp-authentication"></a>

1. In the AWS DevOps Agent console, select your Agent Space

1. Go to the **Access** tab

1. Under **User access**, choose **External identity provider**

1. In the configuration form, configure the following:
   + **Identity Provider** — Select your identity provider (Okta or Microsoft Entra ID)
   + **Issuer URL** — The OIDC issuer URL from your identity provider
   + **Client ID** — The client ID from the OIDC application you created
   + **Client Secret** — The client secret from your OIDC application

1. Under **Identity Provider Application Role Name**, choose one of three options:
   + **Auto-create a new DevOps Agent role** (recommended) — Creates a new service role with appropriate permissions
   + **Assign an existing role** — Use an existing IAM role that you've already created
   + **Create a new DevOps Agent role using a policy template** — Use the provided details to create your own role in the IAM Console

1. Review the **Callback URL** warning alert displayed at the bottom of the form. Copy this URL — you will need to add it to your identity provider's allowed redirect URIs before users can sign in.

1. Choose **Connect**

After choosing **Connect**, the console displays the **External Identity Provider Configuration** with the following details:
+ **Provider** — The identity provider you selected
+ **Issuer URL** — The configured OIDC issuer URL
+ **Client ID** — The configured client ID
+ **IAM Role ARN** — The IAM role used for user access
+ **Callback URL** — Configure this URL in your identity provider as an allowed redirect URI
+ **Login URL** — Use this URL to access the web app through your identity provider

### Step 3: Add the callback URL to your identity provider
<a name="step-3-add-the-callback-url-to-your-identity-provider"></a>

#### Okta
<a name="okta"></a>

1. In the Okta Admin Console, navigate to your application's **General** tab

1. Under **Login**, choose **Edit**

1. Add the callback URL as a **Sign-in redirect URI**:
   + `https://{agentSpaceId}.aidevops.global.app.aws/authorizer/idp/callback`

1. (Optional) Set the **Initiate login URI** to enable IdP-initiated login from the Okta dashboard:
   + `https://{agentSpaceId}.aidevops.global.app.aws/authorizer/idp/login`

1. (Recommended) Add a **Sign-out redirect URI** to redirect users back to the web app after logout. Without this, users may see an error page when logging out:
   + `https://{agentSpaceId}.aidevops.global.app.aws/authorizer/welcome`

1. Choose **Save**

#### Microsoft Entra ID
<a name="microsoft-entra-id"></a>

1. In the Azure portal, navigate to your application's **Authentication** page

1. Under **Platform configurations**, choose **Add a platform** > **Web**

1. Enter the callback URL as the **Redirect URI**:
   + `https://{agentSpaceId}.aidevops.global.app.aws/authorizer/idp/callback`

1. (Optional) Add a sign-out redirect URI to redirect users back to the web app after logout:
   + `https://{agentSpaceId}.aidevops.global.app.aws/authorizer/welcome`

1. Choose **Configure**

### Step 4: Verify the configuration
<a name="step-4-verify-the-configuration"></a>

1. Navigate to the **Login URL** shown in the console:
   + `https://{agentSpaceId}.aidevops.global.app.aws/authorizer/idp/login`

1. You should be redirected to your identity provider's login page

1. Sign in with your corporate credentials

1. After successful authentication, you are redirected back to the Agent Space web app

## Updating IdP configuration
<a name="updating-idp-configuration"></a>

You can rotate the client secret without disconnecting:

1. In the AWS DevOps Agent console, select your Agent Space

1. Go to the **Access** tab

1. Under **External Identity Provider Configuration**, choose **Rotate client secret**

1. Enter the new **Client Secret**

1. Choose **Save**

To change any other IdP configuration field (such as Issuer URL, Client ID, or identity provider), you must disconnect the existing IdP and configure a new one.

## How users access the Agent Space web app
<a name="how-users-access-the-agent-space-web-app"></a>

After configuring external IdP authentication:
+ Share the Agent Space web app URL with authorized users
+ When users navigate to the URL, they are redirected to your identity provider's login page
+ After entering their credentials (and completing MFA if configured by your IdP), they are redirected back to the Agent Space web app
+ Sessions refresh automatically — see [Session management](#session-management) for details

## Session management
<a name="session-management"></a>

External IdP sessions for the Agent Space web app have the following characteristics:
+ **Session duration** — Browser sessions last up to 8 hours. This is not configurable in AWS DevOps Agent. If your IdP's session lifetime exceeds 8 hours, users may be re-authenticated automatically on their next visit without entering credentials. Configure your IdP's session and token lifetimes according to your organization's security requirements.
+ **Credential refresh** — Sessions are automatically refreshed using OIDC refresh tokens without requiring users to re-authenticate
+ **Multi-factor authentication** — Supported when configured in your identity provider. The IdP handles MFA during login — no additional configuration is needed in AWS DevOps Agent

### Logout behavior
<a name="logout-behavior"></a>

When a user clicks **Logout** in the web app:

1. All session cookies are cleared immediately

1. The user is redirected to the identity provider's OIDC logout endpoint to terminate the SSO session

1. If a sign-out redirect URI is configured, the user is redirected back to the web app welcome page

### Revoking user access
<a name="revoking-user-access"></a>

To immediately revoke a user's access, you can revoke their sessions directly in your identity provider's admin portal:
+ **Okta** — In the Okta Admin Console, navigate to **Directory** > **People**, select the user, choose **More Actions** > **Clear User Sessions**
+ **Microsoft Entra ID** — In the Azure portal, navigate to **Users**, select the user, and choose **Revoke sessions**

## Security considerations
<a name="security-considerations"></a>

**Client secret storage** — The client secret you provide during setup is encrypted using your customer-managed KMS key if you provided one when creating the Agent Space, or a service-owned key otherwise. It is never returned in API responses or displayed in the console after initial configuration.

**Client secret rotation** — Entra client secrets have a configurable expiration. Set a reminder to rotate the secret before it expires using the **Rotate client secret** option in the AWS DevOps Agent console. If the secret expires, users will be unable to log in until it is rotated.

**Token lifetime management** — The lifetime of tokens (access tokens, refresh tokens) issued by your identity provider is controlled by your IdP's configuration. We recommend configuring appropriate token lifetimes in your IdP:
+ **Okta** — Configure token lifetimes under **Security** > **API** > **Authorization Servers** > **Access Policies**
+ **Microsoft Entra ID** — Configure token lifetimes using [token lifetime policies](https://learn.microsoft.com/en-us/entra/identity-platform/configurable-token-lifetimes)

**Groups claim** — Do not enable the groups claim in your identity provider's token configuration. AWS DevOps Agent does not currently use group membership from your IdP.

**User identifier** — AWS DevOps Agent uses a provider-specific claim to uniquely identify users:
+ **Okta** — Uses the `sub` claim from the ID token
+ **Microsoft Entra ID** — Uses the `oid` (object identifier) claim from the ID token

These identifiers are immutable and appear in CloudTrail logs for audit purposes.

## Disconnecting external IdP
<a name="disconnecting-external-idp"></a>

1. In the AWS DevOps Agent console, select your Agent Space

1. Go to the **Access** tab

1. Under **User access**, choose **Disconnect**

1. Review the impacts listed in the confirmation dialog and confirm

Disconnecting will:
+ Remove the IdP configuration from the Agent Space
+ Prevent users from logging in through the external identity provider
+ Remove individual chat and artifact history associated with IdP user accounts

Active user sessions will continue until they expire or the next credential refresh fails.

## Troubleshooting
<a name="troubleshooting"></a>
+ **Redirect to IdP fails** — Verify the Issuer URL matches your IdP's OIDC discovery endpoint. For Okta, ensure the **Issuer** is set to **Okta URL** (not **Dynamic**) on the **Sign On** tab. For Entra, use the format `https://login.microsoftonline.com/{tenant-id}/v2.0`.
+ **Access denied or policy error (Okta)** — Verify the user or their group is assigned to the application under **Assignments**. Check **Sign On** > **Sign On Policy** rules.
+ **IdP configuration error after login** — Your identity provider did not return a refresh token. Ensure the `offline_access` scope and refresh token grant type are enabled:
  + **Okta** — Go to your application's **General** tab and enable the **Refresh Token** checkbox under **Grant type**
  + **Entra** — Go to **API permissions** and ensure `offline_access` is listed under delegated permissions
+ **Authentication succeeds but web app shows error** — Verify the redirect URI in your IdP exactly matches the **Callback URL** shown in the AWS DevOps Agent console.
+ **Authentication failures** — If the **groups** optional claim is enabled in your IdP, disable it. AWS DevOps Agent does not use group claims.
+ **Login fails after IdP authentication** — For Entra, verify `requestedAccessTokenVersion` is not set to `null` in the application **Manifest**. For Okta, verify the **Issuer URL** is correct.
+ **Error page after choosing Logout (Okta)** — If you see a `post_logout_redirect_uri` error after logging out, add `https://{agentSpaceId}.aidevops.global.app.aws/authorizer/welcome` as a **Sign-out redirect URI** in your Okta application's **General** tab.
+ **Users stay on identity provider page after logout (Entra)** — To redirect users back to the web app after logout, add `https://{agentSpaceId}.aidevops.global.app.aws/authorizer/welcome` as a **Redirect URI** in your Entra application's **Authentication** page.