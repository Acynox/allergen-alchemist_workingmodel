# Allergen Alchemist Backend

This is the backend service for the Allergen Alchemist application.

## Structure
- `main.py`: FastAPI application entry point.
- `bridge.py`: Allergen filtering logic (Case-insensitive).
- `chem_utils.py`: Utilities for FlavorDB and RecipeDB interactions.
- `fetch_candidates.py`: Script to populate `candidates.json` from RecipeDB.
- `candidates.json`: Cached list of safe ingredients.
- `constants.py`: Configuration and API keys.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running
Run the server using the runner script:
```bash
python run.py
```
The server will start at `http://0.0.0.0:8000`.

## API Usage
**Endpoint:** `POST /analyze`

**Payload:**
```json
{
  "ingredient_id": 12,
  "user_filter": "Nut_Allergy"
}
```

## Recent Fixes
- **Concurrency**: Switched to thread-pool execution for blocking API calls.
- **Caching**: Implemented caching for Molecules and Recipe Verification to improve performance.
- **Robustness**: Fixed case-sensitivity issues in Allergen Map.
- **Data Fetching**: Cleaned up `fetch_candidates.py` to skip invalid categories.
