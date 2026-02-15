
FLAVORDB_BASE_URL = "https://cosylab.iiitd.edu.in/flavordb"
RECIPEDB_BASE_URL = "https://cosylab.iiitd.edu.in/recipe2-api"
API_KEY = "vK0t4SzgX3tCHSM5FkWveeEdx9E-XAZW-Ilw2sFJ8K-MA9uT"

# Safe Candidates List (Mocked/Static)
# This will be overridden by fetch_candidates if it exists, or imported there.
# I'll put a default list here.
DEFAULT_SAFE_CANDIDATES = [
    {"name": "apple", "id": 1, "category": "Fruit"},
    {"name": "banana", "id": 2, "category": "Fruit"},
    {"name": "carrot", "id": 3, "category": "Vegetable"},
    {"name": "chicken", "id": 5, "category": "Meat"}, 
    # Add more...
]
