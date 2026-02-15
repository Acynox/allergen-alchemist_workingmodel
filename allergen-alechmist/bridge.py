
# Converted to lowercase for case-insensitive matching
ALLERGEN_MAP = {
    "peanut": "Nut_Allergy",
    "milk": "Lactose",
    "egg": "Egg_Allergy",
    "soy": "Soy_Allergy",
    "wheat": "Gluten",
    "shellfish": "Shellfish_Allergy",
    "fish": "Fish_Allergy",
    "tree nut": "Nut_Allergy",
    "cashew": "Nut_Allergy",
    "walnut": "Nut_Allergy",
    "almond": "Nut_Allergy",
    "hazelnut": "Nut_Allergy",
    "pecan": "Nut_Allergy",
    "pistachio": "Nut_Allergy",
    "macadamia": "Nut_Allergy",
    "crab": "Shellfish_Allergy",
    "lobster": "Shellfish_Allergy",
    "shrimp": "Shellfish_Allergy",
    "tuna": "Fish_Allergy",
    "salmon": "Fish_Allergy",
    "cod": "Fish_Allergy",
    "halibut": "Fish_Allergy",
    "sole": "Fish_Allergy",
    "tilapia": "Fish_Allergy",
    "trout": "Fish_Allergy",
    "catfish": "Fish_Allergy",
    "bass": "Fish_Allergy",
    "haddock": "Fish_Allergy",
    "pollock": "Fish_Allergy",
    "swordfish": "Fish_Allergy",
    "mahi mahi": "Fish_Allergy",
    "grouper": "Fish_Allergy",
    "snapper": "Fish_Allergy",
    "perch": "Fish_Allergy",
    "flounder": "Fish_Allergy",
    "sardine": "Fish_Allergy",
    "anchovy": "Fish_Allergy",
    "herring": "Fish_Allergy",
    "mackerel": "Fish_Allergy"
}


def get_allergen_category(ingredient_name: str) -> str:
    """
    Returns the allergen category for an ingredient, or None if not found.
    """
    return ALLERGEN_MAP.get(ingredient_name.lower())

def is_safe(ingredient_name: str, user_filter: str) -> bool:
    """
    Checks if an ingredient is safe for a given user filter.
    Returns True if safe, False otherwise.
    """
    allergen = get_allergen_category(ingredient_name)
    if allergen == user_filter:
        return False
    return True
