# open-telemetry/opentelemetry-specification

## Summary

The OpenTelemetry specification is the contract that keeps observability tooling coherent across languages, runtimes, and vendors. Its core move is to separate the instrumentation API from the SDK implementation: libraries depend on stable interfaces like `Tracer`, `Meter`, and `Logger`, while application owners choose processors, exporters, and runtime configuration later. That split prevents vendor lock-in, preserves a no-op path when no SDK is installed, and lets one instrumentation library work with many backends.

The spec is organized around telemetry signals such as traces, metrics, logs, and baggage, but the real value is the shared structure around them. Context propagation moves trace and baggage state across process boundaries, resources identify the entity emitting telemetry, semantic conventions give everyone the same attribute vocabulary, and OTLP defines a standard wire protocol for moving data to collectors and backends. The metrics subsystem adds another layer with views, aggregations, cardinality controls, and exemplars so measurements can be reshaped without changing instrumentation code.

The overall theme is interoperability with controlled flexibility. OpenTelemetry standardizes the parts that must match across ecosystems, then leaves room for SDK configuration, exporter choice, schema evolution, and sampling strategies. For long-term learning, the durable ideas are not the specific API names but the design patterns: separate instrumentation from implementation, propagate context explicitly, attach identity at the producer boundary, standardize schemas, and keep collection pipelines configurable without rewriting application code.

## Knowledge Map

- API and SDK separation keeps instrumentation portable and vendor-neutral.
- Signals share cross-cutting context, resources, schemas, and export pipelines.
- Semantic conventions and OTLP standardize meaning and transport separately.
- Metrics use views and aggregations to reshape data after instrumentation.
- Sampling and cardinality limits control cost without discarding the whole model.

## Key Takeaways

- Instrumentation libraries should depend on OpenTelemetry APIs, not concrete SDKs.
- Context propagation and baggage are essential for cross-service correlation.
- Resources and semantic conventions make telemetry queryable across systems.
- OTLP is the default common transport, while exporters remain pluggable.
- Metrics design is largely about post-instrumentation control: views, readers, and aggregation policy.
