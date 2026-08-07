The Datadog integration in `opentelemetry-collector-contrib` consists of a:

* Highly customizable **Datadog Receiver** supporting multiple Datadog protocol versions, implementing native ingestion endpoints and OTLP translation including advanced trace ID reconstruction.

* Flexible **Datadog Connector** that converts trace data into additional metrics representing APM stats, enabling enhanced pipeline-based analytics.

* Rich **Datadog Exporter** that supports OTLP traces, metrics, logs and integrates with Datadog Agent's components for robust data transformation, host metadata reporting, API key validation, and native format serialization.

Together, these components create a comprehensive bi-directional Datadog integration with consistency enforced through shared translators, rich feature flags, and robust configuration with comprehensive integration tests demonstrating the expected end-to-end behavior.

---

**Sources:**

- `exporter/datadogexporter/factory.go:1-155, 168-195, 198-274`
- `exporter/datadogexporter/traces_exporter.go:41-93, 95-148`
- `exporter/datadogexporter/metrics_exporter.go:58-123, 175-234`
- `exporter/datadogexporter/README.md:2-90, 100-103`
- `receiver/datadogreceiver/receiver.go:40-221, 223-370`
- `receiver/datadogreceiver/internal/translator/traces_translator.go:50-114, 116-190`
- `connector/datadogconnector/factory.go:18-28`
- `exporter/datadogexporter/integrationtest/integration_test.go:78-148`