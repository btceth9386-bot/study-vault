---
id: collector-authentication-extensions
title: Collector Authentication Extensions
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-opentelemetry-collector-contrib/
related:
  - collector-extensions
  - collector-pipeline-architecture
tags:
  - observability
  - opentelemetry
  - collector
---

# Collector Authentication Extensions

- **One-sentence definition**: Authentication extensions are shared Collector services that verify incoming credentials or attach credentials to outgoing requests.
- **Why it exists / what problem it solves**: They keep login and credential-refresh logic out of every receiver and exporter.
- **Keywords**: authentication, bearer token, OAuth, credentials, extension
- **Related concepts**: [[collector-extensions]], [[collector-pipeline-architecture]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/opentelemetry-collector-contrib

## Summary

Authentication is the Collector's reusable door guard. A server authenticator checks who is sending telemetry, while a client authenticator adds the credentials needed to send telemetry onward. Keeping that work in an extension means receivers and exporters can focus on moving data instead of each implementing token handling.

## Example

An OTLP receiver uses a bearer-token authenticator to reject unknown clients. The exporter uses an OAuth authenticator that refreshes an access token before sending accepted telemetry to a cloud backend.

## Relationship to existing concepts

- [[collector-extensions]]: Authentication is a shared support service outside the telemetry data path.
- [[collector-pipeline-architecture]]: Authenticators protect the inbound and outbound boundaries of a pipeline.

## Open questions

- Which credentials should be refreshed by the Collector rather than supplied by its deployment?
- How should a pipeline behave when its outbound credentials cannot be renewed?
