import requests
import json
import time

RECIPEDB_BASE_URL = "https://cosylab.iiitd.edu.in/recipe2-api"
HEADERS = {"Authorization": "Bearer vK0t4SzgX3tCHSM5FkWveeEdx9E-XAZW-Ilw2sFJ8K-MA9uT"}

# Expanded categories based on common food groups
CATEGORIES = [
    "Fruit", "Vegetable", "Herbs and Spices", "Cereal", "Fish", "Meat", 
    "Bakery", "Dairy", "Plant", "Nut and Seed", "Pulse", "Seafood", "Beverage"
]

def fetch_candidates():
    candidates = []
    seen_ids = set()
    
    for category in CATEGORIES:
        print(f"Fetching {category}...")
        # Increase limit to get more candidates
        url = f"{RECIPEDB_BASE_URL}/ingredients/flavor/{category}?limit=100"
        try:
            response = requests.get(url, headers=HEADERS)
            if response.status_code == 200:
                data = response.json()
                items = data.get("data", [])
                # The structure in postman file line 2323 shows "data" is a list of objects
                # But wait, looking at line 2323 again:
                # "data": [ { "ingredient": "...", "flavordb_id": "..." } ]
                # But looking at line 3221: "payload": { "data": [ ... ] }
                # The structure might vary.
                # In line 2323 it was directly "data".
                
                if isinstance(items, list):
                    for item in items:
                        f_id = item.get("flavordb_id")
                        name = item.get("ingredient")
                        if f_id and f_id not in seen_ids:
                            candidates.append({
                                "name": name,
                                "id": int(f_id), # FlavorDB IDs are ints usually
                                "category": category
                            })
                            seen_ids.add(f_id)
            else:
                print(f"Failed to fetch {category}: {response.status_code}")
        except Exception as e:
            print(f"Error fetching {category}: {e}")
        time.sleep(1) # Be nice to API
        
    print(f"Fetched {len(candidates)} candidates.")
    with open("allergen_alchemist/candidates.json", "w") as f:
        json.dump(candidates, f, indent=2)

if __name__ == "__main__":
    fetch_candidates()
