## Purpose and Scope

This section provides an overview of MCP's authorization and security framework, which enables secure access control for HTTP-based MCP servers. Authorization in MCP is **optional** but becomes essential when MCP servers need to protect resources, validate client identity, or enforce access policies. For implementation details of the OAuth 2.1 flow, see [OAuth 2.1 Authorization Framework](#3.1). For attack vectors and defensive measures, see [Security Best Practices](#3.2).

Authorization is designed exclusively for HTTP-based transports. Implementations using the stdio transport should retrieve credentials from the environment rather than following this specification.

Sources: [docs/specification/draft/basic/authorization.mdx:9-25]()

## When Authorization is Required

Authorization **MUST** be implemented when:

- The MCP server is accessed over HTTP/HTTPS transport
- The server handles user-specific or sensitive data
- Access control policies need enforcement
- Audit trails of client actions are required
- Rate limiting or quota management is needed per client

Authorization is **NOT** required for:

- stdio transport implementations (use environment-based credentials)
- Local, single-user deployments
- Public, read-only MCP servers with no access restrictions

The following table summarizes transport-specific requirements:

| Transport Type | Authorization Requirement | Credential Source |
|----------------|---------------------------|-------------------|
| HTTP/HTTPS | **SHOULD** follow OAuth 2.1 | Authorization Server |
| stdio | **SHOULD NOT** use OAuth | Environment variables |
| Alternative transports | **MUST** follow protocol-appropriate security | Transport-specific |

Sources: [docs/specification/draft/basic/authorization.mdx:17-25](), [docs/docs/tutorials/security/authorization.mdx:10-27]()

## Architecture Overview

MCP authorization implements a three-party OAuth 2.1 architecture with distinct roles for clients, resource servers, and authorization servers.

```mermaid
graph TB
    subgraph "MCP Client"
        Client["MCP Client<br/>(OAuth 2.1 Client)"]
    end
    
    subgraph "MCP Server"
        ResourceServer["MCP Server<br/>(Resource Server)<br/>Validates Bearer tokens"]
        PRM["Protected Resource Metadata<br/>/.well-known/oauth-protected-resource"]
    end
    
    subgraph "Authorization Server"
        AuthServer["Authorization Server<br/>Issues access tokens"]
        ASMetadata["Authorization Server Metadata<br/>/.well-known/oauth-authorization-server"]
        AuthEndpoint["/authorize<br/>User consent"]
        TokenEndpoint["/token<br/>Token exchange"]
        IntrospectEndpoint["/token/introspect<br/>Token validation"]
    end
    
    Client -->|"1. MCP Request<br/>(no token)"| ResourceServer
    ResourceServer -->|"2. 401 Unauthorized<br/>WWW-Authenticate header"| Client
    Client -->|"3. Fetch metadata"| PRM
    PRM -->|"4. Points to"| ASMetadata
    Client -->|"5. OAuth flow"| AuthEndpoint
    AuthEndpoint -->|"6. Authorization code"| Client
    Client -->|"7. Exchange code"| TokenEndpoint
    TokenEndpoint -->|"8. Access token"| Client
    Client -->|"9. Bearer token"| ResourceServer
    ResourceServer -->|"10. Validate"| IntrospectEndpoint
```

**Architecture: Three-Party OAuth 2.1 Model**

### Roles

**MCP Client** (OAuth 2.1 client): Initiates requests to MCP servers and obtains access tokens on behalf of resource owners. Acts as a public client supporting PKCE for security.

**MCP Server** (OAuth 2.1 resource server): Protects MCP resources and validates Bearer tokens. Implements Protected Resource Metadata (RFC 9728) to advertise its authorization requirements.

**Authorization Server**: Issues access tokens after user authentication and consent. May be co-located with the MCP server or operate as a separate service. Implements Authorization Server Metadata (RFC 8414) for discovery.

Sources: [docs/specification/draft/basic/authorization.mdx:42-52](), [docs/specification/draft/basic/authorization.mdx:148-196]()

## Standards Compliance

MCP authorization is based on the following specifications, implementing a subset of features to ensure security while maintaining simplicity:

| Specification | RFC/Draft | Role in MCP |
|---------------|-----------|-------------|
| OAuth 2.1 | draft-ietf-oauth-v2-1-13 | Core authorization framework |
| Authorization Server Metadata | RFC 8414 | Endpoint discovery |
| Protected Resource Metadata | RFC 9728 | Resource server metadata |
| Dynamic Client Registration | RFC 7591 | Automatic client registration |
| OAuth Client ID Metadata Documents | draft-ietf-oauth-client-id-metadata-document-00 | URL-based client identity |
| Resource Indicators | RFC 8707 | Token audience binding |

Authorization servers **MUST** implement OAuth 2.1 with security measures for both confidential and public clients. MCP servers **MUST** implement Protected Resource Metadata. Both authorization servers and clients **SHOULD** support Client ID Metadata Documents for simplified registration.

Sources: [docs/specification/draft/basic/authorization.mdx:27-40](), [docs/specification/draft/basic/authorization.mdx:56-73]()

## Discovery Flow

MCP implements a discovery chain that allows clients to dynamically locate authorization servers and understand their capabilities without pre-configuration.

```mermaid
sequenceDiagram
    participant Client as "MCP Client"
    participant MCP as "MCP Server<br/>(Resource Server)"
    participant AS as "Authorization Server"

    Note over Client,AS: Discovery Phase
    
    Client->>MCP: "MCP request (no token)"
    MCP-->>Client: "401 Unauthorized<br/>WWW-Authenticate: Bearer<br/>resource_metadata=<url>"
    
    alt Header includes resource_metadata URL
        Client->>MCP: "GET resource_metadata URL"
    else Fallback to well-known URI
        Client->>MCP: "GET /.well-known/oauth-protected-resource/mcp"
        alt Not found
            Client->>MCP: "GET /.well-known/oauth-protected-resource"
        end
    end
    
    MCP-->>Client: "Protected Resource Metadata<br/>{authorization_servers: [...],<br/>scopes_supported: [...]}"
    
    Note over Client: Extract authorization_servers[0]
    
    Client->>AS: "GET /.well-known/oauth-authorization-server"
    alt OAuth 2.0 metadata found
        AS-->>Client: "Authorization Server Metadata"
    else Try OpenID Connect
        Client->>AS: "GET /.well-known/openid-configuration"
        AS-->>Client: "OIDC Discovery metadata"
    end
    
    Note over Client,AS: OAuth 2.1 Flow Begins
```

**Discovery: Protected Resource and Authorization Server Metadata**

### Discovery Mechanisms

**Protected Resource Metadata Discovery** (RFC 9728):

MCP servers **MUST** implement one of:
1. **WWW-Authenticate Header**: Include `resource_metadata` parameter in 401 responses
2. **Well-Known URI**: Serve metadata at `/.well-known/oauth-protected-resource` or path-specific variant

The `WWW-Authenticate` header **SHOULD** include a `scope` parameter indicating required scopes:

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource",
                         scope="mcp:tools"
```

**Authorization Server Metadata Discovery**:

Clients **MUST** support both OAuth 2.0 Authorization Server Metadata (RFC 8414) and OpenID Connect Discovery 1.0 endpoints, attempting them in priority order based on the issuer URL structure.

For issuer URLs with path components (e.g., `https://auth.example.com/tenant1`):
1. OAuth: `https://auth.example.com/.well-known/oauth-authorization-server/tenant1`
2. OIDC (insertion): `https://auth.example.com/.well-known/openid-configuration/tenant1`
3. OIDC (appending): `https://auth.example.com/tenant1/.well-known/openid-configuration`

Sources: [docs/specification/draft/basic/authorization.mdx:74-148](), [docs/specification/draft/basic/authorization.mdx:132-147]()

## Client Registration Approaches

MCP supports three client registration mechanisms to accommodate different deployment scenarios. For detailed implementation guidance, see [Client Registration Methods](#3.3).

```mermaid
flowchart TD
    Start["Client needs authorization"] --> Check1{"Pre-registered<br/>credentials<br/>available?"}
    
    Check1 -->|"Yes"| PreReg["Use pre-registered<br/>client_id + secret"]
    Check1 -->|"No"| Check2{"Authorization Server<br/>supports CIMD?<br/>(client_id_metadata_document_supported)"}
    
    Check2 -->|"Yes"| CIMD["Use Client ID Metadata Documents<br/>client_id = https://app.example.com/metadata.json"]
    Check2 -->|"No"| Check3{"Authorization Server<br/>has registration_endpoint?"}
    
    Check3 -->|"Yes"| DCR["Use Dynamic Client Registration<br/>POST /register"]
    Check3 -->|"No"| Manual["Manual entry required<br/>User provides credentials"]
    
    PreReg --> Flow["Continue OAuth flow"]
    CIMD --> Flow
    DCR --> Flow
    Manual --> Flow
```

**Client Registration: Priority Order**

### Registration Priority

Clients supporting multiple registration options **SHOULD** follow this priority:

1. **Pre-registration** (highest priority): Use existing client credentials if available
2. **Client ID Metadata Documents**: Use URL-based client_id if `client_id_metadata_document_supported: true`
3. **Dynamic Client Registration**: Fall back to RFC 7591 if `registration_endpoint` present
4. **Manual entry** (lowest priority): Prompt user for credentials

**Client ID Metadata Documents** (recommended): Simplifies the unbounded clients/servers problem in MCP by allowing clients to use HTTPS URLs as identifiers, pointing to self-hosted metadata:

```json
{
  "client_id": "https://app.example.com/oauth/client-metadata.json",
  "client_name": "Example MCP Client",
  "redirect_uris": ["http://127.0.0.1:3000/callback"],
  "grant_types": ["authorization_code"],
  "token_endpoint_auth_method": "none"
}
```

Sources: [docs/specification/draft/basic/authorization.mdx:199-317](), [docs/specification/draft/basic/authorization.mdx:245-260]()

## Authorization Flow Overview

The complete authorization flow integrates discovery, registration, and token acquisition. The following sequence shows how all components interact:

```mermaid
sequenceDiagram
    participant Browser as "User-Agent"
    participant Client as "MCP Client"
    participant MCP as "MCP Server"
    participant AS as "Authorization Server"

    Note over Client,AS: Phase 1: Discovery
    Client->>MCP: "MCP request"
    MCP-->>Client: "401 + WWW-Authenticate"
    Client->>MCP: "GET resource metadata"
    MCP-->>Client: "authorization_servers, scopes_supported"
    Client->>AS: "GET authorization server metadata"
    AS-->>Client: "endpoints, capabilities"

    Note over Client,AS: Phase 2: Client Registration
    alt Client ID Metadata Documents
        Note over Client: "Use HTTPS URL as client_id"
        AS->>Client: "Fetch metadata from client_id URL"
        Client-->>AS: "JSON metadata document"
    else Dynamic Client Registration
        Client->>AS: "POST /register"
        AS-->>Client: "client_id, client_secret"
    else Pre-registered
        Note over Client: "Use existing client_id"
    end

    Note over Client,AS: Phase 3: Authorization
    Client->>Client: "Generate PKCE params<br/>(code_verifier, code_challenge)"
    Client->>Browser: "Open /authorize?client_id=...&resource=...&code_challenge=..."
    Browser->>AS: "Authorization request with resource parameter"
    AS->>Browser: "User authentication & consent UI"
    Browser->>AS: "User approves"
    AS->>Browser: "Redirect with authorization code"
    Browser->>Client: "Authorization code callback"

    Note over Client,AS: Phase 4: Token Exchange
    Client->>AS: "POST /token<br/>code, code_verifier, resource"
    AS-->>Client: "access_token, refresh_token, expires_in"

    Note over Client,MCP: Phase 5: Authenticated Requests
    Client->>MCP: "MCP request<br/>Authorization: Bearer <access_token>"
    MCP->>AS: "Validate token (introspection or JWT)"
    AS-->>MCP: "Token valid, scopes, audience"
    MCP-->>Client: "MCP response"
```

**Authorization Flow: Complete OAuth 2.1 Sequence**

### Key Flow Elements

**PKCE (Proof Key for Code Exchange)**: All clients **MUST** implement PKCE per OAuth 2.1 requirements. The client generates a `code_verifier` (random string) and `code_challenge` (SHA-256 hash), sending the challenge during authorization and the verifier during token exchange.

**Resource Parameter**: Clients **MUST** include the `resource` parameter (RFC 8707) in authorization and token requests, set to the canonical URI of the MCP server. This binds tokens to their intended audience, preventing token replay attacks.

Example: For MCP server at `https://mcp.example.com/api`, the resource parameter is:
```
resource=https%3A%2F%2Fmcp.example.com%2Fapi
```

**Bearer Token Usage**: Access tokens **MUST** be sent in the `Authorization` header:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

Tokens **MUST NOT** be included in URI query strings.

Sources: [docs/specification/draft/basic/authorization.mdx:352-400](), [docs/specification/draft/basic/authorization.mdx:404-441](), [docs/specification/draft/basic/authorization.mdx:443-487]()

## Scope Selection and Elevation

MCP implements a progressive scope model following the principle of least privilege. For detailed scope management strategies, see [Token Management and Scope Strategy](#3.4).

### Initial Scope Selection

Clients **SHOULD** follow this priority for initial authorization:

1. Use `scope` parameter from 401 `WWW-Authenticate` header (if provided)
2. Use all scopes from `scopes_supported` in Protected Resource Metadata (if defined)
3. Omit `scope` parameter if neither is available

This approach minimizes user friction while allowing authorization servers and users to determine appropriate permissions during consent.

### Incremental Scope Elevation

When runtime operations require additional permissions, servers respond with:

```http
HTTP/1.1 403 Forbidden
WWW-Authenticate: Bearer error="insufficient_scope",
                         scope="files:read files:write user:profile",
                         resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource"
```

Clients **SHOULD** initiate a step-up authorization flow requesting the additional scopes, retry the operation with the new token, and implement retry limits to avoid repeated failures.

Sources: [docs/specification/draft/basic/authorization.mdx:336-351](), [docs/specification/draft/basic/authorization.mdx:498-558]()

## Security Principles

MCP authorization enforces multiple security layers. For comprehensive attack scenarios and mitigations, see [Security Best Practices](#3.2).

### Core Security Requirements

**Token Audience Validation**: MCP servers **MUST** validate that tokens were issued specifically for them (audience claim). Clients **MUST** include the `resource` parameter in all authorization and token requests. Token passthrough is **explicitly forbidden** - servers **MUST NOT** accept or forward tokens issued for other resources.

**Communication Security**: All authorization server endpoints **MUST** use HTTPS. Redirect URIs **MUST** be either `localhost` or HTTPS.

**Authorization Code Protection**: All clients **MUST** implement PKCE (OAuth 2.1 requirement) to prevent authorization code interception attacks.

**Token Storage**: Clients and servers **MUST** implement secure token storage following OAuth best practices. Authorization servers **SHOULD** issue short-lived access tokens and **MUST** rotate refresh tokens for public clients.

**Session Security**: MCP servers implementing authorization **MUST** verify all inbound requests with tokens, not sessions. Session IDs **MUST** be cryptographically secure and non-deterministic.

Sources: [docs/specification/draft/basic/authorization.mdx:560-598](), [docs/specification/draft/basic/security_best_practices.mdx:246-332]()

## Implementation Status and SDK Support

Authorization support varies across the MCP ecosystem. The client feature matrix shows current adoption:

| Feature Category | Adoption Rate | Representative Clients |
|------------------|---------------|------------------------|
| HTTP Transport + Auth | ~20% | Claude.ai, ChatGPT, Postman |
| Tools Only | ~95% | Most clients (60+ implementations) |
| Full Auth Support (8/8 features) | ~3% | VS Code GitHub Copilot, fast-agent, VT Code |

### SDK Support

**TypeScript SDK**: Provides built-in authorization middleware and metadata routers:
- `mcpAuthMetadataRouter()` - Serves Protected Resource Metadata endpoints
- `requireBearerAuth()` - Validates Bearer tokens and enforces scopes
- `OAuthMetadata` - Type definitions for authorization server metadata
- `checkResourceAllowed()` - Validates resource parameter audience binding

Example server setup (TypeScript):
```typescript
import { mcpAuthMetadataRouter, requireBearerAuth } from '@modelcontextprotocol/sdk/server/auth';

app.use(mcpAuthMetadataRouter({
  oauthMetadata,
  resourceServerUrl: mcpServerUrl,
  scopesSupported: ["mcp:tools"],
  resourceName: "MCP Server"
}));

const authMiddleware = requireBearerAuth({
  verifier: tokenVerifier,
  requiredScopes: []
});
```

**Python SDK (FastMCP)**: Authorization configuration managed through `Config` class with built-in token validation via introspection or JWT verification.

Sources: [docs/clients.mdx:14-220](), [docs/docs/tutorials/security/authorization.mdx:286-614]()

## Related Documentation

- **[OAuth 2.1 Authorization Framework](#3.1)**: Detailed OAuth implementation guide including authorization code flow, PKCE, and token exchange
- **[Security Best Practices](#3.2)**: Attack vectors and mitigations including confused deputy, token passthrough, session hijacking, and local server compromise
- **[Client Registration Methods](#3.3)**: In-depth coverage of pre-registration, Client ID Metadata Documents, and Dynamic Client Registration
- **[Token Management and Scope Strategy](#3.4)**: Token validation, audience verification, scope selection algorithms, and refresh token handling

Sources: [README.md:1-29](), [docs/specification/versioning.mdx:1-39]()

# OAuth 2.1 Authorization Framework




## Purpose and Scope

This document describes MCP's OAuth 2.1-based authorization framework for HTTP-based transports. It covers authorization server discovery, dynamic client registration, token management, and security requirements for implementing protected MCP servers and clients.

Authorization is **OPTIONAL** for MCP implementations. When implemented, this specification applies **ONLY** to HTTP-based transports. For STDIO transports, credentials should be retrieved from the environment. For alternative transports, follow established security best practices for that protocol.

For security best practices and attack mitigations, see [Security Best Practices](#3.2). For implementation tutorials, see [Authorization Implementation Guide](#3.3). For token validation details, see [Token Validation and Scope Management](#3.4).

**Sources:** [docs/specification/draft/basic/authorization.mdx:1-26]()

## Standards and Specifications

MCP's authorization framework implements a selected subset of OAuth 2.1 and related specifications to ensure security while maintaining simplicity:

| Specification | RFC/Draft | Purpose |
|---------------|-----------|---------|
| OAuth 2.1 | draft-ietf-oauth-v2-1-13 | Core authorization protocol |
| Authorization Server Metadata | RFC8414 | Discovery of authorization server capabilities |
| Dynamic Client Registration | RFC7591 | Automatic client registration without user interaction |
| Protected Resource Metadata | RFC9728 | Discovery of resource server authorization requirements |
| Resource Indicators | RFC8707 | Token audience binding to prevent misuse |
| Bearer Token Usage | RFC6750 | Access token transmission in HTTP requests |
| Token Introspection | RFC7662 | Token validation by resource servers |

**Sources:** [docs/specification/draft/basic/authorization.mdx:27-39]()

## Roles and Architecture

### OAuth 2.1 Role Mapping

```mermaid
graph TB
    subgraph "OAuth 2.1 Roles in MCP Context"
        RC["Resource Owner<br/>(End User)"]
        
        subgraph "MCP Client Role"
            MC["MCP Client<br/>OAuth 2.1 Client<br/>Makes protected requests"]
        end
        
        subgraph "MCP Server Role"
            MS["MCP Server<br/>OAuth 2.1 Resource Server<br/>Validates access tokens"]
        end
        
        subgraph "Authorization Server Role"
            AS["Authorization Server<br/>Issues access tokens<br/>May be separate service"]
        end
    end
    
    RC -->|"Authorizes"| AS
    MC -->|"1. Requests without token"| MS
    MS -->|"2. HTTP 401 + WWW-Authenticate"| MC
    MC -->|"3. Initiates OAuth flow"| AS
    AS -->|"4. Returns access token"| MC
    MC -->|"5. Protected requests with Bearer token"| MS
    MS -->|"6. Validates token audience"| AS
```

**Roles:**
- **MCP Server**: Acts as OAuth 2.1 resource server, validates access tokens, requires tokens to be specifically issued for its URI
- **MCP Client**: Acts as OAuth 2.1 client, manages authorization flow on behalf of resource owner, MUST include `resource` parameter in all auth requests
- **Authorization Server**: Issues tokens, may be hosted with MCP server or as separate service, MUST implement OAuth 2.1 with PKCE support

**Sources:** [docs/specification/draft/basic/authorization.mdx:40-54]()

### Implementation Requirements Matrix

| Component | MUST | SHOULD | MAY |
|-----------|------|--------|-----|
| **Authorization Servers** | OAuth 2.1 implementation, PKCE support, RFC9728 compliance | DCR (RFC7591), Short-lived tokens | Multiple discovery mechanisms |
| **MCP Servers** | RFC9728 Protected Resource Metadata, Token audience validation, WWW-Authenticate headers | Include `scope` in 401 responses | Custom scope strategies |
| **MCP Clients** | RFC9728 support, PKCE with S256, `resource` parameter, Both discovery mechanisms | DCR (RFC7591), State parameter validation | Retry logic for scope challenges |

**Sources:** [docs/specification/draft/basic/authorization.mdx:55-71]()

## Authorization Server Discovery

### Discovery Mechanisms

MCP provides multiple discovery paths to locate authorization servers and their capabilities:

```mermaid
sequenceDiagram
    participant C as "MCP Client"
    participant M as "MCP Server"
    participant A as "Authorization Server"
    
    Note over C: "Attempt unauthenticated request"
    C->>M: "MCP request without Authorization header"
    M->>C: "HTTP 401 Unauthorized<br/>WWW-Authenticate: Bearer resource_metadata=..., scope=..."
    
    alt "WWW-Authenticate includes resource_metadata"
        C->>M: "GET resource_metadata URI"
        M->>C: "Protected Resource Metadata<br/>{authorization_servers: [...], scopes_supported: [...]}"
    else "No resource_metadata in header"
        Note over C: "Fallback to well-known URI probing"
        C->>M: "GET /.well-known/oauth-protected-resource/mcp"
        alt "Sub-path metadata exists"
            M->>C: "Protected Resource Metadata"
        else "Sub-path not found"
            C->>M: "GET /.well-known/oauth-protected-resource"
            alt "Root metadata exists"
                M->>C: "Protected Resource Metadata"
            else "Root metadata not found"
                Note over C: "Abort or use pre-configured values"
            end
        end
    end
    
    Note over C: "Extract authorization_servers[0]"
    
    Note over C: "Try AS metadata endpoints in priority order"
    C->>A: "GET /.well-known/oauth-authorization-server[/path]"
    alt "OAuth 2.0 AS Metadata found"
        A->>C: "AS Metadata (RFC8414)"
    else "Try OpenID Connect Discovery"
        C->>A: "GET /.well-known/openid-configuration[/path]"
        A->>C: "OIDC Discovery document"
    end
```

**Sources:** [docs/specification/draft/basic/authorization.mdx:72-194]()

### Protected Resource Metadata Discovery

MCP servers **MUST** implement one of these discovery mechanisms:

1. **WWW-Authenticate Header** (Preferred):
```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource",
                         scope="files:read"
```

2. **Well-Known URI** at MCP endpoint path:
```
https://example.com/public/mcp → https://example.com/.well-known/oauth-protected-resource/public/mcp
```

3. **Well-Known URI** at root:
```
https://example.com/.well-known/oauth-protected-resource
```

**MCP Client Requirements:**
- MUST support both discovery mechanisms
- MUST use `resource_metadata` from WWW-Authenticate when present
- MUST fall back to well-known URIs in order listed above
- MUST be able to parse WWW-Authenticate headers

**Sources:** [docs/specification/draft/basic/authorization.mdx:91-128]()

### Authorization Server Metadata Discovery

MCP clients **MUST** attempt multiple well-known endpoints to handle different issuer URL formats:

**For issuer URLs with path components** (e.g., `https://auth.example.com/tenant1`):
1. OAuth 2.0 AS Metadata with path insertion: `https://auth.example.com/.well-known/oauth-authorization-server/tenant1`
2. OpenID Connect Discovery with path insertion: `https://auth.example.com/.well-known/openid-configuration/tenant1`
3. OpenID Connect Discovery path appending: `https://auth.example.com/tenant1/.well-known/openid-configuration`

**For issuer URLs without path components** (e.g., `https://auth.example.com`):
1. OAuth 2.0 AS Metadata: `https://auth.example.com/.well-known/oauth-authorization-server`
2. OpenID Connect Discovery: `https://auth.example.com/.well-known/openid-configuration`

**Authorization Server Requirements:**
- MUST provide at least one discovery mechanism (RFC8414 or OpenID Connect Discovery)
- OpenID providers MUST include `code_challenge_methods_supported` in metadata for MCP compatibility

**Sources:** [docs/specification/draft/basic/authorization.mdx:129-145]()

### Discovery Protocol Details

```mermaid
graph TD
    Start["Client receives HTTP 401"]
    
    ParseHeader["Parse WWW-Authenticate header"]
    ExtractRM["Extract resource_metadata URL"]
    HasRM{resource_metadata<br/>present?}
    
    FetchRM["Fetch resource_metadata URL"]
    TrySubPath["Try /.well-known/oauth-protected-resource/[mcp-path]"]
    TryRoot["Try /.well-known/oauth-protected-resource"]
    
    SubPathSuccess{Success?}
    RootSuccess{Success?}
    
    ParseRS["Parse Protected Resource Metadata"]
    ExtractAS["Extract authorization_servers array"]
    SelectAS["Select authorization server<br/>(client decision)"]
    
    TryOAuth["Try OAuth 2.0 AS Metadata<br/>/.well-known/oauth-authorization-server[/path]"]
    TryOIDC["Try OpenID Connect Discovery<br/>/.well-known/openid-configuration[/path]"]
    
    OAuthSuccess{Success?}
    OIDCSuccess{Success?}
    
    ParseAS["Parse Authorization Server Metadata"]
    ValidatePKCE["Validate code_challenge_methods_supported<br/>includes S256"]
    PKCESupported{PKCE<br/>supported?}
    
    ProceedAuth["Proceed with authorization flow"]
    AbortNoPKCE["MUST refuse to proceed<br/>No PKCE support"]
    AbortNoMetadata["Abort or use pre-configured values"]
    
    Start --> ParseHeader
    ParseHeader --> HasRM
    
    HasRM -->|Yes| ExtractRM
    ExtractRM --> FetchRM
    FetchRM --> ParseRS
    
    HasRM -->|No| TrySubPath
    TrySubPath --> SubPathSuccess
    SubPathSuccess -->|Yes| ParseRS
    SubPathSuccess -->|No| TryRoot
    TryRoot --> RootSuccess
    RootSuccess -->|Yes| ParseRS
    RootSuccess -->|No| AbortNoMetadata
    
    ParseRS --> ExtractAS
    ExtractAS --> SelectAS
    SelectAS --> TryOAuth
    
    TryOAuth --> OAuthSuccess
    OAuthSuccess -->|Yes| ParseAS
    OAuthSuccess -->|No| TryOIDC
    
    TryOIDC --> OIDCSuccess
    OIDCSuccess -->|Yes| ParseAS
    OIDCSuccess -->|No| AbortNoMetadata
    
    ParseAS --> ValidatePKCE
    ValidatePKCE --> PKCESupported
    PKCESupported -->|Yes| ProceedAuth
    PKCESupported -->|No| AbortNoPKCE
```

**Key Metadata Fields:**

**Protected Resource Metadata (RFC9728):**
- `resource`: Canonical URI of the MCP server
- `authorization_servers`: Array of authorization server issuer URLs
- `scopes_supported`: Optional array of scope strings for least-privilege access
- `bearer_methods_supported`: Token transmission methods (typically `["header"]`)

**Authorization Server Metadata (RFC8414/OIDC Discovery):**
- `issuer`: Authorization server issuer URL
- `authorization_endpoint`: URL for authorization requests
- `token_endpoint`: URL for token requests
- `code_challenge_methods_supported`: **MUST** include `S256` for MCP compatibility
- `registration_endpoint`: Optional URL for dynamic client registration (RFC7591)
- `scopes_supported`: Optional list of supported scope values

**Sources:** [docs/specification/draft/basic/authorization.mdx:129-145, 476-488]()

## Client Registration Approaches

### Overview and Priority Order

MCP supports three client registration mechanisms to handle the diverse ecosystem where clients and servers often have no prior relationship. Clients supporting multiple options **SHOULD** follow this priority order:

```mermaid
graph TD
    Start["Client needs registration"]
    
    CheckPreReg{Pre-registered<br/>client_id available?}
    UsePreReg["Use Pre-registered Credentials<br/>Priority 1"]
    
    CheckCIMD{"Authorization Server Metadata<br/>client_id_metadata_document_supported?"}
    UseCIMD["Use Client ID Metadata Documents<br/>Priority 2"]
    
    CheckDCR{"Authorization Server Metadata<br/>registration_endpoint present?"}
    UseDCR["Use Dynamic Client Registration<br/>Priority 3"]
    
    PromptUser["Prompt User for Manual Registration<br/>Priority 4"]
    
    ProceedAuth["Proceed with Authorization Flow"]
    
    Start --> CheckPreReg
    CheckPreReg -->|Yes| UsePreReg
    CheckPreReg -->|No| CheckCIMD
    
    CheckCIMD -->|Yes| UseCIMD
    CheckCIMD -->|No| CheckDCR
    
    CheckDCR -->|Yes| UseDCR
    CheckDCR -->|No| PromptUser
    
    UsePreReg --> ProceedAuth
    UseCIMD --> ProceedAuth
    UseDCR --> ProceedAuth
    PromptUser --> ProceedAuth
```

**Priority Order Rationale:**
1. **Pre-registration**: Highest priority for established client-server relationships
2. **Client ID Metadata Documents**: Addresses "unbounded clients/servers" problem with URL-based registration
3. **Dynamic Client Registration**: Backward compatibility fallback
4. **Manual Registration**: Last resort requiring user intervention

**Sources:** [docs/specification/draft/basic/authorization.mdx:199-212]()

### Client ID Metadata Documents (Recommended)

MCP clients and authorization servers **SHOULD** support OAuth Client ID Metadata Documents (draft-ietf-oauth-client-id-metadata-document-00) as specified in [docs/specification/draft/basic/authorization.mdx:213-317]().

**Client ID Metadata Documents Flow:**

```mermaid
sequenceDiagram
    participant User
    participant Client["MCP Client"]
    participant MetadataHost["https://app.example.com"]
    participant Server["Authorization Server"]
    participant Resource["MCP Server"]
    
    Note over Client,MetadataHost: "Client hosts metadata document at HTTPS URL"
    
    User->>Client: "Initiates connection to MCP Server"
    
    Client->>Server: "Authorization Request<br/>client_id=https://app.example.com/oauth/client-metadata.json<br/>redirect_uri=http://localhost:3000/callback<br/>code_challenge=xyz&code_challenge_method=S256"
    
    Server->>User: "Authentication prompt"
    User->>Server: "Provides credentials"
    
    Note over Server: "Detects URL-formatted client_id"
    
    Server->>MetadataHost: "GET https://app.example.com/oauth/client-metadata.json"
    MetadataHost-->>Server: "JSON Metadata Document<br/>{<br/>  client_id: 'https://app.example.com/oauth/client-metadata.json',<br/>  client_name: 'Example MCP Client',<br/>  redirect_uris: ['http://localhost:3000/callback'],<br/>  grant_types: ['authorization_code'],<br/>  response_types: ['code'],<br/>  token_endpoint_auth_method: 'none'<br/>}"
    
    Note over Server: "Validates:<br/>1. client_id matches URL<br/>2. redirect_uri in allowed list<br/>3. Document structure valid"
    
    alt "Validation Success"
        Server->>User: "Display consent page with client_name"
        User->>Server: "Approves access"
        Server->>Client: "Authorization code via redirect_uri"
        Client->>Server: "Exchange code for token<br/>client_id=https://app.example.com/oauth/client-metadata.json"
        Server-->>Client: "Access token"
        Client->>Resource: "MCP requests with access token"
        Resource-->>Client: "MCP responses"
    else "Validation Failure"
        Server->>User: "Error response<br/>error=invalid_client or invalid_request"
    end
    
    Note over Server: "Cache metadata for future requests<br/>(respecting HTTP cache headers)"
```

**Implementation Requirements:**

**MCP Clients MUST:**
- Host metadata document at HTTPS URL with path component (e.g., `https://example.com/client.json`)
- Ensure `client_id` in metadata matches document URL exactly
- Include required fields: `client_id`, `client_name`, `redirect_uris`
- Use `token_endpoint_auth_method: "none"` for public clients
- May use `private_key_jwt` for authentication with appropriate JWKS configuration

**Authorization Servers SHOULD:**
- Fetch metadata documents when encountering URL-formatted `client_id` values
- Validate fetched document's `client_id` matches URL exactly
- Cache metadata respecting HTTP cache headers
- Validate redirect URIs against metadata document
- Advertise support via `client_id_metadata_document_supported: true` in Authorization Server Metadata

**Example Metadata Document:**
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

**Discovery:**

Authorization servers advertise support in OAuth Authorization Server Metadata:
```json
{
  "client_id_metadata_document_supported": true
}
```

**Sources:** [docs/specification/draft/basic/authorization.mdx:213-317]()

### Pre-registration

MCP clients **SHOULD** support static client credentials for established client-server relationships. This can be implemented by:

1. **Hardcoded Credentials**: Client ID (and client secret if applicable) embedded for specific authorization server
2. **User Configuration UI**: Allow users to enter credentials after manual registration through server's configuration interface

**Sources:** [docs/specification/draft/basic/authorization.mdx:318-327]()

### Dynamic Client Registration (Backward Compatibility)

MCP clients and authorization servers **MAY** support OAuth 2.0 Dynamic Client Registration Protocol (RFC7591) for backward compatibility with earlier MCP authorization specifications.

**Dynamic Client Registration Flow:**

```mermaid
sequenceDiagram
    participant C["MCP Client"]
    participant A["Authorization Server<br/>registration_endpoint"]
    
    Note over C: "Discovered registration_endpoint from AS metadata"
    
    C->>A: "POST /register<br/>Content-Type: application/json<br/>{<br/>  client_name: 'My MCP Client',<br/>  redirect_uris: ['http://localhost:8080/callback'],<br/>  grant_types: ['authorization_code', 'refresh_token'],<br/>  token_endpoint_auth_method: 'none'<br/>}"
    
    Note over A: "Validates request<br/>Applies registration policy<br/>Generates client_id"
    
    alt "Registration successful"
        A->>C: "HTTP 201 Created<br/>{<br/>  client_id: 'abc123',<br/>  client_secret: null,<br/>  redirect_uris: ['http://localhost:8080/callback'],<br/>  grant_types: ['authorization_code', 'refresh_token'],<br/>  client_id_issued_at: 1234567890<br/>}"
        Note over C: "Store client_id for future requests"
    else "Registration rejected"
        A->>C: "HTTP 400 Bad Request<br/>{<br/>  error: 'invalid_redirect_uri',<br/>  error_description: '...'<br/>}"
        Note over C: "Handle error or fall back to manual registration"
    end
```

**Key Registration Parameters:**
- `client_name`: Human-readable client name
- `redirect_uris`: Array of valid redirect URIs (localhost or HTTPS)
- `grant_types`: Should include `authorization_code`, `refresh_token`
- `token_endpoint_auth_method`: Set to `none` for public clients
- `response_types`: Typically `["code"]` for authorization code flow

**Sources:** [docs/specification/draft/basic/authorization.mdx:328-334]()

## Authorization Flow

### Complete Authorization Flow with PKCE

```mermaid
sequenceDiagram
    participant B as "User-Agent<br/>(Browser)"
    participant C as "MCP Client"
    participant M as "MCP Server<br/>(Resource Server)"
    participant A as "Authorization Server"
    
    rect
        Note over C,M: "Phase 1: Discovery"
        C->>M: "MCP request without token"
        M->>C: "HTTP 401 Unauthorized<br/>WWW-Authenticate: Bearer resource_metadata=..."
        C->>M: "GET resource_metadata URI"
        M->>C: "Protected Resource Metadata<br/>{authorization_servers: [...]}"
        C->>A: "GET Authorization Server Metadata"
        A->>C: "AS Metadata<br/>{authorization_endpoint, token_endpoint, ...}"
    end
    
    rect
        Note over C,A: "Phase 2: Client Registration (Choose based on priority)"
        
        alt "Pre-registration available"
            Note over C: "Use existing client_id"
        else "Client ID Metadata Documents supported"
            Note over C: "Use HTTPS URL as client_id<br/>client_id=https://app.example.com/oauth/metadata.json"
            A->>C: "Fetch metadata from client_id URL"
            C-->>A: "JSON metadata document"
            Note over A: "Validate metadata and redirect_uris"
        else "Dynamic Client Registration supported"
            C->>A: "POST /register<br/>{client_name, redirect_uris, ...}"
            A->>C: "Client Credentials<br/>{client_id: 'abc123', ...}"
        else "Manual registration required"
            Note over C: "Prompt user to enter client_id"
        end
    end
    
    rect
        Note over B,A: "Phase 3: Authorization Code Flow with PKCE"
        Note over C: "Generate PKCE parameters<br/>code_verifier = random(43-128 chars)<br/>code_challenge = base64url(sha256(code_verifier))"
        Note over C: "Apply Scope Selection Strategy<br/>Use scope from WWW-Authenticate or scopes_supported"
        Note over C: "Include resource parameter<br/>resource = https://mcp.example.com"
        
        C->>B: "Open browser with authorization URL:<br/>?response_type=code<br/>&client_id=abc123<br/>&redirect_uri=http://localhost:8080/callback<br/>&code_challenge=xyz<br/>&code_challenge_method=S256<br/>&resource=https://mcp.example.com<br/>&scope=files:read<br/>&state=random-state"
        
        B->>A: "GET /authorize with parameters"
        Note over A: "User authenticates<br/>User authorizes scopes"
        A->>B: "Redirect to callback:<br/>?code=auth-code-123<br/>&state=random-state"
        
        B->>C: "Authorization code callback"
        Note over C: "Validate state parameter"
        
        C->>A: "POST /token<br/>grant_type=authorization_code<br/>&code=auth-code-123<br/>&redirect_uri=http://localhost:8080/callback<br/>&code_verifier=original-verifier<br/>&resource=https://mcp.example.com<br/>&client_id=abc123"
        
        Note over A: "Validate PKCE<br/>Validate resource parameter<br/>Issue token bound to audience"
        
        A->>C: "Access Token Response<br/>{<br/>  access_token: 'eyJ...',<br/>  token_type: 'Bearer',<br/>  expires_in: 3600,<br/>  refresh_token: '...',<br/>  scope: 'files:read'<br/>}"
    end
    
    rect
        Note over C,M: "Phase 4: MCP Communication"
        C->>M: "MCP request<br/>Authorization: Bearer eyJ..."
        Note over M: "Validate token audience<br/>matches self"
        M->>C: "MCP response"
        Note over C,M: "Ongoing communication with valid token"
    end
```

**Sources:** [docs/specification/draft/basic/authorization.mdx:236-276]()

### PKCE Requirements

**Proof Key for Code Exchange (PKCE)** is **REQUIRED** for all MCP clients to prevent authorization code interception and injection attacks.

**PKCE Protocol:**
1. Client generates `code_verifier`: Random string (43-128 characters)
2. Client computes `code_challenge`: `base64url(sha256(code_verifier))`
3. Client sends `code_challenge` and `code_challenge_method=S256` in authorization request
4. Client sends `code_verifier` in token request
5. Authorization server validates that `sha256(code_verifier)` matches the stored `code_challenge`

**MCP-Specific Requirements:**
- Clients MUST use `S256` code challenge method when technically capable
- Clients MUST verify PKCE support before proceeding with authorization
- Clients MUST refuse to proceed if `code_challenge_methods_supported` is absent or doesn't include `S256`
- Authorization servers MUST include `code_challenge_methods_supported` in metadata

**Sources:** [docs/specification/draft/basic/authorization.mdx:472-488]()

### Resource Parameter Implementation

MCP clients **MUST** implement Resource Indicators (RFC8707) to bind tokens to specific MCP servers and prevent token misuse across services.

**Requirements:**
1. MUST include `resource` parameter in both authorization and token requests
2. MUST identify the MCP server the client intends to use the token with
3. MUST use the canonical URI of the MCP server

**Canonical Server URI Definition:**

```mermaid
graph LR
    Input["MCP Server URL"]
    
    subgraph "Valid Canonical URIs"
        V1["https://mcp.example.com/mcp"]
        V2["https://mcp.example.com"]
        V3["https://mcp.example.com:8443"]
        V4["https://mcp.example.com/server/mcp"]
    end
    
    subgraph "Invalid Canonical URIs"
        I1["mcp.example.com<br/>(missing scheme)"]
        I2["https://mcp.example.com#fragment<br/>(contains fragment)"]
    end
    
    Input --> V1
    Input --> V2
    Input --> V3
    Input --> V4
```

**Canonical URI Rules:**
- MUST include scheme (https)
- MUST include host (domain or IP)
- MAY include port if non-standard
- MAY include path when necessary to identify individual MCP server
- MUST NOT include fragment
- SHOULD omit trailing slash unless semantically significant
- SHOULD use lowercase scheme and host (but implementations SHOULD accept uppercase)

**Example Authorization Request:**
```
GET /authorize?
  response_type=code&
  client_id=abc123&
  redirect_uri=http://localhost:8080/callback&
  code_challenge=xyz&
  code_challenge_method=S256&
  resource=https%3A%2F%2Fmcp.example.com&
  scope=files:read&
  state=random-state
```

**Sources:** [docs/specification/draft/basic/authorization.mdx:278-315]()

## Scope Management

### Scope Selection Strategy

MCP clients **SHOULD** follow the principle of least privilege by requesting only necessary scopes. During initial authorization handshake, clients should use this priority order:

```mermaid
graph TD
    Start["Initiate authorization"]
    
    Check401["Check WWW-Authenticate header<br/>from HTTP 401 response"]
    HasScope{scope parameter<br/>present?}
    
    UseScope["Use scope from<br/>WWW-Authenticate header<br/>Priority 1"]
    
    CheckMetadata["Check Protected Resource Metadata"]
    HasScopesSupported{scopes_supported<br/>defined?}
    
    UseScopesSupported["Request all scopes from<br/>scopes_supported<br/>Priority 2"]
    OmitScope["Omit scope parameter<br/>(authorization server decides)"]
    
    BuildAuthRequest["Build authorization request<br/>with selected scopes"]
    
    Start --> Check401
    Check401 --> HasScope
    
    HasScope -->|Yes| UseScope
    HasScope -->|No| CheckMetadata
    
    CheckMetadata --> HasScopesSupported
    HasScopesSupported -->|Yes| UseScopesSupported
    HasScopesSupported -->|No| OmitScope
    
    UseScope --> BuildAuthRequest
    UseScopesSupported --> BuildAuthRequest
    OmitScope --> BuildAuthRequest
```

**Scope Selection Rationale:**

1. **Use `scope` from WWW-Authenticate** (Priority 1): Server explicitly signals minimal required scopes for initial access
2. **Use all `scopes_supported` from metadata** (Priority 2): Request full minimal scope set defined by resource server
3. **Omit scope parameter**: Let authorization server determine appropriate scopes if none specified

This approach accommodates the general-purpose nature of MCP clients, which typically lack domain-specific knowledge to make informed decisions about individual scope selection. Requesting all available scopes from `scopes_supported` allows the authorization server and end-user to determine appropriate permissions during the consent process.

The `scopes_supported` field represents the minimal set of scopes necessary for basic functionality (see Security Best Practices for scope minimization). Additional scopes can be requested incrementally through step-up authorization flows when more privileged operations are attempted.

**Sources:** [docs/specification/draft/basic/authorization.mdx:335-350]()

### Scope Challenge Handling

When a client has a token but needs additional permissions, servers respond with `insufficient_scope` errors, triggering step-up authorization.

**Runtime Insufficient Scope Response:**

```http
HTTP/1.1 403 Forbidden
WWW-Authenticate: Bearer error="insufficient_scope",
                         scope="files:read files:write user:profile",
                         resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource",
                         error_description="Additional file write permission required"
```

**Response Components:**
- `error="insufficient_scope"`: Indicates specific authorization failure type
- `scope`: Space-separated list of scopes needed for the operation
- `resource_metadata`: URI of Protected Resource Metadata document for consistency
- `error_description`: Optional human-readable description

**Scope Parameter Semantics:**

The `scope` parameter in `insufficient_scope` challenges has flexible semantics. Servers **MAY**:
- Include only newly-required scopes (minimum approach)
- Include existing granted scopes plus newly-required scopes (recommended approach)
- Include existing, newly-required, and related scopes that commonly work together (extended approach)

Servers **SHOULD** be consistent in their scope inclusion strategy to provide predictable behavior for clients. The scopes included **MAY** match `scopes_supported`, be a subset, superset, or alternative collection. Clients **MUST NOT** assume any particular set relationship and **MUST** treat challenged scopes as authoritative for satisfying the current request.

**Sources:** [docs/specification/draft/basic/authorization.mdx:504-532]()

### Step-Up Authorization Flow

```mermaid
sequenceDiagram
    participant C as "MCP Client"
    participant M as "MCP Server"
    participant B as "User-Agent"
    participant A as "Authorization Server"
    
    Note over C: "Client has existing access token<br/>with scope: files:read"
    
    C->>M: "Request to write file<br/>Authorization: Bearer existing-token"
    
    Note over M: "Check token scopes<br/>files:write required but not granted"
    
    M->>C: "HTTP 403 Forbidden<br/>WWW-Authenticate: Bearer error='insufficient_scope',<br/>  scope='files:read files:write'"
    
    Note over C: "Parse insufficient_scope error<br/>Extract required scopes"
    
    Note over C: "Determine scope set:<br/>- Keep existing: files:read<br/>- Add required: files:write<br/>Final: files:read files:write"
    
    C->>B: "Initiate re-authorization<br/>with expanded scope set"
    B->>A: "Authorization request<br/>scope=files:read files:write"
    
    Note over A: "User consents to<br/>additional permission"
    
    A->>B: "Authorization code"
    B->>C: "Code callback"
    
    C->>A: "Token request"
    A->>C: "New access token<br/>scope: files:read files:write"
    
    Note over C: "Replace existing token with new token"
    
    C->>M: "Retry original request<br/>Authorization: Bearer new-token"
    M->>C: "Success response"
```

**Step-Up Authorization Flow Requirements:**

**MCP Clients:**
1. **Parse error information** from authorization server response or WWW-Authenticate header
2. **Determine required scopes** following Scope Selection Strategy (use challenged scope set)
3. **Initiate re-authorization** with determined scope set
4. **Retry original request** with new access token
5. **SHOULD** implement retry limits to avoid repeated failures
6. **SHOULD** track scope upgrade attempts per resource/operation to detect permanent authorization failures

**When to Attempt Step-Up:**
- **SHOULD** attempt for clients acting on behalf of users (authorization code grant)
- **MAY** attempt or abort immediately for `client_credentials` clients acting on their own behalf

**MCP Servers:**
- **SHOULD** include scopes needed to satisfy current request in `scope` parameter
- **SHOULD** be consistent in scope inclusion strategy
- **SHOULD** consider user experience impact when determining which scopes to include
- **MAY** use different strategies: minimum (only new scopes), recommended (existing + new), or extended (existing + new + related)
- Servers have flexibility in determining which scopes to include based on assessment of user experience and authorization friction

**Sources:** [docs/specification/draft/basic/authorization.mdx:545-559]()

## Token Management

### Access Token Usage

**Token Transmission:**

MCP clients **MUST** use the `Authorization` header with Bearer scheme:

```http
GET /mcp HTTP/1.1
Host: mcp.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Requirements:**
- MUST use Authorization header field (OAuth 2.1 Section 5.1.1)
- MUST include authorization in every HTTP request, even within same logical session
- MUST NOT include access tokens in URI query string
- Access tokens MUST be transmitted as `Bearer` tokens per RFC6750

**Sources:** [docs/specification/draft/basic/authorization.mdx:317-344]()

### Token Validation

```mermaid
graph TD
    Receive["MCP Server receives request<br/>with Authorization: Bearer token"]
    
    Extract["Extract access token from header"]
    
    ValidateFormat{Token format<br/>valid?}
    
    CheckExpiry{Token<br/>expired?}
    
    ValidateAudience{Token audience<br/>matches server URI?}
    
    CheckScopes{Required scopes<br/>present?}
    
    ProcessRequest["Process MCP request"]
    
    Return401Format["HTTP 401 Unauthorized<br/>error: invalid_token<br/>error_description: Malformed token"]
    
    Return401Expired["HTTP 401 Unauthorized<br/>error: invalid_token<br/>error_description: Token expired"]
    
    Return401Audience["HTTP 401 Unauthorized<br/>error: invalid_token<br/>error_description: Invalid audience"]
    
    Return403Scope["HTTP 403 Forbidden<br/>error: insufficient_scope<br/>scope: required scopes"]
    
    Receive --> Extract
    Extract --> ValidateFormat
    
    ValidateFormat -->|Invalid| Return401Format
    ValidateFormat -->|Valid| CheckExpiry
    
    CheckExpiry -->|Expired| Return401Expired
    CheckExpiry -->|Valid| ValidateAudience
    
    ValidateAudience -->|Mismatch| Return401Audience
    ValidateAudience -->|Match| CheckScopes
    
    CheckScopes -->|Insufficient| Return403Scope
    CheckScopes -->|Sufficient| ProcessRequest
```

**MCP Server Validation Requirements:**
- MUST validate access tokens per OAuth 2.1 Section 5.2
- MUST validate token audience matches server's canonical URI (RFC8707)
- MUST verify tokens were issued by the server's authorization server
- MUST NOT accept or transit tokens for other resources
- MUST respond with HTTP 401 for invalid/expired tokens
- MUST respond with HTTP 403 for insufficient scopes

**MCP Client Validation Requirements:**
- MUST NOT send tokens to MCP server other than ones issued by that server's authorization server
- MUST verify state parameter in authorization responses
- MUST discard responses with mismatched or missing state

**Sources:** [docs/specification/draft/basic/authorization.mdx:345-362, 513-533]()

### Token Audience Binding

Token audience binding prevents token misuse across different services:

**Token Audience Validation Flow:**

```mermaid
sequenceDiagram
    participant C as "MCP Client"
    participant M as "MCP Server<br/>(https://mcp.example.com)"
    participant A as "Authorization Server"
    
    Note over C: "Requesting token for mcp.example.com"
    
    C->>A: "POST /token<br/>resource=https://mcp.example.com<br/>code=..., code_verifier=..."
    
    Note over A: "Issue token with audience<br/>aud: https://mcp.example.com"
    
    A->>C: "Access Token<br/>{aud: 'https://mcp.example.com'}"
    
    rect
        Note over C,M: "Valid Usage: Token used at intended server"
        C->>M: "Authorization: Bearer token"
        Note over M: "Validate token.aud == self<br/>https://mcp.example.com == https://mcp.example.com<br/>✓ Match"
        M->>C: "Success response"
    end
    
    rect
        Note over C: "Invalid Usage: Attacker tries token at different server"
        C->>M: "Authorization: Bearer token<br/>(to different-server.com)"
        Note over M: "Validate token.aud == self<br/>https://mcp.example.com != https://different-server.com<br/>✗ Mismatch"
        M->>C: "HTTP 401 Unauthorized<br/>Invalid audience"
    end
```

**Audience Binding Requirements:**
- Clients MUST include `resource` parameter in authorization and token requests
- Clients MUST send this parameter regardless of authorization server support
- Servers MUST validate tokens were issued specifically for them
- Servers MUST reject tokens that don't include them in the audience claim
- Servers MUST NOT pass through tokens received from clients to upstream APIs

**Sources:** [docs/specification/draft/basic/authorization.mdx:440-450, 513-533]()

### Token Lifecycle

| Token Event | Client Action | Server Action |
|-------------|---------------|---------------|
| **Issuance** | Store securely (OAuth 2.1 Section 7.1) | Issue short-lived tokens |
| **Usage** | Include in Authorization header | Validate on every request |
| **Expiration** | Request new token using refresh token | Return HTTP 401 |
| **Refresh** | Exchange refresh token for new access token | Rotate refresh tokens (public clients) |
| **Revocation** | Clear stored tokens | Invalidate tokens |

**Security Requirements:**
- Authorization servers SHOULD issue short-lived access tokens to reduce impact of token theft
- Authorization servers MUST rotate refresh tokens for public clients (OAuth 2.1 Section 4.3.1)
- Clients and servers MUST implement secure token storage
- Clients MUST follow OAuth 2.1 Section 7.1 best practices

**Sources:** [docs/specification/draft/basic/authorization.mdx:451-461]()

## Error Handling

### HTTP Status Codes

| Status Code | Description | Usage | Required WWW-Authenticate |
|-------------|-------------|-------|---------------------------|
| 401 Unauthorized | Authorization required or token invalid | No token provided, token expired, token invalid | Yes (with `resource_metadata`) |
| 403 Forbidden | Invalid scopes or insufficient permissions | Token valid but lacks required scopes | Yes (with `error`, `scope`) |
| 400 Bad Request | Malformed authorization request | Invalid parameters, malformed token | No |

**Sources:** [docs/specification/draft/basic/authorization.mdx:363-372]()

### WWW-Authenticate Header Formats

**Initial Authorization Required (401):**
```http
WWW-Authenticate: Bearer resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource",
                         scope="files:read"
```

**Invalid Token (401):**
```http
WWW-Authenticate: Bearer error="invalid_token",
                         error_description="The access token expired",
                         resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource"
```

**Insufficient Scope (403):**
```http
WWW-Authenticate: Bearer error="insufficient_scope",
                         scope="files:read files:write",
                         resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource",
                         error_description="Additional file write permission required"
```

**Sources:** [docs/specification/draft/basic/authorization.mdx:117-123, 409-418]()

## Security Requirements

### Communication Security

All authorization communication **MUST** use HTTPS:

**Requirements:**
- All authorization server endpoints MUST be served over HTTPS
- All redirect URIs MUST be either `localhost` or use HTTPS
- Implementations MUST follow OAuth 2.1 Section 1.5 Communication Security
- TLS 1.2 or higher SHOULD be enforced
- Certificate validation MUST NOT be disabled

**Sources:** [docs/specification/draft/basic/authorization.mdx:462-471]()

### PKCE and Authorization Code Protection

PKCE prevents authorization code interception and injection attacks:

**Attack Scenario Without PKCE:**
1. Attacker intercepts authorization code from redirect
2. Attacker exchanges code for access token before legitimate client
3. Attacker gains unauthorized access

**Protection with PKCE:**
1. Client generates random `code_verifier` and sends `code_challenge` to authorization server
2. Even if attacker intercepts authorization code, they don't have `code_verifier`
3. Authorization server rejects token exchange without matching `code_verifier`

**Sources:** [docs/specification/draft/basic/authorization.mdx:472-488]()

### Open Redirection Prevention

**Attack Vector:** Attacker crafts malicious redirect URIs to direct users to phishing sites.

**Mitigations:**

**MCP Clients MUST:**
- Have redirect URIs registered with authorization server
- Verify state parameters in authorization code flow
- Discard responses with mismatched or missing state

**Authorization Servers MUST:**
- Validate exact redirect URIs against pre-registered values
- Take precautions to prevent redirecting to untrusted URIs (OAuth 2.1 Section 7.12.2)
- Only automatically redirect if redirect URI is trusted
- May inform user and rely on user decision if URI is not trusted

**Sources:** [docs/specification/draft/basic/authorization.mdx:489-503]()

### Confused Deputy Prevention

**Attack Scenario:** MCP server acts as proxy to third-party APIs, attacker exploits this to gain unauthorized access using stolen authorization codes.

```mermaid
graph LR
    subgraph "Attack Without Protection"
        Attacker1["Attacker"]
        MCPServer1["MCP Server<br/>(static client_id)"]
        ThirdParty1["Third-Party API"]
        
        Attacker1 -->|"Stolen authorization code"| MCPServer1
        MCPServer1 -->|"Forwards without consent"| ThirdParty1
        ThirdParty1 -->|"Grants access"| MCPServer1
        MCPServer1 -->|"Attacker gains access"| Attacker1
    end
    
    subgraph "Protection with Per-Client Consent"
        User2["Legitimate User"]
        MCPServer2["MCP Server<br/>(per-client approval)"]
        ThirdParty2["Third-Party API"]
        ConsentDB["Approved Client Registry"]
        
        User2 -->|"Authorization code"| MCPServer2
        MCPServer2 -->|"Check approval"| ConsentDB
        ConsentDB -->|"Approved for this client_id"| MCPServer2
        MCPServer2 -->|"Forward with consent"| ThirdParty2
    end
```

**Protection Requirements:**

MCP proxy servers using static client IDs MUST:
- Obtain user consent for each dynamically registered client
- Maintain registry of approved `client_id` values
- Verify client approval before forwarding to third-party authorization servers
- May require additional consent at third-party authorization server

**Sources:** [docs/specification/draft/basic/authorization.mdx:504-512]()

### Token Theft Prevention

**Attack Vector:** Attackers obtain tokens stored by client or cached/logged on server.

**Mitigations:**

**Authorization Servers SHOULD:**
- Issue short-lived access tokens
- Rotate refresh tokens for public clients (OAuth 2.1 Section 4.3.1)
- Implement token binding where possible

**Clients and Servers MUST:**
- Implement secure token storage per OAuth 2.1 Section 7.1
- Never log tokens
- Encrypt tokens at rest
- Use secure memory management for in-memory tokens
- Clear tokens on logout/revocation

**Sources:** [docs/specification/draft/basic/authorization.mdx:451-461]()

### Access Token Privilege Restriction

**Two Critical Dimensions:**

1. **Audience Validation Failures:** Server doesn't verify token was intended for it, allowing token reuse across services
2. **Token Passthrough:** Server forwards unmodified tokens to downstream services, causing confused deputy issues

**Protection Requirements:**

**MCP Servers MUST:**
- Validate access tokens per OAuth 2.1 Section 5.2
- Ensure token was issued specifically for the MCP server
- Reject tokens without server in audience claim
- NOT pass through received tokens to upstream APIs
- Generate separate tokens when acting as OAuth client to upstream APIs

**MCP Clients MUST:**
- Implement `resource` parameter per RFC8707
- Explicitly specify target resource in authorization and token requests
- Ensure tokens are bound to intended resources

**Sources:** [docs/specification/draft/basic/authorization.mdx:513-533]()

### Security Checklist

| Component | Requirement | Purpose |
|-----------|-------------|---------|
| **Transport** | HTTPS for all endpoints | Prevent eavesdropping |
| **PKCE** | S256 code challenge REQUIRED | Prevent authorization code interception |
| **Redirect URIs** | Exact validation required | Prevent open redirection |
| **State Parameter** | Verify in responses | Prevent CSRF attacks |
| **Token Storage** | Secure storage per OAuth 2.1 Section 7.1 | Prevent token theft |
| **Token Lifetime** | Short-lived access tokens | Limit impact of theft |
| **Refresh Tokens** | Rotation for public clients | Prevent refresh token reuse |
| **Audience Validation** | MUST validate token.aud matches self | Prevent token misuse |
| **Resource Parameter** | MUST include in auth/token requests | Bind tokens to intended resource |
| **Token Passthrough** | FORBIDDEN | Prevent confused deputy |
| **Scope Minimization** | Request only necessary scopes | Principle of least privilege |
| **Per-Client Consent** | Required for proxy servers | Prevent confused deputy |

**Sources:** [docs/specification/draft/basic/authorization.mdx:436-533]()