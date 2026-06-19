"""Deterministic intent/shape detection for the recipe KG."""

import re

from .shapes import ShapeId


def _norm(question: str) -> str:
    q = question.strip().lower()
    q = re.sub(r"[?!.]+$", "", q)
    q = re.sub(r"\s+", " ", q)
    return q


HIERARCHICAL_CUISINES = {
    "asian",
    "chinese",
    "world",
}

DIRECT_CUISINES = {
    "italian",
    "sichuan",
    "french",
    "thai",
    "japanese",
    "korean",
    "indian",
    "mexican",
    "american",
    "mediterranean",
    "middle eastern",
    "levantine",
    "spanish",
}


def _has_use_cue(q: str) -> bool:
    return bool(re.search(r"\b(use|uses|using|with)\b", q))


def detect_shape(question: str) -> ShapeId | None:
    """Classify question into one of the 15 ShapeId values, or None."""
    q = _norm(question)

    # q15: Find recipes optionally tagged with <technique>
    if re.fullmatch(r"find recipes optionally tagged with .+", q):
        return ShapeId.Q15

    # q14: Find recipes that use ginger but not garlic
    # Must come before q1.
    if re.fullmatch(r"find recipes that (use|uses|using|with) .+ (but not|without) .+", q):
        return ShapeId.Q14

    # q13: Find recipes that use peppercorn or any subtype/kind
    if re.fullmatch(r"find recipes that (use|uses|using|with) .+ or any (subtype|kind)", q):
        return ShapeId.Q13

    # q10: Find recipes with prep time under 30 minutes
    if re.fullmatch(r"find recipes with prep time under \d+\s*minutes?", q):
        return ShapeId.Q10

    # q11: Find ingredients used in Italian recipes
    if re.fullmatch(r"find ingredients used in .+ recipes", q):
        return ShapeId.Q11

    # q12: Find authors of Sichuan recipes
    if re.fullmatch(r"find authors of .+ recipes", q):
        return ShapeId.Q12

    # q9: Find Italian recipes ranked by popularity / most popular Italian recipes
    if re.fullmatch(r"find .+ recipes ranked by popularity", q):
        return ShapeId.Q9

    if re.fullmatch(r"find most popular .+ recipes", q):
        return ShapeId.Q9

    # q8: Find recipes by author Maria Rossi that use basil
    # Must come before q2 and q1.
    if re.fullmatch(r"find recipes by author .+ that (use|uses|using|with) .+", q):
        return ShapeId.Q8

    if re.fullmatch(r"find recipes by .+ that (use|uses|using|with) .+", q):
        return ShapeId.Q8

    # q7: Find recipes that require wok technique
    if re.fullmatch(r"find recipes that require .+ technique", q):
        return ShapeId.Q7

    # q5/q6: Find Sichuan/Chinese recipes that use ginger
    m = re.fullmatch(r"find (.+) recipes that (use|uses|using|with) (.+)", q)
    if m:
        cuisine = m.group(1).strip()

        if cuisine in HIERARCHICAL_CUISINES:
            return ShapeId.Q6

        if cuisine in DIRECT_CUISINES:
            return ShapeId.Q5

        return None

    # q2: Find recipes by author Maria Rossi / Find recipes by Maria Rossi
    if re.fullmatch(r"find recipes by author .+", q):
        return ShapeId.Q2

    if re.fullmatch(r"find recipes by .+", q):
        return ShapeId.Q2

    # q1: Find recipes that use ginger
    # Bare ingredient names are NOT supported.
    if re.fullmatch(r"find recipes that (use|uses|using|with) .+", q):
        return ShapeId.Q1

    # q3/q4: Find Italian/Asian recipes
    m = re.fullmatch(r"find (.+) recipes", q)
    if m:
        cuisine = m.group(1).strip()

        if cuisine in HIERARCHICAL_CUISINES:
            return ShapeId.Q4

        if cuisine in DIRECT_CUISINES:
            return ShapeId.Q3

        return None

    return None