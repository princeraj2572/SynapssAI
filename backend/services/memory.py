from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import List
import json

from models.memory import Memory
from models.daily_stat import DailyStat
from models.activity import Activity
from services.llm import ask_with_context


def generate_daily_memory(db: Session, target_date: date) -> str:
    """Convert a day's stats into a natural language memory sentence."""
    stats = (
        db.query(DailyStat, Activity)
        .join(Activity, DailyStat.activity_id == Activity.id)
        .filter(DailyStat.date == target_date, DailyStat.total_value > 0)
        .all()
    )

    if not stats:
        return ""

    parts = []
    for stat, activity in stats:
        unit = activity.unit or "units"
        parts.append(f"{activity.name}: {round(stat.total_value, 1)} {unit}")

    memory_text = f"On {target_date}: " + ", ".join(parts) + "."
    return memory_text


def store_memory(db: Session, content: str, memory_type: str = "daily_summary"):
    """Store a memory sentence in the database."""
    memory = Memory(content=content, type=memory_type)
    db.add(memory)
    db.commit()
    db.refresh(memory)
    return memory


def get_recent_memories(db: Session, days: int = 30) -> List[str]:
    """Retrieve recent memory sentences for RAG context."""
    since = date.today() - timedelta(days=days)
    memories = (
        db.query(Memory)
        .filter(Memory.created_at >= since)
        .order_by(Memory.created_at.desc())
        .limit(50)
        .all()
    )
    return [m.content for m in memories]


def simple_keyword_search(memories: List[str], query: str, top_k: int = 5) -> List[str]:
    """
    Simple keyword-based memory retrieval.
    Replace with pgvector similarity search when sentence-transformers is installed.
    """
    query_words = set(query.lower().split())
    scored = []
    for memory in memories:
        memory_words = set(memory.lower().split())
        overlap = len(query_words & memory_words)
        if overlap > 0:
            scored.append((overlap, memory))
    scored.sort(reverse=True)
    return [m for _, m in scored[:top_k]]


async def query_memory(db: Session, query: str, top_k: int = 5) -> dict:
    """Full RAG pipeline: retrieve relevant memories, then ask LLM."""
    all_memories = get_recent_memories(db, days=60)
    relevant = simple_keyword_search(all_memories, query, top_k=top_k)
    answer = await ask_with_context(query, relevant)
    return {
        "answer": answer,
        "context_used": relevant,
        "model": "ollama",
    }
