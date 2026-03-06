import re

def normalize_quantity(qty: str):
    """
    Converts quantity to a normalized base unit.
    Returns (value, unit) or (None, None)
    """
    qty = qty.replace(" ", "").lower()

    if qty.endswith("ml"):
        return int(qty.replace("ml", "")), "ml"

    if qty.endswith("l"):
        return int(float(qty.replace("l", "")) * 1000), "ml"

    if qty.endswith("g"):
        return int(qty.replace("g", "")), "g"

    if qty.endswith("kg"):
        return int(float(qty.replace("kg", "")) * 1000), "g"

    return None, None


def parse_query(query: str):
    """
    Examples:
    "amul milk 1l"
    "milk amul 1l"
    "1l milk"
    "milk"

    Output:
    {
        'product_keywords': ['milk'],
        'quantity': (1000, 'ml') or None
    }
    """
    query = query.lower()

    result = {
        "product_keywords": [],
        "quantity": None
    }

    # 1️⃣ Extract quantity (order independent)
    qty_match = re.search(r"\d+(\.\d+)?\s?(ml|l|kg|g)", query)
    if qty_match:
        value, unit = normalize_quantity(qty_match.group())
        result["quantity"] = (value, unit)
        query = query.replace(qty_match.group(), " ")

    # 2️⃣ Remaining words are product/brand keywords
    tokens = query.split()

    # remove very common filler words if any
    STOP_WORDS = {"of", "and", "with"}
    keywords = [t for t in tokens if t not in STOP_WORDS]

    result["product_keywords"] = keywords

    return result
