import requests
import json
from allergen_alchemist.constants import RECIPEDB_BASE_URL, API_KEY
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def get_recipe_details(recipe_title):
    try:
        url = f"{RECIPEDB_BASE_URL}/recipe-bytitle/recipeByTitle?title={recipe_title}"
        print(f"Fetching: {url}")
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            recipes = data.get("data", [])
            if recipes:
                recipe = recipes[0]
                with open("recipe_keys.json", "w") as f:
                    json.dump(list(recipe.keys()), f)
                    f.write("\n\nSample:\n")
                    f.write(json.dumps(recipe, indent=2)[:2000])
                
                print("First Recipe Keys written to recipe_keys.json")
                
                # Guess keys based on sample
                r_id = recipe.get("Recipe_id") or recipe.get("recipe_id") or recipe.get("id")
                print(f"Resolved Recipe ID: {r_id}")
                
                # Fetch full details
                url_details = f"{RECIPEDB_BASE_URL}/search-recipe/{r_id}"
                print(f"Fetching Details: {url_details}")
                resp_details = requests.get(url_details, headers=HEADERS)
                if resp_details.status_code == 200:
                    details = resp_details.json()
                    
                    with open("recipe_details.json", "w") as f:
                        json.dump(details, f, indent=2)
                    print("Detailed recipe written to recipe_details.json")
                    
                    if "ingredients" in details:
                        print("Ingredients found in details!")
                        print(json.dumps(details["ingredients"], indent=2)[:500])
                    elif "Ingredients" in details:
                         print("Ingredients found in details (Capitalized)!")
                         print(json.dumps(details["Ingredients"], indent=2)[:500])
                    else:
                        print("Ingredients key NOT FOUND in details")
                        print("Keys available:", list(details.keys()))
                else:
                    print(f"Failed to fetch details: {resp_details.status_code}")
                
            else:
                print("No recipes found.")
        else:
            print(f"Failed: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_recipe_details("Apple Pie")
