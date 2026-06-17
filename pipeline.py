from mapper.errors import UnsupportedQueryError
from mapper.intent import detect_shape
from mapper.slots import extract_slots
from mapper.cypher import compile_cypher


def answer(driver, question):
    shape = detect_shape(question)

    if shape is None:
        raise UnsupportedQueryError()

    slots = extract_slots(question, shape)

    cypher = compile_cypher(shape, slots)

    if not cypher:
        raise UnsupportedQueryError()

    clean_slots = {k: v for k, v in slots.items() if v is not None}

    with driver.session() as session:
        result = session.run(cypher, **clean_slots)
        return [r.data() for r in result]