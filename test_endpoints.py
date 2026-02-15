import requests
import json

API_URL = "http://localhost:8000"

print("=" * 60)
print("TESTING ALLERGEN ALCHEMIST API ENDPOINTS")
print("=" * 60)

# Test 1: Get Allergens
print("\n1. Testing /allergens endpoint...")
try:
    response = requests.get(f"{API_URL}/allergens")
    if response.status_code == 200:
        allergens = response.json()
        print(f"   ✓ SUCCESS: Found {len(allergens)} allergens")
        print(f"   Allergens: {allergens[:3]}...")
    else:
        print(f"   ✗ FAILED: Status {response.status_code}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

# Test 2: Analyze Recipe
print("\n2. Testing /analyze_recipe endpoint...")
try:
    payload = {
        "recipe_name": "Apple Pie",
        "user_allergens": ["Egg_Allergy", "Dairy_Allergy"]
    }
    response = requests.post(f"{API_URL}/analyze_recipe", json=payload)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ SUCCESS: Recipe '{data.get('recipe_title')}' analyzed")
        print(f"   Found issues: {data.get('found_issues')}")
        if data.get('substitutions'):
            print(f"   Substitutions: {len(data['substitutions'])} ingredients")
    else:
        print(f"   ✗ FAILED: Status {response.status_code}")
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

# Test 3: Generate Diet Plan
print("\n3. Testing /generate_diet_plan endpoint...")
try:
    payload = {
        "user_allergens": ["Egg_Allergy"],
        "diet_preference": "both"
    }
    response = requests.post(f"{API_URL}/generate_diet_plan", json=payload)
    if response.status_code == 200:
        data = response.json()
        weekly_plan = data.get('weekly_plan', [])
        print(f"   ✓ SUCCESS: Generated {len(weekly_plan)} days")
        if weekly_plan:
            day1 = weekly_plan[0]
            print(f"   {day1['day']}: {day1['breakfast']}, {day1['lunch']}, {day1['dinner']}")
    else:
        print(f"   ✗ FAILED: Status {response.status_code}")
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

# Test 4: Get Nutrition
print("\n4. Testing /get_nutrition endpoint...")
try:
    payload = {
        "recipe_name": "Chicken Curry"
    }
    response = requests.post(f"{API_URL}/get_nutrition", json=payload)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ SUCCESS: Nutrition for '{data.get('recipe_title')}'")
        print(f"   Calories: {data.get('calories')}kcal, Protein: {data.get('protein')}g")
        print(f"   Carbs: {data.get('carbs')}g, Fat: {data.get('fat')}g")
    else:
        print(f"   ✗ FAILED: Status {response.status_code}")
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

print("\n" + "=" * 60)
print("TESTING COMPLETE")
print("=" * 60)
