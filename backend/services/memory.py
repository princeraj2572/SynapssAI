from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import List, Optional
import json
import logging
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
import numpy as np

from models.memory import Memory
from models.daily_stat import DailyStat
from models.activity import Activity
from services.llm import ask_with_context
from config import settings

logger = logging.getLogger(__name__)

# Load embeddings model once
try:
    embed_model = SentenceTransformer(settings.EMBED_MODEL)
    logger.info(f"Loaded embeddings model: {settings.EMBED_MODEL}")
except Exception as e:
    logger.warning(f"Could not load embeddings model: {e}. Will use keyword search.")
    embed_model = None


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


def store_memory(db: Session, content: str, memory_type: str = "daily_summary", embedding: Optional[List[float]] = None):
    """Store a memory with optional semantic embedding."""
    memory = Memory(content=content, type=memory_type)
    db.add(memory)
    db.commit()
    db.refresh(memory)
    return memory


def get_embedding(text: str) -> Optional[List[float]]:
    """Generate semantic embedding for text."""
    if embed_model is None:
        return None
    try:
        return embed_model.encode(text, convert_to_tensor=False).tolist()
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        return None


def get_recent_memories(db: Session, days: int = 30) -> List[tuple]:
    """Retrieve recent memory sentences with metadata."""
    since = date.today() - timedelta(days=days)
    memories = (
        db.query(Memory)
        .filter(Memory.created_at >= since)
        .order_by(Memory.created_at.desc())
        .limit(100)
        .all()
    )
    return [(m.content, m.type, m.created_at) for m in memories]


def semantic_search(memories: List[str], query: str, top_k: int = 5) -> List[str]:
    """Semantic similarity search using sentence transformers."""
    if embed_model is None or not memories:
        return []
    
    try:
        query_embedding = get_embedding(query)
        memory_embeddings = [get_embedding(m) for m in memories]
        
        # Calculate similarity scores
        scores = []
        for i, mem_emb in enumerate(memory_embeddings):
            if mem_emb is not None and query_embedding is not None:
                similarity = 1 - cosine(query_embedding, mem_emb)
                scores.append((similarity, memories[i]))
        
        scores.sort(reverse=True)
        return [m for _, m in scores[:top_k] if scores]
    except Exception as e:
        logger.error(f"Semantic search error: {e}")
        return []


def simple_keyword_search(memories: List[str], query: str, top_k: int = 5) -> List[str]:
    """Fallback: Simple keyword-based memory retrieval."""
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
    memory_texts = [m[0] for m in all_memories]
    
    # Try semantic search first, fall back to keyword
    if embed_model is not None:
        relevant = semantic_search(memory_texts, query, top_k=top_k)
    else:
        relevant = simple_keyword_search(memory_texts, query, top_k=top_k)
    
    # If no results, get most recent memories as fallback
    if not relevant:
        relevant = memory_texts[:top_k]
    
    answer = await ask_with_context(query, relevant)
    return {
        "answer": answer,
        "context_used": relevant,
        "model": "ollama",
        "search_type": "semantic" if embed_model else "keyword",
    }
