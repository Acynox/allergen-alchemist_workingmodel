import uvicorn
import webbrowser
import threading
import time

def open_browser():
    time.sleep(2) # Wait for server to start
    webbrowser.open("http://localhost:8000/static/index.html")

if __name__ == "__main__":
    threading.Thread(target=open_browser).start()
    uvicorn.run("allergen_alchemist.main:app", host="0.0.0.0", port=8000, reload=True)
