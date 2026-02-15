import unittest
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

class TestAllergenAlchemist(unittest.TestCase):
    
    def test_analyze_valid_input(self):
        print("\nTesting: Valid Input (Peanut -> Nut_Allergy filter)")
        payload = {"ingredient_id": 12, "user_filter": "Nut_Allergy"}
        response = requests.post(f"{BASE_URL}/analyze", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("top_substitutes", data)
        self.assertGreater(len(data["top_substitutes"]), 0)
        
        # Check that results are NOT Peanut (which is 12)
        for sub in data["top_substitutes"]:
            self.assertNotEqual(sub["id"], 12)
            # Check safety: None of the top results should be Peanut or Nut related if mapped
            # But our map is simple. Peanut -> Nut_Allergy.
            # If candidate is "Almond" (id ?), it maps to "Nut_Allergy".
            # So "Almond" should be filtered out.
            
    def test_analyze_invalid_id(self):
        print("\nTesting: Invalid ID (99999)")
        payload = {"ingredient_id": 99999, "user_filter": "None"}
        response = requests.post(f"{BASE_URL}/analyze", json=payload)
        self.assertEqual(response.status_code, 404)
        
    def test_concurrency(self):
        print("\nTesting: Concurrency (5 requests)")
        import threading
        
        def make_request():
            payload = {"ingredient_id": 12, "user_filter": "None"}
            requests.post(f"{BASE_URL}/analyze", json=payload)
            
        threads = []
        start = time.time()
        for _ in range(5):
            t = threading.Thread(target=make_request)
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
        end = time.time()
        print(f"Time taken: {end - start:.2f}s")
        # Should be relatively fast if async works or threading works

if __name__ == "__main__":
    unittest.main()
