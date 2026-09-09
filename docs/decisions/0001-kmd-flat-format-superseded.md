# ADR-001: Use KMD flat format for v0.1, defer OKF v0.1 bundle to v0.2

**Status:** Superseded by ADR-002

**Date:** 2026-07-04

**Drivers:** @anomalyco

## Context

The `knowledge` SDK needs a persistence format for knowledge graphs. Two
candidates exist:

1. **Knowledge Markdown (KMD)** — A flat Markdown file where all elements
   (entities, concepts, facts, relationships, evidence) are serialised into
   a single document with `## Section: id` headings.

2. **Open Knowledge Format (OKF) v0.1** — A directory-bundle format
   (published by Google on 2026-06-13) consisting of an `index.md`,
   individual files per element, YAML frontmatter, and an `assets/`
   directory.

During early development, the flat Markdown approach was adopted for
simplicity. The question is whether to migrate to OKF v0.1 before the
v0.1.0 release.

## Options Considered

### Option A: Ship v0.1 with KMD, add OKF v0.1 in v0.2

- **Pro:** Fastest path to v0.1.0 release.
- **Pro:** KMD is already implemented, tested, and working (288 tests).
- **Pro:** KMD is simpler to debug — everything is one file.
- **Pro:** OKF v0.1 spec was only published 3 weeks ago; ecosystem
  conventions are still forming.
- **Con:** Users must eventually migrate from KMD to OKF.
- **Con:** KMD is not an industry standard.

### Option B: Implement OKF v0.1 for v0.1.0

- **Pro:** Industry-aligned format from the start.
- **Pro:** No format migration path for users.
- **Con:** Delays v0.1.0 by weeks or months.
- **Con:** OKF v0.1 spec is new and may change.
- **Con:** Adds significant complexity (directory I/O, file management,
  YAML parsing, asset handling).

### Option C: Support both formats in v0.1

- **Pro:** Users can choose.
- **Con:** Doubles maintenance burden for v0.1.
- **Con:** Unclear which format to treat as canonical.
- **Con:** Most users won't benefit from the dual support.

## Decision

**Accept Option A.** Ship v0.1.0 with KMD as the sole persistence format.
Implement OKF v0.1 directory bundle support in v0.2.0.

## Consequences

### Positive

- v0.1.0 can ship immediately.
- KMD is proven — 293 tests pass, 98 % coverage.
- OKF v0.1 implementation benefits from KMD experience and a settled
  internal model.

### Negative

- Users adopting v0.1.0 will need to migrate documents when OKF support
  lands in v0.2.0. A migration tool will be provided.
- KMD documents are not directly interoperable with OKF v0.1 tooling
  until a converter exists.

### Neutral

- The internal `KnowledgeGraph` model is format-agnostic — adding OKF
  v0.1 requires only a new parser and serializer pair, not model changes.
