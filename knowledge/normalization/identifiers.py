"""Stable, deterministic identifier generation for knowledge elements.

Identifiers must survive updates, verification, repair, formatting,
and serialization. Identity represents meaning — not position inside
a document.
"""

from __future__ import annotations

import hashlib
import re


class StableIdGenerator:
    """Generates deterministic, content-addressed identifiers.

    The same content always produces the same ID. This ensures
    stability across serialization cycles and enables duplicate
    detection.
    """

    @staticmethod
    def generate(prefix: str, content: str, salt: str = "") -> str:
        """Generate a deterministic, content-addressed identifier.

        Args:
            prefix: Namespace prefix (e.g. ``"ent"``, ``"fact"``).
            content: The source content to hash.
            salt: Optional extra string to mix into the hash.

        Returns:
            A 16-character hex string identifier.
        """
        raw = f"{prefix}:{content.strip().lower()}{salt}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    @staticmethod
    def is_valid(element_id: str) -> bool:
        """Check whether a string is a valid stable identifier.

        Args:
            element_id: The identifier string to validate.

        Returns:
            True if the string matches the 16-char hex pattern.
        """
        return bool(re.match(r"^[a-f0-9]{16}$", element_id))


class CanonicalIdGenerator:
    """Generates canonical identifiers for normalized knowledge elements.

    Unlike StableIdGenerator which uses raw content, this generator
    strips whitespace, normalizes casing, and applies other
    normalizations before hashing.
    """

    @staticmethod
    def normalize_name(name: str) -> str:
        """Normalize a name for canonical comparison.

        Collapses whitespace and lowercases the input.

        Args:
            name: The name string to normalize.

        Returns:
            Normalized name string.
        """
        return re.sub(r"\s+", " ", name.strip().lower())

    @staticmethod
    def generate(prefix: str, name: str) -> str:
        """Generate a canonical identifier from a normalized name.

        Args:
            prefix: Namespace prefix.
            name: The source name to hash.

        Returns:
            A 16-character hex string identifier.
        """
        normalized = CanonicalIdGenerator.normalize_name(name)
        raw = f"{prefix}:{normalized}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    @staticmethod
    def entity_id(name: str) -> str:
        """Generate a deterministic entity ID from its name.

        Args:
            name: The entity name.

        Returns:
            A stable 16-character hex identifier.
        """
        return CanonicalIdGenerator.generate("ent", name)

    @staticmethod
    def concept_id(name: str) -> str:
        """Generate a deterministic concept ID from its name.

        Args:
            name: The concept name.

        Returns:
            A stable 16-character hex identifier.
        """
        return CanonicalIdGenerator.generate("concept", name)

    @staticmethod
    def fact_id(statement: str) -> str:
        """Generate a deterministic fact ID from its statement.

        Args:
            statement: The fact statement text.

        Returns:
            A stable 16-character hex identifier.
        """
        return CanonicalIdGenerator.generate("fact", statement)

    @staticmethod
    def relationship_id(source: str, rel_type: str, target: str) -> str:
        """Generate a deterministic relationship ID from its parts."""
        return CanonicalIdGenerator.generate("rel", f"{source}:{rel_type}:{target}")

    @staticmethod
    def evidence_id(content: str) -> str:
        """Generate a deterministic evidence ID from content."""
        return CanonicalIdGenerator.generate("ev", content)

    @staticmethod
    def source_id(source: str) -> str:
        """Generate a deterministic source ID."""
        return CanonicalIdGenerator.generate("src", source)
