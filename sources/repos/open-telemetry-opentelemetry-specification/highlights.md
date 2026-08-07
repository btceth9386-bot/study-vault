# Highlights

- `Section: OpenTelemetry Specification Overview` The specification separates API packages from SDK packages so libraries can instrument once and applications can choose implementations later.
- `Section: OpenTelemetry Architecture` Traces, metrics, logs, and baggage are independent signals that still share common propagation and identity mechanisms.
- `Section: Context API and Baggage` Context is immutable and carries execution-scoped state; baggage uses that mechanism to propagate application-defined key-value pairs across services.
- `Section: Resource SDK` A resource is the immutable identity of the telemetry producer, and providers bind that identity to all emitted telemetry.
- `Section: Semantic Conventions` Standard attribute names such as `service.name` and `http.request.method` make telemetry portable across languages and backends.
- `Section: Exporters and Protocol` OTLP defines a common transport with gRPC, HTTP/protobuf, and HTTP/JSON variants, while signal-specific endpoints stay predictable.
- `Section: Metrics System` Views, aggregations, readers, and exemplar handling let teams change exported metric shape without rewriting instrumentation.
- `Section: Advanced Topics` Consistent probability sampling uses shared randomness and thresholds so distributed traces stay intact even when sampling rates vary.
