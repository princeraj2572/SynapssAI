from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TrackRequest(BaseModel):
    activity: str
    value: Optional[float] = 1.0
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    source: Optional[str] = "manual"
    notes: Optional[str] = None


class BatchTrackRequest(BaseModel):
    events: List[TrackRequest]


class TrackResponse(BaseModel):
    status: str
    activity: str
    id: int


class BatchTrackResponse(BaseModel):
    status: str
    count: int
    ids: List[int]
