import requests
import json
from .constants import FLAVORDB_BASE_URL, RECIPEDB_BASE_URL, API_KEY

HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def get_molecules(ingredient_id):
    """
    Fetches the molecules for a given ingredient ID from FlavorDB.
    Returns a set of molecule common names (or some identifier).
    """
    url = f"{FLAVORDB_BASE_URL}/entities_json?id={ingredient_id}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # Inspect structure. Usually 'molecules' key exists.
            # If data is a list, take first item?
            # Based on user description, it returns details.
            # Let's handle list or dict.
            if isinstance(data, list):
                if not data: return set()
                data = data[0]
            
            molecules = set()
            # Structure could be 'molecules': [{'common_name': '...'}, ...]
            if 'molecules' in data:
                for mol in data['molecules']:
                    name = mol.get('common_name') or mol.get('pubchem_id')
                    if name:
                        molecules.add(name)
            return molecules
        else:
            print(f"Failed to fetch molecules for {ingredient_id}: {response.status_code}")
            return set()
    except Exception as e:
        print(f"Error fetching molecules for {ingredient_id}: {e}")
        return set()

def calculate_jaccard(set1, set2):
    """
    Calculates Jaccard Similarity between two sets.
    """
    if not set1 and not set2:
        return 0.0
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    if union == 0:
        return 0.0
    return intersection / union

def check_recipe_viability(ingredient_name):
    """
    Checks if there are recipes using this ingredient by searching RecipeDB.
    Returns True if > 0 recipes found.
    """
    # Using Recipe By Title as proxy since Recipe By Ingredient is elusive
    url = f"{RECIPEDB_BASE_URL}/recipe-bytitle/recipeByTitle?title={ingredient_name}"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            # recipes = data.get('recipes', []) # Structure Check
            # Based on lines 1220-1246 in postman file (Recipe By Title):
            # Response body: { "success": true, "data": [ ... ] }
            recipes = data.get("data", [])
            return len(recipes) > 0
        return False
    except Exception as e:
        print(f"Error checking viability for {ingredient_name}: {e}")
        return False

def search_recipe_by_title(title):
    try:
        url = f"{RECIPEDB_BASE_URL}/recipe-bytitle/recipeByTitle?title={title}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            recipes = data.get("data", [])
            if recipes:
                # Return first match
                r = recipes[0]
                # Try various keys for ID
                r_id = r.get("Recipe_id") or r.get("recipe_id")
                r_title = r.get("Recipe_title") or r.get("recipe_title")
                return {"id": r_id, "title": r_title}
        return None
    except Exception as e:
        print(f"Error searching recipe: {e}")
        return None

def get_recipe_ingredients(recipe_id):
    try:
        url = f"{RECIPEDB_BASE_URL}/search-recipe/{recipe_id}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            # The structure is { "recipe": {...}, "ingredients": [...] }
            # ingredients is a list of objects
            return data.get("ingredients", [])
        return []
    except Exception as e:
        print(f"Error fetching ingredients for {recipe_id}: {e}")
        return []
