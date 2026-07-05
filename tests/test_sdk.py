"""Tests for the SDK — Knowledge class."""

from unittest.mock import patch

from knowledge import Knowledge
from knowledge.models import Concept, KnowledgeGraph


def _sample_graph() -> KnowledgeGraph:
    c1 = Concept(id="intro", name="Introduction", description="Welcome.", tags=["guide"])
    c2 = Concept(id="usage", name="Usage", description="How to use it.", tags=["guide"])
    return KnowledgeGraph().add_concept(c1).add_concept(c2)


class TestKnowledge:
    def test_create(self) -> None:
        fake_html = "<html><body><h2>Intro</h2><p>Hi</p></body></html>"
        patches = [
            patch("knowledge.sdk.fetch_url", return_value=fake_html),
            patch("knowledge.llm.extractor.LLMExtractor.extract", return_value=_sample_graph()),
        ]
        with patches[0], patches[1]:
            knowledge = Knowledge()
            graph = knowledge.create("https://example.com/doc.html")
            assert isinstance(graph, KnowledgeGraph)
            assert len(graph.concepts) == 2

    def test_create_bundle(self) -> None:
        fake_html = "<html><body><h2>Intro</h2><p>Hi</p></body></html>"
        patches = [
            patch("knowledge.sdk.fetch_url", return_value=fake_html),
            patch("knowledge.llm.manager.KnowledgeBundleManager.create", return_value=2),
        ]
        with patches[0], patches[1]:
            knowledge = Knowledge()
            count = knowledge.create_bundle("https://example.com/doc.html", "/tmp/out")
            assert count == 2

    def test_update(self) -> None:
        fake_html = "<html><body><h2>Intro</h2><p>Hi</p></body></html>"
        patches = [
            patch("knowledge.sdk.fetch_url", return_value=fake_html),
            patch("knowledge.llm.manager.KnowledgeBundleManager.update", return_value=3),
        ]
        with patches[0], patches[1]:
            knowledge = Knowledge()
            count = knowledge.update("https://example.com/doc.html", "/tmp/bundle")
            assert count == 3

    def test_remove(self) -> None:
        with patch("knowledge.llm.manager.KnowledgeBundleManager.remove", return_value=1):
            knowledge = Knowledge()
            count = knowledge.remove(["intro"], "/tmp/bundle")
            assert count == 1

    def test_import(self) -> None:
        assert Knowledge is not None
