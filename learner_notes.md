# Integration 9B — Learner Notes

Document your design choices and what you learned. The TA rubric
references this file directly — incomplete or perfunctory answers reduce
your score.

## 1. Intents you handled and how you classified them

I handled the bounded set of 15 recipe-KG question shapes with a deterministic, priority-ordered rule system in `detect_shape`. The classifier normalizes the question by lowercasing it, trimming whitespace, and removing trailing punctuation. Then it applies regex and keyword rules from most specific to least specific.

The easiest shapes to classify were the ones with very distinctive wording, such as `q10` for “under <N> minutes”, `q11` for “ingredients used in <cuisine> recipes”, `q12` for “authors of <cuisine> recipes”, `q13` for “or any subtype”, and `q15` for “optionally tagged with <technique>”. These contain strong phrases that do not overlap much with other templates.

The ambiguous shapes were the ones that shared words like “use”, “recipes”, “author”, and cuisine names. For example, “Find recipes that use ginger but not garlic” contains the same “use ginger” pattern as `q1`, but the correct shape is `q14` because it includes negation. I handled this by checking `q14` before `q1`. Another example is “Find recipes by author Maria Rossi that use basil”. This could look like `q2` because it starts with an author pattern, and it could also look like `q1` because it contains an ingredient-use pattern. The correct shape is `q8`, so I check the author-plus-ingredient conjunction before the simpler author-only and ingredient-only rules.

A specific ambiguous case from the canonical evaluation set is “Find Sichuan recipes that use ginger”. Both `q5` and `q6` could produce a similar answer set when the cuisine has no deeper descendants, because the hierarchical traversal can collapse to the direct edge with `*0..`. However, the gold shape is `q5` because the question asks for a direct cuisine plus ingredient conjunction and does not ask for a cuisine subtree. I therefore classify direct cuisines such as Sichuan as `q5`, while broader hierarchical cuisines such as Asian or Chinese use the subtree templates `q4` or `q6`.

I also made sure that unsupported questions return `None` rather than guessing a shape. For example, a bare ingredient mention without a cue such as “use” or “with” is not classified as `q1`. This prevents silent false positives.

## 2. A question that worked end-to-end

One canonical question I tested end-to-end was:

```bash
python cli.py "Find recipes that use ginger"
```

The pipeline handled it as follows.

`detect_shape` returned:

```python
ShapeId.Q1
```

`extract_slots` returned:

```python
{"ingredient": "ginger"}
```

`compile_to_cypher` returned the canonical Cypher template for `q1`, using a parameter placeholder instead of string interpolation:

```cypher
MATCH (r:Recipe)-[:USES_INGREDIENT]->(:Ingredient {name: $ingredient})
RETURN r.name AS recipe
ORDER BY r.name
LIMIT 50
```

The bound params dict was:

```python
{"ingredient": "ginger"}
```

The driver then executed:

```python
session.run(cypher, **params)
```

and converted each Neo4j row with `row.data()` so the final Python return type was a list of dictionaries keyed by the Cypher `RETURN` aliases.

The CLI printed JSON rows in this shape:

```json
[
  {
    "recipe": "..."
  }
]
```

This confirmed that the full path worked: natural-language question → shape detection → slot extraction → canonical Cypher lookup → parameterized Neo4j execution → JSON-style CLI output. The exact recipe names come from the fixture data, but the important behavior is that the result rows are returned under the `recipe` alias from the canonical template.

## 3. A failure mode you diagnosed

A failure mode I diagnosed was an adversarial/off-template question:

```bash
python cli.py "find tomato which is a fruit"
```

This question contains the ingredient word “tomato”, but it does not contain the required cue pattern such as “use <ingredient>” or “with <ingredient>”. A naive classifier that simply scans for known ingredient names could incorrectly classify it as `q1`. My classifier avoids that by requiring the supported template wording.

The pipeline correctly treated this as unsupported. `detect_shape` returned `None`, and `pipeline.answer` raised `UnsupportedQueryError` instead of returning an empty list. The CLI output was:

```text
Question shape not supported: 'find tomato which is a fruit'
Supported shapes:
  - q1: Find recipes that use <ingredient>
  - q2: Find recipes by author <name>
  - q3: Find <cuisine> recipes
  - q4: Find recipes in a cuisine and all subtypes (e.g., 'Asian recipes')
  - q5: Find <cuisine> recipes that use <ingredient>
  - q6: Find recipes in a cuisine subtree that use <ingredient>
  - q7: Find recipes that require <technique> technique
  - q8: Find recipes by author <name> that use <ingredient>
  - q9: Find <cuisine> recipes ranked by popularity
  - q10: Find recipes with prep time under <N> minutes
  - q11: Find ingredients used in <cuisine> recipes
  - q12: Find authors of <cuisine> recipes (including subtypes)
  - q13: Find recipes that use <ingredient> or any subtype
  - q14: Find recipes that use <ingredient> but not <other-ingredient>
  - q15: Find recipes optionally tagged with <technique>
```

This is the desired fail-loud behavior. An empty list should mean “valid supported question, but no matching rows.” It should not mean “the mapper did not understand the question.” Raising `UnsupportedQueryError` preserves that diagnostic signal.

## 4. A design tradeoff between the deterministic mapper and the Tier 3 chain

I would prefer the deterministic mapper in production when the schema and question surface are bounded, as they are in this recipe-KG integration. The main advantages are auditability, low latency, and operational safety. Every supported question maps to a known `ShapeId`, every `ShapeId` maps to a static canonical Cypher template, and every slot value is passed through `$params`. This makes the system easier to test, easier to explain, and safer against Cypher injection. It is also grading-stable because the same input should always produce the same shape, the same template, and the same parameter structure.

The tradeoff is coverage cost. If users ask a sixteenth question shape, the deterministic mapper will reject it until an engineer adds a new rule, slot extraction logic, and canonical template. That is good for safety, but it is less flexible under distribution shift.

I would prefer the Tier 3 LLM chain when the user input is open-ended and the expected question shapes are not fully known in advance. The LLM chain can potentially generalize to new phrasings and new combinations of graph patterns without hand-authoring every template. This is valuable when schema coverage is changing quickly or when users ask questions in many different styles.

The tradeoff is operational risk and auditability. The Cypher emitted by an LLM is white-box after it is generated, but the generation process itself is less predictable than deterministic template lookup. The LLM may produce an invalid query, use the wrong relationship direction, omit a hierarchy traversal, or generate unsafe Cypher unless strict validation and allowlists are used. Therefore, I see the deterministic mapper as better for a bounded, high-confidence production path, while the Tier 3 chain is better as a flexible exploratory interface with strong guardrails.
