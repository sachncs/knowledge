# API Reference

## Knowledge

The primary entry point for working with OKF documents.

```python
from knowledge import Knowledge

knowledge = Knowledge()
```

### `create(input, verify=True, fmt=None)`

Creates a new OKF document from a knowledge source.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `input` | `str` | File path or text content. File paths are auto-detected. |
| `verify` | `bool` | Run verification after creation. Default: `True` |
| `fmt` | `str or None` | Source format override (`"text"`, `"markdown"`). Auto-detected when `None`. |

**Returns:** `OKFDocument`

**Raises:** `UnsupportedSourceError` for unsupported input types.

```python
doc = knowledge.create("Python is a language.")
doc = knowledge.create("sources/overview.md")
doc = knowledge.create("Python is great.", verify=False)
```

### `read(path)`

Loads an existing OKF Markdown document from disk.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `path` | `str` | Path to an OKF `.md` file. |

**Returns:** `OKFDocument`

**Raises:** `ParseError` if the file cannot be parsed.

```python
doc = knowledge.read("knowledge.md")
```

### `update(okf, input, fmt=None)`

Updates an existing OKF document with additional knowledge.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `okf` | `OKFDocument` | The document to update. |
| `input` | `str` | New knowledge source (file path or text). |
| `fmt` | `str or None` | Source format override. |

**Returns:** `OKFDocument` (new instance)

```python
updated = knowledge.update(doc, "JavaScript is for web development.")
```

---

## OKFDocument

The primary object returned by the SDK. All operations produce new instances.

### `graph`

The underlying `KnowledgeGraph`. Read-only.

### `source`

The source identifier (file path or `None`).

### `verify(threshold=80.0)`

Runs the verification engine.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `threshold` | `float` | Quality threshold (0–100). Default: `80.0` |

**Returns:** `VerificationResult`

```python
result = doc.verify(threshold=95.0)
```

### `save(path)`

Writes the document to disk in OKF Markdown format.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `path` | `str` | Output file path. |

```python
doc.save("knowledge.md")
```

### `inspect()`

Returns a high-level overview of the document.

**Returns:** `dict` with keys: `entity_count`, `concept_count`, `fact_count`,
`relationship_count`, `evidence_count`, `verification_score`, `source`.

```python
info = doc.inspect()
print(info["entity_count"])
```

### `score()`

Computes document quality scores.

**Returns:** `KnowledgeScore` with fields: `overall`, `completeness`,
`consistency`, `evidence_quality`, `ontology_quality`, `metadata_completeness`.

```python
score = doc.score()
print(f"Overall: {score.overall:.1f}%")
```

### `diff(other)`

Computes semantic differences between two documents.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `other` | `OKFDocument` | The document to compare against. |

**Returns:** `dict` with keys like `entities_added`, `entities_removed`,
`facts_added`, `facts_removed`, etc.

```python
changes = doc_a.diff(doc_b)
print(f"Added: {changes['entities_added']}")
```

### `merge(other)`

Combines two OKF documents. Duplicate entities are merged; all elements
from both documents are preserved.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `other` | `OKFDocument` | The document to merge with. |

**Returns:** `OKFDocument` (new instance)

```python
merged = doc_a.merge(doc_b)
```

### `update(input, source=None, verify=False)`

Updates the document with new knowledge content.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `input` | `str` | Text content to update from. |
| `source` | `str or None` | Optional source identifier. |
| `verify` | `bool` | Run verification after update. Default: `False` |

**Returns:** `OKFDocument` (new instance)

```python
updated = doc.update("New information to add.", "chapter2.md")
```

### `delete(entity_id=None, relationship_id=None, fact_id=None)`

Removes knowledge safely. Dependent references are repaired automatically.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `entity_id` | `str or None` | Entity ID to remove. |
| `relationship_id` | `str or None` | Relationship ID to remove. |
| `fact_id` | `str or None` | Fact ID to remove. |

**Returns:** `OKFDocument` (new instance)

```python
updated = doc.delete(entity_id="ent_001")
updated = doc.delete(relationship_id="rel_001")
```

---

## Exceptions

All exceptions inherit from `KnowledgeError`.

| Exception | Description |
|---|---|
| `KnowledgeError` | Base exception for all SDK errors. |
| `ParseError` | Raised when parsing an OKF document fails. |
| `SchemaValidationError` | Raised when schema validation fails. |
| `SemanticValidationError` | Raised when semantic validation fails. |
| `VerificationError` | Raised when verification fails critically. |
| `MergeConflictError` | Raised when a merge encounters unresolvable conflicts. |
| `UnsupportedSourceError` | Raised when a source type is not supported. |

---

## VerificationResult

Returned by `verify()`.

| Field | Type | Description |
|---|---|---|
| `graph` | `KnowledgeGraph` | The verified graph. |
| `score` | `KnowledgeScore` | Quality scores. |
| `diagnostics` | `list[Diagnostic]` | All diagnostics produced. |
| `repairs_applied` | `int` | Number of repairs performed. |
| `iteration_count` | `int` | Verification iterations used. |
| `converged` | `bool` | Whether verification converged. |
| `threshold_met` | `bool` | Whether quality threshold was met. |

---

## Compiler Passes

### `Phase` enum

- `PARSING`
- `EXTRACTION`
- `NORMALIZATION`
- `ANALYSIS`
- `VERIFICATION`
- `REPAIR`
- `SCORING`
- `SERIALIZATION`

### `CompilerPass`

Base class for all passes.

```python
class MyPass(CompilerPass):
    id = "my.custom_pass"
    phase = Phase.VERIFICATION
    depends_on = ("verification.schema",)

    def execute(self, graph, config=None):
        # Validation or transformation logic
        return PassResult(graph=graph, diagnostics=[...])
```

### `PassManager`

Orchestrates pass registration and execution.

```python
manager = PassManager()
manager.register(SchemaValidationPass())
manager.register(StructuralValidationPass())
result = manager.execute(graph, phases=[Phase.VERIFICATION])
```
