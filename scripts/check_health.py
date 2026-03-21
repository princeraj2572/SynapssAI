"""Quick health check for all services."""
import httpx

services = {
    "API":      "http://localhost:8080/health",
    "Ollama":   "http://localhost:11434/api/tags",
    "Frontend": "http://localhost:3000",
}

for name, url in services.items():
    try:
        r = httpx.get(url, timeout=3)
        print(f"  {name:12} OK  ({r.status_code})")
    except Exception as e:
        print(f"  {name:12} DOWN  ({e})")
