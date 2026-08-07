# Highlights

- `Architecture.md:L8-L60` The Collector separates foundation interfaces, component implementations, service orchestration, and generated distributions into distinct architectural layers.
- `Pipeline_and_Data_Flow.md:L7-L35` Each pipeline is a directed flow for one signal type, identified by a signal plus an optional name and composed of receivers, processors, and exporters.
- `Pipeline_and_Data_Flow.md:L81-L118` Components exchange `pdata`, while declared mutation capabilities determine whether fan-out branches share references or receive clones.
- `Component_Model.md:L96-L109` The five component roles are receivers, processors, exporters, connectors, and extensions, each with a distinct place in or around the data path.
- `Component_Model.md:L113-L156` Factories create signal-specific implementations, after which the service manages a consistent create-start-run-shutdown lifecycle.
- `Connectors_and_Extensions.md:L3-L45` A connector acts as the exporter of one pipeline and the receiver of another, enabling routing and cross-signal transformation without an external transport.
- `Connectors_and_Extensions.md:L47-L112` Extensions stay outside the telemetry pipeline while supplying lifecycle-scoped services such as diagnostics, authentication, and middleware.
- `Builder_Configuration.md:L1-L40` The Collector Builder uses a YAML manifest to generate a custom distribution containing only the selected component modules and configuration providers.
- `URI_Expansion_and_Dynamic_Configuration.md:L9-L62` The resolver expands standalone, embedded, nested, and default-scheme URIs through pluggable providers.
- `URI_Expansion_and_Dynamic_Configuration.md:L107-L134` Providers may emit change events, allowing the resolver to re-read configuration and trigger a new resolution cycle.
- `OTLP_Exporters.md:L772-L829` Exporter helpers place bounded queues and optional persistent storage ahead of transmission to buffer bursts and survive restarts.
- `OTLP_Exporters.md:L902-L1015` Retry behavior depends on error classification: permanent failures stop, transient failures back off, and throttling failures honor server-directed delays.
