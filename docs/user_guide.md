# User Guide

## Creating Knowledge

The simplest way to create knowledge is from text or a file:

```python
from knowledge import Knowledge

knowledge = Knowledge()

# From text
doc = knowledge.create("Python is a programming language. It supports asynchronous programming.")

# From a file (auto-detected)
doc = knowledge.create("sources/overview.md")

# Skip verification for speed
doc = knowledge.create("Quick fact.", verify=False)
```

## Reading OKF Documents

```python
doc = knowledge.read("existing-knowledge.md")
print(doc.inspect())
```

## Updating Knowledge

```python
updated = doc.update("JavaScript is used for web development.")
# Or via the Knowledge class:
updated = knowledge.update(doc, "Additional information.")
```

## Verifying Documents

Verification validates structure, semantics, and evidence, then repairs
issues automatically:

```python
result = doc.verify(threshold=85.0)
print(f"Score: {result.score.overall}%")
print(f"Repairs applied: {result.repairs_applied}")
print(f"Converged: {result.converged}")
```

The verified graph is available at `result.graph`. Diagnostics explain
every issue found and repair performed.

## Inspecting Documents

```python
info = doc.inspect()
# {
#     "entity_count": 5,
#     "fact_count": 3,
#     "relationship_count": 2,
#     "evidence_count": 4,
#     "verification_score": 92.5,
#     "source": "sources/overview.md"
# }
```

## Scoring Quality

The SDK computes quality scores across five dimensions:

```python
score = doc.score()
print(f"Overall:         {score.overall:.1f}%")
print(f"Completeness:    {score.completeness:.1f}%")
print(f"Consistency:     {score.consistency:.1f}%")
print(f"Evidence:        {score.evidence_quality:.1f}%")
print(f"Ontology:        {score.ontology_quality:.1f}%")
print(f"Metadata:        {score.metadata_completeness:.1f}%")
```

## Comparing Documents

```python
changes = doc_a.diff(doc_b)
# {
#     "entities_added": ["ent_003"],
#     "entities_removed": [],
#     "facts_added": ["f_002"],
#     "facts_removed": ["f_001"],
#     ...
# }
```

## Merging Documents

```python
merged = doc_a.merge(doc_b)
```

## Deleting Knowledge

```python
# Remove an entity (related relationships are cleaned up)
updated = doc.delete(entity_id="ent_001")

# Remove a specific relationship
updated = doc.delete(relationship_id="rel_003")
```

## Saving Documents

```python
doc.save("output-knowledge.md")
```

## Using the CLI

```bash
# Create
knowledge create "Python is a language." -o knowledge.md

# Read and verify
knowledge verify knowledge.md

# Inspect
knowledge inspect knowledge.md

# Score
knowledge score knowledge.md

# Diff
knowledge diff before.md after.md

# Update
knowledge update knowledge.md "New information."
```

## Workflow Example

```python
from knowledge import Knowledge

# 1. Initialize
knowledge = Knowledge()

# 2. Create from source
doc = knowledge.create("project-overview.md")

# 3. Inspect initial state
print(doc.inspect())

# 4. Verify with quality threshold
result = doc.verify(threshold=80.0)
print(f"Quality: {result.score.overall}%")

# 5. Add more knowledge
doc = knowledge.update(doc, "additional-research.md")

# 6. Re-verify
result = doc.verify()

# 7. Save
doc.save("final-knowledge.md")
```
