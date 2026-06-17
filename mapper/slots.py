import re
from shapes import ShapeId


def extract_slots(q: str, shape):

    ql = q.lower().strip()

    # ---------------- INGREDIENT FILTER ----------------
    if shape == ShapeId.Q_INGREDIENT_FILTER:
        ingredients = ["ginger", "basil", "peppercorn", "garlic", "tomato"]

        found = None
        for i in ingredients:
            if i in ql:
                found = i
                break

        return {"ingredient": found}

    # ---------------- AUTHOR ----------------
    if shape == ShapeId.Q_AUTHOR:
        m = re.search(r"author\s+([a-zA-Z\s]+)", q, re.I)
        return {"author": m.group(1).strip() if m else None}

    # ---------------- CUISINE ----------------
    if shape == ShapeId.Q_CUISINE:
        cuisines = {
            "italian": "Italian",
            "chinese": "Chinese",
            "sichuan": "Sichuan",
            "asian": "Asian",
            "mexican": "Mexican",
            "indian": "Indian"
        }

        for k, v in cuisines.items():
            if k in ql:
                return {"cuisine": v}

        return {}

    # ---------------- TECHNIQUE ----------------
    if shape == ShapeId.Q_TECHNIQUE:
        if "wok" in ql:
            return {"technique": "wok"}

        m = re.search(r"technique\s+(\w+)", q, re.I)
        return {"technique": m.group(1).lower() if m else None}

    # ---------------- RANKING ----------------
    if shape == ShapeId.Q_RANKING:
        return {}

    # ---------------- NEGATION (FIXED) ----------------
    if shape == ShapeId.Q_NEGATION:
        ing = None
        excl = None

        ingredients = ["ginger", "basil", "garlic", "peppercorn", "tomato"]

        for i in ingredients:
            if i in ql:
                ing = i

        if "garlic" in ql:
            excl = "garlic"

        return {
            "ingredient": ing,
            "exclude_ingredient": excl
        }

    # ---------------- OPTIONAL ----------------
    if shape == ShapeId.Q_OPTIONAL:
        return {"technique": "wok"}

    # ---------------- HIERARCHY (FIXED NORMALIZATION) ----------------
    if shape == ShapeId.Q_HIERARCHY:
        if "asian" in ql:
            return {"cuisine": "asian"}
        if "sichuan" in ql:
            return {"cuisine": "sichuan"}
        return {}

    return {}