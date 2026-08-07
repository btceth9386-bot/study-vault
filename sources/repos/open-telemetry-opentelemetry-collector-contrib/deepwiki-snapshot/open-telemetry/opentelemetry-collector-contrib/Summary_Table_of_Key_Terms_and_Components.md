| Term / Component | Description | Key Files / Packages |
| :--- | :--- | :--- |
| `pdata` | The internal protocol data format used by the collector for all telemetry. | [receiver/datadogreceiver/go.mod:36-36]() |
| `Factory` | The entry point for creating instances of a component. | [connector/datadogconnector/go.mod:10-14]() |
| `ocb` | OpenTelemetry Collector Builder. | [cmd/otelcontribcol/builder-config.yaml:1-5]() |
| `mdatagen` | Tool for generating component code from metadata. | [.github/CODEOWNERS:21-27]() |
| `testbed` | Framework for end-to-end performance testing. | [testbed/go.mod:1-38]() |
| `telemetrygen` | Tool for generating synthetic telemetry data for testing. | [.github/CODEOWNERS:26-26]() |
| `golden` | Testing utility for comparing actual output against expected "golden" files. | [pkg/golden/go.mod:1-5]() |

**Sources:**
[cmd/otelcontribcol/builder-config.yaml:1-15](), [.github/CODEOWNERS:1-100](), [testbed/go.mod:1-50](), [receiver/datadogreceiver/go.mod:21-22]()