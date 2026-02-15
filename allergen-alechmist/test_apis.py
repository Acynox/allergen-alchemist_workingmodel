import requests

FLAVORDB_BASE_URL = "https://cosylab.iiitd.edu.in/flavordb"
# Note: The user said /entities_json?id={id}

def test_flavordb():
    url = f"{FLAVORDB_BASE_URL}/entities_json?id=12"
    try:
        response = requests.get(url)
        print(f"FlavorDB Status: {response.status_code}")
        if response.status_code == 200:
            print("FlavorDB Response (first 200 chars):", response.text[:200])
        else:
            print("FlavorDB Failed")
    except Exception as e:
        print(f"FlavorDB Error: {e}")



def test_recipedb():
    base_url = "https://cosylab.iiitd.edu.in/recipe2-api"
    ingredient = "chicken"
    potential_endpoints = [
        f"/recipe/search_recipe?ingredient={ingredient}",
        f"/recipes?ingredient={ingredient}",
        f"/search?ingredient={ingredient}",
        f"/byingredient/ingredient?ingredient={ingredient}",
        f"/byingredients/ingredients?ingredients={ingredient}",
        f"/ingredients/search?ingredient={ingredient}",
        f"/recipe/by-ingredient?ingredient={ingredient}",
        f"/compute/search?ingredient={ingredient}", # Sometimes api is /compute/
        # Check patterns from file:
        # /recipe-bytitle/recipeByTitle?title=
        # /recipes-calories/calories?
        # /recipes-time/time? (inferred)
        # /recipes-method/method?
        # /recipes_cuisine/cuisine/
        
        # Maybe:
        f"/recipes-ingredient/ingredient?ingredient={ingredient}",
        f"/recipes-ingredients/ingredients?ingredients={ingredient}",
        f"/recipe-byingredient/recipeByIngredient?ingredient={ingredient}"
    ]
    
    headers = {"Authorization": "Bearer vK0t4SzgX3tCHSM5FkWveeEdx9E-XAZW-Ilw2sFJ8K-MA9uT"}
    
    for endpoint in potential_endpoints:
        url = f"{base_url}{endpoint}"
        try:
            print(f"Testing: {url}")
            response = requests.get(url, headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("SUCCESS!")
                print("Response (first 200 chars):", response.text[:200])
                return # Stop if found
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_flavordb()
    test_recipedb()
