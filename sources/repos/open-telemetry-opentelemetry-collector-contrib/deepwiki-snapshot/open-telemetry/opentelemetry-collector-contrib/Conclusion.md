OTTL provides a powerful and flexible framework enabling end users to transform OpenTelemetry telemetry data declaratively. The system's core parser translates human-readable statements into executable logic using context-aware path resolution and a formal function factory system. Built-in editors support in-place modifications, while converters provide rich utilities for data manipulation, all designed to integrate seamlessly with the Collector’s internal pdata telemetry model.

This robust architecture facilitates extensible and safe telemetry transformations to meet diverse use cases in observability pipelines.

---

**Sources:**
[pkg/ottl/ottlfuncs/README.md:1-62](),
[pkg/ottl/parser.go:20-181](),
[pkg/ottl/parser_test.go:29-133](),
[pkg/ottl/functions.go:30-120](),
[pkg/ottl/expression.go:32-157](),
[pkg/ottl/contexts/ottllog/log.go:40-58](),
[pkg/ottl/contexts/ottlspanevent/span_events.go:40-140](),
[pkg/ottl/ottlfuncs/functions.go:10-140]()