"""Tests for knowledge normalization — aliases, dedup, and normalization passes."""

from __future__ import annotations

from knowledge.models import Concept, Entity, KnowledgeGraph
from knowledge.normalization.aliases import AliasResolver
from knowledge.normalization.dedup import DuplicateDetector
from knowledge.normalization.identifiers import CanonicalIdGenerator, StableIdGenerator
from knowledge.passes import AliasResolutionPass, DuplicateDetectionPass, PassManager, Phase


class TestStableIdGenerator:
    def test_deterministic(self) -> None:
        id1 = StableIdGenerator.generate("ent", "Python")
        id2 = StableIdGenerator.generate("ent", "Python")
        assert id1 == id2

    def test_different_content_different_id(self) -> None:
        id1 = StableIdGenerator.generate("ent", "Python")
        id2 = StableIdGenerator.generate("ent", "JavaScript")
        assert id1 != id2

    def test_different_prefixes(self) -> None:
        id1 = StableIdGenerator.generate("ent", "Python")
        id2 = StableIdGenerator.generate("concept", "Python")
        assert id1 != id2

    def test_case_insensitive(self) -> None:
        """StableIdGenerator lowercases input for stability."""
        id1 = StableIdGenerator.generate("ent", "Python")
        id2 = StableIdGenerator.generate("ent", "python")
        assert id1 == id2  # deliberately case-insensitive

    def test_is_valid(self) -> None:
        eid = StableIdGenerator.generate("ent", "Test")
        assert StableIdGenerator.is_valid(eid)
        assert not StableIdGenerator.is_valid("invalid-id")
        assert not StableIdGenerator.is_valid("")


class TestCanonicalIdGenerator:
    def test_normalize_name(self) -> None:
        assert CanonicalIdGenerator.normalize_name("  Hello  World  ") == "hello world"

    def test_entity_id(self) -> None:
        eid = CanonicalIdGenerator.entity_id("Python")
        assert len(eid) == 16
        assert all(c in "0123456789abcdef" for c in eid)

    def test_deterministic(self) -> None:
        assert CanonicalIdGenerator.entity_id("Python") == CanonicalIdGenerator.entity_id("Python")

    def test_normalized_equivalence(self) -> None:
        assert CanonicalIdGenerator.entity_id("Python") == CanonicalIdGenerator.entity_id("python")

    def test_concept_id(self) -> None:
        cid = CanonicalIdGenerator.concept_id("Machine Learning")
        assert len(cid) == 16

    def test_fact_id(self) -> None:
        fid = CanonicalIdGenerator.fact_id("Python is a language.")
        assert len(fid) == 16


class TestAliasResolver:
    def test_no_duplicates(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_entity(Entity(name="Python", id="ent_001"))
        graph = graph.add_entity(Entity(name="JavaScript", id="ent_002"))
        resolver = AliasResolver()
        result = resolver.resolve(graph)
        assert len(result.entities) == 2

    def test_merges_duplicate_names(self) -> None:
        e1 = Entity(name="Python", id="ent_001")
        e2 = Entity(name="Python", id="ent_002")
        graph = KnowledgeGraph()
        graph = graph.add_entity(e1).add_entity(e2)
        resolver = AliasResolver()
        result = resolver.resolve(graph)
        assert len(result.entities) == 1

    def test_merges_aliases(self) -> None:
        e1 = Entity(name="Python", aliases=["Py"], id="ent_001")
        e2 = Entity(name="Python", aliases=["CPython"], id="ent_002")
        graph = KnowledgeGraph()
        graph = graph.add_entity(e1).add_entity(e2)
        resolver = AliasResolver()
        result = resolver.resolve(graph)
        merged = list(result.entities.values())[0]
        assert "Py" in merged.aliases
        assert "CPython" in merged.aliases

    def test_case_insensitive_matching(self) -> None:
        e1 = Entity(name="Python", id="ent_001")
        e2 = Entity(name="python", id="ent_002")
        graph = KnowledgeGraph()
        graph = graph.add_entity(e1).add_entity(e2)
        resolver = AliasResolver()
        result = resolver.resolve(graph)
        assert len(result.entities) == 1

    def test_empty_graph(self) -> None:
        resolver = AliasResolver()
        result = resolver.resolve(KnowledgeGraph())
        assert len(result.entities) == 0


class TestDuplicateDetector:
    def test_deduplicate_entities(self) -> None:
        detector = DuplicateDetector()
        e1 = Entity(name="Python", id="ent_001")
        e2 = Entity(name="Python", id="ent_002")
        e3 = Entity(name="JavaScript", id="ent_003")
        graph = KnowledgeGraph()
        graph = graph.add_entity(e1).add_entity(e2).add_entity(e3)
        result = detector.deduplicate_entities(graph)
        assert len(result.entities) == 2  # Python deduped, JavaScript remains

    def test_deduplicate_concepts(self) -> None:
        detector = DuplicateDetector()
        c1 = Concept(name="Machine Learning", id="con_001")
        c2 = Concept(name="Machine Learning", id="con_002")
        c3 = Concept(name="Deep Learning", id="con_003")
        graph = KnowledgeGraph()
        graph = graph.add_concept(c1).add_concept(c2).add_concept(c3)
        result = detector.deduplicate_concepts(graph)
        assert len(result.concepts) == 2

    def test_deduplicate_all(self) -> None:
        detector = DuplicateDetector()
        e1 = Entity(name="Python", id="ent_001")
        e2 = Entity(name="Python", id="ent_002")
        c1 = Concept(name="ML", id="con_001")
        c2 = Concept(name="ML", id="con_002")
        graph = KnowledgeGraph()
        graph = graph.add_entity(e1).add_entity(e2).add_concept(c1).add_concept(c2)
        result = detector.deduplicate_all(graph)
        assert len(result.entities) == 1
        assert len(result.concepts) == 1

    def test_empty_graph(self) -> None:
        detector = DuplicateDetector()
        result = detector.deduplicate_all(KnowledgeGraph())
        assert len(result.entities) == 0
        assert len(result.concepts) == 0


class TestAliasResolutionPass:
    def test_execute(self) -> None:
        passer = PassManager()
        passer.register(AliasResolutionPass())
        graph = KnowledgeGraph()
        graph = graph.add_entity(Entity(name="Python", id="ent_001"))
        graph = graph.add_entity(Entity(name="Python", id="ent_002"))
        result = passer.execute(graph)
        assert len(result.graph.entities) == 1
        assert len(result.diagnostics) == 1

    def test_no_entities(self) -> None:
        passer = PassManager()
        passer.register(AliasResolutionPass())
        result = passer.execute(KnowledgeGraph())
        assert len(result.diagnostics) == 0
        assert len(result.graph.entities) == 0


class TestDuplicateDetectionPass:
    def test_execute(self) -> None:
        passer = PassManager()
        passer.register(DuplicateDetectionPass())
        passer.register(AliasResolutionPass())  # dependency
        graph = KnowledgeGraph()
        graph = graph.add_entity(Entity(name="Python", id="ent_001"))
        graph = graph.add_entity(Entity(name="Python", id="ent_002"))
        result = passer.execute(graph)
        assert len(result.graph.entities) == 1

    def test_dependency_order(self) -> None:
        passer = PassManager()
        passer.register(DuplicateDetectionPass())
        passer.register(AliasResolutionPass())
        order = passer.resolve_order(phases=[Phase.NORMALIZATION])
        assert order.index("normalization.aliases") < order.index("normalization.dedup")


class TestNormalizationPipeline:
    def test_full_pipeline(self) -> None:
        passer = PassManager()
        passer.register(AliasResolutionPass())
        passer.register(DuplicateDetectionPass())
        graph = KnowledgeGraph()
        graph = graph.add_entity(Entity(name="Python", aliases=["Py"], id="ent_001"))
        graph = graph.add_entity(Entity(name="python", aliases=["CPython"], id="ent_002"))
        graph = graph.add_entity(Entity(name="Java", id="ent_003"))
        result = passer.execute(graph, phases=[Phase.NORMALIZATION])
        assert len(result.graph.entities) == 2
        merged = [e for e in result.graph.entities.values() if e.name == "Python"]
        if merged:
            assert "Py" in merged[0].aliases
            assert "CPython" in merged[0].aliases
