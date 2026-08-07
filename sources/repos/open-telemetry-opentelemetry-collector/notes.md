# open-telemetry/opentelemetry-collector

## Summary

The OpenTelemetry Collector is a modular service for receiving, transforming, and exporting traces, metrics, and logs. A signal-specific pipeline normally connects one or more receivers to optional processors and then to exporters. Components exchange telemetry through small consumer interfaces and a shared in-memory `pdata` representation, which keeps protocol decoding at the edges and processing independent of wire formats.

The component model makes this graph extensible without giving up lifecycle control. Factories create signal-specific components from YAML-derived configuration and developer settings; the service then coordinates creation, startup, operation, and shutdown. Receivers ingest data, processors transform it, exporters deliver it, connectors bridge pipelines or convert one signal into another, and extensions provide supporting services such as authentication and diagnostics. Shared components allow multiple pipelines to reuse one underlying listener or resource.

Performance and safety depend on an explicit ownership contract. Processors and exporters declare whether they mutate data, allowing fan-out logic to share read-only data while cloning branches that require exclusive ownership. Export reliability is similarly layered: batching improves efficiency, bounded queues absorb bursts, persistent storage can survive restarts, and retry logic distinguishes permanent, transient, and throttling failures.

Configuration and distribution are also modular. The `confmap` resolver composes configuration from providers such as environment variables, files, HTTP, HTTPS, and YAML; URI expansion preserves typed standalone values and supports provider-driven change notifications. The OpenTelemetry Collector Builder (`ocb`) turns a YAML component manifest into a purpose-built Go distribution, including generated factory registration and module dependencies. Together these mechanisms make the Collector less a fixed agent than a configurable telemetry runtime whose topology, capabilities, and deployment footprint can be tailored to the operating environment.

## Knowledge Map

- Signal-specific receiver-processor-exporter pipelines define the primary data path.
- Factories and lifecycle contracts let the service orchestrate heterogeneous components uniformly.
- Capability-driven ownership protects mutable `pdata` at fan-out points.
- Connectors join pipelines; extensions supply cross-cutting operational services.
- Queueing, batching, persistence, and classified retries make exporters resilient.
- Configuration providers and `ocb` customize runtime behavior and binary composition.

## Key Takeaways

- Treat the Collector as a programmable pipeline host, not merely an OTLP proxy.
- Declare mutation honestly: it determines whether fan-out can share data safely.
- Use connectors for in-process routing and signal conversion between pipelines.
- Size queues and retries as bounded failure buffers, not guarantees of lossless delivery.
- Build custom distributions when a smaller, controlled component set matters operationally.
