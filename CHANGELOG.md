# Changelog

## 0.1.0 (unreleased)

### Milestone 1 — Project Foundation

- `6f3d47f` Add pass framework exports and comprehensive tests
- `ee461d9` Add PassManager with dependency resolution and pipeline execution
- `97f3c4d` Add diagnostics framework and base pass abstraction
- `932fa33` Add comprehensive OKF round-trip tests
- `d498bf5` Add OKF parser and serializer for Markdown persistence
- `f1d2072` Add exceptions module and update package exports
- `80f56c9` Extend CI to lint tests/ and check formatting
- `4c978da` Add PEP 561 py.typed marker and gitignore SPEC.md
- `fe17398` Add KnowledgeGraph container and comprehensive model tests
- `190f43c` Add domain models: Entity, Concept, Fact, Relationship, Evidence
- Initial project structure and package layout with hatchling build backend
- Development tooling (ruff, mypy, pytest, CI)
- Documentation skeleton (mkdocs)
- Example project and test infrastructure

### Milestone 5 — Knowledge Extraction

- Add deterministic source readers (Markdown, plain text)
- Add EntityExtractor, ConceptExtractor, FactExtractor
- Add RelationshipExtractor with pattern-based entity relation detection
- Add EvidenceExtractor for capturing source evidence blocks
- Add ExtractionPipeline orchestrator and ExtractionPass compiler pass
- Add comprehensive extraction test suite

### Milestone 6 — Normalization

- Add StableIdGenerator and CanonicalIdGenerator for content-addressed IDs
- Add AliasResolver for consolidating entities with equivalent names
- Add DuplicateDetector for merging duplicate entities and concepts
- Add AliasResolutionPass and DuplicateDetectionPass compiler passes
- Add dependency-ordered normalization pipeline tests

### Milestone 8 — Semantic Verification

- Add ReasoningProvider interface for pluggable reasoning
- Add DeterministicReasoningProvider with rule-based consistency checking
- Add SemanticValidationPass for evidence, entity, and reference validation
- Add OntologyValidationPass for relationship type and taxonomy validation
- Add EvidenceValidationPass for provenance and coverage checks
- Add verification pipeline integration tests

### Milestone 7 — Verification Engine

- `0089194` Update package exports and add comprehensive tests
- `f3baa2b` Add public SDK, CLI, and extension system
- `8e11015` Add Verification Engine with converge loop
- `68711f5` Add automatic repair passes for knowledge graphs
- `d600114` Add consistency validation and quality scoring passes
- `05ff309` Add schema and structural validation passes
- `ec03862` Add KnowledgeGraph merge/diff methods and new exception types

### Milestone 7 — Verification Engine (details)

- SchemaValidationPass: required fields, valid IDs, duplicate detection
- StructuralValidationPass: orphaned relationship refs, evidence refs, duplicates
- ConsistencyValidationPass: contradictory facts, conflicting descriptions
- ScoringPass + KnowledgeScore: 5 quality dimensions with weighted overall score
- 4 repair passes: MergeDuplicateEntities, AttachProvenance, FixEvidenceRefs, NormalizeConfidence
- VerificationEngine: iterative converge loop with quality threshold
- VerificationResult: final graph, scores, diagnostics, repair metadata
- Knowledge class: create from text/file, read OKF documents, update with content
- OKFDocument: save, verify, inspect, score, diff, merge, update, delete
- CLI: 7 commands (create, read, update, verify, inspect, score, diff)
- Extension system: ExtensionRegistry with entry point discovery
- 5 new exception types for structured error handling
- 5 new test modules (53 tests) — all 243 passing, ruff/mypy clean

### Milestone 13 — Documentation

- `375497c` Comprehensive User Guide with create/read/update/verify/score/diff/merge/delete workflows
- `375497c` Full API Reference documenting Knowledge, OKFDocument, VerificationResult, CompilerPass, PassManager
- `375497c` Architecture Guide with layer diagrams, verification lifecycle, and compiler pipeline
- `375497c` Plugin Guide with extension points, entry point registration, and custom pass examples
- `375497c` Updated examples/basic_usage.py to use the real SDK
- `375497c` Updated mkdocs.yml navigation with all documentation sections

### Milestone 14 — Release Preparation

- `214852c` CONTRIBUTING.md with development setup, PR process, and code style
- `214852c` CODE_OF_CONDUCT.md (Contributor Covenant v2.1)
- `214852c` GitHub Actions release workflow for PyPI publishing
- `214852c` Benchmark infrastructure (pytest-benchmark) with verification, serialization, and creation benchmarks
- `214852c` Updated README.md with current milestone status and documentation links
- `214852c` Updated pyproject.toml with benchmark dependencies and test paths

### Code Quality & Refactoring

- `e6ae787` (2026-07-03) Update tests for refactored API
- `00d0512` (2026-07-03) Refactor SDK: public API, lifecycle methods, auto-verify on update
- `cbdb936` (2026-07-03) Refactor CLI, extensions, and reasoning modules
- `e7c8dac` (2026-07-03) Refactor VerificationEngine: register all passes, simplify scoring
- `45f239a` (2026-07-03) Refactor repair passes
- `8108eba` (2026-07-03) Refactor verification passes
- `79b53ad` (2026-07-03) Refactor ScoringPass: public API, shared constants, docstrings
- `c967672` (2026-07-03) Add KnowledgeScore, shared constants, and improve PassResult
- `bf9838b` (2026-07-03) Add docstrings and fix naming in pass modules
- `e71237a` (2026-07-03) Add comprehensive docstrings to OKF parser and serializer
- `1096097` (2026-07-03) Refactor extraction module
- `5ed5188` (2026-07-03) Consolidate normalization modules
- `0228e27` (2026-07-03) Refactor KnowledgeGraph: simplify merge/diff, remove unused helpers
- `afe90b4` (2026-07-03) Add module docstring to models/base.py
- `962988f` (2026-07-03) Add docstrings to model modules
- `c8f6246` (2026-07-03) Update passes module exports
- `a6b4f0d` (2026-07-03) Update __init__.py imports for renamed version module
- `de51f14` (2026-07-03) Rename _version.py to version.py and add new modules

### Code Quality & Refactoring (continued)

- `f6b72fa` (2026-07-03) docs: update documentation files
- `12e6310` (2026-07-03) docs: add docstrings to extraction module
- `b9d8a74` (2026-07-03) chore: update CI, README badges, gitignore, and cleanup.sh
- `1bbd338` (2026-07-03) test: expand test coverage to 98% and remove semi-private naming
- `a1a0dad` (2026-07-03) docs: add comprehensive docstrings across all modules
