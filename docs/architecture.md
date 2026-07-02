# Architecture

The `knowledge` SDK is organized into independent layers with clear boundaries.
Each layer has a single responsibility and communicates through well-defined interfaces.

## Architectural Layers

```
Knowledge Sources
        │
        ▼
+--------------------------+
|  1. Source Layer         |
|  Markdown, PDF, HTML,    |
|  JSON, plain text, URLs  |
+--------------------------+
        │
        ▼
+--------------------------+
|  2. Extraction Layer     |
|  Entities, Concepts,     |
|  Facts, Relationships,   |
|  Evidence, Provenance    |
+--------------------------+
        │
        ▼
+--------------------------+
|  3. Canonical Knowledge  |
|    Model                 |
|  KnowledgeGraph          |
+--------------------------+
        │
        ▼
+--------------------------+
|  4. OKF Layer            |
|  Parser / Serializer     |
+--------------------------+
        │
        ▼
+--------------------------+
|  5. Verification Layer   |
|  Engine + Passes         |
|  Validate → Diagnose →   |
|  Repair → Rescore → Loop |
+--------------------------+
        │
        ▼
+--------------------------+
|  6. Public API Layer     |
|  Knowledge, OKFDocument  |
|  CLI                     |
+--------------------------+
        │
        ▼
Verified OKF Document
```

### 1. Source Layer

Responsible for reading external information. Supported source types
include Markdown, plain text, HTML (via extension), PDF (future), and
arbitrary plugins. The source layer never understands OKF — its only
responsibility is acquiring information.

### 2. Extraction Layer

Converts raw information into structured knowledge. The extraction
pipeline discovers entities, concepts, relationships, facts, and evidence
while preserving provenance. Extraction is deterministic and rule-based.

### 3. Canonical Knowledge Model

The internal representation used throughout the SDK. Every operation —
update, merge, delete, verify, inspect, score, diff — works against this
model. The model is **immutable**: every mutation produces a new instance.

### 4. OKF Layer

Responsible only for parsing and serializing OKF Markdown documents.
Business logic never depends on Markdown structure. This separation allows
internal evolution without affecting the persistence format.

### 5. Verification Layer

The iterative quality gate protecting knowledge integrity. Every mutation
passes through verification before completion. The engine runs a converge
loop: validate → diagnose → repair → rescore → repeat until quality
threshold is met or no further improvements are possible.

### 6. Public API Layer

Exposes the lifecycle of an OKF document through a minimal, predictable
API. The `Knowledge` class provides create/read/update entry points.
The `OKFDocument` class provides verify, save, inspect, score, diff,
merge, and delete operations. The CLI exposes all operations through
subcommands.

## Compiler Pipeline

```
Sources
    │
    ▼
Parser Passes        (Markdown → KnowledgeModel)
    │
    ▼
Extraction Passes    (text → Entities, Facts, Relationships)
    │
    ▼
Normalization Passes (alias resolution, duplicate detection, IDs)
    │
    ▼
Analysis Passes      (graph statistics, dependency analysis)
    │
    ▼
Verification Passes  (schema, structural, semantic, ontology, evidence)
    │
    ▼
Repair Passes        (merge entities, fix refs, attach provenance)
    │
    ▼
Scoring Passes       (completeness, consistency, evidence, ontology)
    │
    ▼
OKF Serialization
```

## Compiler Pass Design

Each pass is a class that extends `CompilerPass` and declares:

- **id** — Unique identifier (e.g., `"verification.schema"`)
- **phase** — Execution phase from `Phase` enum
- **depends_on** — Explicit dependency declarations
- **version** — Semantic version for the pass
- **execute(graph, config)** — The single entry point

Passes are registered with the `PassManager`, which resolves dependencies
and executes passes in the correct order.

## Verification Lifecycle

```
Knowledge Graph
    │
    ▼
Validation Passes  ───► Diagnostics
    │                       │
    ▼                       ▼
Repair Passes  ◄───────────┘
    │
    ▼
Updated Graph
    │
    ▼
Rescore
    │
    ▼
Converged? ──Yes──► Done
    │
    No
    ▼
  Repeat
```

## Extension System

Third-party packages can register additional passes through Python
entry points (`knowledge.passes` group). Extensions are discovered,
registered, and configured through the `ExtensionRegistry`. Each
extension contributes one or more compiler passes to the pipeline.
