# Python API

The `knowledge` package exposes a small, stable surface. The `Knowledge` class is the entry point for every operation; the sub-package classes (`LLMExtractor`, `BundleSerializer`, `KnowledgeBundleManager`) are available when you need finer control.

## Knowledge

::: knowledge.Knowledge
    options:
      show_source: true
      heading_level: 3
      members:
        - __init__
        - create
        - create_bundle
        - update
        - remove
        - remove_with_unknowns
        - read_source

## fetch_url

::: knowledge.sdk.fetch_url
    options:
      show_source: true
      heading_level: 3

## Models

### Concept

::: knowledge.models.Concept
    options:
      show_source: true
      heading_level: 4

### KnowledgeGraph

::: knowledge.models.KnowledgeGraph
    options:
      show_source: true
      heading_level: 4
      members:
        - add_concept
        - remove_concept

## LLMExtractor

::: knowledge.llm.extractor.LLMExtractor
    options:
      show_source: true
      heading_level: 4
      members:
        - __init__
        - extract
        - split_sections
        - split_html_headings
        - split_markdown_headings
        - extract_section

## BundleSerializer

::: knowledge.kmd.bundle.BundleSerializer
    options:
      show_source: true
      heading_level: 4
      members:
        - __init__
        - serialize
        - validate
        - find_path

## KnowledgeBundleManager

::: knowledge.llm.manager.KnowledgeBundleManager
    options:
      show_source: true
      heading_level: 4
      members:
        - __init__
        - create
        - update
        - remove
        - remove_with_unknowns
        - read_bundle

## Exceptions

::: knowledge.exceptions
    options:
      show_source: true
      heading_level: 3
