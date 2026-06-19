"""Compile a detected ShapeId and slots into canonical Cypher and params."""

from .shapes import CANONICAL_CYPHER


def compile_to_cypher(shape, slots: dict) -> tuple[str, dict]:
    """Return the canonical Cypher template and params dict."""
    template = CANONICAL_CYPHER[shape]
    return template, dict(slots)