# Plugin Guide

The `knowledge` SDK is designed to be extensible. Third-party packages
can contribute custom compiler passes without modifying the core SDK.

## Extension Points

Extensions can contribute:

| Extension Point | Description |
|---|---|
| **Parser Passes** | Convert external formats into the Knowledge Model |
| **Extraction Passes** | Extract entities, facts, relationships, evidence |
| **Normalization Passes** | Resolve aliases, detect duplicates, normalize ontology |
| **Verification Passes** | Add custom validation rules |
| **Repair Passes** | Implement domain-specific repair strategies |
| **Scoring Passes** | Provide custom quality metrics |
| **Serialization Passes** | Support alternative output layouts |

## Writing a Plugin

Each plugin contributes one or more `CompilerPass` subclasses:

```python
from knowledge.passes import CompilerPass, PassResult, Phase

class ComplianceValidationPass(CompilerPass):
    id = "compliance.validation"
    phase = Phase.VERIFICATION
    depends_on = ("verification.schema",)
    version = "1.0.0"
    description = "Validate enterprise compliance rules"

    def execute(self, graph, config=None):
        diagnostics = []
        # ... validation logic ...
        return PassResult(graph=graph, diagnostics=diagnostics)
```

## Registering via Entry Points

Plugins are discovered through Python entry points. Add to your
package's `pyproject.toml`:

```toml
[project.entry-points."knowledge.passes"]
compliance = "my_plugin:ComplianceValidationPass"
```

The `ExtensionRegistry` discovers and registers all passes from
the `knowledge.passes` entry point group automatically.

## Configuration

Users can enable, disable, and configure passes:

```python
from knowledge.extensions import ExtensionConfig, ExtensionRegistry

registry = ExtensionRegistry()
config = ExtensionConfig(
    enabled_passes=["compliance.validation"],
    disabled_passes=["experimental.repair"],
    pass_config={"compliance.validation": {"strict_mode": True}},
)

manager = PassManager()
registry.apply_to(manager, config)
```

Or via TOML configuration:

```toml
[knowledge]
enabled_passes = [
    "compliance.validation",
    "ontology.enrichment",
]
disabled_passes = [
    "experimental.repair",
]
```

## Best Practices

1. **Single responsibility** — Each pass should do one thing well.
2. **Deterministic when possible** — Avoid randomness in validation and repair.
3. **Explicit dependencies** — Declare `depends_on` so the Pass Manager orders correctly.
4. **Stable IDs** — Use a unique, versioned pass ID (e.g., `"my_org.ontology.v2"`).
5. **Diagnostics** — Use the standard `Diagnostic` API; don't invent your own reporting.
6. **No side effects** — Passes should be stateless and produce new graph instances.

## Example: Custom Scoring Pass

```python
from knowledge.passes import CompassPass, PassResult, Phase, Diagnostic, Severity

class CoverageScoringPass(CompilerPass):
    id = "scoring.coverage"
    phase = Phase.SCORING

    def execute(self, graph, config=None):
        total = len(graph.entities) + len(graph.concepts)
        covered = sum(1 for e in graph.entities.values() if e.description)
        score = (covered / max(total, 1)) * 100.0
        diag = Diagnostic(
            severity=Severity.INFORMATION,
            message=f"Coverage score: {score:.1f}%",
            location="scoring.coverage",
        )
        return PassResult(graph=graph, diagnostics=[diag])
```
