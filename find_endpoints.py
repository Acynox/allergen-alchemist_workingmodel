import json

def list_endpoints():
    with open(r"c:\Users\sssha\Downloads\rdb2_postman_collection.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    out_file = open("found_endpoints.txt", "w", encoding="utf-8")
    
    def recurse(items, path=""):
        for item in items:
            if "item" in item:
                recurse(item["item"], path)
            elif "request" in item:
                req = item["request"]
                url = req.get("url")
                raw_url = url.get("raw") if isinstance(url, dict) else url
                if raw_url and "recipe2-api" in str(raw_url):
                    out_file.write(str(raw_url) + "\n")

    if "item" in data:
        recurse(data["item"])
        
    out_file.close()

if __name__ == "__main__":
    list_endpoints()
