# API Reference

## Knowledge

The primary entry point for working with OKF documents.

```python
from knowledge import Knowledge

knowledge = Knowledge()
```

### `create(input, fmt="text")`

Creates a new OKF document from a knowledge source. Verification runs automatically.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `input` | `str` | File path or text content. File paths are auto-detected. |
| `fmt` | `str` | Source format (`"text"`, `"markdown"`). Default: `"text"` |

**Returns:** `OKFDocument`

**Raises:** `UnsupportedSourceError` for unsupported input types.

```python
doc = knowledge.create("Python is a language.")
doc = knowledge.create("sources/overview.md")
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

### `update(doc, input, fmt="text")`

Updates an existing OKF document with additional knowledge. Verification runs automatically.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `doc` | `OKFDocument` | The document to update. |
| `input` | `str` | New knowledge source (file path or text). |
| `fmt` | `str` | Source format (`"text"`, `"markdown"`). Default: `"text"` |

**Returns:** `OKFDocument` (new instance)

```python
updated = knowledge.update(doc, "JavaScript is for web development.")
```

### `verify(doc, threshold=80.0, max_iterations=5)`

Verifies an existing OKF document.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `doc` | `OKFDocument` | The document to verify. |
| `threshold` | `float` | Quality threshold (0–100). Default: `80.0` |
| `max_iterations` | `int` | Maximum verification iterations. Default: `5` |

**Returns:** `VerificationResult`

```python
result = knowledge.verify(doc, threshold=95.0)
```

### `delete(doc, entity_id=None, relationship_id=None, fact_id=None, concept_id=None)`

Removes knowledge elements from a document.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `doc` | `OKFDocument` | The document to delete from. |
| `entity_id` | `str or None` | Entity ID to remove. |
| `relationship_id` | `str or None` | Relationship ID to remove. |
| `fact_id` | `str or None` | Fact ID to remove. |
| `concept_id` | `str or None` | Concept ID to remove. |

**Returns:** `OKFDocument` (new instance)

```python
updated = knowledge.delete(doc, entity_id="ent_001")
```

### `inspect(doc)`

Returns a high-level overview of a document.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `doc` | `OKFDocument` | The document to inspect. |

**Returns:** `dict`

```python
info = knowledge.inspect(doc)
```

### `score(doc)`

Computes document quality scores.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `doc` | `OKFDocument` | The document to score. |

**Returns:** `KnowledgeScore`

```python
score = knowledge.score(doc)
```

### `diff(a, b)`

Computes semantic differences between two documents.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `a` | `OKFDocument` | First document. |
| `b` | `OKFDocument` | Second document. |

**Returns:** `dict`

```python
changes = knowledge.diff(doc_a, doc_b)
```

### `merge(a, b)`

Merges two documents into one.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `a` | `OKFDocument` | Primary document. |
| `b` | `OKFDocument` | Document to merge in. |

**Returns:** `OKFDocument` (new instance)

```python
merged = knowledge.merge(doc_a, doc_b)
```

---

## OKFDocument

The primary object returned by the SDK. All operations produce new instances.

### `graph`

The underlying `KnowledgeGraph` (read-only property).

### `source`

The source identifier (file path or `None`).

### `verify(threshold=80.0, max_iterations=5)`

Runs the verification engine.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `threshold` | `float` | Quality threshold (0–100). Default: `80.0` |
| `max_iterations` | `int` | Maximum verification iterations. Default: `5` |

**Returns:** `VerificationResult`

```python
result = doc.verify(threshold=95.0)
```

### `save(path)`

Writes the document to disk in KMD (Knowledge Markdown) format.

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

### `update(content, source="unknown", fmt="text")`

Updates the document with new knowledge content.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `content` | `str` | Text content to extract knowledge from. |
| `source` | `str` | Source identifier for provenance. Default: `"unknown"` |
| `fmt` | `str` | Input format (`"text"`, `"markdown"`). Default: `"text"` |
**Returns:** `OKFDocument` (new instance)

```python
updated = doc.update("New information to add.", source="chapter2.md")
```

### `delete(entity_id=None, relationship_id=None, fact_id=None, concept_id=None)`

Removes knowledge safely. Dependent references are repaired automatically.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `entity_id` | `str or None` | Entity ID to remove. |
| `relationship_id` | `str or None` | Relationship ID to remove. |
| `fact_id` | `str or None` | Fact ID to remove. |
| `concept_id` | `str or None` | Concept ID to remove. |

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
| `ParseError` | Raised when parsing a KMD document fails. |
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
