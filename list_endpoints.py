import json

def list_endpoints():
    with open(r"c:\Users\sssha\Downloads\rdb2_postman_collection.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    def recurse(items, path=""):
        for item in items:
            name = item.get("name", "Unnamed")
            current_path = f"{path} -> {name}"
            
            if "item" in item:
                recurse(item["item"], current_path)
            elif "request" in item:
                req = item["request"]
                method = req.get("method")
                url = req.get("url")
                raw_url = url.get("raw") if isinstance(url, dict) else url
                print(f"{method} {raw_url} ({current_path})")

    if "item" in data:
        recurse(data["item"])

if __name__ == "__main__":
    list_endpoints()
