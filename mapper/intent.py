from .shapes import ShapeId


def detect_shape(question: str) -> ShapeId | None:
    q = question.lower().strip()

    # ---------------- adversarial / meta FIRST ----------------
    if "(" in q and ")" in q:
        return None
    if "which is" in q or "meaning" in q:
        return None
    if "fruit" in q and "tomato" in q:
        return None

    # ---------------- NEGATION ----------------
    if "but not" in q or "without" in q:
        return ShapeId.Q14

    # ---------------- OPTIONAL ----------------
    if "optionally" in q or "optional" in q:
        return ShapeId.Q15

    # ---------------- HIERARCHY (IMPORTANT FIX) ----------------
    if "descendant" in q or "subtype" in q:
        return ShapeId.Q13

    # ---------------- RANKING ----------------
    if "ranked" in q or "popularity" in q:
        return ShapeId.Q9

    # ---------------- NUMERIC FILTER ----------------
    if "under" in q and "minute" in q:
        return ShapeId.Q10

    # ---------------- INVERSE ----------------
    if "ingredients used in" in q:
        return ShapeId.Q11

    if "authors of" in q:
        return ShapeId.Q12

    # ---------------- RELATIONAL COMPOSITE (Q8) ----------------
    if "by" in q and "use" in q:
        return ShapeId.Q8

    # ---------------- COMPOSITE (Q5) ----------------
    if "that use" in q and "recipes" in q:
        return ShapeId.Q5

    # ---------------- CUISINE + HIERARCHY (Q4) ----------------
    cuisines = ["asian", "sichuan", "italian", "mexican", "indian", "chinese"]
    if any(c in q for c in cuisines) and "recipes" in q:
        return ShapeId.Q4

    # ---------------- SIMPLE CUISINE (Q3) ----------------
    if any(c in q for c in cuisines):
        return ShapeId.Q3

    # ---------------- TECHNIQUE ----------------
    if "technique" in q or "require" in q or "wok" in q:
        return ShapeId.Q7

    # ---------------- INGREDIENT (Q1) ----------------
    ingredients = ["ginger", "garlic", "tomato", "onion"]
    if "use" in q or "with" in q:
        if not ("technique" in q or "require" in q):
            return ShapeId.Q1

    # ---------------- AUTHOR fallback ----------------
    if "by" in q:
        return ShapeId.Q2

    return None