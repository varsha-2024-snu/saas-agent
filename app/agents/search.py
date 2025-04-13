import requests
from app.config import Config

def web_search(query: str, site: str = "notion.so") -> dict:
    """Search Google via Serper API with Notion focus"""
    url = "https://google.serper.dev/search"
    payload = {
        "q": f"site:{site} {query}",
        "gl": "us",
        "hl": "en"
    }
    headers = {
        "X-API-KEY": Config.SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.json() if response.status_code == 200 else None
    except Exception:
        return None