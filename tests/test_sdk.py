"""Tests for the minimal SDK — Knowledge class."""

from knowledge import Knowledge
from knowledge.models import KnowledgeGraph


class TestKnowledge:
    def test_create_from_url(self) -> None:
        knowledge = Knowledge()
        graph = knowledge.create("https://google.github.io/styleguide/pyguide.html")
        assert isinstance(graph, KnowledgeGraph)
        assert len(graph.concepts) > 10

    def test_import(self) -> None:
        assert Knowledge is not None
