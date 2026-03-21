from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.memory import MemoryQueryRequest
from services.memory import query_memory
from services.llm import is_ollama_running

router = APIRouter(prefix="/api/memory", tags=["ai"])


@router.post("/query")
async def memory_query(req: MemoryQueryRequest, db: Session = Depends(get_db)):
    result = await query_memory(db, req.query, req.top_k or 5)
    return result


@router.get("/status")
def llm_status():
    running = is_ollama_running()
    return {
        "ollama_running": running,
        "message": "LLM ready" if running else "Start Ollama: ollama serve",
    }
