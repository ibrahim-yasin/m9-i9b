"""End-to-end NL-question pipeline against the recipe KG."""

from mapper import (
    detect_shape,
    extract_slots,
    compile_to_cypher,
    UnsupportedQueryError,
)


def answer(driver, question: str) -> list[dict]:
    """Run the full NL question → Cypher → Neo4j result pipeline."""
    shape = detect_shape(question)

    if shape is None:
        raise UnsupportedQueryError(question)

    slots = extract_slots(question, shape)
    cypher, params = compile_to_cypher(shape, slots)

    with driver.session() as session:
        result = session.run(cypher, **params)
        return [row.data() for row in result]