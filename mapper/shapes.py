from shapes import ShapeId

def detect_shape(q: str):
    ql = q.lower().strip()

    # ❌ adversarial
    if "(" in ql and ")" in ql:
        return None
    if "which is" in ql or "meaning" in ql:
        return None

    # ❌ negation
    if "but not" in ql or "without" in ql:
        return ShapeId.Q_NEGATION

    # ❌ optional
    if "optionally" in ql:
        return ShapeId.Q_OPTIONAL

    # ❌ ranking
    if "rank" in ql or "popularity" in ql or "highest" in ql:
        return ShapeId.Q_RANKING

    # ❌ hierarchy
    if "descendant" in ql or "subtype" in ql:
        return ShapeId.Q_HIERARCHY

    # ❌ author
    if "author" in ql or "by " in ql:
        return ShapeId.Q_AUTHOR

    # ❌ cuisine
    if any(x in ql for x in ["italian", "chinese", "sichuan", "asian"]):
        return ShapeId.Q_CUISINE

    # ❌ technique (FIXED)
    if "technique" in ql or "wok" in ql or "method" in ql:
        return ShapeId.Q_TECHNIQUE

    # ❌ ingredient filter (LAST)
    if "use" in ql or "with" in ql or "containing" in ql:
        return ShapeId.Q_INGREDIENT_FILTER

    return ShapeId.Q_SEARCH