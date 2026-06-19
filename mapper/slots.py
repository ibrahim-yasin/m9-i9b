"""Slot extraction for the deterministic recipe KG mapper."""

import re

try:
    import spacy
except ImportError:
    spacy = None


from .shapes import ShapeId


_NLP = None


def _get_nlp():
    global _NLP

    if _NLP is not None:
        return _NLP

    if spacy is None:
        return None

    try:
        _NLP = spacy.load("en_core_web_sm")
    except OSError:
        _NLP = None

    return _NLP


CUISINES = [
    "World",
    "Asian",
    "Chinese",
    "Sichuan",
    "Italian",
    "French",
    "Thai",
    "Japanese",
    "Korean",
    "Indian",
    "Mexican",
    "American",
    "Mediterranean",
    "Middle Eastern",
    "Levantine",
    "Spanish",
]


INGREDIENTS = [
    "ginger",
    "garlic",
    "basil",
    "peppercorn",
    "tomato",
    "onion",
    "chicken",
    "beef",
    "pork",
    "fish",
    "shrimp",
    "rice",
    "noodles",
    "pasta",
    "egg",
    "milk",
    "butter",
    "cheese",
    "flour",
    "sugar",
    "salt",
    "pepper",
    "soy sauce",
    "vinegar",
    "olive oil",
    "sesame oil",
    "chili",
    "cumin",
    "coriander",
    "turmeric",
    "paprika",
    "parsley",
    "cilantro",
    "mint",
    "lemon",
    "lime",
    "potato",
    "carrot",
    "mushroom",
    "tofu",
]


TECHNIQUES = [
    "wok",
    "baking",
    "grilling",
    "roasting",
    "steaming",
    "frying",
    "stir-fry",
    "stir frying",
    "boiling",
    "braising",
    "simmering",
]


def _norm(question: str) -> str:
    q = question.strip()
    q = re.sub(r"[?!.]+$", "", q)
    q = re.sub(r"\s+", " ", q)
    return q


def _find_vocab(text: str, vocab: list[str]) -> str | None:
    text_lower = text.lower()

    # أطول اسم أولاً حتى "Middle Eastern" ينمسك قبل "Eastern" لو موجود.
    for item in sorted(vocab, key=len, reverse=True):
        pattern = r"\b" + re.escape(item.lower()) + r"\b"
        if re.search(pattern, text_lower):
            return item

    return None


def _extract_author(question: str) -> str:
    nlp = _get_nlp()

    if nlp is not None:
        doc = nlp(question)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text.strip()

    # fallback لو spaCy مش لاقط الاسم
    m = re.search(
        r"\bby author\s+(.+?)(?:\s+that\s+(?:use|uses|using|with)\b|$)",
        question,
        flags=re.IGNORECASE,
    )
    if m:
        return m.group(1).strip()

    m = re.search(
        r"\bby\s+(.+?)(?:\s+that\s+(?:use|uses|using|with)\b|$)",
        question,
        flags=re.IGNORECASE,
    )
    if m:
        return m.group(1).strip()

    raise ValueError("Could not extract author slot")


def _extract_cuisine(question: str) -> str:
    cuisine = _find_vocab(question, CUISINES)

    if cuisine is None:
        raise ValueError("Could not extract cuisine slot")

    return cuisine


def _extract_ingredient(text: str) -> str:
    ingredient = _find_vocab(text, INGREDIENTS)

    if ingredient is None:
        raise ValueError("Could not extract ingredient slot")

    return ingredient


def _extract_technique(question: str) -> str:
    technique = _find_vocab(question, TECHNIQUES)

    if technique is not None:
        return technique

    m = re.search(r"require\s+(.+?)\s+technique", question, flags=re.IGNORECASE)
    if m:
        return m.group(1).strip().lower()

    m = re.search(r"optionally tagged with\s+(.+)$", question, flags=re.IGNORECASE)
    if m:
        return m.group(1).strip().lower()

    raise ValueError("Could not extract technique slot")


def extract_slots(question: str, shape: ShapeId) -> dict:
    """Extract slots required by the shape's canonical Cypher template."""
    q = _norm(question)

    if shape == ShapeId.Q1:
        return {
            "ingredient": _extract_ingredient(q),
        }

    if shape == ShapeId.Q2:
        return {
            "author": _extract_author(q),
        }

    if shape == ShapeId.Q3:
        return {
            "cuisine": _extract_cuisine(q),
        }

    if shape == ShapeId.Q4:
        return {
            "cuisine": _extract_cuisine(q),
        }

    if shape == ShapeId.Q5:
        return {
            "cuisine": _extract_cuisine(q),
            "ingredient": _extract_ingredient(q),
        }

    if shape == ShapeId.Q6:
        return {
            "cuisine": _extract_cuisine(q),
            "ingredient": _extract_ingredient(q),
        }

    if shape == ShapeId.Q7:
        return {
            "technique": _extract_technique(q),
        }

    if shape == ShapeId.Q8:
        return {
            "author": _extract_author(q),
            "ingredient": _extract_ingredient(q),
        }

    if shape == ShapeId.Q9:
        return {
            "cuisine": _extract_cuisine(q),
        }

    if shape == ShapeId.Q10:
        m = re.search(r"under\s+(\d+)\s*minutes?", q, flags=re.IGNORECASE)

        if not m:
            raise ValueError("Could not extract max_minutes slot")

        return {
            "max_minutes": int(m.group(1)),
        }

    if shape == ShapeId.Q11:
        return {
            "cuisine": _extract_cuisine(q),
        }

    if shape == ShapeId.Q12:
        return {
            "cuisine": _extract_cuisine(q),
        }

    if shape == ShapeId.Q13:
        return {
            "ingredient": _extract_ingredient(q),
        }

    if shape == ShapeId.Q14:
        parts = re.split(r"\bbut not\b|\bwithout\b", q, flags=re.IGNORECASE)

        if len(parts) != 2:
            raise ValueError("Could not split positive/negative ingredient slots")

        positive_part = parts[0]
        negative_part = parts[1]

        return {
            "ingredient": _extract_ingredient(positive_part),
            "exclude_ingredient": _extract_ingredient(negative_part),
        }

    if shape == ShapeId.Q15:
        return {
            "technique": _extract_technique(q),
        }

    raise ValueError("Unsupported shape")