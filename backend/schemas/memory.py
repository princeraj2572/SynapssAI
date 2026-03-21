from pydantic import BaseModel
from typing import List, Optional


class MemoryQueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    stream: Optional[bool] = False


class MemoryQueryResponse(BaseModel):
    answer: str
    context_used: List[str]
    model: str


class JournalCreateRequest(BaseModel):
    date: str          # YYYY-MM-DD
    content: str
    mood_score: Optional[float] = None


class JournalResponse(BaseModel):
    id: int
    date: str
    content: str
    mood_score: Optional[float]
