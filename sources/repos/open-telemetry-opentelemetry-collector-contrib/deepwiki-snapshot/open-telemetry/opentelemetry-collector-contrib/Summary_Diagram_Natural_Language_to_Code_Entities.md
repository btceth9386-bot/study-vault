```mermaid
graph LR
    NL_OTTL["OTTL Statement"]

    NL_Functions["Functions (Editors / Converters)"]
    NL_Paths["Path Expressions"]
    NL_Expressions["Boolean and Math Expressions"]
    NL_Contexts["Telemetry Contexts (log, span, metric, spanevent, etc.)"]

    CodeParser["ottl.Parser[K]"]
    CodeFunctions["Function Factory map (StandardFuncs)"]
    CodePathParser["PathExpressionParser[K]"]
    CodeStatements["ottl.Statement[K]"]
    CodeExecution["Statement.Execute(ctx, tCtx)"]
    CodeContext["TransformContext implementations"]
    CodeGetSetter["GetSetter[K] interfaces"]
    CodeEditors["Editor implementations (e.g., delete_key, flatten)"]
    CodeConverters["Converter implementations"]

    NL_OTTL --> NL_Functions
    NL_OTTL --> NL_Paths
    NL_OTTL --> NL_Expressions
    NL_OTTL --> NL_Contexts

    NL_Functions --> CodeFunctions
    NL_Paths --> CodePathParser
    NL_Contexts --> CodeContext

    CodeParser --> CodeStatements
    CodeParser --> CodeFunctions
    CodeParser --> CodePathParser

    CodeStatements --> CodeExecution
    CodeExecution --> CodeGetSetter
    CodeExecution --> CodeEditors
    CodeExecution --> CodeConverters

    CodeGetSetter --> CodeContext

    style NL_OTTL fill:#f9f9f9
    style CodeParser fill:#e1ffe1
    style CodeStatements fill:#ccf5cc
    style CodeExecution fill:#ccf5cc
```

This diagram illustrates the transition from a high-level OTTL statement specification in natural language form to the corresponding code entities involved in parsing, runtime path resolution, and execution of editing or converter functions within specific telemetry contexts.

---

# Summary Diagram: Function Categories and Context Usage

```mermaid
graph TB
    FunctionCategory["OTTL Function Category"]
    Editors["Editors (transform telemetry)"]
    Converters["Converters (utilities / computations)"]

    Contexts["Telemetry Contexts"]
    Logs["Log Context (ottllog)"]
    Spans["Span Context (ottlspan)"]
    SpanEvents["SpanEvent Context (ottlspanevent)"]
    Metrics["Metric Context (ottlmetric)"]

    Editors --> Logs
    Editors --> Spans
    Editors --> SpanEvents
    Editors --> Metrics

    Converters --> Logs
    Converters --> Spans
    Converters --> SpanEvents
    Converters --> Metrics

    FunctionCategory --> Editors
    FunctionCategory --> Converters

    style Editors fill:#ccf5cc
    style Converters fill:#d7d7d7
```

This diagram maps the two primary function types in OTTL—Editors and Converters—and their applicability within different telemetry contexts supported by the Collector's transformations.

---