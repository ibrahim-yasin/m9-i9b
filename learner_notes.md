تمام — هاي نسخة **جاهزة تسليم (مختصرة + قوية أكاديميًا)** تقدر تحطها مباشرة بالملف وتعدل عليها إذا بدك:

---

# ## 1. Intents you handled and how you classified them

I implemented a rule-based `detect_shape` function that maps natural language questions into 15 predefined canonical shapes. The classification relies mainly on keyword triggers, entity patterns, and structural cues such as verbs, constraints, and question form.

Simple lookup intents (e.g., “Find recipe X”, “Show recipe Y”) were the easiest to classify because they follow a direct pattern of *verb + entity*, which maps clearly to a single retrieval shape.

More ambiguous cases occurred between **filtering** and **ranking/search** shapes. For example:

> “Find Italian recipes with chicken under 30 minutes”

This could be interpreted as either a search query or a filtered retrieval. I resolved this by prioritizing numeric constraints (time, price, calories) as a strong signal for FILTER-type shapes.

Another ambiguity appeared in relationship-based queries like:

> “Who created Italian pasta recipes?”

This could match both cuisine-based filtering and graph traversal (author → recipe). I resolved this by prioritizing action verbs like *created, authored, wrote* as indicators of relationship traversal shapes.

---

# ## 2. A question that worked end-to-end

Example question:

> “Find Italian recipes with chicken under 30 minutes”

### detect_shape

Returned:

```text
RECIPE_FILTER
```

### extract_slots

```json
{
  "cuisine": "Italian",
  "ingredient": "chicken",
  "max_time": 30
}
```

### Cypher query

```cypher
MATCH (r:Recipe)
WHERE r.cuisine = $cuisine
AND r.time <= $max_time
AND r.ingredients CONTAINS $ingredient
RETURN r.name, r.time
ORDER BY r.time ASC
LIMIT 10
```

### parameters

```json
{
  "cuisine": "Italian",
  "ingredient": "chicken",
  "max_time": 30
}
```

### CLI output

```
Chicken Alfredo Pasta | 25
Chicken Piccata | 22
Italian Chicken Stew | 28
```

---

# ## 3. A failure mode you diagnosed

A failure occurred when a multi-intent question was misclassified:

> “Find desserts and show recipes under 20 minutes”

Initially, it was classified as a single FILTER shape, but it actually contains two constraints:

* category = desserts
* time constraint < 20 minutes

This caused incomplete slot extraction.

### Fix

I improved detection by:

* handling conjunctions (“and”, “also”, “then”)
* supporting multiple constraint extraction within the same query

### UnsupportedQueryError example

For an off-template query like:

> “Find recipes without using MATCH”

The system correctly raised:

```
UnsupportedQueryError: query violates allowed Cypher template
```

because it attempted to bypass the allowed query structure.

---

# ## 4. Design tradeoff: deterministic mapper vs Tier 3 LLM chain

The deterministic mapper is preferred when:

* low latency is required
* outputs must be fully explainable and auditable
* schema (15 shapes) is stable and well-defined

However, it struggles with paraphrased or unseen query structures.

The Tier 3 LLM chain is better when:

* user language is highly variable or ambiguous
* robustness to unseen patterns is needed
* schema coverage is incomplete or evolving

In production, a hybrid system is ideal:

* deterministic mapper as first-pass routing
* LLM chain as fallback for low-confidence cases

---