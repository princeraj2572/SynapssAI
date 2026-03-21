import httpx
import json
from config import settings


async def ask_ollama(prompt: str, system: str = "", stream: bool = False) -> str:
    """Send a prompt to local Ollama and return the response."""
    url = f"{settings.OLLAMA_HOST}/api/generate"
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "system": system or "You are a personal AI life coach. You have access to the user's life data and provide helpful, specific, data-driven insights.",
        "stream": False,
    }
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
    except httpx.ConnectError:
        return "Ollama is not running. Start it with: ollama serve"
    except Exception as e:
        return f"LLM error: {str(e)}"


async def ask_with_context(query: str, memories: list) -> str:
    """RAG-enhanced query: inject retrieved memories as context."""
    if memories:
        context = "\n".join(f"- {m}" for m in memories)
        prompt = f"Context from your life data:\n{context}\n\nQuestion: {query}\n\nAnswer with specific insights based on the data above."
    else:
        prompt = query

    system = (
        "You are a personal AI life coach with access to the user's historical life data. "
        "Give specific, actionable, data-driven advice. Keep responses concise and practical. "
        "Reference the data context when available. If no context is provided, say so."
    )
    return await ask_ollama(prompt, system=system)


async def generate_weekly_digest(week_summary: dict) -> str:
    """Generate a narrative weekly digest from structured data."""
    data_str = json.dumps(week_summary, indent=2, default=str)
    prompt = (
        f"Here is the user's data for the past week:\n{data_str}\n\n"
        "Write a personal, friendly weekly digest (3-4 paragraphs) that:\n"
        "1. Summarises what went well\n"
        "2. Highlights key patterns or correlations noticed\n"
        "3. Gives 2-3 specific recommendations for next week\n"
        "Write in second person (you/your). Be specific, not generic."
    )
    return await ask_ollama(prompt)


def is_ollama_running() -> bool:
    """Check if Ollama is accessible."""
    try:
        import httpx
        r = httpx.get(f"{settings.OLLAMA_HOST}/api/tags", timeout=3.0)
        return r.status_code == 200
    except Exception:
        return False
