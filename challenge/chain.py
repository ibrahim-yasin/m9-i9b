from typing import Any
import json

def run_chain(driver, llm_client, question: str) -> dict[str, Any]:
    result = {
        "question": question,
        "cypher": None,
        "params": {},
        "rows": [],
        "rejected": False,
        "rejection_reason": None
    }

    prompt = build_prompt(question)

    llm_output = llm_client.invoke(prompt)
    text = getattr(llm_output, "content", str(llm_output))

    cypher = None
    params = {}

    for line in text.splitlines():
        line = line.strip()

        if line.lower().startswith("cypher:"):
            cypher = line.split(":", 1)[1].strip()

        elif line.lower().startswith("params:"):
            try:
                params = json.loads(line.split(":", 1)[1].strip())
            except:
                params = {}

    result["cypher"] = cypher
    result["params"] = params

    if not cypher:
        return result

    # allowlist validation
    validate_query_shape(cypher)

    # execute
    with driver.session() as session:
        records = session.run(cypher, **params)
        result["rows"] = [r.data() for r in records]

    return result