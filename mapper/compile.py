from .shapes import CANONICAL_CYPHER, ShapeId


def compile_to_cypher(shape: ShapeId, slots: dict) -> tuple[str, dict]:

    try:
        template = CANONICAL_CYPHER[shape]
    except KeyError:
        raise KeyError(f"Missing Cypher template for shape: {shape}")

    clean_slots = {k: v for k, v in slots.items() if v is not None}

    return template, clean_slots