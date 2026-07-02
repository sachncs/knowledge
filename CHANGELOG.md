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
