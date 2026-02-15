from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import concurrent.futures

# Relative imports (assuming package structure)
try:
    from . import constants
    from . import bridge
    from . import chem_utils
except ImportError:
    import constants
    import bridge
    import chem_utils

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def read_root():
    return {"message": "Welcome to Allergen Alchemist API. Frontend is at /static/index.html"}

# In-memory cache for molecules
MOLECULE_CACHE = {}
# In-memory cache for recipe verification
RECIPE_VERIFICATION_CACHE = {}

def load_candidates():
    """
    Load candidates from constants or json file.
    """
    # 1. Try to load from candidates.json
    candidates_path = os.path.join(os.path.dirname(__file__), "candidates.json")
    if os.path.exists(candidates_path):
        try:
            with open(candidates_path, "r") as f:
                return json.load(f)
        except:
            pass
    # 2. Fallback
    return constants.DEFAULT_SAFE_CANDIDATES

CANDIDATES = load_candidates()

class AnalysisRequest(BaseModel):
    ingredient_id: int
    user_filter: str

class RecipeAnalysisRequest(BaseModel):
    recipe_name: str
    user_allergens: list[str]

class DietPlanRequest(BaseModel):
    user_allergens: list[str]
    diet_preference: str

class NutritionRequest(BaseModel):
    recipe_name: str

@app.get("/ingredients")
def get_ingredients():
    return CANDIDATES

@app.get("/allergens")
def get_allergens():
    # Return unique allergens from bridge.ALLERGEN_MAP's VALUES
    return sorted(list(set(bridge.ALLERGEN_MAP.values())))

def analyze_single_ingredient_logic(ingredient_id: int, user_allergens: list[str]):
    # 1. Fetch Molecule Profile
    input_molecules = chem_utils.get_molecules(ingredient_id)
    if not input_molecules:
        return []

    # 2. Filter Candidates (Safety Check)
    safe_candidates = []
    for cand in CANDIDATES:
        c_name = cand["name"]
        possible_issue = False
        for allergen in user_allergens:
            if not bridge.is_safe(c_name, allergen):
                possible_issue = True
                break
        
        if not possible_issue:
            safe_candidates.append(cand)
            
    # 3. Calculate Similarity
    scored_candidates = []
    for cand in safe_candidates:
        c_id = cand["id"]
        
        if c_id in MOLECULE_CACHE:
            c_molecules = MOLECULE_CACHE[c_id]
        else:
            c_molecules = chem_utils.get_molecules(c_id)
            if c_molecules:
                MOLECULE_CACHE[c_id] = c_molecules
        
        if c_molecules:
            score = chem_utils.calculate_jaccard(input_molecules, c_molecules)
            cand_copy = cand.copy()
            cand_copy["score"] = score
            
            # UNIQUE FEATURE: Common Molecules
            common = input_molecules.intersection(c_molecules)
            cand_copy["common_molecules"] = sorted(list(common))[:10] # Limit to top 10 for display
            
            scored_candidates.append(cand_copy)
            
    # 4. Sort
    scored_candidates.sort(key=lambda x: x["score"], reverse=True)
    top_3 = scored_candidates[:5] # Increase to top 5 for better options
    
    # 5. Verification
    final_results = []
    for cand in top_3:
        c_name = cand["name"]
        if c_name in RECIPE_VERIFICATION_CACHE:
            verified = RECIPE_VERIFICATION_CACHE[c_name]
        else:
            verified = chem_utils.check_recipe_viability(c_name)
            RECIPE_VERIFICATION_CACHE[c_name] = verified
        cand["verified"] = verified
        final_results.append(cand)
        
    return final_results

# Endpoint for single analysis removed as per request.

@app.post("/analyze_recipe")
def analyze_recipe(request: RecipeAnalysisRequest):
    recipe_name = request.recipe_name
    user_allergens = request.user_allergens
    
    # 1. Search Recipe
    recipe_info = chem_utils.search_recipe_by_title(recipe_name)
    if not recipe_info:
        raise HTTPException(status_code=404, detail="Recipe not found")
        
    r_id = recipe_info["id"]
    r_title = recipe_info["title"]
    
    # 2. Get Ingredients
    ingredients = chem_utils.get_recipe_ingredients(r_id)
    
    # 3. Assess Safety & Substitute
    analysis_results = []
    
    import concurrent.futures
    
    # Identify unsafe ingredients
    unsafe_ingredients = []
    for ing in ingredients:
        ing_name = ing.get("ingredient")
        matched_allergen = bridge.get_allergen_category(ing_name)
        
        if matched_allergen and matched_allergen in user_allergens:
            unsafe_ingredients.append(ing)

    # Process substitutes concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_map = {}
        for ing in unsafe_ingredients:
            ing_id = ing.get("ing_id")
            ing_name = ing.get("ingredient")
            if ing_id:
                 future = executor.submit(analyze_single_ingredient_logic, ing_id, user_allergens)
                 future_map[future] = ing_name
            else:
                pass
        
        for future in concurrent.futures.as_completed(future_map):
            ing_name = future_map[future]
            try:
                subs = future.result()
                analysis_results.append({
                    "original_ingredient": ing_name,
                    "substitutes": subs
                })
            except Exception as e:
                print(f"Error substituting {ing_name}: {e}")

    return {
        "recipe_title": r_title,
        "recipe_id": r_id,
        "found_issues": len(analysis_results) > 0,
        "substitutions": analysis_results
    }

@app.post("/generate_diet_plan")
def generate_diet_plan(request: DietPlanRequest):
    user_allergens = request.user_allergens
    diet_preference = request.diet_preference
    
    # Predefined recipe titles from RecipeDB to use as meal suggestions
    # These are categorized by meal type and dietary preference
    veg_recipes = {
        "breakfast": ["Pancakes", "Oatmeal", "French Toast", "Waffles", "Smoothie"],
        "lunch": ["Vegetable Soup", "Pasta Salad", "Veggie Burger", "Quinoa Bowl", "Vegetable Curry"],
        "dinner": ["Mushroom Risotto", "Vegetable Stir Fry", "Pasta Primavera", "Bean Burrito", "Vegetable Pizza"]
    }
    
    non_veg_recipes = {
        "breakfast": ["Scrambled Eggs", "Bacon and Eggs", "Egg Benedict", "Omelet", "Breakfast Burrito"],
        "lunch": ["Chicken Salad", "Fish Tacos", "Chicken Curry", "Beef Stir Fry", "Grilled Chicken"],
        "dinner": ["Grilled Steak", "Chicken Tikka Masala", "Fish and Chips", "Pork Chops", "Lamb Curry"]
    }
    
    # Helper function to check if a recipe name suggests allergens (keyword-based)
    def recipe_has_allergen_keywords(recipe_title):
        """Quick keyword-based check for common allergens in recipe names"""
        title_lower = recipe_title.lower()
        
        allergen_keywords = {
            "Egg_Allergy": ["egg", "omelet", "benedict"],
            "Dairy_Allergy": ["cheese", "cream", "milk", "butter"],
            "Fish_Allergy": ["fish", "salmon", "tuna"],
            "Shellfish_Allergy": ["shrimp", "crab", "lobster", "shellfish"],
            "Nut_Allergy": ["nut", "peanut", "almond", "walnut"],
            "Soy_Allergy": ["soy", "tofu"],
            "Wheat_Allergy": ["wheat"],
            "Gluten": ["bread", "pasta", "wheat"]
        }
        
        for allergen in user_allergens:
            keywords = allergen_keywords.get(allergen, [])
            if any(keyword in title_lower for keyword in keywords):
                return True
        return False
    
    # Select recipe pool based on preference
    if diet_preference == "veg":
        recipe_pool = veg_recipes
    elif diet_preference == "non-veg":
        recipe_pool = non_veg_recipes
    else:  # both
        recipe_pool = {
            "breakfast": veg_recipes["breakfast"] + non_veg_recipes["breakfast"],
            "lunch": veg_recipes["lunch"] + non_veg_recipes["lunch"],
            "dinner": veg_recipes["dinner"] + non_veg_recipes["dinner"]
        }
    
    # Filter safe recipes using keyword matching (fast)
    if user_allergens:
        safe_recipes = {
            "breakfast": [r for r in recipe_pool["breakfast"] if not recipe_has_allergen_keywords(r)],
            "lunch": [r for r in recipe_pool["lunch"] if not recipe_has_allergen_keywords(r)],
            "dinner": [r for r in recipe_pool["dinner"] if not recipe_has_allergen_keywords(r)]
        }
    else:
        safe_recipes = recipe_pool
    
    # Fallback to generic meals if no safe recipes found
    if not safe_recipes["breakfast"]:
        safe_recipes["breakfast"] = ["Fresh Fruit Bowl", "Smoothie", "Toast with Jam"]
    if not safe_recipes["lunch"]:
        safe_recipes["lunch"] = ["Garden Salad", "Rice Bowl", "Vegetable Soup"]
    if not safe_recipes["dinner"]:
        safe_recipes["dinner"] = ["Grilled Vegetables", "Rice and Beans", "Baked Potato"]
    
    # Generate weekly plan
    import random
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekly_plan = []
    
    for day in days:
        weekly_plan.append({
            "day": day,
            "breakfast": random.choice(safe_recipes["breakfast"]),
            "lunch": random.choice(safe_recipes["lunch"]),
            "dinner": random.choice(safe_recipes["dinner"])
        })
    
    return {"weekly_plan": weekly_plan}

@app.post("/get_nutrition")
def get_nutrition(request: NutritionRequest):
    recipe_name = request.recipe_name
    
    # Search for recipe
    recipe_info = chem_utils.search_recipe_by_title(recipe_name)
    if not recipe_info:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    r_id = recipe_info["id"]
    r_title = recipe_info["title"]
    
    # Get ingredients
    ingredients = chem_utils.get_recipe_ingredients(r_id)
    
    # Estimate nutrition (simplified - in production, use a nutrition API)
    # This is a mock calculation based on ingredient count and types
    import random
    
    # Base values
    calories = random.randint(200, 800)
    protein = random.randint(10, 50)
    carbs = random.randint(20, 100)
    fat = random.randint(5, 40)
    fiber = random.randint(2, 15)
    sugar = random.randint(5, 30)
    
    # Adjust based on ingredient keywords (simplified)
    for ing in ingredients:
        ing_name = ing.get("ingredient", "").lower()
        if any(word in ing_name for word in ["chicken", "beef", "pork", "fish"]):
            protein += random.randint(10, 20)
            calories += random.randint(50, 150)
        if any(word in ing_name for word in ["rice", "pasta", "bread", "potato"]):
            carbs += random.randint(20, 40)
            calories += random.randint(100, 200)
        if any(word in ing_name for word in ["oil", "butter", "cream", "cheese"]):
            fat += random.randint(10, 20)
            calories += random.randint(80, 150)
    
    return {
        "recipe_title": r_title,
        "calories": calories,
        "protein": protein,
        "carbs": carbs,
        "fat": fat,
        "fiber": fiber,
        "sugar": sugar
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
